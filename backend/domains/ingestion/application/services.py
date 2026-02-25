import os
import logging
import uuid
import json
from datetime import datetime
from fastapi import Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from config.env import UploadConfig
from domains.ingestion.events import DATASET_INGESTED
from domains.shared.events.event_models import EventMessage
from domains.shared.events.registry import get_event_bus
from exceptions.exception import ServiceException
from middlewares.trace_middleware import TraceCtx
from module_admin.dao.upload_dao import UploadDao
from module_admin.entity.do.upload_do import SysUpload
from module_admin.entity.vo.common_vo import CrudResponseModel, UploadResponseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.upload_util import UploadUtil

logger = logging.getLogger(__name__)


class IngestionService:
    """
    上传接入应用服务：负责上传登记与事件投递。
    """
    IDEMPOTENCY_RESULT_TTL_SECONDS = 24 * 60 * 60
    IDEMPOTENCY_LOCK_TTL_SECONDS = 5 * 60

    @classmethod
    def _idempotency_key(cls, dataset_id: str, dataset_version: str) -> str:
        return f'ingestion:idempotency:{dataset_id}:{dataset_version}'

    @classmethod
    async def ingest_upload_file(
        cls,
        request: Request,
        file: UploadFile,
        query_db: AsyncSession,
        current_user: CurrentUserModel,
        dataset_id: str | None = None,
        dataset_version: str = 'v1',
    ) -> CrudResponseModel:
        if dataset_id:
            TraceCtx.set_dataset_id(dataset_id)

        redis = request.app.state.redis
        idempotency_key = None
        lock_key = None
        if dataset_id:
            idempotency_key = cls._idempotency_key(dataset_id, dataset_version)
            lock_key = f'{idempotency_key}:lock'
            cached_result = await redis.get(idempotency_key)
            if cached_result:
                cached_data = json.loads(cached_result)
                return CrudResponseModel(
                    is_success=True,
                    result=UploadResponseModel(**cached_data),
                    message='幂等命中，返回已处理结果',
                )
            lock_created = await redis.set(lock_key, '1', ex=cls.IDEMPOTENCY_LOCK_TTL_SECONDS, nx=True)
            if not lock_created:
                raise ServiceException(message='相同 dataset_id + version 正在处理中，请稍后重试')

        upload_start_time = datetime.now()
        upload_status = 0
        file_size = 0

        try:
            if not UploadUtil.check_file_extension(file):
                raise ServiceException(message='文件类型不合法')

            relative_path = f'upload/{datetime.now().strftime("%Y")}/{datetime.now().strftime("%m")}/{datetime.now().strftime("%d")}'
            dir_path = os.path.join(UploadConfig.UPLOAD_PATH, relative_path)
            os.makedirs(dir_path, exist_ok=True)

            filename = (
                f'{file.filename.rsplit(".", 1)[0]}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                f'{UploadConfig.UPLOAD_MACHINE}{UploadUtil.generate_random_number()}.{file.filename.rsplit(".")[-1]}'
            )
            filepath = os.path.join(dir_path, filename)

            with open(filepath, 'wb') as fs:
                for chunk in iter(lambda: file.file.read(1024 * 1024 * 10), b''):
                    fs.write(chunk)
                    file_size += len(chunk)

            upload_end_time = datetime.now()
            upload_status = 1
            file_url = f'{request.base_url}{UploadConfig.UPLOAD_PREFIX[1:]}/{relative_path}/{filename}'
            file_name_path = f'{UploadConfig.UPLOAD_PREFIX}/{relative_path}/{filename}'

            upload_record = SysUpload(
                upload_starttime=upload_start_time,
                upload_endtime=upload_end_time,
                upload_userid=current_user.user.user_id,
                upload_status=upload_status,
                original_filename=file.filename,
                new_file_name=filename,
                file_path=file_name_path,
                file_size=file_size,
                file_url=file_url,
            )
            await UploadDao.add_upload_record(query_db, upload_record)
            await query_db.commit()

            logger.info(f'文件上传登记成功: {file.filename}')

            event_bus = get_event_bus()
            event = EventMessage.build(
                event_id=uuid.uuid4().hex,
                event_type=DATASET_INGESTED,
                trace_id=TraceCtx.get_id() or '-',
                producer='ingestion-service',
                dataset_id=str(upload_record.id),
                dataset_version='v1',
                payload={
                    'upload_id': upload_record.id,
                    'original_filename': file.filename,
                    'stored_path': file_name_path,
                    'file_size': file_size,
                    'ingested_at': upload_end_time.isoformat(),
                },
            )
            await event_bus.publish(event)

            upload_response = UploadResponseModel(
                fileName=file_name_path,
                newFileName=filename,
                originalFilename=file.filename,
                url=file_url,
            )
            if idempotency_key:
                await redis.set(
                    idempotency_key,
                    json.dumps(upload_response.model_dump()),
                    ex=cls.IDEMPOTENCY_RESULT_TTL_SECONDS,
                )

            return CrudResponseModel(
                is_success=True,
                result=upload_response,
                message='上传成功，已完成入湖登记并投递处理事件',
            )
        except Exception as exc:
            upload_end_time = datetime.now()
            try:
                upload_record = SysUpload(
                    upload_starttime=upload_start_time,
                    upload_endtime=upload_end_time,
                    upload_userid=current_user.user.user_id if current_user and current_user.user else None,
                    upload_status=0,
                    original_filename=file.filename if file else '未知文件',
                    new_file_name='',
                    file_path='',
                    file_size=file_size,
                    file_url='',
                )
                await UploadDao.add_upload_record(query_db, upload_record)
                await query_db.commit()
            except Exception as db_error:
                logger.error(f'保存上传失败记录异常: {db_error}', exc_info=True)
            raise exc
        finally:
            if lock_key:
                try:
                    await redis.delete(lock_key)
                except Exception as unlock_error:
                    logger.warning(f'幂等锁释放失败: {unlock_error}')

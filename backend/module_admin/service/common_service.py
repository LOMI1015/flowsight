import os
from datetime import datetime
from fastapi import BackgroundTasks, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from config.env import UploadConfig
from exceptions.exception import ServiceException
from module_admin.dao.upload_dao import UploadDao
from module_admin.entity.do.upload_do import SysUpload
from module_admin.entity.vo.common_vo import (
    CrudResponseModel,
    UploadResponseModel,
    UploadRecordPageQueryModel,
)
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.file_data_service import FileDataService
from utils.upload_util import UploadUtil
import logging

logger = logging.getLogger(__name__)


class CommonService:
    """
    通用模块服务层
    """

    @classmethod
    async def upload_service(
        cls, request: Request, file: UploadFile, query_db: AsyncSession, current_user: CurrentUserModel
    ):
        """
        通用上传service

        :param request: Request对象
        :param file: 上传文件对象
        :param query_db: orm对象
        :param current_user: 当前用户信息
        :return: 上传结果
        """
        # 记录开始时间
        upload_start_time = datetime.now()
        upload_status = 0  # 0失败 1成功
        file_size = 0

        try:
            if not UploadUtil.check_file_extension(file):
                raise ServiceException(message='文件类型不合法')

            relative_path = f'upload/{datetime.now().strftime("%Y")}/{datetime.now().strftime("%m")}/{datetime.now().strftime("%d")}'
            dir_path = os.path.join(UploadConfig.UPLOAD_PATH, relative_path)
            try:
                os.makedirs(dir_path)
            except FileExistsError:
                pass

            filename = f'{file.filename.rsplit(".", 1)[0]}_{datetime.now().strftime("%Y%m%d%H%M%S")}{UploadConfig.UPLOAD_MACHINE}{UploadUtil.generate_random_number()}.{file.filename.rsplit(".")[-1]}'
            filepath = os.path.join(dir_path, filename)

            # 写入文件并计算文件大小
            with open(filepath, 'wb') as f:
                # 流式写出大型文件，这里的10代表10MB
                for chunk in iter(lambda: file.file.read(1024 * 1024 * 10), b''):
                    f.write(chunk)
                    file_size += len(chunk)

            # 记录结束时间
            upload_end_time = datetime.now()
            upload_status = 1  # 上传成功

            # 构建文件URL
            file_url = f'{request.base_url}{UploadConfig.UPLOAD_PREFIX[1:]}/{relative_path}/{filename}'
            file_name_path = f'{UploadConfig.UPLOAD_PREFIX}/{relative_path}/{filename}'

            # 保存上传记录到数据库
            upload_record = SysUpload(
                upload_starttime=upload_start_time,  # 开始上传时间
                upload_endtime=upload_end_time,  # 上传结束时间
                upload_userid=current_user.user.user_id,  # 上传用户ID
                upload_status=upload_status,  # 上传状态
                original_filename=file.filename,  # 原始文件名
                new_file_name=filename,  # 新文件名
                file_path=file_name_path,  # 文件路径
                file_size=file_size,  # 文件大小
                file_url=file_url,  # 文件访问URL
            )

            await UploadDao.add_upload_record(query_db, upload_record)
            await query_db.commit()  # 在 service 层统一提交事务

            # 处理文件数据（读取、处理、插入数据库）
            # 注意：这里需要根据实际需求配置表名和列映射
            process_result = None
            try:
                # 从保存的文件路径读取文件进行处理
                # TODO: 根据实际需求配置以下参数
                # table_name: 目标数据库表名
                # column_mapping: Excel 列名到数据库字段名的映射
                # 示例：
                # table_name = 'your_table_name'
                # column_mapping = {
                #     'Excel列名1': 'db_column1',
                #     'Excel列名2': 'db_column2',
                # }
                
                # 如果需要处理文件数据，取消下面的注释并配置参数
                process_result = await FileDataService.process_file_from_path(
                    db=query_db,
                    file_path=filepath,
                    file_name=file.filename,
                    table_name='ods_doudian_chat_session_all_dd',  # 替换为实际的表名
                    column_mapping={
                        # 配置列名映射
                        '会话ID': 'session_id',
                        '会话时间': 'session_time',
                        '用户信息': 'user_name',
                        '发起场景': 'start_scene',
                        '结束场景': 'end_scene',
                        '评价结果': 'eval',
                        '转人工类型': 'session_type',
                        '进入排队时间': 'queue_time',
                        '接待客服': 'agent_name',
                        '首响时长': 'first_reply_time',
                        '平响时长': 'average_reply_time',
                        '人工会话时长': 'service_time',
                        '转接记录': 'transfer_record'
                    },
                    batch_size=1000,  # 批量插入大小
                    schema_name='ods',  # 可选：指定 schema 名称，如 'sales', 'finance' 等，不指定则使用默认 schema（通常是 public）
                    only_mapped_columns=True,  # 只插入已映射的列，忽略 Excel 中未映射的列（如 "评价结果.1" 等）
                )

                logger.info(f'文件上传成功: {file.filename}')
                if process_result:
                    logger.info(f'文件数据处理结果: {process_result.get("message", "")}')

            except Exception as process_error:
                # 文件处理失败不影响上传成功，只记录日志
                logger.error(f'处理文件数据失败: {str(process_error)}', exc_info=True)

            return CrudResponseModel(
                is_success=True,
                result=UploadResponseModel(
                    fileName=file_name_path,
                    newFileName=filename,
                    originalFilename=file.filename,
                    url=file_url,
                ),
                message='上传成功' + (f'，{process_result.get("message", "")}' if process_result else ''),
            )

        except Exception as e:
            # 记录结束时间（即使失败）
            upload_end_time = datetime.now()

            # 保存失败记录到数据库
            try:
                upload_record = SysUpload(
                    upload_starttime=upload_start_time,
                    upload_endtime=upload_end_time,
                    upload_userid=current_user.user.user_id if current_user and current_user.user else None,
                    upload_status=0,  # 上传失败
                    original_filename=file.filename if file else '未知文件',
                    new_file_name='',
                    file_path='',
                    file_size=file_size,
                    file_url='',
                )
                await UploadDao.add_upload_record(query_db, upload_record)
                await query_db.commit()  # 在 service 层统一提交事务
            except Exception as db_error:
                # 如果数据库保存失败，记录日志但不影响主流程
                import logging
                logging.error(f'保存上传记录失败: {db_error}')

            # 重新抛出原始异常
            raise e

    @classmethod
    async def get_upload_record_list_services(
        cls, query_db: AsyncSession, query_object: UploadRecordPageQueryModel, is_page: bool = False
    ):
        """
        获取上传记录列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 上传记录列表信息对象
        """
        upload_list = await UploadDao.get_upload_record_list(query_db, query_object, is_page)
        return upload_list

    @classmethod
    async def download_services(cls, background_tasks: BackgroundTasks, file_name, delete: bool):
        """
        下载下载目录文件service

        :param background_tasks: 后台任务对象
        :param file_name: 下载的文件名称
        :param delete: 是否在下载完成后删除文件
        :return: 上传结果
        """
        filepath = os.path.join(UploadConfig.DOWNLOAD_PATH, file_name)
        if '..' in file_name:
            raise ServiceException(message='文件名称不合法')
        elif not UploadUtil.check_file_exists(filepath):
            raise ServiceException(message='文件不存在')
        else:
            if delete:
                background_tasks.add_task(UploadUtil.delete_file, filepath)
            return CrudResponseModel(is_success=True, result=UploadUtil.generate_file(filepath), message='下载成功')

    @classmethod
    async def download_resource_services(cls, resource: str):
        """
        下载上传目录文件service

        :param resource: 下载的文件名称
        :return: 上传结果
        """
        filepath = os.path.join(resource.replace(UploadConfig.UPLOAD_PREFIX, UploadConfig.UPLOAD_PATH))
        filename = resource.rsplit('/', 1)[-1]
        if (
            '..' in filename
            or not UploadUtil.check_file_timestamp(filename)
            or not UploadUtil.check_file_machine(filename)
            or not UploadUtil.check_file_random_code(filename)
        ):
            raise ServiceException(message='文件名称不合法')
        elif not UploadUtil.check_file_exists(filepath):
            raise ServiceException(message='文件不存在')
        else:
            return CrudResponseModel(is_success=True, result=UploadUtil.generate_file(filepath), message='下载成功')

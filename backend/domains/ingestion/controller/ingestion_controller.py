from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from domains.admin.application.services import LoginService
from domains.ingestion.application.services import IngestionService
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.log_util import logger
from utils.response_util import ResponseUtil

ingestionController = APIRouter(prefix='/datasets', dependencies=[Depends(LoginService.get_current_user)])


@ingestionController.post('/upload')
async def ingest_dataset_upload(
    request: Request,
    file: UploadFile = File(...),
    dataset_id: str = Form(...),
    dataset_version: str = Form(default='v1'),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    ingest_result = await IngestionService.ingest_upload_file(
        request,
        file,
        query_db,
        current_user,
        dataset_id=dataset_id,
        dataset_version=dataset_version,
    )
    logger.info('ingestion 上传并入库成功')
    return ResponseUtil.success(model_content=ingest_result.result, msg=ingest_result.message)

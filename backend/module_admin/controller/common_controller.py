from fastapi import APIRouter, BackgroundTasks, Depends, File, Query, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from module_admin.annotation.pydantic_annotation import as_query
from module_admin.entity.vo.common_vo import UploadRecordPageQueryModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.common_service import CommonService
from module_admin.service.login_service import LoginService
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil

commonController = APIRouter(prefix='/common', dependencies=[Depends(LoginService.get_current_user)])


@commonController.post('/upload')
async def common_upload(
    request: Request,
    file: UploadFile = File(...),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    upload_result = await CommonService.upload_service(request, file, query_db, current_user)
    logger.info('上传成功')

    return ResponseUtil.success(model_content=upload_result.result)


@commonController.get('/upload/list', response_model=PageResponseModel)
async def get_upload_record_list(
    request: Request,
    upload_record_page_query: UploadRecordPageQueryModel = Depends(UploadRecordPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    upload_list_result = await CommonService.get_upload_record_list_services(
        query_db, upload_record_page_query, is_page=True
    )
    logger.info('获取上传记录列表成功')

    return ResponseUtil.success(model_content=upload_list_result)


@commonController.get('/download')
async def common_download(
    request: Request,
    background_tasks: BackgroundTasks,
    file_name: str = Query(alias='fileName'),
    delete: bool = Query(),
):
    download_result = await CommonService.download_services(background_tasks, file_name, delete)
    logger.info(download_result.message)

    return ResponseUtil.streaming(data=download_result.result)


@commonController.get('/download/resource')
async def common_download_resource(request: Request, resource: str = Query()):
    download_resource_result = await CommonService.download_resource_services(resource)
    logger.info(download_resource_result.message)

    return ResponseUtil.streaming(data=download_resource_result.result)

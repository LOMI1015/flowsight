import os
from fastapi import BackgroundTasks, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from config.env import UploadConfig
from domains.ingestion.application.services import IngestionService
from exceptions.exception import ServiceException
from module_admin.dao.upload_dao import UploadDao
from module_admin.entity.vo.common_vo import (
    CrudResponseModel,
    UploadRecordPageQueryModel,
)
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.upload_util import UploadUtil


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
        return await IngestionService.ingest_upload_file(request, file, query_db, current_user)

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

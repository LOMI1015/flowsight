from datetime import datetime, time
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.upload_do import SysUpload
from module_admin.entity.do.user_do import SysUser
from module_admin.entity.vo.common_vo import UploadRecordPageQueryModel
from utils.page_util import PageUtil


class UploadDao:
    """
    文件上传记录数据库操作层
    """

    @classmethod
    async def add_upload_record(cls, db: AsyncSession, upload_record: SysUpload):
        """
        添加上传记录

        :param db: orm对象
        :param upload_record: 上传记录对象
        :return: 上传记录对象
        """
        db.add(upload_record)
        await db.flush()  # flush 后可以获取自动生成的 ID，但不提交事务
        return upload_record

    @classmethod
    async def get_upload_record_by_id(cls, db: AsyncSession, record_id: int):
        """
        根据ID获取上传记录

        :param db: orm对象
        :param record_id: 记录ID
        :return: 上传记录对象
        """
        result = await db.execute(select(SysUpload).where(SysUpload.id == record_id))
        return result.scalars().first()

    @classmethod
    async def get_upload_record_list(
        cls, db: AsyncSession, query_object: UploadRecordPageQueryModel, is_page: bool = False
    ):
        """
        根据查询参数获取上传记录列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 上传记录列表信息对象
        """
        query = (
            select(
                SysUpload.id,
                SysUpload.upload_starttime,
                SysUpload.upload_endtime,
                SysUpload.upload_userid,
                SysUpload.upload_status,
                SysUpload.original_filename,
                SysUpload.new_file_name,
                SysUpload.file_path,
                SysUpload.file_size,
                SysUpload.file_url,
                SysUser.user_name,
                SysUser.nick_name,
            )
            .select_from(SysUpload)
            .join(SysUser, SysUpload.upload_userid == SysUser.user_id, isouter=True)
            .where(
                SysUpload.original_filename.like(f'%{query_object.original_filename}%')
                if query_object.original_filename
                else True,
                SysUpload.upload_userid == query_object.upload_userid
                if query_object.upload_userid
                else True,
                SysUpload.upload_status == query_object.upload_status
                if query_object.upload_status is not None
                else True,
                SysUpload.upload_starttime.between(
                    datetime.combine(
                        datetime.strptime(query_object.begin_time, '%Y-%m-%d'), time(00, 00, 00)
                    ),
                    datetime.combine(
                        datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)
                    ),
                )
                if query_object.begin_time and query_object.end_time
                else True,
            )
            .order_by(desc(SysUpload.upload_starttime))
            .distinct()
        )
        upload_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return upload_list


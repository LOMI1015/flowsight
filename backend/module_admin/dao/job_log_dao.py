from datetime import datetime, time
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from module_admin.entity.do.job_do import SysJobLog
from module_admin.entity.vo.job_vo import JobLogModel, JobLogPageQueryModel
from utils.page_util import PageUtil


class JobLogDao:
    """
    定时任务日志管理模块数据库操作层
    """

    @classmethod
    async def get_job_log_list(cls, db: AsyncSession, query_object: JobLogPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取定时任务日志列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 定时任务日志列表信息对象
        """
        query = (
            select(SysJobLog)
            .where(
                SysJobLog.job_name.like(f'%{query_object.job_name}%') if query_object.job_name else True,
                SysJobLog.job_group == query_object.job_group if query_object.job_group else True,
                SysJobLog.status == query_object.status if query_object.status else True,
                SysJobLog.create_time.between(
                    datetime.combine(datetime.strptime(query_object.begin_time, '%Y-%m-%d'), time(00, 00, 00)),
                    datetime.combine(datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)),
                )
                if query_object.begin_time and query_object.end_time and query_object.begin_time.strip() and query_object.end_time.strip()
                else True,
            )
            .order_by(desc(SysJobLog.create_time))
            .distinct()
        )
        job_log_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return job_log_list

    @classmethod
    def add_job_log_dao(cls, db: Session, job_log: JobLogModel):
        """
        新增定时任务日志数据库操作

        :param db: orm对象
        :param job_log: 定时任务日志对象
        :return:
        """
        db_job_log = SysJobLog(**job_log.model_dump())
        db.add(db_job_log)
        db.flush()

        return db_job_log

    @classmethod
    def update_job_log_by_job_id_and_start_time(
        cls, db: Session, job_id: int, start_time: datetime, update_data: dict
    ) -> int:
        """
        根据任务ID和开始时间更新日志

        :param db: orm对象
        :param job_id: 任务ID
        :param start_time: 开始时间
        :param update_data: 更新字段
        :return: 更新行数
        """
        return (
            db.query(SysJobLog)
            .filter(SysJobLog.job_id == job_id, SysJobLog.start_time == start_time)
            .update(update_data)
        )

    @classmethod
    def get_latest_running_log_start_time(cls, db: Session, job_id: int):
        """
        查询该任务最近一条「执行中」日志的 start_time，用于 EXECUTED 事件中
        scheduled_run_time 与 SUBMITTED 不一致时仍能正确更新同一条记录。

        :param db: orm对象
        :param job_id: 任务ID
        :return: start_time 或 None
        """
        row = (
            db.query(SysJobLog.start_time)
            .filter(SysJobLog.job_id == job_id, SysJobLog.status == '2')
            .order_by(desc(SysJobLog.start_time))
            .limit(1)
            .first()
        )
        return row[0] if row else None

    @classmethod
    def get_latest_running_log_id(cls, db: Session, job_id: int):
        """
        查询该任务最近一条「执行中」日志的主键 id，用于按主键更新，避免 start_time 不一致导致更新不到。

        :param db: orm对象
        :param job_id: 任务ID
        :return: job_log_id 或 None
        """
        row = (
            db.query(SysJobLog.job_log_id)
            .filter(SysJobLog.job_id == job_id, SysJobLog.status == '2')
            .order_by(desc(SysJobLog.start_time))
            .limit(1)
            .first()
        )
        return row[0] if row else None

    @classmethod
    def update_job_log_by_id(cls, db: Session, job_log_id: int, update_data: dict) -> int:
        """
        根据任务日志主键 ID 更新日志

        :param db: orm对象
        :param job_log_id: 任务日志ID
        :param update_data: 更新字段
        :return: 更新行数
        """
        return (
            db.query(SysJobLog)
            .filter(SysJobLog.job_log_id == job_log_id)
            .update(update_data)
        )

    @classmethod
    async def delete_job_log_dao(cls, db: AsyncSession, job_log: JobLogModel):
        """
        删除定时任务日志数据库操作

        :param db: orm对象
        :param job_log: 定时任务日志对象
        :return:
        """
        await db.execute(delete(SysJobLog).where(SysJobLog.job_log_id.in_([job_log.job_log_id])))

    @classmethod
    async def clear_job_log_dao(cls, db: AsyncSession):
        """
        清除定时任务日志数据库操作

        :param db: orm对象
        :return:
        """
        await db.execute(delete(SysJobLog))

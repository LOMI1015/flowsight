import json
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED, EVENT_JOB_SUBMITTED
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from asyncio import iscoroutinefunction
from datetime import datetime, timedelta
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional, Union
from config.database import AsyncSessionLocal, quote_plus
from config.env import DataBaseConfig, RedisConfig
from module_admin.dao.job_dao import JobDao
from module_admin.dao.job_log_dao import JobLogDao
from module_admin.entity.do.job_do import SysJob
from module_admin.entity.vo.job_vo import JobLogModel, JobModel
from module_admin.service.job_log_service import JobLogService
from utils.log_util import logger
import module_task  # noqa: F401


# 重写Cron定时
class MyCronTrigger(CronTrigger):
    @classmethod
    def from_crontab(cls, expr: str, timezone=None):
        values = expr.split()
        if len(values) != 6 and len(values) != 7:
            raise ValueError('Wrong number of fields; got {}, expected 6 or 7'.format(len(values)))

        second = values[0]
        minute = values[1]
        hour = values[2]
        if '?' in values[3]:
            day = None
        elif 'L' in values[5]:
            day = f"last {values[5].replace('L', '')}"
        elif 'W' in values[3]:
            day = cls.__find_recent_workday(int(values[3].split('W')[0]))
        else:
            day = values[3].replace('L', 'last')
        month = values[4]
        if '?' in values[5] or 'L' in values[5]:
            week = None
        elif '#' in values[5]:
            week = int(values[5].split('#')[1])
        else:
            week = values[5]
        if '#' in values[5]:
            day_of_week = int(values[5].split('#')[0]) - 1
        else:
            day_of_week = None
        year = values[6] if len(values) == 7 else None
        return cls(
            second=second,
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            week=week,
            day_of_week=day_of_week,
            year=year,
            timezone=timezone,
        )

    @classmethod
    def __find_recent_workday(cls, day: int):
        now = datetime.now()
        date = datetime(now.year, now.month, day)
        if date.weekday() < 5:
            return date.day
        else:
            diff = 1
            while True:
                previous_day = date - timedelta(days=diff)
                if previous_day.weekday() < 5:
                    return previous_day.day
                else:
                    diff += 1


SQLALCHEMY_DATABASE_URL = (
    f'mysql+pymysql://{DataBaseConfig.db_username}:{quote_plus(DataBaseConfig.db_password)}@'
    f'{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/{DataBaseConfig.db_database}'
)
if DataBaseConfig.db_type == 'postgresql':
    SQLALCHEMY_DATABASE_URL = (
        f'postgresql+psycopg2://{DataBaseConfig.db_username}:{quote_plus(DataBaseConfig.db_password)}@'
        f'{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/{DataBaseConfig.db_database}'
    )
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=DataBaseConfig.db_echo,
    max_overflow=DataBaseConfig.db_max_overflow,
    pool_size=DataBaseConfig.db_pool_size,
    pool_recycle=DataBaseConfig.db_pool_recycle,
    pool_timeout=DataBaseConfig.db_pool_timeout,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
job_stores = {
    'default': MemoryJobStore(),
    'sqlalchemy': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URL, engine=engine),
    'redis': RedisJobStore(
        **dict(
            host=RedisConfig.redis_host,
            port=RedisConfig.redis_port,
            username=RedisConfig.redis_username,
            password=RedisConfig.redis_password,
            db=RedisConfig.redis_database,
        )
    ),
}
executors = {'default': AsyncIOExecutor(), 'processpool': ProcessPoolExecutor(5)}
job_defaults = {'coalesce': False, 'max_instance': 1}
scheduler = AsyncIOScheduler()
scheduler.configure(jobstores=job_stores, executors=executors, job_defaults=job_defaults)


class SchedulerUtil:
    """
    定时任务相关方法
    """

    @classmethod
    async def init_system_scheduler(cls):
        """
        应用启动时初始化定时任务

        :return:
        """
        logger.info('开始启动定时任务...')
        scheduler.start()
        async with AsyncSessionLocal() as session:
            job_list = await JobDao.get_job_list_for_scheduler(session)
            for item in job_list:
                cls.remove_scheduler_job(job_id=str(item.job_id))
                cls.add_scheduler_job(item)
        scheduler.add_listener(
            cls.scheduler_event_listener,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED | EVENT_JOB_SUBMITTED,
        )
        logger.info('系统初始定时任务加载成功')

    @classmethod
    async def close_system_scheduler(cls):
        """
        应用关闭时关闭定时任务

        :return:
        """
        scheduler.shutdown()
        logger.info('关闭定时任务成功')

    @classmethod
    def get_scheduler_job(cls, job_id: Union[str, int]):
        """
        根据任务id获取任务对象

        :param job_id: 任务id
        :return: 任务对象
        """
        query_job = scheduler.get_job(job_id=str(job_id))

        return query_job

    @classmethod
    def add_scheduler_job(cls, job_info: JobModel):
        """
        根据输入的任务对象信息添加任务

        :param job_info: 任务对象信息
        :return:
        """
        job_func = eval(job_info.invoke_target)
        job_executor = job_info.job_executor
        if iscoroutinefunction(job_func):
            job_executor = 'default'
        scheduler.add_job(
            func=eval(job_info.invoke_target),
            trigger=MyCronTrigger.from_crontab(job_info.cron_expression),
            args=job_info.job_args.split(',') if job_info.job_args else None,
            kwargs=json.loads(job_info.job_kwargs) if job_info.job_kwargs else None,
            id=str(job_info.job_id),
            name=job_info.job_name,
            misfire_grace_time=1000000000000 if job_info.misfire_policy == '3' else None,
            coalesce=True if job_info.misfire_policy == '2' else False,
            max_instances=3 if job_info.concurrent == '0' else 1,
            jobstore=job_info.job_group,
            executor=job_executor,
        )

    @classmethod
    def execute_scheduler_job_once(cls, job_info: JobModel):
        """
        立即执行一次：添加一个仅触发一次的任务（id 带 _immediate），使用传入的 job_info（含临时 kwargs）。
        不删除、不覆盖原定时任务，后续 cron 仍使用数据库中保存的配置。
        """
        job_func = eval(job_info.invoke_target)
        job_executor = job_info.job_executor
        if iscoroutinefunction(job_func):
            job_executor = 'default'
        # 仅本次触发，不绑定 cron，避免覆盖原任务的 kwargs
        job_trigger = DateTrigger()
        scheduler.add_job(
            func=eval(job_info.invoke_target),
            trigger=job_trigger,
            args=job_info.job_args.split(',') if job_info.job_args else None,
            kwargs=json.loads(job_info.job_kwargs) if job_info.job_kwargs else None,
            id=str(job_info.job_id) + '_immediate',
            name=job_info.job_name,
            misfire_grace_time=1000000000000 if job_info.misfire_policy == '3' else None,
            coalesce=True if job_info.misfire_policy == '2' else False,
            max_instances=3 if job_info.concurrent == '0' else 1,
            jobstore=job_info.job_group,
            executor=job_executor,
        )

    @classmethod
    def remove_scheduler_job(cls, job_id: Union[str, int]):
        """
        根据任务id移除任务

        :param job_id: 任务id
        :return:
        """
        query_job = cls.get_scheduler_job(job_id=job_id)
        if query_job:
            scheduler.remove_job(job_id=str(job_id))

    @classmethod
    def _main_job_id(cls, job_id: Union[str, int]) -> Union[int, str, None]:
        """立即执行任务的 id 为 job_id_immediate，日志需关联到主任务 id。"""
        if job_id is None:
            return None
        s = str(job_id)
        if s.endswith('_immediate'):
            try:
                return int(s.replace('_immediate', ''))
            except ValueError:
                return job_id
        return int(job_id) if isinstance(job_id, str) else job_id

    @classmethod
    def scheduler_event_listener(cls, event):
        if not hasattr(event, 'job_id'):
            return

        job_id = event.job_id
        log_job_id = cls._main_job_id(job_id)
        if log_job_id is None:
            return
        scheduled_run_time = cls._normalize_datetime(getattr(event, 'scheduled_run_time', None))
        event_type = event.__class__.__name__

        if event.code & EVENT_JOB_SUBMITTED:
            job_detail = cls._get_job_detail(job_id)
            cls._create_job_log(
                job_id=log_job_id,
                start_time=scheduled_run_time or datetime.now().replace(microsecond=0),
                status='2',
                job_message=f'事件类型: {event_type}, 任务ID: {job_id}, 执行开始',
                job_detail=job_detail,
            )
            return

        status = '0'
        exception_info = ''
        if event.code & EVENT_JOB_ERROR:
            status = '1'
            exception_info = str(getattr(event, 'exception', '') or '')
        if event.code & EVENT_JOB_MISSED:
            status = '1'
            exception_info = '任务触发错过'

        job_result = getattr(event, 'retval', None) if event.code & EVENT_JOB_EXECUTED else None
        if (event.code & EVENT_JOB_EXECUTED) and isinstance(job_result, dict):
            result_status = job_result.get('status')
            if result_status == 'failed':
                status = '1'
                exception_info = exception_info or str(job_result.get('error_message', ''))
            elif result_status == 'exception':
                status = '3'
                exception_info = exception_info or str(job_result.get('error_message', ''))
        # 只写入简短错误摘要，避免超长异常（含整段 SQL）导致 exception_info 列超限、更新失败
        _EXCEPTION_INFO_MAX_LEN = 500
        if len(exception_info) > _EXCEPTION_INFO_MAX_LEN:
            exception_info = exception_info[:_EXCEPTION_INFO_MAX_LEN].rstrip() + '...'
        job_message = f'事件类型: {event_type}, 任务ID: {job_id}, 执行于{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

        # 优先用任务日志主键 id 更新，避免 job_id + start_time 不一致导致更新不到；失败时再用「执行中」的 start_time 兜底
        session = SessionLocal()
        try:
            job_log_id = JobLogDao.get_latest_running_log_id(session, int(log_job_id))
            fallback_start = JobLogDao.get_latest_running_log_start_time(session, int(log_job_id)) if job_log_id is None else None
        finally:
            session.close()

        if job_log_id is not None:
            cls._update_job_log_by_id(
                job_log_id=job_log_id,
                status=status,
                exception_info=exception_info,
                job_result=job_result,
                job_message=job_message,
            )
        else:
            # 无主键时用「执行中」日志的 start_time 更新，避免 EXECUTED 的 scheduled_run_time 与 SUBMITTED 不一致
            update_start_time = (
                cls._normalize_datetime(fallback_start) if fallback_start is not None
                else (cls._normalize_datetime(scheduled_run_time) or datetime.now().replace(microsecond=0))
            )
            cls._update_job_log(
                job_id=log_job_id,
                start_time=update_start_time,
                status=status,
                exception_info=exception_info,
                job_result=job_result,
                job_message=job_message,
            )

    @staticmethod
    def _normalize_datetime(value):
        if not value:
            return None
        try:
            return value.replace(tzinfo=None, microsecond=0)
        except Exception:
            return value

    @classmethod
    def _get_job_detail_from_scheduler(cls, job_id: Union[str, int]):
        query_job = cls.get_scheduler_job(job_id=job_id)
        if not query_job:
            return None
        query_job_info = query_job.__getstate__()
        job_args = query_job_info.get('args') or []
        job_kwargs = query_job_info.get('kwargs') or {}
        return {
            'job_name': query_job_info.get('name'),
            'job_group': query_job._jobstore_alias,
            'job_executor': query_job_info.get('executor'),
            'invoke_target': str(query_job_info.get('func')),
            'job_args': ','.join([str(item) for item in job_args]) if job_args else '',
            'job_kwargs': json.dumps(job_kwargs) if job_kwargs else '',
            'job_trigger': str(query_job_info.get('trigger')),
        }

    @classmethod
    def _get_job_detail_from_db(cls, job_id: Union[str, int]):
        session = SessionLocal()
        try:
            db_id = cls._main_job_id(job_id)
            if db_id is None:
                return None
            db_job = session.query(SysJob).filter(SysJob.job_id == int(db_id)).first()
            if not db_job:
                return None
            return {
                'job_name': db_job.job_name,
                'job_group': db_job.job_group,
                'job_executor': db_job.job_executor,
                'invoke_target': db_job.invoke_target,
                'job_args': db_job.job_args or '',
                'job_kwargs': db_job.job_kwargs or '',
                'job_trigger': db_job.cron_expression or '',
            }
        finally:
            session.close()

    @classmethod
    def _get_job_detail(cls, job_id: Union[str, int]):
        return cls._get_job_detail_from_scheduler(job_id) or cls._get_job_detail_from_db(job_id) or {}

    @staticmethod
    def _serialize_job_result(result) -> str:
        if result is None:
            return ''
        try:
            # 序列化前截短 error_message/error_details，避免超长导致 job_result 列写入失败
            if isinstance(result, dict):
                result = dict(result)
                for key in ('error_message', 'error_details'):
                    if key in result and result[key] is not None:
                        val = result[key]
                        if isinstance(val, str) and len(val) > 500:
                            result[key] = val[:500].rstrip() + '...'
                        elif isinstance(val, list):
                            result[key] = [str(x)[:200] + ('...' if len(str(x)) > 200 else '') for x in val[:10]]
            s = json.dumps(result, ensure_ascii=False, default=str)
            if len(s) > 2000:
                s = s[:1997] + '...'
            return s
        except Exception:
            return str(result)[:2000]

    @classmethod
    def _create_job_log(
        cls,
        job_id: Union[str, int],
        start_time: datetime,
        status: str,
        job_message: str,
        job_detail: Optional[dict] = None,
    ):
        if job_detail is None:
            job_detail = cls._get_job_detail(job_id)
        if not job_detail:
            return
        normalized_start = cls._normalize_datetime(start_time) or datetime.now().replace(microsecond=0)
        job_log = JobLogModel(
            jobId=int(job_id),
            jobName=job_detail.get('job_name'),
            jobGroup=job_detail.get('job_group'),
            jobExecutor=job_detail.get('job_executor'),
            invokeTarget=job_detail.get('invoke_target'),
            jobArgs=job_detail.get('job_args'),
            jobKwargs=job_detail.get('job_kwargs'),
            jobTrigger=job_detail.get('job_trigger'),
            jobMessage=job_message,
            status=status,
            exceptionInfo='',
            jobResult='',
            startTime=normalized_start,
            endTime=None,
            createTime=normalized_start,
        )
        session = SessionLocal()
        JobLogService.add_job_log_services(session, job_log)
        session.close()

    @classmethod
    def _update_job_log_by_id(
        cls,
        job_log_id: int,
        status: str,
        exception_info: str,
        job_result,
        job_message: str,
    ):
        """按任务日志主键 id 更新，避免 start_time 不一致导致更新不到。"""
        update_data = {
            'status': status,
            'exception_info': exception_info,
            'job_result': cls._serialize_job_result(job_result),
            'end_time': datetime.now().replace(microsecond=0),
            'job_message': job_message,
        }
        session = SessionLocal()
        try:
            JobLogService.update_job_log_by_id_services(session, job_log_id, update_data)
        finally:
            session.close()

    @classmethod
    def _update_job_log(
        cls,
        job_id: Union[str, int],
        start_time: datetime,
        status: str,
        exception_info: str,
        job_result,
        job_message: str,
    ):
        normalized_start = cls._normalize_datetime(start_time) or datetime.now().replace(microsecond=0)
        update_data = {
            'status': status,
            'exception_info': exception_info,
            'job_result': cls._serialize_job_result(job_result),
            'end_time': datetime.now().replace(microsecond=0),
            'job_message': job_message,
        }
        session = SessionLocal()
        update_result = JobLogService.update_job_log_services(session, int(job_id), normalized_start, update_data)
        # EXECUTED 事件的 scheduled_run_time 可能与 SUBMITTED 时不一致（尤其异步任务），
        # 导致按 start_time 更新不到「执行中」那条；用该任务最近一条执行中日志的 start_time 再试一次
        if not update_result.is_success:
            fallback_start = JobLogDao.get_latest_running_log_start_time(session, int(job_id))
            if fallback_start is not None:
                fallback_normalized = cls._normalize_datetime(fallback_start)
                if fallback_normalized:
                    update_result = JobLogService.update_job_log_services(
                        session, int(job_id), fallback_normalized, update_data
                    )
        session.close()
        if not update_result.is_success:
            job_detail = cls._get_job_detail(job_id)
            if not job_detail:
                return
            job_log = JobLogModel(
                jobId=int(job_id),
                jobName=job_detail.get('job_name'),
                jobGroup=job_detail.get('job_group'),
                jobExecutor=job_detail.get('job_executor'),
                invokeTarget=job_detail.get('invoke_target'),
                jobArgs=job_detail.get('job_args'),
                jobKwargs=job_detail.get('job_kwargs'),
                jobTrigger=job_detail.get('job_trigger'),
                jobMessage=job_message,
                status=status,
                exceptionInfo=exception_info,
                jobResult=cls._serialize_job_result(job_result),
                startTime=normalized_start,
                endTime=datetime.now().replace(microsecond=0),
                createTime=normalized_start,
            )
            session = SessionLocal()
            JobLogService.add_job_log_services(session, job_log)
            session.close()

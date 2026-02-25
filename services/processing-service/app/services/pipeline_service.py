import logging
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings
from app.utils.file_process_util import FileProcessUtil

logger = logging.getLogger(__name__)


class PipelineService:
    DEFAULT_COLUMN_MAPPING = {
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
        '转接记录': 'transfer_record',
    }

    @classmethod
    async def process_dataset_ingested_event(cls, db: AsyncSession, event: dict) -> dict:
        object_key = event.get('object_key', '')
        if not object_key:
            raise ValueError('object_key missing in event')

        relative_key = object_key.replace('raw/', '', 1) if object_key.startswith('raw/') else object_key
        file_path = os.path.join(settings.data_lake_root, 'raw', relative_key)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'raw file not found: {file_path}')

        rows = FileProcessUtil.process_file(file_path, cls.DEFAULT_COLUMN_MAPPING)
        if not rows:
            return {'status': 'SKIPPED', 'processed_count': 0}

        columns = list(rows[0].keys())
        column_to_param = {}
        params = []
        for col in columns:
            param = col.replace('.', '_').replace(' ', '_').replace('-', '_')
            if param in column_to_param.values():
                idx = 1
                base = param
                while param in column_to_param.values():
                    param = f'{base}_{idx}'
                    idx += 1
            column_to_param[col] = param
            params.append(param)

        full_table_name = f'"{settings.target_schema}"."{settings.target_table}"'
        columns_sql = ', '.join([f'"{c}"' for c in columns])
        placeholders = ', '.join([f':{p}' for p in params])
        sql = text(f'INSERT INTO {full_table_name} ({columns_sql}) VALUES ({placeholders})')

        for row in rows:
            prepared = {}
            for col in columns:
                value = row.get(col)
                prepared[column_to_param[col]] = None if value in (None, '') else value
            await db.execute(sql, prepared)
        await db.commit()

        logger.info(
            f'processing completed: dataset_id={event.get("dataset_id")}, '
            f'job_id={event.get("ingestion_job_id")}, rows={len(rows)}'
        )
        return {'status': 'SUCCEEDED', 'processed_count': len(rows)}

from pydantic_settings import BaseSettings, SettingsConfigDict
from uuid import uuid4


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='PROCESSING_', extra='ignore')

    redis_url: str = 'redis://127.0.0.1:6379/0'
    stream_key: str = 'dataset.events'
    dlq_stream_key: str = 'dataset.events.dlq'
    consumer_group: str = 'processing-group'
    consumer_name: str = f'processing-{uuid4().hex[:8]}'
    block_ms: int = 5000
    batch_size: int = 10
    db_url: str = 'postgresql+asyncpg://flowsight:flowsight@127.0.0.1:5432/flowsight'
    data_lake_root: str = '/app/data-lake'
    target_schema: str = 'ods'
    target_table: str = 'ods_doudian_chat_session_all_dd'
    metadata_schema: str = 'ingestion'
    metadata_dataset_table: str = 'datasets'
    metadata_job_table: str = 'ingestion_jobs'
    max_retry_count: int = 3
    retry_backoff_base_seconds: int = 2
    retry_backoff_max_seconds: int = 60


settings = Settings()

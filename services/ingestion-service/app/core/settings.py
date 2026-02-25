from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='INGESTION_', extra='ignore')

    db_url: str = 'postgresql+asyncpg://flowsight:flowsight@127.0.0.1:5432/flowsight'
    db_schema: str = 'ingestion'
    redis_url: str = 'redis://127.0.0.1:6379/0'
    dataset_ingested_stream_key: str = 'dataset.events'
    event_publish_required: bool = False


settings = Settings()

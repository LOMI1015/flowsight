import logging
from typing import Dict
from app.infrastructure.database import get_db
from app.services.metadata_service import MetadataService
from app.services.pipeline_service import PipelineService

logger = logging.getLogger(__name__)


async def handle_dataset_ingested(message: Dict[str, str]) -> None:
    dataset_id = message.get('dataset_id', '-')
    dataset_version = message.get('dataset_version', 'v1')
    ingestion_job_id = message.get('ingestion_job_id', '-')
    retry_count = int(message.get('retry_count', '0'))
    logger.info(f'processing start: dataset_id={dataset_id}, version={dataset_version}, job_id={ingestion_job_id}')
    async for db in get_db():
        await MetadataService.update_job_status(
            db, ingestion_job_id=ingestion_job_id, status='RUNNING', retry_count=retry_count, last_error=''
        )
        await MetadataService.update_dataset_status(db, dataset_id=dataset_id, status='RUNNING')
        try:
            result = await PipelineService.process_dataset_ingested_event(db, message)
            await MetadataService.update_job_status(
                db, ingestion_job_id=ingestion_job_id, status='SUCCEEDED', retry_count=retry_count, last_error=''
            )
            await MetadataService.update_dataset_status(db, dataset_id=dataset_id, status='SUCCEEDED')
            logger.info(f'processing done: dataset_id={dataset_id}, job_id={ingestion_job_id}, result={result}')
            return
        except Exception as exc:
            await MetadataService.update_job_status(
                db,
                ingestion_job_id=ingestion_job_id,
                status='FAILED',
                retry_count=retry_count,
                last_error=str(exc)[:2000],
            )
            await MetadataService.update_dataset_status(db, dataset_id=dataset_id, status='FAILED')
            raise

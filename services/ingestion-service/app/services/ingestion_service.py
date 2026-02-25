from datetime import datetime, timezone
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
import os
import logging
from app.core.settings import settings
from app.infrastructure.redis_stream import RedisStreamPublisher
from app.models.ingestion_models import IngestionDataset, IngestionJob
from app.repositories.ingestion_repository import IngestionRepository
from app.schemas.dataset import DatasetCreateRequest, DatasetCreateResponse, IngestionJobStatusResponse, IngestionUploadResponse

logger = logging.getLogger(__name__)


class IngestionService:
    DATA_LAKE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data-lake/raw'))

    @staticmethod
    def _utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _build_idempotency_key(dataset_id: str, dataset_version: str, original_filename: str) -> str:
        return f'{dataset_id}:{dataset_version}:{original_filename}'

    @classmethod
    async def create_dataset(cls, db: AsyncSession, payload: DatasetCreateRequest) -> DatasetCreateResponse:
        dataset_id = uuid4().hex
        created_at = cls._utc_now_iso()
        dataset = IngestionDataset(
            dataset_id=dataset_id,
            dataset_name=payload.dataset_name,
            dataset_version=payload.dataset_version,
            status='CREATED',
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(created_at),
        )
        await IngestionRepository.create_dataset(db, dataset)
        return DatasetCreateResponse(
            dataset_id=dataset_id,
            dataset_version=payload.dataset_version,
            status='CREATED',
            created_at=created_at,
        )

    @classmethod
    async def upload_file(cls, db: AsyncSession, dataset_id: str, file: UploadFile) -> IngestionUploadResponse:
        dataset = await IngestionRepository.get_dataset_by_dataset_id(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail=f'dataset not found: {dataset_id}')

        dataset_version = dataset.dataset_version
        created_at = cls._utc_now_iso()
        original_filename = file.filename or 'unnamed.bin'
        idempotency_key = cls._build_idempotency_key(dataset_id, dataset_version, original_filename)
        existing_job = await IngestionRepository.get_ingestion_job_by_idempotency_key(db, idempotency_key)
        if existing_job:
            return IngestionUploadResponse(
                dataset_id=existing_job.dataset_id,
                dataset_version=existing_job.dataset_version,
                ingestion_job_id=existing_job.ingestion_job_id,
                status=existing_job.status,
                filename=existing_job.filename,
                object_key=existing_job.object_key,
                file_size=existing_job.file_size,
                created_at=existing_job.created_at.isoformat(),
            )

        object_dir = os.path.join(cls.DATA_LAKE_ROOT, dataset_id, dataset_version)
        os.makedirs(object_dir, exist_ok=True)
        object_name = f'{created_at.replace(":", "").replace("-", "").replace(".", "")}_{original_filename}'
        object_key = f'raw/{dataset_id}/{dataset_version}/{object_name}'
        file_path = os.path.join(object_dir, object_name)

        file_content = await file.read()
        with open(file_path, 'wb') as fs:
            fs.write(file_content)

        file_size = len(file_content)
        ingestion_job_id = uuid4().hex
        job = IngestionJob(
            ingestion_job_id=ingestion_job_id,
            idempotency_key=idempotency_key,
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            status='PENDING',
            filename=original_filename,
            object_key=object_key,
            file_size=file_size,
            retry_count=0,
            last_error='',
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(created_at),
        )
        await IngestionRepository.create_ingestion_job(db, job)
        dataset.status = 'PENDING'
        dataset.updated_at = datetime.fromisoformat(created_at)
        await IngestionRepository.update_dataset(db, dataset)

        stream_event = {
            'event_type': 'dataset.ingested',
            'event_id': uuid4().hex,
            'occurred_at': created_at,
            'dataset_id': dataset_id,
            'dataset_version': dataset_version,
            'ingestion_job_id': ingestion_job_id,
            'object_key': object_key,
            'file_size': file_size,
            'status': 'PENDING',
        }
        try:
            await RedisStreamPublisher.publish_dataset_ingested(stream_event)
        except Exception as exc:
            logger.exception(f'publish dataset.ingested failed: {exc}')
            if settings.event_publish_required:
                raise HTTPException(status_code=503, detail='publish dataset.ingested failed') from exc

        return IngestionUploadResponse(
            dataset_id=job.dataset_id,
            dataset_version=job.dataset_version,
            ingestion_job_id=job.ingestion_job_id,
            status=job.status,
            filename=job.filename,
            object_key=job.object_key,
            file_size=job.file_size,
            created_at=job.created_at.isoformat(),
        )

    @classmethod
    async def get_ingestion_status(
        cls, db: AsyncSession, dataset_id: str, ingestion_job_id: str
    ) -> IngestionJobStatusResponse:
        job = await IngestionRepository.get_ingestion_job_by_job_id(db, ingestion_job_id)
        if not job or job.dataset_id != dataset_id:
            raise HTTPException(status_code=404, detail='ingestion job not found')
        return IngestionJobStatusResponse(
            dataset_id=job.dataset_id,
            ingestion_job_id=job.ingestion_job_id,
            status=job.status,
            filename=job.filename,
            object_key=job.object_key,
            file_size=job.file_size,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
        )

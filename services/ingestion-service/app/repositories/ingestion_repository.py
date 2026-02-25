from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ingestion_models import IngestionDataset, IngestionJob


class IngestionRepository:
    @staticmethod
    async def create_dataset(db: AsyncSession, dataset: IngestionDataset) -> IngestionDataset:
        db.add(dataset)
        await db.flush()
        await db.commit()
        await db.refresh(dataset)
        return dataset

    @staticmethod
    async def get_dataset_by_dataset_id(db: AsyncSession, dataset_id: str) -> IngestionDataset | None:
        result = await db.execute(select(IngestionDataset).where(IngestionDataset.dataset_id == dataset_id))
        return result.scalars().first()

    @staticmethod
    async def update_dataset(db: AsyncSession, dataset: IngestionDataset) -> IngestionDataset:
        await db.flush()
        await db.commit()
        await db.refresh(dataset)
        return dataset

    @staticmethod
    async def create_ingestion_job(db: AsyncSession, job: IngestionJob) -> IngestionJob:
        db.add(job)
        await db.flush()
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def get_ingestion_job_by_job_id(db: AsyncSession, ingestion_job_id: str) -> IngestionJob | None:
        result = await db.execute(select(IngestionJob).where(IngestionJob.ingestion_job_id == ingestion_job_id))
        return result.scalars().first()

    @staticmethod
    async def get_ingestion_job_by_idempotency_key(db: AsyncSession, idempotency_key: str) -> IngestionJob | None:
        result = await db.execute(select(IngestionJob).where(IngestionJob.idempotency_key == idempotency_key))
        return result.scalars().first()

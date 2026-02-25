from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings


class MetadataService:
    @staticmethod
    def _utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    async def update_job_status(
        cls,
        db: AsyncSession,
        ingestion_job_id: str,
        status: str,
        retry_count: int | None = None,
        last_error: str | None = None,
    ) -> None:
        update_sql = text(
            f"""
            UPDATE "{settings.metadata_schema}"."{settings.metadata_job_table}"
            SET status = :status,
                retry_count = COALESCE(:retry_count, retry_count),
                last_error = COALESCE(:last_error, last_error),
                updated_at = :updated_at
            WHERE ingestion_job_id = :ingestion_job_id
            """
        )
        await db.execute(
            update_sql,
            {
                'status': status,
                'retry_count': retry_count,
                'last_error': last_error,
                'updated_at': datetime.fromisoformat(cls._utc_now_iso()),
                'ingestion_job_id': ingestion_job_id,
            },
        )
        await db.commit()

    @classmethod
    async def update_dataset_status(cls, db: AsyncSession, dataset_id: str, status: str) -> None:
        update_sql = text(
            f"""
            UPDATE "{settings.metadata_schema}"."{settings.metadata_dataset_table}"
            SET status = :status,
                updated_at = :updated_at
            WHERE dataset_id = :dataset_id
            """
        )
        await db.execute(
            update_sql,
            {
                'status': status,
                'updated_at': datetime.fromisoformat(cls._utc_now_iso()),
                'dataset_id': dataset_id,
            },
        )
        await db.commit()

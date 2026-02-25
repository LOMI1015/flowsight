from datetime import datetime
from sqlalchemy import DateTime, Integer, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.core.settings import settings
from app.infrastructure.database import Base


class IngestionDataset(Base):
    __tablename__ = 'datasets'
    __table_args__ = {'schema': settings.db_schema}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dataset_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    dataset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(64), nullable=False, default='v1')
    status: Mapped[str] = mapped_column(String(32), nullable=False, default='CREATED')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class IngestionJob(Base):
    __tablename__ = 'ingestion_jobs'
    __table_args__ = {'schema': settings.db_schema}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ingestion_job_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    dataset_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    dataset_version: Mapped[str] = mapped_column(String(64), nullable=False, default='v1')
    status: Mapped[str] = mapped_column(String(32), nullable=False, default='PENDING')
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    object_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str] = mapped_column(String(2000), nullable=False, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

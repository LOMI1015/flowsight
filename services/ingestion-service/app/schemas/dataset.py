from pydantic import BaseModel, Field
from typing import Optional


class DatasetCreateRequest(BaseModel):
    dataset_name: str = Field(..., description='数据集名称')
    dataset_version: str = Field(default='v1', description='数据集版本')


class DatasetCreateResponse(BaseModel):
    dataset_id: str
    dataset_version: str
    status: Optional[str] = 'CREATED'
    created_at: Optional[str] = None


class IngestionUploadResponse(BaseModel):
    dataset_id: str
    dataset_version: str
    ingestion_job_id: str
    status: str
    filename: str
    object_key: str
    file_size: int
    created_at: Optional[str] = None


class IngestionJobStatusResponse(BaseModel):
    dataset_id: str
    ingestion_job_id: str
    status: str
    filename: str
    object_key: str
    file_size: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

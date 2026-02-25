from pydantic import BaseModel, Field
from typing import Optional


class WorkflowCreateRequest(BaseModel):
    dataset_id: str = Field(..., description='数据集 ID')
    dataset_version: str = Field(default='v1', description='数据集版本')
    trigger_source: Optional[str] = Field(default='ingestion', description='触发来源')


class WorkflowStatusResponse(BaseModel):
    workflow_job_id: str
    dataset_id: str
    dataset_version: str
    status: str
    retry_count: int = 0
    created_at: str
    updated_at: str

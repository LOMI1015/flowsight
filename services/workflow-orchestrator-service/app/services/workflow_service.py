from datetime import datetime, timezone
from fastapi import HTTPException
from typing import Dict
from uuid import uuid4
from app.schemas.workflow import WorkflowCreateRequest, WorkflowStatusResponse

_workflow_store: Dict[str, dict] = {}


class WorkflowService:
    @staticmethod
    def _utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    async def create_workflow_job(cls, payload: WorkflowCreateRequest) -> WorkflowStatusResponse:
        now = cls._utc_now_iso()
        workflow_job_id = uuid4().hex
        _workflow_store[workflow_job_id] = {
            'workflow_job_id': workflow_job_id,
            'dataset_id': payload.dataset_id,
            'dataset_version': payload.dataset_version,
            'status': 'PENDING',
            'retry_count': 0,
            'created_at': now,
            'updated_at': now,
            'trigger_source': payload.trigger_source,
        }
        return WorkflowStatusResponse(**_workflow_store[workflow_job_id])

    @classmethod
    async def get_workflow_job_status(cls, workflow_job_id: str) -> WorkflowStatusResponse:
        job = _workflow_store.get(workflow_job_id)
        if not job:
            raise HTTPException(status_code=404, detail='workflow job not found')
        return WorkflowStatusResponse(**job)

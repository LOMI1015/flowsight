from fastapi import APIRouter
from app.schemas.workflow import WorkflowCreateRequest, WorkflowStatusResponse
from app.services.workflow_service import WorkflowService

router = APIRouter()


@router.get('/healthz')
async def health_check():
    return {'status': 'ok', 'service': 'workflow-orchestrator-service'}


@router.post('/workflows', response_model=WorkflowStatusResponse)
async def create_workflow(payload: WorkflowCreateRequest):
    return await WorkflowService.create_workflow_job(payload)


@router.get('/workflows/{workflow_job_id}', response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_job_id: str):
    return await WorkflowService.get_workflow_job_status(workflow_job_id)

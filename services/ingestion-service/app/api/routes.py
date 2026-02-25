from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.schemas.dataset import DatasetCreateRequest, DatasetCreateResponse, IngestionJobStatusResponse, IngestionUploadResponse
from app.services.ingestion_service import IngestionService

router = APIRouter()


@router.get('/healthz')
async def health_check():
    return {'status': 'ok', 'service': 'ingestion-service'}


@router.post('/datasets', response_model=DatasetCreateResponse)
async def create_dataset(payload: DatasetCreateRequest, db: AsyncSession = Depends(get_db)):
    return await IngestionService.create_dataset(db, payload)


@router.post('/datasets/{dataset_id}/upload', response_model=IngestionUploadResponse)
async def upload_dataset_file(dataset_id: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    return await IngestionService.upload_file(db, dataset_id, file)


@router.get('/datasets/{dataset_id}/ingestions/{ingestion_job_id}', response_model=IngestionJobStatusResponse)
async def get_ingestion_job_status(
    dataset_id: str, ingestion_job_id: str, db: AsyncSession = Depends(get_db)
):
    return await IngestionService.get_ingestion_status(db, dataset_id, ingestion_job_id)

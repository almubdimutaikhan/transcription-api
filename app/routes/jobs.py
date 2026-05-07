from fastapi import APIRouter, Path, HTTPException, Depends
from typing import Annotated
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import TranscriptionJob
from app.dependencies import get_db
from app.schemas.jobs import JobCreate, JobResponse

router = APIRouter(prefix='/jobs', tags=['jobs'])

@router.post('/', status_code=201, response_model=JobResponse)
async def create_job(payload: JobCreate, db: AsyncSession = Depends(get_db)):
    job = TranscriptionJob(**payload.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)

    return JobResponse.model_validate(job)

@router.get('/{job_id}', response_model=JobResponse)
async def find_job(job_id: Annotated[UUID, Path(description="Job UUID")], db: AsyncSession = Depends(get_db)):
    job = await db.get(TranscriptionJob, job_id)

    if job is None:
        raise HTTPException(status_code=404, detail='Job not found')

    return JobResponse.model_validate(job)

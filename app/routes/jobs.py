from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import Annotated
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.dependencies import get_db, get_current_user, PaginationParams
from app.models.job import TranscriptionJob
from app.schemas.jobs import JobCreate, JobRead, JobListResponse, JobStatus, JobStatusUpdate
from worker.celery_app import transcribe_audio

router = APIRouter(prefix='/jobs', tags=['jobs'])


@router.post('/', status_code=201, response_model=JobRead)
async def create_job(
    payload: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    job = TranscriptionJob(user_id=current_user.id, **payload.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)

    transcribe_audio.delay(str(job.id))
    return JobRead.model_validate(job)


@router.get('/', response_model=JobListResponse)
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    pagination: PaginationParams = Depends(),
    status: JobStatus | None = Query(None),
):
    base = (
        select(TranscriptionJob)
        .where(
            TranscriptionJob.user_id == current_user.id,
            TranscriptionJob.deleted_at.is_(None),
        )
    )
    if status:
        base = base.where(TranscriptionJob.status == status.value)

    total = await db.scalar(select(func.count()).select_from(base.subquery()))
    rows = await db.scalars(base.offset(pagination.offset).limit(pagination.size))

    return JobListResponse(
        items=[JobRead.model_validate(j) for j in rows],
        total=total or 0,
        page=pagination.page,
        size=pagination.size,
    )


@router.get('/{job_id}', response_model=JobRead)
async def get_job(
    job_id: Annotated[UUID, Path(description='Job UUID')],
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    job = await db.get(TranscriptionJob, job_id)
    if job is None or job.deleted_at is not None or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail='Job not found')
    return JobRead.model_validate(job)


@router.patch('/{job_id}/status', response_model=JobRead)
async def update_job_status(
    job_id: Annotated[UUID, Path(description='Job UUID')],
    payload: JobStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    job = await db.get(TranscriptionJob, job_id)
    if job is None or job.deleted_at is not None or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail='Job not found')
    job.status = payload.status.value
    await db.commit()
    await db.refresh(job)
    return JobRead.model_validate(job)


@router.delete('/{job_id}', status_code=204)
async def delete_job(
    job_id: Annotated[UUID, Path(description='Job UUID')],
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    job = await db.get(TranscriptionJob, job_id)
    if job is None or job.deleted_at is not None or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail='Job not found')
    job.deleted_at = datetime.now(timezone.utc)
    await db.commit()

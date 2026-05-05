from fastapi import APIRouter, Path, HTTPException
from typing import Annotated
from pydantic import BaseModel, Field
from enum import Enum
from uuid import UUID, uuid4
router = APIRouter(prefix='/jobs', tags=['jobs'])


class Language(str, Enum):
    EN = 'en'
    KZ = 'kz'
    RU = 'ru'
    PL = 'pl'

class JobCreate(BaseModel):
    language: str
    audio_url: Annotated[str, Field(min_length=10)]
    priority: Annotated[int, Field(default=0, le=3, title="Job priority", description="When processing on queue less priority number means higher priority")]
    

class Job(JobCreate):
    id: UUID = Field(default_factory=uuid4)


@router.post('/', status_code=201)
async def create_job(payload: JobCreate) -> Job:
    return Job(**payload.model_dump())


@router.get('/{job_id}')
async def find_job(job_id: Annotated[UUID, Path(description="Job's UUID")]) -> Job:
    raise HTTPException(status_code=404, detail="Job not found")


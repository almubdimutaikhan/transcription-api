from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated
from uuid import UUID
from datetime import datetime
from enum import Enum


class Language(str, Enum):
    EN = 'en'
    KZ = 'kz'
    RU = 'ru'
    PL = 'pl'


class JobStatus(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'


class JobCreate(BaseModel):
    language: Language
    audio_url: Annotated[str, Field(min_length=10)]
    file_ext: Annotated[str, Field(min_length=2, max_length=10)]
    priority: Annotated[int, Field(default=1, ge=1, le=5)]


class JobResponse(BaseModel):
    model_config = {'from_attributes': True}

    id: UUID
    user_id: UUID
    status: JobStatus
    language: Language
    file_ext: str
    audio_url: str
    transcription_text: str | None
    priority: int
    created_at: datetime
    updated_at: datetime
    finished_at: datetime | None

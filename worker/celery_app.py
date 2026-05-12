from celery import Celery
from app.config import settings
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC"
)

sync_engine = create_engine(
    settings.database_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
)

@celery_app.task()
def transcribe_audio(job_id: str):
    from app.models.job import TranscriptionJob
    from uuid import UUID
    from datetime import datetime, timezone

    with Session(sync_engine) as session:
        job = session.get(TranscriptionJob, UUID(job_id))
        job.status = "processing"
        session.commit()

    sleep(5)  # simulate transcription

    with Session(sync_engine) as session:
        job = session.get(TranscriptionJob, UUID(job_id))
        job.status = "completed"
        job.transcription_text = "This is a sample transcription."
        job.finished_at = datetime.now(timezone.utc)
        session.commit()
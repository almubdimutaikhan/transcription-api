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
    timezone="UTC",
)

sync_engine = create_engine(
    settings.database_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
)


@celery_app.task(bind=True, max_retries=3)
def transcribe_audio(self, job_id: str):
    from app.models.job import TranscriptionJob
    from uuid import UUID
    from datetime import datetime, timezone

    uuid = UUID(job_id)

    try:
        with Session(sync_engine) as session:
            job = session.get(TranscriptionJob, uuid)
            if job is None:
                return

            job.status = "processing"
            session.commit()

        sleep(5)  # simulate transcription

        with Session(sync_engine) as session:
            job = session.get(TranscriptionJob, uuid)
            if job is None:
                return
            job.status = "completed"
            job.transcription_text = "This is a sample transcription."
            job.finished_at = datetime.now(timezone.utc)
            session.commit()

    except Exception as exc:
        with Session(sync_engine) as session:
            job = session.get(TranscriptionJob, uuid)
            if job:
                job.status = "failed"
                session.commit()
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

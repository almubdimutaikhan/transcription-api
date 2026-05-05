from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import CheckConstraint


class TranscriptionJob(Base):
    __tablename__ = 'transcription_jobs'

    __table_args__ = (
        CheckConstraint("status IN ('pending','processing','completed','failed')", name='valid_status'),
        CheckConstraint('priority BETWEEN 1 AND 5', name='valid_priority'),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), index=True)
    status: Mapped[str] = mapped_column(String(25), default='pending', index=True)
    language: Mapped[str] = mapped_column(String(5))
    file_ext: Mapped[str] = mapped_column(String(10))
    audio_url: Mapped[str] = mapped_column(Text)
    transcription_text: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

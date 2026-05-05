from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from uuid import UUID, uuid4
from datetime import datetime


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), index=True)
    job_id: Mapped[UUID | None] = mapped_column(ForeignKey('transcription_jobs.id'), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    action: Mapped[str] = mapped_column(String(255))
    extra: Mapped[dict | None] = mapped_column(JSONB)

from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import CheckConstraint


class User(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    token_balance: Mapped[int] = mapped_column(Integer, CheckConstraint("token_balance >= 0"), default=100)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
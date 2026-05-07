from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]


class UserResponse(BaseModel):
    model_config = {'from_attributes': True}

    id: UUID
    email: EmailStr
    token_balance: int
    is_active: bool
    created_at: datetime

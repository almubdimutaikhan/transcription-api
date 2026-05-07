from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt

from app.dependencies import get_db
from app.models.user import User
from app.schemas.users import UserCreate, UserResponse

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=201, response_model=UserResponse)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail='Email already registered')

    user = User(
        email=payload.email,
        hashed_password=bcrypt.hashpw(payload.password.encode(), bcrypt.gensalt()).decode(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.get('/{email}', response_model=UserResponse)
async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == email))
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')

    return UserResponse.model_validate(user)

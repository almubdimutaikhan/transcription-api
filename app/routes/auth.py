from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.models.user import User
from app.auth import hash_password, verify_password, create_access_token
from app.schemas.users import UserCreate, UserRead, Token, LoginRequest

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', status_code=201, response_model=UserRead)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail='Email already registered')

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)


@router.post('/token', response_model=Token)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect email or password')
    if not user.is_active:
        raise HTTPException(status_code=403, detail='Account is inactive')

    return Token(access_token=create_access_token(str(user.id)))

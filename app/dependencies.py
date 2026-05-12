from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from uuid import UUID

import app.database as _db
from app.auth import decode_token

bearer_scheme = HTTPBearer()


async def get_db():
    async with _db.AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import User
    credentials_error = HTTPException(status_code=401, detail='Invalid or expired token')
    try:
        user_id = decode_token(credentials.credentials)
    except JWTError:
        raise credentials_error

    user = await db.get(User, UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_error
    return user


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
    ):
        self.page = page
        self.size = size
        self.offset = (page - 1) * size

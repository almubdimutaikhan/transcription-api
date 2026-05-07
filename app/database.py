from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings

engine = create_async_engine(settings.database_url, pool_size=10, max_overflow=20, echo=settings.environment=='development')

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False  # avoid errors with memory commmit
)


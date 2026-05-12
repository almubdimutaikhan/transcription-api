from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    environment: str = 'development'
    jwt_secret: str
    jwt_algorithm: str = 'HS256'
    jwt_expiry_minutes: int = 30
    redis_url: str = "redis://redis:6379/0"

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:12345@localhost:5432/internship_db"
    JWT_SECRET: str = "supersecretkey123"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
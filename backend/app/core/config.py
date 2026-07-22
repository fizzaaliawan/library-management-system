import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load active environment file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Library Management System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/library_db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretjwtkeythatisextremelysecure123!")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    class Config:
        case_sensitive = True

settings = Settings()

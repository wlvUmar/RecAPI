from pydantic_settings import BaseSettings
from typing import ClassVar
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Movie Recommendation API"
    PROJECT_DESCRIPTION: str = """Movie Recommendation Microservice

    An educational microservice built to demonstrate movie recommendations for portfolio purposes.

    Features:
    - Content-based recommendations using metadata and embeddings
    - User authentication with JWT and movie-like tracking
    - CRUD endpoints for movies and users
    - Vector generation via Sentence Transformers
    - Asynchronous FastAPI + SQLAlchemy stack
    - Fully tested with Pytest

    Note: This project is for learning/demo use only, not production-ready.
    """

    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    PG_DB_URL: str = "postgresql+asyncpg://postgres:getout04@localhost:5433/postgres"
    PG_TEST_URL: str = "postgresql+asyncpg://postgres:getout04@localhost:5433/postgres_test"

    SQLITE_DB_URL: str = "sqlite+aiosqlite:///./movies.db"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "securepass"
    SECRET_KEY:str = "your-secret-key"
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
settings = Settings()   
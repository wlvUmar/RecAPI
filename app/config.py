from pydantic_settings import BaseSettings
from typing import ClassVar
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Movie Recommendation API"
    PROJECT_DESCRIPTION: str = """
## Movie Recommendation Microservice

This microservice demonstrates a simple yet effective approach to movie recommendations, built for portfolio showcase.

Features include:
- Content-based recommendations using movie metadata and keywords.
- Neural network embeddings for enhanced recommendation quality.
- Endpoints for movie search, lookup, creation, and personalized recommendations.
- Lightweight design focused on educational and demonstration purposes, not production-scale.

Built with FastAPI, async SQLAlchemy, and Sentence Transformers for embedding text data.
"""
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    PG_DB_URL: str = "postgresql+asyncpg://postgres:getout04@localhost:5433/postgres"
    SQLITE_DB_URL: str = "sqlite+aiosqlite:///./movies.db"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "securepass"
    SECRET_KEY:str = "your-secret-key"
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
settings = Settings()   
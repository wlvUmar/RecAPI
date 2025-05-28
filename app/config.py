from pydantic_settings import BaseSettings
import os

db_url = os.getenv("DATABASE_URL")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Movie Recommendation API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql+asyncpg://recapi:SuLKZxe4m2Tm7TI@recapi-db.flycast:5432/recapi?sslmode=disable"

settings = Settings() 
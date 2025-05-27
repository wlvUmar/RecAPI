from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Movie Recommendation API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgres+asyncpg://postgres:zSupTsJT4miboAy@crimson-sea-6932.flycast:5432"

settings = Settings() 
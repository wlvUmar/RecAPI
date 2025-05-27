from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel
import json
import ast
import logging

logger = logging.getLogger("uvicorn.error")

def parse_stringified_list(s):
    if not isinstance(s, str):
        logger.warn("Not a string, returning as is")
        return s
    try:
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        try:
            result = ast.literal_eval(s)
            return result
        except Exception as e:
            logger.warn(f"ast.literal_eval failed for {s!r}: {e}")
            try:
                result = json.loads(s.replace("'", '"'))
                return result
            except Exception as e2:
                logger.warn(f"json.loads fallback failed for {s!r}: {e2}")
                return []
    except Exception as e:
        logger.error(f"Unexpected error parsing {s!r}: {e}")
        return []

class MovieLite(BaseModel):
    id: UUID
    title: str
    release_year: Optional[int] = None


class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    genres: List[str] = []
    tags: List[str] = []
    release_year: Optional[int] = None
    director: Optional[str] = None
    actors: List[str] = []

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: UUID
    vector: Optional[List[float]] = None

    class Config:
        from_attributes = True

class MovieRecommendationRequest(BaseModel):
    liked_movie_ids: List[str]

class DBSyncRequest(BaseModel):
    host: str
    port: int
    user: str
    password: str
    db_name: str 
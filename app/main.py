import pandas as pd
from uuid import uuid4
import os
from pathlib import Path

from fastapi import FastAPI

from app.config import settings
from app.api import router, vectorize
from app.db import engine, AsyncSessionLocal, Base, Movie as DBMovie
from app.schemas import Movie, MovieCreate, parse_stringified_list


DB_PATH = Path(__file__).resolve().parent.parent / "movies.db"

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)


@app.on_event("startup")
async def startup():
    if os.path.exists(DB_PATH):
        return  # DB already exists, skip startup logic

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    df = pd.read_csv("processed_movies.csv")

    for col in ['genres', 'tags', 'actors']:
        df[col] = df[col].apply(parse_stringified_list)

    async with AsyncSessionLocal() as session:
        for _, row in df.iterrows():
            movie_data = row.to_dict()
            movie_create = MovieCreate(**movie_data)
            db_movie = DBMovie(
                id=uuid4(),
                title=row['title'],
                description=row['description'],
                genres=row['genres'],
                tags=row['tags'],
                release_year=row['release_year'],
                director=row['director'],
                actors=row['actors'],
                vector=vectorize(movie_create).tolist()
            )
            session.add(db_movie)
        await session.commit()
app.include_router(router, prefix=settings.API_V1_STR) 
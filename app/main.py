import pandas as pd
from uuid import uuid4
import os
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy import select
from app.config import settings
from app.api import *
from app.db import engine, AsyncSessionLocal, Base, Movie as DBMovie
from app.schemas import Movie, MovieCreate, parse_stringified_list
from app.utils import vectorize

DB_PATH = Path(__file__).resolve().parent.parent / "movies.db"

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
)

@app.get("/")
async def root():
    return {"code" : 200, "message": "success"}
    
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    df = pd.read_csv("processed_movies.csv")
    for col in ['genres', 'tags', 'actors']:
        df[col] = df[col].apply(parse_stringified_list)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DBMovie).limit(1))
        exists = result.scalar_one_or_none()
        if exists:
            return
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
app.include_router(user_router)
app.include_router(movie_router)
app.include_router(auth_router) 
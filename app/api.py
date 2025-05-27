import logging
from uuid import UUID

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db, Movie as MovieTable
from app.schemas import *
from app.recommendation import recommend

logger = logging.getLogger("uvicorn.error")
model = SentenceTransformer("all-MiniLM-L6-v2")  


router = APIRouter()

@router.post("/recommend", response_model=List[MovieLite])
async def get_recommendations(request: MovieRecommendationRequest, db: AsyncSession = Depends(get_db), limit: int = Query(10, ge=1, le=100)):
    if not isinstance(request.liked_movie_ids, list) or not request.liked_movie_ids:
        raise HTTPException(status_code=400, detail="liked_movie_ids must be a non-empty list.")

    try:
        valid_ids = [UUID(id_) for id_ in request.liked_movie_ids]
    except ValueError as ve:
        logger.warning(f"Invalid UUID in request: {request.liked_movie_ids}")
        raise HTTPException(status_code=422, detail="All liked_movie_ids must be valid UUIDs.")
    try:
        recommendations = await recommend(valid_ids, db, limit)
        if not recommendations:
            raise HTTPException(status_code=404, detail="No recommendations found for provided movies.")
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Internal error during recommendation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while generating recommendations.")
@router.get("/movies", response_model=List[Movie])
async def list_movies(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(MovieTable))
        movies = result.scalars().all()
        if not movies:
            raise HTTPException(status_code=404, detail="No movies found.")
        return movies
    except SQLAlchemyError as e:
        logger.exception("Database error while listing movies.")
        raise HTTPException(status_code=500, detail="Database error while listing movies.")


@router.get("/movies/lookup", response_model=List[MovieLite])
async def get_movies_lookup(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(MovieTable.id, MovieTable.title, MovieTable.release_year))
        lookup = result.all()
        if not lookup:
            raise HTTPException(status_code=404, detail="No movies available for lookup.")
        return lookup
    except SQLAlchemyError as e:
        logger.exception("Error fetching movie lookup data.")
        raise HTTPException(status_code=500, detail="Error fetching movie lookup data.")


@router.post("/movies", response_model=Movie)
async def create_movie(movie: MovieCreate, db: AsyncSession = Depends(get_db)):
    try:
        if not movie.title or not movie.description:
            raise HTTPException(status_code=400, detail="Title and description are required.")
        
        vector = vectorize(movie)
        db_movie = MovieTable(**movie.model_dump(), vector=vector.tolist())
        db.add(db_movie)
        await db.commit()
        await db.refresh(db_movie)
        return db_movie

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.exception("Database error while creating movie.")
        raise HTTPException(status_code=500, detail="Database error while creating movie.")
    except Exception as e:
        logger.exception("Unexpected error while creating movie.")
        raise HTTPException(status_code=500, detail="Unexpected error while creating movie.")

def vectorize(movie: MovieCreate):
    parts = []

    if movie.title:
        parts.append(f"Title: {movie.title}.")
    if movie.description:
        parts.append(f"Description: {movie.description}.")
    if movie.genres:
        parts.append(f"Genres: {', '.join(movie.genres)}.")
    if movie.tags:
        parts.append(f"Tags: {', '.join(movie.tags)}.")
    if movie.director:
        parts.append(f"Director: {movie.director}.")
    if movie.actors:
        parts.append(f"Actors: {', '.join(movie.actors)}.")

    text_content = " ".join(parts)
    vector = model.encode(text_content)
    return vector
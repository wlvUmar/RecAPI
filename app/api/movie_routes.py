import logging
from uuid import UUID

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db, Movie as MovieTable
from app.schemas import *
from app.recommendation import recommend
from app.utils import get_current_admin, vectorize

logger = logging.getLogger("uvicorn.error")
 


router = APIRouter(
    prefix="/movies",
    tags=["Movies"],
    dependencies=[Depends(get_current_admin)])

@router.post("/recommend", response_model=List[MovieLite])
async def get_recommendations(
    request: MovieRecommendationRequest, 
    db: AsyncSession = Depends(get_db), 
    limit: int = Query(10, ge=1, le=100)):
    """
    Recommend movies based on user liked movies.

    - **liked_movie_ids**: List of UUIDs for movies the user liked.
    - **limit**: Max number of recommendations to return (default 10, max 100).

    Returns a list of recommended movies similar to liked ones.
    Raises errors for invalid input or no recommendations found.
    """

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
async def list_movies(
    db:AsyncSession = Depends(get_db)):
    """
    Get all movies in the database.

    Returns a list of movies with full details.
    Returns 404 if no movies exist.
    """

    try:
        result = await db.execute(select(MovieTable))
        movies = result.scalars().all()
        if not movies:
            raise HTTPException(status_code=404, detail="No movies found.")
        return movies
    except SQLAlchemyError as e:
        logger.exception("Database error while listing movies.")
        raise HTTPException(status_code=500, detail="Database error while listing movies.")

@router.get("/movie", response_model=MovieBase)
async def get_movie_by_idx(
    movie_id: UUID = Query(...), 
    db: AsyncSession = Depends(get_db)):
    """
    Retrieve detailed info for a movie by its UUID.

    - **movie_id**: UUID of the requested movie.

    Returns the movie details or 404 if not found.
    """

    try:
        query = text("""
            SELECT id, title, description, genres, tags, release_year, director, actors 
            FROM movies 
            WHERE id = :id
        """)
        result = (await db.execute(query, {"id": str(movie_id)})).first()
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        return dict(result._mapping)
    except SQLAlchemyError as e:
        logger.exception(f"DB error fetching movie with id {movie_id}")
        raise HTTPException(status_code=500, detail="Database error")



@router.get("/movies/lookup", response_model=List[MovieLite])
async def get_movies_lookup(
    db: AsyncSession = Depends(get_db)):
    """
    Get lightweight movie lookup data.

    Returns a list of movies with id, title, and release year.
    Used for fast lookup or selection lists.
    Returns 404 if no movies available.
    """

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
async def create_movie(
    movie: MovieCreate, 
    db: AsyncSession = Depends(get_db)):
    """
    Create a new movie entry.

    - Requires **title** and **description** fields.
    - Generates vector embedding from movie info.
    - Saves to database and returns created movie.

    Raises validation or database errors.
    """

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


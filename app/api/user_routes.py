import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db, UserLikedMovie, Movie as MovieTable
from app.schemas import *
from app.utils import get_current_admin
logger = logging.getLogger("uvicorn.error")

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_admin)])



@router.post("/{user_id}/likes", status_code=201)
async def add_liked_movie(
    user_id: UUID, 
    movie_id: UUID, 
    session: AsyncSession = Depends(get_db)):
    
    """
    Add a movie to the user's liked list.
    Request body: JSON with movie_id (UUID).
    Returns confirmation message.
    """
    
    # Check if movie exists
    movie = await session.get(MovieTable, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    exists = await session.get(UserLikedMovie, (user_id, movie_id))
    if exists:
        raise HTTPException(status_code=400, detail="Movie already liked")
    liked = UserLikedMovie(user_id=user_id, movie_id=movie_id)
    session.add(liked)
    await session.commit()
    return {"message": "Movie liked"}

@router.delete("/{user_id}/likes/{movie_id}", status_code=204)
async def remove_liked_movie(
    user_id: UUID, 
    movie_id: UUID, 
    session: AsyncSession = Depends(get_db)):
    
    """
    Remove a movie from the user's liked list by movie ID.
    Returns 204 No Content on success.
    """
    
    liked = await session.get(UserLikedMovie, (user_id, movie_id))
    if not liked:
        raise HTTPException(status_code=404, detail="Liked movie not found")
    await session.delete(liked)
    await session.commit()

@router.get("/{user_id}/likes", response_model=List[UUID])
async def list_liked_movies(user_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Retrieve a list of all movie IDs liked by the user.
    Returns a list of UUIDs.
    """

    result = await session.execute(select(UserLikedMovie.movie_id).where(UserLikedMovie.user_id == user_id))
    movie_ids = result.scalars().all()
    return movie_ids

@router.put("/{user_id}/likes")
async def update_liked_movies(user_id: UUID, movie_ids: List[UUID], session: AsyncSession = Depends(get_db)):
    """
    Replace the user's liked movies with a new list.
    Request body: JSON array of movie IDs (UUID).
    Returns confirmation message.
    """
    # Delete existing
    await session.execute(
        UserLikedMovie.__table__.delete().where(UserLikedMovie.user_id == user_id)
    )
    # Add new liked movies
    liked_list = [UserLikedMovie(user_id=user_id, movie_id=mid) for mid in movie_ids]
    session.add_all(liked_list)
    await session.commit()
    return {"message": "Liked movies updated"}
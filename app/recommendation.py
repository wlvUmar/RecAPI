from typing import List
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy import literal
from sqlalchemy.orm import load_only
from app.db import Movie
import logging

logger = logging.getLogger("uvicorn.error")

async def recommend(liked_movie_ids: List[str], db: AsyncSession, limit=10, by="content") -> List[dict]:
    
    try:
        if by == "content":
            result = await db.execute(
                select(Movie.vector).where(Movie.id.in_(liked_movie_ids))
            )
            vectors = [row[0] for row in result if row[0] is not None]
            if not vectors:
                logger.warning("No valid vectors found for liked movies.")
                return []

            avg_vector = np.mean(vectors, axis=0).tolist()

            stmt = (
                select(Movie.id, Movie.title, Movie.release_year)
                .where(~Movie.id.in_(liked_movie_ids))
                .order_by(Movie.vector.op('<->')(literal(avg_vector)))
                .limit(limit)
            )
            result = await db.execute(stmt)
            movies = result.all()
            return [{"id": mid, "title": title, "release_year": year} for mid, title, year in movies]
        if by == "latest":
            stmt = select(Movie.id, Movie.title, Movie.release_year).order_by(Movie.release_year.desc()).limit(limit)
            result = await db.execute(stmt) 
            movies = result.all()
            return [{"id": mid, "title": title, "release_year": year} for mid, title, year in movies]
        if by == "popularity":
        
            result = await db.execute(
            select(Movie, func.count(UserLikedMovie.user_id).label("popularity"))
            .join(UserLikedMovie, Movie.id == UserLikedMovie.movie_id)
            .group_by(Movie.id)
            .order_by(desc("popularity"))
            .limit(limit)
            )
            popular_movies = result.scalars().all() 
            return popular_movies if popular_movies else {"msg": "no user interactions yet"}
        if by == "user_based":
            subq = (
                select(UserLikedMovie.user_id)
                .where(UserLikedMovie.movie_id.in_(liked_movie_ids))
                .subquery()
            )
            stmt = (
                select(Movie.id, Movie.title, Movie.release_year, func.count(UserLikedMovie.user_id).label("score"))
                .join(UserLikedMovie, Movie.id == UserLikedMovie.movie_id)
                .where(UserLikedMovie.user_id.in_(subq))
                .where(~Movie.id.in_(liked_movie_ids))
                .group_by(Movie.id)
                .order_by(desc("score"))
                .limit(limit)
            )
            result = await db.execute(stmt)
            movies = result.all()
            return [{"id": mid, "title": title, "release_year": year} for mid, title, year, _ in movies]

        if by == "hybrid":
            content_res = await recommend(liked_movie_ids, db, limit*2, by="content")
            content_ids = {m['id'] for m in content_res}
            pop_stmt = (
                select(Movie.id, Movie.title, Movie.release_year, func.count(UserLikedMovie.user_id).label("popularity"))
                .join(UserLikedMovie, Movie.id == UserLikedMovie.movie_id)
                .where(~Movie.id.in_(liked_movie_ids))
                .limit(limit*2)
                .group_by(Movie.id)
                .order_by(desc("popularity"))
            )
            pop_result = await db.execute(pop_stmt)
            pop_movies = pop_result.all()
            
            combined = {m['id']: m for m in content_res}
            for mid, title, year, _ in pop_movies:
                if mid not in combined:
                    combined[mid] = {"id": mid, "title": title, "release_year": year}
                if len(combined) >= limit:
                    break

            return list(combined.values())[:limit]
    except Exception:
        logger.exception("Failed to generate recommendations")
        return []
from typing import List
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import load_only
from app.db import Movie
import logging

logger = logging.getLogger("uvicorn.error")


async def recommend(liked_movie_ids: List[str], db: AsyncSession, limit=10) -> List[dict]:
    try:
        result = await db.execute(
            select(Movie.id,Movie.release_year, Movie.vector).where(Movie.id.in_(liked_movie_ids))
        )
        liked_movies = result.all()

        if not liked_movies:
            logger.warning("No liked movies found for IDs: %s", liked_movie_ids)
            return []

        liked_vectors = [vec for _,_, vec in liked_movies if vec is not None]
        if not liked_vectors:
            logger.warning("Liked movies have no vectors: %s", liked_movie_ids)
            return []

        avg_vector = np.mean(liked_vectors, axis=0)

        result = await db.execute(
            select(Movie.id, Movie.title, Movie.release_year, Movie.vector)
            .where(~Movie.id.in_(liked_movie_ids))
        )
        candidates = result.all()

        recommendations = []
        for movie_id, title, release_year, vector in candidates:
            if vector is None:
                continue
            sim = np.dot(avg_vector, vector) / (
                np.linalg.norm(avg_vector) * np.linalg.norm(vector)
            )
            recommendations.append((movie_id, title, release_year, sim))

        recommendations.sort(key=lambda x: x[3], reverse=True)
        return [{"id": mid, "title": t, "release_year": y} for mid, t,y, _ in recommendations[:limit]]

    except Exception:
        logger.exception("Failed to generate recommendations")
        return []
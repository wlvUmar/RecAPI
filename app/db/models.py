from uuid import uuid4
from sqlalchemy import Column, String, Integer, ARRAY, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

Base = declarative_base()

class Movie(Base):
    __tablename__ = "movies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String, nullable=False)
    description = Column(String)
    genres = Column(JSON)
    tags = Column(JSON)
    release_year = Column(Integer)
    director = Column(String)
    actors = Column(JSON)
    vector = Column(JSON) 

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    liked_movies = relationship("UserLikedMovie", back_populates="user", cascade="all, delete-orphan")

class UserLikedMovie(Base):
    __tablename__ = "user_liked_movies"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    movie_id = Column(UUID(as_uuid=True), primary_key=True)
    user = relationship("User", back_populates="liked_movies")
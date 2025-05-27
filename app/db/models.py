from uuid import uuid4
from sqlalchemy import Column, String, Integer, ARRAY, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import JSON

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
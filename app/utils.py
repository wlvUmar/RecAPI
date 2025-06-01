from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings
from app.schemas import MovieCreate

model = SentenceTransformer("all-MiniLM-L6-v2")  
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_credentials(username: str, password: str) -> bool:
    return username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username != settings.ADMIN_USERNAME:
            raise HTTPException(status_code=401, detail="Not authorized")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def vectorize(movie: MovieCreate):
    """
    Convert a each movie into a single formatted text string and encode it into a dense vector using a pretrained model.

    The movie attributes are concatenated into a structured string with explicit field markers and consistent separators:
    - Each field is prefixed with an uppercase key in square brackets, e.g. [TITLE], [GENRES].
    - Fields are separated by " || ".
    - Multiple items in list fields (like genres or actors) are separated by " | ".

    This formatting helps the model recognize different movie attributes distinctly and produce more meaningful embeddings.

    Args:
        movie (MovieCreate): Movie data containing attributes like title, description, genres, tags, director, and actors.

    Returns:
        numpy.ndarray: A fixed-size dense vector embedding representing the combined semantic content of the movie.
    """
    
    parts = []

    if movie.title:
        parts.append(f"[TITLE] {movie.title}")
    if movie.description:
        parts.append(f"[DESC] {movie.description}")
    if movie.genres:
        parts.append(f"[GENRES] {' | '.join(movie.genres)}")
    if movie.tags:
        parts.append(f"[TAGS] {' | '.join(movie.tags)}")
    if movie.director:
        parts.append(f"[DIRECTOR] {movie.director}")
    if movie.actors:
        parts.append(f"[ACTORS] {' | '.join(movie.actors)}")

    text_content = " || ".join(parts)
    vector = model.encode(text_content)
    return vector
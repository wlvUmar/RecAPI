import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.utils import verify_credentials, create_access_token
from app.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Auth"])

logger = logging.getLogger("uvicorn.error")

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not verify_credentials(form_data.username, form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    token = create_access_token({"sub": form_data.username}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}
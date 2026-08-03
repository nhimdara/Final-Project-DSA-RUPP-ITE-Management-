from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.auth import authenticate
from app.database import get_db
from app.schemas import LoginRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=UserResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    return authenticate(db, body.username, body.password)

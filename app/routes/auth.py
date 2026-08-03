from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.auth import authenticate, create_access_token, current_user
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, body.username, body.password)
    return {"username": user.username, "role": user.role, "student_id": user.student_id,
            "access_token": create_access_token(user), "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)):
    return user

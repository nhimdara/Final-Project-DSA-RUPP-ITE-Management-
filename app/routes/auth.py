from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.controllers.auth import AuthenticatedUser, authenticate, create_access_token, current_user
from app.database import get_db
from app.models import Student
from app.schemas import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, body.username, body.password)
    selected_student_id = user.student_id
    if user.role == "parent":
        if not body.student_id:
            raise HTTPException(400, "Student ID is required for parent login.")
        selected_student_id = body.student_id.strip().upper()
        if db.get(Student, selected_student_id) is None:
            raise HTTPException(404, "Student ID was not found.")
    return {"username": user.username, "role": user.role, "student_id": selected_student_id,
            "access_token": create_access_token(user, selected_student_id), "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def me(user: AuthenticatedUser = Depends(current_user)):
    return user

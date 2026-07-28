from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import User
from api.schemas import Token, UserRead
from api.security import create_access_token, get_current_user, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/token", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    user = db.scalar(select(User).where(User.username == form.username.lower().strip()))
    if user is None or not user.is_active or not verify_password(
        form.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user))


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> User:
    return user


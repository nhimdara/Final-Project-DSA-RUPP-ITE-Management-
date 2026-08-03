import hashlib
import hmac
import base64
import json
import os
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

TOKEN_SECRET = os.getenv("TOKEN_SECRET", "change-this-secret-in-production")
TOKEN_LIFETIME = 8 * 60 * 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str, salt: str = "student-management") -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def authenticate(db: Session, username: str, password: str) -> User:
    user = db.get(User, username.strip())
    if user is None or not hmac.compare_digest(user.password_hash, hash_password(password)):
        raise HTTPException(401, "Invalid username or password.")
    return user


def create_access_token(user: User) -> str:
    payload = {"sub": user.username, "role": user.role,
               "student_id": user.student_id, "exp": int(time.time()) + TOKEN_LIFETIME}
    encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(TOKEN_SECRET.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        encoded, supplied_signature = token.split(".", 1)
        expected_signature = hmac.new(TOKEN_SECRET.encode(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(supplied_signature, expected_signature):
            raise credentials_error
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        if payload.get("exp", 0) < time.time():
            raise credentials_error
        user = db.get(User, payload.get("sub"))
        if user is None or user.role != payload.get("role"):
            raise credentials_error
        return user
    except (ValueError, TypeError, json.JSONDecodeError):
        raise credentials_error


def allow_roles(*roles: str):
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission for this action.")
        return user
    return dependency


def require_student_access(student_id: str, user: User) -> None:
    if user.role in {"administrator", "teacher"}:
        return
    if user.role in {"student", "parent"} and user.student_id == student_id.strip().upper():
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "You may only access your linked student record.")

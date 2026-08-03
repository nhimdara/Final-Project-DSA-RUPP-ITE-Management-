import hashlib
import hmac

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User


def hash_password(password: str, salt: str = "student-management") -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def authenticate(db: Session, username: str, password: str) -> User:
    user = db.get(User, username.strip())
    if user is None or not hmac.compare_digest(user.password_hash, hash_password(password)):
        raise HTTPException(401, "Invalid username or password.")
    return user

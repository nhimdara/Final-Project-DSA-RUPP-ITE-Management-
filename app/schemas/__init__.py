from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse, ScoreUpdate
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate

__all__ = [
    "CourseCreate", "CourseResponse", "CourseUpdate", "EnrollmentCreate",
    "EnrollmentResponse", "LoginRequest", "ScoreUpdate", "StudentCreate",
    "StudentResponse", "StudentUpdate", "TokenResponse", "UserResponse",
]

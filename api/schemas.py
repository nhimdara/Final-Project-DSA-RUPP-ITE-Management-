from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StudentCreate(BaseModel):
    student_id: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=120)
    department: str = Field(
        default="Information Technology Engineering", min_length=1, max_length=120
    )
    year: int = Field(ge=1, le=8)

    @field_validator("student_id")
    @classmethod
    def normalize_id(cls, value: str) -> str:
        value = value.strip().upper()
        if ":" in value:
            raise ValueError("student ID cannot contain ':'")
        return value

    @field_validator("name", "department")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    department: str | None = Field(default=None, min_length=1, max_length=120)
    year: int | None = Field(default=None, ge=1, le=8)


class StudentRead(ORMModel):
    id: int
    student_id: str
    name: str
    department: str
    year: int
    created_at: datetime
    updated_at: datetime


class CourseCreate(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=120)
    credits: int = Field(ge=1, le=30)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        value = value.strip().upper()
        if ":" in value:
            raise ValueError("course code cannot contain ':'")
        return value


class CourseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    credits: int | None = Field(default=None, ge=1, le=30)


class CourseRead(ORMModel):
    id: int
    code: str
    name: str
    credits: int
    created_at: datetime
    updated_at: datetime


class EnrollmentCreate(BaseModel):
    student_id: str
    course_code: str

    @field_validator("student_id", "course_code")
    @classmethod
    def normalize_key(cls, value: str) -> str:
        return value.strip().upper()


class ScoreUpdate(BaseModel):
    score: float = Field(ge=0, le=100)


class EnrollmentRead(BaseModel):
    id: int
    student_id: str
    course_code: str
    course_name: str
    credits: int
    score: float | None
    grade: str | None
    grade_point: float | None


class StudentReport(BaseModel):
    student: StudentRead
    enrollments: list[EnrollmentRead]
    gpa: float | None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(ORMModel):
    id: int
    username: str
    role: str
    is_active: bool
    student_id: int | None


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    role: str
    linked_student_id: str | None = None


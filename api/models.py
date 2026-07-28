from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class Student(TimestampMixin, Base):
    __tablename__ = "students"
    __table_args__ = (CheckConstraint("year BETWEEN 1 AND 8"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    department: Mapped[str] = mapped_column(
        String(120), default="Information Technology Engineering"
    )
    year: Mapped[int] = mapped_column(Integer)

    enrollments: Mapped[list[Enrollment]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    users: Mapped[list[User]] = relationship(back_populates="student")


class Course(TimestampMixin, Base):
    __tablename__ = "courses"
    __table_args__ = (CheckConstraint("credits BETWEEN 1 AND 30"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    credits: Mapped[int] = mapped_column(Integer)

    enrollments: Mapped[list[Enrollment]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )


class Enrollment(TimestampMixin, Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
        CheckConstraint("score IS NULL OR (score >= 0 AND score <= 100)"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), index=True
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)

    student: Mapped[Student] = relationship(back_populates="enrollments")
    course: Mapped[Course] = relationship(back_populates="enrollments")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    student_id: Mapped[int | None] = mapped_column(
        ForeignKey("students.id", ondelete="SET NULL"), nullable=True
    )

    student: Mapped[Student | None] = relationship(back_populates="users")


from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    department: Mapped[str] = mapped_column(
        String(120), nullable=False, default="Information Technology Engineering"
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )

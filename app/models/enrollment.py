from __future__ import annotations

from sqlalchemy import CheckConstraint, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (CheckConstraint("score >= 0 AND score <= 100", name="valid_score"),)

    student_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("students.student_id", ondelete="CASCADE"), primary_key=True
    )
    course_code: Mapped[str] = mapped_column(
        String(20), ForeignKey("courses.code", ondelete="CASCADE"), primary_key=True
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    student: Mapped["Student"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")

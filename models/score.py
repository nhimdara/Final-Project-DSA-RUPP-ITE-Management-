from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.row_mapping import RowMapping, row_to_dict


@dataclass(slots=True)
class Score:
    id: Optional[int] = None
    student_id: str = ""
    student_name: str = ""
    course_id: Optional[int] = None
    course_code: str = ""
    course_name: str = ""
    score: float = 0.0
    grade: str = "F"
    semester: str = "Semester 1"
    academic_year: str = "2026"
    recorded_by: Optional[int] = None
    recorded_at: str = ""

    @classmethod
    def from_row(cls, row: RowMapping) -> "Score":
        data = row_to_dict(row)
        return cls(
            id=data.get("id"),
            student_id=data.get("student_id", ""),
            student_name=data.get("student_name", ""),
            course_id=data.get("course_id"),
            course_code=data.get("course_code", ""),
            course_name=data.get("course_name", ""),
            score=float(data.get("score", 0.0)),
            grade=data.get("grade", "F"),
            semester=data.get("semester", "Semester 1"),
            academic_year=data.get("academic_year", "2026"),
            recorded_by=data.get("recorded_by"),
            recorded_at=data.get("recorded_at", ""),
        )

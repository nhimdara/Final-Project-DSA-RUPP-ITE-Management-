from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.row_mapping import RowMapping, row_to_dict


@dataclass(slots=True)
class Course:
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    department_id: Optional[int] = None
    department_name: str = ""
    teacher_id: Optional[int] = None
    teacher_name: str = ""
    credits: int = 3

    @classmethod
    def from_row(cls, row: RowMapping) -> "Course":
        data = row_to_dict(row)
        return cls(
            id=data.get("id"),
            code=data.get("code", ""),
            name=data.get("name", ""),
            department_id=data.get("department_id"),
            department_name=data.get("department_name", ""),
            teacher_id=data.get("teacher_id"),
            teacher_name=data.get("teacher_name", ""),
            credits=data.get("credits", 3),
        )

    def label(self) -> str:
        return f"{self.code} - {self.name}"

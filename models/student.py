from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.row_mapping import RowMapping, row_to_dict


@dataclass(slots=True)
class Student:
    id: str
    name: str
    gender: str = ""
    date_of_birth: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    department_id: Optional[int] = None
    department_name: str = ""
    year: int = 1
    parent_name: str = ""
    parent_phone: str = ""

    @classmethod
    def from_row(cls, row: RowMapping) -> "Student":
        data = row_to_dict(row)
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            gender=data.get("gender", ""),
            date_of_birth=data.get("date_of_birth", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            department_id=data.get("department_id"),
            department_name=data.get("department_name", ""),
            year=data.get("year", 1),
            parent_name=data.get("parent_name", ""),
            parent_phone=data.get("parent_phone", ""),
        )

    def searchable_text(self) -> str:
        return " ".join(
            [
                self.id,
                self.name,
                self.gender,
                self.email,
                self.phone,
                self.department_name,
                str(self.year),
                self.parent_name,
            ]
        ).lower()

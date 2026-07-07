from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.row_mapping import RowMapping, row_to_dict


@dataclass(slots=True)
class Teacher:
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""
    department_id: Optional[int] = None
    department_name: str = ""
    user_id: Optional[int] = None

    @classmethod
    def from_row(cls, row: RowMapping) -> "Teacher":
        data = row_to_dict(row)
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            department_id=data.get("department_id"),
            department_name=data.get("department_name", ""),
            user_id=data.get("user_id"),
        )

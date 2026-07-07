from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.row_mapping import RowMapping, row_to_dict


@dataclass(slots=True)
class Department:
    id: Optional[int] = None
    name: str = ""
    description: str = ""

    @classmethod
    def from_row(cls, row: RowMapping) -> "Department":
        data = row_to_dict(row)
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
        )

    def to_record(self) -> dict[str, str | int | None]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.user import User


@dataclass(slots=True)
class Admin:
    id: Optional[int] = None
    username: str = ""
    full_name: str = ""

    @classmethod
    def from_user(cls, user: User) -> "Admin":
        return cls(id=user.id, username=user.username, full_name=user.full_name)

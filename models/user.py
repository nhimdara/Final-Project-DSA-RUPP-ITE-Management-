from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest
from typing import Optional

from models.row_mapping import RowMapping, row_to_dict


PASSWORD_SALT = "rupp-ite-student-management"
ROLES = ("admin", "teacher", "student", "parent")


def hash_password(password: str) -> str:
    return sha256(f"{PASSWORD_SALT}:{password}".encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return compare_digest(hash_password(password), password_hash)


@dataclass(slots=True)
class User:
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    role: str = "student"
    full_name: str = ""
    linked_student_id: Optional[str] = None
    created_at: str = ""

    @classmethod
    def from_row(cls, row: RowMapping) -> "User":
        data = row_to_dict(row)
        return cls(
            id=data.get("id"),
            username=data.get("username", ""),
            password_hash=data.get("password_hash", ""),
            role=data.get("role", "student"),
            full_name=data.get("full_name", ""),
            linked_student_id=data.get("linked_student_id"),
            created_at=data.get("created_at", ""),
        )

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_teacher(self) -> bool:
        return self.role == "teacher"

    @property
    def is_student(self) -> bool:
        return self.role == "student"

    @property
    def is_parent(self) -> bool:
        return self.role == "parent"

    def public_dict(self) -> dict[str, str | int | None]:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "full_name": self.full_name,
            "linked_student_id": self.linked_student_id,
            "created_at": self.created_at,
        }

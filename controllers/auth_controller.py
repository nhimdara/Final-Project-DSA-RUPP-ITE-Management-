from __future__ import annotations

from typing import Optional

from models.user import User
from services.authentication_service import AuthenticationService


class AuthController:
    def __init__(self, service: Optional[AuthenticationService] = None) -> None:
        self.service = service or AuthenticationService()
        self.current_user: Optional[User] = None

    def login(self, username: str, password: str) -> Optional[User]:
        self.current_user = self.service.authenticate(username, password)
        return self.current_user

    def logout(self) -> None:
        self.current_user = None

    def is_logged_in(self) -> bool:
        return self.current_user is not None

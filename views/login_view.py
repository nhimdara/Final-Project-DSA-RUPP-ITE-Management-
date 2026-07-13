from __future__ import annotations

from controllers.auth_controller import AuthController
from views.dashboard_view import DashboardView
from views.menu import title


class LoginView:
    def __init__(self) -> None:
        self.auth = AuthController()

    @staticmethod
    def _read_password() -> str:
        return input("Password: ")

    def run(self) -> None:
        while True:
            title("Student Management System")
            print(
                "Default accounts: admin/admin123, teacher/teacher123, "
                "student/student123, parent/parent123"
            )
            username = input("Username (or exit): ").strip()
            if username.lower() in {"exit", "quit", "0"}:
                print("Goodbye.")
                return
            password = self._read_password()
            user = self.auth.login(username, password)
            if user is None:
                print("Invalid username or password.")
                continue
            DashboardView(self.auth).show(user)

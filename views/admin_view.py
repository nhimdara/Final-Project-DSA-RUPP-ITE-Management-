from __future__ import annotations

from controllers.admin_controller import AdminController
from controllers.user_controller import UserController
from models.user import ROLES
from views.menu import (
    menu_choice,
    pause,
    print_table,
    prompt_int,
    prompt_optional,
    prompt_required,
    show_error,
    show_success,
    yes_no,
)


USER_TABLE_COLUMNS = [
    ("id", "ID"),
    ("username", "Username"),
    ("role", "Role"),
    ("name", "Name"),
    ("student", "Linked Student"),
]


class AdminView:
    def __init__(self) -> None:
        self.admin = AdminController()
        self.users = UserController()

    def show_dashboard(self) -> None:
        stats = self.admin.dashboard_stats()
        print_table(
            [{"item": key.title(), "count": value} for key, value in stats.items()],
            [("item", "Item"), ("count", "Count")],
        )

    def user_menu(self) -> None:
        while True:
            choice = menu_choice(
                "User Management",
                {
                    "1": "Create user",
                    "2": "Update user",
                    "3": "Delete user",
                    "4": "View users",
                    "0": "Back",
                },
            )
            if choice == "1":
                self.create_user()
            elif choice == "2":
                self.update_user()
            elif choice == "3":
                self.delete_user()
            elif choice == "4":
                self.list_users()
            elif choice == "0":
                return
            else:
                print("Invalid option.")
            pause()

    def list_users(self) -> None:
        rows = [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "name": user.full_name,
                "student": user.linked_student_id or "",
            }
            for user in self.users.list_users()
        ]
        print_table(rows, USER_TABLE_COLUMNS)

    def create_user(self) -> None:
        try:
            print(f"Roles: {', '.join(ROLES)}")
            user = self.users.create_user(
                prompt_required("Username"),
                prompt_required("Password"),
                prompt_required("Role").lower(),
                prompt_required("Full name"),
                prompt_optional("Linked student ID").upper() or None,
            )
            show_success(f"User {user.username} created.")
        except Exception as exc:
            show_error(exc)

    def update_user(self) -> None:
        try:
            user_id = prompt_int("User ID", minimum=1)
            if user_id is None:
                return
            current = self.users.get_user(user_id)
            user = self.users.update_user(
                user_id,
                prompt_required("Username", current.username),
                prompt_required("Role", current.role),
                prompt_required("Full name", current.full_name),
                prompt_optional(
                    "Linked student ID",
                    current.linked_student_id or "",
                ).upper()
                or None,
                prompt_optional("New password (blank to keep)"),
            )
            show_success(f"User {user.username} updated.")
        except Exception as exc:
            show_error(exc)

    def delete_user(self) -> None:
        try:
            user_id = prompt_int("User ID", minimum=1)
            if user_id is None:
                return
            user = self.users.get_user(user_id)
            if yes_no(f"Delete user {user.username}", default=False):
                self.users.delete_user(user_id)
                show_success("User deleted.")
        except Exception as exc:
            show_error(exc)

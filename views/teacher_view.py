from __future__ import annotations

from controllers.department_controller import DepartmentController
from controllers.teacher_controller import TeacherController
from views.menu import menu_choice, pause, print_table, prompt_int, prompt_optional, prompt_required, show_error, show_success, yes_no


class TeacherView:
    def __init__(self) -> None:
        self.controller = TeacherController()
        self.departments = DepartmentController()

    def menu(self) -> None:
        while True:
            choice = menu_choice(
                "Teacher Management",
                {
                    "1": "Add teacher",
                    "2": "Update teacher",
                    "3": "Delete teacher",
                    "4": "View teachers",
                    "0": "Back",
                },
            )
            if choice == "1":
                self.add_teacher()
            elif choice == "2":
                self.update_teacher()
            elif choice == "3":
                self.delete_teacher()
            elif choice == "4":
                self.list_teachers()
            elif choice == "0":
                return
            else:
                print("Invalid option.")
            pause()

    def _department_id(self, default: int | None = None) -> int | None:
        print_table(
            [dept.to_record() for dept in self.departments.list_departments()],
            [("id", "ID"), ("name", "Name"), ("description", "Description")],
        )
        value = prompt_int("Department ID (0 for none)", default=default or 0, minimum=0)
        return None if value == 0 else value

    def list_teachers(self) -> None:
        rows = [
            {
                "id": teacher.id,
                "name": teacher.name,
                "email": teacher.email,
                "phone": teacher.phone,
                "department": teacher.department_name,
                "user_id": teacher.user_id or "",
            }
            for teacher in self.controller.list_teachers()
        ]
        print_table(rows, [("id", "ID"), ("name", "Name"), ("email", "Email"), ("phone", "Phone"), ("department", "Department"), ("user_id", "User ID")])

    def add_teacher(self) -> None:
        try:
            teacher = self.controller.add_teacher(
                prompt_required("Name"),
                prompt_optional("Email"),
                prompt_optional("Phone"),
                self._department_id(),
            )
            show_success(f"Teacher {teacher.id} saved.")
        except Exception as exc:
            show_error(exc)

    def update_teacher(self) -> None:
        try:
            teacher_id = prompt_int("Teacher ID", minimum=1)
            if teacher_id is None:
                return
            current = self.controller.get_teacher(teacher_id)
            teacher = self.controller.update_teacher(
                teacher_id,
                prompt_required("Name", current.name),
                prompt_optional("Email", current.email),
                prompt_optional("Phone", current.phone),
                self._department_id(current.department_id),
                current.user_id,
            )
            show_success(f"Teacher {teacher.id} updated.")
        except Exception as exc:
            show_error(exc)

    def delete_teacher(self) -> None:
        try:
            teacher_id = prompt_int("Teacher ID", minimum=1)
            if teacher_id is None:
                return
            teacher = self.controller.get_teacher(teacher_id)
            if yes_no(f"Delete {teacher.name}", default=False) and self.controller.delete_teacher(teacher_id):
                show_success("Teacher deleted.")
        except Exception as exc:
            show_error(exc)

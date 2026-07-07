from __future__ import annotations

from controllers.department_controller import DepartmentController
from views.menu import menu_choice, pause, print_table, prompt_int, prompt_optional, prompt_required, show_error, show_success


class DepartmentView:
    def __init__(self) -> None:
        self.controller = DepartmentController()

    def menu(self) -> None:
        while True:
            choice = menu_choice(
                "Department Management",
                {
                    "1": "Add department",
                    "2": "Search departments",
                    "3": "Update department",
                    "4": "Delete department",
                    "5": "View departments",
                    "0": "Back",
                },
            )
            if choice == "1":
                self.add_department()
            elif choice == "2":
                self.search_departments()
            elif choice == "3":
                self.update_department()
            elif choice == "4":
                self.delete_department()
            elif choice == "5":
                self.list_departments()
            elif choice == "0":
                return
            else:
                print("Invalid option.")
            pause()

    def list_departments(self) -> None:
        rows = [dept.to_record() for dept in self.controller.list_departments()]
        print_table(rows, [("id", "ID"), ("name", "Name"), ("description", "Description")])

    def add_department(self) -> None:
        try:
            dept = self.controller.add_department(
                prompt_required("Department name"),
                prompt_optional("Description"),
            )
            show_success(f"Department saved with ID {dept.id}.")
        except Exception as exc:
            show_error(exc)

    def search_departments(self) -> None:
        keyword = prompt_required("Search keyword")
        rows = [dept.to_record() for dept in self.controller.search_departments(keyword)]
        print_table(rows, [("id", "ID"), ("name", "Name"), ("description", "Description")])

    def update_department(self) -> None:
        try:
            dept_id = prompt_int("Department ID", minimum=1)
            if dept_id is None:
                return
            dept = self.controller.get_department(dept_id)
            updated = self.controller.update_department(
                dept_id,
                prompt_required("Department name", dept.name),
                prompt_optional("Description", dept.description),
            )
            show_success(f"Department {updated.id} updated.")
        except Exception as exc:
            show_error(exc)

    def delete_department(self) -> None:
        try:
            dept_id = prompt_int("Department ID", minimum=1)
            if dept_id is None:
                return
            if self.controller.delete_department(dept_id):
                show_success("Department deleted.")
            else:
                print("Department not found.")
        except Exception as exc:
            show_error(exc)

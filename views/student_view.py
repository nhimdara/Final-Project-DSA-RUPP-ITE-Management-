from __future__ import annotations

from controllers.department_controller import DepartmentController
from controllers.student_controller import StudentController
from models.student import Student
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


class StudentView:
    def __init__(self) -> None:
        self.controller = StudentController()
        self.departments = DepartmentController()

    def menu(self) -> None:
        while True:
            choice = menu_choice(
                "Student Management",
                {
                    "1": "Add student",
                    "2": "Search student",
                    "3": "Update student",
                    "4": "Delete student",
                    "5": "View students",
                    "0": "Back",
                },
            )
            if choice == "1":
                self.add_student()
            elif choice == "2":
                self.search_students()
            elif choice == "3":
                self.update_student()
            elif choice == "4":
                self.delete_student()
            elif choice == "5":
                self.list_students()
            elif choice == "0":
                return
            else:
                print("Invalid option.")
            pause()

    def _department_id(self, default: int | None = None) -> int | None:
        departments = self.departments.list_departments()
        print_table(
            [dept.to_record() for dept in departments],
            [("id", "ID"), ("name", "Name"), ("description", "Description")],
        )
        dept_id = prompt_int("Department ID", default=default, minimum=1)
        return dept_id

    def _collect_student(self, existing: Student | None = None) -> Student:
        student_id = prompt_required("Student ID", existing.id if existing else None).upper()
        return Student(
            id=student_id,
            name=prompt_required("Name", existing.name if existing else None),
            gender=prompt_optional("Gender", existing.gender if existing else ""),
            date_of_birth=prompt_optional("Date of birth", existing.date_of_birth if existing else ""),
            email=prompt_optional("Email", existing.email if existing else ""),
            phone=prompt_optional("Phone", existing.phone if existing else ""),
            address=prompt_optional("Address", existing.address if existing else ""),
            department_id=self._department_id(existing.department_id if existing else None),
            year=prompt_int("Year", existing.year if existing else 1, minimum=1) or 1,
            parent_name=prompt_optional("Parent name", existing.parent_name if existing else ""),
            parent_phone=prompt_optional("Parent phone", existing.parent_phone if existing else ""),
        )

    def list_students(self) -> None:
        self.controller.refresh_cache()
        self._print_students(self.controller.list_students())

    def _print_students(self, students: list[Student]) -> None:
        rows = [
            {
                "id": student.id,
                "name": student.name,
                "department": student.department_name,
                "year": student.year,
                "phone": student.phone,
                "parent": student.parent_name,
            }
            for student in students
        ]
        print_table(rows, [("id", "ID"), ("name", "Name"), ("department", "Department"), ("year", "Year"), ("phone", "Phone"), ("parent", "Parent")])

    def add_student(self) -> None:
        try:
            student = self.controller.add_student(self._collect_student())
            show_success(f"Student {student.id} saved.")
        except Exception as exc:
            show_error(exc)

    def search_students(self) -> None:
        keyword = prompt_required("Search keyword")
        self._print_students(self.controller.search_students(keyword))

    def update_student(self) -> None:
        try:
            student_id = prompt_required("Student ID").upper()
            current = self.controller.get_student(student_id)
            updated_student = self._collect_student(current)
            updated_student.id = current.id
            updated = self.controller.update_student(updated_student)
            show_success(f"Student {updated.id} updated.")
        except Exception as exc:
            show_error(exc)

    def delete_student(self) -> None:
        try:
            student_id = prompt_required("Student ID").upper()
            student = self.controller.get_student(student_id)
            if yes_no(f"Delete {student.name}", default=False) and self.controller.delete_student(student_id):
                show_success("Student deleted.")
        except Exception as exc:
            show_error(exc)

    def show_profile(self, student_id: str) -> None:
        try:
            student = self.controller.get_student(student_id)
            print_table(
                [
                    {
                        "id": student.id,
                        "name": student.name,
                        "gender": student.gender,
                        "dob": student.date_of_birth,
                        "email": student.email,
                        "phone": student.phone,
                        "department": student.department_name,
                        "year": student.year,
                        "parent": student.parent_name,
                    }
                ],
                [
                    ("id", "ID"),
                    ("name", "Name"),
                    ("gender", "Gender"),
                    ("dob", "DOB"),
                    ("email", "Email"),
                    ("phone", "Phone"),
                    ("department", "Department"),
                    ("year", "Year"),
                    ("parent", "Parent"),
                ],
            )
        except Exception as exc:
            show_error(exc)

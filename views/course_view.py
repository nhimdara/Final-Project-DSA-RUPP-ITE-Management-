from __future__ import annotations

from controllers.course_controller import CourseController
from controllers.department_controller import DepartmentController
from controllers.teacher_controller import TeacherController
from models.course import Course
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


COURSE_TABLE_COLUMNS = [
    ("id", "ID"),
    ("code", "Code"),
    ("name", "Name"),
    ("department", "Department"),
    ("teacher", "Teacher"),
    ("credits", "Credits"),
]


class CourseView:
    def __init__(self) -> None:
        self.controller = CourseController()
        self.departments = DepartmentController()
        self.teachers = TeacherController()

    def menu(self) -> None:
        while True:
            choice = menu_choice(
                "Course Management",
                {
                    "1": "Add course",
                    "2": "Search courses",
                    "3": "Update course",
                    "4": "Delete course",
                    "5": "View courses",
                    "0": "Back",
                },
            )
            if choice == "1":
                self.add_course()
            elif choice == "2":
                self.search_courses()
            elif choice == "3":
                self.update_course()
            elif choice == "4":
                self.delete_course()
            elif choice == "5":
                self.list_courses()
            elif choice == "0":
                return
            else:
                print("Invalid option.")
            pause()

    def _print_courses(self, courses: list[Course]) -> None:
        rows = [
            {
                "id": course.id,
                "code": course.code,
                "name": course.name,
                "department": course.department_name,
                "teacher": course.teacher_name,
                "credits": course.credits,
            }
            for course in courses
        ]
        print_table(rows, COURSE_TABLE_COLUMNS)

    def _department_id(self, default: int | None = None) -> int:
        print_table(
            [dept.to_record() for dept in self.departments.list_departments()],
            [("id", "ID"), ("name", "Name"), ("description", "Description")],
        )
        value = prompt_int("Department ID", default=default, minimum=1)
        if value is None:
            raise ValueError("Department ID is required.")
        return value

    def _teacher_id(self, default: int | None = None) -> int | None:
        teachers = self.teachers.list_teachers()
        if teachers:
            print_table(
                [
                    {
                        "id": teacher.id,
                        "name": teacher.name,
                        "department": teacher.department_name,
                    }
                    for teacher in teachers
                ],
                [("id", "ID"), ("name", "Name"), ("department", "Department")],
            )
        value = prompt_int("Teacher ID (0 for none)", default=default or 0, minimum=0)
        return None if value == 0 else value

    def list_courses(self) -> None:
        self._print_courses(self.controller.list_courses())

    def add_course(self) -> None:
        try:
            course = self.controller.add_course(
                prompt_required("Course code"),
                prompt_required("Course name"),
                self._department_id(),
                self._teacher_id(),
                prompt_int("Credits", default=3, minimum=1) or 3,
            )
            show_success(f"Course {course.code} saved.")
        except Exception as exc:
            show_error(exc)

    def search_courses(self) -> None:
        keyword = prompt_required("Search keyword")
        self._print_courses(self.controller.search_courses(keyword))

    def update_course(self) -> None:
        try:
            course_id = prompt_int("Course ID", minimum=1)
            if course_id is None:
                return
            current = self.controller.get_course(course_id)
            course = self.controller.update_course(
                course_id,
                prompt_required("Course code", current.code),
                prompt_required("Course name", current.name),
                self._department_id(current.department_id),
                self._teacher_id(current.teacher_id),
                prompt_int("Credits", default=current.credits, minimum=1) or current.credits,
            )
            show_success(f"Course {course.code} updated.")
        except Exception as exc:
            show_error(exc)

    def delete_course(self) -> None:
        try:
            course_id = prompt_int("Course ID", minimum=1)
            if course_id is None:
                return
            course = self.controller.get_course(course_id)
            if yes_no(f"Delete {course.label()}", default=False):
                self.controller.delete_course(course_id)
                show_success("Course deleted.")
        except Exception as exc:
            show_error(exc)

    def show_student_courses(self, student_id: str) -> None:
        self._print_courses(self.controller.courses_for_student(student_id))

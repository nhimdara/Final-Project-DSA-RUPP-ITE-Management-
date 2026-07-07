from __future__ import annotations

from typing import TypedDict

from controllers.course_controller import CourseController
from controllers.department_controller import DepartmentController
from controllers.student_controller import StudentController
from models.course import Course
from models.department import Department
from models.student import Student


class SearchResults(TypedDict):
    students: list[Student]
    courses: list[Course]
    departments: list[Department]


class SearchController:
    def __init__(self) -> None:
        self.students = StudentController()
        self.courses = CourseController()
        self.departments = DepartmentController()

    def global_search(self, keyword: str) -> SearchResults:
        return {
            "students": self.students.search_students(keyword),
            "courses": self.courses.search_courses(keyword),
            "departments": self.departments.search_departments(keyword),
        }

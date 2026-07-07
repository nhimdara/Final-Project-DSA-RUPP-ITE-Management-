from __future__ import annotations

from controllers.auth_controller import AuthController
from controllers.search_controller import SearchController
from models.user import User
from views.admin_view import AdminView
from views.course_view import CourseView
from views.department_view import DepartmentView
from views.menu import menu_choice, pause, print_table, prompt_required
from views.performance_view import PerformanceView
from views.report_view import ReportView
from views.student_view import StudentView
from views.teacher_view import TeacherView


class DashboardView:
    def __init__(self, auth: AuthController) -> None:
        self.auth = auth
        self.admin = AdminView()
        self.students = StudentView()
        self.courses = CourseView()
        self.departments = DepartmentView()
        self.teachers = TeacherView()
        self.performance = PerformanceView()
        self.reports = ReportView()

    def show(self, user: User) -> None:
        if user.role == "admin":
            self._admin_menu(user)
        elif user.role == "teacher":
            self._teacher_menu(user)
        elif user.role == "student":
            self._student_menu(user)
        elif user.role == "parent":
            self._parent_menu(user)

    def _admin_menu(self, user: User) -> None:
        while self.auth.is_logged_in():
            choice = menu_choice(
                f"Dashboard - {user.full_name}",
                {
                    "1": "Dashboard summary",
                    "2": "Manage students",
                    "3": "Manage courses",
                    "4": "Manage departments",
                    "5": "Manage teachers",
                    "6": "Manage users",
                    "7": "Scores and performance",
                    "8": "Reports",
                    "9": "Search",
                    "0": "Logout",
                },
            )
            if choice == "1":
                self.admin.show_dashboard()
            elif choice == "2":
                self.students.menu()
            elif choice == "3":
                self.courses.menu()
            elif choice == "4":
                self.departments.menu()
            elif choice == "5":
                self.teachers.menu()
            elif choice == "6":
                self.admin.user_menu()
            elif choice == "7":
                self.performance.menu(user.id)
            elif choice == "8":
                self.reports.menu(user.id)
            elif choice == "9":
                self._global_search()
            elif choice == "0":
                self.auth.logout()
                return
            else:
                print("Invalid option.")
            pause()

    def _teacher_menu(self, user: User) -> None:
        while self.auth.is_logged_in():
            choice = menu_choice(
                f"Teacher Menu - {user.full_name}",
                {
                    "1": "Input scores",
                    "2": "View students",
                    "3": "View performance",
                    "4": "Reports",
                    "5": "Search",
                    "0": "Logout",
                },
            )
            if choice == "1":
                self.performance.record_score(user.id)
            elif choice == "2":
                self.students.list_students()
            elif choice == "3":
                student_id = prompt_required("Student ID").upper()
                self.performance.show_student_performance(student_id)
            elif choice == "4":
                self.reports.menu(user.id)
            elif choice == "5":
                self._global_search()
            elif choice == "0":
                self.auth.logout()
                return
            else:
                print("Invalid option.")
            pause()

    def _student_menu(self, user: User) -> None:
        student_id = self._linked_student_id(user)
        while self.auth.is_logged_in():
            choice = menu_choice(
                f"Student Menu - {user.full_name}",
                {
                    "1": "View profile",
                    "2": "View courses",
                    "3": "View grades",
                    "0": "Logout",
                },
            )
            if choice == "1":
                self.students.show_profile(student_id)
            elif choice == "2":
                self.courses.show_student_courses(student_id)
            elif choice == "3":
                self.performance.show_student_performance(student_id)
            elif choice == "0":
                self.auth.logout()
                return
            else:
                print("Invalid option.")
            pause()

    def _parent_menu(self, user: User) -> None:
        student_id = self._linked_student_id(user)
        while self.auth.is_logged_in():
            choice = menu_choice(
                f"Parent Menu - {user.full_name}",
                {
                    "1": "View student information",
                    "2": "View grades",
                    "0": "Logout",
                },
            )
            if choice == "1":
                self.students.show_profile(student_id)
            elif choice == "2":
                self.performance.show_student_performance(student_id)
            elif choice == "0":
                self.auth.logout()
                return
            else:
                print("Invalid option.")
            pause()

    def _linked_student_id(self, user: User) -> str:
        if user.linked_student_id:
            return user.linked_student_id
        return prompt_required("Linked student ID").upper()

    def _global_search(self) -> None:
        keyword = prompt_required("Search keyword")
        results = SearchController().global_search(keyword)
        print("\nStudents")
        print_table(
            [
                {
                    "id": student.id,
                    "name": student.name,
                    "department": student.department_name,
                }
                for student in results["students"]
            ],
            [("id", "ID"), ("name", "Name"), ("department", "Department")],
        )
        print("\nCourses")
        print_table(
            [
                {
                    "id": course.id,
                    "code": course.code,
                    "name": course.name,
                    "department": course.department_name,
                }
                for course in results["courses"]
            ],
            [("id", "ID"), ("code", "Code"), ("name", "Name"), ("department", "Department")],
        )
        print("\nDepartments")
        print_table(
            [dept.to_record() for dept in results["departments"]],
            [("id", "ID"), ("name", "Name"), ("description", "Description")],
        )

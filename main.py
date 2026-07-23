"""Console menu for the data-structure Student Management System."""

from __future__ import annotations

import shutil
import textwrap

from data import USERS
from data_structures.student_management import (
    Course,
    Student,
    StudentManagementSystem,
    User,
)


def read_int(label: str) -> int:
    try:
        return int(input(label).strip())
    except ValueError as exc:
        raise ValueError("Please enter a whole number.") from exc


def show_students(system: StudentManagementSystem, students: list[Student] | None = None) -> None:
    students = system.display_students() if students is None else students
    if not students:
        print("No students found.")
        return
    for student in students:
        print(f"{student.student_id} | {student.name} | {student.department} | Year {student.year}")


def show_courses(system: StudentManagementSystem, courses: list[Course] | None = None) -> None:
    courses = system.display_courses() if courses is None else courses
    if not courses:
        print("No courses found.")
        return
    for course in courses:
        print(f"{course.code} | {course.name} | {course.credits} credits")


def show_enrollment_graph(system: StudentManagementSystem) -> None:
    """Render the enrollment graph as a compact, course-centered terminal view."""
    courses = system.display_courses()
    students = system.display_students()
    course_enrollments = [
        (course, system.course_students(course.code)) for course in courses
    ]
    enrollment_count = sum(
        len(enrolled_students)
        for _, enrolled_students in course_enrollments
    )

    width = max(46, min(shutil.get_terminal_size((88, 24)).columns, 96))
    rule = "=" * width
    divider = "-" * width

    print(f"\n{rule}")
    print("ENROLLMENT GRAPH".center(width))
    print(rule)
    print(
        f"Courses: {len(courses)}  |  Students: {len(students)}  |  "
        f"Enrollments: {enrollment_count}"
    )

    if not courses:
        print(divider)
        print("The graph is empty.")
        print(rule)
        return

    print(divider)
    print("COURSE  ->  ENROLLED STUDENTS")

    for course, enrolled_students in course_enrollments:
        print(divider)
        count_label = (
            f"{len(enrolled_students)} student"
            f"{'' if len(enrolled_students) == 1 else 's'}"
        )
        course_label = f"{course.code} - {course.name}"
        available = width - len(count_label) - 3
        if len(course_label) > available:
            course_label = textwrap.shorten(
                course_label, width=max(8, available), placeholder="..."
            )
        print(f"{course_label:<{available}} | {count_label}")

        student_ids = ", ".join(
            student.student_id for student in enrolled_students
        )
        if not student_ids:
            print("  `-- No students enrolled")
            continue

        wrapped_ids = textwrap.wrap(
            student_ids,
            width=max(1, width - 6),
            break_long_words=False,
            break_on_hyphens=False,
        )
        for line_number, line in enumerate(wrapped_ids):
            branch = "`--" if line_number == len(wrapped_ids) - 1 else "|--"
            print(f"  {branch} {line}")

    print(rule)


def select_course_code(
    system: StudentManagementSystem, label: str = "Choose course",
) -> str:
    """Display existing courses and return the code selected by number."""
    courses = system.display_courses()
    if not courses:
        raise ValueError("No courses are available.")

    print(f"\n{label}:")
    for number, course in enumerate(courses, start=1):
        print(f"{number}. {course.code} | {course.name} | {course.credits} credits")

    choice = read_int("Course number: ")
    if choice < 1 or choice > len(courses):
        raise ValueError("Please choose a course number from the list.")
    return courses[choice - 1].code


def run_admin_menu(system: StudentManagementSystem) -> None:
    actions = {
        "1": "Insert student",
        "2": "Display students",
        "3": "Search students",
        "4": "Delete student",
        "5": "Insert course",
        "6": "Display courses",
        "7": "Delete course",
        "8": "Enroll student in course",
        "9": "Record score",
        "10": "Show student report",
        "11": "Update student",
        "12": "Search courses",
        "13": "Update course",
        "14": "Display enrollment graph",
        "0": "Logout",
    }

    while True:
        print("\n=== ADMINISTRATOR MENU ===")
        for key, label in actions.items():
            print(f"{key}. {label}")
        choice = input("Choose: ").strip()

        try:
            if choice == "0":
                print("Logged out.")
                return
            if choice == "1":
                system.insert_student(
                    input("Student ID: "), input("Name: "),
                    read_int("Year: "),
                )
                print("Student inserted.")
            elif choice == "2":
                show_students(system)
            elif choice == "3":
                show_students(system, system.search_students(input("Search: ")))
            elif choice == "4":
                deleted = system.delete_student(input("Student ID: "))
                print("Student deleted." if deleted else "Student not found.")
            elif choice == "5":
                course_code = system.insert_course_automatically(
                    input("Course name: "), read_int("Credits: "),
                )
                print(f"Course inserted with ID {course_code}.")
            elif choice == "6":
                show_courses(system)
            elif choice == "7":
                deleted = system.delete_course(
                    select_course_code(system, "Select course to delete")
                )
                print("Course deleted." if deleted else "Course not found.")
            elif choice == "8":
                student_id = input("Student ID: ")
                course_code = select_course_code(system, "Select course for enrollment")
                system.enroll(student_id, course_code)
                print("Student enrolled.")
            elif choice == "9":
                student_id = input("Student ID: ")
                course_code = select_course_code(system, "Select course for the score")
                system.record_score(
                    student_id, course_code,
                    float(input("Score (0-100): ").strip()),
                )
                print("Score saved.")
            elif choice == "10":
                print(system.student_report(input("Student ID: ")))
            elif choice == "11":
                system.update_student(
                    input("Student ID: "), input("New name: "),
                    read_int("New year: "),
                )
                print("Student updated.")
            elif choice == "12":
                show_courses(system, system.search_courses(input("Search: ")))
            elif choice == "13":
                system.update_course(
                    select_course_code(system, "Select course to update"),
                    input("New course name: "),
                    read_int("New credits: "),
                )
                print("Course updated.")
            elif choice == "14":
                show_enrollment_graph(system)
            else:
                print("Invalid choice.")
        except ValueError as exc:
            print(f"Error: {exc}")


def run_teacher_menu(system: StudentManagementSystem) -> None:
    actions = {
        "1": "Display students",
        "2": "Search students",
        "3": "Display courses",
        "4": "Search courses",
        "5": "Enroll student in course",
        "6": "Input student score by course",
        "7": "Show student report",
        "0": "Logout",
    }
    while True:
        print("\n=== TEACHER MENU ===")
        for key, label in actions.items():
            print(f"{key}. {label}")
        choice = input("Choose: ").strip()
        try:
            if choice == "0":
                print("Logged out.")
                return
            if choice == "1":
                show_students(system)
            elif choice == "2":
                show_students(system, system.search_students(input("Search: ")))
            elif choice == "3":
                show_courses(system)
            elif choice == "4":
                show_courses(system, system.search_courses(input("Search: ")))
            elif choice == "5":
                student_id = input("Student ID: ")
                course_code = select_course_code(system, "Select course for enrollment")
                system.enroll(student_id, course_code)
                print("Student enrolled.")
            elif choice == "6":
                course_code = select_course_code(system, "Select course for scoring")
                enrolled_students = system.course_students(course_code)
                if not enrolled_students:
                    print("No students are enrolled in this course.")
                    continue
                print("Enrolled students:")
                show_students(system, enrolled_students)
                student_id = input("Student ID: ")
                score = float(input("Score (0-100): ").strip())
                system.record_score(student_id, course_code, score)
                print("Score saved.")
            elif choice == "7":
                print(system.student_report(input("Student ID: ")))
            else:
                print("Invalid choice.")
        except ValueError as exc:
            print(f"Error: {exc}")


def request_linked_student_id(
    system: StudentManagementSystem, user: User,
) -> str | None:
    """Ask for a student ID and enforce an optional account link."""
    student_id = input("Student ID: ").strip().upper()
    if not student_id:
        print("Student ID is required.")
        return None
    if user.student_id and student_id != user.student_id.upper():
        print("Access denied: this student ID is not linked to your account.")
        return None
    if system.search_student_by_id(student_id) is None:
        print(f"Student record {student_id} was not found.")
        return None
    return student_id


def run_student_menu(system: StudentManagementSystem, user: User) -> None:
    print("\nEnter your student ID to continue.")
    student_id = request_linked_student_id(system, user)
    if student_id is None:
        return

    while True:
        print("\n=== STUDENT MENU ===")
        print("1. View student information")
        print("2. View enrolled courses")
        print("3. View GPA")
        print("4. Show full academic report")
        print("0. Logout")
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Logged out.")
            return
        try:
            if choice == "1":
                print(system.student_information(student_id))
            elif choice == "2":
                show_courses(system, system.student_courses(student_id))
            elif choice == "3":
                print(system.student_gpa_report(student_id))
            elif choice == "4":
                print(system.student_report(student_id))
            else:
                print("Invalid choice.")
        except ValueError as exc:
            print(f"Error: {exc}")


def run_parent_menu(system: StudentManagementSystem, user: User) -> None:
    print("\nEnter your student's ID to continue.")
    student_id = request_linked_student_id(system, user)
    if student_id is None:
        return

    while True:
        print("\n=== PARENT MENU ===")
        print("1. View student information")
        print("2. View GPA")
        print("3. Show student's full academic report")
        print("0. Logout")
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Logged out.")
            return
        if choice == "1":
            try:
                print(system.student_information(student_id))
            except ValueError as exc:
                print(f"Error: {exc}")
        elif choice == "2":
            print(system.student_gpa_report(student_id))
        elif choice == "3":
            print(system.student_report(student_id))
        else:
            print("Invalid choice.")


def login(system: StudentManagementSystem) -> User | None:
    print("\nDemo accounts:")
    for account in USERS:
        role = account["role"].title()
        username = account["username"]
        password = account["password"]
        print(f"  {role:<13} username: {username:<8} password: {password}")

    while True:
        print("\n=== LOGIN ===")
        print("Enter 0 as the username to exit.")
        username = input("Username: ").strip()
        if username == "0":
            return None
        password = input("Password: ")
        user = system.authenticate(username, password)
        if user is not None:
            print(f"Welcome, {user.username} ({user.role}).")
            return user
        print("Invalid username or password.")


def main() -> None:
    system = StudentManagementSystem()
    while True:
        user = login(system)
        if user is None:
            print("Goodbye.")
            return
        if user.role == "administrator":
            run_admin_menu(system)
        elif user.role == "teacher":
            run_teacher_menu(system)
        elif user.role == "student":
            run_student_menu(system, user)
        elif user.role == "parent":
            run_parent_menu(system, user)
        else:
            print(f"Cannot open menu: unsupported role '{user.role}'.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")

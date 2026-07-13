"""Student and course records managed directly with data structures."""

from __future__ import annotations

from dataclasses import dataclass, field

from data import COURSES, ENROLLMENTS, SCORES, STUDENTS, USERS
from data_structures.graph import Graph
from data_structures.hash_table import HashTable
from data_structures.tree import GradeDecisionTree


@dataclass
class Student:
    student_id: str
    name: str
    department: str
    year: int
    scores: dict[str, float] = field(default_factory=dict)


@dataclass
class Course:
    code: str
    name: str
    credits: int


@dataclass(frozen=True)
class User:
    username: str
    password: str
    role: str
    student_id: str = ""


class StudentManagementSystem:
    """Manage students and courses without MVC or a database."""

    def __init__(self) -> None:
        self.students: HashTable[str, Student] = HashTable()
        self.courses: HashTable[str, Course] = HashTable()
        self.users: HashTable[str, User] = HashTable()
        self.enrollments = Graph()
        self.grade_tree = GradeDecisionTree()
        self._insert_demo_data()
        self._insert_default_users()

    def _insert_demo_data(self) -> None:
        """Create complete records for demonstrating every menu."""
        for student in STUDENTS:
            self.insert_student(**student)
        for course in COURSES:
            self.insert_course(**course)
        for enrollment in ENROLLMENTS:
            self.enroll(**enrollment)
        for score in SCORES:
            self.record_score(**score)

    # Login data is also stored in a hash table, not an MVC service.
    def _insert_default_users(self) -> None:
        for user_data in USERS:
            user = User(**user_data)
            self.users.insert(user.username, user)

    def authenticate(self, username: str, password: str) -> User | None:
        user = self.users.search(username.strip().lower())
        if user is None or user.password != password:
            return None
        return user

    # Student operations: insert, delete, search, update, and display.
    def insert_student(self, student_id: str, name: str, department: str, year: int) -> None:
        student_id = student_id.strip().upper()
        if not student_id or not name.strip() or not department.strip():
            raise ValueError("Student ID, name, and department are required.")
        if self.students.contains(student_id):
            raise ValueError("Student ID already exists.")
        if year < 1:
            raise ValueError("Year must be at least 1.")

        student = Student(student_id, name.strip(), department.strip(), year)
        self.students.insert(student_id, student)
        self.enrollments.insert(self._student_vertex(student_id))

    def add_student(self, student_id: str, name: str, department: str, year: int) -> None:
        """Backward-compatible name for insert_student."""
        self.insert_student(student_id, name, department, year)

    def delete_student(self, student_id: str) -> bool:
        student_id = student_id.strip().upper()
        if any(user.student_id.upper() == student_id for user in self.users.values()):
            raise ValueError(
                "Cannot delete this student because a login account is linked to it."
            )
        if not self.students.delete(student_id):
            return False
        self.enrollments.delete(self._student_vertex(student_id))
        return True

    def search_student_by_id(self, student_id: str) -> Student | None:
        return self.students.search(student_id.strip().upper())

    def search_students(self, keyword: str) -> list[Student]:
        keyword = keyword.strip().lower()
        matches = [
            student
            for student in self.students.values()
            if keyword in f"{student.student_id} {student.name} {student.department}".lower()
        ]
        return sorted(matches, key=lambda student: student.student_id)

    def update_student(self, student_id: str, name: str, department: str, year: int) -> None:
        student_id = student_id.strip().upper()
        student = self._get_student(student_id)
        if not name.strip() or not department.strip():
            raise ValueError("Student name and department are required.")
        if year < 1:
            raise ValueError("Year must be at least 1.")

        student.name = name.strip()
        student.department = department.strip()
        student.year = year
        self.students.update(student_id, student)

    def display_students(self) -> list[Student]:
        return sorted(
            (student for _, student in self.students.display()),
            key=lambda student: student.student_id,
        )

    def list_students(self) -> list[Student]:
        """Backward-compatible name for display_students."""
        return self.display_students()

    # Course operations: insert, delete, search, update, and display.
    def insert_course(self, code: str, name: str, credits: int) -> None:
        code = code.strip().upper()
        if not code or not name.strip():
            raise ValueError("Course code and name are required.")
        if self.courses.contains(code):
            raise ValueError("Course code already exists.")
        if credits < 1:
            raise ValueError("Credits must be at least 1.")

        self.courses.insert(code, Course(code, name.strip(), credits))
        self.enrollments.insert(self._course_vertex(code))

    def add_course(self, code: str, name: str, credits: int) -> None:
        """Backward-compatible name for insert_course."""
        self.insert_course(code, name, credits)

    def delete_course(self, code: str) -> bool:
        code = code.strip().upper()
        if not self.courses.delete(code):
            return False
        self.enrollments.delete(self._course_vertex(code))
        for student in self.students.values():
            student.scores.pop(code, None)
        return True

    def search_course_by_code(self, code: str) -> Course | None:
        return self.courses.search(code.strip().upper())

    def search_courses(self, keyword: str) -> list[Course]:
        keyword = keyword.strip().lower()
        matches = [
            course
            for course in self.courses.values()
            if keyword in f"{course.code} {course.name}".lower()
        ]
        return sorted(matches, key=lambda course: course.code)

    def update_course(self, code: str, name: str, credits: int) -> None:
        code = code.strip().upper()
        course = self._get_course(code)
        if not name.strip():
            raise ValueError("Course name is required.")
        if credits < 1:
            raise ValueError("Credits must be at least 1.")

        course.name = name.strip()
        course.credits = credits
        self.courses.update(code, course)

    def display_courses(self) -> list[Course]:
        return sorted(
            (course for _, course in self.courses.display()),
            key=lambda course: course.code,
        )

    def list_courses(self) -> list[Course]:
        """Backward-compatible name for display_courses."""
        return self.display_courses()

    # Enrollment, scoring, and report operations.
    def enroll(self, student_id: str, course_code: str) -> None:
        student_id = student_id.strip().upper()
        course_code = course_code.strip().upper()
        self._get_student(student_id)
        self._get_course(course_code)
        self.enrollments.add_edge(
            self._student_vertex(student_id), self._course_vertex(course_code)
        )

    def record_score(self, student_id: str, course_code: str, score: float) -> None:
        student_id = student_id.strip().upper()
        course_code = course_code.strip().upper()
        student = self._get_student(student_id)
        self._get_course(course_code)
        if not self.enrollments.has_edge(
            self._student_vertex(student_id), self._course_vertex(course_code)
        ):
            raise ValueError("Student is not enrolled in this course.")
        self.grade_tree.calculate(score)
        student.scores[course_code] = score

    def student_courses(self, student_id: str) -> list[Course]:
        """Return the courses in which a student is enrolled."""
        student = self._get_student(student_id.strip().upper())
        course_codes = [
            vertex.removeprefix("course:")
            for vertex in self.enrollments.neighbors(self._student_vertex(student.student_id))
            if vertex.startswith("course:")
        ]
        return sorted(
            (self._get_course(code) for code in course_codes),
            key=lambda course: course.code,
        )

    def course_students(self, course_code: str) -> list[Student]:
        """Return the students enrolled in a course."""
        course = self._get_course(course_code.strip().upper())
        student_ids = [
            vertex.removeprefix("student:")
            for vertex in self.enrollments.neighbors(self._course_vertex(course.code))
            if vertex.startswith("student:")
        ]
        return sorted(
            (self._get_student(student_id) for student_id in student_ids),
            key=lambda student: student.student_id,
        )

    def student_gpa_report(self, student_id: str) -> str:
        """Create a per-course and credit-weighted GPA report."""
        student = self._get_student(student_id.strip().upper())
        lines = [f"GPA for {student.student_id} - {student.name}:"]
        graded_courses = [
            course for course in self.student_courses(student.student_id)
            if course.code in student.scores
        ]
        if not graded_courses:
            lines.append("  No scores recorded.")
            return "\n".join(lines)

        total_grade_points = 0.0
        total_credits = 0
        for course in graded_courses:
            score = student.scores[course.code]
            result = self.grade_tree.calculate(score)
            total_grade_points += result.gpa * course.credits
            total_credits += course.credits
            lines.append(
                f"  {course.code} - {course.name}: "
                f"Score {score:.1f} | GPA {result.gpa:.1f}"
            )
        overall_gpa = total_grade_points / total_credits
        lines.append(f"Overall GPA: {overall_gpa:.2f}")
        return "\n".join(lines)

    def student_grade_report(self, student_id: str) -> str:
        """Backward-compatible name for student_gpa_report."""
        return self.student_gpa_report(student_id)

    def student_information(self, student_id: str) -> str:
        """Create a profile summary for a student or parent account."""
        student = self._get_student(student_id.strip().upper())
        return "\n".join(
            [
                f"Student ID: {student.student_id}",
                f"Name: {student.name}",
                f"Department: {student.department}",
                f"Year: {student.year}",
            ]
        )

    def student_report(self, student_id: str) -> str:
        student = self._get_student(student_id.strip().upper())
        courses = self.student_courses(student.student_id)
        lines = [
            f"Student: {student.student_id} - {student.name}",
            f"Department: {student.department} | Year: {student.year}",
            "Courses:",
        ]
        if not courses:
            lines.append("  No courses enrolled.")
        for course in courses:
            score = student.scores.get(course.code)
            result = self.grade_tree.calculate(score) if score is not None else None
            gpa = (
                f"Score {score:.1f} | GPA {result.gpa:.1f}"
                if result else "No score recorded"
            )
            lines.append(f"  {course.code} - {course.name}: {gpa}")
        if any(course.code in student.scores for course in courses):
            overall_line = self.student_gpa_report(student.student_id).splitlines()[-1]
            lines.append(overall_line)
        return "\n".join(lines)

    def display_relationships(self) -> dict[str, list[str]]:
        return self.enrollments.display()

    def _get_student(self, student_id: str) -> Student:
        student = self.students.search(student_id)
        if student is None:
            raise ValueError(f"Student '{student_id}' was not found.")
        return student

    def _get_course(self, code: str) -> Course:
        course = self.courses.search(code)
        if course is None:
            raise ValueError(f"Course '{code}' was not found.")
        return course

    @staticmethod
    def _student_vertex(student_id: str) -> str:
        return f"student:{student_id}"

    @staticmethod
    def _course_vertex(code: str) -> str:
        return f"course:{code}"

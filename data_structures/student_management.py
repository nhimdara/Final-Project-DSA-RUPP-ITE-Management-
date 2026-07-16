"""Combined data structures and operations for student management.

This module keeps the complete implementation in one place: hash tables store
records, a graph stores enrollment relationships, and a decision tree converts
scores into grades and GPA values.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from typing import Generic, Optional, TypeVar

from data import COURSES, ENROLLMENTS, SCORES, STUDENTS, USERS


# ---------------------------------------------------------------------------
# Generic hash table
# ---------------------------------------------------------------------------
# K is the key type (for example, str) and V is the stored record type.
K = TypeVar("K")
V = TypeVar("V")


class HashTable(Generic[K, V]):
    """Store records by key for fast insert, search, update, and delete."""

    def __init__(self) -> None:
        """Create an empty table backed by Python's dictionary."""
        self._items: dict[K, V] = {}

    @classmethod
    def from_items(
        cls, items: Iterable[V], key: Callable[[V], K]
    ) -> "HashTable[K, V]":
        """Build a table from values using ``key`` to identify each value."""
        table: HashTable[K, V] = cls()
        for item in items:
            table.insert(key(item), item)
        return table

    def insert(self, key: K, value: V) -> None:
        """Insert a value, replacing the old value if the key already exists."""
        self._items[key] = value

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Return a value or ``default`` when the key is absent."""
        return self._items.get(key, default)

    def search(self, key: K) -> Optional[V]:
        """Return the value for a key, or ``None`` when it is absent."""
        return self._items.get(key)

    def update(self, key: K, value: V) -> bool:
        """Replace an existing value and report whether the key was found."""
        if key not in self._items:
            return False
        self._items[key] = value
        return True

    def delete(self, key: K) -> bool:
        """Delete a value and report whether the key was found."""
        if key not in self._items:
            return False
        del self._items[key]
        return True

    def contains(self, key: K) -> bool:
        """Return whether the table contains ``key``."""
        return key in self._items

    def values(self) -> list[V]:
        """Return a snapshot of all stored values."""
        return list(self._items.values())

    def items(self) -> list[tuple[K, V]]:
        """Return a snapshot of all key-value pairs."""
        return list(self._items.items())

    def display(self) -> list[tuple[K, V]]:
        """Return table contents in a form suitable for the console UI."""
        return self.items()

    def clear(self) -> None:
        """Remove every value from the table."""
        self._items.clear()

    def __len__(self) -> int:
        """Return the number of stored values."""
        return len(self._items)

    def __iter__(self) -> Iterator[K]:
        """Iterate over keys, matching normal dictionary behavior."""
        return iter(self._items)


# ---------------------------------------------------------------------------
# Enrollment graph
# ---------------------------------------------------------------------------
class Graph:
    """Undirected graph connecting students to their enrolled courses.

    Every adjacency set stores both sides of an edge. For example, adding an
    S001-CS101 enrollment makes the course a neighbor of the student and the
    student a neighbor of the course.
    """

    def __init__(self) -> None:
        """Create an empty adjacency-list graph."""
        self.adjacency: dict[str, set[str]] = {}

    def add_vertex(self, vertex: str) -> None:
        """Add a vertex without changing it when it already exists."""
        self.adjacency.setdefault(vertex, set())

    def insert(self, vertex: str) -> None:
        """Alias used by the management system when inserting records."""
        self.add_vertex(vertex)

    def add_edge(self, first: str, second: str) -> None:
        """Connect two vertices and create missing vertices automatically."""
        self.add_vertex(first)
        self.add_vertex(second)
        self.adjacency[first].add(second)
        self.adjacency[second].add(first)

    def has_edge(self, first: str, second: str) -> bool:
        """Return whether two vertices are directly connected."""
        return second in self.adjacency.get(first, set())

    def remove_edge(self, first: str, second: str) -> None:
        """Remove both directions of an edge; missing vertices are harmless."""
        self.adjacency.get(first, set()).discard(second)
        self.adjacency.get(second, set()).discard(first)

    def remove_vertex(self, vertex: str) -> bool:
        """Remove a vertex and every edge that points to it."""
        if vertex not in self.adjacency:
            return False
        for neighbor in self.adjacency.pop(vertex, set()):
            self.adjacency[neighbor].discard(vertex)
        return True

    def delete(self, vertex: str) -> bool:
        """Alias for ``remove_vertex`` used by CRUD operations."""
        return self.remove_vertex(vertex)

    def search(self, vertex: str) -> bool:
        """Return whether a vertex exists."""
        return vertex in self.adjacency

    def update(self, old_vertex: str, new_vertex: str) -> bool:
        """Rename a vertex while preserving all its edges."""
        if old_vertex not in self.adjacency or new_vertex in self.adjacency:
            return False
        neighbors = self.adjacency.pop(old_vertex)
        self.adjacency[new_vertex] = neighbors
        for neighbor in neighbors:
            self.adjacency[neighbor].discard(old_vertex)
            self.adjacency[neighbor].add(new_vertex)
        return True

    def neighbors(self, vertex: str) -> list[str]:
        """Return directly connected vertices in stable sorted order."""
        return sorted(self.adjacency.get(vertex, set()))

    def breadth_first(self, start: str) -> list[str]:
        """Traverse the connected component from ``start`` using a queue."""
        if start not in self.adjacency:
            return []
        visited = {start}
        queue = deque([start])
        order: list[str] = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in self.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def has_path(self, first: str, second: str) -> bool:
        """Return whether ``second`` is reachable from ``first``."""
        return second in self.breadth_first(first)

    def display(self) -> dict[str, list[str]]:
        """Return a deterministic, read-only-style snapshot for display."""
        return {
            vertex: self.neighbors(vertex)
            for vertex in sorted(self.adjacency)
        }


# ---------------------------------------------------------------------------
# Grade decision tree
# ---------------------------------------------------------------------------
@dataclass(slots=True)
class GradeResult:
    """Final grade information returned after evaluating a score."""

    score: float
    grade: str
    gpa: float
    message: str


@dataclass(slots=True)
class DecisionNode:
    """A threshold branch or terminal grade in the decision tree.

    Branch nodes use ``threshold``, ``passed``, and ``failed``. Leaf nodes use
    ``grade``, ``gpa``, and ``message``.
    """

    threshold: Optional[float] = None
    grade: Optional[str] = None
    gpa: Optional[float] = None
    message: str = ""
    passed: Optional["DecisionNode"] = None
    failed: Optional["DecisionNode"] = None

    def decide(self, score: float) -> GradeResult:
        """Recursively follow thresholds until a grade leaf is reached."""
        # A grade marks this node as a terminal leaf.
        if self.grade is not None:
            if self.gpa is None:
                raise ValueError("A grade decision must include a GPA value.")
            return GradeResult(score, self.grade, self.gpa, self.message)
        if self.threshold is None:
            raise ValueError("Decision node must have either a threshold or a grade.")
        # Scores equal to the threshold take the passing branch.
        next_node = self.passed if score >= self.threshold else self.failed
        if next_node is None:
            raise ValueError("Decision tree is incomplete.")
        return next_node.decide(score)


class GradeDecisionTree:
    """Convert a score into a letter grade and GPA using threshold nodes."""

    def __init__(self) -> None:
        """Build the A/B/C/D/F threshold tree from highest to lowest."""
        self.root = DecisionNode(
            threshold=90,
            passed=DecisionNode(grade="A", gpa=4.0, message="Excellent"),
            failed=DecisionNode(
                threshold=80,
                passed=DecisionNode(grade="B", gpa=3.0, message="Very good"),
                failed=DecisionNode(
                    threshold=70,
                    passed=DecisionNode(grade="C", gpa=2.0, message="Good"),
                    failed=DecisionNode(
                        threshold=60,
                        passed=DecisionNode(
                            grade="D", gpa=1.0, message="Needs improvement"
                        ),
                        failed=DecisionNode(grade="F", gpa=0.0, message="Fail"),
                    ),
                ),
            ),
        )

    def calculate(self, score: float) -> GradeResult:
        """Validate a percentage score and return its grade result."""
        if score < 0 or score > 100:
            raise ValueError("Score must be between 0 and 100.")
        return self.root.decide(score)


# ---------------------------------------------------------------------------
# Domain records
# ---------------------------------------------------------------------------
@dataclass
class Student:
    """Student profile plus scores keyed by course code."""

    student_id: str
    name: str
    department: str
    year: int
    scores: dict[str, float] = field(default_factory=dict)


@dataclass
class Course:
    """Course metadata used for enrollment and GPA weighting."""

    code: str
    name: str
    credits: int


@dataclass(frozen=True)
class User:
    """Login account; ``student_id`` optionally limits record access."""

    username: str
    password: str
    role: str
    student_id: str = ""


class StudentManagementSystem:
    """Coordinate records, enrollments, authentication, and grade reports.

    IDs and course codes are normalized to uppercase at the public-method
    boundary. Usernames are normalized to lowercase. Student/course records
    live in hash tables, while their many-to-many enrollment relationship lives
    in the graph. Data is in memory and is rebuilt on each program start.
    """

    def __init__(self, data_file: str | Path | None = None) -> None:
        """Create each structure and load the initial data from ``data.py``.

        ``data_file`` is mainly useful for tests or alternate installations.
        When omitted, changes are saved to the project's normal ``data.py``.
        """
        self._data_file = (
            Path(data_file)
            if data_file is not None
            else Path(__file__).resolve().parents[1] / "data.py"
        )

        # Loading calls the normal CRUD methods. This flag prevents those calls
        # from rewriting data.py before every initial collection is available.
        self._loading_initial_data = True

        # Separate tables prevent key collisions between record categories.
        self.students: HashTable[str, Student] = HashTable()
        self.courses: HashTable[str, Course] = HashTable()
        self.users: HashTable[str, User] = HashTable()

        # The graph contains prefixed vertices such as ``student:S001`` and
        # ``course:CS101``. Prefixes keep both ID namespaces unambiguous.
        self.enrollments = Graph()
        self.grade_tree = GradeDecisionTree()

        # Records/courses must exist before enrollments and scores are loaded.
        self._insert_demo_data()
        self._insert_default_users()
        self._loading_initial_data = False

    def _insert_demo_data(self) -> None:
        """Load records in dependency order so references are always valid."""
        for student in STUDENTS:
            self.insert_student(**student)
        for course in COURSES:
            self.insert_course(**course)
        for enrollment in ENROLLMENTS:
            self.enroll(**enrollment)
        for score in SCORES:
            self.record_score(**score)

    # Authentication operations
    def _insert_default_users(self) -> None:
        """Load login accounts into a username-keyed hash table."""
        for user_data in USERS:
            user = User(**user_data)
            # Usernames in data.py are expected to use their canonical form.
            self.users.insert(user.username, user)

    def authenticate(self, username: str, password: str) -> User | None:
        """Return the matching account, or ``None`` for invalid credentials."""
        user = self.users.search(username.strip().lower())
        if user is None or user.password != password:
            return None
        return user

    # Student CRUD operations
    def insert_student(self, student_id: str, name: str, department: str, year: int) -> None:
        """Validate and insert a student into both the table and graph."""
        # Canonical IDs make lookup case-insensitive throughout the program.
        student_id = student_id.strip().upper()
        if not student_id or not name.strip() or not department.strip():
            raise ValueError("Student ID, name, and department are required.")
        if self.students.contains(student_id):
            raise ValueError("Student ID already exists.")
        if year < 1:
            raise ValueError("Year must be at least 1.")

        student = Student(student_id, name.strip(), department.strip(), year)
        self.students.insert(student_id, student)
        # Create the isolated vertex now; enrollment edges can be added later.
        self.enrollments.insert(self._student_vertex(student_id))
        self._persist_data()

    def add_student(self, student_id: str, name: str, department: str, year: int) -> None:
        """Backward-compatible name for insert_student."""
        self.insert_student(student_id, name, department, year)

    def delete_student(self, student_id: str) -> bool:
        """Delete a student and its enrollments unless an account links to it."""
        student_id = student_id.strip().upper()
        # A linked student/parent account must never point at a deleted record.
        if any(user.student_id.upper() == student_id for user in self.users.values()):
            raise ValueError(
                "Cannot delete this student because a login account is linked to it."
            )
        if not self.students.delete(student_id):
            return False
        # Graph deletion also removes every course edge for this student.
        self.enrollments.delete(self._student_vertex(student_id))
        self._persist_data()
        return True

    def search_student_by_id(self, student_id: str) -> Student | None:
        """Look up one student by a case-insensitive ID."""
        return self.students.search(student_id.strip().upper())

    def search_students(self, keyword: str) -> list[Student]:
        """Search IDs, names, and departments with a case-insensitive term."""
        keyword = keyword.strip().lower()
        matches = [
            student
            for student in self.students.values()
            if keyword in f"{student.student_id} {student.name} {student.department}".lower()
        ]
        return sorted(matches, key=lambda student: student.student_id)

    def update_student(self, student_id: str, name: str, department: str, year: int) -> None:
        """Update the editable profile fields of an existing student."""
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
        self._persist_data()

    def display_students(self) -> list[Student]:
        """Return every student sorted by ID for predictable display."""
        return sorted(
            (student for _, student in self.students.display()),
            key=lambda student: student.student_id,
        )

    def list_students(self) -> list[Student]:
        """Backward-compatible name for display_students."""
        return self.display_students()

    # Course CRUD operations
    def insert_course(self, code: str, name: str, credits: int) -> None:
        """Validate and insert a course into both the table and graph."""
        code = code.strip().upper()
        if not code or not name.strip():
            raise ValueError("Course code and name are required.")
        if self.courses.contains(code):
            raise ValueError("Course code already exists.")
        if credits < 1:
            raise ValueError("Credits must be at least 1.")

        self.courses.insert(code, Course(code, name.strip(), credits))
        # Courses start as isolated vertices until students enroll.
        self.enrollments.insert(self._course_vertex(code))
        self._persist_data()

    def add_course(self, code: str, name: str, credits: int) -> None:
        """Backward-compatible name for insert_course."""
        self.insert_course(code, name, credits)

    def delete_course(self, code: str) -> bool:
        """Delete a course, its enrollment edges, and associated scores."""
        code = code.strip().upper()
        if not self.courses.delete(code):
            return False
        self.enrollments.delete(self._course_vertex(code))
        # Scores are stored on Student, so they require explicit cleanup.
        for student in self.students.values():
            student.scores.pop(code, None)
        self._persist_data()
        return True

    def search_course_by_code(self, code: str) -> Course | None:
        """Look up one course by a case-insensitive code."""
        return self.courses.search(code.strip().upper())

    def search_courses(self, keyword: str) -> list[Course]:
        """Search course codes and names with a case-insensitive term."""
        keyword = keyword.strip().lower()
        matches = [
            course
            for course in self.courses.values()
            if keyword in f"{course.code} {course.name}".lower()
        ]
        return sorted(matches, key=lambda course: course.code)

    def update_course(self, code: str, name: str, credits: int) -> None:
        """Update the name and credit weight of an existing course."""
        code = code.strip().upper()
        course = self._get_course(code)
        if not name.strip():
            raise ValueError("Course name is required.")
        if credits < 1:
            raise ValueError("Credits must be at least 1.")

        course.name = name.strip()
        course.credits = credits
        self.courses.update(code, course)
        self._persist_data()

    def display_courses(self) -> list[Course]:
        """Return every course sorted by code for predictable display."""
        return sorted(
            (course for _, course in self.courses.display()),
            key=lambda course: course.code,
        )

    def list_courses(self) -> list[Course]:
        """Backward-compatible name for display_courses."""
        return self.display_courses()

    # Enrollment and scoring operations
    def enroll(self, student_id: str, course_code: str) -> None:
        """Connect an existing student and course in the enrollment graph."""
        student_id = student_id.strip().upper()
        course_code = course_code.strip().upper()
        self._get_student(student_id)
        self._get_course(course_code)
        self.enrollments.add_edge(
            self._student_vertex(student_id), self._course_vertex(course_code)
        )
        self._persist_data()

    def record_score(self, student_id: str, course_code: str, score: float) -> None:
        """Save a valid score for a student enrolled in the given course."""
        student_id = student_id.strip().upper()
        course_code = course_code.strip().upper()
        student = self._get_student(student_id)
        self._get_course(course_code)
        if not self.enrollments.has_edge(
            self._student_vertex(student_id), self._course_vertex(course_code)
        ):
            raise ValueError("Student is not enrolled in this course.")
        # Calculation validates the 0-100 range before the score is persisted.
        self.grade_tree.calculate(score)
        student.scores[course_code] = score
        self._persist_data()

    def student_courses(self, student_id: str) -> list[Course]:
        """Return the courses in which a student is enrolled."""
        student = self._get_student(student_id.strip().upper())
        # A student vertex should only connect to course-prefixed vertices.
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
        # A course vertex should only connect to student-prefixed vertices.
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
            # More-credit courses contribute proportionally more to the GPA.
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
        """Create a complete profile, course, score, and GPA summary."""
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
        """Return all enrollment vertices and edges for administrator display."""
        return self.enrollments.display()

    # Persistence helpers
    def _persist_data(self) -> None:
        """Atomically save the complete in-memory state to ``data.py``.

        Saving every related collection together keeps students, courses,
        enrollments, and scores consistent. A temporary file is replaced only
        after the complete Python source has been written successfully.
        """
        if self._loading_initial_data:
            return

        users = tuple(
            {
                "username": user.username,
                "password": user.password,
                "role": user.role,
                "student_id": user.student_id,
            }
            for user in sorted(self.users.values(), key=lambda item: item.username)
        )
        students = tuple(
            {
                "student_id": student.student_id,
                "name": student.name,
                "department": student.department,
                "year": student.year,
            }
            for student in self.display_students()
        )
        courses = tuple(
            {
                "code": course.code,
                "name": course.name,
                "credits": course.credits,
            }
            for course in self.display_courses()
        )

        # Derive relationships from the graph instead of maintaining a second
        # enrollment collection that could become out of sync.
        enrollments = tuple(
            {"student_id": student.student_id, "course_code": course.code}
            for student in self.display_students()
            for course in self.student_courses(student.student_id)
        )
        scores = tuple(
            {
                "student_id": student.student_id,
                "course_code": course.code,
                "score": student.scores[course.code],
            }
            for student in self.display_students()
            for course in self.student_courses(student.student_id)
            if course.code in student.scores
        )

        collections = (
            ("USERS", users),
            ("STUDENTS", students),
            ("COURSES", courses),
            ("ENROLLMENTS", enrollments),
            ("SCORES", scores),
        )
        source = (
            '"""Persistent data for the Student Management System.\n\n'
            "This file is updated automatically when records change through "
            'the console.\n"""\n\n'
            "from __future__ import annotations\n\n\n"
        )
        source += "\n\n".join(
            f"{name} = {pformat(values, width=88, sort_dicts=False)}"
            for name, values in collections
        )
        source += "\n"

        temporary_file = self._data_file.with_name(f".{self._data_file.name}.tmp")
        try:
            temporary_file.write_text(source, encoding="utf-8")
            temporary_file.replace(self._data_file)
        except OSError as exc:
            # The menu already displays ValueError messages cleanly to users.
            temporary_file.unlink(missing_ok=True)
            raise ValueError(f"Could not save data to '{self._data_file}'.") from exc

    # Internal lookup helpers centralize consistent not-found errors.
    def _get_student(self, student_id: str) -> Student:
        """Return an existing student or raise a user-facing ``ValueError``."""
        student = self.students.search(student_id)
        if student is None:
            raise ValueError(f"Student '{student_id}' was not found.")
        return student

    def _get_course(self, code: str) -> Course:
        """Return an existing course or raise a user-facing ``ValueError``."""
        course = self.courses.search(code)
        if course is None:
            raise ValueError(f"Course '{code}' was not found.")
        return course

    @staticmethod
    def _student_vertex(student_id: str) -> str:
        """Create the graph namespace key for a student ID."""
        return f"student:{student_id}"

    @staticmethod
    def _course_vertex(code: str) -> str:
        """Create the graph namespace key for a course code."""
        return f"course:{code}"

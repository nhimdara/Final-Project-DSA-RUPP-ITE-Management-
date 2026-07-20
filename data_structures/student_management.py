"""
Student Management System - core data structures.

This file re-implements the three data structures from your Data Structures
course using the classic textbook approach, instead of relying on Python's
built-in dict/set shortcuts:

    1. Hash Table  -> array of buckets + chaining (separate chaining)
    2. Graph       -> adjacency list (dictionary of lists)
    3. Decision Tree -> binary tree of nodes, walked recursively

Plain classes (no dataclasses, no typing generics) are used throughout so the
code reads the same way it would in a lesson or a textbook.
"""

from collections import deque
import math
from pathlib import Path
from pprint import pformat

from data import COURSES, ENROLLMENTS, SCORES, STUDENTS, USERS


# Every student belongs to this single department. Keeping the value in one
# constant prevents different spellings from being saved in student records.
DEPARTMENT = "Information Technology Engineering"


# ---------------------------------------------------------------------------
# 1. HASH TABLE  (separate chaining)
# ---------------------------------------------------------------------------
# A hash table stores (key, value) pairs. Instead of computing an index and
# putting ONE item there, we put a small LIST ("bucket") at every index.
# If two keys hash to the same index (a "collision"), they simply live in the
# same bucket's list. This is the "separate chaining" method taught in class.


class HashTable:
    """A hash table with a fixed number of buckets and chaining."""

    def __init__(self, capacity=101):
        # capacity = number of buckets. A prime number spreads keys out more
        # evenly, which is why 101 (instead of 100) is used here.
        self.capacity = capacity
        # Each bucket starts as an empty list that will hold [key, value] pairs.
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0  # how many items are currently stored

    def _hash(self, key):
        """Turn a key into a bucket index between 0 and capacity - 1."""
        # Python's built-in hash() works for any hashable key (strings, etc).
        # We only care about a non-negative index, so we take it mod capacity.
        return hash(key) % self.capacity

    def insert(self, key, value):
        """Insert a (key, value) pair, or overwrite the value if key exists."""
        index = self._hash(key)
        bucket = self.buckets[index]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value  # key already there -> just update it
                return
        bucket.append([key, value])
        self.size += 1

    def search(self, key):
        """Return the value stored for key, or None if it is not present."""
        index = self._hash(key)
        bucket = self.buckets[index]
        for stored_key, stored_value in bucket:
            if stored_key == key:
                return stored_value
        return None

    def get(self, key, default=None):
        """Same as search(), but lets you choose the value returned if missing."""
        value = self.search(key)
        return default if value is None else value

    def update(self, key, value):
        """Replace an existing value. Returns True if key was found."""
        index = self._hash(key)
        bucket = self.buckets[index]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return True
        return False

    def delete(self, key):
        """Remove a key from the table. Returns True if key was found."""
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, pair in enumerate(bucket):
            if pair[0] == key:
                bucket.pop(i)
                self.size -= 1
                return True
        return False

    def contains(self, key):
        """Return True if key exists in the table."""
        return self.search(key) is not None

    def keys(self):
        """Return a list of every key currently stored."""
        result = []
        for bucket in self.buckets:
            for key, _value in bucket:
                result.append(key)
        return result

    def values(self):
        """Return a list of every value currently stored."""
        result = []
        for bucket in self.buckets:
            for _key, value in bucket:
                result.append(value)
        return result

    def items(self):
        """Return a list of (key, value) tuples for every stored pair."""
        result = []
        for bucket in self.buckets:
            for key, value in bucket:
                result.append((key, value))
        return result

    def __len__(self):
        return self.size


# ---------------------------------------------------------------------------
# 2. GRAPH  (adjacency list, undirected)
# ---------------------------------------------------------------------------
# The graph connects students to the courses they are enrolled in. Each
# vertex (student or course) keeps a plain LIST of its neighbors. Because the
# graph is undirected, adding an edge A-B adds B to A's list AND A to B's list.


class Graph:
    """Undirected graph stored as an adjacency list (dict of lists)."""

    def __init__(self):
        self.adjacency = {}  # vertex -> list of neighboring vertices

    def add_vertex(self, vertex):
        """Add a vertex with no edges yet, if it doesn't already exist."""
        if vertex not in self.adjacency:
            self.adjacency[vertex] = []

    def add_edge(self, first, second):
        """Connect two vertices and return whether a new edge was created."""
        self.add_vertex(first)
        self.add_vertex(second)
        if self.has_edge(first, second):
            return False
        if second not in self.adjacency[first]:
            self.adjacency[first].append(second)
        if first not in self.adjacency[second]:
            self.adjacency[second].append(first)
        return True

    def has_edge(self, first, second):
        """Return True if first and second are directly connected."""
        return second in self.adjacency.get(first, [])

    def remove_edge(self, first, second):
        """Disconnect two vertices, if the edge exists."""
        if first in self.adjacency and second in self.adjacency[first]:
            self.adjacency[first].remove(second)
        if second in self.adjacency and first in self.adjacency[second]:
            self.adjacency[second].remove(first)

    def remove_vertex(self, vertex):
        """Remove a vertex and every edge pointing to it. Returns True if found."""
        if vertex not in self.adjacency:
            return False
        for neighbor in self.adjacency.pop(vertex):
            self.adjacency[neighbor].remove(vertex)
        return True

    def neighbors(self, vertex):
        """Return the sorted list of vertices directly connected to vertex."""
        return sorted(self.adjacency.get(vertex, []))

    def breadth_first_search(self, start):
        """Classic BFS: visit start, then its neighbors, then their neighbors..."""
        if start not in self.adjacency:
            return []
        visited = {start}
        queue = deque([start])   # FIFO queue -> breadth-first order
        order = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in self.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def display(self):
        """Return every vertex with its neighbors, sorted for readability."""
        return {vertex: self.neighbors(vertex) for vertex in sorted(self.adjacency)}


# ---------------------------------------------------------------------------
# 3. DECISION TREE  (binary tree, walked recursively)
# ---------------------------------------------------------------------------
# Each node either:
#   - holds a threshold and points to a "yes" branch and a "no" branch, or
#   - is a leaf holding the final grade.
# Converting a score to a grade means starting at the root and walking down,
# going left or right depending on the score, until a leaf is reached.


class TreeNode:
    """One node of the grading decision tree."""

    def __init__(self, threshold=None, yes_branch=None, no_branch=None,
                 grade=None, gpa=None, message=""):
        self.threshold = threshold      # only set on branch nodes
        self.yes_branch = yes_branch    # taken when score >= threshold
        self.no_branch = no_branch      # taken when score <  threshold
        self.grade = grade              # only set on leaf nodes
        self.gpa = gpa
        self.message = message

    def is_leaf(self):
        return self.grade is not None


class GradeResult:
    """Plain container for the outcome of grading one score."""

    def __init__(self, score, grade, gpa, message):
        self.score = score
        self.grade = grade
        self.gpa = gpa
        self.message = message


class GradeDecisionTree:
    """A small binary decision tree that turns a 0-100 score into a grade."""

    def __init__(self):
        # Build the tree from the bottom up so each branch can point to the
        # nodes below it.
        f_leaf = TreeNode(grade="F", gpa=0.0, message="Fail")
        d_leaf = TreeNode(grade="D", gpa=1.0, message="Needs improvement")
        c_leaf = TreeNode(grade="C", gpa=2.0, message="Good")
        b_leaf = TreeNode(grade="B", gpa=3.0, message="Very good")
        a_leaf = TreeNode(grade="A", gpa=4.0, message="Excellent")

        branch_60 = TreeNode(threshold=60, yes_branch=d_leaf, no_branch=f_leaf)
        branch_70 = TreeNode(threshold=70, yes_branch=c_leaf, no_branch=branch_60)
        branch_80 = TreeNode(threshold=80, yes_branch=b_leaf, no_branch=branch_70)
        self.root = TreeNode(threshold=90, yes_branch=a_leaf, no_branch=branch_80)

    def calculate(self, score):
        """Validate the score, then walk the tree from the root to a leaf."""
        if not isinstance(score, (int, float)) or not math.isfinite(score):
            raise ValueError("Score must be a finite number between 0 and 100.")
        if score < 0 or score > 100:
            raise ValueError("Score must be between 0 and 100.")

        current = self.root
        while True:
            # Branch links are optional when a TreeNode is created, so verify
            # the node before accessing it. This also lets static type checkers
            # safely narrow ``current`` from TreeNode | None to TreeNode.
            if current is None:
                raise RuntimeError("The grade decision tree is incomplete.")
            if current.is_leaf():
                return GradeResult(
                    score, current.grade, current.gpa, current.message
                )
            if current.threshold is None:
                raise RuntimeError("A grade decision branch has no threshold.")

            if score >= current.threshold:
                current = current.yes_branch
            else:
                current = current.no_branch


# ---------------------------------------------------------------------------
# Domain records (plain classes, no dataclasses)
# ---------------------------------------------------------------------------
class Student:
    def __init__(self, student_id, name, department, year):
        self.student_id = student_id
        self.name = name
        self.department = department
        self.year = year
        self.scores = {}  # course_code -> score


class Course:
    def __init__(self, code, name, credits):
        self.code = code
        self.name = name
        self.credits = credits


class User:
    def __init__(self, username, password, role, student_id=""):
        self.username = username
        self.password = password
        self.role = role
        self.student_id = student_id


# ---------------------------------------------------------------------------
# Student Management System
# ---------------------------------------------------------------------------
class StudentManagementSystem:
    """Coordinates records, enrollments, authentication, and grade reports.

    - students / courses / users are stored in HashTables (fast lookup by ID).
    - enrollments (student <-> course) are stored in the Graph.
    - scores are converted into letter grades using the GradeDecisionTree.
    """

    def __init__(self, data_file=None):
        self._data_file = (
            Path(data_file)
            if data_file is not None
            else Path(__file__).resolve().parents[1] / "data.py"
        )

        # Prevents saving to disk while the starting data is still loading.
        self._loading_initial_data = True

        self.students = HashTable()
        self.courses = HashTable()
        self.users = HashTable()

        # Vertices are prefixed ("student:S001" / "course:CS101") so the two
        # ID spaces never collide inside the same graph.
        self.enrollments = Graph()
        self.grade_tree = GradeDecisionTree()

        self._insert_demo_data()
        self._insert_default_users()
        self._loading_initial_data = False

    def _insert_demo_data(self):
        for student in STUDENTS:
            self.insert_student(**student)
        for course in COURSES:
            self.insert_course(**course)
        for enrollment in ENROLLMENTS:
            self.enroll(**enrollment)
        for score in SCORES:
            self.record_score(**score)

    # -- Authentication -----------------------------------------------------
    def _insert_default_users(self):
        for user_data in USERS:
            user = User(**user_data)
            self.users.insert(user.username, user)

    def authenticate(self, username, password):
        user = self.users.search(username.strip().lower())
        if user is None or user.password != password:
            return None
        return user

    # -- Student CRUD ---------------------------------------------------
    def insert_student(self, student_id, name, department, year):
        student_id = student_id.strip().upper()
        if not student_id or not name.strip():
            raise ValueError("Student ID and name are required.")
        # Also enforce the fixed department for calls made outside main.py.
        if department.strip() != DEPARTMENT:
            raise ValueError(f"Department must be '{DEPARTMENT}'.")
        if self.students.contains(student_id):
            raise ValueError("Student ID already exists.")
        if year < 1:
            raise ValueError("Year must be at least 1.")

        student = Student(student_id, name.strip(), department.strip(), year)
        self.students.insert(student_id, student)
        self.enrollments.add_vertex(self._student_vertex(student_id))
        self._persist_data()

    def add_student(self, student_id, name, department, year):
        self.insert_student(student_id, name, department, year)

    def delete_student(self, student_id):
        student_id = student_id.strip().upper()
        if any(user.student_id.upper() == student_id for user in self.users.values()):
            raise ValueError(
                "Cannot delete this student because a login account is linked to it."
            )
        if not self.students.delete(student_id):
            return False
        self.enrollments.remove_vertex(self._student_vertex(student_id))
        self._persist_data()
        return True

    def search_student_by_id(self, student_id):
        return self.students.search(student_id.strip().upper())

    def search_students(self, keyword):
        keyword = keyword.strip().lower()
        matches = [
            student
            for student in self.students.values()
            if keyword in f"{student.student_id} {student.name} {student.department}".lower()
        ]
        return sorted(matches, key=lambda student: student.student_id)

    def update_student(self, student_id, name, department, year):
        student_id = student_id.strip().upper()
        student = self._get_student(student_id)
        if not name.strip():
            raise ValueError("Student name is required.")
        # Updating a student must not introduce a second department.
        if department.strip() != DEPARTMENT:
            raise ValueError(f"Department must be '{DEPARTMENT}'.")
        if year < 1:
            raise ValueError("Year must be at least 1.")

        student.name = name.strip()
        student.department = department.strip()
        student.year = year
        self.students.update(student_id, student)
        self._persist_data()

    def display_students(self):
        return sorted(self.students.values(), key=lambda student: student.student_id)

    def list_students(self):
        return self.display_students()

    # -- Course CRUD ----------------------------------------------------
    def insert_course(self, code, name, credits):
        code = code.strip().upper()
        if not code or not name.strip():
            raise ValueError("Course code and name are required.")
        if self.courses.contains(code):
            raise ValueError("Course code already exists.")
        if credits < 1:
            raise ValueError("Credits must be at least 1.")

        self.courses.insert(code, Course(code, name.strip(), credits))
        self.enrollments.add_vertex(self._course_vertex(code))
        self._persist_data()

    def insert_course_automatically(self, name, credits):
        """Insert a course with the next available C001-style code."""
        number = 1
        code = f"C{number:03d}"
        # Existing course codes may not be sequential, so keep checking until
        # an unused generated code is found.
        while self.courses.contains(code):
            number += 1
            code = f"C{number:03d}"

        self.insert_course(code, name, credits)
        return code

    def add_course(self, code, name, credits):
        self.insert_course(code, name, credits)

    def delete_course(self, code):
        code = code.strip().upper()
        if not self.courses.delete(code):
            return False
        self.enrollments.remove_vertex(self._course_vertex(code))
        for student in self.students.values():
            student.scores.pop(code, None)
        self._persist_data()
        return True

    def search_course_by_code(self, code):
        return self.courses.search(code.strip().upper())

    def search_courses(self, keyword):
        keyword = keyword.strip().lower()
        matches = [
            course
            for course in self.courses.values()
            if keyword in f"{course.code} {course.name}".lower()
        ]
        return sorted(matches, key=lambda course: course.code)

    def update_course(self, code, name, credits):
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

    def display_courses(self):
        return sorted(self.courses.values(), key=lambda course: course.code)

    def list_courses(self):
        return self.display_courses()

    # -- Enrollment and scoring ------------------------------------------
    def enroll(self, student_id, course_code):
        student_id = student_id.strip().upper()
        course_code = course_code.strip().upper()
        self._get_student(student_id)
        self._get_course(course_code)
        created = self.enrollments.add_edge(
            self._student_vertex(student_id), self._course_vertex(course_code)
        )
        if not created:
            raise ValueError(
                f"Student '{student_id}' is already enrolled in course "
                f"'{course_code}'."
            )
        self._persist_data()
        return True

    def record_score(self, student_id, course_code, score):
        student_id = student_id.strip().upper()
        course_code = course_code.strip().upper()
        student = self._get_student(student_id)
        self._get_course(course_code)
        if not self.enrollments.has_edge(
            self._student_vertex(student_id), self._course_vertex(course_code)
        ):
            raise ValueError("Student is not enrolled in this course.")
        self.grade_tree.calculate(score)  # validates the 0-100 range
        student.scores[course_code] = score
        self._persist_data()

    def student_courses(self, student_id):
        student = self._get_student(student_id.strip().upper())
        course_codes = [
            vertex[len("course:"):]
            for vertex in self.enrollments.neighbors(self._student_vertex(student.student_id))
            if vertex.startswith("course:")
        ]
        return sorted(
            (self._get_course(code) for code in course_codes),
            key=lambda course: course.code,
        )

    def course_students(self, course_code):
        course = self._get_course(course_code.strip().upper())
        student_ids = [
            vertex[len("student:"):]
            for vertex in self.enrollments.neighbors(self._course_vertex(course.code))
            if vertex.startswith("student:")
        ]
        return sorted(
            (self._get_student(student_id) for student_id in student_ids),
            key=lambda student: student.student_id,
        )

    def student_gpa_report(self, student_id):
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

    def student_grade_report(self, student_id):
        return self.student_gpa_report(student_id)

    def student_information(self, student_id):
        student = self._get_student(student_id.strip().upper())
        return "\n".join(
            [
                f"Student ID: {student.student_id}",
                f"Name: {student.name}",
                f"Department: {student.department}",
                f"Year: {student.year}",
            ]
        )

    def student_report(self, student_id):
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

    def display_relationships(self):
        return self.enrollments.display()

    # -- Persistence ------------------------------------------------------
    def _persist_data(self):
        """Save the complete in-memory state to data.py."""
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
            {"code": course.code, "name": course.name, "credits": course.credits}
            for course in self.display_courses()
        )
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
            temporary_file.unlink(missing_ok=True)
            raise ValueError(f"Could not save data to '{self._data_file}'.") from exc

    # -- Internal lookup helpers ------------------------------------------
    def _get_student(self, student_id):
        student = self.students.search(student_id)
        if student is None:
            raise ValueError(f"Student '{student_id}' was not found.")
        return student

    def _get_course(self, code):
        course = self.courses.search(code)
        if course is None:
            raise ValueError(f"Course '{code}' was not found.")
        return course

    @staticmethod
    def _student_vertex(student_id):
        return f"student:{student_id}"

    @staticmethod
    def _course_vertex(code):
        return f"course:{code}"

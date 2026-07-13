from __future__ import annotations

from collections import Counter
from math import isfinite
from statistics import mean
from typing import Optional, TypedDict

from database.queries import execute, fetch_all, fetch_one
from data_structures.tree import GradeDecisionTree
from models.score import Score


class StudentPerformance(TypedDict):
    student_id: str
    average: float
    grade: str
    subjects: int
    grade_counts: dict[str, int]


DEFAULT_SEMESTER = "Semester 1"
DEFAULT_ACADEMIC_YEAR = "2026"

SCORE_SELECT = """
SELECT
    sc.id,
    sc.student_id,
    COALESCE(st.name, '') AS student_name,
    sc.course_id,
    COALESCE(c.code, '') AS course_code,
    COALESCE(c.name, '') AS course_name,
    sc.score,
    sc.grade,
    sc.semester,
    sc.academic_year,
    sc.recorded_by,
    sc.recorded_at
FROM scores sc
JOIN students st ON st.id = sc.student_id
JOIN courses c ON c.id = sc.course_id
"""


class ScoreController:
    def __init__(self) -> None:
        self.grade_tree = GradeDecisionTree()

    def save_score(
        self,
        student_id: str,
        course_id: int,
        score: float,
        semester: str = "Semester 1",
        academic_year: str = "2026",
        recorded_by: Optional[int] = None,
    ) -> Score:
        student_id = student_id.strip().upper()
        if not student_id:
            raise ValueError("Student ID is required.")
        if course_id <= 0:
            raise ValueError("Course ID is required.")
        numeric_score = float(score)
        semester = semester.strip() or DEFAULT_SEMESTER
        academic_year = academic_year.strip() or DEFAULT_ACADEMIC_YEAR
        if not isfinite(numeric_score):
            raise ValueError("Score must be a finite number.")
        result = self.grade_tree.calculate(numeric_score)
        params = (
            student_id,
            course_id,
            numeric_score,
            result.grade,
            semester,
            academic_year,
            recorded_by,
        )
        execute(
            """
            INSERT INTO scores
                (student_id, course_id, score, grade, semester, academic_year, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                score = VALUES(score),
                grade = VALUES(grade),
                recorded_by = VALUES(recorded_by),
                recorded_at = CURRENT_TIMESTAMP
            """,
            params,
        )
        return self.get_score(student_id, course_id, semester, academic_year)

    def get_score(
        self,
        student_id: str,
        course_id: int,
        semester: str,
        academic_year: str,
    ) -> Score:
        row = fetch_one(
            f"""
            {SCORE_SELECT}
            WHERE sc.student_id = ?
              AND sc.course_id = ?
              AND sc.semester = ?
              AND sc.academic_year = ?
            """,
            (
                student_id.strip().upper(),
                course_id,
                semester.strip() or DEFAULT_SEMESTER,
                academic_year.strip() or DEFAULT_ACADEMIC_YEAR,
            ),
        )
        if row is None:
            raise ValueError("Score not found.")
        return Score.from_row(row)

    def list_scores(self) -> list[Score]:
        rows = fetch_all(f"{SCORE_SELECT} ORDER BY st.id, c.code, sc.academic_year, sc.semester")
        return [Score.from_row(row) for row in rows]

    def scores_for_student(self, student_id: str) -> list[Score]:
        rows = fetch_all(
            f"""
            {SCORE_SELECT}
            WHERE sc.student_id = ?
            ORDER BY sc.academic_year, sc.semester, c.code
            """,
            (student_id.strip().upper(),),
        )
        return [Score.from_row(row) for row in rows]

    def scores_for_course(self, course_id: int) -> list[Score]:
        rows = fetch_all(
            f"{SCORE_SELECT} WHERE sc.course_id = ? ORDER BY st.id, sc.academic_year, sc.semester",
            (course_id,),
        )
        return [Score.from_row(row) for row in rows]

    def performance_for_student(self, student_id: str) -> StudentPerformance:
        scores = self.scores_for_student(student_id)
        if not scores:
            return {
                "student_id": student_id.strip().upper(),
                "average": 0.0,
                "grade": "N/A",
                "subjects": 0,
                "grade_counts": {},
            }
        average = round(mean(score.score for score in scores), 2)
        grade = self.grade_tree.calculate(average).grade
        return {
            "student_id": student_id.strip().upper(),
            "average": average,
            "grade": grade,
            "subjects": len(scores),
            "grade_counts": dict(Counter(score.grade for score in scores)),
        }

    def delete_score(self, score_id: int) -> bool:
        row = fetch_one("SELECT id FROM scores WHERE id = ?", (score_id,))
        if row is None:
            return False
        execute("DELETE FROM scores WHERE id = ?", (score_id,))
        return True

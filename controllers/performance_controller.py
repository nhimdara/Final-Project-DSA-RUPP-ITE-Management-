from __future__ import annotations

from typing import TypedDict

from controllers.score_controller import ScoreController, StudentPerformance
from database.queries import fetch_all
from data_structures.tree import GradeDecisionTree


class RankedStudent(TypedDict):
    student_id: str
    student_name: str
    department: str
    average_score: float
    grade: str
    subjects: int


class DepartmentPerformanceSummary(TypedDict):
    department: str
    students: int
    scores: int
    average_score: float
    grade: str


class PerformanceController:
    def __init__(self) -> None:
        self.scores = ScoreController()
        self.grade_tree = GradeDecisionTree()

    def calculate_grade(self, score: float) -> str:
        return self.grade_tree.calculate(score).grade

    def student_performance(self, student_id: str) -> StudentPerformance:
        return self.scores.performance_for_student(student_id)

    def top_students(self, limit: int = 10) -> list[RankedStudent]:
        rows = fetch_all(
            """
            SELECT
                st.id AS student_id,
                st.name AS student_name,
                COALESCE(d.name, '') AS department,
                ROUND(AVG(sc.score), 2) AS average_score,
                COUNT(sc.id) AS subjects
            FROM students st
            JOIN scores sc ON sc.student_id = st.id
            LEFT JOIN departments d ON d.id = st.department_id
            GROUP BY st.id, st.name, d.name
            ORDER BY average_score DESC, st.id
            LIMIT ?
            """,
            (limit,),
        )
        result: list[RankedStudent] = []
        for row in rows:
            average = float(row["average_score"])
            result.append(
                {
                    "student_id": str(row["student_id"]),
                    "student_name": str(row["student_name"]),
                    "department": str(row["department"]),
                    "average_score": average,
                    "grade": self.calculate_grade(average),
                    "subjects": int(row["subjects"]),
                }
            )
        return result

    def department_summary(self) -> list[DepartmentPerformanceSummary]:
        rows = fetch_all(
            """
            SELECT
                d.name AS department,
                COUNT(DISTINCT st.id) AS students,
                COUNT(sc.id) AS scores,
                ROUND(AVG(sc.score), 2) AS average_score
            FROM departments d
            LEFT JOIN students st ON st.department_id = d.id
            LEFT JOIN scores sc ON sc.student_id = st.id
            GROUP BY d.id, d.name
            ORDER BY d.name
            """
        )
        summaries: list[DepartmentPerformanceSummary] = []
        for row in rows:
            average = row["average_score"]
            summaries.append(
                {
                    "department": str(row["department"]),
                    "students": int(row["students"]),
                    "scores": int(row["scores"]),
                    "average_score": float(average) if average is not None else 0.0,
                    "grade": self.calculate_grade(float(average)) if average is not None else "N/A",
                }
            )
        return summaries

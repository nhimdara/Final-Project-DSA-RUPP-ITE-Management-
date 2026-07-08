from __future__ import annotations

from controllers.course_controller import CourseController
from controllers.department_controller import DepartmentController
from controllers.performance_controller import PerformanceController
from controllers.score_controller import ScoreController
from controllers.student_controller import StudentController
from database.db import execute
from data_structures.graph import build_academic_graph
from models.report import Report
from reports.report_generator import ReportGenerator


class ReportController:
    def __init__(self) -> None:
        self.students = StudentController()
        self.courses = CourseController()
        self.departments = DepartmentController()
        self.scores = ScoreController()
        self.performance = PerformanceController()
        self.generator = ReportGenerator()

    def student_list_report(self) -> Report:
        students = self.students.list_students()
        rows = [
            {
                "ID": student.id,
                "Name": student.name,
                "Department": student.department_name,
                "Year": student.year,
                "Phone": student.phone,
            }
            for student in students
        ]
        return Report(
            title="Student List Report",
            report_type="students",
            rows=rows,
            summary={"Total students": len(students)},
        )

    def score_report(self) -> Report:
        scores = self.scores.list_scores()
        rows = [
            {
                "Student ID": score.student_id,
                "Student": score.student_name,
                "Course": score.course_code,
                "Score": score.score,
                "Grade": score.grade,
                "Semester": score.semester,
                "Year": score.academic_year,
            }
            for score in scores
        ]
        return Report(
            title="Score Report",
            report_type="scores",
            rows=rows,
            summary={"Total scores": len(scores)},
        )

    def performance_report(self) -> Report:
        ranked_students = self.performance.top_students(limit=50)
        rows = [
            {
                "Student ID": student["student_id"],
                "Student": student["student_name"],
                "Department": student["department"],
                "Average": student["average_score"],
                "Grade": student["grade"],
                "Subjects": student["subjects"],
            }
            for student in ranked_students
        ]
        return Report(
            title="Performance Report",
            report_type="performance",
            rows=rows,
            summary={"Ranked students": len(rows)},
        )

    def relationship_graph_report(self) -> Report:
        graph = build_academic_graph(
            self.departments.list_departments(),
            self.courses.list_courses(),
            self.students.list_students(),
        )
        rows = [
            {"Source": source, "Target": target}
            for source, targets in graph.as_dict().items()
            for target in targets
        ]
        return Report(
            title="Academic Relationship Graph",
            report_type="graph",
            rows=rows,
            summary={"Vertices": len(graph.vertices()), "Relationships": len(rows)},
        )

    def save_report(self, report: Report, generated_by: int | None = None) -> str:
        path = self.generator.save_text_report(report)
        execute(
            """
            INSERT INTO report_history (title, report_type, generated_by, file_path)
            VALUES (?, ?, ?, ?)
            """,
            (report.title, report.report_type, generated_by, str(path)),
        )
        return str(path)

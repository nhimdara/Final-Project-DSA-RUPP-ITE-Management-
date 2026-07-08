from __future__ import annotations

from controllers.course_controller import CourseController
from controllers.performance_controller import PerformanceController
from controllers.score_controller import ScoreController
from views.menu import (
    menu_choice,
    pause,
    print_table,
    prompt_float,
    prompt_int,
    prompt_optional,
    prompt_required,
    show_error,
    show_success,
)


COURSE_PICKER_COLUMNS = [
    ("id", "ID"),
    ("code", "Code"),
    ("name", "Name"),
    ("department", "Department"),
]
STUDENT_SCORE_COLUMNS = [
    ("course", "Course"),
    ("name", "Name"),
    ("score", "Score"),
    ("grade", "Grade"),
    ("semester", "Semester"),
    ("year", "Year"),
]
TOP_STUDENT_COLUMNS = [
    ("student_id", "ID"),
    ("student_name", "Name"),
    ("department", "Department"),
    ("average_score", "Average"),
    ("grade", "Grade"),
    ("subjects", "Subjects"),
]
DEPARTMENT_SUMMARY_COLUMNS = [
    ("department", "Department"),
    ("students", "Students"),
    ("scores", "Scores"),
    ("average_score", "Average"),
    ("grade", "Grade"),
]
ALL_SCORE_COLUMNS = [
    ("student", "Student"),
    ("name", "Name"),
    ("course", "Course"),
    ("score", "Score"),
    ("grade", "Grade"),
    ("semester", "Semester"),
    ("year", "Year"),
]


class PerformanceView:
    def __init__(self) -> None:
        self.scores = ScoreController()
        self.courses = CourseController()
        self.performance = PerformanceController()

    def menu(self, recorded_by: int | None = None) -> None:
        while True:
            choice = menu_choice(
                "Scores and Performance",
                {
                    "1": "Input score",
                    "2": "View student performance",
                    "3": "View top students",
                    "4": "View department summary",
                    "5": "View all scores",
                    "0": "Back",
                },
            )
            if choice == "1":
                self.record_score(recorded_by)
            elif choice == "2":
                student_id = prompt_required("Student ID").upper()
                self.show_student_performance(student_id)
            elif choice == "3":
                self.show_top_students()
            elif choice == "4":
                self.show_department_summary()
            elif choice == "5":
                self.show_all_scores()
            elif choice == "0":
                return
            else:
                print("Invalid option.")
            pause()

    def record_score(self, recorded_by: int | None = None) -> None:
        try:
            courses = self.courses.list_courses()
            print_table(
                [
                    {
                        "id": course.id,
                        "code": course.code,
                        "name": course.name,
                        "department": course.department_name,
                    }
                    for course in courses
                ],
                COURSE_PICKER_COLUMNS,
            )
            course_id = prompt_int("Course ID", minimum=1)
            if course_id is None:
                raise ValueError("Course ID is required.")
            score = self.scores.save_score(
                prompt_required("Student ID").upper(),
                course_id,
                prompt_float("Score", minimum=0, maximum=100),
                prompt_optional("Semester", "Semester 1"),
                prompt_optional("Academic year", "2026"),
                recorded_by,
            )
            show_success(
                f"Saved {score.score} for {score.student_id} in "
                f"{score.course_code}. Grade: {score.grade}"
            )
        except Exception as exc:
            show_error(exc)

    def show_scores_for_student(self, student_id: str) -> None:
        rows = [
            {
                "course": score.course_code,
                "name": score.course_name,
                "score": score.score,
                "grade": score.grade,
                "semester": score.semester,
                "year": score.academic_year,
            }
            for score in self.scores.scores_for_student(student_id)
        ]
        print_table(rows, STUDENT_SCORE_COLUMNS)

    def show_student_performance(self, student_id: str) -> None:
        self.show_scores_for_student(student_id)
        summary = self.performance.student_performance(student_id)
        print()
        print(f"Average: {summary['average']}")
        print(f"Overall grade: {summary['grade']}")
        print(f"Subjects: {summary['subjects']}")

    def show_top_students(self) -> None:
        rows = self.performance.top_students()
        print_table(rows, TOP_STUDENT_COLUMNS)

    def show_department_summary(self) -> None:
        rows = self.performance.department_summary()
        print_table(rows, DEPARTMENT_SUMMARY_COLUMNS)

    def show_all_scores(self) -> None:
        rows = [
            {
                "student": score.student_id,
                "name": score.student_name,
                "course": score.course_code,
                "score": score.score,
                "grade": score.grade,
                "semester": score.semester,
                "year": score.academic_year,
            }
            for score in self.scores.list_scores()
        ]
        print_table(rows, ALL_SCORE_COLUMNS)

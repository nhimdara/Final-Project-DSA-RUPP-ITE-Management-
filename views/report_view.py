from __future__ import annotations

from controllers.report_controller import ReportController
from views.menu import menu_choice, pause, show_error, show_success, yes_no


class ReportView:
    def __init__(self) -> None:
        self.controller = ReportController()

    def menu(self, generated_by: int | None = None) -> None:
        while True:
            choice = menu_choice(
                "Reports",
                {
                    "1": "Student list report",
                    "2": "Score report",
                    "3": "Performance report",
                    "4": "Relationship graph report",
                    "0": "Back",
                },
            )
            if choice == "0":
                return
            try:
                if choice == "1":
                    report = self.controller.student_list_report()
                elif choice == "2":
                    report = self.controller.score_report()
                elif choice == "3":
                    report = self.controller.performance_report()
                elif choice == "4":
                    report = self.controller.relationship_graph_report()
                else:
                    print("Invalid option.")
                    pause()
                    continue
                print()
                print(report.as_text())
                if yes_no("Save report to reports/generated", default=True):
                    path = self.controller.save_report(report, generated_by)
                    show_success(f"Report saved: {path}")
            except Exception as exc:
                show_error(exc)
            pause()

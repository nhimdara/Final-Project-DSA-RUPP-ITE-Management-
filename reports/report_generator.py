from __future__ import annotations

from pathlib import Path

from models.report import Report


OUTPUT_DIR = Path(__file__).resolve().parent / "generated"


class ReportGenerator:
    def save_text_report(self, report: Report) -> Path:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        safe_title = "".join(char if char.isalnum() else "_" for char in report.title.lower()).strip("_")
        filename = f"{report.generated_at:%Y%m%d_%H%M%S}_{safe_title}.txt"
        path = OUTPUT_DIR / filename
        path.write_text(report.as_text(), encoding="utf-8")
        return path

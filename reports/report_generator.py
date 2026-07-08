from __future__ import annotations

from pathlib import Path

from models.report import Report


OUTPUT_DIR = Path(__file__).resolve().parent / "generated"


def _safe_filename(value: str) -> str:
    safe_value = "".join(char if char.isalnum() else "_" for char in value.lower()).strip("_")
    return safe_value or "report"


class ReportGenerator:
    def save_text_report(self, report: Report) -> Path:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{report.generated_at:%Y%m%d_%H%M%S}_{_safe_filename(report.title)}.txt"
        path = OUTPUT_DIR / filename
        path.write_text(report.as_text(), encoding="utf-8")
        return path

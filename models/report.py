from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Report:
    title: str
    report_type: str
    rows: Sequence[Mapping[str, Any]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)

    def as_text(self) -> str:
        lines = [
            self.title,
            f"Type: {self.report_type}",
            f"Generated: {self.generated_at:%Y-%m-%d %H:%M:%S}",
            "",
        ]
        if self.summary:
            lines.append("Summary")
            for key, value in self.summary.items():
                lines.append(f"- {key}: {value}")
            lines.append("")

        if self.rows:
            headers = list(self.rows[0].keys())
            widths = {
                header: max(len(str(header)), *(len(str(row.get(header, ""))) for row in self.rows))
                for header in headers
            }
            lines.append(" | ".join(header.ljust(widths[header]) for header in headers))
            lines.append("-+-".join("-" * widths[header] for header in headers))
            for row in self.rows:
                lines.append(" | ".join(str(row.get(header, "")).ljust(widths[header]) for header in headers))
        else:
            lines.append("No rows.")

        return "\n".join(lines)

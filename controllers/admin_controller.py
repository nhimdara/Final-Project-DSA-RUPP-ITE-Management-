from __future__ import annotations

from database.queries import fetch_one


class AdminController:
    def dashboard_stats(self) -> dict[str, int]:
        tables = {
            "students": "students",
            "teachers": "teachers",
            "courses": "courses",
            "departments": "departments",
            "users": "users",
            "scores": "scores",
        }
        stats: dict[str, int] = {}
        for key, table in tables.items():
            row = fetch_one(f"SELECT COUNT(*) AS count FROM {table}")
            stats[key] = int(row["count"]) if row is not None else 0
        return stats

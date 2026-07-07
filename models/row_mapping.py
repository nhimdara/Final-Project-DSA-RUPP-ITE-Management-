from __future__ import annotations

from typing import Any, Protocol


class RowMapping(Protocol):
    def keys(self) -> list[str]:
        ...

    def __getitem__(self, key: str) -> Any:
        ...


def row_to_dict(row: RowMapping) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}

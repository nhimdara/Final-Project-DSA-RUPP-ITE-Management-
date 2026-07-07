from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Optional


def title(text: str) -> None:
    print()
    print("=" * 72)
    print(text.upper())
    print("=" * 72)


def pause() -> None:
    input("\nPress Enter to continue...")


def prompt_required(label: str, default: Optional[str] = None) -> str:
    while True:
        suffix = f" [{default}]" if default not in (None, "") else ""
        value = input(f"{label}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        print("This field is required.")


def prompt_optional(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value if value else default


def prompt_int(
    label: str,
    default: Optional[int] = None,
    minimum: Optional[int] = None,
    maximum: Optional[int] = None,
) -> Optional[int]:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        value = input(f"{label}{suffix}: ").strip()
        if not value and default is not None:
            return default
        try:
            number = int(value)
        except ValueError:
            print("Please enter a valid number.")
            continue
        if minimum is not None and number < minimum:
            print(f"Minimum value is {minimum}.")
            continue
        if maximum is not None and number > maximum:
            print(f"Maximum value is {maximum}.")
            continue
        return number


def prompt_float(
    label: str,
    default: Optional[float] = None,
    minimum: Optional[float] = None,
    maximum: Optional[float] = None,
) -> float:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        value = input(f"{label}{suffix}: ").strip()
        if not value and default is not None:
            return default
        try:
            number = float(value)
        except ValueError:
            print("Please enter a valid number.")
            continue
        if minimum is not None and number < minimum:
            print(f"Minimum value is {minimum}.")
            continue
        if maximum is not None and number > maximum:
            print(f"Maximum value is {maximum}.")
            continue
        return number


def yes_no(label: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    value = input(f"{label} ({suffix}): ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes"}


def menu_choice(heading: str, options: dict[str, str]) -> str:
    title(heading)
    for key, label in options.items():
        print(f"{key}. {label}")
    return input("Choose option: ").strip()


def print_table(rows: Iterable[Mapping[str, Any]], columns: list[tuple[str, str]]) -> None:
    rows = list(rows)
    if not rows:
        print("No records found.")
        return

    widths: dict[str, int] = {}
    for key, header in columns:
        widths[key] = max(len(header), *(len(str(row.get(key, ""))) for row in rows))

    print(" | ".join(header.ljust(widths[key]) for key, header in columns))
    print("-+-".join("-" * widths[key] for key, _ in columns))
    for row in rows:
        print(" | ".join(str(row.get(key, "")).ljust(widths[key]) for key, _ in columns))


def show_error(exc: Exception) -> None:
    print(f"Error: {exc}")


def show_success(message: str) -> None:
    print(message)

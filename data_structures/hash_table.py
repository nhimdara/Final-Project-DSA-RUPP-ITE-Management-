from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import Generic, Optional, TypeVar


K = TypeVar("K")
V = TypeVar("V")


class HashTable(Generic[K, V]):
    """Small dictionary wrapper used by the diagram for fast student lookup."""

    def __init__(self) -> None:
        self._items: dict[K, V] = {}

    @classmethod
    def from_items(cls, items: Iterable[V], key: Callable[[V], K]) -> "HashTable[K, V]":
        table: HashTable[K, V] = cls()
        for item in items:
            table.insert(key(item), item)
        return table

    def insert(self, key: K, value: V) -> None:
        self._items[key] = value

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        return self._items.get(key, default)

    def search(self, key: K) -> Optional[V]:
        """Search for and return a value by its key."""
        return self._items.get(key)

    def update(self, key: K, value: V) -> bool:
        """Update an existing value. Return False when the key is missing."""
        if key not in self._items:
            return False
        self._items[key] = value
        return True

    def delete(self, key: K) -> bool:
        if key not in self._items:
            return False
        del self._items[key]
        return True

    def contains(self, key: K) -> bool:
        return key in self._items

    def values(self) -> list[V]:
        return list(self._items.values())

    def items(self) -> list[tuple[K, V]]:
        return list(self._items.items())

    def display(self) -> list[tuple[K, V]]:
        """Return all key-value pairs for display by the console program."""
        return self.items()

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[K]:
        return iter(self._items)

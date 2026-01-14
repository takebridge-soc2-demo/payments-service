from __future__ import annotations

from dataclasses import dataclass
from threading import Lock


@dataclass
class InMemoryIdempotencyStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._map: dict[str, str] = {}
        self._locks: dict[str, Lock] = {}
        self._locks_lock = Lock()

    def get(self, key: str) -> str | None:
        with self._lock:
            return self._map.get(key)

    def put(self, key: str, charge_id: str) -> None:
        with self._lock:
            self._map[key] = charge_id

    def lock_for(self, key: str) -> Lock:
        with self._locks_lock:
            lock = self._locks.get(key)
            if lock is None:
                lock = Lock()
                self._locks[key] = lock
            return lock

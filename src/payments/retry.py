from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


class TemporaryGatewayError(Exception):
    """Transient upstream payment gateway failure (retryable)."""


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    retry_on: tuple[type[Exception], ...] = (TemporaryGatewayError,)

    def run(self, fn: Callable[[], T]) -> T:
        attempt = 0
        while True:
            attempt += 1
            try:
                return fn()
            except self.retry_on:
                if attempt >= self.max_attempts:
                    raise

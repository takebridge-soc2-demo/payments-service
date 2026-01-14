from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import sleep as _sleep
from typing import TypeVar

T = TypeVar("T")


class TemporaryGatewayError(Exception):
    """Transient upstream payment gateway failure (retryable)."""


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_s: float = 0.2
    backoff_factor: float = 2.0
    retry_on: tuple[type[Exception], ...] = (TemporaryGatewayError,)

    def run(self, fn: Callable[[], T], sleep: Callable[[float], None] = _sleep) -> T:
        """Execute with retries; inject sleep to keep tests fast and deterministic."""
        attempt = 0
        delay = self.base_delay_s

        while True:
            attempt += 1
            try:
                return fn()
            except self.retry_on:
                if attempt >= self.max_attempts:
                    raise
                # Keep this realistic, but tests can inject a no-op sleep.
                sleep(delay)
                delay *= self.backoff_factor

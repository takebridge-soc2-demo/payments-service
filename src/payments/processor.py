from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .retry import RetryPolicy, TemporaryGatewayError


@dataclass(frozen=True)
class ChargeRequest:
    amount_cents: int
    currency: str
    customer_id: str


class PaymentGateway(Protocol):
    def charge(self, req: ChargeRequest) -> str:
        ...


class FakeGateway:
    """Demo gateway with deterministic charge ids."""
    def __init__(self) -> None:
        self._counter = 1000

    def charge(self, req: ChargeRequest) -> str:
        self._counter += 1
        return f"ch_{self._counter}"


class FlakyGateway:
    """Fails N times then succeeds; useful for tests."""
    def __init__(self, fail_times: int) -> None:
        self._remaining = fail_times
        self._counter = 2000

    def charge(self, req: ChargeRequest) -> str:
        if self._remaining > 0:
            self._remaining -= 1
            raise TemporaryGatewayError("upstream timeout")
        self._counter += 1
        return f"ch_{self._counter}"


class PaymentProcessor:
    def __init__(self, gateway: PaymentGateway, retry: RetryPolicy | None = None) -> None:
        self._gateway = gateway
        self._retry = retry or RetryPolicy()

    def charge(self, req: ChargeRequest) -> str:
        return self._retry.run(lambda: self._gateway.charge(req))

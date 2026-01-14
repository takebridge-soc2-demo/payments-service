from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .idempotency import InMemoryIdempotencyStore
from .retry import RetryPolicy, TemporaryGatewayError


@dataclass(frozen=True)
class ChargeRequest:
    amount_cents: int
    currency: str
    customer_id: str
    idempotency_key: str


class PaymentGateway(Protocol):
    def charge(self, req: ChargeRequest) -> str:
        ...


class FakeGateway:
    def __init__(self) -> None:
        self._counter = 1000

    def charge(self, req: ChargeRequest) -> str:
        self._counter += 1
        return f"ch_{self._counter}"


class FlakyGateway:
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
    def __init__(
        self,
        gateway: PaymentGateway,
        retry: RetryPolicy | None = None,
        idempotency: InMemoryIdempotencyStore | None = None,
    ) -> None:
        self._gateway = gateway
        self._retry = retry or RetryPolicy()
        self._idem = idempotency or InMemoryIdempotencyStore()

    def charge(self, req: ChargeRequest) -> str:
        lock = self._idem.lock_for(req.idempotency_key)
        with lock:
            existing = self._idem.get(req.idempotency_key)
            if existing:
                return existing

            charge_id = self._retry.run(lambda: self._gateway.charge(req))
            self._idem.put(req.idempotency_key, charge_id)
            return charge_id

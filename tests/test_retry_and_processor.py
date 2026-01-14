import pytest
from fastapi.testclient import TestClient

from app import app
from payments.processor import ChargeRequest, FlakyGateway, PaymentProcessor
from payments.retry import RetryPolicy, TemporaryGatewayError


def test_fails_after_max_attempts() -> None:
    gateway = FlakyGateway(fail_times=10)
    p = PaymentProcessor(gateway=gateway, retry=RetryPolicy(max_attempts=3))
    with pytest.raises(TemporaryGatewayError):
        p.charge(
            ChargeRequest(
                amount_cents=100,
                currency="USD",
                customer_id="cust_1",
                idempotency_key="k1",
            )
        )


def test_idempotency_returns_same_charge_id() -> None:
    gateway = FlakyGateway(fail_times=0)
    p = PaymentProcessor(gateway=gateway)

    r1 = p.charge(ChargeRequest(100, "USD", "cust_1", "idem_123"))
    r2 = p.charge(ChargeRequest(100, "USD", "cust_1", "idem_123"))
    assert r1 == r2


def test_api_requires_idempotency_header() -> None:
    client = TestClient(app)
    r = client.post(
        "/charge",
        json={"amount_cents": 100, "currency": "USD", "customer_id": "cust_1"},
    )
    assert r.status_code == 400

    r2 = client.post(
        "/charge",
        headers={"Idempotency-Key": "idem_abc"},
        json={"amount_cents": 100, "currency": "USD", "customer_id": "cust_1"},
    )
    assert r2.status_code == 200
    assert r2.json()["charge_id"].startswith("ch_")

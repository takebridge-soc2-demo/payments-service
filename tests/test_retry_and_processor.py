import pytest

from payments.processor import ChargeRequest, FlakyGateway, PaymentProcessor
from payments.retry import TemporaryGatewayError


def test_retries_then_succeeds() -> None:
    gateway = FlakyGateway(fail_times=2)
    p = PaymentProcessor(gateway=gateway)
    charge_id = p.charge(ChargeRequest(amount_cents=100, currency="USD", customer_id="cust_1"))
    assert charge_id.startswith("ch_")


def test_fails_after_max_attempts() -> None:
    gateway = FlakyGateway(fail_times=10)
    p = PaymentProcessor(gateway=gateway)
    with pytest.raises(TemporaryGatewayError):
        p.charge(ChargeRequest(amount_cents=100, currency="USD", customer_id="cust_1"))

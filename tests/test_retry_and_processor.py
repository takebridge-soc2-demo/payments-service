import pytest

from payments.processor import ChargeRequest, FlakyGateway, PaymentProcessor
from payments.retry import RetryPolicy, TemporaryGatewayError


def test_retries_then_succeeds_without_sleeping() -> None:
    gateway = FlakyGateway(fail_times=2)
    policy = RetryPolicy(max_attempts=3, base_delay_s=0.01, backoff_factor=2.0)
    charge_id = policy.run(
        lambda: gateway.charge(
            ChargeRequest(amount_cents=100, currency="USD", customer_id="cust_1")
        ),
        sleep=lambda _: None,
    )
    assert charge_id.startswith("ch_")


def test_fails_after_max_attempts() -> None:
    gateway = FlakyGateway(fail_times=10)
    p = PaymentProcessor(gateway=gateway, retry=RetryPolicy(max_attempts=3))
    with pytest.raises(TemporaryGatewayError):
        p.charge(ChargeRequest(amount_cents=100, currency="USD", customer_id="cust_1"))

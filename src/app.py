from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from payments.processor import ChargeRequest, FakeGateway, PaymentProcessor

app = FastAPI(title="payments-service", version="0.1.0")

processor = PaymentProcessor(gateway=FakeGateway())


class ChargeIn(BaseModel):
    amount_cents: int
    currency: str
    customer_id: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/charge")
def charge(body: ChargeIn) -> dict:
    charge_id = processor.charge(
        ChargeRequest(
            amount_cents=body.amount_cents,
            currency=body.currency,
            customer_id=body.customer_id,
        )
    )
    return {"charge_id": charge_id}

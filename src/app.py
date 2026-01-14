from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from payments.processor import ChargeRequest, FakeGateway, PaymentProcessor

app = FastAPI(title="payments-service", version="0.2.0")
processor = PaymentProcessor(gateway=FakeGateway())


class ChargeIn(BaseModel):
    amount_cents: int
    currency: str
    customer_id: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/charge")
def charge(body: ChargeIn, idempotency_key: str | None = Header(default=None)) -> dict:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key header")

    charge_id = processor.charge(
        ChargeRequest(
            amount_cents=body.amount_cents,
            currency=body.currency,
            customer_id=body.customer_id,
            idempotency_key=idempotency_key,
        )
    )
    return {"charge_id": charge_id}

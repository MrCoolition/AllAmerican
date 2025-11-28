from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .db import SessionLocal
from .models import Order


router = APIRouter(tags=["orders"])


class OrderEmailPayload(BaseModel):
    phone: str = Field(..., description="Phone number of the caller")
    item_details: str = Field(..., description="Clean inventory list provided by the caller")
    estimate_price: float = Field(..., description="Estimate price calculated for the move")
    move_date: str = Field(..., description="Move date as provided by the caller")
    locations: str = Field(..., description="Origin and destination details")
    estimate_calculation_table: str = Field(
        ..., description="Full itemized inventory and fee breakdown used for the estimate"
    )
    name: str = Field(..., description="Caller first and last name")
    stairwells: str = Field(..., description="Stairwell/elevator details and floors at each location")
    email: str = Field(..., description="Caller email address")


@router.post("/orders/email")
def record_order_email(payload: OrderEmailPayload) -> dict:
    """Record an order request and return a generated reference."""
    ext_ref = f"ORD-{uuid4().hex[:8].upper()}"

    summary_lines = [
        f"Name: {payload.name}",
        f"Phone: {payload.phone}",
        f"Email: {payload.email}",
        f"Move date: {payload.move_date}",
        f"Locations: {payload.locations}",
        f"Stairwells: {payload.stairwells}",
        f"Items: {payload.item_details}",
        f"Estimate price: {payload.estimate_price}",
        f"Estimate calculation table: {payload.estimate_calculation_table}",
    ]
    notes = "\n".join(summary_lines)

    with SessionLocal() as db:
        order = Order(
            ext_ref=ext_ref,
            customer_name=payload.name,
            status="new lead",
            eta=payload.move_date,
            notes=notes,
        )
        db.add(order)
        db.commit()

    return {"status": "received", "order_ref": ext_ref}

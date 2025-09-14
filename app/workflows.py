from .db import SessionLocal
from .models import Appointment, Order
from .quotes import compute_quote, MoveSpec


def create_appointment(**kwargs) -> int:
    with SessionLocal() as db:
        appt = Appointment(**kwargs)
        db.add(appt)
        db.commit()
        db.refresh(appt)
        return appt.id

def get_order_status(ref: str | None, name: str | None, phone: str | None) -> str:
    with SessionLocal() as db:
        q = db.query(Order)
        if ref:
            q = q.filter(Order.ext_ref == ref)
        elif phone:
            q = q.filter(Order.notes.contains(phone))
        elif name:
            q = q.filter(Order.customer_name.ilike(f"%{name}%"))
        row = q.first()
        if not row:
            return "I couldn't locate that order yet. Could you repeat the reference or name on the order?"
        msg = f"Order {row.ext_ref or row.id} for {row.customer_name} is '{row.status}'. ETA {row.eta or 'TBD'}."
        return msg

def estimate_from_strings(miles: float, rooms: int, stairs: bool, piano: bool, weekend: bool) -> dict:
    spec = MoveSpec(miles=miles, rooms=rooms, stairs=stairs, piano=piano, weekend=weekend)
    return compute_quote(spec)

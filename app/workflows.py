from .db import SessionLocal
from .models import Appointment, Order
from .quotes import compute_quote, MoveSpec, BoxOrder
from .furniture_catalog import LocationProfile


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

def _approx_weight_from_rooms(rooms: int) -> float:
    # Conservative default: ~1,500 lbs per room.
    return max(rooms, 1) * 1500.0

def estimate_from_strings(miles: float, rooms: int, stairs: bool, piano: bool, weekend: bool) -> dict:
    weight_estimate = _approx_weight_from_rooms(rooms)
    profile = LocationProfile.HEAVY_STAIRS if stairs else LocationProfile.MULTI_FLOOR
    is_intrastate = miles > 30

    origin_to_dest_minutes = max(20.0, miles * 1.5)

    box_order = BoxOrder()
    if piano:
        # Use packing labor for a TV box rental as a placeholder for piano handling time.
        box_order.rental["Flat Sceen TV"] = 1
        box_order.packing_services["Flat Sceen TV"] = 1

    spec = MoveSpec(
        total_weight_lbs=weight_estimate,
        location_profile=profile,
        friday_or_saturday=weekend,
        is_intrastate=is_intrastate,
        origin_to_destination_minutes=origin_to_dest_minutes,
    )
    return compute_quote(spec)

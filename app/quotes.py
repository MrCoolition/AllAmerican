from dataclasses import dataclass
from .db import SessionLocal
from .models import PricingRules

@dataclass
class MoveSpec:
    miles: float
    rooms: int
    stairs: bool = False
    piano: bool = False
    weekend: bool = False

def compute_quote(spec: MoveSpec) -> dict:
    with SessionLocal() as db:
        rules = db.query(PricingRules).first()
        if not rules:
            rules = PricingRules()
            db.add(rules)
            db.commit()
            db.refresh(rules)

    total = rules.base_fee + spec.miles * rules.per_mile + spec.rooms * rules.per_room
    if spec.stairs:
        total += rules.stairs_fee
    if spec.piano:
        total += rules.piano_fee
    if spec.weekend:
        total *= rules.weekend_multiplier

    return {
        "subtotal": round(total, 2),
        "currency": "USD",
        "line_items": {
            "base_fee": rules.base_fee,
            "mileage": spec.miles * rules.per_mile,
            "rooms": spec.rooms * rules.per_room,
            "stairs": rules.stairs_fee if spec.stairs else 0,
            "piano": rules.piano_fee if spec.piano else 0,
            "weekend_multiplier": rules.weekend_multiplier if spec.weekend else 1.0,
        },
    }

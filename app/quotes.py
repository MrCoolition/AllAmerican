from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Dict

from .furniture_catalog import (
    LocationProfile,
    estimate_hours,
    hourly_rate_lbs,
    movers_needed,
    trucks_needed,
)


LOCAL_MOVER_RATE_WEEKDAY = 50.0
LOCAL_MOVER_RATE_WEEKEND = 55.0
LOCAL_TRUCK_RATE_WEEKDAY = 50.0
LOCAL_TRUCK_RATE_WEEKEND = 55.0

INTRASTATE_MOVER_RATE_WEEKDAY = 55.0
INTRASTATE_MOVER_RATE_WEEKEND = 60.0
INTRASTATE_TRUCK_RATE_WEEKDAY = 55.0
INTRASTATE_TRUCK_RATE_WEEKEND = 60.0

PROTECTIVE_PER_1000_LBS = 5.0
SALES_TAX = 0.075

PURCHASE_BOX_RATES: Dict[str, tuple[float, float]] = {
    "Dishpak": (7.75, 16.67),
    "1.5": (2.25, 8.33),
    "30": (3.50, 8.33),
    "4.5": (5.00, 8.33),
    "6": (6.75, 8.33),
    "Mirror": (17.99, 12.50),
    "Flat Sceen TV": (80.00, 25.00),
    "Wardrobe": (22.00, 6.25),
    "Twin mattress bag": (11.99, 8.33),
    "King/Queen/double mattress bag": (16.99, 12.00),
}

RENTAL_BOX_RATES: Dict[str, tuple[float, float]] = {
    "Flat Sceen TV": (50.00, 25.00),
    "Wardrobe": (7.00, 6.25),
}


@dataclass
class BoxOrder:
    purchase: Dict[str, int] = field(default_factory=dict)
    rental: Dict[str, int] = field(default_factory=dict)
    packing_services: Dict[str, int] = field(default_factory=dict)


@dataclass
class MoveSpec:
    total_weight_lbs: float
    location_profile: str = LocationProfile.MULTI_FLOOR
    friday_or_saturday: bool = False
    is_intrastate: bool = False
    origin_to_destination_minutes: float = 20.0
    warehouse_to_origin_minutes: float = 30.0
    destination_to_warehouse_minutes: float = 30.0
    disassembled_beds: int = 0
    sleep_number_beds: int = 0
    desks_to_disassemble: int = 0
    box_order: BoxOrder = field(default_factory=BoxOrder)
    mover_override: int | None = None


def _round_up_quarter(hour_value: float) -> float:
    return math.ceil(hour_value * 4) / 4.0


def _protective_materials_cost(weight_lbs: float) -> float:
    units = math.ceil(max(weight_lbs, 0.0) / 1000.0)
    return units * PROTECTIVE_PER_1000_LBS


def _extra_task_hours(spec: MoveSpec, movers: int) -> float:
    tasks = spec.disassembled_beds + spec.sleep_number_beds + spec.desks_to_disassemble
    if movers <= 0:
        return 0.0
    # Each task is 30 minutes of one-mover time.
    return (0.5 * tasks) / movers


def _box_costs(order: BoxOrder) -> dict:
    purchase_box_total = 0.0
    purchase_labor_total = 0.0
    for name, count in order.purchase.items():
        rate, labor = PURCHASE_BOX_RATES.get(name, (0.0, 0.0))
        purchase_box_total += rate * count
        pack_count = order.packing_services.get(name, 0)
        purchase_labor_total += labor * pack_count

    rental_box_total = 0.0
    rental_labor_total = 0.0
    for name, count in order.rental.items():
        rate, labor = RENTAL_BOX_RATES.get(name, (0.0, 0.0))
        rental_box_total += rate * count
        pack_count = order.packing_services.get(name, 0)
        rental_labor_total += labor * pack_count

    taxable_total = purchase_box_total + purchase_labor_total
    tax = taxable_total * SALES_TAX

    return {
        "purchase_boxes": round(purchase_box_total, 2),
        "purchase_packing_labor": round(purchase_labor_total, 2),
        "rental_boxes": round(rental_box_total, 2),
        "rental_packing_labor": round(rental_labor_total, 2),
        "sales_tax": round(tax, 2),
        "total": round(
            purchase_box_total
            + purchase_labor_total
            + rental_box_total
            + rental_labor_total
            + tax,
            2,
        ),
    }


def _hourly_rates(spec: MoveSpec) -> tuple[float, float]:
    if spec.is_intrastate:
        if spec.friday_or_saturday:
            return INTRASTATE_MOVER_RATE_WEEKEND, INTRASTATE_TRUCK_RATE_WEEKEND
        return INTRASTATE_MOVER_RATE_WEEKDAY, INTRASTATE_TRUCK_RATE_WEEKDAY

    if spec.friday_or_saturday:
        return LOCAL_MOVER_RATE_WEEKEND, LOCAL_TRUCK_RATE_WEEKEND
    return LOCAL_MOVER_RATE_WEEKDAY, LOCAL_TRUCK_RATE_WEEKDAY


def _travel_hours(spec: MoveSpec, is_local: bool) -> float:
    if is_local:
        # Rule 5 and Rule 7 (local): 1 hour travel + 20 minutes between sites.
        return 1.0 + (20.0 / 60.0)

    # Intrastate: actual drive times with minimums and quarter-hour rounding.
    to_origin = max(0.5, spec.warehouse_to_origin_minutes / 60.0)
    to_origin = _round_up_quarter(to_origin)

    to_warehouse = max(0.5, spec.destination_to_warehouse_minutes / 60.0)
    to_warehouse = _round_up_quarter(to_warehouse)

    origin_to_dest = _round_up_quarter(spec.origin_to_destination_minutes / 60.0)

    return to_origin + to_warehouse + origin_to_dest


def compute_quote(spec: MoveSpec) -> dict:
    movers = spec.mover_override if spec.mover_override is not None else movers_needed(spec.total_weight_lbs)
    trucks = trucks_needed(spec.total_weight_lbs)
    movement_rate = hourly_rate_lbs(spec.location_profile)

    onsite_hours = estimate_hours(spec.total_weight_lbs, spec.location_profile, movers)
    onsite_hours += _extra_task_hours(spec, movers)

    travel_hours = _travel_hours(spec, is_local=not spec.is_intrastate)
    total_hours = onsite_hours + travel_hours

    if not spec.is_intrastate:
        total_hours = max(total_hours, 3.0)  # Rule 6 local minimum

    mover_rate, truck_rate = _hourly_rates(spec)

    mover_cost = mover_rate * movers * total_hours
    truck_cost = truck_rate * trucks * total_hours

    box_costs = _box_costs(spec.box_order)
    protective_cost = _protective_materials_cost(spec.total_weight_lbs)

    subtotal = mover_cost + truck_cost + box_costs["total"] + protective_cost

    return {
        "weight_lbs": spec.total_weight_lbs,
        "movement_rate_lbs_per_mover_hour": movement_rate,
        "movers": movers,
        "trucks": trucks,
        "onsite_hours": round(onsite_hours, 2),
        "travel_hours": round(travel_hours, 2),
        "total_hours": round(total_hours, 2),
        "hourly_rates": {
            "mover_rate": mover_rate,
            "truck_rate": truck_rate,
        },
        "costs": {
            "mover_cost": round(mover_cost, 2),
            "truck_cost": round(truck_cost, 2),
            "boxes_and_packing": box_costs,
            "protective_materials": round(protective_cost, 2),
        },
        "subtotal": round(subtotal, 2),
        "notes": {
            "local_minimum_hours": 3.0 if not spec.is_intrastate else None,
            "quarter_hour_rounding": spec.is_intrastate,
        },
    }

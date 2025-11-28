# Move estimate mechanics

This document spells out everything that powers the price estimate so the moving company owner has a complete picture of the logic, data sources, and outputs.

## What runs the calculation
- **Entry point:** `compute_quote` in `app/quotes.py` consumes a `MoveSpec` dataclass (miles, rooms, stairs, piano, weekend).
- **Persistent pricing settings:** The first row in the `pricing_rules` table (`app.models.PricingRules`) supplies the dollar amounts and multipliers. If the table is empty, `compute_quote` writes a new row with the defaults below before any math runs.
- **Database session management:** `SessionLocal` in `app/db.py` opens the database connection used to read or seed `pricing_rules`.
- **Inventory rules:** For inventory-driven estimates, `app/furniture_catalog.py` loads the TSV catalog embedded in that file, applies fuzzy matching to user-entered item names, and runs Rules 1–4 to suggest movers, trucks, and hours.

## Inputs captured
- `miles` (float): one-way distance between origin and destination.
- `rooms` (int): count of rooms being moved.
- `stairs` (bool): whether stairs are involved at either location.
- `piano` (bool): whether a piano or similar special item is included.
- `weekend` (bool): whether the move occurs on a weekend.

Inventory requests use `order: dict[str, int]` keyed by furniture names and an optional `profile` string (`multi-floor`, `second-floor apartment`, `first-floor home`, `storage`, or `dock job`).

## Default pricing rule values
Inserted automatically when the database has no `pricing_rules` rows:
- `base_fee`: $129.00
- `per_mile`: $2.50 per mile
- `per_room`: $85.00 per room
- `stairs_fee`: $75.00 flat when `stairs=True`
- `piano_fee`: $200.00 flat when `piano=True`
- `weekend_multiplier`: 1.15 applied to the subtotal when `weekend=True`

## Calculation sequence
1. Start with `total = base_fee + miles * per_mile + rooms * per_room`.
2. If `stairs` is true, add `stairs_fee` to `total`.
3. If `piano` is true, add `piano_fee` to `total`.
4. If `weekend` is true, multiply `total` by `weekend_multiplier`.
5. Return a JSON-serializable dict containing:
   - `subtotal`: `total` rounded to two decimals.
   - `currency`: always `"USD"`.
   - `line_items`: a breakdown of each component, including zero values when a flag is false and `1.0` multiplier when `weekend` is false.

## Inventory-driven estimator
The catalog-based estimator adds detail beyond the simple room count:
- Fuzzy-matches each requested item to the TSV catalog and returns match scores plus any handling/surcharge notes.
- Computes total matched weight.
- Applies movement rules from `app/furniture_catalog.py`:
  - Rule 1: base mover productivity is 310 lbs/hour with adjustments for stairs, apartments, first-floor-only jobs, storage units, and dock work.
  - Rule 2: one truck fits up to 8,000 lbs of furniture.
  - Rule 3: jobs up to 4,000 lbs require two movers.
  - Rule 4: add one mover for every additional 2,500 lbs.
- Summarizes movers, trucks, and estimated labor hours using the profile-specific productivity rate.

## Touchpoints inside the product
- `workflows.estimate_from_strings` wraps raw user inputs into `MoveSpec` and calls `compute_quote`, making it easy for voice/websocket flows to request a price quote.
- Other parts of the app can construct a `MoveSpec` directly and pass it to `compute_quote` for the same calculation path.
- Team members can override pricing by editing the single `pricing_rules` row in the database; subsequent calls reuse the stored values automatically.

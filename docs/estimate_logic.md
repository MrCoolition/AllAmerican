# Move estimate mechanics

This repository computes move estimates through `compute_quote` in `app/quotes.py`, which is driven by structured move details (`MoveSpec`).

## Inputs captured
- `miles` (float): one-way distance between origin and destination.
- `rooms` (int): count of rooms being moved.
- `stairs` (bool): whether stairs are involved at either location.
- `piano` (bool): whether a piano or similar special item is included.
- `weekend` (bool): whether the move occurs on a weekend.

## Pricing rule source
`compute_quote` opens a database session (`SessionLocal`) and loads the first `PricingRules` row. If none exists, it inserts a row with defaults:
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

## Where it is called
- `workflows.estimate_from_strings` wraps raw user inputs into `MoveSpec` and calls `compute_quote`, making it easy for voice/WS flows to request a price quote.
- Other parts of the app can construct a `MoveSpec` directly and pass it to `compute_quote` for the same calculation path.

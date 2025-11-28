from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable
import difflib
import math
import re


@dataclass(frozen=True)
class CatalogItem:
    name: str
    volume: float
    weight: float
    handling: str | None
    surcharge: str | None


CATALOG_TSV = """Name\tVolume\tWeight\tHandling\tSurcharge
2 Wheel Dollies\t1\t7\t\t
Air Compressor\t10\t70\t\t
Air Cond Window\t5\t35\t\t
Air Purifier\t5\t35\t\t
Aquarium 10.0\t10\t70\t\t
Aquarium 20.0\t20\t140\t\t
Arcade Game\t50\t350\t\t
1-Door Armoire\t20\t90\tdisassembly/reassembly\t
2-Door Armoire\t40\t180\tdisassembly/reassembly\t
3-Door Armoire\t70\t300\tdisassembly/reassembly\t
Artificial Plant - Large\t10\t70\t\t
Artificial Plant - Small\t5\t35\t\t
ATV\t125\t875\t\t
Baby/Dog Gates\t2\t14\t\t
Baker's Rack - Large\t20\t140\t\t
Baker's Rack - Medium\t15\t105\t\t
Baker's Rack - Small\t10\t70\t\t
Bar - Portable\t20\t140\t\t
Bar Stool\t3\t21\t\t
Basketball Hoop/Pole\t50\t350\tdisassembly/reassembly\t
Bassinet\t5\t35\t\t
BBQ Grill - Large\t15\t105\t\t
BBQ Grill - Small\t5\t35\t\t
Bean Bag\t5\t35\t\t
Bean Bag - Large\t15\t105\t\t
Bed - Bassinette\t15\t105\t\t
Bed - Bunk (Set of 2)\t55\t385\tdisassembly/reassembly\t
Bed - Daybed\t30\t210\tdisassembly/reassembly\t
Bed - Footboard\t10\t70\t\t
Bed - Headboard\t15\t105\t\t
Bed - Roll-A-Way\t15\t105\t\t
Bed - Trundle Bed\t10\t70\tdisassembly/reassembly\t
Bed - Twin\t30\t210\t\t
Bed - Waterbed Base\t10\t70\tdisassembly/reassembly\t
Bed Double/Full - Box Spring\t15\t105\t\t
Bed Double/Full - Frame\t10\t70\t\t
Bed Double/Full - Mattress\t20\t140\t\t
Bed Double/Full - Platform\t15\t105\t\t
Bed Double/Full- Sleep Number\t35\t245\t\t
Bed Full - Footboard\t10\t70\t\t
Bed Full - Headboard\t10\t70\t\t
Bed King - Box Spring\t25\t175\t\t
Bed King - Box Spring 1/2\t15\t105\t\t
Bed King - Footboard\t10\t70\t\t
Bed King - Frame\t20\t140\t\t
Bed King - Headboard\t15\t105\t\t
Bed King - Mattress\t35\t245\t\t
Bed King - Platform\t25\t175\t\t
Bed King - Sleep Number\t60\t420\t\t
Bed King - Split Adjustable Base\t50\t350\t\t
Bed Queen - Adjustable Base\t25\t175\tdisassembly/reassembly\t
Bed Queen - Box Spring\t20\t140\t\t
Bed Queen - Footboard\t10\t70\t\t
Bed Queen - Frame\t15\t105\t\t
Bed Queen - Metal Frame\t10\t70\t\t
Bed Queen - Headboard\t15\t105\t\t
Bed Queen - Mattress\t25\t175\t\t
Bed Queen - Platform\t20\t140\t\t
Bed Queen - Sleep Number\t45\t315\t\t
Bed Twin/Single - Box Spring\t10\t70\t\t
Bed Twin/Single - Frame\t10\t70\t\t
Bed Twin/Single - Mattress\t15\t105\t\t
Bed Twin/Single - Platform\t10\t70\t\t
Bed King - Storage\t80\t300\tdisassembly/reassembly\t
Bed Queen - Storage\t70\t250\tdisassembly/reassembly\t
Bed Single - Storage\t50\t200\tdisassembly/reassembly\t
Bed King - Canopy\t100\t400\tdisassembly/reassembly\t
Bed Queen - Canopy\t70\t350\tdisassembly/reassembly\t
Bed Single - Canopy\t60\t250\tdisassembly/reassembly\t
Bed King - Murphy (Wall Bed)\t70\t250\tdisassembly/reassembly\t
Bed Queen - Murphy (Wall Bed)\t60\t200\tdisassembly/reassembly\t
Bed Single - Murphy (Wall Bed)\t50\t150\tdisassembly/reassembly\t
Bench - Large\t15\t105\t\t
Bench - Piano\t3\t21\t\t
Bench - Small\t5\t35\t\t
Bicycle - Adult\t10\t70\t\t
Bicycle - Child\t5\t35\t\t
Bicycle - Exercise\t10\t70\t\t
Bike Rack\t5\t35\t\t
Bird Cage\t5\t35\t\t
Birdbath\t5\t35\t\t
Boat\t35\t245\t\t
Boat >14'\t350\t2450\t\t
Boat Trailer\t100\t700\t\t
Bookcase - Large\t20\t140\tdisassembly/reassembly\t
Bookcase - Medium\t10\t70\t\t
Bookcase - Small\t5\t35\t\t
Bookcase - Large Wall mounted\t20\t140\tdisassembly/reassembly\t
Bookcase - Medium Wall mounted\t10\t70\tdisassembly/reassembly\t
Bookcase - Small Wall mounted\t5\t35\tdisassembly/reassembly\t
Bucket\t2\t14\t\t
Buffet - Base\t30\t210\t\t
Buffet - Top\t20\t140\t\t
Butcher Block\t5\t35\t\t
Bathtub\t80\t250\t\t
Cabinet - China\t25\t175\t\t
Cabinet - China (2 pc.)\t40\t280\t\t
Cabinet - Corner\t25\t175\t\t
Cabinet - Curio/Large\t25\t175\t\t
Cabinet - Curio/Small\t15\t105\t\t
Cabinet - Gun\t15\t105\t\t
Cabinet - Large\t35\t245\t\t
Cabinet - Medium\t20\t140\t\t
Cabinet - Metal\t20\t140\t\t
Cabinet - Small\t10\t70\t\t
Camper Trailer\t700\t4900\t\t
Camping Gear\t15\t105\t\t
Canoe  <14'\t20\t140\t\t
Canoe >14'\t30\t210\t\t
Carseat\t5\t35\t\t
Cart\t10\t70\t\t
Cartop Carrier\t25\t175\t\t
Cat Box\t3\t21\t\t
Cat Post\t4\t28\t\t
Cat Tree\t15\t105\t\t
CD/DVD Rack\t5\t35\t\t
Chair - Arm\t10\t70\t\t
Chair - Bar\t10\t70\t\t
Chair - Childs\t3\t21\t\t
Chair - Dining\t5\t35\t\t
Chair - Folding\t2\t14\t\t
Chair - Glider/Settee\t20\t140\t\t
Chair - High\t5\t35\t\t
Chair - Occasional\t15\t105\t\t
Chair - Office\t10\t70\t\t
Chair - OS/Reclining\t25\t175\t\t
Chair - Rocker\t10\t70\t\t
Chaise Lounge - Large\t25\t175\t\t
Chaise Lounge - Small\t15\t105\t\t
Changing Table\t15\t105\t\t
Chest\t10\t70\t\t
Chest - Cedar\t15\t105\t\t
Chest - Toy\t10\t70\t\t
Chest of Drawers\t15\t105\t\t
Child's Slide\t10\t70\t\t
Child's Swing\t30\t210\t\t
Chimenea\t10\t70\t\t
Chipper/Shreader\t15\t105\t\t
Christmas Tree\t8\t56\t\t
Clock - Grandfather\t25\t175\t\t
Clothes Dryer Rack\t5\t35\t\t
Clothes Hamper\t3\t21\t\t
Coat Rack\t5\t35\t\t
Cooler\t3\t21\t\t
Copier\t20\t140\t\t
Credenza\t30\t210\t\t
Crib\t15\t105\t\t
Conference table (Large)\t50\t150\tdisassembly/reassembly\t
Deck Box - Large\t25\t175\t\t
Deck Box - Small\t15\t105\t\t
Dehumidifier\t5\t35\t\t
Desk - Large\t30\t210\tdisassembly/reassembly\t
Desk - Medium\t20\t140\t\t
Desk - Roll top/2 pc.\t60\t420\t\t
Desk - Small\t10\t70\t\t
Desk - w. Return\t35\t245\tdisassembly/reassembly\t
Desk Chair\t6\t42\t\t
Dining - Hutch\t20\t140\t\t
Dining - Hutch (2 pc.)\t35\t245\tdisassembly/reassembly\t
Dining - Leaf\t2\t14\t\t
Dining Table - Large\t30\t210\tdisassembly/reassembly\t
Dining Table - Medium\t25\t175\t\t
Dining Table - Small\t20\t140\t\t
Dishwasher\t20\t140\t\t
Dog House/Kennel\t10\t70\tdisassembly/reassembly\t
Dollhouse\t10\t70\t\t
Drafting Table\t35\t245\t\t
Dresser - Double\t20\t140\t\t
Dresser - Mirror\t6\t42\t\t
Dresser - Single\t10\t70\t\t
Dresser - Triple\t30\t210\t\t
Dresser - Vanity\t20\t140\t\t
Dresser - Vanity Bench\t3\t21\t\t
Drill Press\t15\t105\t\t
Dropleaf Table\t10\t70\t\t
Dryer\t25\t175\t\t
Easel\t5\t35\t\t
Electronic Equipment\t2\t14\t\t
Eliptical\t25\t175\t\t
End Table\t5\t35\t\t
Entertainment Center - Large\t50\t350\tdisassembly/reassembly\t
Entertainment Center - Medium\t40\t280\t\t
Entertainment Center - Small\t30\t210\t\t
Exercise Equipment\t10\t70\t\t
Exercise Equipment - Bench\t20\t140\t\t
Exercise Equipment - Bike\t10\t70\t\t
Exercise Equipment - Eliptical Large\t30\t210\t\t
Exercise Equipment - Rowing Machine\t15\t105\t\t
Exercise Equipment - Squat Rack\t35\t245\t\t
Exercise Equipment - Treadmill\t30\t210\t\t
Exercise Machine\t30\t210\t\t
Exercise Mat\t10\t70\t\t
Fan\t3\t21\t\t
Fan - Large\t5\t35\t\t
File - Lat. 2-3 dr\t10\t70\t\t
File - Lat. 4-5 dr\t25\t175\t\t
File Cab - Vert. 2-3 dr\t10\t70\t\t
File Cab - Vert. 4-5 dr\t25\t175\t\t
File cabinet-Verticle\t20\t140\t\t
Fire Pit (Lg)\t15\t105\t\t
Fire Pit (Sm)\t10\t70\t\t
Fireplace Equipment\t5\t35\t\t
Folding Table\t5\t35\t\t
Freezer - Large\t60\t420\t\t
Freezer - Medium\t45\t315\t\t
Freezer - Small\t30\t210\t\t
Futon\t25\t175\t\t
Game Table\t15\t105\t\t
Garden Hose/Tool\t5\t35\t\t
Generator (Lg)\t15\t105\t\t
Generator (Sm)\t10\t70\t\t
Glass Tops\t5\t35\t\t
Glider\t20\t140\tdisassembly/reassembly\t
Golf Bag\t10\t70\t\t
Golf Cart\t70\t490\t\t
Guitar Case\t5\t35\t\t
Hammock w. Frame\t10\t70\t\t
Heater/Radiator\t5\t35\t\t
Home Gym\t40\t280\t\t
Home Gym Built\t80\t560\t\t
Hot Tub\t70\t490\tdisassembly/reassembly\t
Hutch\t20\t140\t\t
Ironing Board\t5\t35\t\t
Island - Kitchen\t10\t70\t\t
Jack/Auto Equipment\t10\t70\t\t
Jet Ski\t60\t420\t\t
Jewelry Chest\t5\t35\t\t
Juke Box\t50\t350\t\t
Kayak\t15\t105\t\t
Kayak 14' & Under\t10\t70\t\t
Keyboard\t10\t70\t\t
Ladder\t5\t35\t\t
Ladder (Lg)\t10\t70\t\t
Ladder - Extension\t15\t105\t\t
Ladder - Step\t3\t21\t\t
Lamp - Floor\t5\t21\t\t
Lamp - Table\t3\t15\t\t
Lawn Mower\t10\t70\t\t
Lawn Mower - Push\t5\t35\t\t
Lawn Mower - Riding\t50\t350\t\t
Leaf Blower\t5\t35\t\t
Locker - Large\t20\t140\tdisassembly/reassembly\t
Locker - Small\t10\t70\t\t
Magazine Rack\t2\t14\t\t
Mannequins\t10\t70\t\t
Metal Screen\t3\t21\t\t
Microwave Stand\t10\t70\t\t
Mirror - Full Floor Style\t15\t105\t\t
Mirror/Picture\t3\t21\t\t
Mirror/Picture - Large\t10\t70\t\t
Miter Saw\t15\t105\t\t
Monitor\t2\t14\t\t
Motorbike\t20\t140\t\t
Nightstand - Large\t10\t70\t\t
Nightstand - Small\t5\t35\t\t
Organ\t25\t175\t\t
Ottoman - Large\t10\t70\t\t
Ottoman - Small\t3\t21\t\t
Pack and Play\t5\t35\t\t
Patio Chair - Large\t10\t70\t\t
Patio Chair - Small\t5\t35\t\t
Patio Sofa\t20\t140\t\t
Patio Table\t10\t70\t\t
Patio Table - Large\t25\t175\t\t
Pedestal\t10\t70\t\t
Piano - Baby Grand\t60\t420\t\t
Ping Pong Table\t25\t175\tdisassembly/reassembly\t
Plant Stand\t5\t35\t\t
Plants/Planter - Large\t10\t70\t\t
Plants/Planter - Small\t5\t35\t\t
Plastic Drawers\t3\t21\t\t
Plastic Tote - Large\t5\t35\t\t
Plastic Tote - Small\t3\t21\t\t
Pool Table - Composite\t25\t175\tdisassembly/reassembly\t
Pool Table - Slate\t60\t420\tdisassembly/reassembly\t
Porch - Swing\t10\t70\tdisassembly/reassembly\t
Power Tool\t5\t35\t\t
Power Tool - Large\t15\t105\t\t
Pressure Washer\t10\t70\t\t
Printer\t5\t35\t\t
Picnic table - attached benches (4-6)\t30\t150\tdisassembly/reassembly\t
Picnic table - attached benches (6-8)\t40\t250\tdisassembly/reassembly\t
Picnic table - attached benches (8-10)\t60\t350\tdisassembly/reassembly\t
Range/Stove\t25\t175\t\t
Refrigerator\t30\t210\t\t
Refrigerator - Large\t45\t315\t\t
Refrigerator - Small\t10\t70\t\t
Room Divider\t10\t70\t\t
Rototiller\t20\t140\t\t
Rug - Large\t15\t105\t\t
Rug - Medium\t5\t35\t\t
Rug - Small\t2\t14\t\t
Saddle\t5\t35\t\t
Safe - (Extra Lg)\t75\t525\t\t
Safe - (Lg)\t50\t350\t\t
Safe - (Md)\t25\t175\t\t
Safe - (Sm)\t10\t70\t\t
Sandbox\t10\t70\t\t
Saw Horse\t5\t35\t\t
Scooter\t3\t21\t\t
Sculpture\t5\t35\t\t
Sewing Machine\t5\t35\t\t
Sewing Machine Cabinet\t15\t105\t\t
Shelves\t10\t70\t\t
Shelves - Heavy Metal\t25\t175\t\t
Shelves - Metal\t5\t35\t\t
Shelving - Plastic\t5\t35\t\t
Shoe Rack\t5\t35\t\t
Skiis\t5\t35\t\t
Sled\t5\t35\t\t
Snowblower\t25\t175\t\t
Sofa - 3 Seater\t50\t350\t\t
Sofa - Futon\t30\t210\t\t
Sofa - Loveseat\t35\t245\t\t
Sofa - Power Reacliner\t60\t420\t\t
Sofa - Sec. Per Section\t35\t245\t\t
Sofa Table\t10\t70\t\t
Speaker - Large\t10\t70\t\t
Speaker - Small\t5\t35\t\t
Sporting Goods\t4\t28\t\t
Stand\t5\t35\t\t
Statue (Small)\t10\t35\t\t
Statue (Medium)\t40\t80\t\t
Statue (Large)\t80\t250\t\t
Stool - Bar\t3\t21\t\t
Stool - Foot\t3\t21\t\t
Storage Shed\t60\t420\tdisassembly/reassembly\t
Stroller\t5\t35\t\t
Suitcase\t5\t35\t\t
Surfboard\t6\t42\t\t
Shoe Rack - Small\t4\t10\t\t
Shoe Rack - Medium\t7\t20\t\t
Shoe Rack - Large\t12\t30\t\t
Table - Card\t5\t35\t\t
Table - Childs\t5\t35\t\t
Table - Coffee (Lg)\t20\t140\t\t
Table - Coffee (Md)\t10\t70\t\t
Table - Coffee (Sm)\t5\t35\t\t
Table - Extension Leaf\t7\t49\t\t
Table - Inversion\t15\t105\t\t
Table - Kitchen\t15\t105\t\t
Table Saw\t15\t105\tdisassembly/reassembly\t
Telescope\t10\t70\t\t
Tire\t3\t21\t\t
Toolbox\t5\t35\t\t
Toolchest - Large\t45\t315\t\t
Toolchest - Medium\t30\t210\t\t
Toolchest - Small\t15\t105\t\t
Toy - Large\t10\t70\t\t
Toy - Small\t5\t35\t\t
Trampoline - Large\t25\t175\tdisassembly/reassembly\t
Trampoline - Toy\t5\t35\t\t
Trash Can\t5\t35\t\t
Treadmill\t35\t245\t\t
Tricycle\t3\t21\t\t
Tripod\t10\t70\t\t
Trunk - Large\t20\t140\t\t
Trunk - Medium\t15\t105\t\t
Trunk - Small\t10\t70\t\t
TV - 51"-80"\t15\t105\t\t
TV - 81" & Over\t20\t140\t\t
TV - >50"\t5\t35\t\t
TV Stand - Large\t20\t140\t\t
TV Stand - Medium\t15\t105\t\t
TV Stand - Small\t10\t70\t\t
TV Tray Set\t5\t35\t\t
Umbrella - Base\t20\t140\t\t
Umbrella - Patio\t10\t70\t\t
Upright Piano - Large\t40\t280\t\t
Upright Piano - Small\t35\t245\t\t
Vacuum Cleaner\t3\t21\t\t
Wagon\t5\t35\t\t
Walker\t2\t14\t\t
Washing Machine\t25\t175\t\t
Waste Basket\t2\t14\t\t
Weight Bench\t10\t70\t\t
Weights\t0\t0\t\t
Wheelbarrow\t5\t35\t\t
Wheelchair\t5\t35\t\t
Whiteboard\t5\t35\t\t
Wine rack\t10\t70\t\t
Workbench - Large\t40\t280\t\t
Workbench - Small\t20\t140\t\t
Water Dispenser - Small\t3\t15\t\t
Water Dispenser - Medium\t5\t30\t\t
Water Dispenser - Large\t7\t40\t\t
Water Fountain (Small)\t20\t45\t\t
Water Fountain (Medium)\t80\t250\t\t
Yard Ornaments\t2\t14\t\t
"""


@lru_cache()
def _catalog() -> dict[str, CatalogItem]:
    items: dict[str, CatalogItem] = {}
    for raw_line in CATALOG_TSV.strip().splitlines()[1:]:
        columns = re.split(r"\t", raw_line)
        if len(columns) < 3:
            continue
        name = columns[0].strip()
        volume_raw = columns[1].strip() if len(columns) > 1 else "0"
        weight_raw = columns[2].strip() if len(columns) > 2 else "0"
        handling = columns[3].strip() if len(columns) > 3 and columns[3].strip() else None
        surcharge = columns[4].strip() if len(columns) > 4 and columns[4].strip() else None
        volume = float(volume_raw) if volume_raw else 0.0
        weight = float(re.sub(r"[^0-9.]", "", weight_raw) or 0)
        items[name.lower()] = CatalogItem(
            name=name,
            volume=volume,
            weight=weight,
            handling=handling,
            surcharge=surcharge,
        )
    return items


def catalog_items() -> Iterable[CatalogItem]:
    return _catalog().values()


def find_best_item(query: str) -> tuple[CatalogItem, float]:
    key = query.strip().lower()
    items = _catalog()
    if key in items:
        return items[key], 1.0
    candidates = difflib.get_close_matches(key, items.keys(), n=1, cutoff=0.0)
    if not candidates:
        raise KeyError(f"No catalog items found for '{query}'")
    match_key = candidates[0]
    score = difflib.SequenceMatcher(None, key, match_key).ratio()
    return items[match_key], score


def total_weight(order: dict[str, int]) -> tuple[float, list[dict]]:
    total = 0.0
    breakdown: list[dict] = []
    for name, qty in order.items():
        item, confidence = find_best_item(name)
        weight = item.weight * qty
        total += weight
        breakdown.append(
            {
                "requested": name,
                "matched_name": item.name,
                "quantity": qty,
                "weight_each": item.weight,
                "weight_total": weight,
                "confidence": round(confidence, 3),
                "handling": item.handling,
                "surcharge": item.surcharge,
            }
        )
    return total, breakdown


def movers_needed(weight_lbs: float) -> int:
    if weight_lbs <= 0:
        return 0
    if weight_lbs <= 4000:
        return 2
    return 2 + math.ceil((weight_lbs - 4000) / 2500)


def trucks_needed(weight_lbs: float) -> int:
    if weight_lbs <= 0:
        return 0
    return max(1, math.ceil(weight_lbs / 8000))


class LocationProfile:
    MULTI_FLOOR = "multi_floor"
    HEAVY_STAIRS = "heavy_stairs"
    SECOND_FLOOR_APT = "second_floor_apt"
    FIRST_FLOOR_HOME = "first_floor_home"
    GROUND_STORAGE = "ground_storage"
    DOCK_JOB = "dock_job"


PROFILE_RATE = {
    LocationProfile.MULTI_FLOOR: 310.0,
    LocationProfile.HEAVY_STAIRS: 295.0,
    LocationProfile.SECOND_FLOOR_APT: 270.0,
    LocationProfile.FIRST_FLOOR_HOME: 325.0,
    LocationProfile.GROUND_STORAGE: 370.0,
    LocationProfile.DOCK_JOB: 420.0,
}


def hourly_rate_lbs(profile: str) -> float:
    return PROFILE_RATE.get(profile, PROFILE_RATE[LocationProfile.MULTI_FLOOR])


def estimate_hours(weight_lbs: float, profile: str, mover_count: int | None = None) -> float:
    movers = mover_count if mover_count is not None else movers_needed(weight_lbs)
    if movers == 0:
        return 0.0
    per_mover_rate = hourly_rate_lbs(profile)
    hours = weight_lbs / (per_mover_rate * movers)
    return round(hours, 2)


def summarize_order(order: dict[str, int], profile: str = LocationProfile.MULTI_FLOOR) -> dict:
    total, breakdown = total_weight(order)
    movers = movers_needed(total)
    trucks = trucks_needed(total)
    hours = estimate_hours(total, profile, movers)
    return {
        "total_weight_lbs": total,
        "movers_needed": movers,
        "trucks_needed": trucks,
        "estimated_labor_hours": hours,
        "movement_rate_lbs_per_mover_hour": hourly_rate_lbs(profile),
        "profile": profile,
        "items": breakdown,
    }

"""ГОСТ 2.794-79 «Устройства питающие и дозирующие» — рисунки по таблице стандарта."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_symbols import LINE, store, svg

NOTE = "собственный рисунок по скану ГОСТ 2.794-79"
FILL = 'fill="#000" stroke="#000" stroke-width="1"'


def body(*paths, extra=""):
    return svg("".join(f'<path d="{p}" {LINE}/>' for p in paths) + extra)


def arrow(x1, y1, x2, y2, size=5):
    angle = math.atan2(y2 - y1, x2 - x1)
    wing = lambda a: f"{x2 - size * math.cos(angle + a):.1f},{y2 - size * math.sin(angle + a):.1f}"
    head = f'<polygon points="{x2},{y2} {wing(0.4)} {wing(-0.4)}" {FILL}/>'
    return f'<path d="M{x1} {y1}L{x2} {y2}" {LINE}/>' + head


def bar(*ticks):
    return ["M10 30H70"] + [f"M{x} 22V38" for x in (10, 70) + ticks]


def pinwheel(inner):
    arrows = arrow(40, 16, 22, 16) + arrow(54, 30, 54, 10) + arrow(40, 44, 58, 44) + arrow(26, 30, 26, 50)
    return svg(f'<path d="M40 16L54 30L40 44L26 30Z" {LINE}/>' + inner + arrows)


def inner(*paths):
    return "".join(f'<path d="{p}" {LINE}/>' for p in paths)


def pill(x1, x2, ticks_top=(), barbs=False, double=False):
    paths = [f"M{x1 + 10} 20H{x2 - 10}A10 10 0 0 1 {x2 - 10} 40H{x1 + 10}A10 10 0 0 1 {x1 + 10} 20Z", f"M{x1} 17V43", f"M{x2} 17V43"]
    for x in ticks_top:
        paths.append(f"M{x} 14V20")
        if barbs:
            paths.append(f"M{x} 20L{x - 3} 16")
    if double:
        paths.append(f"M{x1 + 14} 24H{x2 - 14}A6 6 0 0 1 {x2 - 14} 36H{x1 + 14}A6 6 0 0 1 {x1 + 14} 24Z")
    return paths


def belt(x1, x2, **kw):
    return svg(inner(*pill(x1, x2, **kw)) + arrow(6, 30, x1, 30))


DOSER_ARROW = lambda: arrow(30, 42, 50, 16)

ROWS = [
    ("feed_hopper", "Hopper container", "Ёмкости: а) бункерные", body("M20 14V34H36V40", "M44 40V34H60V14")),
    ("feed_magazine", "Magazine container", "Ёмкости: б) магазинные", body("M20 14V34H60V14", "M20 29H60", "M36 34V40", "M44 34V40")),
    ("feed_stack", "Stack container", "Ёмкости: в) штабельные", body("M20 14V34H60V14", "M20 24H60", "M20 29H60", "M33 24V34", "M47 24V34", "M36 34V40", "M44 34V40")),
    ("feeder_belt", "Belt feeder (with traction elements)", "Питатели с тяговыми элементами: а) ленточные", belt(24, 64, double=True)),
    ("feeder_plate", "Plate feeder", "Питатели с тяговыми элементами: б) пластинчатые", belt(24, 64, ticks_top=(34, 44, 54))),
    ("feeder_scraper", "Scraper feeder", "Питатели с тяговыми элементами: в) скребковые", belt(24, 64, ticks_top=(34, 44, 54), barbs=True)),
    ("feeder_air_cushion", "Air cushion feeder", "Питатели с тяговыми элементами: г) на воздушной подушке",
     body("M24 30H64", "M24 22V38", "M64 22V38", "M44 31L39 39H49Z", "M6 30H24")),
    ("feeder_plate_disc", "Rotating plate (disc) feeder", "Питатели без тяговых элементов: а) вращающиеся: тарельчатые (дисковые)", pinwheel(inner("M35 26H45", "M40 26V36"))),
    ("feeder_vane", "Rotating vane (sector) feeder", "Питатели без тяговых элементов: а) вращающиеся: лопастные (секторные)", pinwheel(inner("M35 25L45 35", "M45 25L35 35", "M33 30H47", "M40 23V37"))),
    ("feeder_drum", "Rotating drum (rotor) feeder", "Питатели без тяговых элементов: а) вращающиеся: барабанные (роторные)", pinwheel(f'<circle cx="40" cy="30" r="7" {LINE}/>')),
    ("feeder_screw", "Rotating screw (auger) feeder", "Питатели без тяговых элементов: а) вращающиеся: винтовые (шнековые)", pinwheel(inner("M34 30L36 27L38 33L40 27L42 33L44 27L46 30"))),
    ("feeder_vibrating", "Oscillating vibratory feeder", "Питатели без тяговых элементов: б) качающиеся: вибрационные",
     body(*bar(), "M40 30L34 34L46 38L34 42L40 46", "M40 30C48 29 47 21 41 22C38 22.5 39 26 41 26")),
    ("feeder_inertial", "Oscillating inertial feeder", "Питатели без тяговых элементов: б) качающиеся: инерционные",
     body(*bar(), "M10 30L40 12L70 30", "M40 30L34 34L46 38L34 42L40 46")),
    ("feeder_carriage", "Oscillating carriage (plunger) feeder", "Питатели без тяговых элементов: б) качающиеся: кареточные, плунжерные",
     body(*bar(), "M40 30L34 34L46 38L34 42L40 46", "M56 18H66", "M61 18V30")),
    ("feeder_vibroscrew", "Oscillating vibro-screw feeder", "Питатели без тяговых элементов: б) качающиеся: вибровинтовые", pinwheel(inner("M33 30C36 24 39 24 40 30C41 36 44 36 47 30"))),
    ("doser_gear", "Volumetric doser, gear", "Дозаторы объёмные: а) шестеренчатые", body(*bar(), "M24 26L28 34M28 26L24 34", "M52 26L56 34M56 26L52 34")),
    ("doser_vane", "Volumetric doser, vane", "Дозаторы объёмные: б) лопастные", body(*bar(25, 55), "M35 26L45 34M45 26L35 34", "M34 30H46", "M40 25V35")),
    ("doser_ring", "Volumetric doser, ring", "Дозаторы объёмные: в) кольцевые", body(*bar(25, 55), "M33 24H47V36H33Z", "M33 28H47", "M33 32H47", "M40 24V36")),
    ("doser_screw", "Volumetric doser, screw (auger)", "Дозаторы объёмные: г) винтовые (шнековые)", body("M10 30L18 30L22 22L28 38L34 22L40 38L46 22L52 38L58 22L62 30H70", "M10 22V38", "M70 22V38")),
    ("doser_piston", "Volumetric doser, piston", "Дозаторы объёмные: д) поршневые", body(*bar(34, 42, 50), "M28 23H58V37H28")),
    ("doser_disc", "Volumetric doser, disc", "Дозаторы объёмные: е) дисковые", body(*bar(25, 40, 55), "M46 20A6 6 0 1 0 34 20A6 6 0 1 0 46 20")),
    ("doser_bucket", "Volumetric doser, bucket", "Дозаторы объёмные: ж) ковшовые", body(*bar(25, 40, 55), "M36 20V24H44V20", "M40 24V30")),
    ("doser_rotary", "Volumetric doser, rotary", "Дозаторы объёмные: з) ротационные", body(*bar(25, 55), "M46 30A6 6 0 1 0 34 30A6 6 0 1 0 46 30", "M40 24V36", "M34 30H46")),
    ("doser_slot", "Volumetric doser, slot", "Дозаторы объёмные: и) щелевые", svg(inner(*bar(25, 55), "M32 20L48 40", "M48 20L32 40") + arrow(38, 36, 34, 44) + arrow(42, 36, 46, 44))),
    ("doser_liquid", "Volumetric doser, liquid", "Дозаторы объёмные: к) жидкостные", svg(inner(*bar(25, 55)) + arrow(40, 8, 40, 22, 6))),
    ("doser_weight_discrete", "Weight doser, discrete action", "Дозаторы весовые: а) дискретного действия", svg(inner(*bar(), "M40 26V30") + DOSER_ARROW())),
    ("doser_weight_continuous", "Weight doser, continuous action", "Дозаторы весовые: б) непрерывного действия", svg(inner(*pill(14, 66, double=True)) + DOSER_ARROW())),
    ("doser_volume_weight", "Volume-weight doser", "Дозаторы объёмно-весовые", svg(inner(*bar(25, 55)) + DOSER_ARROW())),
]

if __name__ == "__main__":
    store("GOST 2.794", "gost", [(c, en, ru, "Питатели и дозаторы", d) for c, en, ru, d in ROWS], NOTE)

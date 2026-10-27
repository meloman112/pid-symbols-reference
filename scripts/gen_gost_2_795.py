"""ГОСТ 2.795-80 «Центрифуги» — рисунки по таблице стандарта."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_symbols import LINE, store, svg

NOTE = "собственный рисунок по скану ГОСТ 2.795-80"
FILL = 'fill="#000" stroke="#000" stroke-width="1"'
PERF = 'stroke="#000" stroke-width="4" stroke-dasharray="1.5 1.5" fill="none"'


def path(*ds):
    return "".join(f'<path d="{d}" {LINE}/>' for d in ds)


def perf(*ds):
    return "".join(f'<path d="{d}" {PERF}/>' for d in ds)


def arrow(x1, y1, x2, y2, size=5):
    angle = math.atan2(y2 - y1, x2 - x1)
    wing = lambda a: f"{x2 - size * math.cos(angle + a):.1f},{y2 - size * math.sin(angle + a):.1f}"
    out = f'<path d="M{x1} {y1}L{x2} {y2}" {LINE}/><polygon points="{x2},{y2} {wing(0.4)} {wing(-0.4)}" {FILL}/>'
    return out


def rotation(x, y):
    return f'<path d="M{x} {y}Q{x + 5} {y - 5} {x + 10} {y}" {LINE}/><polygon points="{x + 10},{y + 3} {x + 7},{y - 2} {x + 13},{y - 2}" {FILL}/>'


def housing(x1, y1, x2, y2):
    return path(f"M{x1} {y1}H{x2}V{y2}H{x1}Z")


def outlet(x, y=44):
    return arrow(x, y, x, 58, 6)


def shaft_down(y=44):
    return path(f"M50 {y}V58") + rotation(52, 52)


def vertical_rotor(wall, inside="", outlets=outlet(40), shaft=None, bottom=44):
    return svg(housing(34, 14, 66, bottom) + wall + inside + arrow(50, 2, 50, 14) + outlets + (shaft or shaft_down(bottom)), width=100)


def vwalls(y1=18, y2=40, x1=39, x2=61):
    return perf(f"M{x1} {y1}V{y2}", f"M{x2} {y1}V{y2}")


def stirred(wall_dash):
    wall = (perf if wall_dash else path)("M39 18V30", "M61 18V30") + path("M39 30L45 40H55L61 30" if wall_dash else "M39 30L45 40H55L61 30")
    stir = path("M50 14V36", "M45 36H55") + arrow(43, 4, 43, 22)
    return svg(housing(34, 14, 66, 44) + wall + stir + rotation(52, 6) + outlet(40) + arrow(50, 44, 50, 58), width=100)


def knives(dashed):
    strips = (perf if dashed else path)("M36 19H64", "M36 41H64")
    knife = path("M42 24H58L42 38H60")
    shaft = path("M62 30H90") + rotation(78, 26) + arrow(84, 22, 62, 22) + arrow(62, 37, 84, 37)
    return svg(housing(34, 14, 66, 44) + strips + knife + shaft + outlet(40), width=100)


def screw_horizontal(dashed):
    walls = (perf if dashed else path)("M36 18L62 25", "M36 40L62 33")
    inside = path("M40 21L44 38L48 21L52 38L56 24", "M66 22H72V36H66")
    shaft = path("M60 30H92") + rotation(80, 26) + arrow(84, 24, 70, 24) + arrow(72, 34, 86, 34)
    return svg(housing(34, 14, 66, 44) + walls + inside + shaft + outlet(40) + outlet(70, 36), width=100)


def screw_vertical(dashed):
    walls = (perf if dashed else path)("M38 17L44 40", "M62 17L56 40")
    spring = path("M46 17L54 22L46 28L54 34L47 40")
    return svg(housing(34, 14, 66, 44) + walls + spring + arrow(50, 2, 50, 14) + outlet(40) + outlet(46) + shaft_down(), width=100)


def horizontal_cone(dashed):
    walls = (perf if dashed else path)("M38 17L64 23", "M38 43L64 37")
    inside = path("M42 30H56", "M45 30L56 24V36Z")
    shaft = path("M8 30H70") + rotation(24, 24) + arrow(14, 28, 8, 28)
    return svg(housing(38, 14, 68, 46) + walls + inside + shaft + arrow(88, 22, 68, 22) + arrow(68, 40, 90, 40) + outlet(52, 46), width=100)


def hydraulic(full):
    walls = perf("M38 18V28", "M62 18V28") + path("M38 28H62")
    flow = arrow(50, 2, 50, 30) + arrow(50, 46, 50, 34)
    return svg(housing(34, 16, 66, 46) + walls + flow + (arrow(50, 46, 50, 58) if full else shaft_down(46)) + outlet(40, 46), width=100)


def hydraulic_internal(full):
    walls = perf("M38 18V28", "M62 18V28") + path("M38 28H62")
    shaft = arrow(50, 2, 50, 56 if full else 24) if full else arrow(50, 2, 50, 24) + path("M50 24V56")
    return svg(housing(34, 14, 66, 42) + walls + shaft + rotation(52, 22) + outlet(40, 42), width=100)


ROWS = [
    ("cf_filter_manual", "Filtering centrifuge, batch, manual discharge", "Центрифуги фильтрующие: а) периодического действия с выгрузкой осадка: ручной", vertical_rotor(vwalls(), outlets=arrow(40, 44, 40, 58, 6))),
    ("cf_filter_gravity", "Filtering centrifuge, batch, gravity discharge", "Центрифуги фильтрующие: а) периодического действия с выгрузкой осадка: гравитационной (под действием сил тяжести)", stirred(True)),
    ("cf_filter_knives", "Filtering centrifuge, batch, automatic knife discharge", "Центрифуги фильтрующие: а) периодического действия с выгрузкой осадка: ножами (автоматически)", knives(True)),
    ("cf_filter_inertial", "Filtering centrifuge, continuous, inertial discharge", "Центрифуги фильтрующие: б) непрерывного действия с выгрузкой осадка: инерционной", screw_vertical(True)),
    ("cf_filter_vibrating_cone", "Filtering centrifuge, continuous, vibrating horizontal conical rotor", "Центрифуги фильтрующие: б) непрерывного действия с выгрузкой осадка: вибрационной с горизонтальным коническим ротором", horizontal_cone(True)),
    ("cf_filter_vertical_cone", "Filtering centrifuge, continuous, vertical conical rotor", "Центрифуги фильтрующие: б) непрерывного действия с выгрузкой осадка: с вертикальным коническим ротором",
     svg(housing(34, 14, 66, 42) + perf("M38 18L44 38", "M62 18L56 38") + path("M50 20L45 32H55Z") + arrow(50, 2, 50, 14) + outlet(40, 42) + outlet(46, 42) + path("M52 32V58") + f'<polygon points="52,60 49,54 55,54" {FILL}/><polygon points="52,34 49,40 55,40" {FILL}/>' + rotation(54, 46), width=100)),
    ("cf_filter_pulsating_piston", "Filtering centrifuge, continuous, pulsating piston", "Центрифуги фильтрующие: б) непрерывного действия с выгрузкой осадка: пульсирующим поршнем",
     svg(housing(38, 14, 68, 46) + perf("M40 19H66", "M40 41H66") + path("M42 24L56 30L42 36Z", "M46 26V34", "M50 27V33", "M6 30H58") + rotation(22, 24) + arrow(14, 28, 6, 28) + arrow(14, 28, 22, 28) + arrow(88, 24, 62, 24) + arrow(70, 38, 92, 38) + outlet(52, 46), width=100)),
    ("cf_filter_screw", "Filtering centrifuge, continuous, screw discharge", "Центрифуги фильтрующие: б) непрерывного действия с выгрузкой осадка: шнековой", screw_horizontal(True)),
    ("cf_settling_manual", "Settling centrifuge, batch, manual discharge", "Центрифуги отстойные: а) периодического действия с выгрузкой осадка: ручной",
     vertical_rotor(path("M38 14V38H62V14"), outlets=outlet(40))),
    ("cf_settling_gravity", "Settling centrifuge, batch, gravity discharge", "Центрифуги отстойные: а) периодического действия с выгрузкой осадка: гравитационной (под действием сил тяжести)", stirred(False)),
    ("cf_settling_knives", "Settling centrifuge, batch, automatic knife discharge", "Центрифуги отстойные: а) периодического действия с выгрузкой осадка: ножами (автоматически)", knives(False)),
    ("cf_settling_screw_horizontal", "Settling centrifuge, continuous, horizontal screw discharge", "Центрифуги отстойные: б) непрерывного действия со шнековой выгрузкой осадка: горизонтальные", screw_horizontal(False)),
    ("cf_settling_screw_vertical", "Settling centrifuge, continuous, vertical screw discharge", "Центрифуги отстойные: б) непрерывного действия со шнековой выгрузкой осадка: вертикальные", screw_vertical(False)),
    ("cf_hydraulic_external_partial", "Hydraulic-drive centrifuge, external drive, partial-flow", "Центрифуги с гидравлическим приводом ротора: а) с внешним приводом: неполнопоточные", hydraulic(False)),
    ("cf_hydraulic_external_full", "Hydraulic-drive centrifuge, external drive, full-flow", "Центрифуги с гидравлическим приводом ротора: а) с внешним приводом: полнопоточные", hydraulic(True)),
    ("cf_hydraulic_internal_partial", "Hydraulic-drive centrifuge, internal drive, partial-flow", "Центрифуги с гидравлическим приводом ротора: б) с внутренним приводом: неполнопоточные", hydraulic_internal(False)),
    ("cf_hydraulic_internal_full", "Hydraulic-drive centrifuge, internal drive, full-flow", "Центрифуги с гидравлическим приводом ротора: б) с внутренним приводом: полнопоточные", hydraulic_internal(True)),
    ("cf_supercentrifuge_tubular", "Supercentrifuge, tubular, batch, manual sludge discharge", "Центрифуги с гидравлическим приводом ротора: в) сверхцентрифуги: трубчатые, периодического действия, с ручной выгрузкой осадка",
     svg(housing(34, 18, 66, 48) + path("M38 22H62V44H38Z", "M38 27H62", "M38 31H62", "M38 35H62", "M38 39H62") + arrow(50, 4, 50, 22) + arrow(34, 22, 12, 22) + arrow(66, 34, 88, 34) + path("M50 48V58") + rotation(52, 52), width=100)),
    ("cf_separator_batch", "Separator, batch, manual sludge discharge", "Центрифуги с гидравлическим приводом ротора: в) сверхцентрифуги: сепараторы периодического действия с ручной выгрузкой осадка",
     svg(housing(34, 24, 66, 50) + path("M45 26L40 46H35", "M55 26L60 46H65") + arrow(52, 4, 52, 26) + arrow(41, 24, 41, 8) + arrow(46, 24, 46, 8) + path("M50 50V60") + rotation(52, 52), width=100)),
    ("cf_separator_continuous", "Separator, continuous, hydraulic sludge discharge", "Центрифуги с гидравлическим приводом ротора: в) сверхцентрифуги: сепараторы непрерывного действия с гидравлической выгрузкой осадка",
     svg(housing(34, 24, 66, 50) + path("M45 26L40 46H35", "M55 26L60 46H65") + arrow(52, 4, 52, 26) + arrow(42, 24, 42, 8) + arrow(66, 44, 88, 44) + path("M50 50V60") + rotation(52, 52), width=100)),
]

if __name__ == "__main__":
    store("GOST 2.795", "gost", [(c, en, ru, "Центрифуги", d) for c, en, ru, d in ROWS], NOTE)

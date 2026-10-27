"""ГОСТ 2.792-74 «Аппараты сушильные» — рисунки по таблице 1 стандарта (по скану)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_symbols import LINE, THIN, store, svg

NOTE = "собственный рисунок по скану ГОСТ 2.792-74"
CATEGORY = "Сушильные аппараты"


def p(d, style=LINE):
    return f'<path d="{d}" {style}/>'


def paths(*ds, style=LINE):
    return "".join(p(d, style) for d in ds)


def circle(cx, cy, r, style=LINE):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" {style}/>'


def rect(x, y, w, h, rx=0, style=LINE):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" {style}/>'


def dot(x, y, r=1.6):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#000"/>'


def arrowhead(x, y, dx, dy):
    """Filled triangle with tip at (x, y) pointing along (dx, dy)."""
    px, py = -dy, dx
    return f'<path d="M{x} {y}L{x - 6 * dx + 3 * px} {y - 6 * dy + 3 * py}L{x - 6 * dx - 3 * px} {y - 6 * dy - 3 * py}Z" fill="#000"/>'


# --- корпуса (разд. «корпуса») ---
BOX = "M26 12H54V48H26Z"
BOX_VAC = "M26 12L40 17L54 12V48L40 43L26 48Z"
ROLL = "M28 50V24L40 10L52 24V50Z"
ROLL_VAC = "M28 50L40 46L52 50V24L40 10L28 24Z"
SPRAY = "M28 10H52V32L40 50L28 32Z"
CYCLONE = "M20 21V10H52V32L40 50L28 32V21H20"
AEROFOUNT = "M28 18L40 8L52 18V32L40 50L28 32Z"
PNEUMATIC = ("M28 12H52M28 48H52", "M32 12V48", "M48 12V48")
SHAFT = "M26 12H54L40 50Z"
SHAFT_UP = "M26 22L40 12L54 22L40 50Z"
SHAFT_VAC = "M26 12L40 20L54 12L40 50Z"

HATCH = ('<defs><pattern id="h" width="4" height="4" patternUnits="userSpaceOnUse">'
         f'<path d="M0 0L4 4M4 0L0 4" {THIN}/></pattern></defs>')


def hatched(d):
    return svg(HATCH + f'<path d="{d}" stroke="#000" stroke-width="2" fill="url(#h)"/>')


def shelves(x, y, w, h, count=7):
    step = h / count
    lines = "".join(p(f"M{x} {y + step * i:.1f}H{x + w}", THIN) for i in range(1, count))
    return rect(x, y, w, h) + lines


def roller(cx, cy):
    return circle(cx, cy, 5) + circle(cx, cy - 1, 2.5, THIN)


def roller_pair(cx, cy):
    return circle(cx - 5, cy, 5) + circle(cx + 5, cy, 5) + circle(cx - 5, cy - 1, 2.5, THIN) + circle(cx + 5, cy - 1, 2.5, THIN)


def rotor_stem(dots=False):
    ys = (24, 32, 40, 48) if dots else (28, 35, 42, 50)
    bars = paths(*(f"M{28} {y}H52" for y in ys))
    ends = "".join(dot(28, y) + dot(52, y) for y in ys) if dots else ""
    return paths("M40 8V54") + bars + ends


def belt(x, y, w, h):
    return rect(x, y, w, h, h / 2) + rect(x + 3, y + 3, w - 6, h - 6, (h - 6) / 2)


LOOP = "M12 38V28C12 6 32 6 32 28V38C32 58 56 58 56 38V30"
DOTS_FILL = "".join(dot(20 + 7 * i, 38 + 4 * (i % 2), 0.9) for i in range(8))
SURFACE = "M14 32C22 28 28 36 38 32S54 28 66 32"
ZIGZAG = "M8 30H20L23 24L27 36L30 30H34"
ZIGZAG_R = "M46 30H50L53 24L57 36L60 30H72"
VIB = paths("M8 30H20L23 24L27 36L30 30H34", "M46 30H50L53 24L57 36L60 30H72") + p("M34 30H46", THIN.replace('stroke-width="1"', 'stroke-width="2" stroke-dasharray="4 3"'))
SCREW = "M8 32H72"


def screw_body(style):
    return paths("M24 38V18H46L50 24H66V46H54V38Z", style=style) + p("M32 32L36 38L40 26L44 38L48 26L52 38L56 32", style)


def screw_dryer(transform, lw):
    style = f'stroke="#000" stroke-width="{lw}" fill="none"'
    return f'<g transform="{transform}">' + screw_body(style) + p("M10 32H32M56 32H72", style) + "</g>"


def rotating_arrow_left():
    return p("M12 24C6 27 6 33 12 36") + arrowhead(12, 36, 1, 0.3)


def drum(body_path):
    rings = rect(20, 16, 5, 28, style='stroke="#000" stroke-width="1" fill="#000"') + rect(55, 16, 5, 28, style='stroke="#000" stroke-width="1" fill="#000"')
    arrow = p("M44 54C52 40 50 28 44 14") + arrowhead(44, 14, -0.3, -1)
    return svg(p(body_path) + rings + arrow)


def rotor_dryer(body_path, jacket=False):
    ticks = paths(*(f"M{26 + 4 * i} 25V35" for i in range(9)), style=THIN)
    jacket_part = rect(24, 13, 32, 7) + rect(24, 40, 32, 7) if jacket else ""
    return svg(jacket_part + p(body_path) + p("M10 30H72") + ticks + rotating_arrow_left())


CABINET = "M26 8H54V52H26Z"
CABINET_VAC = "M26 8L40 14L54 8V52L40 46L26 52Z"
RACK = shelves(33, 18, 14, 24, 6)
RACK_SM = shelves(33, 20, 14, 20, 6)

ELEMENTS = [
    ("body_cabinet_atm", "Cabinet dryer housing, atmospheric pressure", "Корпус шкафа сушильного под атмосферным давлением", svg(p(BOX))),
    ("body_cabinet_vacuum", "Cabinet dryer housing, below atmospheric pressure", "Корпус шкафа сушильного под давлением ниже атмосферного", svg(p(BOX_VAC))),
    ("body_roll_atm", "Roll dryer housing, atmospheric pressure", "Корпус вальцовой сушилки под атмосферным давлением", svg(p(ROLL))),
    ("body_roll_vacuum", "Roll dryer housing, below atmospheric pressure", "Корпус вальцовой сушилки под давлением ниже атмосферного", svg(p(ROLL_VAC))),
    ("body_spray", "Spray dryer housing", "Корпус распылительной сушилки", svg(p(SPRAY))),
    ("body_cyclone", "Cyclone dryer housing", "Корпус циклонной сушилки", svg(p(CYCLONE))),
    ("body_fountain", "Fluidized-fountain (aerofountain) dryer housing", "Корпус аэрофонтанной сушилки", svg(p(AEROFOUNT))),
    ("body_pneumatic", "Pneumatic dryer housing", "Корпус пневматической сушилки", svg(paths(*PNEUMATIC))),
    ("body_shaft_atm", "Shaft dryer housing, atmospheric pressure", "Корпус шахтной сушилки под атмосферным давлением", svg(p(SHAFT))),
    ("body_shaft_pressure", "Shaft dryer housing, above atmospheric pressure", "Корпус шахтной сушилки под давлением выше атмосферного", svg(p(SHAFT_UP))),
    ("body_shaft_vacuum", "Shaft dryer housing, below atmospheric pressure", "Корпус шахтной сушилки под давлением ниже атмосферного", svg(p(SHAFT_VAC))),
    ("conv_shelf_racks", "Conveyor element: racks with shelves", "Элементы транспортирующих устройств: стеллажи с полками", svg(shelves(30, 12, 20, 36, 9))),
    ("conv_single_roll", "Conveyor element: single-roll", "Элементы транспортирующих устройств: элемент одновальцовый", svg(circle(40, 30, 8) + circle(39, 29, 5.5, THIN))),
    ("conv_double_roll", "Conveyor element: double-roll", "Элементы транспортирующих устройств: элемент двухвальцовый", svg(circle(32, 30, 9) + circle(48, 30, 9) + circle(31, 29, 6, THIN) + circle(47, 29, 6, THIN))),
    ("conv_shelf_disc_rotor", "Conveyor element: shelf-disc rotor", "Элементы транспортирующих устройств: ротор полочно-дисковый", svg(paths("M40 8V52", "M30 30H50", "M30 37H50", "M30 44H50", "M30 52H50"))),
    ("conv_shelf_disc_rotor_tilting", "Conveyor element: shelf-disc rotor with tilting shelves", "Элементы транспортирующих устройств: ротор полочно-дисковый с опрокидывающимися полками", svg(rotor_stem(dots=True))),
    ("conv_wagon", "Conveyor element: wagon", "Элементы транспортирующих устройств: вагонетка", svg(paths("M28 22V30H52V22") + circle(34, 38, 6) + circle(46, 38, 6) + circle(34, 37, 3, THIN) + circle(46, 37, 3, THIN))),
    ("conv_belt", "Conveyor element: belt", "Элементы транспортирующих устройств: лента", svg(belt(12, 21, 56, 18))),
    ("conv_loop", "Conveyor element: loop", "Элементы транспортирующих устройств: петля", svg(p(LOOP))),
    ("conv_screw", "Conveyor element: screw", "Элементы транспортирующих устройств: шнек", svg(p("M8 30H18L22 24L28 36L34 24L40 36L46 24L52 36L56 30H72"))),
    ("conv_vibrating_surface", "Conveyor element: vibrating surface", "Элементы транспортирующих устройств: вибрирующая поверхность", svg(VIB)),
]

DRYERS = [
    ("dryer_general", "Dryer, general symbol", "Аппараты сушильные. Общее обозначение", svg(rect(14, 16, 52, 28) + p(SURFACE) + DOTS_FILL)),
    ("dryer_cabinet_atm", "Cabinet dryer, atmospheric pressure", "Шкафы сушильные под атмосферным давлением", svg(p(CABINET) + rect(32, 16, 16, 28) + shelves(35, 20, 10, 20, 6))),
    ("dryer_cabinet_vacuum", "Cabinet dryer, below atmospheric pressure", "Шкафы сушильные под давлением ниже атмосферного", svg(p(CABINET_VAC) + rect(32, 18, 16, 24) + shelves(35, 21, 10, 18, 6))),
    ("dryer_roll_single_atm", "Single-roll dryer, atmospheric pressure", "Сушилки вальцовые: сушилка одновальцовая под атмосферным давлением", svg(p("M26 52V22L40 8L54 22V52Z") + roller(40, 38))),
    ("dryer_roll_double_atm", "Double-roll dryer, atmospheric pressure", "Сушилки вальцовые: сушилка двухвальцовая под атмосферным давлением", svg(p("M26 52V22L40 8L54 22V52Z") + roller_pair(40, 38))),
    ("dryer_roll_single_vacuum", "Single-roll dryer, below atmospheric pressure", "Сушилки вальцовые: сушилка одновальцовая под давлением ниже атмосферного", svg(p("M26 52L40 47L54 52V22L40 8L26 22Z") + roller(40, 36))),
    ("dryer_roll_double_vacuum", "Double-roll dryer, below atmospheric pressure", "Сушилки вальцовые: сушилка двухвальцовая под давлением ниже атмосферного", svg(p("M24 52L40 47L56 52V22L40 8L24 22Z") + roller_pair(40, 36))),
    ("dryer_spray_centrifugal", "Spray dryer, centrifugal atomization", "Сушилки распылительные: с центробежным распылением", svg(p("M26 14H54V34L40 52L26 34Z") + paths("M40 4V18", "M34 18H46"))),
    ("dryer_spray_nozzle", "Spray dryer, nozzle atomization", "Сушилки распылительные: с форсуночным распылением", svg(p("M26 14H54V34L40 52L26 34Z") + paths("M40 4V20", "M40 20L36 28", "M40 20V29", "M40 20L44 28"))),
    ("dryer_fluidized_boiling", "Fluidized-bed dryer, boiling bed", "Сушилки со взвешенным слоем: с кипящим слоем", svg(rect(28, 6, 24, 48) + p("M28 36C34 32 38 40 44 36S50 34 52 35", LINE) + "".join(dot(31 + 5 * (i % 4), 41 + 4 * (i // 4), 0.9) for i in range(8)) + p("M28 48H52"))),
    ("dryer_fluidized_cyclone", "Fluidized-bed dryer, cyclone", "Сушилки со взвешенным слоем: циклонные", svg(p(CYCLONE) + p("M28 32H52", THIN.replace('stroke-width="1"', 'stroke-width="1.5" stroke-dasharray="4 3"')))),
    ("dryer_fluidized_fountain", "Fluidized-bed dryer, fountain", "Сушилки со взвешенным слоем: аэрофонтанные", svg(p(AEROFOUNT) + paths("M33 20L36 26L39 21", "M41 21L44 26L47 20", style=THIN))),
    ("dryer_fluidized_pneumatic", "Fluidized-bed dryer, pneumatic", "Сушилки со взвешенным слоем: пневматические", svg(paths(*PNEUMATIC) + paths("M40 18V30") + '<path d="M36 28L40 34L44 28Z" ' + THIN + "/>" + p("M32 40H48", THIN.replace('stroke-width="1"', 'stroke-width="1.5" stroke-dasharray="4 3"')))),
    ("dryer_shaft_atm", "Shaft dryer, atmospheric pressure", "Сушилки шахтные под атмосферным давлением", hatched(SHAFT)),
    ("dryer_shaft_pressure", "Shaft dryer, above atmospheric pressure", "Сушилки шахтные под давлением выше атмосферного", hatched(SHAFT_UP)),
    ("dryer_shaft_vacuum", "Shaft dryer, below atmospheric pressure", "Сушилки шахтные под давлением ниже атмосферного", hatched(SHAFT_VAC)),
    ("dryer_belt_single", "Single-belt dryer", "Сушилки ленточные одноленточные", svg(rect(10, 20, 60, 20) + belt(16, 24, 48, 12))),
    ("dryer_belt_multi", "Multi-belt dryer", "Сушилки ленточные многоленточные", svg(rect(12, 4, 56, 52) + belt(18, 8, 44, 11) + belt(16, 24, 48, 11) + belt(18, 40, 44, 11))),
    ("dryer_belt_roll", "Roll-belt dryer", "Сушилки ленточные вальцеленточные", svg(rect(10, 6, 60, 48) + circle(20, 18, 4) + circle(28, 18, 4) + belt(18, 30, 46, 16))),
    ("dryer_belt_loop", "Loop belt dryer", "Сушилки ленточные петлевые", svg(rect(10, 6, 60, 48) + p("M18 14V30C18 52 36 52 36 30V24C36 8 52 8 52 24V32C52 48 64 48 64 34"))),
    ("dryer_screw_single", "Screw dryer, single-screw", "Сушилки шнековые одношнековые", svg(screw_dryer("", 2))),
    ("dryer_screw_gallery", "Screw dryer, gallery", "Сушилки шнековые галерейные", svg(screw_dryer("translate(1 -4) scale(0.6)", 3.3) + screw_dryer("translate(15 10) scale(0.6)", 3.3) + screw_dryer("translate(29 24) scale(0.6)", 3.3))),
    ("dryer_screw_multitier", "Screw dryer, multi-tier", "Сушилки шнековые многоярусные", svg(screw_dryer("translate(20 -5) scale(0.5)", 4) + screw_dryer("translate(60 12) scale(-0.5 0.5)", 4) + screw_dryer("translate(20 29) scale(0.5)", 4))),
    ("dryer_vibrating", "Vibrating dryer", "Сушилки вибрационные", svg(rect(18, 20, 44, 20) + VIB)),
    ("dryer_drum_atm", "Drum dryer with rotating drum, atmospheric pressure", "Сушилки барабанные с вращающимся барабаном под атмосферным давлением", drum("M14 20H66V40H14Z")),
    ("dryer_drum_vacuum", "Drum dryer with rotating drum, below atmospheric pressure", "Сушилки барабанные с вращающимся барабаном под давлением ниже атмосферного", drum("M14 18L19 30L14 42H66L61 30L66 18Z")),
    ("dryer_rotor_atm", "Rotor dryer, atmospheric pressure", "Сушилки роторные под атмосферным давлением", rotor_dryer("M16 20H64V40H16Z")),
    ("dryer_rotor_vacuum", "Rotor dryer, below atmospheric pressure", "Сушилки роторные под давлением ниже атмосферного", rotor_dryer("M14 18L18 30L14 42H66L62 30L66 18Z")),
    ("dryer_rotor_jacket_atm", "Rotor dryer with external heating, atmospheric pressure", "Сушилки роторные с наружным обогревом под атмосферным давлением", rotor_dryer("M16 20H64V40H16Z", jacket=True)),
    ("dryer_rotor_jacket_vacuum", "Rotor dryer with external heating, below atmospheric pressure", "Сушилки роторные с наружным обогревом под давлением ниже атмосферного", rotor_dryer("M14 18L18 30L14 42H66L62 30L66 18Z", jacket=True)),
    ("dryer_tubular", "Tubular dryer", "Сушилки трубчатые", svg(rect(18, 16, 44, 28) + paths("M18 22H62", "M18 26H62", "M18 34H62", "M18 38H62", style=THIN) + rect(10, 27, 60, 6) + rotating_arrow_left())),
    ("dryer_sublimation", "Sublimation (freeze) dryer", "Сушилки сублимационные", svg(p("M28 8L40 13L52 8V52L40 47L28 52Z") + circle(40, 34, 6) + p("M36 34H44"))),
    ("dryer_tray_disc", "Tray dryer, shelf-disc", "Сушилки полочные полочно-дисковые", svg(rect(26, 16, 28, 36) + paths("M40 6V44", "M26 22H38", "M42 28H54", "M26 34H38", "M42 40H54", "M34 6C38 6 41 8 43 10") + arrowhead(44, 10, 0.8, 0.6))),
    ("dryer_tray_tilting", "Tray dryer with tilting shelves", "Сушилки полочные с опрокидывающимися полками", svg(rect(26, 16, 28, 36) + paths("M40 6V48", "M26 24H54", "M26 32H54", "M26 40H54", style=THIN) + paths("M31 20H49", "M31 28H49", "M31 36H49", "M31 44H49") + "".join(dot(x, y) for y in (20, 28, 36, 44) for x in (31, 49)) + p("M34 6C38 6 41 8 43 10") + arrowhead(44, 10, 0.8, 0.6))),
]

if __name__ == "__main__":
    rows = [(code, en, ru, CATEGORY, drawing) for code, en, ru, drawing in ELEMENTS + DRYERS]
    store("GOST 2.792", "gost", rows, NOTE)

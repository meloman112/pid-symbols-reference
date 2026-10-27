"""ГОСТ 2.793-79 «Элементы и устройства машин и аппаратов химических производств. Общие обозначения» — рисунки по таблице 1 (по скану)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_symbols import LINE, THIN, store, svg

NOTE = "собственный рисунок по скану ГОСТ 2.793-79"
CATEGORY = "Элементы машин и аппаратов"
DASH = 'stroke="#000" stroke-width="1" stroke-dasharray="3 2" fill="none"'
LIQ, GAS = "для жидкости", "для воздуха (газа)"
LIQ_EN, GAS_EN = "liquid", "air/gas"


def p(d, style=LINE):
    return f'<path d="{d}" {style}/>'


def paths(*ds, style=LINE):
    return "".join(p(d, style) for d in ds)


def tri(x, y, direction, filled, size=7, half=3.5):
    """Arrowhead with tip at (x, y); direction is one of r, l, u, d."""
    dx, dy = {"r": (1, 0), "l": (-1, 0), "u": (0, -1), "d": (0, 1)}[direction]
    bx, by = x - size * dx, y - size * dy
    a, b = (bx - half * dy, by + half * dx), (bx + half * dy, by - half * dx)
    style = 'fill="#000" stroke="#000" stroke-width="1"' if filled else 'fill="none" stroke="#000" stroke-width="1.5"'
    return f'<path d="M{x} {y}L{a[0]} {a[1]}L{b[0]} {b[1]}Z" {style}/>'


def open_arrow(x, y, dx, dy):
    """Thin open arrowhead with tip at (x, y) pointing along (dx, dy)."""
    return p(f"M{x - 3 * dx - 2 * dy} {y - 3 * dy + 2 * dx}L{x} {y}L{x - 3 * dx + 2 * dy} {y - 3 * dy - 2 * dx}", THIN)


def diamond(cx=40, cy=30, r=12, style=LINE):
    return p(f"M{cx - r} {cy}L{cx} {cy - r}L{cx + r} {cy}L{cx} {cy + r}Z", style)


def lead(side, filled, pointing="r"):
    """Pipe stub on the left or right of the diamond with an arrowhead."""
    tip = {("l", "r"): 21, ("l", "l"): 14, ("r", "r"): 67, ("r", "l"): 59}[(side, pointing)]
    line = "M8 30H28" if side == "l" else "M52 30H72"
    return p(line) + tri(tip, 30, pointing, filled)


def top_out(filled=False, pointing="u"):
    return p("M40 18V6") + (tri(40, 8, "u", filled) if pointing == "u" else tri(40, 15, "d", filled))


def bottom_out(filled=True):
    return p("M40 42V55") + tri(40, 55, "d", filled)


CHORD = p("M28 30H52", THIN)
VERT = p("M40 20V40", THIN)
UP = open_arrow(40, 20, 0, -1)
DOWN = open_arrow(40, 40, 0, 1)
STAR = paths("M38 28L42 32", "M42 28L38 32", style=THIN)
COOL = VERT + CHORD + UP
HEAT = VERT + CHORD + STAR + DOWN
BOTH = VERT + CHORD + STAR + UP + DOWN
EVAP = CHORD + p("M40 30V40", THIN) + DOWN


def coolant(filled):
    return p("M34 36V55") + p("M46 36V55") + tri(34, 44, "u", filled) + tri(46, 51, "d", filled)


FAN = tri(40, 42, "u", False)
INJECT = p("M25 47L35 37", THIN) + open_arrow(35, 37, 0.7, -0.7)
ELECTRIC = p("M40 42V44") + f'<rect x="35" y="44" width="10" height="5" {LINE}/>'

# (code, English, Russian, drawing under the apparatus)
HEATING_WAYS = [
    ("natural", "natural", "с естественным", ""),
    ("by_liquid", "forced, by liquid", "с принудительным жидкостью", coolant(True)),
    ("by_gas", "forced, by air (gas)", "с принудительным воздухом (газом)", coolant(False)),
    ("fan", "forced, by fan", "с принудительным вентилятором", FAN),
    ("injection", "forced, by injection", "с принудительным впрыском", INJECT),
    ("electric", "forced, by electric current", "с принудительным электрическим током", ELECTRIC),
]


def through(filled):
    return lead("l", filled) + lead("r", filled)


MEDIUMS = [("liquid", LIQ_EN, LIQ, True), ("gas", GAS_EN, GAS, False)]
COOL_WAYS = [(c, e, r.replace("принудительным", "принудительным охлаждением").replace("естественным", "естественным охлаждением"), x) for c, e, r, x in HEATING_WAYS if c != "electric"]
HEAT_WAYS = [(c, e, r.replace("принудительным", "принудительным обогревом").replace("естественным", "естественным обогревом"), x) for c, e, r, x in HEATING_WAYS]


def way_rows_simple(code, en, ru, inside, ways, base, mediums):
    rows = []
    for way_code, way_en, way_ru, extra in ways:
        for medium_code, medium_en, medium_ru, filled in mediums:
            name_ru = f"{ru} {way_ru}" + (f", {medium_ru}" if len(mediums) > 1 else "")
            name_en = f"{en}, {way_en}" + (f", for {medium_en}" if len(mediums) > 1 else "")
            suffix = f"_{medium_code}" if len(mediums) > 1 else ""
            rows.append((f"{code}_{way_code}{suffix}", name_en, name_ru, svg(diamond() + inside + base(filled) + extra)))
    return rows


HEAT_EXCHANGERS = way_rows_simple("heat_exchanger", "Heat exchanger", "Аппараты теплообменные", COOL, COOL_WAYS, through, MEDIUMS)
HEATERS = way_rows_simple("heater", "Heater", "Подогреватели", HEAT, HEAT_WAYS, through, MEDIUMS)
THERMOREGULATORS = [(f"thermoregulator_{c}", f"Thermoregulator with alternating heat supply and removal, for {e}",
                     f"Терморегуляторы, работающие в переменном режиме подвода и отвода тепла от рабочей среды, {r}",
                     svg(diamond() + BOTH + through(f))) for c, e, r, f in MEDIUMS]


def condenser(extra):
    return svg(diamond() + COOL + lead("l", False) + lead("r", True) + p("M40 18V6") + tri(40, 8, "u", False) + extra)


CONDENSERS = [(f"condenser_{c}", f"Condenser, {e}", f"Конденсаторы {r.replace('принудительным', 'принудительным охлаждением').replace('естественным', 'естественным охлаждением')}", condenser(x))
              for c, e, r, x in COOL_WAYS]

MISC = [
    ("oil_sprayer", "Oil sprayer (lubricator)", "Маслораспылители", svg(diamond() + lead("l", False) + lead("r", False))),
    ("air_humidifier", "Air (gas) humidifier", "Увлажнители воздуха (газа)", svg(diamond() + CHORD + lead("l", False) + lead("r", False) + p("M40 42V55") + tri(40, 46, "u", True))),
]


def evaporator(inside, extra):
    return svg(diamond() + inside + lead("l", True) + top_out(False) + extra)


EVAPORATION_WAYS = [(c, e, r.replace("принудительным", "принудительным обогревом").replace("естественным", "естественным обогревом"), x) for c, e, r, x in HEATING_WAYS]
EVAPORATORS = (
    [(f"evaporator_concentrating_{c}", f"Concentrating evaporator, {e}", f"Аппараты выпарные: выпариватели {r}", evaporator(HEAT, x)) for c, e, r, x in EVAPORATION_WAYS]
    + [(f"evaporator_vaporizing_{c}", f"Vaporizer, {e}", f"Аппараты выпарные: испарители {r}", evaporator(EVAP, x)) for c, e, r, x in EVAPORATION_WAYS]
)
COLUMN = [("column_apparatus", "Column apparatus", "Аппараты колонные",
           svg(diamond() + VERT + CHORD + lead("l", False) + lead("r", True, "l") + top_out(False) + bottom_out(True)))]


# --- фильтры ---
def filtration(code, en, ru, inside, with_arrows, bottom=None, top=None):
    """Filter drawing; with_arrows gives the liquid and air (gas) variants of the process line."""
    rows = []
    for medium_code, medium_en, medium_ru, filled in MEDIUMS if with_arrows else [("", "", "", False)]:
        body = diamond() + inside + (through(filled) if with_arrows else p("M8 30H28") + p("M52 30H72"))
        body += (bottom or "") + (top or "")
        rows.append((f"{code}_{medium_code}" if medium_code else code,
                     en + (f", for {medium_en}" if medium_code else ""), ru + (f", {medium_ru}" if medium_code else ""), svg(body)))
    return rows


DRAIN = bottom_out(True)
THIN_DRAIN = p("M40 42V54") + open_arrow(40, 54, 0, 1)
FLOAT = p("M36 33H44L40 39Z", THIN)
LIQUID_SEP = p("M40 18V30", DASH) + CHORD
SOLID_SEP = p("M40 20V40", DASH) + p("M36 21V39", THIN) + p("M44 21V39", THIN)
SOLID_SEP_AUTO = SOLID_SEP + f'<circle cx="40" cy="26" r="2" {THIN}/>'
GAS_SEP = CHORD + p("M40 30V42", DASH)
CHEMICAL = p("M28 30H52", THIN) + p("M33 34H47", THIN)

FILTERS = (
    filtration("filter_liquid_manual", "Filter for separating liquid fractions, manual drain", "Фильтры для отделения жидких фракций с ручным спуском", LIQUID_SEP, True, DRAIN)
    + filtration("filter_liquid_auto", "Filter for separating liquid fractions, automatic drain", "Фильтры для отделения жидких фракций с автоматическим спуском", LIQUID_SEP + FLOAT, True, DRAIN)
    + [("filter_chemical_manual", "Filter, chemical method, manual drain", "Фильтры для отделения жидких фракций химическим способом с ручным спуском",
        svg(diamond() + CHEMICAL + lead("l", False) + lead("r", False) + DRAIN)),
       ("filter_chemical_auto", "Filter, chemical method, automatic drain", "Фильтры для отделения жидких фракций химическим способом с автоматическим спуском",
        svg(diamond() + CHEMICAL + FLOAT + lead("l", False) + lead("r", False) + DRAIN))]
    + filtration("filter_solid_manual", "Filter for separating solid fractions, manual cleaning", "Фильтры для отделения твердых фракций с ручной очисткой", SOLID_SEP, True, THIN_DRAIN)
    + filtration("filter_solid_auto", "Filter for separating solid fractions, automatic cleaning", "Фильтры для отделения твердых фракций с автоматической очисткой", SOLID_SEP_AUTO, True, THIN_DRAIN)
    + filtration("filter_electromagnetic", "Electromagnetic filter", "Фильтры электромагнитные",
                 SOLID_SEP + f'<rect x="40" y="12" width="9" height="18" {LINE}/>', True, THIN_DRAIN)
    + filtration("filter_gas_manual", "Filter for separating gas fractions, manual cleaning", "Фильтры для отделения газовых фракций с ручной очисткой", GAS_SEP, True, None, top_out(False))
    + filtration("filter_gas_auto", "Filter for separating gas fractions, automatic cleaning", "Фильтры для отделения газовых фракций с автоматической очисткой",
                 GAS_SEP + p("M36 27H44L40 21Z", THIN), True, None, top_out(False))
    + [("filter_full_flow", "Full-flow filter", "Фильтры полнопоточные", svg(diamond() + p("M40 20V40", DASH) + open_arrow(40, 40, 0, 1) + p("M8 30H28") + p("M52 30H72"))),
       ("filter_partial_flow", "Partial-flow filter", "Фильтры неполнопоточные", svg(diamond() + p("M40 24V36M34 30H46", THIN) + p("M8 30H28") + p("M52 30H72")))]
)

WATER_SEP = CHORD
WATER_SEP_AUTO = CHORD + p("M36 34H44L40 39Z", THIN)
FILTER_TRAIL = p("M8 30H28") + p("M52 30H72")
DRYER_CHORDS = p("M28 30H52", THIN) + p("M33 26H47", THIN)
CONDITIONER_GAUGE = f'<circle cx="49" cy="30" r="7" {LINE}/>' + p("M46 33L52 27", THIN) + open_arrow(52, 27, 0.7, -0.7)

AIR_TREATMENT = [
    ("moisture_separator_manual", "Moisture separator, manual drain", "Влагоотделитель с ручным спуском", svg(diamond() + WATER_SEP + FILTER_TRAIL + DRAIN)),
    ("moisture_separator_auto", "Moisture separator, automatic drain", "Влагоотделитель с автоматическим спуском", svg(diamond() + WATER_SEP_AUTO + FILTER_TRAIL + DRAIN)),
    ("air_dryer", "Air dryer", "Воздухосушитель", svg(diamond() + DRYER_CHORDS + FLOAT + lead("l", False) + lead("r", False) + DRAIN)),
    ("air_conditioning_unit", "Air conditioning unit", "Установка для кондиционирования воздуха",
     svg(f'<rect x="18" y="19" width="44" height="22" {LINE}/>' + p("M6 30H18M62 30H74") + p("M26 24V36", DASH) + CONDITIONER_GAUGE)),
]


# --- аппараты сушильные (пункт 10) ---
def band(lines, cx=40, cy=30, r=12):
    """Lines parallel to the lower-right edge of the diamond; s is the offset from centre in units of r."""
    return "".join(p(f"M{cx + (s * r - r) / 2:.1f} {cy + (s * r + r) / 2:.1f}L{cx + (s * r + r) / 2:.1f} {cy + (s * r - r) / 2:.1f}", THIN) for s in lines)


DRY_BAND = band((0.15, 0.55))
DRY_DIELECTRIC = band((0.35, 0.7)) + p("M41 38L47 32", THIN)
DRY_LEAD_IN = p("M8 30H28") + tri(21, 30, "r", False)
DRY_LEAD_OUT = p("M8 30H28") + tri(14, 30, "l", False)
DRYERS = [
    ("apparatus_dryer_air", "Drying apparatus, air (gas)", "Аппараты сушильные воздушные (газовые)", svg(diamond() + DRY_BAND + DRY_LEAD_IN + top_out(False))),
    ("apparatus_dryer_vacuum", "Drying apparatus, vacuum", "Аппараты сушильные вакуумные", svg(diamond() + DRY_BAND + DRY_LEAD_OUT + top_out(False))),
    ("apparatus_dryer_dielectric", "Drying apparatus, dielectric", "Аппараты сушильные диэлектрические", svg(diamond() + DRY_DIELECTRIC + top_out(False))),
    ("apparatus_dryer_radiation", "Drying apparatus, radiation", "Аппараты сушильные радиационные",
     svg(diamond() + band((0.15, 0.55)) + top_out(False) + p("M56 46L48 38", THIN) + open_arrow(48, 38, -0.7, -0.7))),
]


# --- питающие и дозирующие устройства (пункт 11) ---
def ends(x1, x2, extra=""):
    return p(f"M{x1} 30H{x2}") + p(f"M{x1} 24V36") + p(f"M{x2} 24V36") + extra


def rotating_feeder():
    arrows = (p("M33 18H21") + open_arrow(21, 18, -1, 0) + p("M52 20V8") + open_arrow(52, 8, 0, -1)
              + p("M28 40V52") + open_arrow(28, 52, 0, 1) + p("M44 44H58") + open_arrow(58, 44, 1, 0))
    return svg(f'<g transform="rotate(-20 40 30)">{p("M32 22H48V38H32Z")}</g>' + arrows)


FEEDERS = [
    ("feeder_traction", "Feeder with traction elements", "Питатели с тяговыми элементами",
     svg(p("M10 30H70") + p("M70 24V36") + p("M34 24V36") + open_arrow(34, 30, 1, 0))),
    ("feeder_rotating", "Feeder without traction elements, rotating", "Питатели без тяговых элементов вращающиеся", rotating_feeder()),
    ("feeder_oscillating", "Feeder without traction elements, oscillating", "Питатели без тяговых элементов качающиеся",
     svg(ends(14, 66, p("M40 30L33 34L47 38L33 42L47 46L40 50")))),
    ("dosing_volumetric", "Volumetric dosing device", "Дозаторы объемные", svg(ends(14, 66) + "".join(p(f"M{x} 27V33", THIN) for x in (27, 40, 53)))),
    ("dosing_weighing", "Weighing dosing device", "Дозаторы весовые", svg(ends(14, 66, p("M28 42L52 20") + open_arrow(52, 20, 0.75, -0.65)))),
]


# --- кристаллизаторы (пункт 12) ---
CRYST_CORE = diamond() + VERT + CHORD + lead("l", True) + lead("r", True)
THIN_DOWN = p("M40 42V54") + open_arrow(40, 54, 0, 1)
CRYSTALLIZERS = [
    ("crystallizer_cooled_liquid", "Crystallizer, liquid-cooled", "Кристаллизаторы с охлаждением жидкостью", svg(CRYST_CORE + coolant(True) + THIN_DOWN)),
    ("crystallizer_cooled_gas", "Crystallizer, air (gas)-cooled", "Кристаллизаторы с охлаждением воздухом (газом)", svg(CRYST_CORE + coolant(False) + THIN_DOWN)),
    ("crystallizer_vacuum", "Vacuum crystallizer", "Кристаллизаторы вакуумные", svg(CRYST_CORE + p("M40 18V6") + tri(40, 8, "u", False) + THIN_DOWN)),
    ("crystallizer_pressure", "Pressure crystallizer", "Кристаллизаторы давления", svg(CRYST_CORE + p("M40 18V6") + tri(40, 15, "d", False) + THIN_DOWN)),
]


# --- аппараты с механическими перемешивающими устройствами (пункт 13) ---
SHAFT_OPEN = p("M40 6V28") + p("M35 28H45")
SHAFT_CLOSED = p("M40 8V38") + p("M35 38H45")
VESSEL_OPEN = p("M22 8V32H58V8")
STUBS = {
    "liquid": p("M30 32V54") + p("M50 32V54") + tri(30, 43, "u", True) + tri(50, 50, "d", True),
    "gas": p("M30 32V54") + p("M50 32V54") + tri(30, 43, "u", False) + tri(50, 50, "d", False),
    "electric": f'<rect x="35" y="32" width="10" height="6" {LINE}/>',
}


def closed_vessel(left, right):
    return svg(paths("M26 16H54", "M26 44H54", left, right) + SHAFT_CLOSED)


STIRRERS = [
    ("stirrer_open", "Paddle, propeller, turbine stirrer for liquids, atmospheric pressure", "Мешалки лопастные, пропеллерные, турбинные и т. п. для жидких сред под атмосферным давлением", svg(VESSEL_OPEN + SHAFT_OPEN)),
    ("stirrer_over_pressure", "Stirrer for liquids, internal pressure above atmospheric", "Мешалки лопастные, пропеллерные, турбинные и т. п. для жидких сред с внутренним давлением выше атмосферного", closed_vessel("M26 16Q14 30 26 44", "M54 16Q66 30 54 44")),
    ("stirrer_vacuum", "Stirrer for liquids, internal pressure below atmospheric", "Мешалки лопастные, пропеллерные, турбинные и т. п. для жидких сред с внутренним давлением ниже атмосферного", closed_vessel("M26 16Q34 30 26 44", "M54 16Q46 30 54 44")),
    ("stirrer_alternating_pressure", "Stirrer for liquids, internal pressure alternately above and below atmospheric", "Мешалки лопастные, пропеллерные, турбинные и т. п. для жидких сред с внутренним давлением выше и ниже атмосферного попеременно", closed_vessel("M26 16Q14 30 26 44", "M54 16Q46 30 54 44")),
    ("stirrer_open_heated_liquid", "Stirrer under atmospheric pressure, heated by liquid", "Мешалки под атмосферным давлением с обогревом жидкостью", svg(VESSEL_OPEN + SHAFT_OPEN + STUBS["liquid"])),
    ("stirrer_open_heated_gas", "Stirrer under atmospheric pressure, heated by air (gas)", "Мешалки под атмосферным давлением с обогревом воздухом (газом)", svg(VESSEL_OPEN + SHAFT_OPEN + STUBS["gas"])),
    ("stirrer_open_heated_electric", "Stirrer under atmospheric pressure, electrically heated", "Мешалки под атмосферным давлением с обогревом электрическим током", svg(VESSEL_OPEN + SHAFT_OPEN + STUBS["electric"])),
    ("stirrer_screw", "Screw, anchor, roller, plate stirrer for pasty materials", "Мешалки шнековые, якорные, валковые, тарельчатые и т. п. для пастообразных материалов",
     svg(f'<rect x="18" y="17" width="44" height="26" {LINE}/>' + p("M8 30H18M62 30H72") + p("M24 30L28 25L32 35L36 25L40 35L44 25L48 35L52 25L56 30"))),
    ("stirrer_bulk", "Stirrer for bulk materials", "Мешалки для сыпучих материалов", svg(f'<rect x="14" y="20" width="52" height="20" {LINE}/>' + f'<rect x="14" y="20" width="5" height="20" fill="#000"/><rect x="61" y="20" width="5" height="20" fill="#000"/>')),
]

CENTRIFUGE_BODY = '<rect x="18" y="14" width="44" height="22" stroke="#000" stroke-width="2" fill="none"/><rect x="18" y="14" width="5" height="22" fill="#000"/><rect x="57" y="14" width="5" height="22" fill="#000"/>'
CENTRIFUGES = [
    ("centrifuge_settling", "Centrifuge, settling", "Центрифуги отстойники", svg(CENTRIFUGE_BODY + p("M40 36V52") + tri(40, 54, "d", True))),
    ("centrifuge_filtering", "Centrifuge, filtering", "Центрифуги фильтрующие", svg(CENTRIFUGE_BODY + "".join(p(f"M{x} 14V36", THIN) for x in (30, 40, 50)) + p("M40 36V52") + tri(40, 54, "d", True))),
    ("supercentrifuge", "Supercentrifuge (liquid separator)", "Сверхцентрифуги (сепараторы жидкостные)",
     svg(diamond() + lead("l", True) + lead("r", True) + p("M40 42V54") + open_arrow(40, 54, 0, 1))),
]

GRANULATOR = ('<defs><clipPath id="d"><path d="M28 30L40 18L52 30L40 42Z"/></clipPath></defs><g clip-path="url(#d)">'
              + "".join(p(f"M{22 + 3 * i} 48L{44 + 3 * i} 12", THIN) for i in range(0, 14)) + "</g>")
SOLIDS = [
    ("grinder", "Solids grinding apparatus", "Аппараты для измельчения твердых материалов", svg(diamond() + CHORD + paths("M34 24L46 36", "M46 24L34 36", style=THIN))),
    ("sorter", "Solids sorting apparatus", "Аппараты для сортировки твердых материалов", svg(diamond() + "".join(p(f"M{28 + abs(y - 30)} {y}H{52 - abs(y - 30)}", DASH) for y in (24, 30, 36)))),
    ("granulator", "Granulator", "Грануляторы", svg(diamond(style='stroke="#000" stroke-width="2" fill="none"') + GRANULATOR)),
]


MIXERS = [
    ("mixer_gas", "Gas mixer", "Смесители газовый",
     svg(diamond(r=11) + p("M8 30H29M51 30H72") + tri(22, 30, "r", False) + tri(58, 30, "l", False) + p("M40 19V6") + tri(40, 8, "u", False))),
    ("mixer_liquid", "Liquid mixer", "Смесители жидкостный",
     svg(diamond(r=11) + p("M8 30H29M51 30H72") + tri(22, 30, "r", True) + tri(58, 30, "l", True) + p("M40 41V55") + tri(40, 53, "d", True))),
    ("mixer_liquid_gas", "Liquid and gas mixer", "Смесители жидкости и газа",
     svg(diamond(r=11) + p("M8 30H29M51 30H72") + tri(22, 30, "r", True) + tri(58, 30, "l", False) + p("M40 41V55") + tri(40, 53, "d", True))),
]

ALL = (HEAT_EXCHANGERS + HEATERS + THERMOREGULATORS + CONDENSERS + MISC + EVAPORATORS + COLUMN + FILTERS
       + AIR_TREATMENT + DRYERS + FEEDERS + CRYSTALLIZERS + STIRRERS + CENTRIFUGES + SOLIDS + MIXERS)

if __name__ == "__main__":
    store("GOST 2.793", "gost", [(c, en, ru, CATEGORY, d) for c, en, ru, d in ALL], NOTE)

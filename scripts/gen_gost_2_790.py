"""ГОСТ 2.790-74 «Аппараты колонные» — собственные рисунки по скану стандарта."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_symbols import LINE, store

STANDARD = "GOST 2.790"
CATEGORY = "Колонные аппараты"
NOTE = "собственный рисунок по скану ГОСТ 2.790-74"
W, H = 60, 120
CX = 30
HALF = 21  # полуширина корпуса / ширина тарелки 42


def sv(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W * 2}" height="{H * 2}">{body}</svg>'


def path(d):
    return f'<path d="{d}" {LINE}/>'


def fill_path(d):
    return f'<path d="{d}" fill="#000" stroke="none"/>'


def arrow(x1, y1, x2, y2, head=4):
    """Линия со сплошной стрелкой на конце (x2, y2); направление вертикальное или горизонтальное."""
    if x1 == x2:
        s = 1 if y2 > y1 else -1
        tip = f"M{x2} {y2}l{-head / 2} {-s * head}h{head}z"
    else:
        s = 1 if x2 > x1 else -1
        tip = f"M{x2} {y2}l{-s * head} {-head / 2}v{head}z"
    return path(f"M{x1} {y1}L{x2} {y2}") + fill_path(tip)


# --- знаки внутри круга, центр (0,0), круг радиуса 9, толщина 1.3 при масштабе 1.55 ---
GLYPH_LINE = 'stroke="#000" stroke-width="1.3" fill="none"'
GLYPHS = {
    "bubble_cap": "M-6 5H-3V-3H3V5H6",
    "jet": "M-9 0H-4L3 4M3 4H9",
    "valve": "M-9 0H-5M5 0H9M-5 -3H5M0 -3V7",
    "valve_flow": "M-9 0H-5M5 0H9M0 7V-4M-3 -2L2 -5",
    "s_element": "M-6 -5H-4V4H4V-5H6M-1.5 -5V1H1.5V-5",
    "sieve": "M-9 0H-5M-2 0H2M5 0H9",
    "sieve_baffle": "M-3 -6L3 -4M-4 -3L2 -1M-5 0L1 2M-6 3L0 5M-1 -1L5 1",
    "sieve_valve": "M-9 0H9M-7 -2L-3 -4M-7 -4L-3 -2M1 -2L5 -4M1 -4L5 -2",
    "louver": "M-9 0H-3M-3 0L0 -3M0 0L3 -3M3 0L6 -3H9M-5 -1L-3 -4",
    "vortex": "M-3 -6V6M3 -6V6M-3 -6L3 6M3 -6L-3 6",
}
GRATE = (
    f'<path d="M-3 -5V4M3 5V-4M-6 0H6" {GLYPH_LINE}/>'
    '<path d="M-3 6L-5 2H-1zM3 -6L1 -2H5z" fill="#000"/>'
)


def glyph_in_circle(kind, cx, cy):
    inner = GRATE if kind == "grate" else f'<path d="{GLYPHS[kind]}" {GLYPH_LINE}/>'
    return f'<circle cx="{cx}" cy="{cy}" r="14" {LINE}/><g transform="translate({cx} {cy}) scale(1.55)">{inner}</g>'


# --- таблица 1: контактные устройства (тарелки — горизонтальные линии) ---
def tray_lines(ys, x0=9, x1=51):
    return "".join(path(f"M{x0} {y}H{x1}") for y in ys)


def tray(kind=None):
    if kind is None:
        return sv(tray_lines([14 + 13 * i for i in range(6)]))
    return sv(tray_lines([8, 21, 61, 74]) + glyph_in_circle(kind, CX, 41))


# --- таблица 2: корпуса колонн, центр глифа (CX, 57) ---
CY = 57
END, LINE_OFF, BOX = 50, 35, 19


def housing(style="flat", glyph=None):
    xl, xr = CX - HALF, CX + HALF
    top, bot = CY - END, CY + END
    if style == "peak":
        outline = f"M{xl} {top + 9}L{CX} {top - 0}L{xr} {top + 9}V{bot - 9}L{CX} {bot}L{xl} {bot - 9}Z"
    elif style == "notch":
        outline = f"M{xl} {top - 2}L{CX} {top + 6}L{xr} {top - 2}V{bot + 2}L{CX} {bot - 6}L{xl} {bot + 2}Z"
    else:
        outline = f"M{xl} {top}H{xr}V{bot}H{xl}Z"
    lines = "".join(path(f"M{xl} {CY + o}H{xr}") for o in (-LINE_OFF, -BOX, BOX, LINE_OFF))
    body = path(outline) + lines
    return sv(body + (glyph_in_circle(glyph, CX, CY) if glyph else ""))


def plain_box(top, bottom, inner):
    xl, xr = CX - HALF, CX + HALF
    return path(f"M{xl} {top}H{xr}V{bottom}H{xl}Z") + inner


def hlines(ys, x0=CX - HALF, x1=CX + HALF):
    return "".join(path(f"M{x0} {y}H{x1}") for y in ys)


def tray_column_general():
    top, step = 6, 14.9
    return sv(plain_box(top, top + 7 * step, hlines([top + step * i for i in range(1, 7)])))


def pulsation():
    top, bot = 5, 108
    arrows = arrow(CX, 56, CX, 92, 8) + arrow(CX, 56, CX, 20, 8)
    return sv(plain_box(top, bot, arrows))


def packed(kind, style):
    xl, xr = CX - HALF, CX + HALF
    top, bot = 7, 112
    if kind == "random":
        top, bot = 8, 112
        inner = hlines([29, 91]) + path(f"M{xl} 29L{xr} 91M{xr} 29L{xl} 91")
        return sv(plain_box(top, bot, inner))
    outline = f"M{xl} {top - 2}L{CX} {top + 6}L{xr} {top - 2}V{bot + 2}L{CX} {bot - 6}L{xl} {bot + 2}Z"
    grid = hlines([27, 48, 69, 90])
    grid += "".join(path(f"M{x} 27V90") for x in (CX - 7, CX + 7))
    return sv(path(outline) + grid)


def rotor_blades(top, bottom, ys):
    shaft = path(f"M{CX} {top}V{bottom}")
    arc = path(f"M{CX - 12} {top + 8}Q{CX - 2} {top - 2} {CX + 8} {top + 5}") + fill_path(
        f"M{CX + 10} {top + 8}l-5 -1l2 -5z")
    return shaft + arc + "".join(path(f"M{CX - 7} {y}H{CX + 7}") for y in ys)


def column_rotor():
    xl, xr = CX - HALF, CX + HALF
    top, bot = 28, 112
    ys = [top + 16.5 * i for i in range(1, 5)]
    blades = rotor_blades(8, bot - 14, [y - 7 for y in ys] + [bot - 14])
    return sv(plain_box(top, bot, hlines(ys)) + blades)


def rotor_element():
    ys = [34 + 8.5 * i for i in range(9)]
    return sv(rotor_blades(14, ys[-1], ys))


def packing_single(kind):
    xl, xr = CX - HALF, CX + HALF
    top, bot = 28, 88
    if kind == "random":
        inner = path(f"M{xl} {top}L{xr} {bot}M{xr} {top}L{xl} {bot}")
    else:
        inner = hlines([48, 68]) + "".join(path(f"M{x} {top}V{bot}") for x in (CX - 7, CX + 7))
    return sv(plain_box(top, bot, inner))


T1 = "Устройства тарельчатые контактные: "
T2 = "Аппараты колонные тарельчатые "
ROWS = [
    ("tray_general", "Contact tray, general", T1 + "общее обозначение", tray()),
    ("tray_bubble_cap", "Bubble-cap tray", T1 + "тарелки колпачковые", tray("bubble_cap")),
    ("tray_jet", "Jet tray", T1 + "тарелки струйные", tray("jet")),
    ("tray_valve", "Valve tray", T1 + "тарелки клапанные", tray("valve")),
    ("tray_valve_flow", "Direct-flow valve tray", T1 + "тарелки клапанные прямоточные", tray("valve_flow")),
    ("tray_s_element", "S-element tray", T1 + "тарелки из S-образных элементов", tray("s_element")),
    ("tray_sieve", "Sieve tray", T1 + "тарелки ситчатые", tray("sieve")),
    ("tray_sieve_baffle", "Sieve tray with baffle elements", T1 + "тарелки ситчатые с отбойными элементами", tray("sieve_baffle")),
    ("tray_sieve_valve", "Sieve-valve tray", T1 + "тарелки ситчато-клапанные", tray("sieve_valve")),
    ("tray_louver_valve", "Louver-valve tray", T1 + "тарелки жалюзийно-клапанные", tray("louver")),
    ("tray_grid", "Grid (through-slot) tray", T1 + "тарелки решетчато-провальные", tray("grate")),
    ("tray_vortex", "Vortex tray", T1 + "тарелки вихревые", tray("vortex")),
    ("packing_random", "Random packing", "Устройства насадочные контактные: насадки насыпные", packing_single("random")),
    ("packing_regular", "Regular packing", "Устройства насадочные контактные: насадки регулярные", packing_single("regular")),
    ("column_rotor_element", "Column rotor", "Ротор колонны", rotor_element()),
    ("col_pulsation", "Pulsation column", "Аппараты колонные пульсационные", pulsation()),
    ("col_tray_general", "Tray column, general", T2 + "общее обозначение", tray_column_general()),
    ("col_tray_bubble_cap", "Tray column with bubble-cap trays", T2 + "с колпачковыми тарелками", housing("flat", "bubble_cap")),
    ("col_tray_jet_overpressure", "Tray column with jet trays above atmospheric pressure", T2 + "со струйными тарелками под давлением выше атмосферного", housing("peak", "jet")),
    ("col_tray_valve_vacuum", "Tray column with valve trays below atmospheric pressure", T2 + "с клапанными тарелками под давлением ниже атмосферного", housing("notch", "valve")),
    ("col_tray_valve_flow", "Tray column with direct-flow valve trays", T2 + "с клапанными прямоточными тарелками", housing("flat", "valve_flow")),
    ("col_tray_s_element", "Tray column with S-element trays", T2 + "с тарелками из S-образных элементов", housing("flat", "s_element")),
    ("col_tray_sieve", "Tray column with sieve trays", T2 + "с ситчатыми тарелками", housing("flat", "sieve")),
    ("col_tray_sieve_baffle", "Tray column with sieve trays with baffle elements", T2 + "с ситчатыми тарелками с отбойными элементами", housing("flat", "sieve_baffle")),
    ("col_tray_sieve_valve", "Tray column with sieve-valve trays at atmospheric pressure", T2 + "с ситчато-клапанными тарелками под атмосферным давлением", housing("flat", "sieve_valve")),
    ("col_tray_sieve_valve_vacuum", "Tray column with sieve-valve trays below atmospheric pressure", T2 + "с ситчато-клапанными тарелками под давлением ниже атмосферного", housing("notch", "sieve_valve")),
    ("col_tray_louver_valve", "Tray column with louver-valve trays", T2 + "с жалюзийно-клапанными тарелками", housing("flat", "louver")),
    ("col_tray_grid", "Tray column with grid trays", T2 + "с решетчато-провальными тарелками", housing("flat", "grate")),
    ("col_tray_vortex", "Tray column with vortex trays", T2 + "с вихревыми тарелками", housing("flat", "vortex")),
    ("col_packed_random", "Packed column with random packing", "Аппараты колонные насадочные: с насыпной насадкой", packed("random", "flat")),
    ("col_packed_regular_vacuum", "Packed column with regular packing below atmospheric pressure", "Аппараты колонные насадочные: с регулярной насадкой под давлением ниже атмосферного", packed("regular", "notch")),
    ("col_rotor", "Rotor column", "Аппарат колонный роторный", column_rotor()),
]

if __name__ == "__main__":
    store(STANDARD, "gost_2_790", [(c, e, r, CATEGORY, s) for c, e, r, s in ROWS], NOTE)

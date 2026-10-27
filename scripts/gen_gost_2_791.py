"""ГОСТ 2.791-74 «Отстойники и фильтры» — собственные рисунки по скану стандарта.

Координаты в пикселях страницы скана (повёрнутой, ширина 2000); wrap() уменьшает их вдвое.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_symbols import store

STANDARD = "GOST 2.791"
CATEGORY = "Отстойники и фильтры"
NOTE = "собственный рисунок по скану ГОСТ 2.791-74"
STROKE = 'stroke="#000" stroke-width="4" fill="none" stroke-linejoin="round"'
HEAD_LEN, HEAD_HALF = 18, 8


def wrap(body, x0, y0, x1, y1, clip=""):
    w, h = (x1 - x0) / 2, (y1 - y0) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * 2}" height="{h * 2}">'
            f'{clip}<g transform="scale(0.5) translate({-x0} {-y0})">{body}</g></svg>')


def p(d):
    return f'<path d="{d}" {STROKE}/>'


def dash(d):
    return f'<path d="{d}" stroke="#000" stroke-width="3" fill="none" stroke-dasharray="14 10"/>'


def rect(x0, y0, x1, y1):
    return p(f"M{x0} {y0}H{x1}V{y1}H{x0}Z")


def hatch_fill(x0, y0, x1, y1):
    return f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#000"/>'


def arrow(x1, y1, x2, y2):
    """Линия от (x1,y1) со сплошной стрелкой, остриё в (x2,y2)."""
    angle = math.atan2(y2 - y1, x2 - x1)
    ux, uy = math.cos(angle), math.sin(angle)
    bx, by = x2 - ux * HEAD_LEN, y2 - uy * HEAD_LEN
    head = f"M{x2} {y2}L{bx - uy * HEAD_HALF:.1f} {by + ux * HEAD_HALF:.1f}L{bx + uy * HEAD_HALF:.1f} {by - ux * HEAD_HALF:.1f}z"
    return p(f"M{x1} {y1}L{bx:.1f} {by:.1f}") + f'<path d="{head}" fill="#000"/>'


def curved_arrow(x1, y1, cx, cy, x2, y2):
    angle = math.atan2(y2 - cy, x2 - cx)
    ux, uy = math.cos(angle), math.sin(angle)
    hl, hh = 14, 6
    bx, by = x2 - ux * hl, y2 - uy * hl
    head = f"M{x2} {y2}L{bx - uy * hh:.1f} {by + ux * hh:.1f}L{bx + uy * hh:.1f} {by - ux * hh:.1f}z"
    return p(f"M{x1} {y1}Q{cx} {cy} {bx:.1f} {by:.1f}") + f'<path d="{head}" fill="#000"/>'


def spiral(cx, cy, turns=2.5, r_max=24):
    pts = [(cx + r_max * t / turns / 2 / math.pi * math.cos(t), cy + r_max * t / turns / 2 / math.pi * math.sin(t))
           for t in (i * 0.25 for i in range(int(turns * 2 * math.pi / 0.25) + 1))]
    return p("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts))


def dots(x0, y0, x1, y1, step=9):
    return "".join(f'<circle cx="{x + (step / 2 if j % 2 else 0)}" cy="{y}" r="1.6" fill="#000"/>'
                   for j, y in enumerate(range(y0 + 5, y1, step // 2 + 1))
                   for x in range(x0 + 5, x1 - 3, step))


def meshed(x0, y0, x1, y1):
    cid = "mesh"
    clip = f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>'
    lines = "".join(f"M{x0 + i} {y0}l{y1 - y0} {y1 - y0}M{x0 + i} {y0}l{-(y1 - y0)} {y1 - y0}" for i in range(0, x1 - x0 + 40, 7))
    return clip + f'<g clip-path="url(#{cid})"><path d="{lines}" stroke="#000" stroke-width="2" fill="none"/></g>' + rect(x0, y0, x1, y1)


# --- таблица 1: корпуса и перегородки ---
def partition_fabric(x0=731, y0=1042, x1=812, y1=1068):
    squares = "".join(hatch_fill(x, y, x + 6, y + 6) for x, y in
                      [(741, 1047), (759, 1047), (777, 1047), (795, 1047), (750, 1057), (768, 1057), (786, 1057)])
    return rect(x0, y0, x1, y1) + squares


def partition_mesh():
    return meshed(731, 1127, 812, 1153)


def partition_porous():
    return rect(731, 1214, 812, 1243) + dots(733, 1214, 810, 1243, 8)


def partition_slotted():
    return rect(1553, 244, 1630, 275) + p("M1553 252H1630M1553 260H1630M1553 267H1630")


def basin_body():
    return p("M711 263L742 277H820V257M832 257V269H820")


BASIN_BODY = "M1522 557L1568 570H1618V540M1630 540V552H1618"
CHAMBER_BODY = "M741 347V400L770 432L797 400V347"
THICKENER_BODY = "M743 505V540L770 568L797 540V505"
DRUM_BODY = "M743 622A27 27 0 0 0 797 622"
HYDROCYCLONE_BODY = "M743 798H800V822L772 860L743 822ZM743 822H800"
SEPARATOR_BODY = "M727 902H817V945L772 968L727 945Z"


def belt_body():
    return p("M714 727H830A10 10 0 0 1 830 747H714A10 10 0 0 1 714 727Z") + (
        '<circle cx="714" cy="737" r="6" ' + STROKE + '/><circle cx="830" cy="737" r="6" ' + STROKE + '/>')


# --- таблица 2: аппараты ---
def settler_basin():
    return p(BASIN_BODY) + arrow(1548, 517, 1548, 550) + p("M1640 540V525H1663") + arrow(1625, 538, 1695, 538)


def settler_single():
    return (p("M1562 653V705L1590 740L1618 705V653") + arrow(1598, 640, 1598, 685) +
            arrow(1618, 663, 1668, 663) + arrow(1590, 725, 1590, 790))


def settler_multi():
    shape = p("M1535 905V953L1559 985V1010H1614V985L1590 947L1559 985M1590 947V929M1614 985L1641 953V905")
    return (shape + arrow(1552, 872, 1552, 915) + arrow(1641, 904, 1695, 904) +
            arrow(1614, 1010, 1695, 1010) + '<circle cx="1614" cy="1010" r="4" fill="#000"/>')


def rake_thickener(tiers):
    body = p("M1560 1140V1195L1588 1222L1616 1195V1130")
    rake = p("M1588 1128V1215") + curved_arrow(1572, 1142, 1590, 1130, 1608, 1142)
    zigzag = "".join(p(f"M1565 {y}l7 -7l7 7l7 -7l7 7l7 -7l7 7l7 -7l7 7") for y in tiers)
    return (body + rake + zigzag + arrow(1568, 1105, 1568, 1142) + arrow(1616, 1160, 1668, 1160) +
            arrow(1588, 1222, 1588, 1270))


def rake_one():
    return rake_thickener([1203])


def rake_two():
    body = p("M728 300V345L757 362L786 345V300")
    rake = p("M757 268V362") + curved_arrow(742, 282, 758, 270, 775, 284)
    zigzag = "".join(p(f"M733 {y}l6 -6l6 6l6 -6l6 6l6 -6l6 6l6 -6l6 6") for y in (318, 336))
    return (body + rake + zigzag + arrow(737, 255, 737, 297) + arrow(786, 307, 833, 307) +
            arrow(786, 330, 833, 330) + arrow(757, 362, 757, 412))


def sand_filter():
    return (p("M730 535V585H783V535") + dots(731, 562, 782, 584, 7) + p("M730 560H783") +
            arrow(757, 505, 757, 545) + arrow(757, 585, 757, 635))


def hydrocyclone():
    return (p("M731 785H783V808L757 845L731 808ZM731 808H783") +
            arrow(683, 797, 730, 797) + p("M757 785V752H800") + arrow(780, 752, 830, 752) + arrow(757, 840, 757, 890))


def drum_filter():
    return (p("M752 1000a20 20 0 1 0 0.1 0") + p("M708 1000A44 44 0 0 0 796 1000") +
            curved_arrow(736, 982, 760, 970, 782, 982) + arrow(722, 958, 722, 1000) +
            arrow(752, 1040, 752, 1092) + arrow(803, 993, 850, 1005))


def trough_filter(left, right, base_y, shaft_x):
    troughs = p(f"M{left} {base_y - 22}V{base_y}H{left + 33}V{base_y - 22}") + p(f"M{right} {base_y - 22}V{base_y}H{right + 35}V{base_y - 22}")
    axis = p(f"M{left} {base_y}H{right + 35}") + p(f"M{shaft_x} {base_y - 45}V{base_y + 12}") + p(f"M{shaft_x - 12} {base_y + 12}H{shaft_x + 12}")
    return troughs + axis + curved_arrow(shaft_x - 14, base_y - 35, shaft_x, base_y - 50, shaft_x + 18, base_y - 38)


def plate_filter():
    return (trough_filter(685, 788, 1203, 752) + arrow(703, 1148, 703, 1182) +
            p("M815 1182V1165H845") + arrow(830, 1165, 868, 1165) + arrow(752, 1215, 752, 1260))


def carousel_filter():
    body = p("M1508 292V308H1640M1508 292H1540V308") + p("M1608 308V325H1640V308") + p("M1573 262V320") + p("M1561 320H1585")
    return (body + curved_arrow(1558, 275, 1573, 262, 1595, 275) + arrow(1525, 255, 1525, 290) +
            arrow(1575, 328, 1575, 365) + arrow(1625, 330, 1625, 365))


def stadium(x0, y0, x1, y1):
    r = (y1 - y0) / 2
    return p(f"M{x0 + r} {y0}H{x1 - r}A{r} {r} 0 0 1 {x1 - r} {y1}H{x0 + r}A{r} {r} 0 0 1 {x0 + r} {y0}Z")


def bucket_conveyor():
    return (dash("M1520 455H1640A50 40 0 0 1 1640 535H1520A50 40 0 0 1 1520 455Z") +
            p("M1522 485H1628V507H1522Z") + '<circle cx="1522" cy="495" r="10" ' + STROKE + '/><circle cx="1628" cy="495" r="10" ' + STROKE + '/>' +
            p("M1535 485L1545 465H1565L1575 485M1580 485L1590 468H1605") +
            arrow(1530, 422, 1530, 470) + arrow(1580, 508, 1580, 572) + arrow(1628, 520, 1628, 572) +
            curved_arrow(1500, 480, 1494, 505, 1508, 525))


def belt_filter():
    return (stadium(1508, 692, 1648, 728) + stadium(1516, 699, 1640, 721) + '<circle cx="1523" cy="711" r="8" ' + STROKE + '/><circle cx="1633" cy="711" r="8" ' + STROKE + '/>' +
            arrow(1538, 632, 1538, 682) + arrow(1580, 712, 1580, 770) + arrow(1660, 718, 1695, 745) +
            curved_arrow(1508, 695, 1495, 710, 1508, 725))


def druk_filter():
    body = p("M1555 842L1562 830H1604L1610 842V965L1583 992L1555 965Z") + p("M1555 938H1610M1555 946H1610")
    return (body + arrow(1515, 850, 1555, 850) + p("M1598 938V912H1630") + arrow(1620, 912, 1655, 912) + arrow(1583, 990, 1583, 1022))


def nutsch_filter():
    body = p("M1557 1098V1230L1583 1240L1610 1230V1213H1557M1557 1219H1610M1598 1100V1213")
    return body + arrow(1583, 1058, 1583, 1100) + p("M1598 1106H1620") + arrow(1598, 1106, 1655, 1106) + arrow(1583, 1240, 1583, 1272)


def hex_body(x0, y0, x1, y1, cut=13):
    ym = (y0 + y1) / 2
    return p(f"M{x0 + cut} {y0}H{x1 - cut}L{x1} {ym}L{x1 - cut} {y1}H{x0 + cut}L{x0} {ym}Z")


def horizontal_leaf(inner, y0=258):
    body = hex_body(697, y0, 845, y0 + 54)
    inside = (rect(720, y0 + 12, 825, y0 + 44) if inner == "long" else
              "".join(p(f"M{x} {y0 + 10}V{y0 + 42}") for x in (733, 760, 786, 812)))
    return (body + inside + arrow(657, y0 + 10, 697, y0 + 10) + arrow(697, y0 + 40, 657, y0 + 40) +
            arrow(771, y0 + 42, 771, y0 + 97))


def vertical_leaf():
    body = p("M742 628L752 607H790L800 628V732L782 750H760L742 732Z")
    return (body + "".join(p(f"M{x} 628V738") for x in (752, 761, 771, 780, 790)) +
            arrow(693, 620, 742, 620) + p("M790 607V590H820") + arrow(800, 590, 852, 590) + arrow(771, 750, 771, 797))


def disc_filter(pressure):
    base = 925 if not pressure else 1140
    parts = p(f"M684 {base}H888") + arrow(684, base, 628, base) + p(f"M684 {base - 15}V{base + 15}")
    if pressure:
        parts += hex_body(695, 1112, 848, 1168) + "".join(p(f"M{x} 1127V1153") for x in (730, 755, 780, 805))
        parts += arrow(825, 1060, 825, 1110) + arrow(716, 1168, 716, 1215)
    else:
        parts += p("M705 925V955H838V925") + "".join(p(f"M{x} 900V940") for x in (730, 755, 780, 805, 830))
        parts += arrow(826, 845, 826, 890) + arrow(771, 955, 771, 1002)
    return parts + curved_arrow(866, base - 22, 884, base, 866, base + 22)


def disc_filter_horizontal():
    body = p("M1565 330L1575 312H1607L1617 330V445L1600 462H1582L1565 445Z")
    discs = "".join(p(f"M1573 {y}H1610") for y in (345, 372, 398, 425))
    shaft = p("M1590 262V462") + curved_arrow(1580, 275, 1595, 262, 1610, 278)
    return (body + discs + shaft + arrow(1508, 328, 1562, 328) + arrow(1590, 462, 1590, 528) + arrow(1608, 477, 1608, 505))


def corrugated_filter():
    return (rect(1565, 637, 1620, 773) + rect(1578, 650, 1608, 760) + p("M1572 658H1614M1572 752H1614") +
            arrow(1593, 590, 1593, 635) + arrow(1593, 773, 1593, 830))


def cartridge_filter():
    body = p("M1565 925L1590 908H1595L1620 925V1060L1593 1085L1565 1060Z") + rect(1572, 945, 1612, 1045)
    cartridge = "".join(p(f"M{x} 945V1045") for x in (1581, 1590, 1599, 1608 - 4))
    return (body + cartridge + arrow(1510, 957, 1565, 957) + arrow(1612, 930, 1670, 930) + arrow(1593, 1085, 1593, 1115))


def press_vertical():
    return (rect(1527, 1172, 1657, 1226) + "".join(p(f"M{x} 1172V1226") for x in (1550, 1566, 1582, 1598, 1614, 1630)) +
            arrow(1480, 1182, 1527, 1182) + arrow(1527, 1217, 1480, 1217) + arrow(1592, 1205, 1592, 1268))


def press_horizontal():
    column = rect(742, 257, 793, 390) + p("M742 268H793M742 277H793M742 372H793M742 381H793M742 305H793M742 350H793")
    left = curved_arrow(742, 310, 716, 316, 716, 352)
    right = p("M793 285H836V360H793") + curved_arrow(793, 312, 818, 318, 818, 352)
    return column + left + right + arrow(766, 392, 766, 436) + arrow(748, 436, 748, 392)


def pentagon(x0, y0, w=86):
    return p(f"M{x0} {y0}H{x0 + w}V{y0 + 42}L{x0 + w / 2} {y0 + 70}L{x0} {y0 + 42}Z")


def separator(x0, y0, inside, extra="", first_in=10):
    """Фильтр-сепаратор: корпус-пятиугольник, вход слева, выход справа, слив вниз."""
    body = pentagon(x0, y0) + inside
    arrows = arrow(x0 - 40, y0 + first_in, x0, y0 + first_in) + arrow(x0 + 86, y0 + 46, x0 + 124, y0 + 46)
    return body + arrows + extra


def separator_one():
    return separator(726, 495, rect(737, 508, 800, 538), extra=arrow(768, 565, 768, 612))


def separator_two():
    inside = rect(735, 697, 763, 730) + rect(773, 697, 800, 730)
    extra = arrow(753, 642, 753, 686) + arrow(768, 745, 768, 800) + arrow(792, 800, 792, 745)
    return separator(724, 686, inside, extra=extra, first_in=8)


def separator_three():
    inside = "".join(rect(x, 843, x + 15, 878) for x in (736, 757, 779))
    return separator(724, 832, inside, extra=arrow(768, 900, 768, 945))


def separator_static():
    cx, y0 = 1590, 258
    inside = p(f"M{cx} {y0 + 12}V{y0 + 55}") + "".join(p(f"M{cx - w} {y0 + 12 + i * 12}L{cx} {y0 + 20 + i * 12}L{cx + w} {y0 + 12 + i * 12}") for i, w in enumerate((18, 20, 15)))
    return separator(1547, y0, inside, extra=arrow(1590, 325, 1590, 372))


def separator_countercurrent():
    return separator(1547, 410, rect(1558, 421, 1583, 455) + rect(1595, 421, 1622, 455), extra=arrow(1590, 478, 1590, 530))


def separator_basket():
    return separator(1547, 588, rect(1556, 598, 1625, 636) + rect(1566, 608, 1615, 628), extra=arrow(1590, 655, 1590, 710))


def separator_spiral():
    return separator(1547, 755, spiral(1590, 783), extra=arrow(1590, 822, 1590, 872))


ROWS = [
    ("basin_body", "Basin (pond) body", "Бассейн", wrap(basin_body(), 700, 245, 845, 290)),
    ("chamber_body", "Chamber body", "Камера", wrap(p(CHAMBER_BODY), 725, 335, 815, 445)),
    ("thickener_body", "Thickener body", "Корпус сгустителя", wrap(p(THICKENER_BODY), 725, 495, 815, 580)),
    ("drum_vacuum_filter_body", "Drum vacuum filter body", "Корпуса барабанных вакуумных фильтров", wrap(p(DRUM_BODY), 725, 610, 815, 660)),
    ("belt_filter_body", "Belt filter body", "Корпус ленточного фильтра", wrap(belt_body(), 695, 715, 850, 760)),
    ("hydrocyclone_body", "Hydrocyclone body", "Корпус гидроциклона", wrap(p(HYDROCYCLONE_BODY), 725, 788, 815, 870)),
    ("separator_filter_body", "Body of separator, basket and spiral filters", "Корпусы фильтров-сепараторов, фильтров корзинчатого и спирального", wrap(p(SEPARATOR_BODY), 715, 890, 830, 980)),
    ("partition_fabric", "Filter partition: fabric", "Фильтрующие перегородки: тканевые", wrap(partition_fabric(), 720, 1032, 825, 1078)),
    ("partition_mesh", "Filter partition: mesh", "Фильтрующие перегородки: сетчатые", wrap(partition_mesh(), 720, 1117, 825, 1163)),
    ("partition_porous", "Filter partition: porous", "Фильтрующие перегородки: пористые", wrap(partition_porous(), 720, 1204, 825, 1253)),
    ("partition_slotted", "Filter partition: slotted", "Фильтрующие перегородки: щелевые", wrap(partition_slotted(), 1540, 235, 1645, 285)),
    ("settler_basin", "Basin settler", "Отстойник бассейновый", wrap(settler_basin(), 1510, 505, 1710, 585)),
    ("settler_single_chamber", "Single-chamber settler", "Отстойник однокамерный", wrap(settler_single(), 1545, 630, 1690, 800)),
    ("settler_multi_chamber", "Multi-chamber settler", "Отстойник многокамерный", wrap(settler_multi(), 1520, 860, 1710, 1025)),
    ("thickener_rake_single_tier", "Rake thickener, single-tier", "Сгуститель гребковый: одноярусный", wrap(rake_one(), 1545, 1095, 1690, 1285)),
    ("thickener_rake_two_tier", "Rake thickener, two-tier", "Сгуститель гребковый: двухъярусный", wrap(rake_two(), 715, 245, 850, 425)),
    ("filter_sand_hydrostatic", "Hydrostatic sand filter", "Фильтр песочный гидростатический", wrap(sand_filter(), 715, 495, 800, 648)),
    ("hydrocyclone", "Hydrocyclone", "Гидроциклон", wrap(hydrocyclone(), 670, 740, 850, 900)),
    ("filter_drum", "Drum filter", "Фильтр барабанный", wrap(drum_filter(), 695, 945, 865, 1105)),
    ("filter_plate", "Plate (disc) filter", "Фильтр тарельчатый", wrap(plate_filter(), 670, 1135, 885, 1272)),
    ("filter_bucket_carousel", "Bucket carousel filter", "Фильтр ковшовый карусельный", wrap(carousel_filter(), 1495, 245, 1655, 375)),
    ("filter_bucket_conveyor", "Bucket conveyor filter", "Фильтр ковшовый конвейерный", wrap(bucket_conveyor(), 1480, 410, 1705, 585)),
    ("filter_belt", "Belt filter", "Фильтр ленточный", wrap(belt_filter(), 1485, 620, 1710, 780)),
    ("filter_druk", "Druk filter", "Друк-фильтр", wrap(druk_filter(), 1500, 815, 1670, 1030)),
    ("filter_nutsch", "Nutsch filter (vacuum filter)", "Нутч-фильтр (фильтр вакуумный)", wrap(nutsch_filter(), 1540, 1048, 1670, 1282)),
    ("filter_leaf_horizontal_transverse", "Horizontal leaf filter, transverse leaves, internal pressure above atmospheric", "Фильтр листовой горизонтальный с поперечными листами и внутренним давлением выше атмосферного", wrap(horizontal_leaf("cross"), 645, 245, 860, 365)),
    ("filter_leaf_horizontal_longitudinal", "Horizontal leaf filter, longitudinal leaves, internal pressure above atmospheric", "Фильтр листовой горизонтальный с продольными листами и внутренним давлением выше атмосферного", wrap(horizontal_leaf("long", 418), 645, 405, 860, 525)),
    ("filter_leaf_vertical", "Vertical leaf filter, internal pressure above atmospheric", "Фильтр листовой вертикальный с внутренним давлением выше атмосферного", wrap(vertical_leaf(), 680, 575, 865, 805)),
    ("filter_disc_vacuum", "Vacuum disc filter", "Фильтр дисковый вакуумный", wrap(disc_filter(False), 615, 835, 900, 1012)),
    ("filter_disc_pressure", "Pressure disc filter, above atmospheric", "Фильтр дисковый под давлением выше атмосферного", wrap(disc_filter(True), 615, 1050, 900, 1225)),
    ("filter_disc_horizontal_discs", "Pressure disc filter with horizontal discs, above atmospheric", "Фильтр дисковый под давлением выше атмосферного с горизонтальными дисками", wrap(disc_filter_horizontal(), 1495, 250, 1635, 540)),
    ("filter_corrugated_element", "Filter with corrugated filter element", "Фильтр с гофрированным фильтроэлементом", wrap(corrugated_filter(), 1550, 580, 1640, 840)),
    ("filter_cartridge", "Cartridge filter, above atmospheric pressure", "Фильтр патронный под давлением выше атмосферного", wrap(cartridge_filter(), 1495, 895, 1685, 1125)),
    ("filter_press_vertical_plates", "Filter press with vertical plates", "Фильтр-пресс с вертикальными плитами", wrap(press_vertical(), 1465, 1160, 1670, 1280)),
    ("filter_press_horizontal_plates", "Filter press with horizontal plates", "Фильтр-пресс с горизонтальными плитами", wrap(press_horizontal(), 700, 245, 850, 445)),
    ("filter_separator_single_stage", "Filter-separator, single-stage", "Фильтр-сепаратор: одноступенчатый", wrap(separator_one(), 675, 485, 860, 625)),
    ("filter_separator_two_stage", "Filter-separator, two-stage", "Фильтр-сепаратор: двухступенчатый", wrap(separator_two(), 675, 635, 860, 810)),
    ("filter_separator_three_stage", "Filter-separator, three-stage", "Фильтр-сепаратор: трёхступенчатый", wrap(separator_three(), 675, 820, 860, 955)),
    ("filter_separator_static_plate", "Static filter-separator (plate)", "Фильтр-сепаратор статический (тарельчатый)", wrap(separator_static(), 1495, 245, 1685, 385)),
    ("filter_countercurrent_wash", "Filter with countercurrent washing", "Фильтр с противоточной промывкой", wrap(separator_countercurrent(), 1495, 400, 1685, 540)),
    ("filter_basket", "Basket filter", "Фильтр корзинчатый", wrap(separator_basket(), 1485, 578, 1690, 720)),
    ("filter_spiral", "Spiral filter", "Фильтр спиральный", wrap(separator_spiral(), 1495, 745, 1690, 885)),
]

if __name__ == "__main__":
    store(STANDARD, "gost_2_791", [(c, e, r, CATEGORY, s) for c, e, r, s in ROWS], NOTE)

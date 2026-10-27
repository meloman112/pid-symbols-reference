"""ГОСТ 2.788-74 «Аппараты выпарные» — рисунки по таблицам 1–3 стандарта (координаты сняты со скана)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_symbols import LINE, svg

NOTE = "собственный рисунок по скану ГОСТ 2.788-74"
CATEGORY = "Выпарные аппараты"
STROKE = f'{LINE} vector-effect="non-scaling-stroke"'
DASH_DOT = f'{STROKE} stroke-dasharray="14 5 3 5"'


def P(d, style=STROKE):
    return f'<path d="{d}" {style}/>'


def R(x0, y0, x1, y1):
    return P(f"M{x0} {y0}H{x1}V{y1}H{x0}Z")


def head(x, y, direction, filled, size=20):
    """Стрелка с остриём в (x, y); direction — куда она смотрит."""
    bx, by = {"u": (0, 1), "d": (0, -1), "l": (1, 0), "r": (-1, 0)}[direction]
    px, py = -by * size / 2, bx * size / 2
    ax, ay = x + bx * size, y + by * size
    d = f"M{x} {y}L{ax + px} {ay + py}L{ax - px} {ay - py}Z"
    return f'<path d="{d}" fill="#000"/>' if filled else P(d)


def scan(body, box, k=None):
    """Рисунок в координатах скана; box — его габарит, k — масштаб (по умолчанию вписать в 52 по высоте)."""
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    k = k or min(52 / bh, 64 / bw)
    width = max(40, round(bw * k + 16))
    tx, ty = (width - bw * k) / 2 - x0 * k, (60 - bh * k) / 2 - y0 * k
    return svg(f'<g transform="translate({tx:.2f} {ty:.2f}) scale({k:.4f})">{body}</g>', width)


def tubes(x0, x1, y0, y1, xs):
    return R(x0, y0, x1, y1) + "".join(P(f"M{x} {y0}V{y1}") for x in xs)


def heater(x0, x1, y0, y1, head_h, xs):
    """Тепловая камера: корпус, две распределительные зоны и трубы между ними."""
    return R(x0, y0, x1, y1) + P(f"M{x0} {y0 + head_h}H{x1}M{x0} {y1 - head_h}H{x1}") + "".join(
        P(f"M{x} {y0 + head_h}V{y1 - head_h}") for x in xs)


K1, K2 = 0.4, 0.38

SHELLS = [
    ("evap_shell_atm", "Shell, atmospheric pressure", "Обечайка под атмосферным давлением", scan(P("M720 248V378M773 248V378"), (700, 240, 795, 385), K1)),
    ("evap_shell_over", "Shell, internal pressure above atmospheric", "Обечайка с внутренним давлением выше атмосферного", scan(P("M720 403V430L711 470L720 510V537M773 403V430L782 470L773 510V537"), (700, 400, 795, 540), K1)),
    ("evap_shell_under", "Shell, internal pressure below atmospheric", "Обечайка с внутренним давлением ниже атмосферного", scan(P("M722 585V620L732 650L722 685V715M775 585V620L765 650L775 685V715"), (700, 580, 795, 720), K1)),
    ("evap_head_atm", "Head, atmospheric pressure", "Днище под атмосферным давлением", scan(P("M718 845V870H772V845"), (700, 835, 790, 880), K1)),
    ("evap_head_over", "Head, internal pressure above atmospheric", "Днище с внутренним давлением выше атмосферного", scan(P("M718 902V920L745 930L772 920V902"), (700, 895, 790, 940), K1)),
    ("evap_head_under", "Head, internal pressure below atmospheric", "Днище с внутренним давлением ниже атмосферного", scan(P("M718 960V985L745 977L772 985V960"), (700, 955, 790, 1000), K1)),
]

BODIES = [
    ("evap_body_atm", "Evaporator body, atmospheric pressure", "Корпус аппарата под атмосферным давлением", scan(R(1522, 295, 1570, 425), (1500, 285, 1595, 435), K2)),
    ("evap_body_over", "Evaporator body, internal pressure above atmospheric", "Корпус аппарата с внутренним давлением выше атмосферного", scan(P("M1527 535L1550 520L1573 535V645L1550 660L1527 645Z"), (1500, 510, 1595, 670), K2)),
    ("evap_body_under", "Evaporator body, internal pressure below atmospheric", "Корпус аппарата с внутренним давлением ниже атмосферного", scan(P("M1525 810L1550 822L1575 810V940L1550 930L1525 940Z"), (1500, 800, 1595, 950), K2)),
    ("evap_film_body_atm", "Film evaporator body, atmospheric pressure", "Корпус плёночного выпарного аппарата под атмосферным давлением", scan(P("M1503 1112H1595V1150H1572V1245H1523V1150H1503Z"), (1490, 1100, 1610, 1255), K2)),
    ("evap_film_body_over", "Film evaporator body, internal pressure above atmospheric", "Корпус плёночного выпарного аппарата с внутренним давлением выше атмосферного", scan(P("M704 262L750 248L797 262V300H775V385L750 400L725 385V300H704Z"), (690, 240, 810, 410), K2)),
    ("evap_film_body_under", "Film evaporator body, internal pressure below atmospheric", "Корпус плёночного выпарного аппарата с внутренним давлением ниже атмосферного", scan(P("M701 440L750 455L797 440V485H775V572L750 563L725 572V485H701Z"), (690, 430, 810, 580), K2)),
]


NATURAL_REMOTE = (
    P("M1443 263H1640V612H1443Z", DASH_DOT)
    + R(1575, 305, 1625, 438)
    + P("M1600 305V250") + head(1600, 277, "u", False)
    + P("M1433 316H1575") + head(1560, 316, "r", True)
    + heater(1485, 1537, 418, 550, 27, (1497, 1504, 1513, 1520, 1527))
    + P("M1511 418V372H1575") + head(1511, 388, "u", True)
    + P("M1433 453H1485") + head(1478, 453, "r", True)
    + P("M1433 515H1485") + head(1455, 515, "l", True)
    + P("M1600 438V595H1511V550") + head(1511, 565, "u", True)
)

FORCED_COAXIAL = (
    P("M1458 937H1633V1178H1458Z", DASH_DOT)
    + heater(1495, 1547, 980, 1112, 22, (1503, 1511, 1521, 1530, 1538))
    + P("M1521 980V922") + head(1521, 948, "u", False)
    + P("M1443 990H1495") + head(1490, 990, "r", True)
    + P("M1443 1014H1495") + head(1490, 1014, "r", True)
    + P("M1443 1078H1495") + head(1470, 1078, "l", True)
    + P("M1547 990H1600V1054") + head(1565, 990, "l", True)
    + f'<circle cx="1600" cy="1080" r="26" {STROKE}/>' + head(1600, 1056, "u", True, 24)
    + P("M1600 1106V1165H1521V1112") + head(1521, 1127, "d", True)
)

FORCED_REMOTE = (
    P("M652 264H850V617H652Z", DASH_DOT)
    + R(787, 311, 838, 445)
    + P("M812 311V248") + head(812, 281, "u", False)
    + P("M637 321H787") + head(780, 321, "r", True)
    + heater(696, 745, 423, 555, 27, (706, 713, 722, 729, 737))
    + P("M720 423V380H787") + head(720, 395, "u", True)
    + P("M637 455H696") + head(692, 455, "r", True)
    + P("M637 545H696") + head(662, 545, "l", True)
    + P("M812 445V499")
    + f'<circle cx="810" cy="525" r="26" {STROKE}/>' + head(811, 548, "d", True, 22)
    + P("M812 551V600H720V555") + head(720, 568, "u", True)
)


def film(x0, x1, top, head_h, stem_x0, stem_x1, bottom, sx, left_y, right_y, inner):
    """Плёночный аппарат: широкая верхняя часть, узкий корпус, штуцеры сверху, снизу, справа и слева."""
    outline = f"M{x0} {top}H{x1}V{top + head_h}H{stem_x1}V{bottom}H{stem_x0}V{top + head_h}H{x0}Z"
    stubs = (f"M{sx} {top - 22}V{top}M{sx} {bottom}V{bottom + 22}"
             f"M{x1} {right_y}H{x1 + 25}M{x0} {left_y}H{stem_x0}")
    return P(outline) + P(stubs) + inner


FILM_FALLING = film(708, 797, 752, 38, 727, 778, 885, 752, 812, 778, P("M752 767V872M740 767H766"))
FILM_RISING = film(1503, 1590, 268, 32, 1523, 1573, 400, 1547, 328, 295, P("M1547 285V385M1535 385H1560"))
FILM_ROTOR = film(1505, 1590, 487, 28, 1525, 1575, 613, 1547, 547, 510,
                  f'<circle cx="1547" cy="500" r="6" {STROKE}/>' + P("M1547 506V590"))

SUBMERGED = (
    R(1525, 693, 1575, 822) + P("M1550 693V660") + head(1550, 660, "u", False, 18)
    + P("M1473 775H1515") + head(1525, 775, "r", True)
    + P("M1527 765H1573", STROKE + ' stroke-dasharray="none"')
    + P("M1530 805H1570M1530 815H1570", f'{STROKE} stroke-dasharray="6 4"')
    + P("M1533 802C1533 785 1545 777 1558 780C1556 794 1547 802 1533 802Z")
)

APPARATUS = [
    ("evap_general", "Evaporator, general symbol", "Аппарат выпарной. Общее обозначение",
     scan(R(733, 806, 783, 935) + P("M759 806V775M759 935V955") + head(759, 775, "u", False, 18)
          + P("M712 850H772L750 860L772 870L750 880L765 886H712"), (705, 770, 790, 960))),
    ("evap_natural_coaxial", "Evaporator, natural circulation, coaxial heating chamber", "Аппарат выпарной с естественной циркуляцией, с соосной тепловой камерой",
     scan(heater(735, 785, 1062, 1190, 26, (742, 750, 770, 778)) + P("M759 1062V1006M759 1190V1208")
          + head(759, 1028, "u", False, 18) + P("M712 1072H735M712 1097H735M712 1155H735"), (705, 1000, 790, 1212))),
    ("evap_natural_remote", "Evaporator, natural circulation, remote heating chamber", "Аппарат выпарной с естественной циркуляцией, с выносной тепловой камерой",
     scan(NATURAL_REMOTE, (1425, 245, 1650, 615))),
    ("evap_forced_coaxial", "Evaporator, forced circulation, coaxial heating chamber", "Аппарат выпарной с принудительной циркуляцией, с соосной тепловой камерой",
     scan(FORCED_COAXIAL, (1435, 920, 1640, 1180))),
    ("evap_forced_remote", "Evaporator, forced circulation, remote heating chamber", "Аппарат выпарной с принудительной циркуляцией, с выносной тепловой камерой",
     scan(FORCED_REMOTE, (630, 245, 855, 620))),
    ("evap_film_falling", "Film evaporator, free falling film", "Аппарат выпарной плёночный со свободно падающей плёнкой", scan(FILM_FALLING, (700, 728, 830, 910))),
    ("evap_film_rising", "Film evaporator, rising film", "Аппарат выпарной плёночный с восходящей плёнкой", scan(FILM_RISING, (1495, 245, 1620, 425))),
    ("evap_film_rotor", "Film evaporator, rotary", "Аппарат выпарной плёночный роторный", scan(FILM_ROTOR, (1495, 465, 1620, 635))),
    ("evap_submerged_combustion", "Evaporator with submerged combustion", "Аппарат выпарной с погружённым горением", scan(SUBMERGED, (1465, 655, 1585, 825))),
]

if __name__ == "__main__":
    from gen_symbols import store

    rows = [(code, en, ru, CATEGORY, drawing) for code, en, ru, drawing in SHELLS + BODIES + APPARATUS]
    store("GOST 2.788", "gost", rows, NOTE)

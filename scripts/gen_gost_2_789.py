"""ГОСТ 2.789-74 «Аппараты теплообменные» — рисунки по таблицам 1–3 стандарта (координаты сняты со скана)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_gost_2_788 import R, STROKE, head, scan
from gen_gost_2_788 import P as path
from gen_symbols import THIN

NOTE = "собственный рисунок по скану ГОСТ 2.789-74"
CATEGORY = "Теплообменники"
THINS = f'{THIN} vector-effect="non-scaling-stroke"'


def P(*segments):
    return path("".join(segments))


def filled_rect(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000"/>'


def circle(cx, cy, r):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" {STROKE}/>'


def hatch(x0, y0, x1, y1, step, rising=True):
    """Штриховка под 45°, обрезанная по прямоугольнику."""
    segments = []
    if rising:
        for c in range(int(x0 + y0), int(x1 + y1), step):
            xa, xb = max(x0, c - y1), min(x1, c - y0)
            segments.append(f"M{xa} {c - xa}L{xb} {c - xb}")
    else:
        for c in range(int(x0 - y1), int(x1 - y0), step):
            xa, xb = max(x0, c + y0), min(x1, c + y1)
            segments.append(f"M{xa} {xa - c}L{xb} {xb - c}")
    return path("".join(segments), THINS)


def zigzag(x0, x1, y_low, y_high, n):
    """Ломаная от (x0, y_low) до (x1, y_low) из n звеньев."""
    return "".join(f"L{x0 + (x1 - x0) * i / n:.1f} {y_low if i % 2 == 0 else y_high}" for i in range(1, n + 1))


def lines_x(xs, y0, y1):
    return "".join(f"M{x} {y0}V{y1}" for x in xs)


def lines_y(ys, x0, x1):
    return "".join(f"M{x0} {y}H{x1}" for y in ys)


# --- Таблица 1: элементы, осуществляющие теплообмен ---

ELEMENTS = [
    ("hx_tube_fixed_sheets", "Tubular element, fixed tube sheets", "Элемент трубчатый с неподвижными трубными решётками",
     scan(P("M122 42H237M122 200H237", lines_x((148, 157, 205, 215), 42, 200)), (115, 35, 245, 205))),
    ("hx_tube_floating_head", "Tubular element, floating head", "Элемент трубчатый с плавающей головкой",
     scan(P("M122 312H237", lines_x((148, 157, 205, 215), 312, 470), "M142 470H218A38 22 0 0 1 142 470"), (115, 305, 245, 515))),
    ("hx_tube_floating_head_gland", "Tubular element, floating head with gland", "Элемент трубчатый с плавающей головкой и сальником",
     scan(P("M122 640H237", lines_x((148, 157, 205, 215), 640, 800), "M142 800H218A38 24 0 0 1 142 800M168 824V910H188V824")
          + filled_rect(150, 855, 15, 30) + filled_rect(190, 855, 15, 30), (115, 635, 245, 915))),
    ("hx_tube_u", "Tubular element, U-tubes", "Элемент трубчатый с U-образными трубами",
     scan(P("M122 42H237M137 42V175A41.5 60 0 0 0 220 175V42"), (115, 35, 245, 240))),
    ("hx_tube_field", "Tubular element, Field tubes", "Элемент трубчатый с трубками Фильда",
     scan(P("M122 365H237M160 352H195M177 352V365M137 365V490A41.5 55 0 0 0 220 490V365M177 365V515"), (115, 345, 245, 550))),
    ("hx_tube_u_separate_sheets", "Tubular element, U-tubes with separate tube sheets", "Элемент трубчатый с U-образными трубами и раздельными трубными досками",
     scan(P("M127 648H160M195 648H232M137 648V780A41.5 55 0 0 0 220 780V648"), (115, 640, 245, 840))),
    ("hx_tube_coiled", "Tubular element, coiled", "Элемент трубчатый витой",
     scan(R(120, 930, 228, 1090) + hatch(120, 930, 228, 1090, 24), (115, 925, 235, 1095))),
    ("hx_tube_spiral", "Tubular element, spiral", "Элемент трубчатый спиральный",
     scan(P("M265 50V155", zigzag(265, 410, 155, 135, 12), "V50"), (255, 45, 420, 160))),
    ("hx_tube_flat", "Tubular element, flat", "Элемент трубчатый плоский",
     scan(P("M265 240V355H412V240", lines_y((285, 307, 330), 265, 412)), (255, 235, 420, 360))),
    ("hx_direct_distributor_down", "Direct heat transfer: heating or cooling liquid/gas distributor (downward)",
     "Элемент с прямой теплопередачей: распределитель жидкости или газа, нагревающий или охлаждающий (вниз)",
     scan(P("M112 657H290M195 620V657", *(f"M{x - 18} 690L{x} 660L{x + 18} 690" for x in (148, 195, 245))), (105, 615, 300, 695))),
    ("hx_direct_distributor_up", "Direct heat transfer: heating or cooling liquid/gas distributor (upward)",
     "Элемент с прямой теплопередачей: распределитель жидкости или газа, нагревающий или охлаждающий (вверх)",
     scan(P("M392 657H570M481 657V697", *(f"M{x - 18} 625L{x} 657L{x + 18} 625" for x in (430, 481, 540))), (385, 615, 575, 700))),
    ("hx_direct_sprayer_centrifugal", "Direct heat transfer: centrifugal sprayer", "Элемент с прямой теплопередачей: распылитель центробежный",
     scan(P("M340 790V868M300 868H382"), (290, 780, 392, 875))),
    ("hx_direct_flame_sprayer", "Direct heat transfer: open flame sprayer", "Элемент с прямой теплопередачей: распылитель открытым пламенем",
     scan(P("M45 95H125M125 95L160 35C183 55 168 90 125 95"), (40, 30, 185, 100))),
    ("hx_direct_radiant", "Direct heat transfer: radiant heating element", "Элемент с прямой теплопередачей: элемент нагрева радиационный",
     scan(P("M106 200V268M60 310H152A46 42 0 0 0 60 310"), (50, 195, 160, 315))),
    ("hx_jacket", "Heating or cooling jacket", "Рубашка греющая или охлаждающая",
     scan(P("M278 130V347M278 160H255V312H278M378 130V347M378 160H400V312H378"), (245, 125, 410, 352))),
    ("hx_regenerator_element", "Heat regenerator", "Регенератор тепла",
     scan(R(278, 448, 383, 608) + hatch(278, 448, 383, 608, 18) + hatch(278, 448, 383, 608, 18, False), (270, 440, 392, 615))),
]

# --- Таблица 2: примеры построения ---


def shell_tube(shell, plates, tube_xs, y0, y1, stubs, box):
    return scan(P(shell, plates, lines_x(tube_xs, y0, y1), stubs), box)


def double_u(x0, x1, y0, y_arc, gap=8):
    inner = f"M{x0 + gap} {y0}V{y_arc}A{(x1 - x0) / 2 - gap} 24 0 0 0 {x1 - gap} {y_arc}V{y0}"
    return f"M{x0} {y0}V{y_arc}A{(x1 - x0) / 2} 30 0 0 0 {x1} {y_arc}V{y0}" + inner


FIXED = "M140 85L92 105V350L140 372L188 350V105Z"
FIXED_STUBS = "M140 30V85M140 372V430M40 168H92M188 287H240"

SHELL_TUBE = [
    ("hx_shell_tube_fixed", "Shell-and-tube exchanger, fixed tube sheets, pressure above atmospheric in tubes and shell",
     "Аппарат теплообменный кожухотрубчатый с неподвижными трубными решётками при давлении в трубах и межтрубном пространстве выше атмосферного",
     shell_tube(FIXED, "M92 150H188M92 305H188", (106, 118, 162, 174), 150, 305, FIXED_STUBS, (35, 25, 245, 435))),
    ("hx_shell_tube_fixed_waist", "Shell-and-tube exchanger, fixed tube sheets, pressure above atmospheric in tubes and below atmospheric in shell",
     "Аппарат теплообменный кожухотрубчатый с неподвижными трубными решётками при давлении в трубах выше, а в межтрубном пространстве ниже атмосферного",
     shell_tube("M140 645L92 665V705L106 790L92 868V915L140 935L188 915V868L174 790L188 705V665Z", "M92 708H188M92 868H188",
                (113, 125, 157, 169), 708, 868, "M140 590V645M140 935V990M40 725H92M188 850H236", (35, 585, 245, 995))),
    ("hx_shell_tube_expansion", "Shell-and-tube exchanger with shell expansion joint, pressure above atmospheric",
     "Аппарат теплообменный кожухотрубчатый с температурным компенсатором на кожухе при давлении в трубах и межтрубном пространстве выше атмосферного",
     shell_tube("M135 95L85 115V345L135 385L188 345V115Z", "M85 160H188M85 322H188", (100, 113, 160, 174), 160, 322,
                "M135 40V95M135 385V445M38 180H85M188 298H238M85 225A9 15 0 0 0 85 255M188 225A9 15 0 0 1 188 255", (30, 35, 245, 450))),
    ("hx_shell_tube_floating", "Shell-and-tube exchanger with floating head, pressure above atmospheric",
     "Аппарат теплообменный кожухотрубчатый с плавающей головкой при давлении в трубах и межтрубном пространстве выше атмосферного",
     shell_tube("M85 640L137 618L190 640V888L137 915L85 888Z", "M137 618V655M85 655H190", (110, 122, 158, 170), 655, 840,
                "M108 575V630M165 575V630M40 700H85M190 818H240M110 840H170A30 28 0 0 1 110 840", (35, 570, 245, 920))),
    ("hx_shell_tube_u", "Shell-and-tube exchanger with U-tubes, pressure above atmospheric",
     "Аппарат теплообменный кожухотрубчатый с U-образными трубами при давлении в трубах и межтрубном пространстве выше атмосферного",
     scan(P("M160 55L100 80V325L160 358L215 325V80Z", "M160 55V118M100 118H215", "M128 20V68M192 20V68M55 145H100M215 268H262",
            double_u(125, 190, 118, 268)), (50, 15, 265, 365))),
    ("hx_shell_tube_gland", "Shell-and-tube exchanger with gland, pressure above atmospheric",
     "Аппарат теплообменный кожухотрубчатый с сальником при давлении в трубах и межтрубном пространстве выше атмосферного",
     scan(P("M100 615L160 590L218 615V870H185M100 615V870H135", "M100 660H218", lines_x((130, 142, 178, 190), 668, 820),
            "M138 822H182A22 26 0 0 1 138 822M150 850V935H170V850M160 545V590M160 935V985M55 685H100M218 805H262")
          + filled_rect(134, 872, 14, 36) + filled_rect(172, 872, 14, 36), (50, 540, 268, 990))),
    ("hx_shell_tube_vapor_floating", "Shell-and-tube exchanger with vapor space and floating head, pressure above atmospheric",
     "Аппарат теплообменный кожухотрубчатый с паровым пространством, с плавающей головкой при давлении в трубах и межтрубном пространстве выше атмосферного",
     scan(P("M75 142L50 185L75 248H290M75 142H150V118L200 95L248 118V142H290", "M290 145H325L352 197L325 248H290Z", "M295 197H350",
            "M290 160H128A36 36 0 0 0 128 232H290M125 176H290M125 216H290M128 176A20 20 0 0 0 128 216",
            "M200 40V95M195 248V300M342 162H388M342 230H388"), (40, 35, 395, 305))),
    ("hx_shell_tube_vapor_u", "Shell-and-tube exchanger with vapor space and U-tubes, pressure above atmospheric",
     "Аппарат теплообменный кожухотрубчатый с паровым пространством, с U-образными трубами при давлении в трубах и межтрубном пространстве выше атмосферного",
     scan(P("M72 650L55 700L72 752H297M72 650H155V622L205 598L250 622V650H297", "M297 648H330L355 705L330 752H297Z", "M300 708H352",
            "M297 672H132A32 32 0 0 0 132 736H297", "M205 550V598M200 752V810M345 678H395M345 740H395"), (45, 545, 398, 815))),
    ("hx_shell_tube_coiled", "Shell-and-tube exchanger with coiled tubes, pressure equal to atmospheric",
     "Аппарат теплообменный кожухотрубчатый витые при давлении в трубах и межтрубном пространстве равном атмосферному",
     scan(R(125, 72, 235, 340) + P("M125 125H235M125 285H235M180 18V72M180 340V400M68 148H125M235 262H290") + hatch(125, 125, 235, 285, 30), (60, 15, 295, 405))),
]

TUBULAR = [
    ("hx_submerged_spiral", "Tubular exchanger without shell, submerged spiral",
     "Аппарат теплообменный трубчатый без кожуха, погружённый спиральный",
     scan(P("M90 125V225H270V130M248 55V190M40 208H90M270 148H325M110 55V190", zigzag(110, 248, 190, 170, 12)), (35, 50, 330, 230))),
    ("hx_submerged_flat", "Tubular exchanger without shell, submerged flat",
     "Аппарат теплообменный трубчатый без кожуха, погружённый плоский",
     scan(P("M90 395V490H270V395M110 320V470H248V320M40 470H90M270 405H322", lines_y((400, 418, 436, 452), 110, 248)), (35, 315, 330, 495))),
    ("hx_spray", "Tubular exchanger without shell, spray (irrigation)",
     "Аппарат теплообменный трубчатый без кожуха, оросительный",
     scan(P("M180 580V628M100 628H265", *(f"M{x - 12} 660L{x} 632L{x + 12} 660" for x in (125, 180, 235)),
            "M40 682H250V708H115V735H322M95 722V752H272V722M180 752V810"), (35, 575, 330, 815))),
    ("hx_direct_contact", "Heat exchanger with direct heat transfer",
     "Аппарат теплообменный с прямой теплопередачей",
     scan(P("M90 50V160H270V45M105 125H258", *(f"M{x - 10} 95L{x} 125L{x + 10} 95" for x in (120, 180, 240)),
            "M40 135H90M270 75H325M180 160V208"), (35, 40, 330, 212))),
    ("hx_external_heated", "Heat exchanger with external heating",
     "Аппарат теплообменный с наружным обогревом",
     scan(R(125, 68, 232, 333) + P("M178 20V68M178 333V383M58 205H100M258 202H300M125 125H100V282H125M232 125H258V282H232"), (55, 15, 305, 388))),
    ("hx_electric_heated", "Heat exchanger with electric heating",
     "Аппарат теплообменный с электрическим обогревом",
     scan(R(125, 605, 232, 870) + R(140, 803, 218, 850) + R(150, 812, 208, 841) + P("M178 558V605M178 870V920"), (115, 550, 240, 925))),
    ("hx_regenerative", "Regenerative heat exchanger",
     "Аппарат теплообменный регенеративный",
     scan(R(117, 162, 230, 428) + P("M117 210H230M117 372H230M175 118V162M175 428V480M75 240H117M230 345H270")
          + hatch(117, 210, 230, 372, 18) + hatch(117, 210, 230, 372, 18, False), (70, 112, 275, 485))),
    ("hx_mixing_condenser", "Mixing condenser",
     "Конденсатор смешения",
     scan(R(122, 645, 235, 910) + P("M122 710H160M195 778H235M122 845H162M178 595V645M178 910V958M80 675H122M235 873H278"), (75, 590, 282, 962))),
]

# --- Таблица 3: аппараты, имеющие собственные обозначения ---


def plate_stack(box, outer, lines, diagonals, stubs, extra=""):
    return scan(outer + P(lines, diagonals, stubs) + extra, box)


PLATE = [
    ("hx_plate_spiral", "Plate exchanger, spiral",
     "Аппарат теплообменный листовой спиральный",
     scan(circle(180, 145, 65) + circle(180, 145, 42) + circle(180, 145, 13) + P("M180 35V80M180 210V255M78 145H167M245 145H290"), (75, 30, 295, 260))),
    ("hx_plate_demountable", "Plate exchanger, demountable",
     "Аппарат теплообменный листовой пластинчатый разборный",
     plate_stack((85, 315, 275, 530), "", lines_y((355, 380, 405, 430, 458, 485), 90, 268), "M130 355L228 485M228 355L130 485",
                 "M130 320V355M130 485V527M228 320V355M228 485V527")),
    ("hx_plate_semi_demountable", "Plate exchanger, semi-demountable",
     "Аппарат теплообменный листовой пластинчатый полуразборный",
     plate_stack((85, 610, 280, 820), R(92, 652, 272, 675) + R(92, 700, 272, 725) + R(92, 750, 272, 775), "", "M130 650L232 775M232 650L130 775",
                 "M130 615V650M232 615V650M130 775V815M232 775V815")),
    ("hx_plate_welded_block", "Plate exchanger, welded block",
     "Аппарат теплообменный листовой пластинчатый сварной блочный",
     plate_stack((75, 30, 275, 255), R(82, 78, 268, 215), lines_y((110, 135, 160, 185), 82, 268), "M110 78L232 215M232 78L110 215",
                 "M110 38V78M232 38V78M110 215V250M232 215V250")),
    ("hx_plate_fully_welded", "Plate exchanger, fully welded",
     "Аппарат теплообменный листовой пластинчатый цельносварной",
     plate_stack((75, 325, 275, 615), R(82, 400, 268, 530) + circle(115, 380, 8) + circle(238, 380, 8) + circle(115, 562, 8) + circle(238, 562, 8),
                 lines_y((430, 455, 480, 505), 82, 268), "M115 388L238 554M238 388L115 554", "M112 335V372M238 335V372M112 570V608M238 570V608")),
    ("hx_plate_finned", "Plate exchanger, finned",
     "Аппарат теплообменный листовой пластинчатый ребристый",
     scan(R(88, 700, 268, 830) + P(lines_y((727, 752, 777, 804), 88, 268), "M180 660V700M180 830V878M40 818H88M268 715H308")
          + path("".join(f"M{x} 706V727M{x} 804V828" for x in range(94, 268, 9)), THINS), (35, 655, 312, 882))),
    ("hx_plate_lamellar", "Plate exchanger, lamellar",
     "Аппарат теплообменный листовой ламельный",
     scan(R(100, 88, 375, 195) + R(55, 128, 120, 153) + R(352, 125, 410, 155)
          + P("M348 35V88M125 195V245M410 140H465M120 128L150 100H322L352 128V152L322 180H150L120 152Z", lines_y((118, 132, 146, 160), 155, 320), lines_x((150, 322), 100, 180))
          + filled_rect(362, 112, 12, 56) + filled_rect(386, 112, 12, 56), (50, 30, 470, 250))),
]

MISC = [
    ("hx_air_cooled", "Air-cooled heat exchanger", "Аппарат теплообменный с воздушным охлаждением",
     scan(R(185, 490, 290, 590) + P("M235 445V490M135 548H185M290 548H338", lines_y((515, 540, 570), 185, 290), "M186 590L222 685M289 590L255 685M238 685V715M238 833V880")
          + circle(238, 778, 55) + head(238, 745, "u", False, 16), (130, 440, 345, 885))),
    ("hx_calorifier", "Air heater (calorifier)", "Калорифер",
     scan(P("M150 108H322L370 135V190L322 215H150L105 190V135Z", "M152 108V215M322 108V215M152 108L322 215M322 108L152 215", "M235 55V108M235 215V265M60 162H105M370 162H418"), (55, 50, 422, 270))),
    ("hx_cooling_tower", "Cooling tower", "Градирня",
     scan(P("M225 410V445M242 410V445M212 448H258L290 538H183Z", "M212 538V570M262 538V570", "M145 538V570H325V518H380"), (140, 405, 385, 575))),
]

if __name__ == "__main__":
    from gen_symbols import store

    rows = [(code, en, ru, CATEGORY, drawing)
            for code, en, ru, drawing in ELEMENTS + SHELL_TUBE + TUBULAR + PLATE + MISC]
    store("GOST 2.789", "gost", rows, NOTE)

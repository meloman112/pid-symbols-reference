"""Рисует символы ГОСТ 21.208 и 2.785 (п. 1–13) по рисункам стандартов в svg/gost и пишет их в db."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import db

NOTE_2_785 = "собственный рисунок по скану ГОСТ 2.785-70, п. 1–13"
NOTE_21_208 = "собственный рисунок по табл. 1 ГОСТ 21.208-2013"
LINE = 'stroke="#000" stroke-width="2" fill="none"'
THIN = 'stroke="#000" stroke-width="1" fill="none"'


def svg(body, width=80):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 60" width="{width * 2}" height="120">{body}</svg>'


def pair(square, rect):
    """Допускаемое обозначение ГОСТ 21.208: квадрат и прямоугольник рядом, как в табл. 1."""
    return svg(f'<g transform="translate(4 0)">{square}</g><g transform="translate(84 0)">{rect}</g>', 152)


def diamond(cx, half_w, half_h=26):
    return f'<path d="M{cx} {30 - half_h}L{cx + half_w} 30L{cx} {30 + half_h}L{cx - half_w} 30Z" {LINE}/>'


def actuator(arrows="", inside=""):
    """Исполнительный механизм ГОСТ 21.208: кружок со штоком; стрелки — положение при отказе энергии."""
    return svg(f'<circle cx="40" cy="12" r="6" {LINE}/>{inside}<path d="M40 18V54" {LINE}/>{arrows}')


ARROW_UP = '<path d="M35 26L40 18L45 26Z" fill="#000"/>'
ARROW_DOWN = '<path d="M35 46L40 54L45 46Z" fill="#000"/>'


SQUARE = f'<rect x="10" y="18" width="24" height="24" {LINE}/>'
RECT = f'<rect x="0" y="20" width="64" height="20" {LINE}/>'
SQUARE_SPLIT = SQUARE + f'<path d="M10 30H34" {THIN}/>'
RECT_SPLIT = RECT + f'<path d="M0 30H64" {THIN}/>'

GOST_21_208 = [
    ("instrument_field_main", "Instrument, field-mounted (main symbol)", "Прибор вне щита (по месту), основное обозначение", "Приборы", svg(f'<circle cx="40" cy="30" r="14" {LINE}/>')),
    ("instrument_field_alt", "Instrument, field-mounted (permissible symbol)", "Прибор вне щита (по месту), допускаемое обозначение", "Приборы", pair(SQUARE, RECT)),
    ("instrument_panel_main", "Instrument, panel-mounted (main symbol)", "Прибор на щите, пульте, основное обозначение", "Приборы", svg(f'<circle cx="40" cy="30" r="14" {LINE}/><path d="M26 30H54" {THIN}/>')),
    ("instrument_panel_alt", "Instrument, panel-mounted (permissible symbol)", "Прибор на щите, пульте, допускаемое обозначение", "Приборы", pair(SQUARE_SPLIT, RECT_SPLIT)),
    ("digital_function_block", "Digital function block (controller, system unit, monitor, I/O)", "Функциональный блок цифровой техники (контроллер, системный блок, монитор, УСО)", "Приборы", svg(f'<rect x="20" y="18" width="40" height="24" {LINE}/>')),
    ("sis_field_main", "SIS device, field-mounted (main symbol)", "Прибор ПАЗ вне щита, основное обозначение", "ПАЗ", pair(diamond(22, 22) + SQUARE, diamond(32, 34, 28) + RECT)),
    ("sis_field_alt", "SIS device, field-mounted (permissible symbol)", "Прибор ПАЗ вне щита, допускаемое обозначение", "ПАЗ", pair(f'<rect x="0" y="8" width="44" height="44" {LINE}/>' + diamond(22, 22, 22), f'<rect x="0" y="10" width="64" height="40" {LINE}/>' + diamond(32, 32, 20))),
    ("sis_panel_main", "SIS device, panel-mounted (main symbol)", "Прибор ПАЗ на щите, основное обозначение", "ПАЗ", pair(diamond(22, 22) + SQUARE_SPLIT, diamond(32, 34, 28) + RECT_SPLIT)),
    ("sis_panel_alt", "SIS device, panel-mounted (permissible symbol)", "Прибор ПАЗ на щите, допускаемое обозначение", "ПАЗ", pair(f'<rect x="0" y="8" width="44" height="44" {LINE}/>' + diamond(22, 22, 22) + f'<path d="M0 30H44" {THIN}/>', f'<rect x="0" y="10" width="64" height="40" {LINE}/>' + diamond(32, 32, 20) + f'<path d="M0 30H64" {THIN}/>')),
    ("actuator_general", "Actuator, general symbol", "Исполнительный механизм, общее обозначение", "Исполнительные механизмы", actuator()),
    ("actuator_fail_open", "Actuator: opens the final element on loss of power or signal", "ИМ, открывающий регулирующий орган при прекращении подачи энергии или сигнала", "Исполнительные механизмы", actuator(ARROW_UP)),
    ("actuator_fail_closed", "Actuator: closes the final element on loss of power or signal", "ИМ, закрывающий регулирующий орган при прекращении подачи энергии или сигнала", "Исполнительные механизмы", actuator(ARROW_DOWN)),
    ("actuator_fail_last", "Actuator: keeps the final element in position on loss of power or signal", "ИМ, оставляющий регулирующий орган в неизменном положении при прекращении подачи энергии или сигнала", "Исполнительные механизмы", actuator(ARROW_UP + ARROW_DOWN)),
    ("actuator_manual_override", "Actuator with additional manual drive", "Исполнительный механизм с дополнительным ручным приводом", "Исполнительные механизмы", actuator(inside='<text x="40" y="15.5" font-size="9" text-anchor="middle" font-family="sans-serif">H</text>')),
]

LEFT = "M20 20L40 30L20 40Z"
RIGHT = "M60 20L40 30L60 40Z"
DOWN = "M30 50L40 30L50 50Z"
DOT = '<circle cx="40" cy="30" r="2.5" fill="#000"/>'
ARROW_IN = f'<path d="M40 6V26" {LINE}/><path d="M36 22L40 30L44 22Z" fill="#000"/>'
SPRING = f'<path d="M40 30V24L36 22L44 18L36 14L44 10L40 8V4" {LINE}/>'


def body(*paths, extra=""):
    return svg("".join(f'<path d="{p}" {LINE}/>' for p in paths) + extra)


GOST_2_785 = [
    ("stop_valve_straight", "Stop valve, straight-through", "Вентиль (клапан) запорный проходной", "Арматура", body(LEFT, RIGHT)),
    ("stop_valve_angle", "Stop valve, angle", "Вентиль (клапан) запорный угловой", "Арматура", body(LEFT, DOWN)),
    ("stop_valve_three_way", "Three-way valve", "Вентиль (клапан) трёхходовой", "Арматура", body(LEFT, RIGHT, DOWN)),
    ("control_valve_straight", "Control valve, straight-through", "Вентиль, клапан регулирующий проходной", "Арматура", body(LEFT, RIGHT, extra=ARROW_IN)),
    ("control_valve_angle", "Control valve, angle", "Вентиль, клапан регулирующий угловой", "Арматура", body(LEFT, DOWN, extra=ARROW_IN)),
    ("check_valve_straight", "Check (non-return) valve, straight-through", "Клапан обратный (невозвратный) проходной", "Арматура", body(RIGHT, extra=f'<path d="{LEFT}" fill="#000" stroke="#000" stroke-width="2"/>')),
    ("check_valve_angle", "Check (non-return) valve, angle", "Клапан обратный (невозвратный) угловой", "Арматура", body(DOWN, extra=f'<path d="{LEFT}" fill="#000" stroke="#000" stroke-width="2"/>')),
    ("safety_valve_straight", "Safety (relief) valve, straight-through", "Клапан предохранительный проходной", "Арматура", body(LEFT, RIGHT, extra=SPRING)),
    ("safety_valve_angle", "Safety (relief) valve, angle", "Клапан предохранительный угловой", "Арматура", body(LEFT, DOWN, extra=SPRING)),
    ("throttle_valve", "Throttle valve", "Клапан дроссельный", "Арматура", body("M24 22H56V38H24Z", "M24 22L56 38M24 38L56 22")),
    ("pressure_reducing_valve", "Pressure-reducing valve", "Клапан редукционный", "Арматура", body("M24 22H56V38H24Z", "M24 22L56 30L24 38")),
    ("air_release_valve", "Automatic air release valve", "Клапан воздушный автоматический (вантуз)", "Арматура", body("M26 18H54", "M30 18A10 10 0 0 0 50 18", "M40 28V42", "M33 42H47")),
    ("gate_valve", "Gate valve", "Задвижка", "Арматура", body(LEFT, RIGHT, "M40 20V40")),
    ("butterfly_valve", "Butterfly valve (rotary shutter)", "Затвор поворотный", "Арматура", body("M26 22H54V38H26Z", "M35 26L45 34", extra=DOT)),
    ("cock_straight", "Plug cock, straight-through", "Кран проходной", "Арматура", body(LEFT, RIGHT, extra=DOT)),
    ("cock_angle", "Plug cock, angle", "Кран угловой", "Арматура", body(LEFT, DOWN, extra=DOT)),
    ("cock_three_way", "Three-way cock, general", "Кран трёхходовой, общее обозначение", "Арматура", body(LEFT, RIGHT, DOWN, extra=DOT)),
    ("cock_three_way_t_plug", "Three-way cock with T-plug", "Кран трёхходовой с Т-образной пробкой", "Арматура", body(LEFT, RIGHT, DOWN, extra=f'<circle cx="40" cy="30" r="4" fill="#fff" stroke="#000" stroke-width="2"/><path d="M37 29H43M40 29V33" stroke="#000" stroke-width="1.5"/>')),
    ("cock_three_way_l_plug", "Three-way cock with L-plug", "Кран трёхходовой с L-образной пробкой", "Арматура", body(LEFT, RIGHT, DOWN, extra=f'<circle cx="40" cy="30" r="4" fill="#fff" stroke="#000" stroke-width="2"/><path d="M37 30H40V33" stroke="#000" stroke-width="1.5" fill="none"/>')),
    ("cock_four_way", "Four-way cock", "Кран четырёхходовой", "Арматура", svg(f'<g transform="rotate(45 40 30)"><path d="{LEFT}" {LINE}/><path d="{RIGHT}" {LINE}/></g><g transform="rotate(-45 40 30)"><path d="{LEFT}" {LINE}/><path d="{RIGHT}" {LINE}/></g>')),
]


def store(standard, folder, rows, note):
    out = db.ROOT / "svg" / folder
    out.mkdir(parents=True, exist_ok=True)
    conn = db.connect()
    for code, name_en, name_ru, category, drawing in rows:
        path = out / f"{code}.svg"
        path.write_text(drawing, encoding="utf-8")
        conn.execute(
            """INSERT INTO symbols (standard, code, name_en, name_ru, category, svg_path, license)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT (standard, code) DO UPDATE SET svg_path = excluded.svg_path""",
            (standard, code, name_en, name_ru, category, f"svg/{folder}/{code}.svg", note))
    conn.commit()
    print(standard, len(rows))


if __name__ == "__main__":
    store("GOST 2.785", "gost", GOST_2_785, NOTE_2_785)
    store("GOST 21.208", "gost", GOST_21_208, NOTE_21_208)

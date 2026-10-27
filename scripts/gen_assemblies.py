"""Типовые узлы по ГОСТ: собирает схему из готовых SVG символов базы, пишет svg/assemblies/*.svg и таблицы assemblies, assembly_parts.
Каждая деталь — <g class="part" data-id="id символа">, чтобы в вебе клик по ней открывал карточку."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import db

PIPE = 'stroke="#000" stroke-width="2" fill="none"'
SIGNAL = 'stroke="#000" stroke-width="1" fill="none"'
FONT = 'font-family="sans-serif" text-anchor="middle"'


def part(code, x, y, label, rotate=0, letters=None, number=None):
    """Символ с центром в (x, y). letters/number — надписи прибора по ГОСТ 21.208: буквы сверху, номер снизу."""
    return {"code": code, "x": x, "y": y, "label": label, "rotate": rotate, "letters": letters, "number": number}


def text(x, y, value, size=11):
    return f'<text x="{x}" y="{y}" font-size="{size}" {FONT}>{value}</text>'


def tee(x, y):
    return f'<circle cx="{x}" cy="{y}" r="3" fill="#000"/>'


def arrow(x, y):
    """Направление потока вправо по трубопроводу."""
    return f'<path d="M{x} {y}l-9 -4v8z" fill="#000"/>'


CONTROL_VALVE_STATION = {
    "code": "control_valve_station",
    "name": "Узел регулирующего клапана с обвязкой",
    "width": 640, "height": 360,
    "description": "Регулирующий клапан с исполнительным механизмом, отсечными задвижками до и после, "
                   "ручным байпасом и дренажами. Позволяет снять клапан в ремонт, не останавливая поток.",
    "notes": [
        "Отсечные задвижки ставят с обеих сторон клапана — без них клапан не снять с работающей линии.",
        "Байпас — ручной вентиль, а не задвижка: через него поток регулируют вручную, пока клапан в ремонте.",
        "Дренажи — между задвижками и клапаном, чтобы слить среду перед демонтажем.",
        "Стрелка на штоке исполнительного механизма — положение при потере питания или сигнала; здесь «закрывает».",
        "Сигнал от регулятора — тонкая сплошная линия связи по ГОСТ 21.208.",
    ],
    "parts": [
        part("instrument_panel_main", 320, 46, "Регулятор расхода на щите", letters="FC", number="1"),
        part("actuator_fail_closed", 320, 136, "Исполнительный механизм, закрывает при отказе"),
        part("stop_valve_straight", 320, 160, "Регулирующий орган"),
        part("gate_valve", 120, 160, "Отсечная задвижка до клапана"),
        part("gate_valve", 520, 160, "Отсечная задвижка после клапана"),
        part("stop_valve_straight", 320, 330, "Байпасный вентиль (ручное регулирование)"),
        part("stop_valve_straight", 220, 215, "Дренажный вентиль", rotate=90),
        part("stop_valve_straight", 420, 215, "Дренажный вентиль", rotate=90),
        part("cap_threaded", 220, 267, "Заглушка дренажа", rotate=90),
        part("cap_threaded", 420, 267, "Заглушка дренажа", rotate=90),
    ],
    "pipes": ["M20 160H100", "M140 160H300", "M340 160H500", "M540 160H620",
              "M60 160V330H300", "M340 330H580V160", "M220 160V195", "M420 160V195"],
    "signals": ["M320 112V60"],
    "extra": tee(60, 160) + tee(580, 160) + tee(220, 160) + tee(420, 160) + arrow(48, 160) + arrow(616, 160)
             + text(30, 150, "Вход") + text(605, 150, "Выход") + text(320, 350, "Байпас", 10),
}

PUMP_UNIT = {
    "code": "pump_unit_standby",
    "name": "Насосная установка: рабочий и резервный насос",
    "width": 680, "height": 330,
    "description": "Два одинаковых насоса параллельно. На всасе у каждого задвижка и фильтр, "
                   "на нагнетании — манометр, обратный клапан и задвижка.",
    "notes": [
        "Обратный клапан — сразу после насоса, до задвижки: не даёт среде уйти назад через стоящий резервный насос.",
        "Поток через обратный клапан по ГОСТ 2.785 идёт от белого треугольника к чёрному.",
        "Треугольник насоса по ГОСТ 2.782 — у напорного патрубка, остриём наружу.",
        "Манометр — между насосом и обратным клапаном: показывает давление самого насоса, даже когда он стоит.",
        "Фильтр — на всасе перед насосом, между задвижкой и насосом, чтобы его можно было отсечь и почистить.",
    ],
    "parts": [],
    "pipes": ["M60 40V290", "M20 40H60", "M600 290V40H660"],
    "signals": [],
    "extra": tee(60, 130) + tee(600, 130) + arrow(56, 40) + arrow(656, 40)
             + text(60, 28, "Всас (от ёмкости)") + text(600, 28, "Напор (к потребителю)"),
}

for row, (y, role) in enumerate([(130, "рабочий"), (290, "резервный")], start=1):
    PUMP_UNIT["parts"] += [
        part("gate_valve", 120, y, f"Задвижка на всасе Н-{row}"),
        part("filter", 220, y, f"Фильтр на всасе Н-{row}"),
        part("pump_fixed", 320, y, f"Насос Н-{row} ({role})"),
        part("instrument_field_main", 377, y - 54, f"Манометр Н-{row}", letters="PI", number=f"{row}"),
        part("check_valve_straight", 420, y, f"Обратный клапан Н-{row}", rotate=180),
        part("gate_valve", 500, y, f"Задвижка на нагнетании Н-{row}"),
    ]
    PUMP_UNIT["pipes"] += [f"M60 {y}H100", f"M140 {y}H186", f"M254 {y}H286", f"M354 {y}H400",
                           f"M440 {y}H480", f"M520 {y}H600"]
    PUMP_UNIT["signals"] += [f"M377 {y}V{y - 40}"]
    PUMP_UNIT["extra"] += tee(377, y) + text(320, y + 34, f"Н-{row}", 10)

LEVEL_LOOP = {
    "code": "level_control_loop",
    "name": "Контур регулирования уровня в ёмкости",
    "width": 640, "height": 400,
    "description": "Уровнемер на ёмкости передаёт сигнал регулятору, регулятор управляет клапаном на выходе. "
                   "Отдельные сигнализаторы предельного уровня — верхнего и нижнего.",
    "notes": [
        "Уровнемер подключают к ёмкости двумя отборами — сверху и снизу (перепад давления).",
        "Сигнализаторы предельного уровня — отдельные приборы со своими отборами, а не функция того же уровнемера.",
        "H и L рядом с прибором — верхний и нижний предел по ГОСТ 21.208.",
        "Клапан на выходе закрывается при отказе, чтобы ёмкость не опорожнилась; выбор зависит от процесса.",
        "Ёмкость нарисована условно: её обозначение задаёт стандарт на оборудование, а не ГОСТ 21.208.",
    ],
    "parts": [
        part("instrument_field_main", 300, 184, "Уровнемер (датчик уровня)", letters="LT", number="1-1"),
        part("instrument_panel_main", 460, 184, "Регулятор уровня на щите", letters="LIC", number="1-2"),
        part("actuator_fail_closed", 390, 336, "Исполнительный механизм, закрывает при отказе"),
        part("stop_valve_straight", 390, 360, "Регулирующий орган на выходе"),
        part("gate_valve", 300, 360, "Отсечная задвижка на выходе"),
        part("instrument_field_main", 60, 100, "Сигнализатор верхнего уровня", letters="LSA", number="1-3"),
        part("instrument_field_main", 60, 280, "Сигнализатор нижнего уровня", letters="LSA", number="1-4"),
    ],
    "pipes": ["M120 90A60 30 0 0 1 240 90V290A60 30 0 0 1 120 290Z", "M180 60V20", "M180 320V360H280",
              "M320 360H370", "M410 360H620"],
    "signals": ["M240 110H300V170", "M240 270H300V198", "M314 184H446", "M460 198V318H396",
                "M120 100H74", "M120 280H74"],
    "extra": text(180, 14, "Вход") + text(605, 350, "Выход") + arrow(616, 360) + text(180, 200, "Ёмкость")
             + text(82, 86, "H", 10) + text(82, 266, "L", 10),
}

ASSEMBLIES = [CONTROL_VALVE_STATION, PUMP_UNIT, LEVEL_LOOP]


def symbol_body(conn, code):
    row = conn.execute("SELECT id, svg_path FROM symbols WHERE code = ? AND standard LIKE 'GOST %'", (code,)).fetchone()
    inner = re.sub(r"^<svg[^>]*>|</svg>$", "", (db.ROOT / row["svg_path"]).read_text().strip())
    return row["id"], inner


def render(conn, assembly):
    groups = []
    for index, p in enumerate(assembly["parts"]):
        symbol_id, inner = symbol_body(conn, p["code"])
        p["symbol_id"] = symbol_id
        labels = ""
        if p["letters"]:
            labels = text(40, 27, p["letters"], 9) + text(40, 40, p["number"], 8)
        groups.append(f'<g class="part" data-id="{symbol_id}" data-part="{index}" transform="translate({p["x"] - 40} {p["y"] - 30}) '
                      f'rotate({p["rotate"]} 40 30)"><title>{p["label"]}</title>{inner}{labels}</g>')
    lines = "".join(f'<path d="{d}" {PIPE}/>' for d in assembly["pipes"])
    lines += "".join(f'<path d="{d}" {SIGNAL}/>' for d in assembly["signals"])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {assembly["width"]} {assembly["height"]}" '
            f'width="{assembly["width"]}" height="{assembly["height"]}">{lines}{assembly["extra"]}{"".join(groups)}</svg>')


def main():
    out = db.ROOT / "svg" / "assemblies"
    out.mkdir(exist_ok=True)
    conn = db.connect()
    conn.execute("DELETE FROM assembly_parts")
    conn.execute("DELETE FROM assemblies")
    for a in ASSEMBLIES:
        (out / f"{a['code']}.svg").write_text(render(conn, a), encoding="utf-8")
        assembly_id = conn.execute(
            "INSERT INTO assemblies (code, standard, name, description, notes, svg_path) VALUES (?, 'ГОСТ', ?, ?, ?, ?)",
            (a["code"], a["name"], a["description"], "\n".join(a["notes"]), f"svg/assemblies/{a['code']}.svg")).lastrowid
        conn.executemany("INSERT INTO assembly_parts (assembly_id, symbol_id, label) VALUES (?, ?, ?)",
                         [(assembly_id, p["symbol_id"], p["label"]) for p in a["parts"]])
    conn.commit()
    print(len(ASSEMBLIES), "узла")


if __name__ == "__main__":
    main()

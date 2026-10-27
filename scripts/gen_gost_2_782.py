"""Насосы ГОСТ 2.782-96 (табл. 1, п. 1–2) и фильтр ГОСТ 2.780-96 (табл. 1, п. 1) — для типовых узлов. Сканы: helpeng.ru."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_symbols import LINE, db, svg

# Насос: окружность, залитый треугольник у выходной линии остриём наружу (ГОСТ 2.782-96, табл. 1)
CIRCLE = f'<circle cx="40" cy="30" r="16" {LINE}/><path d="M6 30H24M56 30H74" {LINE}/>'
OUT_RIGHT = '<path d="M56 30L49 25.5V34.5Z" fill="#000"/>'
OUT_LEFT = '<path d="M24 30L31 25.5V34.5Z" fill="#000"/>'
ADJUST = f'<path d="M24 46L56 14" {LINE}/><path d="M56 14L48 16L54 22Z" fill="#000"/>'

ROWS = [
    ("GOST 2.782", "pump_fixed", "Pump, fixed displacement, one flow direction", "Насос нерегулируемый с нереверсивным потоком",
     "Насосы и компрессоры", "svg/gost/pump_fixed.svg", svg(CIRCLE + OUT_RIGHT),
     "Перекачивает жидкость в одном направлении с постоянной подачей.",
     "На линии между всасывающим и напорным трубопроводом; треугольник ставят у напорного патрубка.",
     "Треугольник рисуют у всасывающей линии или остриём внутрь — так меняется смысл направления потока.",
     "Насос с реверсивным потоком — два треугольника; насос регулируемый — косая стрелка через окружность."),
    ("GOST 2.782", "pump_fixed_reversible", "Pump, fixed displacement, reversible flow", "Насос нерегулируемый с реверсивным потоком",
     "Насосы и компрессоры", "svg/gost/pump_fixed_reversible.svg", svg(CIRCLE + OUT_RIGHT + OUT_LEFT),
     "Насос, который может подавать жидкость в обе стороны (при смене направления вращения).",
     "В гидросистемах, где поток по линии меняет направление; обе линии могут быть напорными.",
     "Ставят реверсивный там, где поток всегда в одну сторону, — путает читающего схему.",
     "Насос с нереверсивным потоком — один треугольник."),
    ("GOST 2.782", "pump_variable", "Pump, variable displacement, one flow direction", "Насос регулируемый с нереверсивным потоком",
     "Насосы и компрессоры", "svg/gost/pump_variable.svg", svg(CIRCLE + OUT_RIGHT + ADJUST),
     "Насос с изменяемой подачей (регулируемый рабочий объём или частота вращения).",
     "Там, где подачу меняют по сигналу или вручную; способ регулирования показывают отдельно.",
     "Забывают косую стрелку и рисуют как нерегулируемый; стрелку проводят не через окружность.",
     "Насос нерегулируемый — без стрелки."),
    ("GOST 2.780", "filter", "Filter", "Фильтр",
     "Фильтры и сепараторы", "svg/gost/filter_2_780.svg",
     svg(f'<path d="M28 30L40 16L52 30L40 44Z" {LINE}/><path d="M40 16V44" stroke="#000" stroke-width="1.5" stroke-dasharray="4 3"/><path d="M6 30H28M52 30H74" {LINE}/>'),
     "Очищает рабочую среду от механических примесей.",
     "Перед насосом на всасывающей линии, перед регулирующей арматурой и приборами; с отсечной арматурой для чистки.",
     "Рисуют сплошную линию внутри ромба — это уже другой аппарат; не показывают отсечку для обслуживания.",
     "Влагоотделитель — ромб с горизонтальной чертой внизу; кондиционер общего вида — пустой ромб."),
]

NOTES = {"GOST 2.782": "собственный рисунок по табл. 1 ГОСТ 2.782-96", "GOST 2.780": "собственный рисунок по табл. 1 ГОСТ 2.780-96"}

conn = db.connect()
for standard, code, name_en, name_ru, category, path, drawing, purpose, placement, mistakes, similar in ROWS:
    (db.ROOT / path).write_text(drawing, encoding="utf-8")
    conn.execute(
        """INSERT INTO symbols (standard, code, name_en, name_ru, category, svg_path, license, purpose, placement, mistakes, similar)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT (standard, code) DO UPDATE SET svg_path = excluded.svg_path""",
        (standard, code, name_en, name_ru, category, path, NOTES[standard], purpose, placement, mistakes, similar))
conn.commit()
print(len(ROWS))

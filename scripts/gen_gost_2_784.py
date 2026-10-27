"""ГОСТ 2.784-96 «Элементы трубопроводов» — рисунки по таблице 1 стандарта (текст: helpeng.ru)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_symbols import LINE, store, svg

NOTE = "собственный рисунок по табл. 1 ГОСТ 2.784-96"
PIPE = "M8 30H72"


def dot(x, y):
    return f'<circle cx="{x}" cy="{y}" r="2.5" fill="#000"/>'


def body(*paths, extra=""):
    return svg("".join(f'<path d="{p}" {LINE}/>' for p in paths) + extra)


def piped(*paths, extra=""):
    return body(PIPE, *paths, extra=extra)


PIPES = [
    ("pipeline_main", "Pipeline: suction, pressure, drain lines", "Трубопровод: линии всасывания, напора, слива", svg(f'<path d="{PIPE}" stroke="#000" stroke-width="4"/>')),
    ("pipeline_control", "Pipeline: control, drainage, air vent, condensate lines", "Трубопровод: линии управления, дренажа, выпуска воздуха, отвода конденсата", svg(f'<path d="{PIPE}" stroke="#000" stroke-width="3" stroke-dasharray="8 5"/>')),
    ("pipe_tee", "Pipe junction, tee", "Соединение трубопроводов, тройник", body("M10 34H70", "M40 34V8", extra=dot(40, 34))),
    ("pipe_cross", "Pipe junction, cross", "Крестовина", body("M10 30H70", "M40 6V54", extra=dot(40, 30))),
    ("pipe_crossing", "Pipes crossing without connection", "Пересечение трубопроводов без соединения", body("M10 30H70", "M40 6V54")),
    ("pipe_crossing_bridge", "Pipes crossing without connection (bridge)", "Пересечение трубопроводов без соединения (с обходом)", body("M10 30H70", "M40 6V24A6 6 0 0 1 40 36V54")),
    ("connection_point_closed", "Connection point, not connected (closed)", "Место присоединения несоединённое (закрыто)", body("M10 30H60", "M54 24L66 36M66 24L54 36")),
    ("pipe_with_riser", "Pipeline with vertical riser", "Трубопровод с вертикальным стояком", piped(extra=dot(40, 30))),
    ("hose", "Flexible pipeline, hose", "Трубопровод гибкий, шланг", body("M8 24H22", "M22 24A18 14 0 0 0 58 24", "M58 24H72", extra=dot(22, 24) + dot(58, 24))),
    ("insulated_section", "Insulated pipeline section", "Изолированный участок трубопровода", body("M6 30H74", "M22 18V42", "M58 18V42", "M22 42L28 18L34 42L40 18L46 42L52 18L58 42")),
    ("pipe_in_casing", "Pipeline in a casing pipe", "Трубопровод в трубе (футляре)", body("M6 30H74", "M24 18V24H56V18", "M24 42V36H56V42")),
    ("pipe_in_gland", "Pipeline through a gland", "Трубопровод в сальнике", body("M6 30H74", "M24 18V24H56V18", "M24 42V36H56V42", "M40 18V24", "M40 42V36")),
]

JOINTS = [
    ("joint_detachable", "Detachable pipe joint, general", "Соединение трубопроводов разъёмное, общее обозначение", piped("M40 20V40")),
    ("joint_flanged", "Flanged joint", "Соединение разъёмное фланцевое", piped("M37 20V40", "M43 20V40")),
    ("joint_union", "Threaded union joint", "Соединение штуцерное резьбовое", piped("M44 20H37V40H44", "M41 25V35")),
    ("joint_coupling", "Threaded coupling joint", "Соединение муфтовое резьбовое", piped("M30 24H50", "M30 36H50")),
    ("joint_elastic", "Elastic coupling joint", "Соединение муфтовое эластичное", piped("M28 25H35A5 5 0 0 1 45 25H52", "M28 35H35A5 5 0 0 0 45 35H52")),
    ("swivel_joint", "Swivel joint (single-line)", "Поворотное соединение однолинейное", piped(f'M52 30A12 12 0 1 1 40 18', extra='<path d="M38 14L46 18L38 22Z" fill="#000"/>')),
    ("end_detachable", "Pipe end for detachable joint, general", "Конец трубопровода под разъёмное соединение, общее", body("M8 30H64", "M60 22V38")),
    ("end_flanged", "Pipe end for flanged joint", "Конец трубопровода под фланцевое соединение", body("M8 30H62", "M62 22V38")),
    ("end_union", "Pipe end for threaded union", "Конец трубопровода под штуцерное резьбовое соединение", body("M8 30H62", "M66 22H62V38H66")),
    ("end_coupling", "Pipe end for threaded coupling", "Конец трубопровода под муфтовое резьбовое соединение", body("M8 30H68", "M56 25H68", "M56 35H68")),
    ("end_elastic", "Pipe end for elastic coupling", "Конец трубопровода под муфтовое эластичное соединение", body("M8 30H66", "M56 25H60A6 6 0 0 1 66 20", "M56 35H60A6 6 0 0 0 66 40")),
    ("cap_general", "Pipe end with plug, general", "Конец трубопровода с заглушкой (пробкой), общее", body("M8 30H60", "M65 22V38")),
    ("cap_flanged", "Pipe end with flanged blind", "Конец трубопровода с заглушкой фланцевый", body("M8 30H62", "M62 22V38", "M67 22V38")),
    ("cap_threaded", "Pipe end with threaded plug", "Конец трубопровода с заглушкой резьбовой", body("M8 30H64", "M64 22V38", "M62 20H68V40H62")),
]

FITTINGS = [
    ("elbow", "Elbow (bend)", "Отвод (колено)", body("M30 52V20H58")),
    ("manifold", "Manifold, header, distributor", "Разветвитель, коллектор, гребёнка", body("M8 36H72", "M24 36V24", "M40 36V24", "M56 36V24")),
    ("siphon_trap", "Siphon (water seal)", "Сифон (гидрозатвор)", body("M28 10V40A8 8 0 0 0 44 40V16H60")),
    ("reducer_general", "Reducer, general", "Переход, патрубок переходный, общее обозначение", body("M24 30L56 20V40Z")),
    ("reducer_flanged", "Reducer, flanged", "Переход фланцевый", body("M24 30L56 20V40Z", "M24 20V40", "M56 18V42")),
    ("reducer_union", "Reducer, union (threaded)", "Переход штуцерный", body("M24 30L56 20V40Z", "M20 18H24V42H20", "M60 18H56V42H60")),
]

COMPENSATORS = [
    ("compensator_general", "Expansion joint (compensator), general", "Компенсатор, общее обозначение", body("M10 48H26V24A14 14 0 0 1 54 24V48H70")),
    ("compensator_u", "U-shaped expansion loop", "Компенсатор П-образный", body("M10 48H22Q26 48 26 44V14H54V44Q54 48 58 48H70")),
    ("compensator_lyre", "Lyre-shaped expansion loop", "Компенсатор лирообразный", body("M10 48H34A16 16 0 1 1 46 48H70")),
    ("compensator_lens", "Lens expansion joint", "Компенсатор линзовый", piped(extra=f'<ellipse cx="40" cy="30" rx="5" ry="11" {LINE}/>')),
    ("compensator_wave", "Corrugated (wave) expansion joint", "Компенсатор волнистый", body("M10 16C10 52 32 52 32 30C32 18 48 18 48 30C48 52 70 52 70 16")),
    ("compensator_z", "Z-shaped expansion joint", "Компенсатор Z-образный", body("M10 30H22V22L58 42V34H70")),
    ("compensator_bellows", "Bellows expansion joint", "Компенсатор сильфонный", body("M8 30H26", "M54 30H72", "M28 18H52V42H28Z", "M34 18V42", "M40 18V42", "M46 18V42", "M28 18L24 30L28 42", "M52 18L56 30L52 42")),
    ("compensator_ring", "Ring (loop) expansion joint", "Компенсатор кольцеобразный", body("M10 48H30L46 40A13 13 0 1 0 34 40L50 48H70")),
    ("compensator_telescopic", "Telescopic expansion joint", "Компенсатор телескопический", body("M8 30H30", "M30 22V38", "M30 22H54", "M30 38H54", "M40 30H72")),
    ("insert_damping", "Damping (shock-absorbing) insert", "Вставка амортизационная", body("M8 30H20", "M60 30H72", "M20 24V36", "M60 24V36", "M20 36L30 24V36L40 24V36L50 24V36L60 24")),
    ("insert_sound", "Sound-insulating insert", "Вставка звукоизолирующая", body("M8 30H28", "M52 30H72", "M28 22H52V38H28Z", "M28 22L20 14M52 22L60 14M28 38L20 46M52 38L60 46")),
    ("insert_electric", "Electrically insulating insert", "Вставка электроизолирующая", body("M8 30H30", "M50 30H72", "M30 24H50V36H30Z", "M46 14L36 30H44L34 46", extra='<path d="M31 41L34 46L37 42Z" fill="#000"/>')),
]

DEVICES = [
    ("restriction_viscous", "Flow restriction, viscosity dependent", "Место сопротивления с расходом, зависящим от вязкости", piped("M30 18Q40 26 50 18", "M30 42Q40 34 50 42")),
    ("orifice_plate", "Flow restriction, viscosity independent (orifice, flow nozzle, diaphragm)", "Место сопротивления, не зависящее от вязкости (шайба дроссельная, сужающее устройство, диафрагма)", piped("M32 18L40 26L48 18", "M32 42L40 34L48 42")),
    ("water_hammer_arrester", "Water hammer arrester", "Гаситель гидравлического удара", body("M8 30H22", "M58 30H72", "M22 16H58V44H22Z", "M30 22H50", "M30 38H50", "M30 22V26", "M30 38V34", "M50 22V26", "M50 38V34", "M32 30H46", extra='<path d="M44 26L50 30L44 34Z" fill="#000"/>')),
    ("rupture_membrane", "Rupture membrane", "Мембрана прорыва", body("M8 30H26", "M54 30H72", "M26 10H54V50H26Z", "M40 10V50", "M36 10V16", "M44 10V16", "M36 50V44", "M44 50V44")),
    ("spray_nozzle", "Spray nozzle (atomizer)", "Форсунка", body("M8 30H70", "M54 30L66 18", "M54 30L66 42", extra=dot(54, 30))),
    ("air_intake_atmosphere", "Air intake from atmosphere", "Заборник воздуха из атмосферы", body("M8 30H52", "M60 14V20A10 10 0 0 0 60 40V46")),
]

SUPPORTS = [
    ("support_fixed", "Pipe support, fixed (anchor)", "Опора трубопровода неподвижная", body("M10 30H70", "M30 20L50 40M50 20L30 40")),
    ("support_movable", "Pipe support, movable (general)", "Опора подвижная, общее обозначение", body("M14 16H66", "M28 24H52", "M40 24V50")),
    ("support_ball", "Pipe support, ball type", "Опора шариковая", body("M14 18H66", extra=f'<circle cx="35" cy="27" r="5" {LINE}/><circle cx="45" cy="27" r="5" {LINE}/>')),
    ("support_guide", "Pipe support, guide", "Опора направляющая", body("M14 22H66", "M30 16H50", "M28 28H52", "M40 28V52")),
    ("support_sliding", "Pipe support, sliding", "Опора скользящая", body("M14 22H66", "M30 30H50", "M14 38H66")),
    ("support_roller", "Pipe support, roller", "Опора катковая", body("M14 18H66", "M28 38H52", extra=f'<circle cx="40" cy="28" r="6" {LINE}/>')),
    ("support_spring", "Pipe support, spring (resilient)", "Опора упругая", body("M14 14H66", "M40 14L33 20L47 26L33 32L47 38L33 44L40 48")),
    ("hanger_fixed", "Pipe hanger, fixed", "Подвеска неподвижная", body("M14 50H66", "M40 14V50", "M30 14H50")),
    ("hanger_guide", "Pipe hanger, guide", "Подвеска направляющая", body("M40 8V34", "M26 34H54", "M30 42H50")),
    ("hanger_spring", "Pipe hanger, spring", "Подвеска упругая", body("M14 50H66", "M40 10L33 16L47 22L33 28L47 34L33 40L40 44")),
]

if __name__ == "__main__":
    rows = [(code, en, ru, "Трубопроводные элементы", drawing)
            for code, en, ru, drawing in PIPES + JOINTS + FITTINGS + COMPENSATORS + DEVICES + SUPPORTS]
    store("GOST 2.784", "gost", rows, NOTE)

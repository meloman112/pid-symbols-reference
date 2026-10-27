"""Символы ISA 5.1 из книги T. Kuphaldt «Lessons in Industrial Instrumentation» (CC BY 4.0), раздел 7.5.
PDF: https://www.ibiblio.org/kuphaldt/socratic/sinst/book/liii_2v32.pdf
Запуск: python scripts/harvest_kuphaldt.py путь/к/liii.pdf [--preview]

Символы находятся как связные области растра страницы (подписи стёрты),
подпись берётся из pdftotext -bbox, символ вырезается векторно через pdftocairo -svg."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import db

DPI = 100
SCALE = DPI / 72
GAP = 6  # пикселей: штрихи ближе этого считаются одним символом
PAD = 5  # пунктов вокруг вырезанного символа
SOURCE = "https://www.ibiblio.org/kuphaldt/socratic/sinst/book/liii_2v32.pdf"
LICENSE = "CC BY 4.0"
AUTHOR = "Tony R. Kuphaldt, Lessons in Industrial Instrumentation, §7.5"

# страница PDF → (категория, префикс имени); на 572 кружки приборов идут отдельной сеткой
PAGES = {571: ("Линии связи", "Line"), 572: ("Присоединения к процессу", "Process connection"),
         573: ("Арматура", "Valve"), 574: ("Приводы арматуры", "Actuator"), 575: ("Положение при отказе", "Valve failure mode"),
         576: ("Уровнемеры", "Level element"), 577: ("Расходомеры", "Flow element"), 578: ("Расходомеры", "Flow element")}
SKIP = {"Open", "Closed"}  # пояснение «Valve status», а не символы
BUBBLE_ROWS = {"Discrete": "discrete instrument", "Shared": "shared display/control", "Computer": "computer function",
               "Logic": "PLC / logic"}
BUBBLE_COLS = ["field mounted", "main panel, front", "main panel, rear (inaccessible)",
               "auxiliary panel, front", "auxiliary panel, rear (inaccessible)"]


def caption_lines(pdf, page):
    """Строки текста страницы: (x0, y0, x1, y1, текст) в пунктах."""
    xml = subprocess.run(["pdftotext", "-bbox-layout", "-f", str(page), "-l", str(page), pdf, "-"],
                         capture_output=True, text=True, check=True).stdout
    root = ElementTree.fromstring(re.sub(r"<!DOCTYPE[^>]*>", "", xml).replace('xmlns="http://www.w3.org/1999/xhtml"', ""))
    lines = []
    for line in root.iter("line"):
        text = " ".join(w.text for w in line.iter("word"))
        lines.append((float(line.get("xMin")), float(line.get("yMin")), float(line.get("xMax")), float(line.get("yMax")), text))
    return lines


def is_caption(line):
    """Подписи — строки обычного кегля со строчными буквами; надписи внутри символов (M, LT, Radar) мельче или заглавные."""
    x0, y0, x1, y1, text = line
    return y1 - y0 >= 8.5 and bool(re.search(r"[a-z]{3}", text)) and text != "(or)"


def components(image):
    """Ограничивающие рамки связных областей бинарного изображения (8-связность, с зазором GAP)."""
    width, height = image.size
    pixels = image.load()
    seen = set()
    boxes = []
    for y in range(height):
        for x in range(width):
            if pixels[x, y] or (x, y) in seen:
                continue
            stack, box = [(x, y)], [x, y, x, y]
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop()
                box = [min(box[0], cx), min(box[1], cy), max(box[2], cx), max(box[3], cy)]
                for nx in range(max(cx - GAP, 0), min(cx + GAP + 1, width)):
                    for ny in range(max(cy - GAP, 0), min(cy + GAP + 1, height)):
                        if not pixels[nx, ny] and (nx, ny) not in seen:
                            seen.add((nx, ny))
                            stack.append((nx, ny))
            boxes.append(box)
    return boxes


def page_image(pdf, page, lines):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(page), "-l", str(page), "-gray", "-png", pdf, f"{tmp}/p"], check=True)
        image = Image.open(next(Path(tmp).glob("p*.png"))).point(lambda v: 0 if v < 160 else 255).convert("1")
    draw = ImageDraw.Draw(image)
    for x0, y0, x1, y1, text in lines:
        if is_caption((x0, y0, x1, y1, text)) or y0 < 110:  # подписи и колонтитул
            draw.rectangle([x0 * SCALE - 1, y0 * SCALE - 1, x1 * SCALE + 1, y1 * SCALE + 1], fill=1)
    return image


def to_points(box):
    return [v / SCALE for v in box]


def caption_for(box, captions):
    """Подпись внутри рамки символа или ближайшая над ним, пересекающаяся по горизонтали."""
    x0, y0, x1, y1 = box
    inside = [c for c in captions if x0 <= (c[0] + c[2]) / 2 <= x1 and y0 <= c[1] <= y1]
    above = [c for c in captions if c[3] <= y0 + 2 and c[0] < x1 + 15 and c[2] > x0 - 15 and y0 - c[3] < 45]
    chosen = inside or sorted(above, key=lambda c: y0 - c[3])[:1]
    if not chosen:
        return None
    lead = chosen[0]
    block = [c for c in captions if abs((c[0] + c[2]) / 2 - (lead[0] + lead[2]) / 2) < 30 and 0 <= lead[1] - c[1] < 25]
    return " ".join(c[4] for c in sorted(block, key=lambda c: c[1]))


def bubble_name(box, lines):
    cy = (box[1] + box[3]) / 2
    row = min((l for l in lines if l[4].split()[0] in BUBBLE_ROWS), key=lambda l: abs((l[1] + l[3]) / 2 - cy))
    column = int((box[0] - 160) // 75)
    return f"Instrument bubble: {BUBBLE_ROWS[row[4].split()[0]]}, {BUBBLE_COLS[column]}"


def symbols(pdf, page):
    lines = caption_lines(pdf, page)
    captions = [l for l in lines if is_caption(l) and l[1] > 110]
    boxes = [to_points(b) for b in components(page_image(pdf, page, lines))]
    boxes = [b for b in boxes if not any(o is not b and contains(o, b) for o in boxes)]
    merged, orphans = {}, []
    for box in boxes:
        if box[2] - box[0] < 8 and box[3] - box[1] < 8:
            continue
        if page == 572 and box[1] > 300:
            name = bubble_name(box, lines) if 15 < box[2] - box[0] < 35 and 15 < box[3] - box[1] < 35 else None
        else:
            name = caption_for(box, captions)
        if name is None:
            if page == 576:
                orphans.append(box)
            continue
        merged[name] = union(merged.get(name, box), box)
    for box in orphans:  # уровнемеры: ёмкость под прибором без своей подписи (надпись Radar/US мелкая)
        owner = [n for n, b in merged.items() if b[0] < box[2] and b[2] > box[0] and 0 <= box[1] - b[3] < 40]
        if owner:
            merged[owner[0]] = union(merged[owner[0]], box)
    yield from ((n, b) for n, b in merged.items() if n not in SKIP)


def union(a, b):
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def contains(outer, inner):
    return outer[0] <= inner[0] and outer[1] <= inner[1] and outer[2] >= inner[2] and outer[3] >= inner[3]


def page_svg(pdf, page):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftocairo", "-svg", "-f", str(page), "-l", str(page), pdf, f"{tmp}/p.svg"], check=True)
        return Path(f"{tmp}/p.svg").read_text()


def crop_svg(page_text, box):
    """Вся страница с viewBox на области символа: координаты SVG страницы совпадают с pdftotext (пункты)."""
    x, y = box[0] - PAD, box[1] - 1  # сверху почти без поля: там подпись из книги
    width, height = box[2] - box[0] + 2 * PAD, box[3] - box[1] + PAD + 1
    return re.sub(r'width="[\d.]+(pt)?" height="[\d.]+(pt)?" viewBox="[^"]+"',
                  f'width="{width * 3:.0f}" height="{height * 3:.0f}" viewBox="{x:.1f} {y:.1f} {width:.1f} {height:.1f}"',
                  page_text, count=1)


def main(pdf, preview):
    out = db.ROOT / "svg" / "isa"
    out.mkdir(parents=True, exist_ok=True)
    conn = db.connect()
    for page, (page_category, prefix) in PAGES.items():
        page_text = page_svg(pdf, page)
        for caption, box in symbols(pdf, page):
            bubble = caption.startswith("Instrument bubble")
            name = caption if bubble else f"{prefix}: {caption.replace('Averging', 'Averaging')}"
            category = "Приборы" if bubble else page_category
            code = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
            print(page, f"{box[0]:.0f},{box[1]:.0f},{box[2]:.0f},{box[3]:.0f}", name)
            if preview:
                continue
            (out / f"{code}.svg").write_text(crop_svg(page_text, box))
            conn.execute(
                """INSERT INTO symbols (standard, code, name_en, category, svg_path, source_url, license, author)
                   VALUES ('ISA 5.1', ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT (standard, code) DO UPDATE SET svg_path = excluded.svg_path""",
                (code, name, category, f"svg/isa/{code}.svg", SOURCE, LICENSE, AUTHOR))
    conn.commit()


if __name__ == "__main__":
    main(sys.argv[1], "--preview" in sys.argv)

"""Приводы арматуры DIN 2429 с Wikimedia Commons: в ISO-наборе Commons их нет."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest_iso import clean, db, download, file_infos

TITLES = [f"File:Actuator ({kind}) (DIN 2429).svg" for kind in ("general", "manual", "motor", "diaphragm")]
SVG_DIR = db.ROOT / "svg" / "din"


def main():
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    conn = db.connect()
    for page in file_infos(TITLES):
        info = page["imageinfo"][0]
        meta = info["extmetadata"]
        name_en = re.sub(r"\s*\(DIN 2429\)$", "", page["title"][5:-4])
        code = re.sub(r"[^a-z0-9]+", "_", name_en.lower()).strip("_")
        svg_path = SVG_DIR / f"{code}.svg"
        download(info["url"], svg_path)
        conn.execute(
            """INSERT INTO symbols (standard, code, name_en, category, svg_path, source_url, license, author)
               VALUES ('DIN 2429', ?, ?, 'Приводы арматуры', ?, ?, ?, ?)
               ON CONFLICT (standard, code) DO UPDATE SET svg_path = excluded.svg_path""",
            (code, name_en, f"svg/din/{code}.svg", info["descriptionurl"],
             clean(meta.get("LicenseShortName", {}).get("value", "")), clean(meta.get("Artist", {}).get("value", ""))))
        conn.commit()
        print(name_en)


if __name__ == "__main__":
    main()

"""Скачивает SVG-символы ISO 10628-2 с Wikimedia Commons в svg/iso и пишет метаданные в db."""
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import db

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "pid-symbols-reference/0.1 (https://github.com/meloman112/pid-symbols-reference)"}
SVG_DIR = Path(__file__).resolve().parent.parent / "svg" / "iso"


def api(**params):
    query = urllib.parse.urlencode({"format": "json", **params})
    request = urllib.request.Request(f"{API}?{query}", headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 — фиксированный https-хост
        return json.load(response)


def download(url, path):
    if path.exists():
        return
    request = urllib.request.Request(url, headers=HEADERS)
    for wait in (5, 20, 60):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 — https-хост Commons
                path.write_bytes(response.read())
            time.sleep(1)
            return
        except urllib.error.HTTPError as error:
            if error.code != 429:
                raise
            time.sleep(wait)
    raise RuntimeError(f"Commons 429 не отпускает: {url}")


def find_titles():
    titles, offset = [], 0
    while offset is not None:
        data = api(action="query", list="search", srsearch="ISO 10628 filetype:drawing",
                   srnamespace=6, srlimit=100, sroffset=offset)
        titles += [hit["title"] for hit in data["query"]["search"]]
        offset = data.get("continue", {}).get("sroffset")
    return [t for t in titles if t.endswith(".svg") and "10628-2" in t and "Sheet" not in t]


def file_infos(titles):
    for i in range(0, len(titles), 40):
        data = api(action="query", titles="|".join(titles[i:i + 40]), prop="imageinfo",
                   iiprop="url|extmetadata")
        yield from data["query"]["pages"].values()


def clean(text):
    return re.sub(r"<[^>]+>", "", text).strip()


def main():
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    conn = db.connect()
    for page in file_infos(find_titles()):
        info = page["imageinfo"][0]
        meta = info["extmetadata"]
        name_en = re.sub(r"\s*[-(]*\s*ISO 10628-2\)?\s*$", "", page["title"][5:-4]).strip(" -(,")
        code = re.sub(r"[^a-z0-9]+", "_", name_en.lower()).strip("_")
        svg_path = SVG_DIR / f"{code}.svg"
        download(info["url"], svg_path)
        reg_no = re.search(r"REG#:\s*(\w+)", meta.get("ImageDescription", {}).get("value", ""))
        conn.execute(
            """INSERT INTO symbols (standard, code, name_en, reg_no, svg_path, source_url, license, author)
               VALUES ('ISO 10628-2', ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT (standard, code) DO UPDATE SET reg_no = excluded.reg_no, svg_path = excluded.svg_path,
                   source_url = excluded.source_url, license = excluded.license, author = excluded.author""",
            (code, name_en, reg_no and reg_no.group(1), str(svg_path.relative_to(svg_path.parents[2])),
             info["descriptionurl"], clean(meta.get("LicenseShortName", {}).get("value", "")),
             clean(meta.get("Artist", {}).get("value", ""))),
        )
        conn.commit()
        print(name_en)


if __name__ == "__main__":
    main()

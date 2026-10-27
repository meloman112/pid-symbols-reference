import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "pid.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY,
    standard TEXT NOT NULL,
    code TEXT NOT NULL,
    name_en TEXT NOT NULL,
    reg_no TEXT,
    name_ru TEXT,
    category TEXT,
    purpose TEXT,
    placement TEXT,
    mistakes TEXT,
    similar TEXT,
    svg_path TEXT,
    source_url TEXT,
    license TEXT,
    author TEXT,
    UNIQUE (standard, code)
);
CREATE VIRTUAL TABLE IF NOT EXISTS symbols_fts USING fts5(
    name_en, name_ru, reg_no, category, purpose, placement, mistakes,
    content='symbols', content_rowid='id', tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER IF NOT EXISTS symbols_ai AFTER INSERT ON symbols BEGIN
    INSERT INTO symbols_fts (rowid, name_en, name_ru, reg_no, category, purpose, placement, mistakes)
    VALUES (new.id, new.name_en, new.name_ru, new.reg_no, new.category, new.purpose, new.placement, new.mistakes);
END;
CREATE TRIGGER IF NOT EXISTS symbols_ad AFTER DELETE ON symbols BEGIN
    INSERT INTO symbols_fts (symbols_fts, rowid, name_en, name_ru, reg_no, category, purpose, placement, mistakes)
    VALUES ('delete', old.id, old.name_en, old.name_ru, old.reg_no, old.category, old.purpose, old.placement, old.mistakes);
END;
CREATE TRIGGER IF NOT EXISTS symbols_au AFTER UPDATE ON symbols BEGIN
    INSERT INTO symbols_fts (symbols_fts, rowid, name_en, name_ru, reg_no, category, purpose, placement, mistakes)
    VALUES ('delete', old.id, old.name_en, old.name_ru, old.reg_no, old.category, old.purpose, old.placement, old.mistakes);
    INSERT INTO symbols_fts (rowid, name_en, name_ru, reg_no, category, purpose, placement, mistakes)
    VALUES (new.id, new.name_en, new.name_ru, new.reg_no, new.category, new.purpose, new.placement, new.mistakes);
END;
CREATE TABLE IF NOT EXISTS letters (
    standard TEXT NOT NULL,
    letter TEXT NOT NULL,
    variable TEXT,
    modifier TEXT,
    function TEXT,
    PRIMARY KEY (standard, letter)
);
CREATE TABLE IF NOT EXISTS assemblies (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    standard TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    notes TEXT NOT NULL,
    svg_path TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assembly_parts (
    assembly_id INTEGER NOT NULL REFERENCES assemblies(id),
    symbol_id INTEGER NOT NULL REFERENCES symbols(id),
    label TEXT NOT NULL
);
"""

FIELDS = "id, standard, code, name_en, reg_no, name_ru, category, purpose, placement, mistakes, similar, svg_path"


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _fts_query(text):
    return " OR ".join(f'"{word}"*' for word in text.replace('"', " ").split())


def _filters(standard, category, alias=""):
    clauses, args = [], []
    if standard:  # "GOST" без номера — все ГОСТы
        clauses.append(f"{alias}standard = ?" if " " in standard else f"{alias}standard LIKE ? || ' %'")
        args.append(standard)
    if category:
        clauses.append(f"{alias}category = ?")
        args.append(category)
    return clauses, args


def search(text, limit=10, standard=None, category=None):
    if not text.strip():
        return list_all(standard, limit, category)
    clauses, args = _filters(standard, category, "s.")
    sql = f"""SELECT {', '.join('s.' + f.strip() for f in FIELDS.split(','))} FROM symbols_fts
              JOIN symbols s ON s.id = symbols_fts.rowid
              WHERE symbols_fts MATCH ? {''.join(' AND ' + c for c in clauses)}
              ORDER BY rank LIMIT ?"""
    return [dict(row) for row in connect().execute(sql, [_fts_query(text)] + args + [limit])]


def list_all(standard=None, limit=500, category=None):
    clauses, args = _filters(standard, category)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = connect().execute(
        f"SELECT {FIELDS} FROM symbols {where} ORDER BY category, name_ru LIMIT ?", args + [limit])
    return [dict(row) for row in rows]


def facets():
    """Счётчики для фильтров: стандарты и категории."""
    conn = connect()
    count = lambda column: [{"name": r[0], "count": r[1]} for r in conn.execute(
        f"SELECT {column}, count(*) FROM symbols GROUP BY 1 ORDER BY 2 DESC")]
    return {"standards": count("standard"), "categories": count("category"),
            "assemblies": conn.execute("SELECT count(*) FROM assemblies").fetchone()[0]}


def related(symbol, limit=6):
    """Тот же элемент в других стандартах: поиск по русскому названию без уточнений в скобках."""
    name = symbol["name_ru"].split("(")[0].split(",")[0]
    words = [w for w in name.split() if len(w) > 3][:2]
    if not words:
        return []
    sql = f"""SELECT {', '.join('s.' + f.strip() for f in FIELDS.split(','))} FROM symbols_fts
              JOIN symbols s ON s.id = symbols_fts.rowid
              WHERE symbols_fts MATCH ? AND s.standard != ? ORDER BY rank LIMIT ?"""
    query = " AND ".join(f'name_ru:"{w}"*' for w in words)
    return [dict(row) for row in connect().execute(sql, (query, symbol["standard"], limit))]


def get(symbol_id):
    row = connect().execute(f"SELECT {FIELDS}, source_url, license, author FROM symbols WHERE id = ?",
                            (symbol_id,)).fetchone()
    if not row:
        return None
    symbol = dict(row)
    symbol["used_in"] = [dict(r) for r in connect().execute(
        """SELECT DISTINCT a.id, a.name FROM assembly_parts p JOIN assemblies a ON a.id = p.assembly_id
           WHERE p.symbol_id = ? ORDER BY a.id""", (symbol_id,))]
    return symbol


def assemblies():
    return [dict(r) for r in connect().execute("SELECT id, code, standard, name, description, svg_path FROM assemblies ORDER BY id")]


def assembly(assembly_id):
    conn = connect()
    row = conn.execute("SELECT * FROM assemblies WHERE id = ?", (assembly_id,)).fetchone()
    if not row:
        return None
    result = dict(row)
    result["notes"] = result["notes"].split("\n")
    result["parts"] = [dict(r) for r in conn.execute(
        """SELECT p.label, s.id, s.standard, s.name_ru FROM assembly_parts p JOIN symbols s ON s.id = p.symbol_id
           WHERE p.assembly_id = ? ORDER BY p.rowid""", (assembly_id,))]
    return result


EDITABLE = ("name_ru", "category", "purpose", "placement", "mistakes", "similar")


def update(symbol_id, values):
    conn = connect()
    conn.execute(f"UPDATE symbols SET {', '.join(f + ' = ?' for f in EDITABLE)} WHERE id = ?",
                 [values[f] for f in EDITABLE] + [symbol_id])
    conn.commit()


def decode_tag(tag):
    """Расшифровка буквенной части тега (PDIT-101 → P, D, I, T) по всем стандартам из таблицы letters.
    Для второй и следующих букв показаны и уточняющее, и функциональное значение — выбор за читающим."""
    letters = "".join(ch for ch in tag.upper().split("-")[0] if ch.isalpha())
    conn = connect()
    result = []
    for position, letter in enumerate(letters):
        for row in conn.execute("SELECT * FROM letters WHERE letter = ? ORDER BY standard", (letter,)):
            meanings = [row["variable"]] if position == 0 else [row["modifier"], row["function"]]
            result.append({"letter": letter, "position": position + 1, "standard": row["standard"],
                           "meaning": " | ".join(m for m in meanings if m) or "—"})
    return result


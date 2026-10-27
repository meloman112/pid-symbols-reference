"""export: режет необогащённые символы на work/todo_N.json. apply: заливает work/done_*.json в базу."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import db

WORK = db.ROOT / "work"
CHUNK = 25
FIELDS = ("name_ru", "category", "purpose", "placement", "mistakes", "similar")


def export():
    WORK.mkdir(exist_ok=True)
    todo = [dict(row) for row in db.connect().execute(
        "SELECT id, standard, name_en, name_ru, category FROM symbols WHERE purpose IS NULL ORDER BY id")]
    for number, start in enumerate(range(0, len(todo), CHUNK)):
        (WORK / f"todo_{number:02d}.json").write_text(
            json.dumps(todo[start:start + CHUNK], ensure_ascii=False, indent=1))
    print(f"{len(todo)} символов, {-(-len(todo) // CHUNK)} файлов")


def apply():
    conn = db.connect()
    for path in sorted(WORK.glob("done_*.json")):
        for item in json.loads(path.read_text()):
            missing = [f for f in FIELDS if not item.get(f)]
            if missing:
                raise ValueError(f"{path.name} id={item.get('id')}: нет полей {missing}")
            conn.execute(f"UPDATE symbols SET {', '.join(f + ' = ?' for f in FIELDS)} WHERE id = ?",
                         [item[f] for f in FIELDS] + [item["id"]])
        conn.commit()
        path.rename(path.with_suffix(".applied"))
        print("применён", path.name)


if __name__ == "__main__":
    {"export": export, "apply": apply}[sys.argv[1]]()

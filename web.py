"""Веб-справочник без LLM: JSON API поверх SQLite FTS5, страница справочника и редактор схем.
Запуск: EDIT_PASSWORD=... python web.py [порт]. Без EDIT_PASSWORD всё доступно только на чтение."""
import hashlib
import hmac
import json
import mimetypes
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import db

STATIC = db.ROOT / "static"
TAG = re.compile(r"^[A-Z]{2,6}(-?\d+\w*)?$")
PASSWORD = os.environ.get("EDIT_PASSWORD", "")
TOKEN = hmac.new(PASSWORD.encode(), b"pid-ref-session", hashlib.sha256).hexdigest()
MAX_BODY = 5_000_000


def api_search(args):
    query = args.get("q", [""])[0].strip()
    items = db.search(query, 500, args.get("standard", [None])[0], args.get("category", [None])[0])
    return {"items": items, "tag": db.decode_tag(query) if TAG.match(query) else None}


def api_symbol(symbol_id):
    symbol = db.get(symbol_id)
    if symbol:
        symbol["related"] = db.related(symbol)
    return symbol


def tail_id(path):
    return int(path.rsplit("/", 1)[1])


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, content_type, body, headers=()):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def json(self, data, status=200, headers=()):
        self.reply(status, "application/json; charset=utf-8", json.dumps(data, ensure_ascii=False).encode(), headers)

    def file(self, path):
        if ".." in path.parts or not path.is_file():
            return self.reply(404, "text/plain", b"not found")
        self.reply(200, mimetypes.guess_type(path.name)[0] or "application/octet-stream", path.read_bytes())

    def body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY:
            raise ValueError("слишком большой запрос")
        return json.loads(self.rfile.read(length))

    def authorized(self):
        cookies = dict(c.strip().split("=", 1) for c in self.headers.get("Cookie", "").split(";") if "=" in c)
        return bool(PASSWORD) and hmac.compare_digest(cookies.get("auth", ""), TOKEN)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            return self.file(STATIC / "index.html")
        if url.path == "/editor":
            return self.file(STATIC / "editor.html")
        if url.path.startswith(("/static/", "/svg/")):
            return self.file(db.ROOT / url.path.lstrip("/"))
        if url.path == "/api/facets":
            return self.json(db.facets())
        if url.path == "/api/search":
            return self.json(api_search(parse_qs(url.query)))
        if url.path == "/api/tag":
            return self.json(db.decode_tag(parse_qs(url.query).get("q", [""])[0]))
        if url.path == "/api/assemblies":
            return self.json(db.assemblies())
        if url.path.startswith("/api/assembly/"):
            found = db.assembly(tail_id(url.path))
            return self.json(found) if found else self.json({"error": "узел не найден"}, 404)
        if url.path.startswith("/api/symbol/"):
            symbol = api_symbol(tail_id(url.path))
            return self.json(symbol) if symbol else self.json({"error": "символ не найден"}, 404)
        if url.path == "/api/drawings":
            return self.json(db.drawings())
        if url.path.startswith("/api/drawing/"):
            found = db.drawing(tail_id(url.path))
            return self.json(found) if found else self.json({"error": "схема не найдена"}, 404)
        if url.path == "/api/session":
            return self.json({"editing": bool(PASSWORD), "authorized": self.authorized()})
        self.reply(404, "text/plain", b"not found")

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/login":
            return self.login()
        if not PASSWORD:
            return self.json({"error": "правка выключена: задайте EDIT_PASSWORD на сервере"}, 403)
        if not self.authorized():
            return self.json({"error": "нужен пароль"}, 401)
        if url.path.startswith("/api/symbol/"):
            return self.save_symbol(tail_id(url.path))
        if url.path == "/api/drawings":
            return self.save_drawing()
        self.json({"error": "не найдено"}, 404)

    def do_DELETE(self):
        url = urlparse(self.path)
        if not self.authorized():
            return self.json({"error": "нужен пароль"}, 401)
        if not url.path.startswith("/api/drawing/"):
            return self.json({"error": "не найдено"}, 404)
        db.delete_drawing(tail_id(url.path))
        self.json({"ok": True})

    def login(self):
        password = str(self.body().get("password", ""))
        if not PASSWORD or not hmac.compare_digest(password, PASSWORD):
            return self.json({"error": "неверный пароль"}, 401)
        cookie = f"auth={TOKEN}; Path=/; HttpOnly; SameSite=Strict; Max-Age=2592000"
        self.json({"ok": True}, headers=[("Set-Cookie", cookie)])

    def save_symbol(self, symbol_id):
        values = self.body()
        missing = [f for f in db.EDITABLE if not str(values.get(f, "")).strip()]
        if missing:
            return self.json({"error": f"заполните поля: {', '.join(missing)}"}, 400)
        db.update(symbol_id, {f: values[f].strip() for f in db.EDITABLE})
        self.json(api_symbol(symbol_id))

    def save_drawing(self):
        values = self.body()
        name = str(values.get("name", "")).strip()
        if not name or not isinstance(values.get("data"), dict):
            return self.json({"error": "нужны название схемы и её содержимое"}, 400)
        drawing_id = db.save_drawing(values.get("id"), name, json.dumps(values["data"], ensure_ascii=False))
        self.json(db.drawing(drawing_id))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()

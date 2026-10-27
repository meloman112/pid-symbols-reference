"""Веб-справочник без LLM: JSON API поверх SQLite FTS5 + одна статическая страница. Запуск: python web.py [порт]"""
import json
import mimetypes
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import db

STATIC = db.ROOT / "static"
TAG = re.compile(r"^[A-Z]{2,6}(-?\d+\w*)?$")


def api_search(args):
    query = args.get("q", [""])[0].strip()
    items = db.search(query, 200, args.get("standard", [None])[0], args.get("category", [None])[0])
    return {"items": items, "tag": db.decode_tag(query) if TAG.match(query) else None}


def api_symbol(symbol_id):
    symbol = db.get(symbol_id)
    if symbol:
        symbol["related"] = db.related(symbol)
    return symbol


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body)

    def json(self, data, status=200):
        self.reply(status, "application/json; charset=utf-8", json.dumps(data, ensure_ascii=False).encode())

    def file(self, path):
        if ".." in path.parts or not path.is_file():
            return self.reply(404, "text/plain", b"not found")
        self.reply(200, mimetypes.guess_type(path.name)[0] or "application/octet-stream", path.read_bytes())

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            return self.file(STATIC / "index.html")
        if url.path.startswith(("/static/", "/svg/")):
            return self.file(db.ROOT / url.path.lstrip("/"))
        if url.path == "/api/facets":
            return self.json(db.facets())
        if url.path == "/api/search":
            return self.json(api_search(parse_qs(url.query)))
        if url.path.startswith("/api/symbol/"):
            symbol = api_symbol(int(url.path.rsplit("/", 1)[1]))
            return self.json(symbol) if symbol else self.json({"error": "символ не найден"}, 404)
        self.reply(404, "text/plain", b"not found")

    def do_POST(self):
        url = urlparse(self.path)
        if not url.path.startswith("/api/symbol/"):
            return self.json({"error": "не найдено"}, 404)
        values = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        missing = [f for f in db.EDITABLE if not str(values.get(f, "")).strip()]
        if missing:
            return self.json({"error": f"заполните поля: {', '.join(missing)}"}, 400)
        symbol_id = int(url.path.rsplit("/", 1)[1])
        db.update(symbol_id, {f: values[f].strip() for f in db.EDITABLE})
        self.json(api_symbol(symbol_id))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()

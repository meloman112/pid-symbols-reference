"""MCP-сервер справочника. Запуск: python mcp_server.py — stdio; python mcp_server.py 8081 — HTTP на http://<хост>:8081/mcp"""
import sys

from mcp.server.fastmcp import FastMCP

import db

# host 0.0.0.0 — чтобы в сети работал HTTP-режим: на localhost FastMCP отклоняет чужие заголовки Host
mcp = FastMCP("pid-ref", host="0.0.0.0")


@mcp.tool()
def search_symbols(query: str, standard: str | None = None, category: str | None = None, limit: int = 10) -> list[dict]:
    """Поиск символа P&ID по названию (RU/EN), назначению, категории или номеру REG ISO.
    standard: 'ISO 10628-2', 'ISA 5.1', 'DIN 2429', 'GOST 21.208', 'GOST 2.784', 'GOST 2.785', 'GOST 2.788'…'GOST 2.795',
    или семейство целиком: 'ISO', 'ISA', 'GOST', 'DIN'.
    category: точное название категории, например 'Теплообменники', 'Арматура', 'Сушильные аппараты'."""
    return db.search(query, limit, standard, category)


@mcp.tool()
def get_symbol(symbol_id: int) -> dict:
    """Полная карточка символа; svg_path — путь к рисунку относительно корня справочника."""
    symbol = db.get(symbol_id)
    if not symbol:
        raise ValueError(f"символ {symbol_id} не найден")
    return symbol


@mcp.tool()
def decode_tag(tag: str) -> list[dict]:
    """Расшифровка тега прибора по буквам (PDIT-101, TIC, LSHH) по ГОСТ 21.208 и ISA 5.1.
    Первая буква — измеряемая величина; у следующих даны уточняющее и функциональное значения."""
    return db.decode_tag(tag)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mcp.settings.port = int(sys.argv[1])
        mcp.run("streamable-http")
    else:
        mcp.run()

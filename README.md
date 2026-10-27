# pid-symbols-reference

Справочник условных обозначений для P&ID и технологических схем: ISO 10628-2, ISA 5.1, ГОСТ 21.208, ГОСТ 2.784, 2.785, 2.788–2.795, DIN 2429.
834 символа. У каждого есть SVG, название RU/EN, стандарт, назначение, где ставить, типичные ошибки и похожие символы.
Ещё есть расшифровка тегов приборов по буквам (PDIT-101, TIC, LSHH) по ГОСТ 21.208 и ISA 5.1.

Есть два входа:
- **Веб** (без LLM): поиск, фильтры по стандарту и категории, карточка символа, скачивание SVG, правка описаний.
- **MCP-сервер**: подключается к Gemini CLI, Claude Code или любому MCP-клиенту, чтобы LLM искала символы в справочнике.

## Запуск

    docker compose up -d

- Веб: http://localhost:8080
- MCP: http://localhost:8081/mcp (streamable HTTP)

Если порты заняты, задайте другие в файле `.env` рядом с `compose.yaml`: `WEB_PORT=8790` и `MCP_PORT=8791`.

База лежит в `data/pid.db` и подключена в контейнеры как volume, поэтому правки из веба сохраняются на диске.

## Подключение MCP

Gemini CLI, файл `~/.gemini/settings.json`:

    {"mcpServers": {"pid-ref": {"httpUrl": "http://<хост>:8081/mcp"}}}

Claude Code, файл `.mcp.json`:

    {"mcpServers": {"pid-ref": {"type": "http", "url": "http://<хост>:8081/mcp"}}}

Инструменты:
- `search_symbols(query, standard, category, limit)` — поиск символов;
- `get_symbol(symbol_id)` — полная карточка символа;
- `decode_tag(tag)` — расшифровка тега прибора по буквам.

MCP только читает базу.

> Внимание: правка описаний в вебе работает без авторизации. Не открывайте порт 8080 в интернет, держите его только в локальной сети.

## Без Docker

    python -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python web.py 8080
    .venv/bin/python mcp_server.py 8081   # без порта запускается по stdio

## Сборка данных

`data/pid.db` уже собрана. Скрипты ниже нужны только для пересборки, повторный запуск ничего не ломает.

    scripts/harvest_iso.py                 # ISO 10628-2: SVG с Wikimedia Commons
    scripts/harvest_din.py                 # приводы DIN 2429 с Commons
    scripts/harvest_kuphaldt.py liii.pdf   # ISA 5.1 из книги Kuphaldt (ссылка на PDF в скрипте)
    scripts/gen_symbols.py                 # ГОСТ 21.208 и 2.785 по рисункам стандартов
    scripts/gen_gost_2_784.py              # ГОСТ 2.784
    scripts/gen_gost_2_788.py … 2_795.py   # ГОСТ 2.788–2.795: оборудование химических производств
    scripts/load_letters.py                # буквенные коды ГОСТ 21.208 и ISA 5.1
    scripts/enrich.py export|apply         # описания: work/todo_*.json → LLM → work/done_*.json → база

Что покрыто, откуда взято и что неточно, описано в `catalog/inventory.md`.

## Лицензии

- Код: MIT, см. `LICENSE`.
- Рисунки ISO 10628-2 и DIN 2429 взяты с Wikimedia Commons под лицензией CC BY-SA 4.0 или Public Domain. Автор и ссылка на источник есть в карточке каждого символа.
- Рисунки ISA 5.1 вырезаны из книги T. R. Kuphaldt «Lessons In Industrial Instrumentation», лицензия CC BY 4.0.
- Рисунки ГОСТ нарисованы заново по таблицам стандартов. Тексты стандартов в репозиторий не входят.
- Шрифт Golos Text — SIL Open Font License.
- Описания сгенерированы LLM и со стандартами не сверялись. Перед использованием в проекте проверьте их по стандарту.

const $ = (selector) => document.querySelector(selector);
const GRID = 10;
const PORT_SNAP = 12; // радиус, в котором линия прилипает к точке подключения
const ACTUATOR_STEM = 24; // от центра рисунка ИМ (ГОСТ 21.208, 80×60) до конца штока
const STANDARD = "GOST";

let doc = { parts: [], lines: [], texts: [] };
let drawingId = null;
let tool = "select";
let selected = null; // { type: "part" | "line" | "text", id }
let draft = null; // линия, которую сейчас рисуют
let drag = null;
let history = [];
let dirty = false;
let palette = [];
let zoom = 1;
let pan = null; // перетаскивание листа пробелом или средней кнопкой
let spaceHeld = false;
const SHEET = { width: 3000, height: 2000 };
const ZOOM_STEP = 1.2;
const shapes = {}; // svg_path → { inner, w, h, box, ports }

const esc = (text) => String(text ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const snap = (value) => Math.round(value / GRID) * GRID;
const label = (standard) => standard.replace("GOST", "ГОСТ");
const nextId = () => Math.max(0, ...doc.parts.map((p) => p.id), ...doc.lines.map((l) => l.id), ...doc.texts.map((t) => t.id)) + 1;
const near = (a, b) => Math.abs(a - b) < 0.5;

function status(text, error = false) {
  $("#status").textContent = text;
  $("#status").className = error ? "ed-status error" : "ed-status";
}

async function api(path) {
  const response = await fetch(path);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Ошибка сервера ${response.status}`);
  return data;
}

// Рисунок символа приводим к высоте 60: так все символы ГОСТ одного масштаба. Точки подключения —
// середины сторон габарита рисунка по осям символа: слева, справа, сверху, снизу.
async function loadShape(path) {
  if (shapes[path]) return shapes[path];
  const text = await (await fetch(`/${path}`)).text();
  const [vx, vy, vw, vh] = text.match(/viewBox="([^"]+)"/)[1].split(/[\s,]+/).map(Number);
  const scale = 60 / vh;
  const w = vw * scale, h = 60;
  const body = text.slice(text.indexOf(">", text.indexOf("<svg")) + 1, text.lastIndexOf("</svg>"));
  const inner = `<g transform="scale(${scale}) translate(${-vx} ${-vy})">${body}</g>`;
  const probe = document.createElementNS("http://www.w3.org/2000/svg", "g");
  probe.innerHTML = inner;
  $("#measure").append(probe);
  const box = probe.getBBox();
  probe.remove();
  const ports = [[box.x, h / 2], [box.x + box.width, h / 2], [w / 2, box.y], [w / 2, box.y + box.height]]
    .map(([x, y]) => [x - w / 2, y - h / 2]);
  return (shapes[path] = { inner, w, h, box, ports });
}

function rotate([x, y], degrees) {
  const r = (degrees * Math.PI) / 180;
  return [x * Math.cos(r) - y * Math.sin(r), x * Math.sin(r) + y * Math.cos(r)].map((v) => Math.round(v * 100) / 100);
}

function portsOf(part) {
  return shapes[part.svg_path].ports.map((p) => {
    const [x, y] = rotate(p, part.rotate);
    return [part.x + x, part.y + y];
  });
}

function nearestPort([x, y], except) {
  let best = null;
  for (const part of doc.parts) {
    portsOf(part).forEach((at, port) => {
      const distance = Math.hypot(at[0] - x, at[1] - y);
      const same = except && except.part === part.id && except.port === port;
      if (distance < PORT_SNAP && !same && (!best || distance < best.distance)) best = { part: part.id, port, at, distance };
    });
  }
  return best;
}

const findPart = (id) => doc.parts.find((p) => p.id === id);
const findLine = (id) => doc.lines.find((l) => l.id === id);
const findText = (id) => doc.texts.find((t) => t.id === id);

function change(apply) {
  history.push(JSON.stringify(doc));
  apply();
  dirty = true;
  render();
}

function undo() {
  if (!history.length) return;
  doc = JSON.parse(history.pop());
  selected = null;
  dirty = true;
  render();
}

// ---------- отрисовка ----------

function partSvg(part) {
  const s = shapes[part.svg_path];
  const hit = `<rect class="hit" x="${s.box.x - 4}" y="${s.box.y - 4}" width="${s.box.width + 8}" height="${s.box.height + 8}" fill="transparent"/>`;
  const tag = part.letters
    ? `<text x="0" y="-3" font-size="9" font-family="sans-serif" text-anchor="middle">${esc(part.letters)}</text>`
      + `<text x="0" y="10" font-size="8" font-family="sans-serif" text-anchor="middle">${esc(part.number)}</text>`
    : "";
  return `<g class="part" data-part="${part.id}" data-layer="SYMBOLS" transform="translate(${part.x} ${part.y})">
    <g transform="rotate(${part.rotate}) translate(${-s.w / 2} ${-s.h / 2})">${hit}${s.inner}</g>${tag}</g>`;
}

function lineSvg(line) {
  const points = line.points.map((p) => p.join(",")).join(" ");
  return `<g data-line="${line.id}" data-layer="${line.kind === "pipe" ? "PIPES" : "SIGNALS"}">
    <polyline class="hit" points="${points}" fill="none" stroke="transparent" stroke-width="10"/>
    <polyline points="${points}" fill="none" stroke="#000" stroke-width="${line.kind === "pipe" ? 2 : 1}"/></g>`;
}

function render() {
  $("#lines").innerHTML = doc.lines.map(lineSvg).join("");
  // приводы — под арматурой: щелчок по корпусу клапана берёт клапан, а не шток привода
  const isActuator = (part) => part.code.startsWith("actuator_");
  $("#parts").innerHTML = [...doc.parts].sort((a, b) => isActuator(b) - isActuator(a)).map(partSvg).join("");
  $("#texts").innerHTML = doc.texts.map((t) =>
    `<text data-text="${t.id}" data-layer="TEXT" x="${t.x}" y="${t.y}" font-size="12" font-family="sans-serif" text-anchor="middle">${esc(t.value)}</text>`).join("");
  renderOverlay();
  renderProps();
}

function renderOverlay(cursor) {
  const marks = [];
  if (selected?.type === "part") {
    const part = findPart(selected.id);
    const s = shapes[part.svg_path];
    marks.push(`<g transform="translate(${part.x} ${part.y}) rotate(${part.rotate}) translate(${-s.w / 2} ${-s.h / 2})">
      <rect x="${s.box.x - 6}" y="${s.box.y - 6}" width="${s.box.width + 12}" height="${s.box.height + 12}" fill="none" stroke="#0b6b5f" stroke-dasharray="4 3"/></g>`);
  }
  if (selected?.type === "line") {
    const points = findLine(selected.id).points.map((p) => p.join(",")).join(" ");
    marks.push(`<polyline points="${points}" fill="none" stroke="#0b6b5f" stroke-width="6" stroke-opacity=".35"/>`);
  }
  if (selected?.type === "text") {
    const t = findText(selected.id);
    marks.push(`<circle cx="${t.x}" cy="${t.y + 3}" r="3" fill="#0b6b5f"/>`);
  }
  if (tool === "pipe" || tool === "signal") {
    for (const part of doc.parts) for (const [x, y] of portsOf(part)) marks.push(`<circle cx="${x}" cy="${y}" r="3" fill="#0b6b5f" fill-opacity=".6"/>`);
  }
  if (draft && cursor) {
    const points = [...draft.points, cursor].map((p) => p.join(",")).join(" ");
    marks.push(`<polyline points="${points}" fill="none" stroke="#0b6b5f" stroke-width="${draft.kind === "pipe" ? 2 : 1}" stroke-dasharray="5 4"/>`);
  }
  $("#overlay").innerHTML = marks.join("");
}

// ---------- свойства справа ----------

function renderProps() {
  const panel = $("#props");
  if (!selected) {
    panel.innerHTML = `<h2>Как собрать схему</h2>
      <ul class="keys">
        <li>Перетащите символ из списка слева на лист или нажмите на него.</li>
        <li><b>Труба</b> или <b>Сигнал</b>: щёлкайте по точкам — линия идёт под прямым углом. Зелёные точки — места подключения, линия к ним прилипает. Двойной щелчок заканчивает линию.</li>
        <li>Исполнительный механизм, поднесённый к клапану, сам садится на шток.</li>
        <li>Выберите прибор, чтобы вписать буквы тега — справа появится расшифровка.</li>
      </ul>
      <h3>Клавиши</h3>
      <ul class="keys"><li><kbd>V</kbd> выбор, <kbd>P</kbd> труба, <kbd>S</kbd> сигнал, <kbd>T</kbd> текст</li>
        <li><kbd>Ctrl</kbd>+колесо или <kbd>Ctrl</kbd>+<kbd>+</kbd>/<kbd>−</kbd> — масштаб листа, <kbd>Ctrl</kbd>+<kbd>0</kbd> — 100%</li>
        <li>Пробел или средняя кнопка мыши + перетаскивание — двигать лист</li>
        <li><kbd>R</kbd> повернуть, <kbd>Del</kbd> удалить, <kbd>Ctrl</kbd>+<kbd>Z</kbd> отменить, <kbd>Esc</kbd> прервать линию</li></ul>`;
    return;
  }
  if (selected.type === "line") {
    const line = findLine(selected.id);
    panel.innerHTML = `<h2>${line.kind === "pipe" ? "Трубопровод" : "Линия связи"}</h2>
      <label>Тип линии<select data-prop="kind"><option value="pipe">Трубопровод (толстая)</option><option value="signal">Линия связи (тонкая)</option></select></label>
      <div class="actions"><button class="btn" data-action="delete">Удалить</button></div>`;
    panel.querySelector("select").value = line.kind;
    return;
  }
  if (selected.type === "text") {
    const t = findText(selected.id);
    panel.innerHTML = `<h2>Надпись</h2><label>Текст<input data-prop="value" value="${esc(t.value)}"></label>
      <div class="actions"><button class="btn" data-action="delete">Удалить</button></div>`;
    return;
  }
  const part = findPart(selected.id);
  const variants = palette.filter((s) => s.category === part.category && s.standard === part.standard);
  panel.innerHTML = `<h2>${esc(part.name)}</h2>
    <p class="muted">${esc(label(part.standard))}, ${esc(part.category)}</p>
    <div class="actions"><button class="btn" data-action="rotate">Повернуть</button>
      <button class="btn" data-action="delete">Удалить</button>
      <a class="btn" href="/?id=${part.symbol_id}" target="_blank" rel="noopener">Карточка</a></div>
    <label>Заменить на<select data-prop="symbol">${variants.map((s) =>
      `<option value="${s.id}" ${s.id === part.symbol_id ? "selected" : ""}>${esc(s.name_ru)}</option>`).join("")}</select></label>
    <h3>Тег прибора</h3>
    <label>Буквы<input data-prop="letters" value="${esc(part.letters)}" placeholder="например, FIC" autocomplete="off"></label>
    <label>Номер позиции<input data-prop="number" value="${esc(part.number)}" placeholder="например, 1-2" autocomplete="off"></label>
    <ul class="decode" id="decode"></ul>`;
  decodeTag(part.letters);
}

async function decodeTag(letters) {
  if (!letters) return;
  const rows = (await api(`/api/tag?q=${encodeURIComponent(letters)}`)).filter((r) => r.standard === "GOST 21.208");
  const list = $("#decode");
  if (list) list.innerHTML = rows.map((r) => `<li><b>${esc(r.letter)}</b>${esc(r.meaning)}</li>`).join("");
}

async function setProp(name, value) {
  if (selected.type === "line") return change(() => { findLine(selected.id).kind = value; });
  if (selected.type === "text") return change(() => { findText(selected.id).value = value; });
  const part = findPart(selected.id);
  if (name !== "symbol") return change(() => { part[name] = name === "letters" ? value.toUpperCase().trim() : value.trim(); });
  const symbol = palette.find((s) => s.id === Number(value));
  await loadShape(symbol.svg_path);
  change(() => Object.assign(part, symbolFields(symbol)));
}

// ---------- действия над схемой ----------

function symbolFields(symbol) {
  return { symbol_id: symbol.id, code: symbol.code, name: symbol.name_ru, standard: symbol.standard,
           category: symbol.category, svg_path: symbol.svg_path };
}

async function addPart(symbol, x, y) {
  await loadShape(symbol.svg_path);
  const part = { id: nextId(), ...symbolFields(symbol), x: snap(x), y: snap(y), rotate: 0, letters: "", number: "" };
  change(() => {
    doc.parts.push(part);
    seatActuator(part);
  });
  selected = { type: "part", id: part.id };
  render();
}

// Привод ГОСТ 21.208 рядом с арматурой садится на неё: конец штока — в центр корпуса
function seatActuator(part) {
  if (!part.code.startsWith("actuator_")) return;
  const stem = [part.x, part.y + ACTUATOR_STEM];
  const valve = doc.parts.find((p) => p.category === "Арматура" && Math.hypot(p.x - stem[0], p.y - stem[1]) < 30);
  if (valve) movePart(part, valve.x, valve.y - ACTUATOR_STEM);
}

function movePart(part, x, y) {
  const seated = doc.parts.filter((p) => p !== part && p.code.startsWith("actuator_")
    && near(p.x, part.x) && near(p.y, part.y - ACTUATOR_STEM) && part.category === "Арматура");
  for (const actuator of seated) movePart(actuator, x, y - ACTUATOR_STEM);
  part.x = x;
  part.y = y;
  const ports = portsOf(part);
  for (const line of doc.lines) {
    line.ends.forEach((end, which) => {
      if (end && end.part === part.id) reattach(line, which, ports[end.port]);
    });
  }
}

// Конец линии переезжает за символом, соседняя точка сдвигается так, чтобы углы остались прямыми
function reattach(line, which, at) {
  const pts = line.points;
  const i = which === 0 ? 0 : pts.length - 1;
  const j = which === 0 ? 1 : pts.length - 2;
  const [old, other] = [pts[i], pts[j]];
  const horizontal = near(old[1], other[1]);
  if (pts.length > 2) {
    if (horizontal) other[1] = at[1];
    else other[0] = at[0];
    pts[i] = at;
    return;
  }
  pts[i] = at;
  if (near(at[0], other[0]) || near(at[1], other[1])) return;
  const elbows = horizontal
    ? [[snap((at[0] + other[0]) / 2), at[1]], [snap((at[0] + other[0]) / 2), other[1]]]
    : [[at[0], snap((at[1] + other[1]) / 2)], [other[0], snap((at[1] + other[1]) / 2)]];
  line.points = which === 0 ? [at, ...elbows, other] : [other, ...elbows.reverse(), at];
}

function deleteSelected() {
  if (!selected) return;
  const { type, id } = selected;
  change(() => {
    if (type === "part") {
      doc.parts = doc.parts.filter((p) => p.id !== id);
      for (const line of doc.lines) line.ends = line.ends.map((end) => (end && end.part === id ? null : end));
    }
    if (type === "line") doc.lines = doc.lines.filter((l) => l.id !== id);
    if (type === "text") doc.texts = doc.texts.filter((t) => t.id !== id);
  });
  selected = null;
  render();
}

function rotateSelected() {
  if (selected?.type !== "part") return;
  const part = findPart(selected.id);
  change(() => {
    part.rotate = (part.rotate + 90) % 360;
    movePart(part, part.x, part.y);
  });
}

// ---------- линии ----------

function drawClick(point) {
  const port = nearestPort(point, draft?.ends[0]);
  const at = port ? port.at : point.map(snap);
  if (!draft) {
    draft = { kind: tool, points: [at], ends: [port ? { part: port.part, port: port.port } : null, null] };
    return renderOverlay(at);
  }
  const last = draft.points.at(-1);
  if (port) {
    if (!near(last[0], at[0]) && !near(last[1], at[1])) draft.points.push([at[0], last[1]]);
    draft.points.push(at);
    draft.ends[1] = { part: port.part, port: port.port };
    return finishLine();
  }
  const next = orthogonal(last, at);
  if (near(next[0], last[0]) && near(next[1], last[1])) return finishLine();
  draft.points.push(next);
  renderOverlay(next);
}

function orthogonal(last, at) {
  return Math.abs(at[0] - last[0]) >= Math.abs(at[1] - last[1]) ? [at[0], last[1]] : [last[0], at[1]];
}

function finishLine() {
  if (draft && draft.points.length > 1) {
    const line = { id: nextId(), ...draft };
    change(() => doc.lines.push(line));
  }
  draft = null;
  renderOverlay();
}

// ---------- мышь и клавиатура ----------

function pointer(event) {
  const point = $("#sheet").createSVGPoint();
  point.x = event.clientX;
  point.y = event.clientY;
  const p = point.matrixTransform($("#sheet").getScreenCTM().inverse());
  return [p.x, p.y];
}

// ---------- масштаб и прокрутка листа ----------

// anchor — точка экрана, которая должна остаться на месте (курсор при Ctrl+колесо)
function setZoom(value, anchor) {
  const canvas = $("#canvas");
  const box = canvas.getBoundingClientRect();
  const [ax, ay] = anchor || [box.left + box.width / 2, box.top + box.height / 2];
  const [sx, sy] = pointer({ clientX: ax, clientY: ay });
  zoom = Math.min(4, Math.max(0.2, value));
  const sheet = $("#sheet");
  sheet.setAttribute("width", SHEET.width * zoom);
  sheet.setAttribute("height", SHEET.height * zoom);
  sheet.style.setProperty("--zoom", zoom);
  $("#zoom-reset").textContent = `${Math.round(zoom * 100)}%`;
  const rect = sheet.getBoundingClientRect();
  canvas.scrollLeft += rect.left + sx * zoom - ax;
  canvas.scrollTop += rect.top + sy * zoom - ay;
}

function zoomToFit() {
  const canvas = $("#canvas");
  const box = doc.parts.length || doc.lines.length ? contentBox() : { x: 0, y: 0, width: 1200, height: 800 };
  setZoom(Math.min(2, canvas.clientWidth / box.width, canvas.clientHeight / box.height));
  canvas.scrollLeft = box.x * zoom - (canvas.clientWidth - box.width * zoom) / 2;
  canvas.scrollTop = box.y * zoom - (canvas.clientHeight - box.height * zoom) / 2;
}

function onWheel(event) {
  if (!event.ctrlKey && !event.metaKey) return;
  event.preventDefault();
  setZoom(zoom * (event.deltaY < 0 ? ZOOM_STEP : 1 / ZOOM_STEP), [event.clientX, event.clientY]);
}

function startPan(event) {
  event.preventDefault();
  const canvas = $("#canvas");
  pan = { x: event.clientX, y: event.clientY, left: canvas.scrollLeft, top: canvas.scrollTop };
  $("#sheet").classList.add("panning");
}

function onPointerDown(event) {
  if (event.button === 1 || spaceHeld) return startPan(event);
  const point = pointer(event);
  if (tool === "pipe" || tool === "signal") return drawClick(point);
  if (tool === "text") {
    const value = prompt("Текст надписи");
    if (value?.trim()) {
      const text = { id: nextId(), x: snap(point[0]), y: snap(point[1]), value: value.trim() };
      change(() => doc.texts.push(text));
    }
    return;
  }
  const partEl = event.target.closest("[data-part]");
  const textEl = event.target.closest("[data-text]");
  const lineEl = event.target.closest("[data-line]");
  if (partEl || textEl) {
    const item = partEl ? findPart(Number(partEl.dataset.part)) : findText(Number(textEl.dataset.text));
    selected = { type: partEl ? "part" : "text", id: item.id };
    drag = { item, dx: item.x - point[0], dy: item.y - point[1], before: JSON.stringify(doc), moved: false };
  } else {
    selected = lineEl ? { type: "line", id: Number(lineEl.dataset.line) } : null;
  }
  render();
}

function onPointerMove(event) {
  if (pan) {
    $("#canvas").scrollLeft = pan.left - (event.clientX - pan.x);
    $("#canvas").scrollTop = pan.top - (event.clientY - pan.y);
    return;
  }
  const point = pointer(event);
  if (draft) {
    const port = nearestPort(point, draft.ends[0]);
    return renderOverlay(port ? port.at : orthogonal(draft.points.at(-1), point.map(snap)));
  }
  if (!drag) return;
  const [x, y] = [snap(point[0] + drag.dx), snap(point[1] + drag.dy)];
  if (x === drag.item.x && y === drag.item.y) return;
  drag.moved = true;
  if (selected.type === "part") movePart(drag.item, x, y);
  else Object.assign(drag.item, { x, y });
  render();
}

function onPointerUp() {
  if (pan) {
    pan = null;
    $("#sheet").classList.remove("panning");
  }
  if (!drag) return;
  if (drag.moved) {
    if (selected.type === "part") seatActuator(drag.item);
    history.push(drag.before);
    dirty = true;
    render();
  }
  drag = null;
}

function setTool(name) {
  tool = name;
  draft = null;
  document.querySelectorAll("[data-tool]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.tool === name));
  $("#sheet").classList.toggle("drawing", name !== "select");
  renderOverlay();
}

function onKey(event) {
  // Ctrl +/−/0 масштабируют лист, а не всю страницу
  if ((event.ctrlKey || event.metaKey) && ["+", "=", "-", "0"].includes(event.key)) {
    event.preventDefault();
    return setZoom(event.key === "0" ? 1 : zoom * (event.key === "-" ? 1 / ZOOM_STEP : ZOOM_STEP));
  }
  if (["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement.tagName)) return;
  const key = event.key.toLowerCase();
  if (key === " ") {
    event.preventDefault();
    spaceHeld = true;
    return;
  }
  if ((event.ctrlKey || event.metaKey) && (key === "z" || key === "я")) return event.preventDefault(), undo();
  if (event.ctrlKey || event.metaKey || event.altKey) return;
  const tools = { v: "select", м: "select", p: "pipe", з: "pipe", s: "signal", ы: "signal", t: "text", е: "text" };
  if (tools[key]) return setTool(tools[key]);
  if (key === "r" || key === "к") return rotateSelected();
  if (key === "delete" || key === "backspace") return event.preventDefault(), deleteSelected();
  if (key === "escape") {
    draft = null;
    renderOverlay();
  }
}

// ---------- палитра ----------

function renderPalette() {
  const query = $("#find").value.trim().toLowerCase();
  const category = $("#category").value;
  const items = palette.filter((s) => (query ? s.name_ru.toLowerCase().includes(query) : s.category === category));
  $("#palette-list").innerHTML = items.map((s) =>
    `<button class="pal-item" draggable="true" data-symbol="${s.id}" title="${esc(s.name_ru)} (${esc(label(s.standard))})">
      <img src="/${esc(s.svg_path)}" alt="" loading="lazy">${esc(s.name_ru)}</button>`).join("")
    || `<p class="muted">Ничего не найдено.</p>`;
}

async function loadPalette() {
  palette = (await api(`/api/search?standard=${STANDARD}`)).items;
  const categories = [...new Set(palette.map((s) => s.category))].sort((a, b) => a.localeCompare(b, "ru"));
  $("#category").innerHTML = categories.map((c) => `<option ${c === "Арматура" ? "selected" : ""}>${esc(c)}</option>`).join("");
  renderPalette();
}

function visibleCenter() {
  const box = $("#canvas").getBoundingClientRect();
  return pointer({ clientX: box.left + box.width / 2, clientY: box.top + box.height / 2 });
}

// ---------- файлы ----------

async function refreshList() {
  const list = await api("/api/drawings");
  $("#open").innerHTML = `<option value="">Открыть схему…</option>`
    + list.map((d) => `<option value="${d.id}">${esc(d.name)}</option>`).join("");
}

async function openDrawing(id) {
  if (dirty && !confirm("Несохранённые изменения пропадут. Открыть другую схему?")) return;
  const found = await api(`/api/drawing/${id}`);
  const data = JSON.parse(found.data);
  await Promise.all(data.parts.map((p) => loadShape(p.svg_path)));
  Object.assign(doc, { parts: data.parts, lines: data.lines, texts: data.texts });
  drawingId = found.id;
  $("#name").value = found.name;
  history = [];
  selected = null;
  dirty = false;
  render();
  status(`Открыта схема «${found.name}».`);
}

function newDrawing() {
  if (dirty && !confirm("Несохранённые изменения пропадут. Начать новую схему?")) return;
  doc = { parts: [], lines: [], texts: [] };
  drawingId = null;
  $("#name").value = "";
  history = [];
  selected = null;
  dirty = false;
  render();
  status("Новая схема.");
}

async function saveDrawing() {
  const name = $("#name").value.trim();
  if (!name) {
    $("#name").focus();
    return status("Введите название схемы, чтобы сохранить её.", true);
  }
  try {
    const saved = await apiWrite("/api/drawings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: drawingId, name, data: doc }),
    });
    drawingId = saved.id;
    dirty = false;
    await refreshList();
    $("#open").value = saved.id;
    status(`Схема «${name}» сохранена.`);
  } catch (error) {
    status(error.message, true);
  }
}

// ---------- выгрузка ----------

function fileName(extension) {
  return `${($("#name").value.trim() || "схема").replace(/[\\/:*?"<>|]/g, "_")}.${extension}`;
}

function download(blob, name) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
}

function contentBox() {
  const box = $("#content").getBBox();
  return { x: box.x - 20, y: box.y - 20, width: box.width + 40, height: box.height + 40 };
}

function svgText() {
  const box = contentBox();
  const clone = $("#content").cloneNode(true);
  clone.querySelectorAll(".hit").forEach((el) => el.remove());
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${box.x} ${box.y} ${box.width} ${box.height}" width="${box.width}" height="${box.height}">`
    + `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" fill="#fff"/>${clone.innerHTML}</svg>`;
}

async function exportAs(kind) {
  if (!doc.parts.length && !doc.lines.length) return status("Лист пуст — выгружать нечего.", true);
  if (kind === "svg") return download(new Blob([svgText()], { type: "image/svg+xml" }), fileName("svg"));
  if (kind === "dxf") return download(new Blob([toDxf($("#content"), contentBox())], { type: "application/dxf" }), fileName("dxf"));
  const image = new Image();
  image.src = URL.createObjectURL(new Blob([svgText()], { type: "image/svg+xml" }));
  await image.decode();
  const canvas = document.createElement("canvas");
  canvas.width = image.width * 3;
  canvas.height = image.height * 3;
  canvas.getContext("2d").drawImage(image, 0, 0, canvas.width, canvas.height);
  URL.revokeObjectURL(image.src);
  canvas.toBlob((blob) => download(blob, fileName("png")));
}

// ---------- запуск ----------

function bind() {
  const sheet = $("#sheet");
  sheet.addEventListener("pointerdown", onPointerDown);
  sheet.addEventListener("dblclick", finishLine);
  addEventListener("pointermove", onPointerMove);
  addEventListener("pointerup", onPointerUp);
  addEventListener("keydown", onKey);
  addEventListener("keyup", (event) => { if (event.key === " ") spaceHeld = false; });
  $("#canvas").addEventListener("wheel", onWheel, { passive: false });
  $("#zoom-in").addEventListener("click", () => setZoom(zoom * ZOOM_STEP));
  $("#zoom-out").addEventListener("click", () => setZoom(zoom / ZOOM_STEP));
  $("#zoom-reset").addEventListener("click", () => setZoom(1));
  $("#zoom-fit").addEventListener("click", zoomToFit);
  addEventListener("beforeunload", (event) => { if (dirty) event.preventDefault(); });
  document.querySelectorAll("[data-tool]").forEach((b) => b.addEventListener("click", () => setTool(b.dataset.tool)));
  document.querySelectorAll("[data-export]").forEach((b) => b.addEventListener("click", () => exportAs(b.dataset.export)));
  $("#find").addEventListener("input", renderPalette);
  $("#category").addEventListener("change", renderPalette);
  $("#palette-list").addEventListener("dragstart", (event) => {
    event.dataTransfer.setData("text/plain", event.target.closest("[data-symbol]").dataset.symbol);
  });
  $("#palette-list").addEventListener("click", (event) => {
    const item = event.target.closest("[data-symbol]");
    if (item) addPart(palette.find((s) => s.id === Number(item.dataset.symbol)), ...visibleCenter());
  });
  sheet.addEventListener("dragover", (event) => event.preventDefault());
  sheet.addEventListener("drop", (event) => {
    event.preventDefault();
    const symbol = palette.find((s) => s.id === Number(event.dataTransfer.getData("text/plain")));
    if (symbol) addPart(symbol, ...pointer(event));
  });
  $("#props").addEventListener("change", (event) => {
    const prop = event.target.dataset.prop;
    if (prop) setProp(prop, event.target.value);
  });
  $("#props").addEventListener("input", (event) => {
    if (event.target.dataset.prop === "letters") decodeTag(event.target.value.toUpperCase().trim());
  });
  $("#props").addEventListener("click", (event) => {
    const action = event.target.closest("[data-action]")?.dataset.action;
    if (action === "rotate") rotateSelected();
    if (action === "delete") deleteSelected();
  });
  $("#new").addEventListener("click", newDrawing);
  $("#save").addEventListener("click", saveDrawing);
  $("#open").addEventListener("change", (event) => event.target.value && openDrawing(Number(event.target.value)));
}

async function main() {
  bind();
  setTool("select");
  render();
  await Promise.all([loadPalette(), refreshList()]);
  const id = Number(new URLSearchParams(location.search).get("drawing"));
  if (id) await openDrawing(id);
}

main().catch((error) => status(`Не удалось загрузить редактор: ${error.message}. Проверьте, что сервер запущен, и обновите страницу.`, true));

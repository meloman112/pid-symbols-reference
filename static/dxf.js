// Выгрузка листа в DXF R12 (AutoCAD, Компас, nanoCAD): отрезки, окружности, залитые треугольники, текст.
// 1 единица листа = 0,25 мм: клапан ГОСТ 2.785 выходит 10 мм, окружность прибора — 7 мм.
const DXF_SCALE = 0.25;

function toDxf(root, box) {
  const out = [];
  const toMm = (x, y) => [((x - box.x) * DXF_SCALE).toFixed(3), ((box.y + box.height - y) * DXF_SCALE).toFixed(3)];
  const shapes = root.querySelectorAll("path, line, polyline, polygon, rect, circle, ellipse, text");
  for (const el of shapes) {
    if (el.classList.contains("hit")) continue;
    const matrix = el.getCTM();
    const at = (x, y) => {
      const p = new DOMPoint(x, y).matrixTransform(matrix);
      return toMm(p.x, p.y);
    };
    const layer = el.tagName === "text" ? "TEXT" : el.getAttribute("stroke-dasharray") ? "DASHED" : el.closest("[data-layer]").dataset.layer;
    if (el.tagName === "text") out.push(dxfTextEntity(el, at, matrix, layer));
    else if (el.tagName === "circle") out.push(dxfCircle(el, at, matrix, layer));
    else for (const poly of outlines(el)) out.push(dxfPoly(poly, at, layer, isFilled(el)));
  }
  return ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "0", "ENDSEC",
          "0", "SECTION", "2", "ENTITIES", ...out.flat(), "0", "ENDSEC", "0", "EOF", ""].join("\n");
}

function isFilled(el) {
  const fill = el.getAttribute("fill");
  return fill === "#000" || fill === "black";
}

function outlines(el) {
  const num = (name) => Number(el.getAttribute(name) || 0);
  if (el.tagName === "line") return [{ pts: [[num("x1"), num("y1")], [num("x2"), num("y2")]], closed: false }];
  if (el.tagName === "rect") {
    const [x, y, w, h] = [num("x"), num("y"), num("width"), num("height")];
    return [{ pts: [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], closed: true }];
  }
  if (el.tagName === "polyline" || el.tagName === "polygon") {
    const values = el.getAttribute("points").trim().split(/[\s,]+/).map(Number);
    const pts = [];
    for (let i = 0; i < values.length; i += 2) pts.push([values[i], values[i + 1]]);
    return [{ pts, closed: el.tagName === "polygon" }];
  }
  if (el.tagName === "path") return parsePath(el.getAttribute("d")) || samplePath(el);
  return samplePath(el);
}

// Точный разбор путей из отрезков (M L H V Z); дуги и кривые идут через samplePath
function parsePath(d) {
  if (/[AaCcQqSsTt]/.test(d)) return null;
  const tokens = d.match(/[MLHVZmlhvz]|-?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?/g);
  const polys = [];
  let current = null, x = 0, y = 0, startX = 0, startY = 0, command = "", i = 0;
  const num = () => Number(tokens[i++]);
  while (i < tokens.length) {
    if (/[a-z]/i.test(tokens[i])) command = tokens[i++];
    const relative = command === command.toLowerCase();
    const kind = command.toUpperCase();
    if (kind === "Z") {
      if (current) current.closed = true;
      [x, y, current] = [startX, startY, null];
      continue;
    }
    if (kind === "M") {
      const [nx, ny] = [num(), num()];
      [x, y] = relative ? [x + nx, y + ny] : [nx, ny];
      [startX, startY] = [x, y];
      current = { pts: [[x, y]], closed: false };
      polys.push(current);
      command = relative ? "l" : "L";
      continue;
    }
    if (kind === "L") {
      const [nx, ny] = [num(), num()];
      [x, y] = relative ? [x + nx, y + ny] : [nx, ny];
    }
    if (kind === "H") x = relative ? x + num() : num();
    if (kind === "V") y = relative ? y + num() : num();
    if (!current) {
      current = { pts: [[startX, startY]], closed: false };
      polys.push(current);
    }
    current.pts.push([x, y]);
  }
  return polys;
}

function samplePath(el) {
  const length = el.getTotalLength();
  const steps = Math.max(12, Math.ceil(length / 2));
  const polys = [];
  let current = null, previous = null;
  for (let k = 0; k <= steps; k++) {
    const p = el.getPointAtLength((length * k) / steps);
    // скачок больше нескольких шагов — это переход к новому подконтуру (M), а не отрезок
    if (!previous || Math.hypot(p.x - previous.x, p.y - previous.y) > (3 * length) / steps + 0.5) {
      current = { pts: [], closed: false };
      polys.push(current);
    }
    current.pts.push([p.x, p.y]);
    previous = p;
  }
  return polys;
}

function dxfPoly({ pts, closed }, at, layer, filled) {
  const mm = pts.map(([x, y]) => at(x, y));
  if (filled && closed && (mm.length === 3 || mm.length === 4)) {
    const [a, b, c, d = mm[2]] = mm; // у SOLID третья и четвёртая вершины идут крест-накрест
    return ["0", "SOLID", "8", layer, "10", a[0], "20", a[1], "11", b[0], "21", b[1], "12", d[0], "22", d[1], "13", c[0], "23", c[1]];
  }
  const segments = closed ? [...mm, mm[0]] : mm;
  const entities = [];
  for (let i = 1; i < segments.length; i++) {
    const [p, q] = [segments[i - 1], segments[i]];
    entities.push("0", "LINE", "8", layer, "10", p[0], "20", p[1], "11", q[0], "21", q[1]);
  }
  return entities;
}

function dxfCircle(el, at, matrix, layer) {
  const [x, y] = at(Number(el.getAttribute("cx") || 0), Number(el.getAttribute("cy") || 0));
  const radius = Number(el.getAttribute("r")) * Math.hypot(matrix.a, matrix.b) * DXF_SCALE;
  return ["0", "CIRCLE", "8", layer, "10", x, "20", y, "40", radius.toFixed(3)];
}

function dxfTextEntity(el, at, matrix, layer) {
  const [x, y] = at(Number(el.getAttribute("x") || 0), Number(el.getAttribute("y") || 0));
  const height = (Number(el.getAttribute("font-size") || 12) * Math.hypot(matrix.a, matrix.b) * DXF_SCALE * 0.72).toFixed(3);
  const angle = ((Math.atan2(matrix.b, matrix.a) * 180) / Math.PI).toFixed(1);
  const centered = el.getAttribute("text-anchor") === "middle";
  const align = centered ? ["72", "1", "11", x, "21", y] : [];
  return ["0", "TEXT", "8", layer, "10", x, "20", y, "40", height, "1", dxfString(el.textContent), "50", angle, ...align];
}

// Кириллица в DXF R12 — через \U+XXXX, так её понимают AutoCAD и Компас без настройки кодовой страницы
function dxfString(text) {
  return [...text].map((ch) => (ch.charCodeAt(0) < 128 ? ch : `\\U+${ch.charCodeAt(0).toString(16).toUpperCase().padStart(4, "0")}`)).join("");
}

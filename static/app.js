const $ = (selector) => document.querySelector(selector);
const state = { q: "", standard: "", category: "", id: null, view: "", asm: null };
const FIELDS = [
  ["purpose", "Назначение"],
  ["placement", "Где ставить"],
  ["mistakes", "Типичные ошибки"],
  ["similar", "Похожие символы"],
];
let facets;
let searchTimer;

const esc = (text) => String(text ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const label = (standard) => standard.replace("GOST", "ГОСТ");
const stdClass = (standard) => "std-" + standard.split(" ")[0].toLowerCase();
const isMobile = () => matchMedia("(max-width: 900px)").matches;

async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Ошибка сервера ${response.status}`);
  return data;
}

function readUrl() {
  const params = new URLSearchParams(location.search);
  state.q = params.get("q") || "";
  state.standard = params.get("standard") || "";
  state.category = params.get("category") || "";
  state.id = Number(params.get("id")) || null;
  state.view = params.get("view") || "";
  state.asm = Number(params.get("asm")) || null;
}

function writeUrl() {
  const params = new URLSearchParams();
  for (const key of ["view", "asm", "q", "standard", "category", "id"]) if (state[key]) params.set(key, state[key]);
  history.replaceState(null, "", params.toString() ? `?${params}` : "/");
}

const family = (standard) => standard.split(" ")[0];

function chip(name, text, count, pressed) {
  return `<button class="chip ${name ? stdClass(name) : ""}" data-standard="${esc(name)}" aria-pressed="${pressed}">
    ${name ? '<span class="swatch"></span>' : ""}${esc(text)} <span class="n">${count}</span></button>`;
}

function renderStandards() {
  // Верхний ряд — семейства (ISO, ISA, ГОСТ, DIN); у ГОСТ много номеров, они раскрываются вторым рядом
  const families = new Map();
  for (const s of facets.standards) {
    const f = families.get(family(s.name)) || { members: [], count: 0 };
    f.members.push(s);
    f.count += s.count;
    families.set(family(s.name), f);
  }
  const total = facets.standards.reduce((sum, s) => sum + s.count, 0);
  const active = family(state.standard);
  const assemblies = `<button class="chip chip-asm" data-view="asm" aria-pressed="${state.view === "asm"}">Типовые узлы <span class="n">${facets.assemblies}</span></button>`;
  const top = [assemblies, chip("", "Все стандарты", total, !state.standard && !state.view), ...[...families].map(([name, f]) =>
    f.members.length === 1
      ? chip(f.members[0].name, label(f.members[0].name), f.count, state.standard === f.members[0].name)
      : chip(name, label(name), f.count, state.standard === name))];
  const group = families.get(active);
  group?.members.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));
  const sub = state.standard && group && group.members.length > 1
    ? `<div class="substandards">${group.members.map((s) => chip(s.name, label(s.name), s.count, s.name === state.standard)).join("")}</div>` : "";
  $("#standards").innerHTML = top.join("") + sub;
}

function renderCategorySelect() {
  const options = [`<option value="">Все категории</option>`, ...facets.categories.map((c) =>
    `<option value="${esc(c.name)}" ${c.name === state.category ? "selected" : ""}>${esc(c.name)} (${c.count})</option>`)];
  $("#category").innerHTML = options.join("");
}

function tile(symbol) {
  return `<button class="tile" data-id="${symbol.id}" aria-current="${symbol.id === state.id}">
    <span class="mm"><img src="/${esc(symbol.svg_path)}" alt="" loading="lazy"></span>
    <span class="name">${esc(symbol.name_ru || symbol.name_en)}</span>
    <span class="std ${stdClass(symbol.standard)}"><span class="std-mark"></span>${esc(label(symbol.standard))}</span>
  </button>`;
}

function renderCategories() {
  $("#count").textContent = "";
  $("#tag").innerHTML = "";
  $("#grid").className = "";
  $("#grid").innerHTML = `
    <p class="intro">Ищите по названию на русском или английском, по номеру ISO (например, X8176) или по тегу прибора. Или начните с раздела:</p>
    <div class="categories">${facets.categories.map((c) =>
      `<button data-category="${esc(c.name)}"><span>${esc(c.name)}</span><span class="n">${c.count}</span></button>`).join("")}</div>`;
}

function renderTag(rows) {
  if (!rows || !rows.length) return ($("#tag").innerHTML = "");
  const positions = [...new Set(rows.map((r) => r.position))];
  const meaning = (position, standard) => rows.find((r) => r.position === position && r.standard === standard)?.meaning || "—";
  $("#tag").innerHTML = `<section class="tagbox">
    <h2>Тег ${esc(state.q)} по буквам</h2>
    <table>
      <tr><th></th><th>ГОСТ 21.208</th><th>ISA 5.1</th></tr>
      ${positions.map((p) => `<tr>
        <td class="letter">${esc(rows.find((r) => r.position === p).letter)}</td>
        <td>${esc(meaning(p, "GOST 21.208"))}</td><td>${esc(meaning(p, "ISA 5.1"))}</td></tr>`).join("")}
    </table>
    <p class="count">Первая буква — измеряемая величина, следующие — уточнение или функция прибора.</p>
  </section>`;
}

function assemblyCard(a) {
  return `<button class="tile asm-tile" data-asm="${a.id}">
    <span class="mm"><img src="/${esc(a.svg_path)}" alt="" loading="lazy"></span>
    <span class="name">${esc(a.name)}</span>
    <span class="std">${esc(a.description)}</span>
  </button>`;
}

async function renderAssemblies() {
  $("#tag").innerHTML = "";
  $("#count").textContent = "";
  if (state.asm) return renderAssembly(state.asm);
  const list = await api("/api/assemblies");
  $("#grid").className = "asm-grid";
  $("#grid").innerHTML = `<p class="intro">Фрагменты схем по ГОСТ, собранные из символов справочника. Откройте узел и нажмите на любой элемент — справа появится его карточка.</p>`
    + list.map(assemblyCard).join("");
}

async function renderAssembly(id) {
  const a = await api(`/api/assembly/${id}`);
  const svgText = await (await fetch(`/${a.svg_path}`)).text();
  $("#grid").className = "";
  $("#grid").innerHTML = `<article class="asm">
    <button class="btn" data-action="asm-list">Все узлы</button>
    <h1>${esc(a.name)}</h1>
    <p class="lead">${esc(a.description)}</p>
    <div class="asm-sheet mm">${svgText}</div>
    <p class="count">Наведите на элемент — он подсветится; нажмите — справа откроется его карточка.</p>
    <div class="asm-cols">
      <section><h2>Состав</h2><ol class="parts">${a.parts.map((p, i) =>
        `<li><button data-part="${i}" data-id="${p.id}"><b>${esc(p.label)}</b><span>${esc(p.name_ru)}</span><span class="std ${stdClass(p.standard)}"><span class="std-mark"></span>${esc(label(p.standard))}</span></button></li>`).join("")}</ol></section>
      <section><h2>На что обратить внимание</h2><ul class="notes">${a.notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul></section>
    </div>
  </article>`;
  // Тонкие линии трудно попасть мышью — каждой детали даём прозрачную подложку по её габаритам
  document.querySelectorAll(".asm-sheet .part").forEach((g) => {
    const box = g.getBBox();
    g.insertAdjacentHTML("afterbegin", `<rect x="${box.x - 4}" y="${box.y - 4}" width="${box.width + 8}" height="${box.height + 8}" fill="transparent"/>`);
  });
}

function highlight(index, on) {
  document.querySelectorAll(`.asm [data-part="${index}"]`).forEach((el) => el.classList.toggle("hl", on));
}

async function search() {
  writeUrl();
  $("#category").hidden = state.view === "asm";
  if (state.view === "asm") return renderAssemblies();
  if (!state.q && !state.category && !state.standard) return renderCategories();
  const params = new URLSearchParams({ q: state.q, standard: state.standard, category: state.category });
  const { items, tag } = await api(`/api/search?${params}`);
  renderTag(tag);
  $("#grid").className = items.length ? "grid" : "";
  $("#count").textContent = items.length ? `Найдено: ${items.length}` : "";
  $("#grid").innerHTML = items.length ? items.map(tile).join("")
    : tag ? "" : `<p class="intro">Ничего не найдено. Попробуйте другое слово, английское название или снимите фильтр стандарта.</p>`;
}

function detailView(symbol) {
  const sections = FIELDS.filter(([key]) => symbol[key])
    .map(([key, title]) => `<h2>${title}</h2><p>${esc(symbol[key])}</p>`).join("");
  const related = symbol.related.length
    ? `<h2>В других стандартах</h2><div class="related">${symbol.related.map(tile).join("")}</div>` : "";
  const source = symbol.source_url
    ? `<a href="${esc(symbol.source_url)}" target="_blank" rel="noopener">${esc(symbol.author || "источник")}</a>` : esc(symbol.author || "");
  return `
    <button class="btn back" data-action="close">Назад к списку</button>
    <div class="sheet mm"><img src="/${esc(symbol.svg_path)}" alt="${esc(symbol.name_ru)}"></div>
    <h1>${esc(symbol.name_ru || symbol.name_en)}</h1>
    <p class="en">${esc(symbol.name_en)}</p>
    <dl class="meta">
      <dt>Стандарт</dt><dd class="${stdClass(symbol.standard)}"><span class="std-mark"></span>${esc(label(symbol.standard))}</dd>
      <dt>Категория</dt><dd>${esc(symbol.category)}</dd>
      ${symbol.reg_no ? `<dt>Номер ISO</dt><dd>${esc(symbol.reg_no)}</dd>` : ""}
    </dl>
    ${sections}
    ${symbol.used_in.length ? `<h2>Применяется в узлах</h2><ul class="used-in">${symbol.used_in.map((a) =>
      `<li><button class="link" data-asm="${a.id}">${esc(a.name)}</button></li>`).join("")}</ul>` : ""}
    ${related}
    <div class="actions">
      <a class="btn" href="/${esc(symbol.svg_path)}" download="${esc(symbol.code)}.svg">Скачать SVG</a>
      <button class="btn" data-action="edit">Исправить описание</button>
    </div>
    <p class="source">Рисунок: ${source}${symbol.license ? ` (${esc(symbol.license)})` : ""}. Описание составлено автоматически — проверяйте по стандарту и исправляйте неточности.</p>`;
}

function editView(symbol) {
  const fields = [["name_ru", "Название"], ["category", "Категория"], ...FIELDS].map(([key, title]) =>
    key === "name_ru" || key === "category"
      ? `<label>${title}<input name="${key}" value="${esc(symbol[key])}" required></label>`
      : `<label>${title}<textarea name="${key}" rows="4" required>${esc(symbol[key])}</textarea></label>`).join("");
  return `<form class="edit">
    <div class="sheet mm"><img src="/${esc(symbol.svg_path)}" alt=""></div>
    ${fields}
    <div class="actions"><button class="btn primary" type="submit">Сохранить</button><button class="btn" type="button" data-action="cancel">Отмена</button></div>
    <p class="status" aria-live="polite"></p>
  </form>`;
}

async function openSymbol(id, mode = "view") {
  state.id = id;
  writeUrl();
  document.querySelectorAll(".tile[aria-current]").forEach((t) => t.setAttribute("aria-current", t.dataset.id == id));
  const symbol = await api(`/api/symbol/${id}`);
  const panel = $("#detail");
  panel.hidden = false;
  panel.innerHTML = mode === "edit" ? editView(symbol) : detailView(symbol);
  panel.scrollTop = 0;
  panel.onclick = async (event) => {
    const action = event.target.closest("[data-action]")?.dataset.action;
    const related = event.target.closest(".tile");
    const asm = event.target.closest("[data-asm]");
    if (asm) return openAssembly(Number(asm.dataset.asm));
    if (action === "edit") openSymbol(id, "edit");
    if (action === "cancel") openSymbol(id);
    if (action === "close") closeSymbol();
    if (related) openSymbol(Number(related.dataset.id));
  };
  const form = panel.querySelector("form");
  if (form) form.onsubmit = (event) => saveSymbol(event, id);
}

async function saveSymbol(event, id) {
  event.preventDefault();
  const status = event.target.querySelector(".status");
  try {
    await api(`/api/symbol/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Object.fromEntries(new FormData(event.target))),
    });
    await openSymbol(id);
    $("#detail").insertAdjacentHTML("afterbegin", `<p class="status ok">Описание сохранено.</p>`);
    search();
  } catch (error) {
    status.className = "status error";
    status.textContent = error.message;
  }
}

function openAssembly(id) {
  state.view = "asm";
  state.asm = id;
  state.q = "";
  $("#q").value = "";
  renderStandards();
  search();
  scrollTo(0, 0);
}

function closeSymbol() {
  state.id = null;
  writeUrl();
  if (isMobile()) $("#detail").hidden = true;
  else $("#detail").innerHTML = $("#empty-detail").innerHTML;
}

function bind() {
  $("#q").addEventListener("input", (event) => {
    clearTimeout(searchTimer);
    state.q = event.target.value.trim();
    if (state.view) {
      state.view = "";
      state.asm = null;
      renderStandards();
    }
    searchTimer = setTimeout(search, 180);
  });
  $("#standards").addEventListener("click", (event) => {
    const chip = event.target.closest(".chip");
    if (!chip) return;
    if (chip.dataset.view) return openAssembly(null);
    state.view = "";
    state.asm = null;
    state.standard = chip.dataset.standard;
    renderStandards();
    search();
  });
  $("#category").addEventListener("change", (event) => {
    state.category = event.target.value;
    search();
  });
  $("#grid").addEventListener("click", (event) => {
    if (event.target.closest('[data-action="asm-list"]')) return openAssembly(null);
    const asm = event.target.closest("[data-asm]");
    if (asm) return openAssembly(Number(asm.dataset.asm));
    const part = event.target.closest(".asm [data-id]");
    if (part) return openSymbol(Number(part.dataset.id));
    const category = event.target.closest("[data-category]");
    if (category) {
      state.category = category.dataset.category;
      renderCategorySelect();
      return search();
    }
    const found = event.target.closest(".tile");
    if (found) openSymbol(Number(found.dataset.id));
  });
  for (const type of ["mouseover", "mouseout"]) {
    $("#grid").addEventListener(type, (event) => {
      const part = event.target.closest(".asm [data-part]");
      if (part) highlight(part.dataset.part, type === "mouseover");
    });
  }
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && document.activeElement.tagName !== "INPUT" && document.activeElement.tagName !== "TEXTAREA") {
      event.preventDefault();
      $("#q").focus();
    }
    if (event.key === "Escape" && state.id && isMobile()) closeSymbol();
  });
  new ResizeObserver(() => document.documentElement.style.setProperty("--top-h", `${$(".top").offsetHeight}px`)).observe($(".top"));
}

async function main() {
  readUrl();
  facets = await api("/api/facets");
  $("#q").value = state.q;
  renderStandards();
  renderCategorySelect();
  bind();
  await search();
  if (state.id) openSymbol(state.id);
  else closeSymbol();
}

main().catch((error) => {
  $("#grid").innerHTML = `<p class="status error">Не удалось загрузить справочник: ${esc(error.message)}. Проверьте, что сервер запущен, и обновите страницу.</p>`;
});

// Запись на сервер с входом по паролю: на 401 спрашиваем пароль и повторяем запрос один раз
async function apiWrite(path, options) {
  let response = await fetch(path, options);
  if (response.status === 401 && await askPassword()) response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Ошибка сервера ${response.status}`);
  return data;
}

function askPassword() {
  document.body.insertAdjacentHTML("beforeend", `<dialog class="login"><form method="dialog">
    <h2>Вход для правки</h2>
    <p>Изменения видят все, кто открывает справочник, поэтому сохранять можно только с паролем.</p>
    <input type="password" name="password" required aria-label="Пароль" autocomplete="current-password">
    <p class="status error" aria-live="polite"></p>
    <div class="actions"><button class="btn primary" value="ok">Войти</button><button class="btn" value="cancel" formnovalidate>Отмена</button></div>
  </form></dialog>`);
  const dialog = document.body.lastElementChild;
  dialog.showModal();
  return new Promise((resolve) => {
    const finish = (ok) => { dialog.remove(); resolve(ok); };
    dialog.addEventListener("cancel", () => finish(false));
    dialog.querySelector("form").addEventListener("submit", async (event) => {
      if (event.submitter?.value === "cancel") return finish(false);
      event.preventDefault();
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: dialog.querySelector("input").value }),
      });
      if (response.ok) return finish(true);
      dialog.querySelector(".status").textContent = (await response.json()).error;
    });
  });
}

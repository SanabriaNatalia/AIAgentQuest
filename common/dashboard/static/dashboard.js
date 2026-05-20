// Helpers minimalistas del dashboard (sin libs externas).
(function () {
  // --- Polling: [data-poll-url] + [data-poll-interval] -----------------
  function refresh(el) {
    var url = el.dataset.pollUrl;
    if (!url) return;
    fetch(url, { headers: { Accept: "text/html" } })
      .then(function (r) { return r.ok ? r.text() : null; })
      .then(function (html) { if (html !== null) el.innerHTML = html; })
      .catch(function () { /* best-effort */ });
  }

  function initPolling() {
    var nodes = document.querySelectorAll("[data-poll-url]");
    nodes.forEach(function (el) {
      var interval = parseInt(el.dataset.pollInterval || "30000", 10);
      setInterval(function () { refresh(el); }, interval);
    });
  }

  // --- Copy code: inyecta botón en cada div.codeblock ------------------
  function initCopyButtons() {
    var blocks = document.querySelectorAll(".viewer-prose .codeblock");
    blocks.forEach(function (block) {
      if (block.querySelector(".codeblock-copy")) return;
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "codeblock-copy";
      btn.textContent = "Copiar";
      btn.addEventListener("click", function () {
        var code = block.querySelector("pre");
        if (!code) return;
        var text = code.innerText;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () {
            flash(btn, "✓ Copiado");
          }).catch(function () {
            fallbackCopy(text, btn);
          });
        } else {
          fallbackCopy(text, btn);
        }
      });
      block.appendChild(btn);
    });
  }

  function fallbackCopy(text, btn) {
    try {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "absolute";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      flash(btn, "✓ Copiado");
    } catch (_) {
      flash(btn, "✗ Falló");
    }
  }

  function flash(btn, label) {
    var original = btn.textContent;
    btn.textContent = label;
    btn.classList.add("codeblock-copy--flash");
    setTimeout(function () {
      btn.textContent = original;
      btn.classList.remove("codeblock-copy--flash");
    }, 1400);
  }

  // --- Mark-read: POST al endpoint y deshabilita botón -----------------
  function initMarkRead() {
    var btns = document.querySelectorAll("[data-mark-read-url]");
    btns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var url = btn.dataset.markReadUrl;
        btn.disabled = true;
        btn.textContent = "Sellando…";
        fetch(url, { method: "POST", headers: { Accept: "application/json" } })
          .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
          .then(function () {
            btn.textContent = "✓ Pergamino estudiado";
            btn.classList.add("viewer-mark-read--done");
          })
          .catch(function () {
            btn.disabled = false;
            btn.textContent = "Reintentar";
          });
      });
    });
  }

  // --- Toast de eventos: peek + render + dismiss ------------------------
  function renderToast(host, event) {
    var quest = (event.payload && (event.payload.quest_id || "")) || "";
    var rank = (event.payload && event.payload.rank) || null;
    var leveled = !!(event.payload &&
      event.payload.level_after && event.payload.level_before &&
      event.payload.level_after > event.payload.level_before);

    var title = leveled ? "⚜ Asciendes" : "⚜ Quest completado";
    var bodyParts = [];
    if (rank) bodyParts.push("Rango: " + rank);
    if (event.payload && event.payload.xp_reward != null) {
      bodyParts.push("+" + event.payload.xp_reward + " XP");
    }
    var body = bodyParts.length ? bodyParts.join(" · ") : "El laboratorio recordará este momento.";

    var ctaUrl = "/celebrate" + (quest ? "?quest=" + encodeURIComponent(quest) : "");

    host.innerHTML = (
      '<div class="notification-toast-title">' + title + '</div>' +
      '<div class="notification-toast-body">' + body + '</div>' +
      '<div class="notification-toast-actions">' +
        '<a class="notification-toast-cta" href="' + ctaUrl + '">Ver celebración</a>' +
        '<button type="button" class="notification-toast-dismiss" aria-label="Cerrar">✕</button>' +
      '</div>'
    );
    host.classList.remove("notification-toast--hidden");
    host.dataset.currentEventId = String(event.id);

    var dismissBtn = host.querySelector(".notification-toast-dismiss");
    if (dismissBtn) {
      dismissBtn.addEventListener("click", function () { dismissToast(host); });
    }
  }

  function dismissToast(host) {
    var id = host.dataset.currentEventId;
    var template = host.dataset.eventDismissUrl;
    host.classList.add("notification-toast--hidden");
    host.innerHTML = "";
    host.dataset.currentEventId = "";
    if (!id || !template) return;
    var url = template.replace("{id}", encodeURIComponent(id));
    fetch(url, { method: "POST", headers: { Accept: "application/json" } })
      .catch(function () { /* best-effort */ });
  }

  function pollToast(host) {
    var url = host.dataset.eventPollUrl;
    if (!url) return;
    fetch(url, { headers: { Accept: "application/json" } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || !data.events || !data.events.length) return;
        var completed = data.events.filter(function (e) { return e.kind === "quest_completed"; });
        if (!completed.length) return;
        var top = completed[0];
        if (host.dataset.currentEventId === String(top.id)) return;
        renderToast(host, top);
      })
      .catch(function () { /* best-effort */ });
  }

  function initToast() {
    var host = document.getElementById("event-toast");
    if (!host) return;
    pollToast(host);
    var interval = parseInt(host.dataset.eventPollInterval || "15000", 10);
    setInterval(function () { pollToast(host); }, interval);
  }

  function init() {
    initPolling();
    initCopyButtons();
    initMarkRead();
    initToast();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

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

  // --- Pistas: modal de confirmación + POST async ---------------------
  function initHints() {
    var modal = document.getElementById("hint-modal");
    if (!modal) return;

    var section = document.querySelector("[data-hints-slug]");
    if (!section) return;

    var targetLabel = modal.querySelector("[data-hint-modal-target]");
    var confirmBtn = modal.querySelector("[data-hint-modal-confirm]");
    var dismissNodes = modal.querySelectorAll("[data-hint-modal-dismiss]");
    var pendingCard = null;

    function openModal(card) {
      pendingCard = card;
      var title = card.querySelector(".hint-card-title");
      if (targetLabel) {
        targetLabel.textContent = title ? "Pista a revelar: " + title.textContent : "";
      }
      modal.classList.remove("hint-modal--hidden");
      modal.removeAttribute("hidden");
    }

    function closeModal() {
      pendingCard = null;
      modal.classList.add("hint-modal--hidden");
      modal.setAttribute("hidden", "");
    }

    function reveal(card, html, requestedAt) {
      var btn = card.querySelector(".hint-card-button");
      card.classList.remove("hint-card--available");
      card.classList.add("hint-card--revealed");
      if (btn) btn.remove();

      var body = document.createElement("div");
      body.className = "hint-card-body";
      body.setAttribute("data-hint-content", "");
      body.innerHTML = html || "<p><em>Contenido vacío.</em></p>";
      card.appendChild(body);

      if (requestedAt) {
        var footer = document.createElement("p");
        footer.className = "hint-card-footer arkanum-muted";
        footer.textContent = "Revelada el " + requestedAt;
        card.appendChild(footer);
      }

      unlockNext(card);
    }

    function unlockNext(card) {
      var level = parseInt(card.dataset.hintLevel || "0", 10);
      if (!level) return;
      var nextCard = section.querySelector('.hint-card[data-hint-level="' + (level + 1) + '"]');
      if (!nextCard || !nextCard.classList.contains("hint-card--locked")) return;
      nextCard.classList.remove("hint-card--locked");
      nextCard.classList.add("hint-card--available");

      var locked = nextCard.querySelector(".hint-card-footer");
      if (locked && locked.textContent.indexOf("Requiere") !== -1) {
        locked.remove();
      }

      var slug = section.dataset.hintsSlug;
      if (!slug) return;
      if (nextCard.querySelector(".hint-card-button")) return;
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "hint-card-button";
      btn.textContent = "Solicitar pista";
      btn.dataset.hintRequestUrl = "/api/quests/" + slug + "/hints/" + (level + 1);
      btn.addEventListener("click", function () { openModal(nextCard); });
      nextCard.appendChild(btn);
    }

    section.querySelectorAll(".hint-card-button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var card = btn.closest(".hint-card");
        if (card) openModal(card);
      });
    });

    dismissNodes.forEach(function (node) {
      node.addEventListener("click", closeModal);
    });

    if (confirmBtn) {
      confirmBtn.addEventListener("click", function () {
        if (!pendingCard) { closeModal(); return; }
        var card = pendingCard;
        var btn = card.querySelector(".hint-card-button");
        var url = btn ? btn.dataset.hintRequestUrl : null;
        if (!url) { closeModal(); return; }

        confirmBtn.disabled = true;
        confirmBtn.textContent = "Revelando…";

        fetch(url, {
          method: "POST",
          headers: { Accept: "application/json", "Content-Type": "application/json" },
        })
          .then(function (r) {
            if (!r.ok) {
              return r.json().catch(function () { return { detail: "Error" }; })
                .then(function (body) { throw new Error(body.detail || "Error"); });
            }
            return r.json();
          })
          .then(function (data) {
            reveal(card, data.html, data.requested_at);
            closeModal();
          })
          .catch(function (err) {
            alert("No se pudo revelar la pista: " + (err && err.message ? err.message : ""));
            closeModal();
          })
          .finally(function () {
            confirmBtn.disabled = false;
            confirmBtn.textContent = "Sí, revelar";
          });
      });
    }

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !modal.classList.contains("hint-modal--hidden")) {
        closeModal();
      }
    });
  }

  function init() {
    initPolling();
    initCopyButtons();
    initMarkRead();
    initToast();
    initHints();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

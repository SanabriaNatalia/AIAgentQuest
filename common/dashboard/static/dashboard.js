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

  // --- Copy code: inyecta botón solo en bloques con código real --------
  // Los bloques ```text se usan para rutas, output o ejemplos conceptuales:
  // no se pegan en ningún lado, así que omitimos el botón.
  var NON_COPYABLE_LANGS = { "": 1, "text": 1, "plain": 1, "txt": 1, "output": 1 };

  function initCopyButtons() {
    var blocks = document.querySelectorAll(".viewer-prose .codeblock");
    blocks.forEach(function (block) {
      if (block.querySelector(".codeblock-copy")) return;
      var lang = (block.dataset.lang || "").toLowerCase();
      if (NON_COPYABLE_LANGS[lang]) return;
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

  // --- Start quest: POST al endpoint y reemplaza CTA por panel ---------
  function formatElapsed(startedAt) {
    var start = new Date(startedAt);
    if (isNaN(start.getTime())) return "";
    var diffMs = Date.now() - start.getTime();
    if (diffMs < 0) diffMs = 0;
    var seconds = Math.floor(diffMs / 1000);
    if (seconds < 60) return seconds + "s";
    var minutes = Math.floor(seconds / 60);
    var remSec = seconds % 60;
    if (minutes < 60) return minutes + "m " + remSec + "s";
    var hours = Math.floor(minutes / 60);
    var remMin = minutes % 60;
    return hours + "h " + remMin + "m";
  }

  function tickElapsed(node) {
    var startedAt = node.dataset.startedAt;
    if (!startedAt) return;
    node.textContent = "Cronómetro corriendo · " + formatElapsed(startedAt);
  }

  function initElapsedTickers() {
    var nodes = document.querySelectorAll("[data-quest-start-elapsed]");
    nodes.forEach(function (node) {
      tickElapsed(node);
      setInterval(function () { tickElapsed(node); }, 1000);
    });
  }

  function buildStartedPanel(slug, order, startedAt) {
    return (
      '<div class="quest-start-panel" data-quest-start-panel>' +
        '<header class="quest-start-panel-header">' +
          '<span class="quest-start-badge">⏱ En curso</span>' +
          '<h3>Manos a la obra</h3>' +
        '</header>' +
        '<p class="quest-start-elapsed" data-quest-start-elapsed data-started-at="' + startedAt + '">' +
          'Cronómetro corriendo · 0s' +
        '</p>' +
        '<ol class="quest-start-steps">' +
          '<li><span class="quest-start-step-text">Abre <code>quests/' + slug + '/starter/main.py</code> en tu editor (VS Code u otro IDE) y completa los <code>TODO</code>s.</span></li>' +
          '<li><span class="quest-start-step-text">Cuando termines, valida desde la terminal:</span>' +
            '<pre class="quest-start-cmd"><code>arkanum check ' + order + '</code></pre>' +
          '</li>' +
        '</ol>' +
      '</div>'
    );
  }

  function initStartQuest() {
    var btns = document.querySelectorAll("[data-quest-start-button]");
    btns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var host = btn.closest("[data-quest-start]");
        if (!host) return;
        var url = btn.dataset.startUrl;
        var slug = host.dataset.questSlug;
        var order = host.dataset.questOrder;
        btn.disabled = true;
        btn.textContent = "Invocando…";
        fetch(url, { method: "POST", headers: { Accept: "application/json" } })
          .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
          .then(function (data) {
            var startedAt = data.started_at || new Date().toISOString();
            host.dataset.startedAt = startedAt;
            host.innerHTML = buildStartedPanel(slug, order, startedAt);
            initElapsedTickers();
          })
          .catch(function () {
            btn.disabled = false;
            btn.textContent = "Reintentar";
          });
      });
    });
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

  // --- Live agent: polling de /api/trace/current + render ---------------
  function initLiveAgent() {
    var host = document.querySelector("[data-trace-poll-url]");
    if (!host) return;

    var url = host.dataset.tracePollUrl;
    var stepsHost = host.querySelector("[data-trace-steps]");
    var emptyHost = host.querySelector("[data-trace-empty]");
    var statusHost = host.querySelector("[data-trace-status]");
    var metaHost = host.querySelector("[data-trace-meta]");

    var seenIds = new Set();
    var lastTraceId = null;

    function iconFor(stepType) {
      switch (stepType) {
        case "function_call": return "⚡";
        case "function_result": return "📦";
        case "tokens": return "🧪";
        case "session_start": return "🜂";
        case "session_end": return "🜄";
        default: return "•";
      }
    }

    function payloadText(step) {
      var p = step.payload;
      if (p === null || p === undefined) return "";
      if (typeof p === "string") return p;
      try { return JSON.stringify(p); } catch (_) { return String(p); }
    }

    function renderStep(step) {
      var li = document.createElement("li");
      li.className = "trace-step trace-step--" + step.step_type;
      li.dataset.stepId = String(step.id);

      var head = document.createElement("div");
      head.className = "trace-step-head";
      head.innerHTML =
        '<span class="trace-step-icon" aria-hidden="true">' + iconFor(step.step_type) + '</span>' +
        '<span class="trace-step-type">' + step.step_type + '</span>' +
        (step.name ? '<span class="trace-step-name">' + step.name + '</span>' : '') +
        '<span class="trace-step-time">' + step.created_at + '</span>';
      li.appendChild(head);

      var payload = payloadText(step);
      if (payload) {
        var body = document.createElement("pre");
        body.className = "trace-step-payload";
        body.textContent = payload;
        li.appendChild(body);
      }
      return li;
    }

    function applyData(data) {
      if (!data || !data.steps) return;

      // Cambió de trace → vaciar la lista y reinicializar el set de IDs.
      if (data.trace_id && data.trace_id !== lastTraceId) {
        if (stepsHost) stepsHost.innerHTML = "";
        seenIds = new Set();
        lastTraceId = data.trace_id;
      }

      if (data.steps.length === 0) {
        if (emptyHost) emptyHost.style.display = "";
        if (statusHost) statusHost.textContent = "Esperando trace…";
        if (metaHost) metaHost.textContent = "";
        return;
      }

      if (emptyHost) emptyHost.style.display = "none";

      var added = 0;
      for (var i = 0; i < data.steps.length; i++) {
        var step = data.steps[i];
        if (seenIds.has(step.id)) continue;
        seenIds.add(step.id);
        if (stepsHost) stepsHost.appendChild(renderStep(step));
        added += 1;
      }

      if (statusHost && data.summary) {
        statusHost.textContent = "Trace " + data.summary.trace_id;
      }
      if (metaHost && data.summary) {
        var meta = [];
        if (data.summary.quest_title) meta.push(data.summary.quest_title);
        meta.push(data.summary.steps + " pasos");
        meta.push("último: " + data.summary.last_step_at);
        metaHost.textContent = meta.join(" · ");
      }

      if (added > 0 && stepsHost && stepsHost.lastElementChild) {
        var reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        stepsHost.lastElementChild.scrollIntoView({
          behavior: reducedMotion ? "auto" : "smooth",
          block: "end",
        });
      }
    }

    function poll() {
      fetch(url, { headers: { Accept: "application/json" } })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(applyData)
        .catch(function () { /* best-effort */ });
    }

    poll();
    setInterval(poll, 1000);
  }

  function init() {
    initPolling();
    initCopyButtons();
    initMarkRead();
    initToast();
    initHints();
    initLiveAgent();
    initStartQuest();
    initElapsedTickers();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

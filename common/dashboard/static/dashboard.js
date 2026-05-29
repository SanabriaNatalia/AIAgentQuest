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
    var interval = parseInt(host.dataset.eventPollInterval || "5000", 10);
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
  function truncate(text, max) {
    if (text == null) return "—";
    var s = String(text).replace(/\s+/g, " ").trim();
    if (!s) return "—";
    if (s.length <= max) return s;
    return s.slice(0, max - 1) + "…";
  }

  function setUserPrompt(host, prompt) {
    var preview = host.querySelector("[data-user-prompt-preview]");
    var body = host.querySelector("[data-user-prompt-body]");
    if (preview) preview.textContent = truncate(prompt, 60);
    if (body) {
      if (prompt) {
        body.textContent = prompt;
        body.classList.remove("live-agent-prompt-body--muted");
      } else {
        body.textContent =
          "Lanza `arkanum run 7 \"…\"` o `arkanum run 8 \"…\"` para registrar el prompt del aprendiz.";
        body.classList.add("live-agent-prompt-body--muted");
      }
    }
  }

  function loadSystemPrompt(host) {
    var url = host.dataset.systemPromptUrl;
    if (!url) return;
    var preview = host.querySelector("[data-system-prompt-preview]");
    var body = host.querySelector("[data-system-prompt-body]");
    var note = host.querySelector("[data-system-prompt-note]");
    var panel = body ? body.closest(".live-agent-prompt-panel") : null;
    fetch(url, { headers: { Accept: "application/json" } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data) {
          if (preview) preview.textContent = "(no disponible)";
          if (body) body.textContent = "No se pudo cargar el system prompt.";
          return;
        }
        var content = (data.content || "").trim();
        if (preview) preview.textContent = truncate(content, 60) || "(vacío)";
        if (body) body.textContent = content || "(vacío)";
        if (note) {
          if (data.is_placeholder) {
            note.textContent =
              "Este archivo todavía contiene el placeholder. La Quest 04 te pide reescribirlo.";
            note.classList.add("live-agent-prompt-note--warn");
          } else if (data.error) {
            note.textContent = data.error;
            note.classList.add("live-agent-prompt-note--warn");
          } else {
            note.textContent = data.path
              ? "Origen: " + data.path
              : "";
            note.classList.remove("live-agent-prompt-note--warn");
          }
        }
        // Mejora #18: botón Editar (si hay panel y backend disponible).
        if (panel && !data.error) {
          attachSystemPromptEditor(panel, body, url, data.content || "");
        }
      })
      .catch(function () { /* best-effort */ });
  }

  function attachSystemPromptEditor(panel, body, url, currentContent) {
    if (panel.querySelector("[data-system-prompt-edit]")) return; // ya está
    var actions = document.createElement("div");
    actions.className = "live-agent-prompt-actions";
    actions.innerHTML =
      '<button type="button" class="live-agent-action" data-system-prompt-edit>✏ Editar</button>';
    body.parentNode.insertBefore(actions, body);

    var editBtn = actions.querySelector("[data-system-prompt-edit]");
    editBtn.addEventListener("click", function () {
      // Reemplaza el body por un textarea editable + Guardar/Cancelar.
      var textarea = document.createElement("textarea");
      textarea.className = "live-agent-prompt-textarea";
      textarea.value = currentContent;
      textarea.rows = 8;

      var btnRow = document.createElement("div");
      btnRow.className = "live-agent-prompt-edit-actions";
      var saveBtn = document.createElement("button");
      saveBtn.type = "button";
      saveBtn.className = "live-agent-action";
      saveBtn.textContent = "💾 Guardar";
      var cancelBtn = document.createElement("button");
      cancelBtn.type = "button";
      cancelBtn.className = "live-agent-action";
      cancelBtn.textContent = "Cancelar";
      btnRow.appendChild(saveBtn);
      btnRow.appendChild(cancelBtn);

      var originalBody = body.cloneNode(true);
      body.replaceWith(textarea);
      textarea.after(btnRow);
      actions.style.display = "none";

      function restoreOriginal() {
        textarea.replaceWith(originalBody);
        body = originalBody;
        btnRow.remove();
        actions.style.display = "";
      }

      cancelBtn.addEventListener("click", restoreOriginal);

      saveBtn.addEventListener("click", function () {
        var newContent = textarea.value;
        if (newContent.indexOf('"""') !== -1) {
          window.alert("El contenido no puede incluir comillas triples.");
          return;
        }
        saveBtn.disabled = true;
        saveBtn.textContent = "Guardando…";
        fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({ content: newContent }),
        })
          .then(function (r) {
            if (!r.ok) {
              return r.json().catch(function () { return { detail: "Error" }; })
                .then(function (e) { throw new Error(e.detail || "Error"); });
            }
            return r.json();
          })
          .then(function () {
            // Recarga limpia para reflejar el nuevo contenido y el note.
            window.location.reload();
          })
          .catch(function (err) {
            saveBtn.disabled = false;
            saveBtn.textContent = "💾 Guardar";
            window.alert("No se pudo guardar: " + (err && err.message ? err.message : ""));
          });
      });
    });
  }

  function initLiveAgent() {
    var host = document.querySelector("[data-trace-poll-url]");
    if (!host) return;

    var url = host.dataset.tracePollUrl;
    var historyUrl = host.dataset.tracesHistoryUrl;
    var stepsHost = host.querySelector("[data-trace-steps]");
    var emptyHost = host.querySelector("[data-trace-empty]");
    var statusHost = host.querySelector("[data-trace-status]");
    var metaHost = host.querySelector("[data-trace-meta]");
    var historyListHost = host.querySelector("[data-history-list]");
    var historyStatusHost = host.querySelector("[data-history-status]");

    var seenIds = new Set();
    var lastTraceId = null;
    var lastUserPrompt = null;
    var currentBand = null;       // <ol> activo donde se anexan steps de la iter actual
    var lastIterPayload = null;   // {iter, max} de la iteración activa
    var selectedTraceId = null;   // trace explícitamente fijado por click en historial
    var topTraceId = null;        // trace_id del más reciente conocido

    // System prompt: cargar una vez al inicio.
    loadSystemPrompt(host);
    // User prompt: placeholder hasta que llegue session_start.
    setUserPrompt(host, null);

    // HUD (mejora #13): KPIs computados sobre la lista entera del trace.
    var KPI_PRICE_INPUT_PER_1M = 0.075;   // alineado con services/cost.py
    var KPI_PRICE_OUTPUT_PER_1M = 0.30;

    function computeKpis(steps) {
      var iter = 0;
      var iterMax = null;
      var tools = 0;
      var promptTokens = 0;
      var responseTokens = 0;
      var latencies = [];

      for (var i = 0; i < steps.length; i++) {
        var s = steps[i];
        if (!s) continue;
        if (s.step_type === "iteration_start") {
          var p = s.payload || {};
          if (p.iter != null) iter = Math.max(iter, Number(p.iter) || iter);
          if (p.max != null && iterMax == null) iterMax = Number(p.max);
        } else if (s.step_type === "function_call") {
          tools += 1;
        } else if (s.step_type === "tokens") {
          var n = parseInt(s.payload, 10);
          if (!isNaN(n)) {
            if (s.name === "prompt") promptTokens += n;
            else if (s.name === "response") responseTokens += n;
          }
        } else if (s.step_type === "latency") {
          var sec = (s.payload && typeof s.payload === "object") ? s.payload.seconds : null;
          if (sec != null) latencies.push(Number(sec));
        }
      }

      var totalTokens = promptTokens + responseTokens;
      var costUsd =
        promptTokens * KPI_PRICE_INPUT_PER_1M / 1e6 +
        responseTokens * KPI_PRICE_OUTPUT_PER_1M / 1e6;
      var avgLatency = latencies.length
        ? latencies.reduce(function (a, b) { return a + b; }, 0) / latencies.length
        : null;

      return {
        iter: iter,
        iterMax: iterMax,
        tools: tools,
        tokens: totalTokens,
        cost: costUsd,
        latency: avgLatency,
      };
    }

    function formatTokens(n) {
      if (n < 1000) return String(n);
      if (n < 1_000_000) return (n / 1000).toFixed(1).replace(/\.0$/, "") + "k";
      return (n / 1_000_000).toFixed(2).replace(/\.00$/, "") + "M";
    }

    function renderHud(steps) {
      var hudHost = host.querySelector("[data-trace-hud]");
      if (!hudHost) return;
      var kpis = computeKpis(steps);

      var iterEl = hudHost.querySelector("[data-kpi-iter]");
      var toolsEl = hudHost.querySelector("[data-kpi-tools]");
      var tokensEl = hudHost.querySelector("[data-kpi-tokens]");
      var costEl = hudHost.querySelector("[data-kpi-cost]");
      var latEl = hudHost.querySelector("[data-kpi-latency]");

      if (iterEl) {
        iterEl.textContent = kpis.iterMax
          ? kpis.iter + " / " + kpis.iterMax
          : String(kpis.iter);
      }
      if (toolsEl) toolsEl.textContent = String(kpis.tools);
      if (tokensEl) tokensEl.textContent = formatTokens(kpis.tokens);
      if (costEl) costEl.textContent = "$" + kpis.cost.toFixed(4);
      if (latEl) latEl.textContent = kpis.latency != null ? kpis.latency.toFixed(2) + " s" : "—";
    }

    function appendStep(node) {
      // Si hay una banda activa, los steps van dentro de ella.
      // Si no, van al contenedor principal (steps "fuera de loop").
      var target = currentBand || stepsHost;
      if (target) target.appendChild(node);
    }

    // Stats acumulados por la banda activa (mejora #6: costo por iteración).
    var bandStats = null;

    function refreshBandMeta() {
      if (!currentBand || !bandStats) return;
      var meta = currentBand.parentElement
        ? currentBand.parentElement.querySelector("[data-band-meta]")
        : null;
      if (!meta) return;
      var parts = [];
      if (bandStats.latency != null) {
        parts.push(bandStats.latency.toFixed(2) + " s");
      }
      var totalTok = bandStats.promptTokens + bandStats.responseTokens;
      if (totalTok > 0) {
        var cost =
          bandStats.promptTokens * KPI_PRICE_INPUT_PER_1M / 1e6 +
          bandStats.responseTokens * KPI_PRICE_OUTPUT_PER_1M / 1e6;
        parts.push(formatTokens(totalTok) + " tokens");
        parts.push("$" + cost.toFixed(4));
      }
      meta.textContent = parts.join(" · ");
    }

    function openBand(step) {
      var payload = step.payload || {};
      lastIterPayload = payload;
      bandStats = { latency: null, promptTokens: 0, responseTokens: 0 };
      var band = document.createElement("li");
      band.className = "trace-band";
      band.dataset.iter = String(payload.iter || "?");

      var head = document.createElement("header");
      head.className = "trace-band-head";
      var iter = payload.iter != null ? payload.iter : "?";
      var max = payload.max != null ? " / " + payload.max : "";
      head.innerHTML =
        '<span class="trace-band-icon" aria-hidden="true">↻</span>' +
        '<span class="trace-band-label">Iteración ' + escapeHtml(iter) + escapeHtml(max) + '</span>' +
        '<span class="trace-band-meta" data-band-meta></span>';
      band.appendChild(head);

      var ol = document.createElement("ol");
      ol.className = "trace-band-steps";
      band.appendChild(ol);

      if (stepsHost) stepsHost.appendChild(band);
      currentBand = ol;
    }

    function updateBandMeta(latencySeconds) {
      if (!bandStats) return;
      bandStats.latency = Number(latencySeconds);
      refreshBandMeta();
    }

    function addBandTokens(step) {
      if (!bandStats) return;
      var n = parseInt(step.payload, 10);
      if (isNaN(n)) return;
      if (step.name === "prompt") bandStats.promptTokens += n;
      else if (step.name === "response") bandStats.responseTokens += n;
      refreshBandMeta();
    }

    function appendContextGrowth(step) {
      // Si no hay banda activa, lo añadimos al raíz (caso patológico).
      var bandLi = currentBand ? currentBand.parentElement : stepsHost;
      if (!bandLi) return;

      var payload = step.payload || {};
      var totalMessages = payload.messages != null ? payload.messages : "?";
      var deltaCount = payload.delta_count != null ? payload.delta_count : 0;

      var details = document.createElement("details");
      details.className = "trace-context-growth";

      var summary = document.createElement("summary");
      summary.innerHTML =
        '<span aria-hidden="true">🗂</span> ' +
        '<span class="trace-context-summary-text">Contexto: ' +
        escapeHtml(totalMessages) + ' messages' +
        (deltaCount > 0 ? ' <span class="trace-context-delta-pill">+' + deltaCount + '</span>' : '') +
        '</span>';
      details.appendChild(summary);

      var delta = Array.isArray(payload.delta_preview) ? payload.delta_preview : [];
      if (delta.length) {
        var ul = document.createElement("ul");
        ul.className = "trace-context-delta-list";
        for (var i = 0; i < delta.length; i++) {
          var it = delta[i] || {};
          var li = document.createElement("li");
          li.className = "trace-context-delta-item";
          li.innerHTML =
            '<span class="trace-context-delta-role">' + escapeHtml(it.role || "?") + '</span> ' +
            '<span class="trace-context-delta-kind">' + escapeHtml(it.kind || "?") + '</span>' +
            (it.preview
              ? '<span class="trace-context-delta-preview">' + escapeHtml(it.preview) + '</span>'
              : '');
          ul.appendChild(li);
        }
        details.appendChild(ul);
      }

      bandLi.appendChild(details);
    }

    function resetBands() {
      currentBand = null;
      lastIterPayload = null;
      bandStats = null;
    }

    function iconFor(stepType) {
      switch (stepType) {
        case "function_call": return "⚡";
        case "function_result": return "📦";
        case "tokens": return "🧪";
        case "session_start": return "🜂";
        case "session_end": return "🜄";
        case "agent_thought": return "🧠";
        case "agent_final": return "✦";
        case "iteration_start": return "↻";
        case "latency": return "⏱";
        default: return "•";
      }
    }

    function labelFor(stepType) {
      switch (stepType) {
        case "agent_thought": return "pensamiento";
        case "agent_final": return "respuesta final";
        case "iteration_start": return "iteración";
        case "latency": return "latencia";
        default: return stepType;
      }
    }

    function explainerFor(stepType) {
      switch (stepType) {
        case "function_call":
          return "El modelo decidió ejecutar una herramienta que le diste como tool. Aún no se ha ejecutado en Python.";
        case "function_result":
          return "El sandbox ejecutó la herramienta y devolvió este resultado al modelo en la siguiente vuelta.";
        case "agent_thought":
          return "Texto que el modelo generó entre tool calls — su razonamiento explícito. Aquí ves POR QUÉ elige cada paso.";
        case "agent_final":
          return "Respuesta final tras N iteraciones del loop. Aquí termina la cadena: el agente decidió no llamar más tools.";
        case "iteration_start":
          return "Una vuelta más del for principal del agent loop. El agente puede hacer hasta MAX_ITERS vueltas.";
        case "latency":
          return "Tiempo real que tardó Gemini en responder esta llamada. En producción esto se siente.";
        case "tokens":
          return "Cuántos tokens consumió esta invocación. Multiplica por el precio para el costo en USD.";
        case "context_growth":
          return "Cuánto creció `messages` tras esta iteración. Es la memoria del loop: el modelo la lee en la siguiente vuelta.";
        case "session_start":
          return "Marca el inicio del trace. El payload trae el prompt original del aprendiz.";
        case "session_end":
          return "El proceso del agente terminó (con su exit code). El trace queda sellado.";
        default:
          return "";
      }
    }

    function payloadText(step) {
      var p = step.payload;
      if (p === null || p === undefined) return "";
      if (typeof p === "string") return p;
      try { return JSON.stringify(p); } catch (_) { return String(p); }
    }

    function payloadField(step, key) {
      var p = step.payload;
      if (p && typeof p === "object" && p[key] !== undefined) return p[key];
      return null;
    }

    function escapeHtml(s) {
      return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function attachResultToPendingCall(stepsHost, step) {
      // Busca la última function_call pendiente y le ancla el resultado.
      // Devuelve true si emparejó, false si no había candidata.
      var pending = stepsHost.querySelectorAll(
        '.trace-step--function_call[data-pair-status="pending"]'
      );
      if (!pending.length) return false;
      var call = pending[pending.length - 1];

      call.dataset.pairStatus = "resolved";
      call.classList.add("trace-step--paired");

      var spinner = call.querySelector(".trace-step-pending");
      if (spinner) spinner.remove();

      var resBlock = document.createElement("div");
      resBlock.className = "trace-step-result";
      resBlock.innerHTML =
        '<span class="trace-step-result-label">' +
        '<span aria-hidden="true">📦</span> Resultado' +
        '</span>';

      var payload = payloadText(step);
      if (payload) {
        var pre = document.createElement("pre");
        pre.className = "trace-step-result-payload";
        pre.textContent = payload;
        resBlock.appendChild(pre);
      }
      call.appendChild(resBlock);
      return true;
    }

    function renderStep(step) {
      var li = document.createElement("li");
      li.className = "trace-step trace-step--" + step.step_type;
      li.dataset.stepId = String(step.id);
      var hint = explainerFor(step.step_type);
      if (hint) li.dataset.explainer = hint;

      // Header común (icono + tipo + nombre + hora)
      var head = document.createElement("div");
      head.className = "trace-step-head";
      head.innerHTML =
        '<span class="trace-step-icon" aria-hidden="true">' + iconFor(step.step_type) + '</span>' +
        '<span class="trace-step-type">' + labelFor(step.step_type) + '</span>' +
        (step.name ? '<span class="trace-step-name">' + escapeHtml(step.name) + '</span>' : '') +
        '<span class="trace-step-time">' + escapeHtml(step.created_at) + '</span>';
      li.appendChild(head);

      // function_call: marcamos como "pending" para que su function_result
      // posterior se ancle dentro de la misma tarjeta (mejora #2).
      if (step.step_type === "function_call") {
        li.dataset.pairStatus = "pending";
        li.dataset.pairName = step.name || "";
        var payload = payloadText(step);
        if (payload) {
          var body = document.createElement("pre");
          body.className = "trace-step-payload";
          body.textContent = payload;
          li.appendChild(body);
        }
        var pending = document.createElement("p");
        pending.className = "trace-step-pending";
        pending.innerHTML = '<span class="trace-step-pending-spinner" aria-hidden="true"></span>ejecutando…';
        li.appendChild(pending);
        return li;
      }

      // agent_thought / agent_final: body en prosa (no monoespacial)
      if (step.step_type === "agent_thought" || step.step_type === "agent_final") {
        var text = payloadField(step, "text");
        if (text == null) text = payloadText(step);
        if (text) {
          var prose = document.createElement("p");
          prose.className = "trace-step-prose";
          prose.textContent = text;
          li.appendChild(prose);
        }
        return li;
      }

      // latency: chip compacto, sin body
      if (step.step_type === "latency") {
        var seconds = payloadField(step, "seconds");
        if (seconds != null) {
          var chip = document.createElement("span");
          chip.className = "trace-step-chip";
          chip.textContent = seconds + " s";
          head.appendChild(chip);
        }
        return li;
      }

      // iteration_start: separador con label
      if (step.step_type === "iteration_start") {
        var iter = payloadField(step, "iter");
        var max = payloadField(step, "max");
        if (iter != null) {
          var counter = document.createElement("span");
          counter.className = "trace-step-counter";
          counter.textContent = "Iteración " + iter + (max ? " / " + max : "");
          head.appendChild(counter);
        }
        return li;
      }

      // resto (function_call, function_result, tokens, session_*): payload en mono
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
        lastUserPrompt = null;
        resetBands();
        setUserPrompt(host, null);
        // Reset del control de polling adaptativo.
        idleCount = 0;
        traceSealed = false;
      }
      if (data.summary && data.summary.has_session_end) traceSealed = true;

      if (data.steps.length === 0) {
        if (emptyHost) emptyHost.style.display = "";
        if (statusHost) statusHost.textContent = "Esperando trace…";
        if (metaHost) metaHost.textContent = "";
        renderHud([]);
        return;
      }

      if (emptyHost) emptyHost.style.display = "none";

      var added = 0;
      for (var i = 0; i < data.steps.length; i++) {
        var step = data.steps[i];
        if (seenIds.has(step.id)) continue;
        seenIds.add(step.id);

        if (step.step_type === "iteration_start") {
          // Abre una banda nueva como contenedor para los siguientes steps.
          openBand(step);
        } else if (step.step_type === "function_result") {
          // Ancla el resultado dentro de la última function_call pendiente.
          // Búsqueda restringida al contenedor actual (banda activa o raíz).
          var container = currentBand || stepsHost;
          var anchored = container
            ? attachResultToPendingCall(container, step)
            : false;
          if (!anchored) appendStep(renderStep(step));
        } else if (step.step_type === "latency") {
          // En la banda actual, suma la latencia al meta del header.
          // También se muestra como step individual (chip) por compatibilidad.
          var seconds = payloadField(step, "seconds");
          if (seconds != null) updateBandMeta(seconds);
          appendStep(renderStep(step));
        } else if (step.step_type === "tokens") {
          // Suma a la banda activa para mostrar costo en su header.
          addBandTokens(step);
          appendStep(renderStep(step));
        } else if (step.step_type === "context_growth") {
          // Renderiza dentro de la banda como panel desplegable (mejora #11/#17).
          appendContextGrowth(step);
        } else {
          appendStep(renderStep(step));
        }
        added += 1;

        // Captura el user_prompt del session_start si está disponible.
        if (
          step.step_type === "session_start" &&
          step.payload &&
          typeof step.payload === "object" &&
          step.payload.user_prompt &&
          step.payload.user_prompt !== lastUserPrompt
        ) {
          lastUserPrompt = step.payload.user_prompt;
          setUserPrompt(host, lastUserPrompt);
        }
      }

      if (statusHost && data.summary) {
        statusHost.textContent = "Trace " + data.summary.trace_id;
      }
      // Mejora #5: stale detection. >30s sin step nuevo y sin session_end.
      var trToolbar = host.querySelector(".live-agent-toolbar");
      if (trToolbar) trToolbar.classList.remove("live-agent-toolbar--stale", "live-agent-toolbar--sealed");
      if (data.summary) {
        var sinceLast = data.summary.seconds_since_last_step;
        var hasEnd = data.summary.has_session_end;
        if (hasEnd) {
          if (trToolbar) trToolbar.classList.add("live-agent-toolbar--sealed");
        } else if (sinceLast != null && sinceLast > 30) {
          if (trToolbar) trToolbar.classList.add("live-agent-toolbar--stale");
        }
      }
      if (metaHost && data.summary) {
        var meta = [];
        if (data.summary.quest_title) meta.push(data.summary.quest_title);
        meta.push(data.summary.steps + " pasos");
        if (data.summary.has_session_end) {
          meta.push("sellado");
        } else if (data.summary.seconds_since_last_step != null && data.summary.seconds_since_last_step > 30) {
          meta.push("stale (" + Math.round(data.summary.seconds_since_last_step) + "s sin actividad)");
        } else {
          meta.push("último: " + data.summary.last_step_at);
        }
        metaHost.textContent = meta.join(" · ");
      }

      if (added > 0 && stepsHost && stepsHost.lastElementChild) {
        var reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        stepsHost.lastElementChild.scrollIntoView({
          behavior: reducedMotion ? "auto" : "smooth",
          block: "end",
        });
      }

      // Mejora #13: recalcula KPIs sobre la lista completa, no incremental.
      renderHud(data.steps);

      // Mejora #8: registra cuántos steps llegaron en este poll para decidir
      // el siguiente intervalo.
      lastPollAddedSteps = added;
    }

    function buildPollUrl() {
      if (!selectedTraceId) return url;
      var sep = url.indexOf("?") === -1 ? "?" : "&";
      return url + sep + "trace_id=" + encodeURIComponent(selectedTraceId);
    }

    // Polling adaptativo (mejora #8): el intervalo varía según actividad.
    var POLL_FAST_MS = 250;
    var POLL_NORMAL_MS = 1000;
    var POLL_IDLE_MS = 3000;
    var POLL_IDLE_THRESHOLD = 5;
    var idleCount = 0;
    var traceSealed = false;
    var lastPollAddedSteps = 0;
    var pollTimer = null;

    function nextPollDelay() {
      if (traceSealed) return 0;  // 0 = stop
      if (lastPollAddedSteps > 0) return POLL_FAST_MS;
      if (idleCount >= POLL_IDLE_THRESHOLD) return POLL_IDLE_MS;
      return POLL_NORMAL_MS;
    }

    function schedulePoll() {
      if (pollTimer) clearTimeout(pollTimer);
      var delay = nextPollDelay();
      if (delay === 0) return;  // session_end llegó: parar.
      pollTimer = setTimeout(poll, delay);
    }

    function poll() {
      lastPollAddedSteps = 0;
      fetch(buildPollUrl(), { headers: { Accept: "application/json" } })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (data) {
          applyData(data);
          if (lastPollAddedSteps > 0) idleCount = 0;
          else idleCount += 1;
          schedulePoll();
        })
        .catch(function () { schedulePoll(); });
    }

    function formatRelative(iso) {
      if (!iso) return "—";
      var t = new Date(iso).getTime();
      if (isNaN(t)) return iso;
      var delta = (Date.now() - t) / 1000;
      if (delta < 60) return Math.max(0, Math.round(delta)) + " s atrás";
      if (delta < 3600) return Math.round(delta / 60) + " min atrás";
      if (delta < 86400) return Math.round(delta / 3600) + " h atrás";
      return Math.round(delta / 86400) + " d atrás";
    }

    function renderHistory(traces) {
      if (!historyListHost) return;
      historyListHost.innerHTML = "";
      topTraceId = traces.length ? traces[0].trace_id : null;
      if (!traces.length) {
        if (historyStatusHost) historyStatusHost.textContent = "(sin ejecuciones)";
        return;
      }
      if (historyStatusHost) {
        historyStatusHost.textContent = traces.length + " ejecuciones";
      }
      traces.forEach(function (t, idx) {
        var li = document.createElement("li");
        li.className = "live-agent-history-item";
        var isLive = idx === 0;
        var isActive = (selectedTraceId
          ? t.trace_id === selectedTraceId
          : isLive);
        if (isLive) li.classList.add("live-agent-history-item--live");
        if (isActive) li.classList.add("live-agent-history-item--active");

        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "live-agent-history-button";
        btn.dataset.traceId = t.trace_id;

        var head = document.createElement("div");
        head.className = "live-agent-history-button-head";
        var label = isLive ? "● en vivo" : "○ histórico";
        head.innerHTML =
          '<span class="live-agent-history-status-pill' +
          (isLive ? ' live-agent-history-status-pill--live' : '') + '">' +
          escapeHtml(label) + '</span>' +
          '<span class="live-agent-history-time">' +
          escapeHtml(formatRelative(t.last_step_at)) + '</span>';
        btn.appendChild(head);

        var title = document.createElement("div");
        title.className = "live-agent-history-title";
        title.textContent = t.quest_title || t.trace_id;
        btn.appendChild(title);

        var prompt = document.createElement("div");
        prompt.className = "live-agent-history-prompt";
        prompt.textContent = truncate(t.user_prompt || "(sin prompt)", 80);
        btn.appendChild(prompt);

        var meta = document.createElement("div");
        meta.className = "live-agent-history-meta";
        meta.textContent = t.steps + " pasos · " + (t.trace_id || "");
        btn.appendChild(meta);

        btn.addEventListener("click", function () {
          // El más reciente vuelve a polling "vivo" (sin filtro).
          selectedTraceId = isLive ? null : t.trace_id;
          // Vacía render para forzar repintado limpio.
          if (stepsHost) stepsHost.innerHTML = "";
          seenIds = new Set();
          lastTraceId = null;
          resetBands();
          renderHistory(traces);  // re-render para refrescar el highlight
          poll();
        });

        li.appendChild(btn);
        historyListHost.appendChild(li);
      });
    }

    function loadHistory() {
      if (!historyUrl) return;
      fetch(historyUrl, { headers: { Accept: "application/json" } })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (data) {
          if (!data || !Array.isArray(data.traces)) return;
          renderHistory(data.traces);
        })
        .catch(function () { /* best-effort */ });
    }

    loadHistory();
    setInterval(loadHistory, 5000);

    // ----- Mejora #16: Export (markdown + JSON). ------------------------
    function stepToMarkdown(step) {
      var icon = iconFor(step.step_type);
      var label = labelFor(step.step_type);
      var head = "- " + icon + " **" + label + "**";
      if (step.name) head += " · `" + step.name + "`";
      var body = "";
      if (step.step_type === "agent_thought" || step.step_type === "agent_final") {
        var text = payloadField(step, "text") || payloadText(step);
        if (text) body = "\n\n  > " + String(text).split("\n").join("\n  > ");
      } else if (step.step_type === "context_growth") {
        var msgs = payloadField(step, "messages");
        var delta = payloadField(step, "delta_count");
        body = "\n\n  Contexto: " + msgs + " messages (+ " + delta + ")";
      } else {
        var payload = payloadText(step);
        if (payload) {
          body = "\n\n  ```\n  " + payload.split("\n").join("\n  ") + "\n  ```";
        }
      }
      return head + body;
    }

    function traceToMarkdown(data) {
      var lines = [];
      var s = data.summary || {};
      lines.push("# Trace `" + (s.trace_id || data.trace_id || "?") + "`");
      lines.push("");
      if (s.quest_title) lines.push("- **Quest:** " + s.quest_title);
      if (s.started_at) lines.push("- **Iniciado:** " + s.started_at);
      if (s.last_step_at) lines.push("- **Último paso:** " + s.last_step_at);
      if (s.steps != null) lines.push("- **Pasos:** " + s.steps);
      lines.push("");

      var currentIter = null;
      for (var i = 0; i < data.steps.length; i++) {
        var step = data.steps[i];
        if (step.step_type === "iteration_start") {
          var p = step.payload || {};
          currentIter = p.iter;
          lines.push("");
          lines.push("## Iteración " + (p.iter || "?") +
            (p.max ? " / " + p.max : ""));
          lines.push("");
          continue;
        }
        lines.push(stepToMarkdown(step));
      }
      return lines.join("\n");
    }

    function copyToClipboard(text) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(text);
      }
      return new Promise(function (resolve, reject) {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "absolute";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        try {
          document.execCommand("copy");
          resolve();
        } catch (e) {
          reject(e);
        } finally {
          document.body.removeChild(ta);
        }
      });
    }

    function withLatestTraceData(cb) {
      fetch(buildPollUrl(), { headers: { Accept: "application/json" } })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (data) { if (data) cb(data); })
        .catch(function () { /* best-effort */ });
    }

    function flashAction(btn, label) {
      var prev = btn.textContent;
      btn.textContent = label;
      btn.classList.add("live-agent-action--flash");
      setTimeout(function () {
        btn.textContent = prev;
        btn.classList.remove("live-agent-action--flash");
      }, 1500);
    }

    var copyBtn = host.querySelector("[data-trace-copy-md]");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        withLatestTraceData(function (data) {
          var md = traceToMarkdown(data);
          copyToClipboard(md)
            .then(function () { flashAction(copyBtn, "✓ Copiado"); })
            .catch(function () { flashAction(copyBtn, "✗ Error"); });
        });
      });
    }

    var jsonBtn = host.querySelector("[data-trace-download-json]");
    if (jsonBtn) {
      jsonBtn.addEventListener("click", function () {
        withLatestTraceData(function (data) {
          var blob = new Blob(
            [JSON.stringify(data, null, 2)],
            { type: "application/json" }
          );
          var url2 = URL.createObjectURL(blob);
          var a = document.createElement("a");
          a.href = url2;
          a.download = "trace_" + (data.trace_id || "unknown") + ".json";
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url2);
          flashAction(jsonBtn, "✓ Descargado");
        });
      });
    }

    // ----- Mejora #14: Replay. -----------------------------------------
    var replayBtn = host.querySelector("[data-trace-replay]");
    var replayState = { running: false, timer: null };
    function stopReplay() {
      replayState.running = false;
      if (replayState.timer) clearTimeout(replayState.timer);
      replayState.timer = null;
    }
    function startReplay(data, speed) {
      if (!stepsHost) return;
      stopReplay();
      stepsHost.innerHTML = "";
      seenIds = new Set();
      resetBands();
      replayState.running = true;

      var steps = data.steps || [];
      if (!steps.length) return;
      var firstT = new Date(steps[0].created_at).getTime();

      function scheduleStep(i) {
        if (!replayState.running || i >= steps.length) {
          replayState.running = false;
          return;
        }
        var step = steps[i];
        // Renderizado: reusa la misma máquina de applyData (subset).
        renderSingleStep(step);
        seenIds.add(step.id);

        var nextStep = steps[i + 1];
        var delayMs = 0;
        if (nextStep) {
          var t1 = new Date(step.created_at).getTime();
          var t2 = new Date(nextStep.created_at).getTime();
          if (!isNaN(t1) && !isNaN(t2)) {
            delayMs = Math.max(0, (t2 - t1) / speed);
            if (delayMs > 3000) delayMs = 3000;  // cap a 3s
          }
        }
        replayState.timer = setTimeout(function () { scheduleStep(i + 1); }, delayMs);
      }
      scheduleStep(0);
    }

    function renderSingleStep(step) {
      if (step.step_type === "iteration_start") { openBand(step); return; }
      if (step.step_type === "function_result") {
        var container = currentBand || stepsHost;
        if (!container || !attachResultToPendingCall(container, step)) {
          appendStep(renderStep(step));
        }
        return;
      }
      if (step.step_type === "latency") {
        var sec = payloadField(step, "seconds");
        if (sec != null) updateBandMeta(sec);
        appendStep(renderStep(step));
        return;
      }
      if (step.step_type === "tokens") {
        addBandTokens(step);
        appendStep(renderStep(step));
        return;
      }
      if (step.step_type === "context_growth") {
        appendContextGrowth(step);
        return;
      }
      appendStep(renderStep(step));
    }

    if (replayBtn) {
      replayBtn.addEventListener("click", function () {
        var speed = parseFloat(window.prompt(
          "Velocidad del replay (0.5, 1, 2, 4, o 999 para instantáneo):",
          "1"
        ));
        if (isNaN(speed) || speed <= 0) return;
        withLatestTraceData(function (data) {
          startReplay(data, speed);
          flashAction(replayBtn, "▶ Reproduciendo");
        });
      });
    }

    // ----- Mejora #15: Modo explicador. --------------------------------
    var explainerToggle = host.querySelector("[data-trace-explainer-toggle]");
    if (explainerToggle) {
      var stored = null;
      try { stored = localStorage.getItem("live-agent-explainer"); } catch (e) {}
      if (stored === "1") {
        explainerToggle.checked = true;
        host.classList.add("live-agent--explainer");
      }
      explainerToggle.addEventListener("change", function () {
        if (explainerToggle.checked) {
          host.classList.add("live-agent--explainer");
          try { localStorage.setItem("live-agent-explainer", "1"); } catch (e) {}
        } else {
          host.classList.remove("live-agent--explainer");
          try { localStorage.setItem("live-agent-explainer", "0"); } catch (e) {}
        }
      });
    }

    // Polling adaptativo: la primera llamada arranca el ciclo recursivo.
    poll();
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

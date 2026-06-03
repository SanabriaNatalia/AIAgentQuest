/* Live Agent — vista de grafo "Constelación del Agente" (estilo n8n).
 *
 * Dibuja el agente como nodo central rodeado por sus herramientas (nodos
 * satélite siempre visibles). Cuando el agente llama una herramienta, la
 * arista pulsa hacia ella; cuando la herramienta devuelve, el pulso vuelve y
 * el nodo muestra contador + última salida.
 *
 * Se alimenta del CustomEvent `live-agent:data` que dispara dashboard.js con
 * el set completo de steps (idempotente) — no hace polling propio. Convive
 * con el timeline mediante un toggle; el timeline es la vista por defecto.
 *
 * Vanilla, sin dependencias. SVG con viewBox fijo (escala solo, no mide px).
 */
(function () {
  "use strict";

  var host = document.querySelector(".live-agent");
  if (!host) return;
  var svg = host.querySelector("[data-graph-svg]");
  var edgesG = host.querySelector("[data-graph-edges]");
  var nodesG = host.querySelector("[data-graph-nodes]");
  var graphHost = host.querySelector("[data-trace-graph]");
  var stepsHost = host.querySelector("[data-trace-steps]");
  var toggleBtn = host.querySelector("[data-trace-view-toggle]");
  var detailHost = host.querySelector("[data-graph-detail]");
  if (!svg || !edgesG || !nodesG) return;

  var SVGNS = "http://www.w3.org/2000/svg";
  var VIEW_W = 820, VIEW_H = 540;
  var CX = VIEW_W / 2, CY = VIEW_H / 2;
  var ORBIT = 188, AGENT_R = 60, TOOL_R = 44;

  var reducedMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Catálogo de respaldo si /api/agent/tools falla — las 4 tools del curso.
  var FALLBACK_TOOLS = [
    { name: "get_files_info", label: "Listar archivos", icon: "📂", description: "Lista archivos de un directorio." },
    { name: "get_file_content", label: "Leer archivo", icon: "📄", description: "Lee el contenido de un archivo." },
    { name: "write_file", label: "Escribir archivo", icon: "✍️", description: "Crea o sobrescribe un archivo." },
    { name: "run_python_file", label: "Ejecutar Python", icon: "🐍", description: "Ejecuta un archivo .py en el sandbox." }
  ];

  var tools = [];          // catálogo {name,label,icon,description}
  var nodeEls = {};        // name -> {group, pulse, badge, badgeText, label}
  var agentRing = null;

  // Estado de animación (se reinicia por trace o al reiniciar un replay).
  var currentTraceId = null;
  var lastStepCount = 0;
  var seenIds = {};        // step.id -> true
  var livePending = [];    // cola FIFO de nombres de tool para emparejar results
  var selectedTool = null;

  function el(tag, attrs, parent) {
    var n = document.createElementNS(SVGNS, tag);
    if (attrs) {
      for (var k in attrs) {
        if (attrs.hasOwnProperty(k)) n.setAttribute(k, attrs[k]);
      }
    }
    if (parent) parent.appendChild(n);
    return n;
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function truncate(s, n) {
    s = String(s == null ? "" : s);
    return s.length <= n ? s : s.slice(0, n - 1) + "…";
  }

  // Extrae {text, isError} de un function_result. Mismo contrato que el
  // timeline: shape nuevo {value, is_error} con fallback al string crudo.
  function extractResult(step) {
    var p = step.payload;
    if (p && typeof p === "object" && !Array.isArray(p) &&
        ("value" in p || "is_error" in p)) {
      var v = p.value;
      var text = (typeof v === "string") ? v : (function () {
        try { return JSON.stringify(v, null, 2); } catch (_e) { return String(v); }
      })();
      return { text: text, isError: !!p.is_error };
    }
    var raw = (typeof p === "string") ? p : (function () {
      try { return JSON.stringify(p); } catch (_e) { return String(p); }
    })();
    return { text: raw, isError: /^\s*error/i.test(raw) };
  }

  // ---- Construcción del grafo ---------------------------------------------

  function buildGraph() {
    edgesG.textContent = "";
    nodesG.textContent = "";
    nodeEls = {};

    var n = tools.length || 1;
    // Aristas primero (van por debajo de los nodos).
    tools.forEach(function (t, i) {
      var pos = toolPosition(i, n);
      var grp = el("g", { "class": "la-edge", "data-edge": t.name }, edgesG);
      el("line", {
        "class": "la-edge-base",
        x1: CX, y1: CY, x2: pos.x, y2: pos.y
      }, grp);
      var pulse = el("line", {
        "class": "la-edge-pulse",
        x1: CX, y1: CY, x2: pos.x, y2: pos.y
      }, grp);
      nodeEls[t.name] = { edge: grp, pulse: pulse };
    });

    // Nodo agente (central, grande).
    var agent = el("g", { "class": "la-agent", transform: "translate(" + CX + "," + CY + ")" }, nodesG);
    el("circle", { "class": "la-agent-glow", r: AGENT_R + 26, cx: 0, cy: 0, fill: "url(#la-agent-glow)" }, agent);
    agentRing = el("circle", { "class": "la-agent-ring", r: AGENT_R + 8, cx: 0, cy: 0 }, agent);
    el("circle", { "class": "la-agent-core", r: AGENT_R, cx: 0, cy: 0 }, agent);
    var sigil = el("text", { "class": "la-agent-sigil", x: 0, y: -4, "text-anchor": "middle" }, agent);
    sigil.textContent = "✦";
    var aLabel = el("text", { "class": "la-agent-label", x: 0, y: 22, "text-anchor": "middle" }, agent);
    aLabel.textContent = "Agente";

    // Nodos herramienta.
    tools.forEach(function (t, i) {
      var pos = toolPosition(i, n);
      var grp = el("g", {
        "class": "la-tool", "data-tool": t.name,
        transform: "translate(" + pos.x + "," + pos.y + ")",
        tabindex: "0", role: "button",
        "aria-label": t.label + ": " + t.description
      }, nodesG);

      el("circle", { "class": "la-tool-core", r: TOOL_R, cx: 0, cy: 0 }, grp);
      var icon = el("text", { "class": "la-tool-icon", x: 0, y: 2, "text-anchor": "middle" }, grp);
      icon.textContent = t.icon || "🛠";
      var label = el("text", { "class": "la-tool-label", x: 0, y: TOOL_R + 20, "text-anchor": "middle" }, grp);
      label.textContent = t.label || t.name;

      // Badge contador (oculto hasta la primera llamada).
      var badge = el("g", { "class": "la-tool-badge", transform: "translate(" + (TOOL_R - 6) + "," + (-TOOL_R + 6) + ")" }, grp);
      el("circle", { "class": "la-tool-badge-bg", r: 13, cx: 0, cy: 0 }, badge);
      var badgeText = el("text", { "class": "la-tool-badge-text", x: 0, y: 1, "text-anchor": "middle" }, badge);
      badgeText.textContent = "0";

      nodeEls[t.name].group = grp;
      nodeEls[t.name].badge = badge;
      nodeEls[t.name].badgeText = badgeText;

      grp.addEventListener("click", function () { selectTool(t.name); });
      grp.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selectTool(t.name); }
      });
    });
  }

  function toolPosition(i, n) {
    // Reparto radial empezando arriba (-90°).
    var angle = (-90 + i * (360 / n)) * Math.PI / 180;
    return { x: CX + ORBIT * Math.cos(angle), y: CY + ORBIT * Math.sin(angle) };
  }

  // ---- Animación ----------------------------------------------------------

  var nodeTimers = {};

  function flashClass(elem, cls, ms) {
    if (!elem) return;
    elem.classList.remove(cls);
    // Forzar reflow para reiniciar la animación CSS aunque la clase repita.
    void elem.getBoundingClientRect();
    elem.classList.add(cls);
  }

  function fireNode(name, dir, isError) {
    var node = nodeEls[name];
    if (!node) return;
    if (reducedMotion) {
      // Sin animación: solo refresca el estado final.
      if (dir === "in") node.group.classList.toggle("has-error", !!isError);
      return;
    }
    var pulseCls = dir === "out" ? "is-firing-out" : "is-firing-in";
    flashClass(node.pulse, pulseCls);
    if (dir === "out") {
      flashClass(node.group, "is-active");
    } else {
      node.group.classList.toggle("has-error", !!isError);
      flashClass(node.group, isError ? "flash-error" : "flash-ok");
    }
    // Limpia las clases transitorias.
    if (nodeTimers[name]) clearTimeout(nodeTimers[name]);
    nodeTimers[name] = setTimeout(function () {
      node.pulse.classList.remove("is-firing-out", "is-firing-in");
      node.group.classList.remove("is-active", "flash-ok", "flash-error");
    }, 900);
  }

  function startThinking() {
    if (agentRing && !reducedMotion) agentRing.classList.add("is-thinking");
  }
  function stopThinking() {
    if (agentRing) agentRing.classList.remove("is-thinking");
  }

  // ---- Procesamiento de datos --------------------------------------------

  function applyStep(step, animate) {
    var type = step.step_type;
    if (type === "function_call") {
      livePending.push(step.name || null);
      stopThinking();
      if (animate && step.name) fireNode(step.name, "out");
    } else if (type === "function_result") {
      var popped = livePending.length ? livePending.shift() : null;
      var nm = step.name || (step.payload && step.payload.name) || popped;
      if (animate && nm) {
        var r = extractResult(step);
        fireNode(nm, "in", r.isError);
      }
    } else if (type === "iteration_start") {
      if (animate) startThinking();
    } else if (type === "agent_final" || type === "session_end" || type === "error") {
      stopThinking();
    }
  }

  // Recalcula stats por herramienta sobre la lista completa (idempotente).
  function recompute(steps) {
    var stats = {};
    tools.forEach(function (t) {
      stats[t.name] = { calls: 0, lastArgs: null, lastResult: null, lastIsError: false };
    });
    var pending = [];
    steps.forEach(function (s) {
      if (!s) return;
      if (s.step_type === "function_call") {
        var nm = s.name;
        if (nm && stats[nm]) {
          stats[nm].calls += 1;
          var args = (s.payload && typeof s.payload === "object") ? s.payload.args : null;
          if (args != null) stats[nm].lastArgs = args;
        }
        pending.push(nm || null);
      } else if (s.step_type === "function_result") {
        var popped = pending.length ? pending.shift() : null;
        var target = s.name || (s.payload && s.payload.name) || popped;
        if (target && stats[target]) {
          var r = extractResult(s);
          stats[target].lastResult = r.text;
          stats[target].lastIsError = r.isError;
        }
      }
    });
    return stats;
  }

  var lastStats = {};

  function refreshBadges(stats) {
    tools.forEach(function (t) {
      var node = nodeEls[t.name];
      if (!node) return;
      var st = stats[t.name] || { calls: 0, lastIsError: false };
      if (node.badgeText) node.badgeText.textContent = String(st.calls);
      if (node.badge) node.badge.classList.toggle("is-visible", st.calls > 0);
      node.group.classList.toggle("has-error", !!st.lastIsError && st.calls > 0);
      node.group.classList.toggle("has-run", st.calls > 0);
    });
  }

  function resetAnimationState() {
    seenIds = {};
    livePending = [];
    lastStats = {};
    stopThinking();
    Object.keys(nodeEls).forEach(function (name) {
      var node = nodeEls[name];
      if (!node.group) return;
      node.group.classList.remove("is-active", "flash-ok", "flash-error", "has-error", "has-run");
      if (node.pulse) node.pulse.classList.remove("is-firing-out", "is-firing-in");
      if (node.badge) node.badge.classList.remove("is-visible");
      if (node.badgeText) node.badgeText.textContent = "0";
    });
  }

  function onData(data) {
    if (!data || !tools.length) return;
    var steps = data.steps || [];
    var traceId = data.trace_id || null;

    var isNewTrace = traceId !== currentTraceId;
    if (isNewTrace) {
      resetAnimationState();
      currentTraceId = traceId;
    } else if (steps.length < lastStepCount) {
      // El conjunto encogió con el mismo trace → replay reiniciado: re-animar.
      resetAnimationState();
    }

    // Primera pintura de un trace (carga de histórico o trace ya avanzado):
    // pobla el estado sin animar para evitar un aluvión de pulsos.
    var firstPaint = (Object.keys(seenIds).length === 0) && steps.length > 1 &&
      (isNewTrace);

    steps.forEach(function (step) {
      if (step == null || seenIds[step.id]) return;
      seenIds[step.id] = true;
      applyStep(step, !firstPaint);
    });

    lastStepCount = steps.length;
    lastStats = recompute(steps);
    refreshBadges(lastStats);
    if (selectedTool) renderDetail(selectedTool);
  }

  // ---- Panel de detalle ---------------------------------------------------

  function selectTool(name) {
    selectedTool = name;
    tools.forEach(function (t) {
      var node = nodeEls[t.name];
      if (node && node.group) node.group.classList.toggle("is-selected", t.name === name);
    });
    renderDetail(name);
  }

  function renderDetail(name) {
    if (!detailHost) return;
    var tool = null;
    for (var i = 0; i < tools.length; i++) { if (tools[i].name === name) { tool = tools[i]; break; } }
    if (!tool) return;
    var st = lastStats[name] || { calls: 0, lastArgs: null, lastResult: null, lastIsError: false };

    var argsHtml = "";
    if (st.lastArgs && typeof st.lastArgs === "object" && !Array.isArray(st.lastArgs)) {
      var keys = Object.keys(st.lastArgs);
      if (keys.length) {
        argsHtml = '<dl class="la-detail-args">' + keys.map(function (k) {
          var v = st.lastArgs[k];
          var vs = (typeof v === "string") ? v : (function () {
            try { return JSON.stringify(v); } catch (_e) { return String(v); }
          })();
          return "<dt>" + escapeHtml(k) + "</dt><dd>" + escapeHtml(vs) + "</dd>";
        }).join("") + "</dl>";
      }
    }

    var resultHtml = "";
    if (st.lastResult != null && st.lastResult !== "") {
      resultHtml =
        '<div class="la-detail-result-label">' +
          (st.lastIsError ? "⚠️ Devolvió un error" : "📦 Devolvió") + "</div>" +
        '<pre class="la-detail-result' + (st.lastIsError ? " is-error" : "") + '">' +
          escapeHtml(truncate(st.lastResult, 1200)) + "</pre>";
    }

    detailHost.hidden = false;
    detailHost.innerHTML =
      '<header class="la-detail-head">' +
        '<span class="la-detail-icon" aria-hidden="true">' + escapeHtml(tool.icon || "🛠") + "</span>" +
        '<span class="la-detail-title">' + escapeHtml(tool.label || tool.name) + "</span>" +
        '<span class="la-detail-count">' + st.calls + (st.calls === 1 ? " llamada" : " llamadas") + "</span>" +
      "</header>" +
      '<p class="la-detail-desc">' + escapeHtml(tool.description || "") + "</p>" +
      '<code class="la-detail-name">' + escapeHtml(tool.name) + "</code>" +
      (argsHtml ? '<div class="la-detail-section"><span class="la-detail-section-label">Últimos argumentos</span>' + argsHtml + "</div>" : "") +
      (resultHtml ? '<div class="la-detail-section">' + resultHtml + "</div>" :
        (st.calls === 0 ? '<p class="la-detail-empty">Aún no se ha llamado en este trace.</p>' : "")) ;
  }

  // ---- Toggle de vista ----------------------------------------------------

  var STORAGE_KEY = "live-agent-view";

  function setView(view) {
    var graph = view === "graph";
    if (graphHost) graphHost.hidden = !graph;
    if (stepsHost) stepsHost.hidden = graph;
    if (toggleBtn) {
      toggleBtn.setAttribute("aria-pressed", graph ? "true" : "false");
      toggleBtn.textContent = graph ? "📜 Timeline" : "🕸 Grafo";
    }
    try { localStorage.setItem(STORAGE_KEY, view); } catch (_e) {}
  }

  if (toggleBtn) {
    toggleBtn.addEventListener("click", function () {
      var goingToGraph = (graphHost && graphHost.hidden);
      setView(goingToGraph ? "graph" : "timeline");
    });
  }

  // ---- Init ---------------------------------------------------------------

  function init(catalog) {
    tools = (catalog && catalog.length) ? catalog : FALLBACK_TOOLS;
    buildGraph();

    host.addEventListener("live-agent:data", function (e) {
      onData(e.detail);
    });

    // Vista por defecto: timeline (no sorprende al aprendiz). Respeta la
    // última elección guardada.
    var stored = null;
    try { stored = localStorage.getItem(STORAGE_KEY); } catch (_e) {}
    setView(stored === "graph" ? "graph" : "timeline");
  }

  var url = host.dataset.agentToolsUrl;
  if (url) {
    fetch(url, { headers: { Accept: "application/json" } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) { init(data && data.tools); })
      .catch(function () { init(null); });
  } else {
    init(null);
  }
})();

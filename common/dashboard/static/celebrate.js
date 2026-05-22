// Confetti DOM-based para /celebrate. Sin librerías.
// Respeta prefers-reduced-motion: no spawnea nada si el usuario lo pidió.
(function () {
  var COLORS = ["#c9a961", "#8b5cf6", "#c084fc", "#65d196", "#e8b94d"];
  var PARTICLES = 36;
  var DURATION_MS = 2600;

  function reducedMotion() {
    try {
      return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch (_) {
      return false;
    }
  }

  function spawn(container) {
    var rect = container.getBoundingClientRect();
    var width = rect.width || window.innerWidth;
    for (var i = 0; i < PARTICLES; i++) {
      var p = document.createElement("span");
      p.className = "confetti-piece";
      var startX = Math.random() * width;
      var color = COLORS[Math.floor(Math.random() * COLORS.length)];
      var rotate = Math.floor(Math.random() * 360);
      var delay = Math.random() * 400;
      var duration = DURATION_MS + Math.random() * 600;
      var size = 5 + Math.random() * 5;
      var drift = (Math.random() - 0.5) * 160;

      p.style.left = startX + "px";
      p.style.background = color;
      p.style.width = size + "px";
      p.style.height = (size * 1.6) + "px";
      p.style.setProperty("--rotate", rotate + "deg");
      p.style.setProperty("--drift", drift + "px");
      p.style.animationDelay = delay + "ms";
      p.style.animationDuration = duration + "ms";

      container.appendChild(p);
      setTimeout(function (node) {
        return function () { if (node.parentNode) node.parentNode.removeChild(node); };
      }(p), delay + duration + 100);
    }
  }

  function init() {
    if (reducedMotion()) return;
    var hosts = document.querySelectorAll("[data-confetti=\"true\"]");
    hosts.forEach(function (host) {
      var container = host.querySelector(".celebrate-confetti");
      if (!container) return;
      spawn(container);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

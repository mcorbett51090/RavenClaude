/*
 * RavenClaude — Constellation Background (shared partial)
 * ----------------------------------------------------------------------------
 * Renders an SVG constellation overlay as a fixed background layer behind
 * the page content. Used by `index.html` and `dashboard.html` (ravenpower
 * aesthetic). Read at generate-time and inlined via the
 * `/*__CONSTELLATION_JS__*\/` marker substitution.
 *
 * Design (per designer-panel, v0.104.0):
 *   - 140 stars, mixed radii r=0.8..3.5, opacity 0.25..0.85
 *   - 90% white #ffffff + 10% gold-tinted #f5e8c0 ("warm Norse sky")
 *   - Deterministic seeded LCG (NOT Math.random) — same sky every load
 *   - Static (no animation v1; drift/parallax is v2)
 *   - position: fixed, inset: 0, z-index: 0, pointer-events: none
 *   - aria-hidden="true" (pure decoration)
 *   - Respects prefers-reduced-motion (no effect v1; defensive for v2)
 *
 * Insertion: the page sets up a placeholder element <svg id="rc-constellation"
 * style="position:fixed;inset:0;z-index:0;pointer-events:none" aria-hidden="true">
 * at the very top of <body>. This script populates it with <circle> children
 * sized to the viewport. Page body content sits at z-index >= 1.
 *
 * Recomputed on resize (debounced) so the constellation stays viewport-fit.
 */

(function renderConstellation() {
  "use strict";
  var svg = document.getElementById("rc-constellation");
  if (!svg) return;

  // Linear Congruential Generator — deterministic across loads.
  // Fixed seed = 0xDEADBEEF. We never call Math.random.
  function lcg(seed) {
    var s = seed >>> 0;
    return function next() {
      s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
      return s / 4294967296;
    };
  }

  function draw() {
    var w = window.innerWidth || document.documentElement.clientWidth || 1440;
    var h = window.innerHeight || document.documentElement.clientHeight || 900;
    // Density: ~140 stars at 1440x900 viewport-equivalent. Scale linearly with area.
    var density = (w * h) / (1440 * 900);
    var STAR_COUNT = Math.max(40, Math.min(220, Math.round(140 * density)));

    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
    // Wipe + redraw
    while (svg.firstChild) svg.removeChild(svg.firstChild);

    var rng = lcg(0xdeadbeef ^ STAR_COUNT);
    var NS = "http://www.w3.org/2000/svg";
    for (var i = 0; i < STAR_COUNT; i++) {
      var x = rng() * w;
      var y = rng() * h;
      // Size distribution: 80% small (0.8-1.2), 15% mid (1.5-2), 5% large (2.5-3.5)
      var rRoll = rng();
      var r;
      if (rRoll < 0.8) r = 0.8 + rng() * 0.4;
      else if (rRoll < 0.95) r = 1.5 + rng() * 0.5;
      else r = 2.5 + rng() * 1.0;
      // Opacity: 0.25..0.85, brighter for larger stars
      var opacity = 0.25 + rng() * 0.6;
      if (r > 2) opacity = Math.max(opacity, 0.7);
      // Color: 90% white + 10% gold-tinted
      var fill = rng() < 0.9 ? "#ffffff" : "#f5e8c0";
      var c = document.createElementNS(NS, "circle");
      c.setAttribute("cx", x.toFixed(2));
      c.setAttribute("cy", y.toFixed(2));
      c.setAttribute("r", r.toFixed(2));
      c.setAttribute("fill", fill);
      c.setAttribute("opacity", opacity.toFixed(2));
      svg.appendChild(c);
    }
  }

  // Debounced resize handler — constellation re-fits viewport
  var resizeT;
  function onResize() {
    clearTimeout(resizeT);
    resizeT = setTimeout(draw, 150);
  }
  window.addEventListener("resize", onResize);

  draw();
})();

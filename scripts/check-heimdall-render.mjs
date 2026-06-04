#!/usr/bin/env node
/* check-heimdall-render.mjs — behavioral test for the Heimdall tab's render
 * logic (the perimeter-alarm surface added in core v0.67.0).
 *
 * Extracts the REAL render functions (renderHookEvents / renderGjallarhorn /
 * renderVersionDrift / renderCiStatus + the TIER_LABEL constant) from the
 * generated dashboard.html and drives them against fixtures under a tiny DOM
 * stub. Asserts the build-plan §3.1 acceptance cases:
 *   - a red (destructive) hook event → Gjallarhorn banner shows red + a hook row
 *   - amber-only → amber banner; grey-only → grey banner
 *   - empty hook events → banner hidden, "quiet" empty state
 *   - version drift → DRIFT row rendered; clean → "in sync" caption
 *   - aria-live: red = assertive, amber/grey = polite
 *
 * No real browser/jsdom — a minimal document stub records the DOM the functions
 * build, which is enough to assert structure + text + classes. Pairs with
 * `node --check` (syntax) for behavioral coverage, mirroring
 * check-dashboard-roundtrip.mjs.
 *
 * Usage: node scripts/check-heimdall-render.mjs [path/to/dashboard.html]
 */
import { readFileSync } from "node:fs";

const htmlPath = process.argv[2] || "plugins/ravenclaude-core/dashboard.html";
const html = readFileSync(htmlPath, "utf8");

const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const app =
  scripts.find((s) => s.includes("function activate(")) ||
  scripts.reduce((a, b) => (b.length > a.length ? b : a), "");

/* Extract a brace-balanced top-level `function NAME(...) {...}` or
 * `const NAME = ...;` declaration by header. (Same idiom as the round-trip test.) */
function extract(src, header) {
  const start = src.indexOf(header);
  if (start === -1) throw new Error(`not found in dashboard.html: ${header}`);
  let i = src.indexOf("{", start);
  let depth = 0;
  for (; i < src.length; i++) {
    if (src[i] === "{") depth++;
    else if (src[i] === "}") {
      depth--;
      if (depth === 0) break;
    }
  }
  let end = i + 1;
  while (end < src.length && /[);\s]/.test(src[end]) && src[end] !== "\n") end++;
  return src.slice(start, end);
}

/* ── Minimal DOM stub ──────────────────────────────────────────────────────
 * Records children, className, textContent, attributes — enough to assert the
 * structure the render functions build. */
class El {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this._class = "";
    this._text = "";
    this.attrs = {};
    this.hidden = false;
    this.href = "";
  }
  set className(v) {
    this._class = v;
  }
  get className() {
    return this._class;
  }
  set textContent(v) {
    this._text = String(v);
    this.children = [];
  }
  get textContent() {
    if (this.children.length) return this.children.map((c) => c.textContent).join("");
    return this._text;
  }
  appendChild(c) {
    this.children.push(c);
    return c;
  }
  append(...cs) {
    for (const c of cs) this.children.push(c);
  }
  replaceChildren(...cs) {
    this.children = cs.filter(Boolean);
  }
  setAttribute(k, v) {
    this.attrs[k] = String(v);
  }
  getAttribute(k) {
    return this.attrs[k];
  }
  appendData() {}
  /* helpers for assertions */
  flatText() {
    return (this._text || "") + this.children.map((c) => c.flatText()).join(" ");
  }
  find(pred) {
    if (pred(this)) return this;
    for (const c of this.children) {
      const r = c.find(pred);
      if (r) return r;
    }
    return null;
  }
  findAll(pred, acc = []) {
    if (pred(this)) acc.push(this);
    for (const c of this.children) c.findAll(pred, acc);
    return acc;
  }
}

const registry = {};
function mkHost(id) {
  const e = new El("div");
  e.id = id;
  registry[id] = e;
  return e;
}

const banner = mkHost("gjallarhorn-banner");
const bannerText = mkHost("gjallarhorn-text");
const hookHost = mkHost("heimdall-hooks");
const driftHost = mkHost("heimdall-drift");
const ciHost = mkHost("heimdall-ci");
const alarmHost = mkHost("heimdall-alarm");

global.document = {
  createElement: (t) => new El(t),
  createDocumentFragment: () => new El("#fragment"),
  createTextNode: (t) => {
    const e = new El("#text");
    e._text = String(t);
    return e;
  },
  getElementById: (id) => registry[id] || null,
};

/* sagaEmptyPanel is reused by the Heimdall renderers (aliased as hmEmpty). */
const sagaEmptyPanelSrc = `
function sagaEmptyPanel(primaryText, codeSnippet) {
  const wrap = document.createElement("div");
  wrap.className = "saga-empty";
  const p = document.createElement("p");
  p.textContent = primaryText;
  if (codeSnippet) { const code = document.createElement("code"); code.textContent = codeSnippet; p.appendChild(code); }
  wrap.appendChild(p);
  return wrap;
}
function hmEmpty(a, b) { return sagaEmptyPanel(a, b); }
`;

const pieces = [
  sagaEmptyPanelSrc,
  extract(app, "const TIER_LABEL ="),
  extract(app, "function renderHookEvents("),
  extract(app, "function renderVersionDrift("),
  extract(app, "function renderGjallarhorn("),
  extract(app, "function renderCiStatus("),
];

const loaded = new Function(
  `${pieces.join("\n")}\n return { renderHookEvents, renderVersionDrift, renderGjallarhorn, renderCiStatus };`,
)();

let failures = 0;
function ok(cond, msg) {
  if (cond) console.log("  ✓ " + msg);
  else {
    console.log("  ✗ " + msg);
    failures++;
  }
}

/* ── Fixtures ── */
const redData = {
  by_hook: {
    "guard-destructive.sh": [
      {
        hook: "guard-destructive.sh",
        verdict: "deny",
        rule: "destructive-pattern",
        path: "git push --force",
        ts: "2026-05-30T10:00:00Z",
        tier: "red",
      },
    ],
    "enforce-layout.sh": [
      {
        hook: "enforce-layout.sh",
        verdict: "deny",
        rule: "off-allow-list",
        path: "x/off.md",
        ts: "2026-05-30T09:00:00Z",
        tier: "amber",
      },
    ],
  },
  total: 2,
  gjallarhorn_tier: "red",
};

/* Case 1: red event → red banner + a hook row present */
loaded.renderHookEvents(redData);
loaded.renderGjallarhorn(redData.gjallarhorn_tier);
ok(banner.hidden === false, "red event: banner is visible");
ok(banner.className.includes("gjallarhorn--red"), "red event: banner carries --red");
ok(banner.getAttribute("aria-live") === "assertive", "red tier: aria-live=assertive");
ok(
  hookHost.findAll((e) => e.className && e.className.includes("hm-evt")).length === 2,
  "red event: two hook rows rendered",
);
ok(
  hookHost.find((e) => e.className === "hm-badge hm-badge--red") !== null,
  "red event: a red badge is present",
);

/* Case 2: amber-only → amber banner, polite */
loaded.renderGjallarhorn("amber");
ok(banner.className.includes("gjallarhorn--amber"), "amber: banner carries --amber");
ok(banner.getAttribute("aria-live") === "polite", "amber tier: aria-live=polite");

/* Case 3: grey-only → grey banner, polite */
loaded.renderGjallarhorn("grey");
ok(banner.className.includes("gjallarhorn--grey"), "grey: banner carries --grey");
ok(banner.getAttribute("aria-live") === "polite", "grey tier: aria-live=polite");

/* Case 4: empty → banner hidden + quiet empty state */
loaded.renderHookEvents({ by_hook: {}, total: 0, gjallarhorn_tier: null });
loaded.renderGjallarhorn(null);
ok(banner.hidden === true, "empty: banner is hidden");
ok(hookHost.flatText().toLowerCase().includes("quiet"), "empty: 'quiet' empty state shown");

/* Case 5: version drift → DRIFT row + caption; clean → in-sync caption */
loaded.renderVersionDrift([
  { plugin: "a", marketplace_version: "1.0.0", plugin_version: "1.0.0", drift: false },
  { plugin: "b", marketplace_version: "1.0.0", plugin_version: "1.1.0", drift: true },
]);
ok(
  driftHost.find((e) => e.className === "hm-stat--drift") !== null,
  "drift: a DRIFT status cell is rendered",
);
ok(driftHost.flatText().includes("1 of 2"), "drift: caption counts the drift");
loaded.renderVersionDrift([
  { plugin: "a", marketplace_version: "1.0.0", plugin_version: "1.0.0", drift: false },
]);
ok(driftHost.flatText().toLowerCase().includes("in sync"), "clean: 'in sync' caption");

/* Case 6: CI rows → success/fail dots */
loaded.renderCiStatus([
  { name: "Validate", status: "completed", conclusion: "success", url: "http://x", branch: "main" },
  { name: "Lint", status: "completed", conclusion: "failure", url: "http://y", branch: "pr" },
]);
ok(
  ciHost.find((e) => e.className && e.className.includes("hm-ci-dot--ok")) !== null,
  "ci: a success dot is rendered",
);
ok(
  ciHost.find((e) => e.className && e.className.includes("hm-ci-dot--fail")) !== null,
  "ci: a fail dot is rendered",
);

console.log("");
if (failures === 0) {
  console.log("Heimdall render: ALL ASSERTIONS PASS");
  process.exit(0);
}
console.log(`Heimdall render: ${failures} assertion(s) FAILED`);
process.exit(1);

#!/usr/bin/env node
/* check-vidarr-render.mjs — behavioral test for the Víðarr "Security log" tab's
 * render + filter logic (added in core v0.68.0).
 *
 * Extracts the REAL renderVidarrTable function (+ the VIDARR_KIND_LABEL constant
 * and the hmEmpty/sagaEmptyPanel helper it reuses) from the generated
 * dashboard.html and drives it against fixtures under a tiny DOM stub. Asserts
 * the build-plan §3.11 acceptance cases:
 *   - a security_deny + a posture-change event both render rows (chronological)
 *   - the type filter narrows to one kind
 *   - an empty event set → the "quiet" empty state
 *   - the security-deny row carries its kind tag
 *
 * No real browser/jsdom — a minimal document stub records the DOM the function
 * builds. The kind filter is driven through the module-level `vidarrKindFilter`
 * the function reads, so we re-declare it in the harness scope. Mirrors
 * check-heimdall-render.mjs.
 *
 * Usage: node scripts/check-vidarr-render.mjs [path/to/dashboard.html]
 */
import { readFileSync } from "node:fs";

const htmlPath = process.argv[2] || "plugins/ravenclaude-core/dashboard.html";
const html = readFileSync(htmlPath, "utf8");

const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const app = scripts.reduce((a, b) => (b.length > a.length ? b : a), "");

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

/* ── Minimal DOM stub (same shape as check-heimdall-render.mjs) ── */
class El {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this._class = "";
    this._text = "";
    this.attrs = {};
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
const content = mkHost("vidarr-content");
const count = mkHost("vidarr-count");

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

/* renderVidarrTable reads a module-level `vidarrKindFilter`; expose a mutable one
 * via a closure setter so the harness can drive the type filter. */
const harness = new Function(
  `${sagaEmptyPanelSrc}
   let vidarrKindFilter = "all";
   ${extract(app, "const VIDARR_KIND_LABEL =")}
   ${extract(app, "function renderVidarrTable(")}
   return {
     render: renderVidarrTable,
     setFilter: (k) => { vidarrKindFilter = k; },
   };`,
)();

let failures = 0;
function ok(cond, msg) {
  if (cond) console.log("  ✓ " + msg);
  else {
    console.log("  ✗ " + msg);
    failures++;
  }
}

const events = [
  {
    ts: "2026-05-30T12:00:00Z",
    kind: "posture-change",
    category: "project",
    summary: "+1 deny",
    source: "dashboard-save",
  },
  {
    ts: "2026-05-30T11:00:00Z",
    kind: "security-deny",
    category: "guard-destructive.sh",
    summary: "destructive-pattern · git push --force",
    source: "Bash",
  },
];

/* Case 1: both kinds render rows */
harness.setFilter("all");
harness.render(events);
ok(
  content.findAll((e) => e.className && e.className.startsWith("vidarr-row")).length === 2,
  "all filter: two rows render",
);
ok(
  content.find((e) => e.className === "vidarr-kind vidarr-kind--security-deny") !== null,
  "security-deny row carries its kind tag",
);
ok(count.textContent.includes("2 events"), "count shows 2 events");

/* Case 2: type filter narrows to posture-change only */
harness.setFilter("posture-change");
harness.render(events);
ok(
  content.findAll((e) => e.className && e.className.startsWith("vidarr-row")).length === 1,
  "posture filter: one row",
);
ok(
  content.find((e) => e.className === "vidarr-row vidarr-row--posture-change") !== null,
  "posture filter: it's the posture row",
);

/* Case 3: security-deny filter narrows to the deny */
harness.setFilter("security-deny");
harness.render(events);
ok(
  content.find((e) => e.className === "vidarr-row vidarr-row--security-deny") !== null,
  "deny filter: the deny row shows",
);
ok(
  content.find((e) => e.className === "vidarr-row vidarr-row--posture-change") === null,
  "deny filter: posture row hidden",
);

/* Case 4: empty → quiet empty state */
harness.setFilter("all");
harness.render([]);
ok(content.flatText().toLowerCase().includes("quiet"), "empty: 'quiet' empty state shown");
ok(count.textContent === "", "empty: count cleared");

console.log("");
if (failures === 0) {
  console.log("Víðarr render: ALL ASSERTIONS PASS");
  process.exit(0);
}
console.log(`Víðarr render: ${failures} assertion(s) FAILED`);
process.exit(1);

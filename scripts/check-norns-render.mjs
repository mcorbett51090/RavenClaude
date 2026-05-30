#!/usr/bin/env node
/* check-norns-render.mjs — behavioral test for the Norns "Lineage" tab's render
 * logic (the Urðr/Verðandi/Skuld lineage view added in core v0.69.0).
 *
 * Extracts the REAL render functions (renderNornsUrdr / renderNornsVerdandi /
 * renderNornsSkuld + the nornsList/hmEmpty helpers) from the generated
 * dashboard.html and drives them against fixtures under a tiny DOM stub. Asserts
 * the build-plan §3.5 acceptance cases:
 *   - Urðr renders surfaced scenarios + commits
 *   - Verðandi renders version + hook/rule counts + last release
 *   - Skuld shows the GATED EMPTY STATE when next_version is absent (the v1 case)
 *   - Skuld renders next_version + proposals when present
 *
 * No real browser/jsdom — a minimal document stub records the DOM. Mirrors
 * check-heimdall-render.mjs / check-vidarr-render.mjs.
 *
 * Usage: node scripts/check-norns-render.mjs [path/to/dashboard.html]
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
const urdr = mkHost("norns-urdr");
const verdandi = mkHost("norns-verdandi");
const skuld = mkHost("norns-skuld");

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

const loaded = new Function(
  `${sagaEmptyPanelSrc}
   ${extract(app, "function nornsList(")}
   ${extract(app, "function renderNornsUrdr(")}
   ${extract(app, "function renderNornsVerdandi(")}
   ${extract(app, "function renderNornsSkuld(")}
   return { renderNornsUrdr, renderNornsVerdandi, renderNornsSkuld };`,
)();

let failures = 0;
function ok(cond, msg) {
  if (cond) console.log("  ✓ " + msg);
  else {
    console.log("  ✗ " + msg);
    failures++;
  }
}

/* Case 1: Urðr renders scenarios + commits */
loaded.renderNornsUrdr({
  scenarios: [{ scenario_path: "plugins/ravenclaude-core/scenarios/2026-05-30-x.md" }],
  decisions: [],
  commits: ["abc123 feat: a thing", "def456 fix: another"],
});
ok(urdr.flatText().includes("2026-05-30-x.md"), "Urðr: surfaced scenario shows (basename)");
ok(urdr.flatText().includes("abc123"), "Urðr: commit shows");
ok(urdr.flatText().toLowerCase().includes("no decision-log"), "Urðr: empty decisions state");

/* Case 2: Verðandi renders version + counts */
loaded.renderNornsVerdandi({ version: "0.69.0", hooks: 14, rules: 4, last_release: "2026-05-30" });
ok(verdandi.flatText().includes("0.69.0"), "Verðandi: version shows");
ok(verdandi.flatText().includes("14"), "Verðandi: hook count shows");
ok(verdandi.flatText().includes("2026-05-30"), "Verðandi: last release shows");

/* Case 3: Skuld GATED empty state when next_version absent (the v1 case) */
loaded.renderNornsSkuld({ next_version: "", roadmap: [], proposals: [] });
ok(skuld.flatText().includes("next_version"), "Skuld: gated empty state names next_version");

/* Case 4: Skuld renders data when present */
loaded.renderNornsSkuld({ next_version: "0.70.0", roadmap: ["thing A"], proposals: ["p1.md"] });
ok(skuld.flatText().includes("0.70.0"), "Skuld: proposed version shows");
ok(skuld.flatText().includes("p1.md"), "Skuld: proposal shows");
ok(!skuld.flatText().includes("Add a next_version"), "Skuld: gated state gone when populated");

console.log("");
if (failures === 0) {
  console.log("Norns render: ALL ASSERTIONS PASS");
  process.exit(0);
}
console.log(`Norns render: ${failures} assertion(s) FAILED`);
process.exit(1);

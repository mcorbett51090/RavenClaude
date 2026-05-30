#!/usr/bin/env node
/* check-nidhoggr-render.mjs — behavioral test for the Níðhöggr "Debt watch" card
 * (lives inside the Heimdall tab; added in core v0.74.0).
 *
 * Extracts the REAL renderNidhoggr + nidhoggrSection functions from the generated
 * dashboard.html and drives them against fixtures under a tiny DOM stub. Asserts:
 *   - each of the four signals renders a section with a count
 *   - a populated signal lists its items; an empty signal shows "clean"
 *
 * No real browser/jsdom — a minimal document stub records the DOM. Mirrors
 * check-norns-render.mjs.
 *
 * Usage: node scripts/check-nidhoggr-render.mjs [path/to/dashboard.html]
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
  flatText() {
    return (this._text || "") + this.children.map((c) => c.flatText()).join(" ");
  }
}

const registry = {};
function mkHost(id) {
  const e = new El("div");
  e.id = id;
  registry[id] = e;
  return e;
}
const debt = mkHost("heimdall-debt");

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
function sagaEmptyPanel(p, c){const w=document.createElement("div");w.className="saga-empty";const x=document.createElement("p");x.textContent=p;w.appendChild(x);return w;}
function hmEmpty(a,b){return sagaEmptyPanel(a,b);}
`;

const loaded = new Function(
  `${sagaEmptyPanelSrc}
   ${extract(app, "function nidhoggrSection(")}
   ${extract(app, "function renderNidhoggr(")}
   return { renderNidhoggr };`,
)();

let failures = 0;
function ok(cond, msg) {
  if (cond) console.log("  ✓ " + msg);
  else {
    console.log("  ✗ " + msg);
    failures++;
  }
}

/* Case 1: populated signals render counts + items */
loaded.renderNidhoggr({
  stale_plugins: [{ plugin: "foo", last_bump: "2025-12-01" }],
  ungated_hooks: [
    { hook: "a.sh", plugin: "core" },
    { hook: "b.sh", plugin: "core" },
  ],
  superseded_decisions: [],
  todo_commits: ["abc123 TODO fix the thing"],
  stale_threshold_days: 120,
});
ok(debt.flatText().includes("120+ days"), "stale section names the 120-day threshold");
ok(debt.flatText().includes("foo (last 2025-12-01)"), "stale plugin item shows");
ok(debt.flatText().includes("Hooks without a CI gate (2)"), "ungated-hooks count = 2");
ok(debt.flatText().includes("a.sh — core"), "ungated hook item shows");
ok(debt.flatText().includes("Superseded decisions (0)"), "superseded count = 0");
ok(debt.flatText().includes("clean"), "empty signal shows 'clean'");
ok(debt.flatText().includes("abc123 TODO"), "todo commit shows");

/* Case 2: all-clean → every section reads clean, no items */
loaded.renderNidhoggr({
  stale_plugins: [],
  ungated_hooks: [],
  superseded_decisions: [],
  todo_commits: [],
  stale_threshold_days: 120,
});
const cleanCount = (debt.flatText().match(/clean/g) || []).length;
ok(cleanCount === 4, "all-clean: four sections all read 'clean'");

console.log("");
if (failures === 0) {
  console.log("Níðhöggr render: ALL ASSERTIONS PASS");
  process.exit(0);
}
console.log(`Níðhöggr render: ${failures} assertion(s) FAILED`);
process.exit(1);

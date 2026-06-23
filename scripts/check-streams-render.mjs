#!/usr/bin/env node
/* check-streams-render.mjs — Gate 113 behavioral test for the Streams tab.
 *
 * Part of Agentic Work-Streams P3 (docs/plans/2026-06-23-agentic-work-streams/plan.md).
 * Three properties:
 *   1. RENDER — extracts the REAL renderStreamsList / renderStreamsHistory from the
 *      generated dashboard.html and drives them against fixtures: a populated list
 *      (active marked), an empty store (honest "create one" empty), no-active
 *      (history shows "set one"), and derived history (kind/label/terms render).
 *   2. NO-PROMPT-EGRESS — the server-side _read_streams reader (shared, byte-identical
 *      across both serve-dashboards.py copies) WHITELISTS event fields, so a
 *      hand-corrupted history line carrying a `prompt` field with a distinctive phrase
 *      is dropped: the rendered payload never contains the phrase. (We assert the
 *      reader's whitelist behavior + that the render functions only read whitelisted
 *      keys.) Must-fail half: a fixture whose history event carries a raw `prompt`
 *      field — the render functions must NOT surface it.
 *   3. PARITY — both serve-dashboards.py copies define `_read_streams` and register
 *      `/__streams` (the duplication invariant; Gate 32 covers byte-identity).
 *
 * No browser/jsdom — a minimal document stub records the DOM. Mirrors
 * check-mimir-render.mjs / check-norns-render.mjs.
 *
 * Usage: node scripts/check-streams-render.mjs [path/to/dashboard.html]
 */
import { readFileSync, existsSync } from "node:fs";

const htmlPath = process.argv[2] || "plugins/ravenclaude-core/dashboard.html";
const html = readFileSync(htmlPath, "utf8");

const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const app =
  scripts.find((s) => s.includes("function activate(")) ||
  scripts.reduce((a, b) => (b.length > a.length ? b : a), "");

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
    this.style = {};
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
const listHost = mkHost("streams-list");
const histHost = mkHost("streams-history");

global.document = {
  createElement: (t) => new El(t),
  createDocumentFragment: () => new El("#fragment"),
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

const pieces = [
  sagaEmptyPanelSrc,
  extract(app, "function renderStreamsList("),
  extract(app, "function renderStreamsHistory("),
];

const loaded = new Function(
  `${pieces.join("\n")}\n return { renderStreamsList, renderStreamsHistory };`,
)();

let failures = 0;
function ok(cond, msg) {
  if (cond) console.log("  ✓ " + msg);
  else {
    console.log("  ✗ " + msg);
    failures++;
  }
}

const PHRASE = "the QUASAR-7 confidential migration phrase";

/* ── Fixture 1: populated list ─────────────────────────────────────────── */
loaded.renderStreamsList({
  count: 2,
  active: "billing-work",
  streams: [
    {
      id: "billing-work",
      name: "Billing Work",
      event_count: 5,
      updated: "2026-06-23T01:00:00Z",
      active: true,
    },
    {
      id: "auth-flow",
      name: "Auth Flow",
      event_count: 2,
      updated: "2026-06-23T00:30:00Z",
      active: false,
    },
  ],
});
ok(listHost.flatText().includes("billing-work"), "populated: stream id renders");
ok(listHost.flatText().includes("Billing Work"), "populated: stream name renders");
ok(listHost.flatText().includes("active: billing-work"), "populated: active summary renders");
ok(listHost.flatText().includes("★"), "populated: active stream is marked");

/* ── Fixture 2: empty store ────────────────────────────────────────────── */
loaded.renderStreamsList({ count: 0, active: null, streams: [] });
ok(listHost.flatText().toLowerCase().includes("no work-streams"), "empty: honest empty state");
ok(listHost.flatText().includes("rc streams create"), "empty: surfaces the create hint");

/* ── Fixture 3: no active stream → history empty state ─────────────────── */
loaded.renderStreamsHistory({ active: null, active_history: [] });
ok(
  histHost.flatText().toLowerCase().includes("no active stream"),
  "no-active: history empty state",
);
ok(
  histHost.flatText().includes("rc streams set-active"),
  "no-active: surfaces the set-active hint",
);

/* ── Fixture 4: derived history renders ────────────────────────────────── */
loaded.renderStreamsHistory({
  active: "billing-work",
  active_history: [
    {
      kind: "classified",
      label: "bill-invoice",
      terms: ["bill", "invoice"],
      word_count: 7,
      ts: "2026-06-23T01:00:00Z",
    },
    { kind: "session_closed", session_id: "s1", ts: "2026-06-23T02:00:00Z" },
  ],
});
ok(histHost.flatText().includes("bill-invoice"), "history: derived label renders");
ok(histHost.flatText().includes("classified"), "history: event kind renders");
ok(histHost.flatText().includes("7 words"), "history: word count renders");

/* ── Fixture 5 (must-fail half): a history event carrying a raw `prompt` field.
 * The render functions read ONLY whitelisted keys (kind/label/terms/word_count/ts),
 * so the phrase must NOT appear. (Defense-in-depth: the server already whitelists;
 * this proves the client also never surfaces an unexpected field.) */
loaded.renderStreamsHistory({
  active: "billing-work",
  active_history: [
    {
      kind: "classified",
      label: "ok",
      prompt: PHRASE,
      content: PHRASE,
      terms: ["ok"],
      word_count: 3,
    },
  ],
});
ok(!histHost.flatText().includes(PHRASE), "no-egress: a raw prompt/content field is NOT rendered");

/* ── Server-reader whitelist + parity (the load-bearing no-egress proof) ── */
const rootSrv = readFileSync("scripts/serve-dashboards.py", "utf8");
const plugSrv = readFileSync("plugins/ravenclaude-core/scripts/serve-dashboards.py", "utf8");
ok(
  rootSrv.includes("def _read_streams(project_root)"),
  "parity: root server defines _read_streams",
);
ok(
  plugSrv.includes("def _read_streams(project_root)"),
  "parity: plugin server defines _read_streams",
);
ok(
  rootSrv.includes('self.path.startswith("/__streams")'),
  "parity: root server registers /__streams",
);
ok(
  plugSrv.includes('self.path.startswith("/__streams")'),
  "parity: plugin server registers /__streams",
);
/* the reader builds active_history from a fixed whitelist, NOT a blind copy */
ok(
  rootSrv.includes("_allowed_event_keys") &&
    rootSrv.includes("clean = {k: ev[k] for k in _allowed_event_keys"),
  "no-egress: _read_streams whitelists event keys (no blind copy of ev)",
);
/* the whitelist must NOT contain a raw-content key */
const wlMatch = rootSrv.match(/_allowed_event_keys = \(([^)]*)\)/);
const wl = wlMatch ? wlMatch[1] : "";
ok(
  wl && !/["'](prompt|text|content|command|raw|body)["']/.test(wl),
  "no-egress: the event whitelist contains no raw-content key",
);

/* ── must-fail teeth: a stripped whitelist (blind copy) WOULD leak — assert the
 * fixture we built above proves the client guard, and the server-side string check
 * proves the whitelist exists. A vacuous gate (no whitelist) is caught by the
 * `_allowed_event_keys` assertion above. */

console.log(failures === 0 ? "\nGate 113 PASS" : `\nGate 113 FAIL (${failures})`);
if (!existsSync(htmlPath)) {
  console.error("dashboard.html missing");
  process.exit(1);
}
process.exit(failures === 0 ? 0 : 1);

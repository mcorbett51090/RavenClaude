#!/usr/bin/env node
/* check-mimir-render.mjs — behavioral test for the Mímir "Session" tab's render
 * logic (the Claude-Code-session-state surface added in the mimir-session-tab
 * v0.114.x line, per docs/plans/2026-06-03-mimir-session-tab/plan.md Phase 4).
 *
 * Extracts the REAL render functions (renderMimirSettings / renderMimirSession /
 * renderMimirActivity / renderMimirRecent / renderMimirUnreachable + the
 * mimirDash / mimirInProcessPill / mimirDl helpers) from the generated
 * dashboard.html and drives them against four fixtures from the plan:
 *
 *   1. POPULATED — every card hydrates from a realistic /__mimir payload.
 *   2. EMPTY-PROJECTS-DIR — server returns `exists: false` shape; cards still
 *      render honest empties (no thrown errors).
 *   3. UNREACHABLE-FIELDS — the in-process-only fields (`/effort`, `/status`,
 *      plan tier) render with an explainer pill, never a dash (per the
 *      mimir skill's honest-empty-state contract).
 *   4. WORKTREE-PATH — branch name carrying a worktree-style path renders
 *      verbatim (no normalization by the client; the server holds the
 *      verbatim-encoded-key invariant).
 *
 * Plus a both-copies-present check (both serve-dashboards.py copies define
 * `_read_mimir` — the duplication invariant in the SKILL).
 *
 * No real browser/jsdom — a minimal document stub records the DOM the
 * functions build, which is enough to assert structure + text + classes.
 * Mirrors check-norns-render.mjs / check-heimdall-render.mjs.
 *
 * Usage: node scripts/check-mimir-render.mjs [path/to/dashboard.html]
 */
import { readFileSync, existsSync } from "node:fs";

const htmlPath = process.argv[2] || "plugins/ravenclaude-core/dashboard.html";
const html = readFileSync(htmlPath, "utf8");

const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const app = scripts.reduce((a, b) => (b.length > a.length ? b : a), "");

/* Extract a brace-balanced top-level `function NAME(...) {...}` declaration
 * by header. (Same idiom as check-norns-render.mjs / check-heimdall-render.mjs.) */
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
 * Records children, className, textContent, attributes — enough to assert
 * the structure the render functions build. */
class El {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this._class = "";
    this._text = "";
    this.attrs = {};
    this.title = "";
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
  flatClasses() {
    return (this._class || "") + " " + this.children.map((c) => c.flatClasses()).join(" ");
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
const settings = mkHost("mimir-settings");
const session = mkHost("mimir-session");
const activity = mkHost("mimir-activity");
const recent = mkHost("mimir-recent");
const unreach = mkHost("mimir-unreach");

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

const pieces = [
  sagaEmptyPanelSrc,
  extract(app, "function mimirDash("),
  extract(app, "function mimirInProcessPill("),
  extract(app, "function mimirDl("),
  extract(app, "function renderMimirSettings("),
  extract(app, "function renderMimirSession("),
  extract(app, "function renderMimirActivity("),
  extract(app, "function renderMimirRecent("),
  extract(app, "function renderMimirUnreachable("),
];

const loaded = new Function(
  `${pieces.join("\n")}\n return { renderMimirSettings, renderMimirSession, renderMimirActivity, renderMimirRecent, renderMimirUnreachable };`,
)();

let failures = 0;
function ok(cond, msg) {
  if (cond) console.log("  ✓ " + msg);
  else {
    console.log("  ✗ " + msg);
    failures++;
  }
}

/* ── Fixture 1: POPULATED ─────────────────────────────────────────────── */
loaded.renderMimirSettings({
  theme: "dark",
  model: { configured: "claude-opus-4-7", last_used: "claude-sonnet-4-6" },
  permission_mode: "default",
});
ok(settings.flatText().includes("dark"), "populated: theme shows");
ok(settings.flatText().includes("claude-opus-4-7"), "populated: configured model shows");
ok(settings.flatText().includes("claude-sonnet-4-6"), "populated: last-used model shows");
ok(settings.flatText().includes("default"), "populated: permission mode shows");
/* RM "honest empty state for unreachable" — reasoning effort must render as a
 * pill, NEVER as a dash. */
ok(
  settings.find((e) => e._class && e._class.includes("mimir-pill--inproc")) !== null,
  "populated: reasoning effort uses in-process pill (not a dash)",
);

loaded.renderMimirSession({
  session_id: "abcd1234",
  pid: 4242,
  started_at: "2026-06-04T01:00:00Z",
  version: "1.0.123",
  found: true,
});
ok(session.flatText().includes("abcd1234"), "populated: session id shows");
ok(session.flatText().includes("4242"), "populated: pid shows");
ok(session.flatText().includes("1.0.123"), "populated: version shows");

loaded.renderMimirActivity({
  as_of: "2026-06-02",
  total_sessions: 100,
  total_messages: 5000,
  daily_activity_7d: [
    { date: "2026-05-28", messageCount: 10, sessionCount: 1 },
    { date: "2026-05-29", messageCount: 20, sessionCount: 2 },
  ],
});
/* RM4 — `as of YYYY-MM-DD` pill is MANDATORY when stats-cache exists. */
ok(
  activity.find((e) => e._class && e._class.includes("mimir-pill--asof")) !== null,
  "populated: 'as of' pill rendered (RM4)",
);
ok(activity.flatText().includes("2026-06-02"), "populated: as-of date shows");
ok(activity.flatText().includes("100"), "populated: total sessions shows");
ok(activity.flatText().includes("5000"), "populated: total messages shows");
ok(activity.flatText().includes("2026-05-28"), "populated: daily activity shows");

loaded.renderMimirRecent([
  {
    session_id: "11112222",
    last_active: "2026-06-04T01:00:00Z",
    event_count: 42,
    output_tokens: 1234,
    git_branch: "main",
  },
  {
    session_id: "33334444",
    last_active: "2026-06-03T01:00:00Z",
    event_count: 7,
    output_tokens: 200,
    git_branch: "feat/x",
  },
]);
ok(recent.flatText().includes("11112222"), "populated: recent session id shows");
ok(recent.flatText().includes("42 events"), "populated: event count shows");
ok(recent.flatText().includes("1234"), "populated: output tokens show");
ok(recent.flatText().includes("feat/x"), "populated: git branch shows");

loaded.renderMimirUnreachable(["effort_dial", "plan_tier", "status_live_cache"]);
ok(
  unreach.flatText().toLowerCase().includes("effort"),
  "populated: unreachable list explains /effort",
);
ok(unreach.flatText().toLowerCase().includes("plan tier"), "populated: explains plan tier");
ok(unreach.flatText().toLowerCase().includes("/status"), "populated: explains /status");

/* ── Fixture 2: EMPTY-PROJECTS-DIR ───────────────────────────────────────
 * `exists: false` shape from _read_mimir → cards still render without
 * thrown errors; session shows the not-found empty state. */
loaded.renderMimirSettings({
  theme: null,
  model: { configured: null, last_used: null },
  permission_mode: null,
});
ok(settings.flatText().includes("—"), "empty-projects: missing fields dash");
ok(
  settings.find((e) => e._class && e._class.includes("mimir-pill--inproc")) !== null,
  "empty-projects: reasoning-effort pill still rendered (in-process is not 'missing')",
);
loaded.renderMimirSession({ found: false });
ok(
  session.flatText().toLowerCase().includes("no live"),
  "empty-projects: session card shows 'no live' empty state",
);
loaded.renderMimirRecent([]);
ok(
  recent.flatText().toLowerCase().includes("no recent"),
  "empty-projects: recent card shows 'no recent' empty state",
);

/* ── Fixture 3: UNREACHABLE-FIELDS — already exercised in (1), but assert
 *    that an UNKNOWN unreachable code does NOT crash the renderer. */
loaded.renderMimirUnreachable(["effort_dial", "made_up_field"]);
ok(
  unreach.flatText().includes("made_up_field"),
  "unreachable-fields: unknown code rendered raw, no crash",
);

/* ── Fixture 4: WORKTREE-PATH — branch name carrying a worktree-style
 *    path renders verbatim (no client-side normalization; the server
 *    holds the verbatim-encoded-key invariant). */
loaded.renderMimirRecent([
  {
    session_id: "wtree001",
    last_active: "2026-06-04T01:00:00Z",
    event_count: 3,
    output_tokens: 100,
    git_branch: "wt/.claude/worktrees/foo",
  },
]);
ok(
  recent.flatText().includes("wt/.claude/worktrees/foo"),
  "worktree-path: branch path rendered verbatim",
);

/* ── Both-copies-present check — the _read_mimir helper is duplicated
 *    byte-identically across both serve-dashboards.py copies per the SKILL
 *    parity discipline (RM6). Gate 32 checks endpoint NAMES, this gate
 *    confirms the reader exists in both. */
const ROOT_SERVER = "scripts/serve-dashboards.py";
const PLUGIN_SERVER = "plugins/ravenclaude-core/scripts/serve-dashboards.py";
if (existsSync(ROOT_SERVER) && existsSync(PLUGIN_SERVER)) {
  const rootSrc = readFileSync(ROOT_SERVER, "utf8");
  const pluginSrc = readFileSync(PLUGIN_SERVER, "utf8");
  ok(
    rootSrc.includes("def _read_mimir("),
    "both-copies: root serve-dashboards.py defines _read_mimir",
  );
  ok(
    pluginSrc.includes("def _read_mimir("),
    "both-copies: bundled-plugin serve-dashboards.py defines _read_mimir",
  );
} else {
  ok(false, "both-copies: one or both serve-dashboards.py copies missing on disk");
}

console.log("");
if (failures === 0) {
  console.log("Mímir render: ALL ASSERTIONS PASS");
  process.exit(0);
}
console.log(`Mímir render: ${failures} assertion(s) FAILED`);
process.exit(1);

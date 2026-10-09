#!/usr/bin/env node
// Stub-DOM checks for the Spectate UI (plugins/ravenclaude-core/dashboard-assets/spectate/app.js).
// No browser, no network: app.js is import()ed under a stub document/localStorage and its
// exported view/state helpers are asserted. Exit 0 = pass, 1 = a check failed.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const assetDir = join(here, "..", "plugins", "ravenclaude-core", "dashboard-assets", "spectate");
const appPath = join(assetDir, "app.js");

const failures = [];
let checks = 0;
function check(name, ok, detail) {
  checks += 1;
  if (!ok) failures.push(detail ? `${name}: ${detail}` : name);
}

// ------------------------------------------------------------------ stub DOM
class StubText {
  constructor(data) {
    this.nodeType = 3;
    this.data = String(data);
    this.children = [];
  }
}

class StubElement {
  constructor(tag, ns) {
    this.nodeType = 1;
    this.tagName = tag;
    this.namespaceURI = ns || null;
    this.attrs = {};
    this.children = [];
    this.listeners = {};
    this.hidden = false;
    this.value = "";
    this.checked = false;
    this.style = {
      props: {},
      setProperty(k, v) {
        this.props[k] = v;
      },
    };
  }
  setAttribute(k, v) {
    this.attrs[k] = String(v);
  }
  getAttribute(k) {
    return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null;
  }
  appendChild(child) {
    this.children.push(child);
    return child;
  }
  removeChild(child) {
    this.children.splice(this.children.indexOf(child), 1);
    return child;
  }
  get firstChild() {
    return this.children[0] || null;
  }
  get textContent() {
    return this.children.map(textOf).join("");
  }
  set textContent(v) {
    this.children = [new StubText(v)];
  }
  addEventListener(type, fn) {
    (this.listeners[type] ||= []).push(fn);
  }
  querySelector() {
    return null;
  }
  querySelectorAll() {
    return [];
  }
  focus() {}
  set innerHTML(_v) {
    throw new Error("innerHTML is forbidden");
  }
  set outerHTML(_v) {
    throw new Error("outerHTML is forbidden");
  }
  insertAdjacentHTML() {
    throw new Error("insertAdjacentHTML is forbidden");
  }
}

function textOf(node) {
  return node.nodeType === 3 ? node.data : node.children.map(textOf).join("");
}

function walk(node, fn) {
  fn(node);
  for (const child of node.children || []) walk(child, fn);
}

function findAll(root, pred) {
  const out = [];
  walk(root, (n) => {
    if (n.nodeType === 1 && pred(n)) out.push(n);
  });
  return out;
}

function makeDoc({ withApp = false } = {}) {
  const byId = new Map();
  const docListeners = {};
  const doc = {
    visibilityState: "visible",
    readyState: "complete",
    activeElement: null,
    documentElement: new StubElement("html"),
    createElement: (tag) => new StubElement(tag),
    createElementNS: (ns, tag) => new StubElement(tag, ns),
    createTextNode: (t) => new StubText(t),
    getElementById(id) {
      if (!withApp) return null;
      if (!byId.has(id)) byId.set(id, new StubElement("div"));
      return byId.get(id);
    },
    addEventListener(type, fn) {
      (docListeners[type] ||= []).push(fn);
    },
    fire(type) {
      for (const fn of docListeners[type] || []) fn({ type });
    },
    write() {
      throw new Error("document.write is forbidden");
    },
    byId,
  };
  return doc;
}

function makeStorage(initial = {}) {
  const store = new Map(Object.entries(initial));
  return {
    store,
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => {
      store.set(k, String(v));
    },
  };
}

// ------------------------------------------------------------------ import under stub globals
const storage = makeStorage();
globalThis.document = makeDoc();
globalThis.localStorage = storage;

let app;
try {
  app = await import(pathToFileURL(appPath).href);
  check("import app.js under stub document does not throw", true);
} catch (err) {
  console.error(`FAIL: import app.js: ${err && err.stack ? err.stack : err}`);
  process.exit(1);
}
const doc = makeDoc();

// ------------------------------------------------------------------ 1. eleven statuses: shape + label
const EXPECTED = [
  "available",
  "unavailable-harness",
  "denied-org",
  "denied-plugin",
  "denied-user",
  "denied-harness",
  "running",
  "succeeded",
  "failed",
  "waiting-approval",
  "idle",
];
const EXPECTED_SHAPE = {
  available: "circle-outline",
  "unavailable-harness": "circle-dashed",
  "denied-org": "octagon",
  "denied-plugin": "diamond",
  "denied-user": "square-x",
  "denied-harness": "hexagon",
  running: "circle-filled-pulse",
  succeeded: "circle-check",
  failed: "circle-cross",
  "waiting-approval": "rounded-square-pause",
  idle: "circle-outline-muted",
};
check("STATUSES has 11 entries", app.STATUSES.length === 11, String(app.STATUSES.length));
check(
  "STATUSES ids match the reducer set",
  JSON.stringify(app.STATUSES.map((s) => s.id).sort()) === JSON.stringify([...EXPECTED].sort()),
);
check("shapes are all distinct", new Set(app.STATUSES.map((s) => s.shape)).size === 11);

const sprite = readFileSync(join(assetDir, "status-icons.svg"), "utf8");
for (const id of EXPECTED) {
  const view = app.statusView(id);
  check(`status ${id}: has view`, !!view);
  if (!view) continue;
  check(`status ${id}: shape ${EXPECTED_SHAPE[id]}`, view.shape === EXPECTED_SHAPE[id], view.shape);
  check(`status ${id}: exact label`, view.label === id);

  const chip = app.statusChip(doc, id);
  const label = findAll(chip, (n) => (n.getAttribute("class") || "").includes("status-label"));
  check(
    `status ${id}: chip has label text`,
    label.length === 1 && textOf(label[0]) === id,
    label.length ? textOf(label[0]) : "none",
  );
  check(`status ${id}: chip carries data-shape`, chip.getAttribute("data-shape") === view.shape);
  const uses = findAll(chip, (n) => n.tagName === "use");
  check(
    `status ${id}: chip has svg <use> to sprite`,
    uses.length === 1 && uses[0].getAttribute("href") === `/spectate/status-icons.svg#s-${id}`,
  );
  check(`status ${id}: sprite defines symbol`, sprite.includes(`<symbol id="s-${id}"`));
}
check(
  "denied-harness is a 6-point hexagon in the sprite",
  /id="s-denied-harness"[\s\S]*?points="([^"]+)"/.test(sprite) &&
    sprite
      .match(/id="s-denied-harness"[\s\S]*?points="([^"]+)"/)[1]
      .trim()
      .split(/\s+/).length === 6,
);
check(
  "denied-org is an 8-point octagon in the sprite",
  sprite
    .match(/id="s-denied-org"[\s\S]*?points="([^"]+)"/)[1]
    .trim()
    .split(/\s+/).length === 8,
);
for (const c of ["connecting", "ok", "stale", "disconnected"])
  check(`sprite defines chrome icon c-${c}`, sprite.includes(`<symbol id="c-${c}"`));

// graph render: one node per status, shape + label in the DOM
const allStatusNodes = app.STATUSES.map((s, i) => ({
  node_id: `tool-${i}`,
  parent_id: "step:main:0:execute-tools",
  agent_id: "main",
  turn: 0,
  step: "execute-tools",
  kind: "tool.post",
  status: s.id,
  tool: { name: `tool${i}`, family: "shell" },
}));
const spineNodes = app.seedNodes().map((n) => ({ ...n, seeded: undefined }));
const model = app.buildGraphModel([...spineNodes, ...allStatusNodes], {
  hidden: [],
  turnsShown: 3,
});
const graphMount = new StubElement("div");
app.renderGraph(doc, graphMount, model, { selectedId: null, seen: new Set(), onSelect: () => {} });
const renderedStatuses = new Set(
  findAll(graphMount, (n) => n.getAttribute("data-node-id") && n.getAttribute("data-status")).map(
    (n) => n.getAttribute("data-status"),
  ),
);
for (const id of EXPECTED)
  check(`graph renders a node with status ${id}`, renderedStatuses.has(id));
for (const btn of findAll(
  graphMount,
  (n) => n.tagName === "button" && n.getAttribute("data-node-id"),
)) {
  const status = btn.getAttribute("data-status");
  check(
    `graph node ${btn.getAttribute("data-node-id")}: label text + shape icon`,
    textOf(btn).includes(status) && findAll(btn, (n) => n.tagName === "use").length === 1,
  );
}
check("graph sets positional --col-main track var", graphMount.style.props["--col-main"] === "1fr");
check(
  "column visibility hides an agent column",
  app.buildGraphModel(
    [
      { node_id: "a", agent_id: "sub", turn: 0 },
      { node_id: "b", agent_id: "main", turn: 0 },
    ],
    { hidden: ["sub"] },
  ).agents.length === 1,
);

// ------------------------------------------------------------------ 2. disconnected keeps nodes
const query = app.parseQuery("?session=demo-claude-code");
check(
  "parseQuery pins a valid session",
  query.session === "demo-claude-code" && query.follow === false,
);
check(
  "parseQuery rejects traversal ids",
  app.parseQuery("?session=../etc").session === null &&
    app.parseQuery("?session=../etc").invalidSession === true,
);
check("parseQuery defaults to follow=latest", app.parseQuery("").follow === true);

const body = {
  session_id: "demo-claude-code",
  harness: "claude-code",
  synthetic: false,
  server_now: "2026-10-09T12:00:30.000Z",
  last_event_ts: "2026-10-09T12:00:20.000Z",
  session_ended: false,
  source_hint: "live",
  etag: "e1",
  nodes: allStatusNodes.slice(0, 3),
};
let state = app.initialState(app.loadPrefs(storage), query);
state = app.applyNodesResult(
  state,
  app.classifyNodesResponse({ status: 200, body, etag: "e1" }),
  1000,
);
check("ok poll stores nodes", state.nodes && state.nodes.nodes.length === 3);
check("ok poll => connection ok", app.describeConnection(state, 1500).value === "ok");
for (let i = 1; i <= 4; i += 1)
  state = app.applyNodesResult(
    state,
    app.classifyNodesResponse({ status: 503, body: null }),
    1000 + i * 2000,
  );
check("failed polls keep nodes", state.nodes && state.nodes.nodes.length === 3);
check("failed polls keep etag", state.etag === "e1");
const conn = app.describeConnection(state, 9000);
check("failed polls => disconnected", conn.value === "disconnected", conn.value);
check("after N failures relaunch command is offered", conn.showRelaunch === true);
check("failure never maps to an idle status", !state.nodes.nodes.some((n) => n.status === "idle"));
const retained = new StubElement("div");
app.renderGraph(
  doc,
  retained,
  app.buildGraphModel(state.nodes.nodes, { hidden: [], turnsShown: 3 }),
  { selectedId: null, seen: new Set() },
);
check(
  "graph still renders retained nodes while disconnected",
  findAll(retained, (n) => n.getAttribute("data-node-id")).length === 3,
);
const overlay = new StubElement("div");
app.renderOverlay(doc, overlay, conn, {});
check(
  "disconnected overlay shows exact rc spectate command",
  findAll(overlay, (n) => n.tagName === "code").some((n) => textOf(n) === "rc spectate"),
);
state = app.applyNodesResult(state, { kind: "not_modified", serverNow: null }, 12000);
check(
  "304 recovers to connected without dropping nodes",
  app.describeConnection(state, 12500).value === "ok" && state.nodes.nodes.length === 3,
);
check(
  "stale after >3x interval while visible",
  app.describeConnection(state, 12000 + 3 * app.POLL_NODES_MS + 1).value === "stale",
);
const hiddenState = app.setVisibility(state, false, 20000);
check(
  "stale is not reported while hidden",
  app.describeConnection(hiddenState, 99999).value === "ok",
);
check(
  "connecting before the first success",
  app.describeConnection(app.initialState(app.loadPrefs(storage), query), 0).value === "connecting",
);

// ------------------------------------------------------------------ 3. empty / no-stream states
let ns = app.initialState(app.loadPrefs(storage), query);
ns = app.applyNodesResult(
  ns,
  app.classifyNodesResponse({
    status: 404,
    body: { error: "no_spectate_stream", has_hook_events: true },
  }),
  10,
);
check(
  "no_spectate_stream classified as its own state",
  ns.emptyKind === "no_spectate_stream" && ns.noStream.hasHookEvents === true,
);
check(
  "no_spectate_stream is not session_not_found",
  app.emptyStateKind(ns) === "no_spectate_stream",
);
const nsMount = new StubElement("div");
app.renderEmpty(doc, nsMount, "no_spectate_stream", ns, {});
check(
  "no-stream copy names the v0.2 emitter",
  textOf(nsMount).includes("no spectate emitter yet") && textOf(nsMount).includes("v0.2"),
);
check("no-stream copy never says not found", !/not found/.test(textOf(nsMount)));
check("no-stream never offers the demo command", !textOf(nsMount).includes("--demo"));
const seeded = app.seedNodes();
check(
  "seeded spine covers the six loop steps, all idle",
  seeded.length === 6 && seeded.every((n) => n.status === "idle"),
);

let nf = app.applyNodesResult(
  app.initialState(app.loadPrefs(storage), query),
  app.classifyNodesResponse({ status: 404, body: { error: "session_not_found" } }),
  10,
);
check("session_not_found classified", app.emptyStateKind(nf) === "session_not_found");
const nfMount = new StubElement("div");
app.renderEmpty(doc, nfMount, "session_not_found", nf, {});
check("session_not_found copy says not found", /not found/.test(textOf(nfMount)));
check(
  "session_not_found state is not a network failure",
  app.describeConnection(nf, 50).value === "ok",
);

const none = app.applySessionsResult(
  app.initialState(app.loadPrefs(storage), app.parseQuery("")),
  { kind: "ok", sessions: [] },
  5,
);
check("no sessions => no_session empty state", app.emptyStateKind(none) === "no_session");
const noneMount = new StubElement("div");
app.renderEmpty(doc, noneMount, "no_session", none, {});
check(
  "Load demo is the copyable rc spectate --demo command",
  app.DEMO_COMMAND === "rc spectate --demo" &&
    findAll(noneMount, (n) => n.getAttribute("data-copy") === "rc spectate --demo").length === 1 &&
    textOf(noneMount).includes("rc spectate --demo"),
);
check(
  "Load demo is a button, not a link or form",
  findAll(noneMount, (n) => ["a", "form"].includes(n.tagName)).length === 0,
);

// follow=latest semantics
const sessions = [
  { session_id: "demo-cursor", harness: "cursor", synthetic: true, has_stream: true, mtime: 300 },
  { session_id: "real-b", harness: "codex-cli", synthetic: false, has_stream: false, mtime: 200 },
  { session_id: "real-a", harness: "claude-code", synthetic: false, has_stream: true, mtime: 100 },
];
check(
  "follow ranks non-synthetic with stream first",
  app.pickFollowTarget(sessions, null).session_id === "real-a",
);
check(
  "follow ranks synthetic last",
  app.rankSessions(sessions).at(-1).session_id === "demo-cursor",
);
check(
  "follow honours harness filter",
  app.pickFollowTarget(sessions, "cursor").session_id === "demo-cursor",
);
let fs = app.applySessionsResult(
  app.initialState(app.loadPrefs(storage), app.parseQuery("")),
  { kind: "ok", sessions },
  1,
);
check("follow=latest picks the ranked session", fs.target === "real-a");
fs = app.selectNode(fs, "step:main:0:assemble");
fs = app.applySessionsResult(
  fs,
  {
    kind: "ok",
    sessions: [
      { ...sessions[0], mtime: 999, synthetic: false, has_stream: true },
      ...sessions.slice(1),
    ],
  },
  2,
);
check("follow does not re-target while a node is selected", fs.target === "real-a");
const pinned = app.pinSession(fs, "real-b");
check(
  "pinning sets target and stops following",
  pinned.target === "real-b" && pinned.followLatest === false && pinned.selectedNodeId === null,
);
check("pin refuses unsafe ids", app.pinSession(fs, "../x") === fs);

// ------------------------------------------------------------------ 4. corrupt storage defaults
const defaults = app.loadPrefs(makeStorage());
check(
  "empty storage => documented defaults",
  defaults.theme === "dark" &&
    defaults.density === "comfortable" &&
    defaults.layout === "default" &&
    defaults.legend === "footer" &&
    defaults.filter === "" &&
    defaults.columns.length === 0,
);
const corrupt = app.loadPrefs(
  makeStorage({
    "rc.spectate.v1.theme": "neon",
    "rc.spectate.v1.density": '{"x":1}',
    "rc.spectate.v1.layout": "\u0000",
    "rc.spectate.v1.legend": "sidebar",
    "rc.spectate.v1.columns": "{not json",
    "rc.spectate.v1.filter": "a\u0007b",
  }),
);
check(
  "corrupt enum values fall back",
  corrupt.theme === "dark" &&
    corrupt.density === "comfortable" &&
    corrupt.layout === "default" &&
    corrupt.legend === "footer",
);
check("corrupt columns JSON => []", Array.isArray(corrupt.columns) && corrupt.columns.length === 0);
check("filter strips control characters", corrupt.filter === "ab");
check(
  "columns of the wrong type => []",
  app.loadPrefs(makeStorage({ "rc.spectate.v1.columns": '"main"' })).columns.length === 0,
);
check(
  "columns reject css-unsafe agent ids",
  JSON.stringify(
    app.loadPrefs(makeStorage({ "rc.spectate.v1.columns": '["sub","a b","x);y"]' })).columns,
  ) === '["sub"]',
);
const throwing = {
  getItem() {
    throw new Error("denied");
  },
  setItem() {
    throw new Error("denied");
  },
};
check(
  "throwing storage does not throw",
  app.loadPrefs(throwing).theme === "dark" && app.savePref(throwing, "theme", "light") === false,
);
check(
  "null storage does not throw",
  app.loadPrefs(null).theme === "dark" && app.savePref(null, "theme", "light") === false,
);
const writable = makeStorage();
check(
  "savePref persists under rc.spectate.v1.*",
  app.savePref(writable, "theme", "light") &&
    writable.store.get("rc.spectate.v1.theme") === "light",
);
check(
  "savePref rejects invalid enum values",
  app.savePref(writable, "theme", "neon") === false &&
    writable.store.get("rc.spectate.v1.theme") === "light",
);
check("prefs round-trip", app.loadPrefs(writable).theme === "light");
check("storage keys use the rc.spectate.v1. namespace", app.STORAGE_PREFIX === "rc.spectate.v1.");

// ------------------------------------------------------------------ 5. chrome badges, capability unknown, unterminated
const demoState = { ...state, nodes: { ...body, synthetic: true, source_hint: "demo" } };
check("source badge: demo", app.describeSource(demoState, 0).value === "demo");
const liveState = {
  ...state,
  nodes: body,
  serverNowMs: Date.parse(body.server_now),
  serverNowAt: 100,
};
const live = app.describeSource(liveState, 100);
check(
  "source badge: live within 60s",
  live.value === "live" && /last event \d+s ago/.test(live.detail),
  JSON.stringify(live),
);
check(
  "source badge: recorded after 60s",
  app.describeSource(liveState, 100 + 61000).value === "recorded",
);
check(
  "source badge: recorded when session ended",
  app.describeSource({ ...liveState, nodes: { ...body, session_ended: true } }, 100).value ===
    "recorded",
);
check(
  "source badge: none without nodes",
  app.describeSource({ ...liveState, nodes: null }, 100) === null,
);
const liveBadge = app.sourceBadge(doc, live);
check(
  "live badge has the 6px running dot",
  findAll(liveBadge, (n) => (n.getAttribute("class") || "") === "live-dot").length === 1,
);
check(
  "demo badge has no live dot",
  findAll(
    app.sourceBadge(doc, { value: "demo", label: "demo", detail: null }),
    (n) => (n.getAttribute("class") || "") === "live-dot",
  ).length === 0,
);
for (const v of ["connecting", "ok", "stale", "disconnected"]) {
  const ind = app.connectionIndicator(doc, {
    value: v,
    label: app.CONNECTION_LABELS[v],
    icon: `c-${v}`,
  });
  check(
    `connection ${v}: icon + text`,
    findAll(ind, (n) => n.tagName === "use").length === 1 &&
      textOf(ind) === app.CONNECTION_LABELS[v],
  );
}
check(
  "observe-only subtitle is in index.html",
  /observe-only[\s\S]*steering unavailable until v0\.3/.test(
    readFileSync(join(assetDir, "index.html"), "utf8"),
  ),
);

const unknownNode = {
  node_id: "step:main:0:call-model",
  agent_id: "main",
  turn: 0,
  step: "call-model",
  kind: "step.seed",
  status: "idle",
  capability_state: "unknown",
};
check("capability unknown label", app.nodeStatusText(unknownNode) === "idle · capability unknown");
const unkBtn = app.nodeButton(doc, unknownNode, { selectedId: null, tabStopId: null });
check(
  "capability unknown renders the ? glyph",
  findAll(unkBtn, (n) => (n.getAttribute("class") || "") === "cap-glyph" && textOf(n) === "?")
    .length === 1,
);
check(
  "capability unknown stays on the idle shape",
  findAll(unkBtn, (n) => n.getAttribute("data-status") === "idle" && n.getAttribute("data-shape"))
    .length === 1,
);
check(
  "capability unknown is never unavailable-harness",
  !textOf(unkBtn).includes("unavailable-harness"),
);
const unterm = {
  node_id: "tool-x",
  agent_id: "main",
  turn: 0,
  status: "running",
  unterminated: true,
};
check(
  "unterminated label suffix",
  app.nodeStatusText(unterm) === "running · no completion observed",
);
const untBtn = app.nodeButton(doc, unterm, { selectedId: null, tabStopId: null });
check(
  "unterminated node keeps its status shape and is marked dashed",
  untBtn.getAttribute("data-unterminated") === "true" &&
    untBtn.getAttribute("data-status") === "running",
);
check(
  "unrecognised status is not painted as a real status",
  app.nodeStatusText({ status: "bogus" }).includes("unrecognized"),
);

// inspector payload: scrubbed fields only
const rows = app.payloadRows({
  ts: "t",
  tool: { name: "Bash", family: "shell", target: "ls", args: "SECRET", output: "SECRET" },
  metrics: { duration_ms: 5, out_bytes: 9, evil: 1 },
  deny: { by: "plugin", source: "hook", rule: "r1", message: "SECRET" },
  prompt: "SECRET",
  args: { a: 1 },
});
check(
  "payload rows are the schema allow-list only",
  rows.map((r) => r[0]).join(",") ===
    "tool.name,tool.family,tool.target,metrics.duration_ms,metrics.out_bytes,deny.by,deny.source,deny.rule,ts",
);
check("payload never carries raw fields", !JSON.stringify(rows).includes("SECRET"));
const emptyBody = new StubElement("div");
app.renderInspectorBody(doc, emptyBody, { node_id: "n", status: "idle" }, "payload");
check("empty payload says no scrubbed fields", textOf(emptyBody).includes("no scrubbed fields"));

// keyboard model
const nav = app.navLayout(app.buildGraphModel([...spineNodes, ...allStatusNodes.slice(0, 2)], {}));
check(
  "nav layout lists spine then tool children",
  nav[0][3] === "step:main:0:execute-tools" && nav[0][4] === "tool-0",
);
check(
  "ArrowDown moves down the column",
  app.navTarget(nav, "step:main:0:assemble", "ArrowDown") === "step:main:0:call-model",
);
check(
  "ArrowUp clamps at the top",
  app.navTarget(nav, "step:main:0:assemble", "ArrowUp") === "step:main:0:assemble",
);

// ------------------------------------------------------------------ 6. hidden tab: zero polls
{
  const appDoc = makeDoc({ withApp: true });
  let nowMs = 0;
  let seq = 0;
  const queue = [];
  const requests = [];
  let failing = false;
  const win = {
    location: { search: "?follow=latest" },
    localStorage: makeStorage(),
    navigator: {},
    history: { replaceState() {} },
    performance: { now: () => nowMs },
    matchMedia: () => ({ matches: true }),
    setTimeout(fn, ms) {
      seq += 1;
      queue.push({ id: seq, at: nowMs + ms, fn });
      return seq;
    },
    clearTimeout(id) {
      const i = queue.findIndex((t) => t.id === id);
      if (i !== -1) queue.splice(i, 1);
    },
    setInterval(fn, ms) {
      seq += 1;
      const id = seq;
      const tick = () => {
        queue.push({
          id,
          at: nowMs + ms,
          fn: () => {
            fn();
            tick();
          },
        });
      };
      tick();
      return id;
    },
    clearInterval(id) {
      for (let i = queue.length - 1; i >= 0; i -= 1) if (queue[i].id === id) queue.splice(i, 1);
    },
    fetch(url, init) {
      requests.push({ url, headers: (init && init.headers) || {}, at: nowMs });
      if (failing) return Promise.reject(new TypeError("fetch failed"));
      const json = url.startsWith("/__spectate/sessions")
        ? {
            sessions: [
              {
                session_id: "real-a",
                harness: "claude-code",
                synthetic: false,
                has_stream: true,
                mtime: 5,
                latest_status: "running",
              },
            ],
            next_cursor: null,
          }
        : { ...body, session_id: "real-a" };
      return Promise.resolve({
        status: 200,
        headers: { get: (h) => (h === "ETag" ? "e1" : null) },
        json: () => Promise.resolve(json),
      });
    },
  };
  const settle = () => new Promise((r) => setImmediate(r));
  async function advance(ms) {
    const end = nowMs + ms;
    for (;;) {
      queue.sort((a, b) => a.at - b.at);
      if (!queue.length || queue[0].at > end) break;
      const next = queue.shift();
      nowMs = next.at;
      next.fn();
      await settle();
    }
    nowMs = end;
    await settle();
  }

  const running = app.startApp(appDoc, win);
  await settle();
  check("startApp boots against the stub DOM", !!running);
  const nodesReqs = () => requests.filter((r) => r.url.startsWith("/__spectate/nodes"));
  const sessionsReqs = () => requests.filter((r) => r.url.startsWith("/__spectate/sessions"));
  check("visible: sessions polled on start", sessionsReqs().length === 1);
  check(
    "follow=latest targets the ranked session and polls nodes",
    nodesReqs().length >= 1 && nodesReqs()[0].url === "/__spectate/nodes?session=real-a",
    nodesReqs()[0] && nodesReqs()[0].url,
  );
  check(
    "every poll is a GET with no body (no write route)",
    requests.every((r) => !("body" in r.headers)),
  );

  await advance(4100);
  const withEtag = nodesReqs().filter((r) => r.headers["If-None-Match"] === "e1");
  check(
    "visible: nodes re-polled with If-None-Match",
    nodesReqs().length >= 3 && withEtag.length >= 2,
    String(nodesReqs().length),
  );
  const nodesPerWindow = nodesReqs().length;
  check("nodes poll cadence is ~2s", nodesPerWindow <= 4, String(nodesPerWindow));

  appDoc.visibilityState = "hidden";
  appDoc.fire("visibilitychange");
  await settle();
  const before = requests.length;
  await advance(10000);
  check(
    "hidden tab: zero requests over 10s",
    requests.length === before,
    `${requests.length - before} requests while hidden`,
  );
  check("hidden tab: no timers left running", queue.length === 0, String(queue.length));

  appDoc.visibilityState = "visible";
  appDoc.fire("visibilitychange");
  await advance(100);
  check("visible again: polling resumes immediately", requests.length > before);

  failing = true;
  await advance(3 * app.POLL_NODES_MS + 200);
  const st = running.getState();
  check(
    "fetch failure: connection disconnected",
    app.describeConnection(st, nowMs).value === "disconnected",
  );
  check("fetch failure: nodes retained in state", st.nodes && st.nodes.nodes.length === 3);
  const graph = appDoc.byId.get("graph");
  check(
    "fetch failure: graph still renders nodes",
    findAll(graph, (n) => n.getAttribute("data-node-id")).length >= 3,
  );
  check(
    "fetch failure: overlay visible with relaunch command",
    appDoc.byId.get("graph-overlay").hidden === false &&
      textOf(appDoc.byId.get("graph-overlay")).includes("rc spectate"),
  );
  check(
    "fetch failure: no idle-success state",
    findAll(graph, (n) => n.getAttribute("data-status") === "idle").length === 0,
  );
  failing = false;
  await advance(2 * app.POLL_SESSIONS_MS + 200);
  check("recovery: overlay hidden again", appDoc.byId.get("graph-overlay").hidden === true);
}

// ------------------------------------------------------------------ 7. no innerHTML helpers, CSP-safe markup
const src = readFileSync(appPath, "utf8");
const code = src.replace(/\/\*[\s\S]*?\*\//g, "").replace(/^\s*\/\/.*$/gm, "");
for (const bad of [
  "innerHTML",
  "outerHTML",
  "insertAdjacentHTML",
  "document.write",
  "createContextualFragment",
  "DOMParser",
  "eval(",
  "new Function",
]) {
  check(`app.js has no ${bad}`, !code.includes(bad));
}
check(
  "app.js has no inline hex colours",
  !/#[0-9a-fA-F]{3,8}\b(?![-\w])/.test(code.replace(/'#[a-z-]+'|`#[^`]*`/g, "")),
);
check(
  "app.js never issues a write request",
  !/method\s*:\s*['"](POST|PUT|PATCH|DELETE)/i.test(code),
);
check(
  "app.js guards DOM bootstrap on typeof document",
  /typeof document !== ["']undefined["']/.test(code),
);
check(
  "app.js polls nodes every 2s and sessions every 5s",
  app.POLL_NODES_MS === 2000 && app.POLL_SESSIONS_MS === 5000,
);
check(
  "app.js exports are pure helpers (module has named exports)",
  ["statusChip", "loadPrefs", "applyNodesResult", "renderGraph"].every(
    (k) => typeof app[k] === "function",
  ),
);

const html = readFileSync(join(assetDir, "index.html"), "utf8");
check(
  "index.html loads the module script by absolute path",
  /<script type="module" src="\/spectate\/app\.js"><\/script>/.test(html),
);
check("index.html loads css by absolute path", html.includes('href="/spectate/spectate.css"'));
check(
  "index.html has no relative asset refs",
  !/(?:src|href)="(?!\/|#|data:)[^"]+"/.test(html.replace(/<noscript>[\s\S]*?<\/noscript>/g, "")),
);
check(
  "index.html has no inline script or style (CSP)",
  !/<script(?![^>]*\ssrc=)/.test(html) &&
    !/<style[\s>]/.test(html) &&
    !/\sstyle="/.test(html) &&
    !/\son[a-z]+="/.test(html),
);
check("index.html has no hex colours", !/#[0-9a-fA-F]{6}\b/.test(html));
const css = readFileSync(join(assetDir, "spectate.css"), "utf8");
for (const id of EXPECTED)
  check(
    `css defines status tokens for ${id}`,
    css.includes(`--status-${id}-fg:`) && css.includes(`--status-${id}-shape:`),
  );
check(
  "css has dark default and light theme blocks",
  css.includes('[data-theme="dark"]') && css.includes('[data-theme="light"]'),
);
check("css honours prefers-reduced-motion", css.includes("prefers-reduced-motion: reduce"));
check("css uses no purple accent", !/#(?:8b5cf6|a855f7|7c3aed|9333ea)/i.test(css));

if (failures.length) {
  for (const f of failures) console.error(`FAIL: ${f}`);
  console.error(`check-spectate-render: ${failures.length} of ${checks} checks failed`);
  process.exit(1);
}
console.log(`check-spectate-render: OK (${checks} checks)`);

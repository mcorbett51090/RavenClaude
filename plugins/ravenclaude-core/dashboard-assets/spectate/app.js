// Harness Spectate UI (v0.3). Polls GET /__spectate/*; prefers SSE /stream; opt-in steer POST.
// Everything above the bootstrap guard is pure or takes an injected `doc`, so
// scripts/check-spectate-render.mjs can import this module under a stub DOM.
// DOM text is set via textContent / text nodes only.

export const STORAGE_PREFIX = "rc.spectate.v1.";
export const SESSION_ID_RE = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
export const NODE_ID_RE = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$/;

export const POLL_NODES_MS = 2000;
export const POLL_SESSIONS_MS = 5000;
export const STALE_FACTOR = 3;
export const LIVE_WINDOW_MS = 60000;
export const RELAUNCH_AFTER_FAILURES = 3;
export const DEFAULT_TURNS_SHOWN = 3;

export const DEMO_COMMAND = "rc spectate --demo";
export const RELAUNCH_COMMAND = "rc spectate";
export const ICON_SPRITE = "/spectate/status-icons.svg";

const SVG_NS = "http://www.w3.org/2000/svg";
const MAX_SESSIONS_LIMIT = 200;

export const HARNESSES = Object.freeze([
  "claude-code",
  "codex-cli",
  "copilot-cli",
  "copilot-vscode",
  "cursor",
  "gemini-cli",
  "grok-build",
  "grok-bot",
  "unknown",
]);

export const STATUSES = Object.freeze([
  {
    id: "available",
    label: "available",
    shape: "circle-outline",
    note: "capability exposed; not started",
  },
  {
    id: "unavailable-harness",
    label: "unavailable-harness",
    shape: "circle-dashed",
    note: "harness does not expose this step",
  },
  {
    id: "denied-org",
    label: "denied-org",
    shape: "octagon",
    note: "blocked by organization policy",
  },
  {
    id: "denied-plugin",
    label: "denied-plugin",
    shape: "diamond",
    note: "blocked by a plugin or hook",
  },
  { id: "denied-user", label: "denied-user", shape: "square-x", note: "denied by user permission" },
  {
    id: "denied-harness",
    label: "denied-harness",
    shape: "hexagon",
    note: "denied by harness-native policy",
  },
  { id: "running", label: "running", shape: "circle-filled-pulse", note: "in flight" },
  { id: "succeeded", label: "succeeded", shape: "circle-check", note: "completed successfully" },
  { id: "failed", label: "failed", shape: "circle-cross", note: "errored" },
  {
    id: "waiting-approval",
    label: "waiting-approval",
    shape: "rounded-square-pause",
    note: "awaiting approval",
  },
  { id: "idle", label: "idle", shape: "circle-outline-muted", note: "not active in this session" },
]);

export const STATUS_BY_ID = Object.freeze(Object.fromEntries(STATUSES.map((s) => [s.id, s])));

export const LOOP_STEPS = Object.freeze([
  { id: "assemble", label: "Assemble" },
  { id: "call-model", label: "Model" },
  { id: "classify", label: "Classify" },
  { id: "execute-tools", label: "Tools" },
  { id: "package", label: "Package" },
  { id: "update-context", label: "Context" },
]);

const STEP_IDS = new Set(LOOP_STEPS.map((s) => s.id));

export const PREF_DEFS = Object.freeze({
  theme: { values: ["dark", "light"], fallback: "dark" },
  density: { values: ["compact", "comfortable", "spacious"], fallback: "comfortable" },
  layout: {
    values: ["default", "graph-focus", "inspector-focus", "sessions-focus"],
    fallback: "default",
  },
  legend: { values: ["footer", "inspector"], fallback: "footer" },
});

export const DEFAULT_PREFS = Object.freeze({
  theme: PREF_DEFS.theme.fallback,
  density: PREF_DEFS.density.fallback,
  layout: PREF_DEFS.layout.fallback,
  legend: PREF_DEFS.legend.fallback,
  filter: "",
  columns: Object.freeze([]),
});

// ---------------------------------------------------------------- storage

function stripControls(text) {
  return String(text).replace(/[\u0000-\u001f\u007f]/g, "");
}

function readItem(storage, key) {
  try {
    if (!storage || typeof storage.getItem !== "function") return null;
    const value = storage.getItem(STORAGE_PREFIX + key);
    return typeof value === "string" ? value : null;
  } catch (_err) {
    return null;
  }
}

export function sanitizeFilter(value) {
  return typeof value === "string" ? stripControls(value).slice(0, 64) : "";
}

export function sanitizeColumns(value) {
  if (!Array.isArray(value)) return [];
  const seen = new Set();
  for (const item of value) {
    if (typeof item === "string" && NODE_ID_RE.test(item)) seen.add(item);
  }
  return Array.from(seen).slice(0, 64);
}

// Never throws: missing, unreadable, or corrupt storage yields DEFAULT_PREFS values.
export function loadPrefs(storage) {
  const prefs = {
    theme: DEFAULT_PREFS.theme,
    density: DEFAULT_PREFS.density,
    layout: DEFAULT_PREFS.layout,
    legend: DEFAULT_PREFS.legend,
    filter: DEFAULT_PREFS.filter,
    columns: [],
  };
  for (const key of Object.keys(PREF_DEFS)) {
    const raw = readItem(storage, key);
    if (raw !== null && PREF_DEFS[key].values.includes(raw)) prefs[key] = raw;
  }
  const filter = readItem(storage, "filter");
  if (filter !== null) prefs.filter = sanitizeFilter(filter);
  const columns = readItem(storage, "columns");
  if (columns !== null) {
    try {
      prefs.columns = sanitizeColumns(JSON.parse(columns));
    } catch (_err) {
      prefs.columns = [];
    }
  }
  return prefs;
}

export function savePref(storage, key, value) {
  try {
    if (!storage || typeof storage.setItem !== "function") return false;
    let text;
    if (key === "columns") text = JSON.stringify(sanitizeColumns(value));
    else if (key === "filter") text = sanitizeFilter(value);
    else if (PREF_DEFS[key] && PREF_DEFS[key].values.includes(value)) text = value;
    else return false;
    storage.setItem(STORAGE_PREFIX + key, text);
    return true;
  } catch (_err) {
    return false;
  }
}

// ---------------------------------------------------------------- query / follow

export function parseQuery(search) {
  const out = { session: null, follow: true, harness: null, invalidSession: false };
  let params;
  try {
    params = new URLSearchParams(typeof search === "string" ? search : "");
  } catch (_err) {
    return out;
  }
  const session = params.get("session");
  if (session !== null && session !== "") {
    if (SESSION_ID_RE.test(session)) {
      out.session = session;
      out.follow = false;
    } else {
      out.invalidSession = true;
    }
  }
  const harness = params.get("harness");
  if (harness && HARNESSES.includes(harness)) out.harness = harness;
  return out;
}

export function buildSearch({ session, harness }) {
  const params = new URLSearchParams();
  if (session) params.set("session", session);
  else params.set("follow", "latest");
  if (harness) params.set("harness", harness);
  return "?" + params.toString();
}

function mtimeValue(value) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  const parsed = typeof value === "string" ? Date.parse(value) : NaN;
  return Number.isFinite(parsed) ? parsed : 0;
}

// non-synthetic with stream > non-synthetic without stream > synthetic; newest first inside a tier.
export function rankSessions(sessions) {
  const tier = (s) => (s.synthetic ? 2 : s.has_stream === false ? 1 : 0);
  return sessions
    .filter((s) => s && typeof s.session_id === "string")
    .slice()
    .sort((a, b) => tier(a) - tier(b) || mtimeValue(b.mtime) - mtimeValue(a.mtime));
}

export function pickFollowTarget(sessions, harness) {
  const pool = rankSessions(sessions).filter(
    (s) => s.session_id !== "unknown" && (!harness || s.harness === harness),
  );
  return pool.length ? pool[0] : null;
}

export function filterSessions(sessions, query) {
  const q = sanitizeFilter(query).trim().toLowerCase();
  if (!q) return sessions;
  return sessions.filter((s) =>
    `${s.session_id} ${s.harness || ""} ${s.latest_status || ""}`.toLowerCase().includes(q),
  );
}

// ---------------------------------------------------------------- status views

export function statusView(id) {
  return Object.prototype.hasOwnProperty.call(STATUS_BY_ID, id) ? STATUS_BY_ID[id] : null;
}

export function iconHref(id) {
  return `${ICON_SPRITE}#s-${id}`;
}

export function nodeStatusText(node) {
  const view = statusView(node && node.status);
  if (!view) return "idle · unrecognized status";
  let text = view.label;
  if (node.capability_state === "unknown") text = `${view.label} · capability unknown`;
  if (node.unterminated) text += " · no completion observed";
  return text;
}

export function formatAge(ms) {
  const s = Math.max(0, Math.round(ms / 1000));
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m`;
  return `${Math.floor(m / 60)}h`;
}

// ---------------------------------------------------------------- chrome descriptors

function estimateServerNow(state, monoNow) {
  if (state.serverNowMs === null || state.serverNowAt === null) return null;
  return state.serverNowMs + Math.max(0, monoNow - state.serverNowAt);
}

export function describeSource(state, monoNow) {
  const body = state.nodes;
  if (!body) return null;
  if (body.synthetic === true || body.source_hint === "demo") {
    return { value: "demo", label: "demo", detail: null };
  }
  if (body.session_ended) return { value: "recorded", label: "recorded", detail: null };
  const last = typeof body.last_event_ts === "string" ? Date.parse(body.last_event_ts) : NaN;
  const now = estimateServerNow(state, monoNow);
  if (Number.isFinite(last) && now !== null) {
    const age = now - last;
    if (age <= LIVE_WINDOW_MS)
      return { value: "live", label: "live", detail: `last event ${formatAge(age)} ago` };
  }
  return { value: "recorded", label: "recorded", detail: null };
}

export function deriveConnection(state, monoNow) {
  if (state.nodesFailures > 0 || state.sessionsFailures > 0) return "disconnected";
  if (!state.hasSucceeded) return "connecting";
  const interval = state.target ? POLL_NODES_MS : POLL_SESSIONS_MS;
  const since = Math.max(state.lastSuccessAt ?? 0, state.visibleSince ?? 0);
  if (state.visible && monoNow - since > STALE_FACTOR * interval) return "stale";
  return "ok";
}

export const CONNECTION_LABELS = Object.freeze({
  connecting: "connecting",
  ok: "connected",
  stale: "stale",
  disconnected: "disconnected",
});

export function describeConnection(state, monoNow) {
  const value = deriveConnection(state, monoNow);
  const failures = Math.max(state.nodesFailures, state.sessionsFailures);
  return {
    value,
    label: CONNECTION_LABELS[value],
    icon: `c-${value}`,
    showRelaunch: value === "disconnected" && failures >= RELAUNCH_AFTER_FAILURES,
    failures,
  };
}

// ---------------------------------------------------------------- state

export function initialState(prefs, query) {
  return {
    prefs,
    harness: query.harness,
    invalidSession: query.invalidSession,
    pinned: query.session,
    followLatest: query.session === null,
    target: query.session,
    sessions: [],
    sessionsLoaded: false,
    nodes: null,
    etag: null,
    serverNowMs: null,
    serverNowAt: null,
    emptyKind: null,
    noStream: null,
    selectedNodeId: null,
    tab: "overview",
    turnsShown: DEFAULT_TURNS_SHOWN,
    nodesFailures: 0,
    sessionsFailures: 0,
    hasSucceeded: false,
    lastSuccessAt: null,
    visibleSince: null,
    visible: true,
    drawerOpen: false,
  };
}

function resetNodes(state) {
  return {
    ...state,
    nodes: null,
    etag: null,
    serverNowMs: null,
    serverNowAt: null,
    emptyKind: null,
    noStream: null,
    selectedNodeId: null,
    drawerOpen: false,
    turnsShown: DEFAULT_TURNS_SHOWN,
    nodesFailures: 0,
  };
}

function withTarget(state, target) {
  if (target === state.target) return state;
  return { ...resetNodes(state), target };
}

export function classifyNodesResponse({ status, body, etag, serverNow }) {
  if (status === 200 && body && typeof body === "object" && Array.isArray(body.nodes)) {
    return { kind: "ok", body, etag: etag || body.etag || null };
  }
  if (status === 304) return { kind: "not_modified", serverNow: serverNow || null };
  const code = body && typeof body === "object" ? body.error : null;
  if (status === 404 && code === "session_not_found") return { kind: "empty", code };
  if (status === 404 && code === "no_spectate_stream") {
    return { kind: "empty", code, hasHookEvents: body.has_hook_events === true };
  }
  if (status === 400) return { kind: "empty", code: "invalid_session_id" };
  return { kind: "network_error", status };
}

// A poll failure never clears nodes and never maps to idle.
export function applyNodesResult(state, result, monoNow) {
  switch (result.kind) {
    case "ok": {
      const parsed = Date.parse(result.body.server_now);
      return {
        ...state,
        nodes: result.body,
        etag: result.etag,
        emptyKind: null,
        noStream: null,
        nodesFailures: 0,
        hasSucceeded: true,
        lastSuccessAt: monoNow,
        serverNowMs: Number.isFinite(parsed) ? parsed : state.serverNowMs,
        serverNowAt: Number.isFinite(parsed) ? monoNow : state.serverNowAt,
      };
    }
    case "not_modified": {
      const parsed = result.serverNow ? Date.parse(result.serverNow) : NaN;
      return {
        ...state,
        nodesFailures: 0,
        hasSucceeded: true,
        lastSuccessAt: monoNow,
        serverNowMs: Number.isFinite(parsed) ? parsed : state.serverNowMs,
        serverNowAt: Number.isFinite(parsed) ? monoNow : state.serverNowAt,
      };
    }
    case "empty":
      return {
        ...state,
        nodes: null,
        etag: null,
        emptyKind: result.code,
        noStream:
          result.code === "no_spectate_stream"
            ? { hasHookEvents: result.hasHookEvents === true }
            : null,
        nodesFailures: 0,
        hasSucceeded: true,
        lastSuccessAt: monoNow,
      };
    default:
      return { ...state, nodesFailures: state.nodesFailures + 1 };
  }
}

export function applySessionsResult(state, result, monoNow) {
  if (result.kind !== "ok") return { ...state, sessionsFailures: state.sessionsFailures + 1 };
  const sessions = Array.isArray(result.sessions) ? result.sessions : [];
  let next = {
    ...state,
    sessions,
    sessionsLoaded: true,
    sessionsFailures: 0,
    hasSucceeded: true,
    lastSuccessAt: monoNow,
  };
  if (next.followLatest && next.selectedNodeId === null) {
    const pick = pickFollowTarget(sessions, next.harness);
    next = withTarget(next, pick ? pick.session_id : null);
  }
  return next;
}

export function pinSession(state, sessionId) {
  if (!SESSION_ID_RE.test(sessionId)) return state;
  return {
    ...withTarget({ ...state, invalidSession: false }, sessionId),
    pinned: sessionId,
    followLatest: false,
    selectedNodeId: null,
    drawerOpen: false,
  };
}

export function followLatest(state) {
  const pick = pickFollowTarget(state.sessions, state.harness);
  return {
    ...withTarget({ ...state, invalidSession: false }, pick ? pick.session_id : null),
    pinned: null,
    followLatest: true,
    selectedNodeId: null,
    drawerOpen: false,
  };
}

export function selectNode(state, nodeId) {
  return { ...state, selectedNodeId: nodeId, drawerOpen: nodeId !== null, tab: state.tab };
}

export function setTab(state, tab) {
  return { ...state, tab };
}

export function setVisibility(state, visible, monoNow) {
  return { ...state, visible, visibleSince: visible ? monoNow : state.visibleSince };
}

export function emptyStateKind(state) {
  if (state.emptyKind === "invalid_session_id") return "invalid_session";
  if (state.emptyKind === "session_not_found") return "session_not_found";
  if (state.emptyKind === "no_spectate_stream") return "no_spectate_stream";
  if (state.target === null && state.sessionsLoaded && state.sessions.length === 0)
    return "no_session";
  if (state.invalidSession && state.target === null && !state.sessionsLoaded)
    return "invalid_session";
  return null;
}

// ---------------------------------------------------------------- graph model

export function seedNodes() {
  return LOOP_STEPS.map((step) => ({
    node_id: `step:main:0:${step.id}`,
    parent_id: null,
    agent_id: "main",
    turn: 0,
    step: step.id,
    kind: "step.seed",
    status: "idle",
    seeded: true,
  }));
}

function isSpineNode(node) {
  return (
    STEP_IDS.has(node.step) &&
    (node.kind === "step.seed" || String(node.node_id).startsWith("step:"))
  );
}

function compareTools(a, b) {
  const ta = typeof a.ts === "string" ? a.ts : "";
  const tb = typeof b.ts === "string" ? b.ts : "";
  return ta < tb ? -1 : ta > tb ? 1 : String(a.node_id) < String(b.node_id) ? -1 : 1;
}

export function buildGraphModel(nodes, opts = {}) {
  const hidden = new Set(opts.hidden || []);
  const turnsShown = Math.max(1, opts.turnsShown || DEFAULT_TURNS_SHOWN);
  const list = (Array.isArray(nodes) ? nodes : []).filter(
    (n) => n && typeof n.node_id === "string",
  );

  const agentOrder = [];
  for (const node of list) {
    const agent = typeof node.agent_id === "string" && node.agent_id ? node.agent_id : "main";
    if (!agentOrder.includes(agent)) agentOrder.push(agent);
  }
  agentOrder.sort((a, b) => (a === "main" ? -1 : b === "main" ? 1 : 0));

  let maxTurn = 0;
  for (const node of list) maxTurn = Math.max(maxTurn, Number.isInteger(node.turn) ? node.turn : 0);
  const minTurn = Math.max(0, maxTurn - turnsShown + 1);
  const hasEarlier = list.some((n) => (Number.isInteger(n.turn) ? n.turn : 0) < minTurn);

  const agents = [];
  for (const agent of agentOrder) {
    if (hidden.has(agent)) continue;
    const turns = new Map();
    for (const node of list) {
      const nodeAgent = typeof node.agent_id === "string" && node.agent_id ? node.agent_id : "main";
      if (nodeAgent !== agent) continue;
      const turn = Number.isInteger(node.turn) ? node.turn : 0;
      if (turn < minTurn) continue;
      if (!turns.has(turn)) turns.set(turn, { turn, steps: new Map(), tools: [] });
      const bucket = turns.get(turn);
      if (isSpineNode(node)) bucket.steps.set(node.step, node);
      else bucket.tools.push(node);
    }
    const turnList = Array.from(turns.values())
      .sort((a, b) => a.turn - b.turn)
      .map((bucket) => ({
        turn: bucket.turn,
        steps: LOOP_STEPS.filter((def) => bucket.steps.has(def.id)).map((def) => ({
          def,
          node: bucket.steps.get(def.id),
        })),
        tools: bucket.tools.sort(compareTools),
      }));
    agents.push({ agent_id: agent, turns: turnList });
  }

  return { agents, allAgents: agentOrder, hasEarlier, minTurn, maxTurn };
}

export function navLayout(model) {
  return model.agents.map((agent) => {
    const ids = [];
    for (const turn of agent.turns) {
      for (const step of turn.steps) {
        ids.push(step.node.node_id);
        if (step.def.id === "execute-tools") for (const tool of turn.tools) ids.push(tool.node_id);
      }
      if (!turn.steps.some((s) => s.def.id === "execute-tools"))
        for (const tool of turn.tools) ids.push(tool.node_id);
    }
    return ids;
  });
}

export function navTarget(layout, currentId, key) {
  let col = -1;
  let row = -1;
  layout.forEach((ids, c) => {
    const r = ids.indexOf(currentId);
    if (r !== -1) {
      col = c;
      row = r;
    }
  });
  if (col === -1) return layout.length && layout[0].length ? layout[0][0] : null;
  const ids = layout[col];
  switch (key) {
    case "ArrowDown":
      return ids[Math.min(ids.length - 1, row + 1)];
    case "ArrowUp":
      return ids[Math.max(0, row - 1)];
    case "Home":
      return ids[0];
    case "End":
      return ids[ids.length - 1];
    case "ArrowRight":
    case "ArrowLeft": {
      const next = col + (key === "ArrowRight" ? 1 : -1);
      if (next < 0 || next >= layout.length || !layout[next].length) return currentId;
      return layout[next][Math.min(row, layout[next].length - 1)];
    }
    default:
      return null;
  }
}

export function gridTracks(count) {
  const vars = {};
  const parts = [];
  for (let i = 0; i < count; i += 1) {
    const name = i === 0 ? "--col-main" : `--col-agent-${i + 1}`;
    vars[name] = "1fr";
    parts.push(`minmax(var(--col-min, 11rem), var(${name}))`);
  }
  return { vars, template: parts.join(" ") };
}

// ---------------------------------------------------------------- payload (scrubbed fields only)

const METRIC_KEYS = ["duration_ms", "out_bytes", "prompt_chars"];
const TOOL_KEYS = ["name", "family", "target"];
const DENY_KEYS = ["by", "source", "rule"];

function safeText(value) {
  return typeof value === "string" ? stripControls(value).slice(0, 200) : null;
}

export function payloadRows(node) {
  const rows = [];
  if (!node) return rows;
  if (node.tool && typeof node.tool === "object") {
    for (const key of TOOL_KEYS) {
      const text = safeText(node.tool[key]);
      if (text) rows.push([`tool.${key}`, text]);
    }
  }
  if (node.metrics && typeof node.metrics === "object") {
    for (const key of METRIC_KEYS) {
      const value = node.metrics[key];
      if (typeof value === "number" && Number.isFinite(value))
        rows.push([`metrics.${key}`, String(value)]);
    }
  }
  if (node.deny && typeof node.deny === "object") {
    for (const key of DENY_KEYS) {
      const text = safeText(node.deny[key]);
      if (text) rows.push([`deny.${key}`, text]);
    }
  }
  const ts = safeText(node.ts);
  if (ts) rows.push(["ts", ts]);
  return rows;
}

// ---------------------------------------------------------------- DOM helpers (doc injected)

function setAttrs(node, attrs) {
  for (const key of Object.keys(attrs || {})) {
    const value = attrs[key];
    if (value === null || value === undefined || value === false) continue;
    node.setAttribute(key, value === true ? "" : String(value));
  }
}

function appendKids(node, doc, kids) {
  for (const kid of kids || []) {
    if (kid === null || kid === undefined || kid === false) continue;
    node.appendChild(typeof kid === "string" ? doc.createTextNode(kid) : kid);
  }
}

export function h(doc, tag, cls, attrs, kids) {
  const node = doc.createElement(tag);
  if (cls) node.setAttribute("class", cls);
  setAttrs(node, attrs);
  appendKids(node, doc, kids);
  return node;
}

function textEl(doc, tag, cls, text, attrs) {
  const node = h(doc, tag, cls, attrs);
  node.textContent = text;
  return node;
}

function svgIcon(doc, symbolId, size) {
  const svg = doc.createElementNS(SVG_NS, "svg");
  setAttrs(svg, {
    width: size,
    height: size,
    viewBox: "0 0 20 20",
    "aria-hidden": "true",
    focusable: "false",
    class: "icon-svg",
  });
  const use = doc.createElementNS(SVG_NS, "use");
  use.setAttribute("href", `${ICON_SPRITE}#${symbolId}`);
  svg.appendChild(use);
  return svg;
}

export function clearNode(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

export function statusIcon(doc, statusId, opts = {}) {
  const view = statusView(statusId) || STATUS_BY_ID.idle;
  const wrap = h(doc, "span", "status-icon", {
    "data-status": view.id,
    "data-shape": view.shape,
    "data-unterminated": opts.unterminated ? "true" : null,
  });
  wrap.appendChild(svgIcon(doc, `s-${view.id}`, opts.size || 14));
  if (opts.capabilityUnknown)
    wrap.appendChild(textEl(doc, "span", "cap-glyph", "?", { "aria-hidden": "true" }));
  return wrap;
}

// Shape + exact label, always both. The label never takes the status hue.
export function statusChip(doc, statusId, opts = {}) {
  const view = statusView(statusId);
  const text = opts.text || nodeStatusText({ status: statusId });
  const chip = h(doc, "span", "status-chip", {
    "data-status": view ? view.id : "idle",
    "data-shape": view ? view.shape : "circle-outline-muted",
  });
  chip.appendChild(statusIcon(doc, view ? view.id : "idle", opts));
  chip.appendChild(textEl(doc, "span", "status-label", text));
  return chip;
}

export function sourceBadge(doc, desc, mount) {
  const badge = mount || h(doc, "span", "badge");
  badge.setAttribute("data-source", desc.value);
  if (desc.value === "live")
    badge.appendChild(h(doc, "span", "live-dot", { "aria-hidden": "true" }));
  badge.appendChild(textEl(doc, "span", "badge-label", desc.label));
  if (desc.detail) badge.appendChild(textEl(doc, "span", "badge-detail", desc.detail));
  return badge;
}

export function connectionIndicator(doc, desc) {
  const wrap = h(doc, "span", "conn-inner", { "data-connection": desc.value });
  wrap.appendChild(svgIcon(doc, desc.icon, 14));
  wrap.appendChild(textEl(doc, "span", "conn-label", desc.label));
  return wrap;
}

function commandBlock(doc, command, buttonLabel, onCopy) {
  const row = h(doc, "div", "command");
  row.appendChild(textEl(doc, "code", "command-text", command));
  const btn = textEl(doc, "button", "btn btn-small", buttonLabel, {
    type: "button",
    "data-copy": command,
  });
  if (onCopy) btn.addEventListener("click", () => onCopy(command, btn));
  row.appendChild(btn);
  return row;
}

export function nodeLabel(node) {
  if (node.seeded || isSpineNode(node)) {
    const def = LOOP_STEPS.find((s) => s.id === node.step);
    return def ? def.label : String(node.step);
  }
  if (node.tool && typeof node.tool.name === "string" && node.tool.name)
    return node.tool.name.slice(0, 64);
  const tail = String(node.node_id).split(":").pop();
  return tail || String(node.node_id);
}

export function nodeButton(doc, node, ctx) {
  const view = statusView(node.status);
  const isSpine = node.seeded || isSpineNode(node);
  const btn = h(doc, "button", `node ${isSpine ? "node-step" : "node-tool"}`, {
    type: "button",
    "data-node-id": node.node_id,
    "data-status": view ? view.id : "idle",
    "data-unterminated": node.unterminated ? "true" : null,
    "data-selected": ctx.selectedId === node.node_id ? "true" : null,
    "aria-current": ctx.selectedId === node.node_id ? "true" : null,
    tabindex: ctx.tabStopId === node.node_id ? "0" : "-1",
  });
  btn.appendChild(
    statusIcon(doc, node.status, {
      size: 16,
      unterminated: node.unterminated,
      capabilityUnknown: node.capability_state === "unknown",
    }),
  );
  const text = h(doc, "span", "node-text");
  text.appendChild(
    textEl(doc, "span", isSpine ? "node-name" : "node-name node-mono", nodeLabel(node)),
  );
  text.appendChild(
    textEl(
      doc,
      "span",
      "node-status",
      node.seeded ? "idle · never seen — cause not established" : nodeStatusText(node),
    ),
  );
  btn.appendChild(text);
  if (ctx.onSelect) btn.addEventListener("click", () => ctx.onSelect(node.node_id));
  return btn;
}

function nodeItem(doc, node, ctx) {
  const entering = ctx.seen && !ctx.seen.has(node.node_id);
  const li = h(doc, "li", "node-wrap", {
    "data-status": statusView(node.status) ? node.status : "idle",
    "data-enter": entering ? "true" : null,
  });
  li.appendChild(nodeButton(doc, node, ctx));
  if (ctx.seen) ctx.seen.add(node.node_id);
  return li;
}

export function renderGraph(doc, mount, model, ctx) {
  clearNode(mount);
  const { vars, template } = gridTracks(model.agents.length);
  if (mount.style && typeof mount.style.setProperty === "function") {
    for (const name of Object.keys(vars)) mount.style.setProperty(name, vars[name]);
    mount.style.setProperty("--graph-tracks", template);
  }
  const layout = navLayout(model);
  const flat = layout.flat();
  const tabStopId =
    ctx.selectedId && flat.includes(ctx.selectedId) ? ctx.selectedId : flat[0] || null;
  const nodeCtx = { ...ctx, tabStopId };

  for (const agent of model.agents) {
    const col = h(doc, "section", "agent-col", {
      "data-agent": agent.agent_id,
      "aria-label": `agent ${agent.agent_id}`,
    });
    col.appendChild(textEl(doc, "h3", "agent-head", agent.agent_id));
    for (const turn of agent.turns) {
      const block = h(doc, "div", "turn", { "data-turn": String(turn.turn) });
      block.appendChild(textEl(doc, "p", "turn-head", `turn ${turn.turn}`));
      const spine = h(doc, "ol", "spine");
      const hasTools = turn.steps.some((s) => s.def.id === "execute-tools");
      for (const step of turn.steps) {
        const item = nodeItem(doc, step.node, nodeCtx);
        if (step.def.id === "execute-tools" && turn.tools.length) {
          const branch = h(doc, "ul", "tool-list", { "aria-label": "tool calls" });
          for (const tool of turn.tools) branch.appendChild(nodeItem(doc, tool, nodeCtx));
          item.appendChild(branch);
        }
        spine.appendChild(item);
      }
      if (!hasTools && turn.tools.length) {
        const branch = h(doc, "ul", "tool-list", { "aria-label": "tool calls" });
        for (const tool of turn.tools) branch.appendChild(nodeItem(doc, tool, nodeCtx));
        spine.appendChild(branch);
      }
      block.appendChild(spine);
      col.appendChild(block);
    }
    mount.appendChild(col);
  }
}

export function renderRail(doc, mount, emptyEl, items, ctx) {
  clearNode(mount);
  emptyEl.hidden = items.length > 0;
  if (items.length === 0) {
    emptyEl.textContent = ctx.hasAny ? "No sessions match the filter." : "No sessions yet.";
  }
  for (const s of items) {
    const li = h(doc, "li", "session-item");
    const active = ctx.target === s.session_id;
    const btn = h(doc, "button", "session-row", {
      type: "button",
      "data-session": s.session_id,
      "aria-current": active ? "true" : null,
      "data-active": active ? "true" : null,
      title: s.session_id,
    });
    const statusId = statusView(s.latest_status) ? s.latest_status : "idle";
    btn.appendChild(statusIcon(doc, statusId, { size: 14 }));
    const text = h(doc, "span", "session-text");
    const top = h(doc, "span", "session-top");
    if (statusId === "running")
      top.appendChild(h(doc, "span", "live-dot", { "aria-hidden": "true" }));
    top.appendChild(textEl(doc, "span", "session-id", s.session_id));
    text.appendChild(top);
    const meta = h(doc, "span", "session-meta");
    meta.appendChild(textEl(doc, "span", "chip-harness", s.harness || "unknown"));
    if (s.synthetic) meta.appendChild(textEl(doc, "span", "chip-demo", "DEMO"));
    if (s.has_stream === false) meta.appendChild(textEl(doc, "span", "chip-nostream", "no stream"));
    meta.appendChild(
      textEl(doc, "span", "chip-status", statusView(s.latest_status) ? s.latest_status : "idle"),
    );
    text.appendChild(meta);
    btn.appendChild(text);
    if (ctx.onPick) btn.addEventListener("click", () => ctx.onPick(s.session_id));
    li.appendChild(btn);
    mount.appendChild(li);
  }
}

export function renderLegend(doc, mount) {
  clearNode(mount);
  const list = h(doc, "ul", "legend-list");
  for (const s of STATUSES) {
    const li = h(doc, "li", "legend-item");
    li.appendChild(statusChip(doc, s.id, { text: s.label, size: 14 }));
    li.appendChild(textEl(doc, "span", "legend-note", s.note));
    list.appendChild(li);
  }
  const extra = h(doc, "li", "legend-item");
  const glyph = h(doc, "span", "status-chip");
  glyph.appendChild(statusIcon(doc, "idle", { size: 14, capabilityUnknown: true }));
  glyph.appendChild(textEl(doc, "span", "status-label", "idle · capability unknown"));
  extra.appendChild(glyph);
  extra.appendChild(textEl(doc, "span", "legend-note", "harness cell unverified; not unavailable"));
  list.appendChild(extra);
  mount.appendChild(list);
}

function infoRows(doc, rows) {
  const dl = h(doc, "dl", "kv");
  for (const [k, v] of rows) {
    dl.appendChild(textEl(doc, "dt", "kv-key", k));
    dl.appendChild(textEl(doc, "dd", "kv-val", v));
  }
  return dl;
}

export function inspectorTabs(placement) {
  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "policy", label: "Policy" },
    { id: "payload", label: "Payload" },
  ];
  if (placement === "inspector") tabs.push({ id: "legend", label: "Legend" });
  return tabs;
}

export function renderInspectorBody(doc, mount, node, tab) {
  clearNode(mount);
  const body = h(doc, "div", "inspector-body", {
    role: "tabpanel",
    id: "inspector-panel",
    "aria-labelledby": `tab-${tab}`,
    tabindex: "0",
  });
  if (tab === "legend") {
    renderLegend(doc, body);
    mount.appendChild(body);
    return;
  }
  if (!node) {
    body.appendChild(textEl(doc, "p", "muted", "Select a node in the graph to inspect it."));
    mount.appendChild(body);
    return;
  }
  if (tab === "overview") {
    body.appendChild(textEl(doc, "h3", "insp-title node-mono", nodeLabel(node)));
    body.appendChild(
      statusChip(doc, node.status, {
        text: nodeStatusText(node),
        unterminated: node.unterminated,
        capabilityUnknown: node.capability_state === "unknown",
        size: 16,
      }),
    );
    const rows = [
      ["node_id", node.node_id],
      ["agent", node.agent_id || "main"],
      ["turn", String(Number.isInteger(node.turn) ? node.turn : 0)],
    ];
    if (node.step) rows.push(["step", String(node.step)]);
    if (node.kind) rows.push(["kind", String(node.kind)]);
    if (node.parent_id) rows.push(["parent", String(node.parent_id)]);
    if (node.parent_truncated) rows.push(["parent", "truncated"]);
    if (node.ts) rows.push(["ts", String(node.ts)]);
    body.appendChild(infoRows(doc, rows));
    if (node.seeded)
      body.appendChild(
        textEl(doc, "p", "muted", "Seeded spine: no events observed — cause not established."),
      );
  } else if (tab === "policy") {
    body.appendChild(textEl(doc, "h3", "insp-title", "Policy"));
    body.appendChild(statusChip(doc, node.status, { text: nodeStatusText(node), size: 16 }));
    if (node.deny && typeof node.deny === "object") {
      body.appendChild(
        infoRows(
          doc,
          DENY_KEYS.map((k) => [`deny.${k}`, safeText(node.deny[k]) || "—"]),
        ),
      );
    } else {
      body.appendChild(textEl(doc, "p", "muted", "No deny joined for this node."));
    }
    if (node.capability_state === "unknown") {
      body.appendChild(
        textEl(
          doc,
          "p",
          "muted",
          "Capability unknown: this harness cell is unverified. It is not reported as unavailable.",
        ),
      );
    }
    if (node.unterminated) {
      body.appendChild(
        textEl(doc, "p", "muted", "No completion observed — cause not established."),
      );
    }
  } else {
    body.appendChild(textEl(doc, "h3", "insp-title", "Payload"));
    const rows = payloadRows(node);
    if (rows.length) body.appendChild(infoRows(doc, rows));
    else body.appendChild(textEl(doc, "p", "muted", "no scrubbed fields"));
  }
  mount.appendChild(body);
}

export function renderEmpty(doc, mount, kind, state, handlers = {}) {
  clearNode(mount);
  const box = h(doc, "div", "empty-inner", { "data-empty": kind });
  if (kind === "no_session") {
    box.appendChild(textEl(doc, "p", "empty-copy", "no sessions yet"));
    box.appendChild(
      textEl(
        doc,
        "p",
        "empty-sub",
        "Run a session in your harness, or copy the command to load the synthetic gallery.",
      ),
    );
    box.appendChild(commandBlock(doc, DEMO_COMMAND, "Load demo", handlers.onCopy));
  } else if (kind === "session_not_found") {
    box.appendChild(textEl(doc, "p", "empty-copy", `session ${state.target} not found`));
    box.appendChild(
      textEl(doc, "p", "empty-sub", "No run directory with that id under .ravenclaude/runs."),
    );
    const btn = textEl(doc, "button", "btn", "Follow latest", { type: "button" });
    if (handlers.onFollow) btn.addEventListener("click", handlers.onFollow);
    box.appendChild(btn);
    box.appendChild(commandBlock(doc, DEMO_COMMAND, "Load demo", handlers.onCopy));
  } else if (kind === "no_spectate_stream") {
    box.appendChild(
      textEl(
        doc,
        "p",
        "empty-copy",
        `session ${state.target} exists — no spectate emitter yet (hook-based emission arrives in v0.2)`,
      ),
    );
    box.appendChild(
      textEl(
        doc,
        "p",
        "empty-sub",
        "Showing a seeded spine: nothing has been observed, cause not established.",
      ),
    );
  } else if (kind === "invalid_session") {
    box.appendChild(textEl(doc, "p", "empty-copy", "that session id is not valid"));
    const btn = textEl(doc, "button", "btn", "Follow latest", { type: "button" });
    if (handlers.onFollow) btn.addEventListener("click", handlers.onFollow);
    box.appendChild(btn);
  }
  mount.appendChild(box);
}

export function renderOverlay(doc, mount, conn, handlers = {}) {
  clearNode(mount);
  const panel = h(doc, "div", "overlay-panel", { role: "status" });
  panel.appendChild(svgIcon(doc, "c-disconnected", 18));
  const body = h(doc, "div", "overlay-body");
  body.appendChild(textEl(doc, "p", "overlay-title", "disconnected — showing last known state"));
  if (conn.showRelaunch) {
    body.appendChild(
      textEl(doc, "p", "overlay-sub", "The spectate server is not answering. Relaunch it with:"),
    );
    body.appendChild(commandBlock(doc, RELAUNCH_COMMAND, "Copy", handlers.onCopy));
  } else {
    body.appendChild(textEl(doc, "p", "overlay-sub", "Retrying…"));
  }
  panel.appendChild(body);
  mount.appendChild(panel);
}

// ---------------------------------------------------------------- bootstrap

function createApp(env) {
  const { doc, win, storage, fetchFn, mono } = env;
  const $ = (id) => doc.getElementById(id);
  const refs = {
    root: $("spectate-app"),
    graph: $("graph"),
    graphEmpty: $("graph-empty"),
    overlay: $("graph-overlay"),
    notice: $("graph-notice"),
    banner: $("follow-banner"),
    earlier: $("earlier-turns"),
    rail: $("session-list"),
    railEmpty: $("session-list-empty"),
    followToggle: $("follow-toggle"),
    inspector: $("inspector"),
    inspectorBody: $("inspector-body"),
    inspectorTabs: $("inspector-tabs"),
    inspectorClose: $("inspector-close"),
    scrim: $("drawer-scrim"),
    legend: $("legend-footer"),
    source: $("source-badge"),
    conn: $("connection-status"),
    filter: $("session-filter"),
    density: $("density-select"),
    layout: $("layout-select"),
    legendSel: $("legend-select"),
    theme: $("theme-toggle"),
    columns: $("columns-list"),
    steerPanel: $("steer-panel"),
    steerPause: $("steer-pause"),
    steerResume: $("steer-resume"),
    steerNote: $("steer-note"),
    steerSend: $("steer-send-note"),
    steerStatus: $("steer-status"),
    observeOnly: $("observe-only"),
  };
  const required = Object.entries(refs).filter(
    ([k]) => !k.startsWith("steer") && k !== "observeOnly",
  );
  if (required.some(([, r]) => !r)) return null;

  const html = doc.documentElement;
  const prefs = loadPrefs(storage);
  const query = parseQuery(win.location.search);
  let state = initialState(prefs, query);
  const seen = new Set();
  const sigs = {};
  let generation = 0;
  const timers = {};
  let eventSource = null;
  let csrfToken = null;
  let steerEnabled = false;
  let steerPending = null;

  const wide = win.matchMedia ? win.matchMedia("(min-width: 80em)") : { matches: true };

  function applyPrefs() {
    html.setAttribute("data-theme", state.prefs.theme);
    html.setAttribute("data-density", state.prefs.density);
    html.setAttribute("data-layout", state.prefs.layout);
    refs.theme.textContent = `Theme: ${state.prefs.theme}`;
    refs.density.value = state.prefs.density;
    refs.layout.value = state.prefs.layout;
    refs.legendSel.value = state.prefs.legend;
    if (refs.filter.value !== state.prefs.filter) refs.filter.value = state.prefs.filter;
  }

  function setPref(key, value) {
    state = { ...state, prefs: { ...state.prefs, [key]: value } };
    savePref(storage, key, value);
    applyPrefs();
    render();
  }

  function copy(command, btn) {
    const nav = win.navigator;
    const done = () => {
      const old = btn.textContent;
      btn.textContent = "Copied";
      win.setTimeout(() => {
        btn.textContent = old;
      }, 1500);
    };
    if (nav && nav.clipboard && typeof nav.clipboard.writeText === "function") {
      nav.clipboard.writeText(command).then(done, () => {});
    }
  }

  function pushUrl() {
    try {
      win.history.replaceState(
        null,
        "",
        buildSearch({ session: state.pinned, harness: state.harness }),
      );
    } catch (_err) {
      /* history may be unavailable in embedded contexts */
    }
  }

  function selectedNode() {
    if (!state.nodes || !state.selectedNodeId) return null;
    return state.nodes.nodes.find((n) => n.node_id === state.selectedNodeId) || null;
  }

  function onSelect(nodeId) {
    state = selectNode(state, nodeId);
    render();
    if (!wide.matches) {
      const close = refs.inspectorClose;
      close.focus();
    }
  }

  function closeInspector() {
    const returnId = state.selectedNodeId;
    state = selectNode(state, null);
    render();
    if (returnId) {
      const btn = refs.graph.querySelector(`[data-node-id="${CSS.escape(returnId)}"]`);
      if (btn) btn.focus();
    }
  }

  function onPick(sessionId) {
    state = pinSession(state, sessionId);
    pushUrl();
    render();
    pollNodes();
    startEventSource();
    refreshSteerStatus();
  }

  function onFollow() {
    state = followLatest(state);
    pushUrl();
    render();
    if (state.target) {
      pollNodes();
      startEventSource();
      refreshSteerStatus();
    }
  }

  function renderChrome() {
    const mn = mono();
    const src = describeSource(state, mn);
    const srcSig = JSON.stringify(src);
    if (sigs.source !== srcSig) {
      sigs.source = srcSig;
      clearNode(refs.source);
      refs.source.hidden = !src;
      if (src) sourceBadge(doc, src, refs.source);
    }
    const conn = describeConnection(state, mn);
    const connSig = JSON.stringify(conn);
    if (sigs.conn !== connSig) {
      sigs.conn = connSig;
      clearNode(refs.conn);
      refs.conn.setAttribute("data-connection", conn.value);
      refs.conn.appendChild(connectionIndicator(doc, conn));
      clearNode(refs.overlay);
      refs.overlay.hidden = conn.value !== "disconnected";
      if (conn.value === "disconnected") renderOverlay(doc, refs.overlay, conn, { onCopy: copy });
    }
  }

  function renderRailIfChanged() {
    const visible = filterSessions(state.sessions, state.prefs.filter);
    const sig = JSON.stringify([visible, state.target, state.prefs.filter, state.followLatest]);
    refs.followToggle.setAttribute("aria-pressed", state.followLatest ? "true" : "false");
    if (sigs.rail === sig) return;
    sigs.rail = sig;
    renderRail(doc, refs.rail, refs.railEmpty, visible, {
      target: state.target,
      hasAny: state.sessions.length > 0,
      onPick,
    });
  }

  function renderGraphIfChanged() {
    const kind = emptyStateKind(state);
    const noStream = state.emptyKind === "no_spectate_stream";
    const nodes = state.nodes ? state.nodes.nodes : noStream ? seedNodes() : [];
    const model = buildGraphModel(nodes, {
      hidden: state.prefs.columns,
      turnsShown: state.turnsShown,
    });
    const sig = JSON.stringify([
      state.etag,
      state.target,
      noStream,
      state.prefs.columns,
      state.turnsShown,
      state.selectedNodeId,
      kind,
      state.nodes ? state.nodes.nodes.length : 0,
    ]);
    refs.banner.hidden = !(state.followLatest && state.target !== null);
    refs.earlier.hidden = !model.hasEarlier;
    if (sigs.graph === sig) return model;
    sigs.graph = sig;
    const focusedId =
      doc.activeElement && doc.activeElement.getAttribute
        ? doc.activeElement.getAttribute("data-node-id")
        : null;
    if (state.nodes === null && !noStream) seen.clear();
    renderGraph(doc, refs.graph, model, { selectedId: state.selectedNodeId, seen, onSelect });
    if (focusedId) {
      const again = refs.graph.querySelector(`[data-node-id="${CSS.escape(focusedId)}"]`);
      if (again) again.focus({ preventScroll: true });
    }
    refs.graph.hidden = model.agents.length === 0;
    refs.graphEmpty.hidden = !kind;
    if (kind) refs.graphEmpty.setAttribute("data-kind", kind);
    if (kind) renderEmpty(doc, refs.graphEmpty, kind, state, { onCopy: copy, onFollow });
    else clearNode(refs.graphEmpty);
    return model;
  }

  function renderInspectorIfChanged() {
    const tabs = inspectorTabs(state.prefs.legend);
    if (!tabs.some((t) => t.id === state.tab)) state = setTab(state, "overview");
    const node = selectedNode();
    const sig = JSON.stringify([state.tab, node, tabs.length]);
    refs.inspector.setAttribute("data-drawer", state.drawerOpen ? "open" : "closed");
    refs.root.setAttribute("data-drawer", state.drawerOpen ? "open" : "closed");
    if (sigs.insp === sig) return;
    sigs.insp = sig;
    clearNode(refs.inspectorTabs);
    for (const t of tabs) {
      const btn = textEl(doc, "button", "tab", t.label, {
        type: "button",
        role: "tab",
        id: `tab-${t.id}`,
        "aria-selected": state.tab === t.id ? "true" : "false",
        "aria-controls": "inspector-panel",
        tabindex: state.tab === t.id ? "0" : "-1",
        "data-tab": t.id,
      });
      btn.addEventListener("click", () => {
        state = setTab(state, t.id);
        render();
      });
      refs.inspectorTabs.appendChild(btn);
    }
    renderInspectorBody(doc, refs.inspectorBody, node, state.tab);
  }

  function renderColumns(model) {
    const ids = model ? model.allAgents : [];
    const sig = JSON.stringify([ids, state.prefs.columns]);
    if (sigs.cols === sig) return;
    sigs.cols = sig;
    clearNode(refs.columns);
    if (!ids.length) {
      refs.columns.appendChild(textEl(doc, "p", "muted", "no agents yet"));
      return;
    }
    for (const id of ids) {
      const label = h(doc, "label", "check");
      const input = h(doc, "input", null, {
        type: "checkbox",
        checked: state.prefs.columns.includes(id) ? null : true,
      });
      input.checked = !state.prefs.columns.includes(id);
      input.addEventListener("change", () => {
        const hidden = new Set(state.prefs.columns);
        if (input.checked) hidden.delete(id);
        else hidden.add(id);
        setPref("columns", Array.from(hidden));
      });
      label.appendChild(input);
      label.appendChild(textEl(doc, "span", "node-mono", id));
      refs.columns.appendChild(label);
    }
  }

  function renderLegendFooter() {
    const footer = state.prefs.legend === "footer";
    refs.legend.hidden = !footer;
    if (footer && sigs.legend !== "footer") {
      sigs.legend = "footer";
      renderLegend(doc, refs.legend);
    } else if (!footer) {
      sigs.legend = null;
    }
  }

  function renderNotice() {
    const bad = state.invalidSession && state.pinned === null;
    refs.notice.hidden = !bad;
    if (bad)
      refs.notice.textContent = "The session id in the URL is not valid; following latest instead.";
  }

  function render() {
    renderChrome();
    renderRailIfChanged();
    const model = renderGraphIfChanged();
    renderInspectorIfChanged();
    renderColumns(model);
    renderLegendFooter();
    renderNotice();
  }

  async function getJson(url, etag) {
    const headers = { Accept: "application/json" };
    if (etag) headers["If-None-Match"] = etag;
    const res = await fetchFn(url, { headers, cache: "no-store", credentials: "same-origin" });
    let body = null;
    if (res.status !== 304) {
      try {
        body = await res.json();
      } catch (_err) {
        body = null;
      }
    }
    return {
      status: res.status,
      body,
      etag: res.headers.get("ETag"),
      serverNow: res.headers.get("X-Spectate-Server-Now"),
    };
  }

  async function pollNodes() {
    const target = state.target;
    if (!target || !state.visible) return;
    let result;
    try {
      const raw = await getJson(
        `/__spectate/nodes?session=${encodeURIComponent(target)}`,
        state.etag,
      );
      result = classifyNodesResponse(raw);
    } catch (_err) {
      result = { kind: "network_error" };
    }
    if (state.target !== target) return;
    state = applyNodesResult(state, result, mono());
    render();
  }

  async function pollSessions() {
    if (!state.visible) return;
    let result;
    try {
      const harness = state.harness ? `&harness=${encodeURIComponent(state.harness)}` : "";
      const raw = await getJson(`/__spectate/sessions?limit=${MAX_SESSIONS_LIMIT}${harness}`, null);
      result =
        raw.status === 200 && raw.body && Array.isArray(raw.body.sessions)
          ? { kind: "ok", sessions: raw.body.sessions }
          : { kind: "error" };
    } catch (_err) {
      result = { kind: "error" };
    }
    const before = state.target;
    state = applySessionsResult(state, result, mono());
    render();
    if (state.target !== before && state.target) pollNodes();
  }

  function loop(name, fn, ms, gen) {
    const run = async () => {
      timers[name] = null;
      if (gen !== generation || !state.visible) return;
      try {
        await fn();
      } catch (_err) {
        /* a render or parse fault must not stop the poll loop */
      }
      if (gen === generation && state.visible) timers[name] = win.setTimeout(run, ms);
    };
    run();
  }

  function stopEventSource() {
    if (eventSource) {
      try {
        eventSource.close();
      } catch (_err) {
        /* ignore */
      }
      eventSource = null;
    }
  }

  function startEventSource() {
    stopEventSource();
    if (!state.visible || !state.target || typeof win.EventSource !== "function") return;
    const url = `/__spectate/stream?session=${encodeURIComponent(state.target)}`;
    try {
      eventSource = new win.EventSource(url);
    } catch (_err) {
      return;
    }
    eventSource.addEventListener("spectate", () => {
      pollNodes();
    });
    eventSource.addEventListener("ready", () => {
      pollNodes();
    });
    eventSource.onerror = () => {
      /* keep poll loop as fallback; EventSource auto-reconnects */
    };
  }

  async function ensureCsrf() {
    if (csrfToken) return csrfToken;
    try {
      const res = await fetchFn("/__csrf", { credentials: "same-origin", cache: "no-store" });
      if (!res.ok) return null;
      const body = await res.json();
      csrfToken = body && body.token ? body.token : null;
      return csrfToken;
    } catch (_err) {
      return null;
    }
  }

  async function refreshSteerStatus() {
    if (!refs.steerPanel) return;
    try {
      const q = state.target ? `?session=${encodeURIComponent(state.target)}` : "";
      const raw = await getJson(`/__spectate/steer${q}`, null);
      if (raw.status !== 200 || !raw.body) {
        steerEnabled = false;
        refs.steerPanel.hidden = true;
        return;
      }
      steerEnabled = !!raw.body.enabled;
      steerPending = raw.body.pending || null;
      refs.steerPanel.hidden = !steerEnabled;
      if (refs.observeOnly) {
        refs.observeOnly.textContent = steerEnabled
          ? "live stream · steer enabled"
          : "live stream · steer opt-in via spectate_steer";
      }
      if (refs.steerStatus) {
        if (!steerPending) refs.steerStatus.textContent = "";
        else {
          const bits = [];
          if (steerPending.paused) bits.push("paused");
          if (steerPending.note_pending) bits.push(`note (${steerPending.note_chars || 0})`);
          refs.steerStatus.textContent = bits.join(" · ");
        }
      }
    } catch (_err) {
      /* ignore */
    }
  }

  async function postSteer(action, note) {
    const token = await ensureCsrf();
    if (!token || !state.target) {
      if (refs.steerStatus) refs.steerStatus.textContent = "steer unavailable";
      return;
    }
    try {
      const res = await fetchFn("/__spectate/steer", {
        method: "POST",
        credentials: "same-origin",
        cache: "no-store",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          "X-CSRF-Token": token,
        },
        body: JSON.stringify({
          session: state.target,
          action,
          note: note || "",
        }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (refs.steerStatus)
          refs.steerStatus.textContent = (body && body.error) || `steer ${res.status}`;
        return;
      }
      steerPending = body.pending || null;
      await refreshSteerStatus();
      pollNodes();
    } catch (_err) {
      if (refs.steerStatus) refs.steerStatus.textContent = "steer failed";
    }
  }

  function startPolling() {
    generation += 1;
    const gen = generation;
    stopTimers();
    loop("nodes", pollNodes, POLL_NODES_MS, gen);
    loop("sessions", pollSessions, POLL_SESSIONS_MS, gen);
    timers.chrome = win.setInterval(renderChrome, 1000);
    startEventSource();
    refreshSteerStatus();
  }

  function stopTimers() {
    for (const key of Object.keys(timers)) {
      if (timers[key] !== null && timers[key] !== undefined) {
        if (key === "chrome") win.clearInterval(timers[key]);
        else win.clearTimeout(timers[key]);
      }
      timers[key] = null;
    }
    stopEventSource();
  }

  function onVisibility() {
    const visible = doc.visibilityState !== "hidden";
    state = setVisibility(state, visible, mono());
    if (visible) {
      render();
      startPolling();
    } else {
      generation += 1;
      stopTimers();
    }
  }

  function trapFocus(event) {
    if (wide.matches || !state.drawerOpen) return;
    if (event.key === "Escape") {
      event.preventDefault();
      closeInspector();
      return;
    }
    if (event.key !== "Tab") return;
    const focusable = Array.from(
      refs.inspector.querySelectorAll("button, [href], input, select, [tabindex]"),
    ).filter((el) => el.getAttribute("tabindex") !== "-1");
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && doc.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && doc.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  function bind() {
    refs.filter.addEventListener("input", () =>
      setPref("filter", sanitizeFilter(refs.filter.value)),
    );
    refs.density.addEventListener("change", () => setPref("density", refs.density.value));
    refs.layout.addEventListener("change", () => setPref("layout", refs.layout.value));
    refs.legendSel.addEventListener("change", () => setPref("legend", refs.legendSel.value));
    refs.theme.addEventListener("click", () =>
      setPref("theme", state.prefs.theme === "dark" ? "light" : "dark"),
    );
    refs.followToggle.addEventListener("click", () => {
      if (state.followLatest) {
        if (state.target) {
          state = pinSession(state, state.target);
          pushUrl();
          render();
        }
      } else {
        onFollow();
      }
    });
    if (refs.steerPause)
      refs.steerPause.addEventListener("click", () =>
        postSteer("pause", refs.steerNote && refs.steerNote.value),
      );
    if (refs.steerResume) refs.steerResume.addEventListener("click", () => postSteer("resume", ""));
    if (refs.steerSend)
      refs.steerSend.addEventListener("click", () => {
        const note = refs.steerNote ? refs.steerNote.value : "";
        postSteer("note", note);
        if (refs.steerNote) refs.steerNote.value = "";
      });
    refs.earlier.addEventListener("click", () => {
      state = { ...state, turnsShown: state.turnsShown + DEFAULT_TURNS_SHOWN };
      render();
    });
    refs.inspectorClose.addEventListener("click", closeInspector);
    refs.scrim.addEventListener("click", closeInspector);
    doc.addEventListener("keydown", trapFocus);
    doc.addEventListener("visibilitychange", onVisibility);

    refs.inspectorTabs.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      const tabs = inspectorTabs(state.prefs.legend);
      const idx = tabs.findIndex((t) => t.id === state.tab);
      const next = tabs[(idx + (event.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
      event.preventDefault();
      state = setTab(state, next.id);
      render();
      const btn = doc.getElementById(`tab-${next.id}`);
      if (btn) btn.focus();
    });

    refs.graph.addEventListener("keydown", (event) => {
      const current =
        event.target && event.target.getAttribute
          ? event.target.getAttribute("data-node-id")
          : null;
      if (!current) return;
      if (event.key === "Enter" || event.key === " ") return;
      const nodes = state.nodes ? state.nodes.nodes : seedNodes();
      const model = buildGraphModel(nodes, {
        hidden: state.prefs.columns,
        turnsShown: state.turnsShown,
      });
      const target = navTarget(navLayout(model), current, event.key);
      if (!target) return;
      event.preventDefault();
      const btn = refs.graph.querySelector(`[data-node-id="${CSS.escape(target)}"]`);
      if (btn) {
        refs.graph
          .querySelectorAll("[data-node-id]")
          .forEach((n) => n.setAttribute("tabindex", "-1"));
        btn.setAttribute("tabindex", "0");
        btn.focus();
      }
    });
  }

  applyPrefs();
  bind();
  state = setVisibility(state, doc.visibilityState !== "hidden", mono());
  render();
  if (state.visible) startPolling();
  return { getState: () => state, render };
}

export function startApp(doc, win) {
  const storage = (() => {
    try {
      return win.localStorage;
    } catch (_err) {
      return null;
    }
  })();
  return createApp({
    doc,
    win,
    storage,
    fetchFn: (...args) => win.fetch(...args),
    mono: () => win.performance.now(),
  });
}

if (typeof document !== "undefined" && typeof window !== "undefined") {
  const boot = () => startApp(document, window);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
}

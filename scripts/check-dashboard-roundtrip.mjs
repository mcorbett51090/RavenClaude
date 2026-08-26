#!/usr/bin/env node
/* check-dashboard-roundtrip.mjs — guards the comfort-posture serializer against the
 * round-trip data-loss class of bug (v0.61.0).
 *
 * The dashboard's emitYaml() rebuilds the WHOLE comfort-posture.yaml from `state`,
 * so any key the serializer doesn't model is silently dropped on save. This test
 * extracts the REAL emitYaml() / applyGuardrailConfig() / quoteYamlKey() sources
 * from the generated dashboard.html (plus the constants they depend on), runs a
 * save → reload round-trip over the pipeline-stage guardrail keys
 * (runaway / decision_review / definition_of_done / command_review.dev_repo_exempt),
 * and asserts every value survives. No DOM is needed — these functions are pure
 * over `state`. Pairs with `node --check` (syntax) for behavioral coverage.
 *
 * Usage: node scripts/check-dashboard-roundtrip.mjs [path/to/dashboard.html]
 */
import { readFileSync } from "node:fs";

const htmlPath = process.argv[2] || "plugins/ravenclaude-core/dashboard.html";
const html = readFileSync(htmlPath, "utf8");

// The app JS is the largest <script> block.
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const app =
  scripts.find((s) => s.includes("function activate(")) ||
  scripts.reduce((a, b) => (b.length > a.length ? b : a), "");

/* Extract a brace-balanced top-level declaration by name. Works for both
 * `function NAME(...) { ... }` and `const NAME = ... ;` (object/array literal). */
function extract(src, header) {
  const start = src.indexOf(header);
  if (start === -1) throw new Error(`not found: ${header}`);
  let i = src.indexOf("{", start);
  // For `const X = Object.freeze({...});` the first { is inside the literal.
  let depth = 0;
  for (; i < src.length; i++) {
    const c = src[i];
    if (c === "{") depth++;
    else if (c === "}") {
      depth--;
      if (depth === 0) break;
    }
  }
  // Include a trailing `);` / `;` if present (for const = (...){...});
  let end = i + 1;
  while (end < src.length && /[);\s]/.test(src[end]) && src[end] !== "\n") end++;
  return src.slice(start, end);
}

const pieces = [
  extract(app, "const CR_DEFAULT ="),
  extract(app, "const TIER_DEFAULT ="),
  extract(app, "const RUNAWAY_DEFAULT ="),
  extract(app, "const PARALLELISM_DEFAULT ="),
  extract(app, "const DOD_DEFAULT ="),
  // simple scalar/array consts the functions reference
  app.match(/const CR_SEATS = \[[^\]]*\];/)[0],
  app.match(/const TIER_SEATS = \[[^\]]*\];/)[0],
  app.match(/const TIERS = \[[^\]]*\];/)[0],
  app.match(/const DECISION_REVIEW_VALUES = \[[^\]]*\];/)[0],
  app.match(/const DECISION_REVIEW_DEFAULT = [^;]*;/)[0],
  app.match(/const WORKTREE_GUARD_VALUES = \[[^\]]*\];/)[0],
  app.match(/const WORKTREE_GUARD_DEFAULT = [^;]*;/)[0],
  app.match(/const WORKTREE_BOUND_VALUES = \[[^\]]*\];/)[0],
  app.match(/const WORKTREE_BOUND_DEFAULT = [^;]*;/)[0],
  app.match(/const DASHBOARD_AUTOSTART_VALUES = \[[^\]]*\];/)[0],
  app.match(/const DASHBOARD_AUTOSTART_DEFAULT = [^;]*;/)[0],
  app.match(/const ORCHESTRATOR_VALUES = \[[^\]]*\];/)[0],
  app.match(/const ORCHESTRATOR_DEFAULT = [^;]*;/)[0],
  app.match(/const ORCHESTRATOR_SCOPE_VALUES = \[[^\]]*\];/)[0],
  app.match(/const ORCHESTRATOR_SCOPE_DEFAULT = [^;]*;/)[0],
  // Agentic Work-Streams classifier keys (F4).
  app.match(/const STREAM_CLASSIFY_VALUES = \[[^\]]*\];/)[0],
  app.match(/const STREAM_CLASSIFY_DEFAULT = [^;]*;/)[0],
  app.match(/const STREAM_THRESHOLD_DEFAULT = [^;]*;/)[0],
  app.match(/const STREAM_THRESHOLD_MIN = [^;]*;/)[0],
  app.match(/const STREAM_THRESHOLD_MAX = [^;]*;/)[0],
  // Conserve-tokens exception (v0.273.0) — the persistent trigger + its threshold.
  app.match(/const CONSERVE_TOKENS_DEFAULT = [^;]*;/)[0],
  app.match(/const CONSERVE_AUTO_PCT_DEFAULT = [^;]*;/)[0],
  app.match(/const CONSERVE_AUTO_PCT_MIN = [^;]*;/)[0],
  app.match(/const CONSERVE_AUTO_PCT_MAX = [^;]*;/)[0],
  // Session-context handoff (v0.61.0 data-loss class) — mode enum + spawn union + freeze default.
  app.match(/const CONTEXT_HANDOFF_MODE_VALUES = \[[^\]]*\];/)[0],
  app.match(/const CONTEXT_HANDOFF_MODE_DEFAULT = [^;]*;/)[0],
  app.match(/const CONTEXT_HANDOFF_SPAWN_VALUES = \[[^\]]*\];/)[0],
  extract(app, "const CONTEXT_HANDOFF_DEFAULT ="),
  // Cheap lane (v0.61.0 data-loss class, closed same shape as context_handoff).
  app.match(/const CHEAP_LANE_MODE_VALUES = \[[^\]]*\];/)[0],
  app.match(/const CHEAP_LANE_MODE_DEFAULT = [^;]*;/)[0],
  app.match(/const CHEAP_LANE_TIER_VALUES = \[[^\]]*\];/)[0],
  app.match(/const CHEAP_LANE_TIER_DEFAULT = [^;]*;/)[0],
  app.match(/const CHEAP_LANE_AGENT_VALUES = \[[^\]]*\];/)[0],
  app.match(/const CHEAP_LANE_AGENT_DEFAULT = [^;]*;/)[0],
  extract(app, "const CHEAP_LANE_DEFAULT ="),
  extract(app, "function freshTiers()"),
  extract(app, "function quoteYamlKey("),
  extract(app, "function applyGuardrailConfig("),
  extract(app, "function emitYaml()"),
  // Web-access serializer (P3) — a SECOND serializer Gate 35 was structurally
  // blind to. It reads/writes the DOM, so the harness supplies a minimal shim.
  extract(app, "function waPanel()"),
  extract(app, "function waLines("),
  extract(app, "function emitWebAccessYaml()"),
  extract(app, "function applyWebAccess("),
];

// Build a sandbox whose body declares `let state` (the variable emitYaml /
// applyGuardrailConfig close over) plus the extracted functions, and exposes a
// fresh-state factory + setter so each scenario starts clean.
// Minimal DOM shim for the web-access serializer (P3). It reads two textareas
// (.wa-allow / .wa-deny) inside a .web-access-page panel via document.querySelector;
// the shim implements exactly that surface and nothing else. Test helpers set/read
// the textarea .value so the harness stays DOM-free from Node's point of view.
const domShim = `
const _waEls = { ".wa-allow": { value: "" }, ".wa-deny": { value: "" } };
const _waPanelObj = { querySelector(sel) { return _waEls[sel] || null; } };
const document = { querySelector(sel) { return sel === ".web-access-page" ? _waPanelObj : null; } };
function _setWA(allowStr, denyStr) { _waEls[".wa-allow"].value = allowStr; _waEls[".wa-deny"].value = denyStr; }
function _getWA() { return { allow: _waEls[".wa-allow"].value, deny: _waEls[".wa-deny"].value }; }
`;

const harness = `
let state = null;
${domShim}
${pieces.join("\n\n")}
function _freshState() {
  return {
    schema_version: 5,
    categories: {},
    security_deny: [],
    security_deny_baseline: [],
    design_checkins: true,
    command_review: Object.assign({}, CR_DEFAULT, { tiers: freshTiers(), mcp_allowed_servers: [] }),
    runaway: Object.assign({}, RUNAWAY_DEFAULT),
    parallelism: Object.assign({}, PARALLELISM_DEFAULT),
    conserve_tokens: CONSERVE_TOKENS_DEFAULT,
    conserve_tokens_auto_pct: CONSERVE_AUTO_PCT_DEFAULT,
    decision_review: DECISION_REVIEW_DEFAULT,
    worktree_guard: WORKTREE_GUARD_DEFAULT,
    worktree_bound: WORKTREE_BOUND_DEFAULT,
    dashboard_autostart: DASHBOARD_AUTOSTART_DEFAULT,
    definition_of_done: Object.assign({}, DOD_DEFAULT),
    orchestrator: ORCHESTRATOR_DEFAULT,
    orchestrator_scope: ORCHESTRATOR_SCOPE_DEFAULT,
    orchestrator_zdr_confirmed: false,
    orchestrator_repo_pii: true,
    orchestrator_pseudonymize: false,
    stream_classify: STREAM_CLASSIFY_DEFAULT,
    stream_threshold: STREAM_THRESHOLD_DEFAULT,
    context_handoff: Object.assign({}, CONTEXT_HANDOFF_DEFAULT),
    cheap_lane: Object.assign({}, CHEAP_LANE_DEFAULT),
    expanded: {},
  };
}
function _set(s) { state = s; }
function _get() { return state; }
return { emitYaml, applyGuardrailConfig, emitWebAccessYaml, applyWebAccess,
         _freshState, _set, _get, _setWA, _getWA,
         _defaults: { PARALLELISM_DEFAULT, CONSERVE_TOKENS_DEFAULT, CONSERVE_AUTO_PCT_DEFAULT } };
`;
const api = new Function(harness)();

let failures = 0;
function check(name, cond) {
  if (!cond) {
    console.error(`  ✗ ${name}`);
    failures++;
  }
}

// ── Test 1: every guardrail key round-trips through emit → parse ──────────────
{
  const s = api._freshState();
  s.runaway = { max_total: 500, max_consecutive: 3, off: false };
  s.parallelism = { enabled: true, max_workers: 6, unlimited: false };
  s.decision_review = "binding";
  s.worktree_guard = "block";
  s.worktree_bound = "off";
  s.dashboard_autostart = "open";
  s.definition_of_done = { cmd: "npm test && npm run lint", max_blocks: 4 };
  s.command_review.dev_repo_exempt = true;
  s.orchestrator = "decide";
  s.orchestrator_scope = "all";
  s.orchestrator_zdr_confirmed = true;
  s.orchestrator_repo_pii = false;
  s.orchestrator_pseudonymize = true;
  s.stream_classify = "auto";
  s.stream_threshold = 0.42;
  s.conserve_tokens = true;
  s.conserve_tokens_auto_pct = 65;
  s.context_handoff = { mode: "nag", spawn: "os-terminal", context_window_tokens: 150000 };
  s.cheap_lane = { mode: "agent", tier: "top", agent: "copilot" };
  api._set(s);

  const yaml = api.emitYaml();
  check("runaway.max_total emitted", /^  max_total: 500$/m.test(yaml));
  check("runaway.max_consecutive emitted", /^  max_consecutive: 3$/m.test(yaml));
  check("parallelism block emitted", /^parallelism:$/m.test(yaml));
  check("parallelism.max_workers emitted", /^  max_workers: 6$/m.test(yaml));
  check("decision_review emitted", /^decision_review: binding$/m.test(yaml));
  check("worktree_guard emitted", /^worktree_guard: block$/m.test(yaml));
  check("worktree_bound emitted", /^worktree_bound: off$/m.test(yaml));
  check("dashboard_autostart emitted", /^dashboard_autostart: open$/m.test(yaml));
  check("definition_of_done.cmd emitted", /^  cmd: "npm test && npm run lint"$/m.test(yaml));
  check("definition_of_done.max_blocks emitted", /^  max_blocks: 4$/m.test(yaml));
  check("command_review.dev_repo_exempt emitted", /^  dev_repo_exempt: true$/m.test(yaml));
  check("orchestrator emitted", /^orchestrator: decide$/m.test(yaml));
  check("orchestrator_scope emitted", /^orchestrator_scope: all$/m.test(yaml));
  check("orchestrator_zdr_confirmed emitted", /^orchestrator_zdr_confirmed: true$/m.test(yaml));
  check("orchestrator_repo_pii emitted", /^orchestrator_repo_pii: false$/m.test(yaml));
  check("orchestrator_pseudonymize emitted", /^orchestrator_pseudonymize: true$/m.test(yaml));
  check("stream_classify emitted", /^stream_classify: auto$/m.test(yaml));
  check("stream_threshold emitted", /^stream_threshold: 0\.42$/m.test(yaml));
  check("conserve_tokens emitted", /^conserve_tokens: true$/m.test(yaml));
  check("conserve_tokens_auto_pct emitted", /^conserve_tokens_auto_pct: 65$/m.test(yaml));
  check("context_handoff block emitted", /^context_handoff:$/m.test(yaml));
  check("context_handoff.mode emitted", /^  mode: nag$/m.test(yaml));
  check("context_handoff.spawn emitted", /^  spawn: os-terminal$/m.test(yaml));
  check(
    "context_handoff.context_window_tokens emitted",
    /^  context_window_tokens: 150000$/m.test(yaml),
  );
  check("cheap_lane block emitted", /^cheap_lane:$/m.test(yaml));
  check("cheap_lane.mode emitted", /^  mode: agent$/m.test(yaml));
  check("cheap_lane.tier emitted", /^  tier: top$/m.test(yaml));
  check("cheap_lane.agent emitted", /^  agent: copilot$/m.test(yaml));

  // And the hydrator reads them back into a fresh state.
  api._set(api._freshState());
  api.applyGuardrailConfig({
    runaway: { max_total: 500, max_consecutive: 3 },
    parallelism: { enabled: true, max_workers: 6 },
    decision_review: "binding",
    worktree_guard: "block",
    worktree_bound: "off",
    dashboard_autostart: "open",
    definition_of_done: { cmd: "npm test && npm run lint", max_blocks: 4 },
    command_review: { dev_repo_exempt: true },
    orchestrator: "decide",
    orchestrator_scope: "all",
    orchestrator_zdr_confirmed: true,
    orchestrator_repo_pii: false,
    orchestrator_pseudonymize: true,
    stream_classify: "auto",
    stream_threshold: 0.42,
    conserve_tokens: true,
    conserve_tokens_auto_pct: 65,
    context_handoff: { mode: "nag", spawn: "os-terminal", context_window_tokens: 150000 },
    cheap_lane: { mode: "agent", tier: "top", agent: "copilot" },
  });
  const h = api._get();
  check("hydrate runaway.max_total", h.runaway.max_total === 500);
  check("hydrate parallelism.max_workers", h.parallelism.max_workers === 6);
  check("hydrate parallelism.enabled", h.parallelism.enabled === true);
  check("hydrate decision_review", h.decision_review === "binding");
  check("hydrate worktree_guard", h.worktree_guard === "block");
  check("hydrate worktree_bound", h.worktree_bound === "off");
  check("hydrate dashboard_autostart", h.dashboard_autostart === "open");
  check("hydrate dod.cmd", /npm test/.test(h.definition_of_done.cmd));
  check("hydrate dev_repo_exempt", h.command_review.dev_repo_exempt === true);
  check("hydrate orchestrator", h.orchestrator === "decide");
  check("hydrate orchestrator_scope", h.orchestrator_scope === "all");
  check("hydrate orchestrator_zdr_confirmed", h.orchestrator_zdr_confirmed === true);
  check("hydrate orchestrator_repo_pii", h.orchestrator_repo_pii === false);
  check("hydrate orchestrator_pseudonymize", h.orchestrator_pseudonymize === true);
  check("hydrate stream_classify", h.stream_classify === "auto");
  check("hydrate stream_threshold", h.stream_threshold === 0.42);
  check("hydrate conserve_tokens", h.conserve_tokens === true);
  check("hydrate conserve_tokens_auto_pct", h.conserve_tokens_auto_pct === 65);
  check("hydrate context_handoff.mode", h.context_handoff.mode === "nag");
  check("hydrate context_handoff.spawn", h.context_handoff.spawn === "os-terminal");
  check(
    "hydrate context_handoff.context_window_tokens",
    h.context_handoff.context_window_tokens === 150000,
  );
  check("hydrate cheap_lane.mode", h.cheap_lane.mode === "agent");
  check("hydrate cheap_lane.tier", h.cheap_lane.tier === "top");
  check("hydrate cheap_lane.agent", h.cheap_lane.agent === "copilot");
}

// ── Test 2: defaults are NOT emitted (absent ⇒ default; no posture bloat) ─────
{
  api._set(api._freshState());
  const yaml = api.emitYaml();
  check("no runaway block at default", !/runaway:/.test(yaml));
  check("no parallelism block at default", !/parallelism:/.test(yaml));
  check("no decision_review at default", !/decision_review:/.test(yaml));
  check("no worktree_guard at default", !/^worktree_guard:/m.test(yaml));
  check("no worktree_bound at default", !/^worktree_bound:/m.test(yaml));
  check("no dashboard_autostart at default", !/^dashboard_autostart:/m.test(yaml));
  check("no definition_of_done at default", !/definition_of_done:/.test(yaml));
  check("no dev_repo_exempt at default", !/dev_repo_exempt:/.test(yaml));
  check("no orchestrator at default", !/^orchestrator:/m.test(yaml));
  check("no orchestrator_scope at default", !/^orchestrator_scope:/m.test(yaml));
  check("no orchestrator_zdr_confirmed at default", !/orchestrator_zdr_confirmed:/.test(yaml));
  check("no orchestrator_repo_pii at default", !/orchestrator_repo_pii:/.test(yaml));
  check("no orchestrator_pseudonymize at default", !/orchestrator_pseudonymize:/.test(yaml));
  check("no stream_classify at default", !/^stream_classify:/m.test(yaml));
  check("no stream_threshold at default", !/^stream_threshold:/m.test(yaml));
  check("no conserve_tokens at default", !/^conserve_tokens:/m.test(yaml));
  check("no conserve_tokens_auto_pct at default", !/^conserve_tokens_auto_pct:/m.test(yaml));
  check("no context_handoff block at default", !/^context_handoff:/m.test(yaml));
  check("no cheap_lane block at default", !/^cheap_lane:/m.test(yaml));
}

// ── Test 3: runaway: off scalar form ─────────────────────────────────────────
{
  const s = api._freshState();
  s.runaway.off = true;
  api._set(s);
  const yaml = api.emitYaml();
  check("runaway: off scalar emitted", /^runaway: off$/m.test(yaml));
}

// ── Test 4: parallelism defaults to MAXIMUM, and the unlimited sentinel still
//            round-trips (v0.273.0).
//
// The pre-v0.273.0 form of this test asserted that {enabled:true, workers:4,
// unlimited:true} EMITS a block. That state is now the DEFAULT, so under the
// emit-when-non-default rule it must emit NOTHING — asserting the old thing
// would have pinned the bug the flip exists to remove. The unlimited sentinel
// is still exercised, on a state that genuinely differs from the default.
{
  const d = api._defaults.PARALLELISM_DEFAULT;
  check("PARALLELISM_DEFAULT is maximum (enabled)", d.enabled === true);
  check("PARALLELISM_DEFAULT is maximum (unlimited)", d.unlimited === true);

  // The max state is the default -> absent from the emitted posture.
  const s0 = api._freshState();
  s0.parallelism = { enabled: true, max_workers: 4, unlimited: true };
  api._set(s0);
  check("max parallelism emits NO block (absent ⇒ max)", !/^parallelism:$/m.test(api.emitYaml()));

  // A non-default state that is still unlimited must emit the sentinel.
  const s = api._freshState();
  s.parallelism = { enabled: true, max_workers: 8, unlimited: true };
  api._set(s);
  const yaml = api.emitYaml();
  check("parallelism unlimited emitted", /^  max_workers: unlimited$/m.test(yaml));

  api._set(api._freshState());
  api.applyGuardrailConfig({ parallelism: { enabled: true, max_workers: "unlimited" } });
  check("hydrate parallelism unlimited", api._get().parallelism.unlimited === true);

  // Sequential must be written EXPLICITLY, or "absent ⇒ max" would silently
  // convert an opt-out into an opt-in on the next Save.
  const sq = api._freshState();
  sq.parallelism = { enabled: false, max_workers: 4, unlimited: true };
  api._set(sq);
  const yseq = api.emitYaml();
  check("sequential parallelism IS emitted", /^parallelism:$/m.test(yseq));
  check("sequential emits enabled:false", /^  enabled: false$/m.test(yseq));

  // Hydrating a block that sets ONLY `enabled` must not clobber `unlimited`.
  api._set(api._freshState());
  api.applyGuardrailConfig({ parallelism: { enabled: false } });
  check("hydrate enabled-only keeps unlimited default", api._get().parallelism.unlimited === true);
  check("hydrate enabled-only sets enabled false", api._get().parallelism.enabled === false);

  // The scalar `parallelism: off` idiom (YAML `off` -> boolean false) must mean
  // sequential. Unhandled, the flipped default would make it mean MAXIMUM --
  // the opposite of what it reads.
  api._set(api._freshState());
  api.applyGuardrailConfig({ parallelism: false });
  check(
    "scalar `parallelism: off` hydrates to sequential",
    api._get().parallelism.enabled === false,
  );
  api._set(api._freshState());
  api.applyGuardrailConfig({ parallelism: true });
  check("scalar `parallelism: on` hydrates to enabled", api._get().parallelism.enabled === true);
}

// ── Test 4b: conserve-tokens threshold bounds ────────────────────────────────
{
  api._set(api._freshState());
  api.applyGuardrailConfig({ conserve_tokens_auto_pct: 101 });
  check(
    "out-of-range auto_pct rejected",
    api._get().conserve_tokens_auto_pct === api._defaults.CONSERVE_AUTO_PCT_DEFAULT,
  );
  api._set(api._freshState());
  api.applyGuardrailConfig({ conserve_tokens_auto_pct: 0 });
  check(
    "auto_pct 0 accepted (disables the automatic trigger)",
    api._get().conserve_tokens_auto_pct === 0,
  );
  const yz = api.emitYaml();
  check("auto_pct 0 IS emitted (differs from default)", /^conserve_tokens_auto_pct: 0$/m.test(yz));
}

// ── Test 5: the web-access serializer round-trips (P3) ───────────────────────
// emitWebAccessYaml()/applyWebAccess() are a SEPARATE serializer (they hydrate
// .ravenclaude/web-access.yaml from the DOM), which Gate 35 was structurally blind
// to. Its schema is only allow/deny — both must survive emit → parse → emit, and a
// reintroduced drop of either key must be caught (see audit-gates.sh must-fail).
{
  api._setWA("api.github.com\nexample.com", "evil.test\nbad.example.com");
  const yaml = api.emitWebAccessYaml();
  check("web-access allow key emitted", /^allow:$/m.test(yaml));
  check("web-access allow entry emitted", /^  - api\.github\.com$/m.test(yaml));
  check("web-access deny key emitted", /^deny:$/m.test(yaml));
  check("web-access deny entry emitted", /^  - evil\.test$/m.test(yaml));

  // Clear the DOM, hydrate from the emitted YAML, re-emit: values must survive.
  api._setWA("", "");
  api.applyWebAccess(yaml);
  const wa = api._getWA();
  check("hydrate web-access allow", wa.allow.split("\n").includes("api.github.com"));
  check("hydrate web-access allow (2nd)", wa.allow.split("\n").includes("example.com"));
  check("hydrate web-access deny", wa.deny.split("\n").includes("evil.test"));
  const yaml2 = api.emitWebAccessYaml();
  check("web-access round-trip is stable", yaml2 === yaml);
}

// ── Test 6: context_handoff round-trips with ONLY spawn set (the live-posture
//            shape: `context_handoff: { spawn: os-terminal }`). mode stays the
//            default `off` (never emitted), but the block MUST still be written so
//            the spawn recipe survives a Save. This is the exact key the v0.61.0
//            data-loss class would have silently dropped before it was modelled. ─
{
  const s = api._freshState();
  s.context_handoff = { mode: "off", spawn: "os-terminal", context_window_tokens: null };
  api._set(s);
  const yaml = api.emitYaml();
  check("context_handoff block emitted for spawn-only", /^context_handoff:$/m.test(yaml));
  check("context_handoff.spawn emitted (spawn-only)", /^  spawn: os-terminal$/m.test(yaml));
  check("context_handoff.mode NOT emitted when default off", !/^  mode:/m.test(yaml));

  // An unknown spawn value is rejected by the union guard, so an otherwise-default
  // block emits nothing (a Save neither invents nor corrupts a value).
  api._set(api._freshState());
  api.applyGuardrailConfig({ context_handoff: { spawn: "not-a-real-value" } });
  check("unknown spawn ignored on hydrate", api._get().context_handoff.spawn === "");
  api._set(api._get());
  check("all-default context_handoff emits no block", !/^context_handoff:/m.test(api.emitYaml()));

  // The union accepts all three readers' spawn values (preserve, don't canonicalize).
  for (const v of ["copy-paste-only", "same-host", "os-terminal"]) {
    api._set(api._freshState());
    api.applyGuardrailConfig({ context_handoff: { spawn: v } });
    check(`spawn union accepts ${v}`, api._get().context_handoff.spawn === v);
  }
}

// ── Test 7: cheap_lane round-trips with ONLY mode set (the live-posture shape:
//            `cheap_lane: { mode: agent, tier: fast }`, where tier is already the
//            default). tier/agent stay their defaults (never emitted), but the
//            block MUST still be written so the mode survives a Save — this is
//            the exact key a real dashboard Save would have silently dropped
//            before this fix (verified absent from emitYaml() prior to it). ──
{
  const s = api._freshState();
  s.cheap_lane = { mode: "advise", tier: "fast", agent: "grok" };
  api._set(s);
  const yaml = api.emitYaml();
  check("cheap_lane block emitted for mode-only", /^cheap_lane:$/m.test(yaml));
  check("cheap_lane.mode emitted (mode-only)", /^  mode: advise$/m.test(yaml));
  check("cheap_lane.tier NOT emitted when default fast", !/^  tier:/m.test(yaml));
  check("cheap_lane.agent NOT emitted when default grok", !/^  agent:/m.test(yaml));

  // An unknown mode/tier/agent value is rejected by the enum guard, so an
  // otherwise-default block emits nothing (a Save neither invents nor
  // corrupts a value).
  api._set(api._freshState());
  api.applyGuardrailConfig({ cheap_lane: { mode: "not-a-real-mode" } });
  check("unknown mode ignored on hydrate", api._get().cheap_lane.mode === "off");
  check("all-default cheap_lane emits no block", !/^cheap_lane:/m.test(api.emitYaml()));

  // Every accepted value round-trips.
  for (const v of ["off", "advise", "agent"]) {
    api._set(api._freshState());
    api.applyGuardrailConfig({ cheap_lane: { mode: v } });
    check(`mode enum accepts ${v}`, api._get().cheap_lane.mode === v);
  }
  for (const v of ["fast", "balanced", "top"]) {
    api._set(api._freshState());
    api.applyGuardrailConfig({ cheap_lane: { tier: v } });
    check(`tier enum accepts ${v}`, api._get().cheap_lane.tier === v);
  }
  for (const v of ["grok", "copilot"]) {
    api._set(api._freshState());
    api.applyGuardrailConfig({ cheap_lane: { agent: v } });
    check(`agent enum accepts ${v}`, api._get().cheap_lane.agent === v);
  }
}

if (failures) {
  console.error(`dashboard round-trip: ${failures} FAILED`);
  process.exit(1);
}
console.log("dashboard round-trip: all guardrail keys survive emit/hydrate; defaults stay absent");

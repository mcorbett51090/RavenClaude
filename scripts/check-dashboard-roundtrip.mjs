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
  app.match(/const ORCHESTRATOR_VALUES = \[[^\]]*\];/)[0],
  app.match(/const ORCHESTRATOR_DEFAULT = [^;]*;/)[0],
  extract(app, "function freshTiers()"),
  extract(app, "function quoteYamlKey("),
  extract(app, "function applyGuardrailConfig("),
  extract(app, "function emitYaml()"),
];

// Build a sandbox whose body declares `let state` (the variable emitYaml /
// applyGuardrailConfig close over) plus the extracted functions, and exposes a
// fresh-state factory + setter so each scenario starts clean.
const harness = `
let state = null;
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
    decision_review: DECISION_REVIEW_DEFAULT,
    definition_of_done: Object.assign({}, DOD_DEFAULT),
    orchestrator: ORCHESTRATOR_DEFAULT,
    expanded: {},
  };
}
function _set(s) { state = s; }
function _get() { return state; }
return { emitYaml, applyGuardrailConfig, _freshState, _set, _get };
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
  s.definition_of_done = { cmd: "npm test && npm run lint", max_blocks: 4 };
  s.command_review.dev_repo_exempt = true;
  s.orchestrator = "decide";
  api._set(s);

  const yaml = api.emitYaml();
  check("runaway.max_total emitted", /^  max_total: 500$/m.test(yaml));
  check("runaway.max_consecutive emitted", /^  max_consecutive: 3$/m.test(yaml));
  check("parallelism block emitted", /^parallelism:$/m.test(yaml));
  check("parallelism.max_workers emitted", /^  max_workers: 6$/m.test(yaml));
  check("decision_review emitted", /^decision_review: binding$/m.test(yaml));
  check("definition_of_done.cmd emitted", /^  cmd: "npm test && npm run lint"$/m.test(yaml));
  check("definition_of_done.max_blocks emitted", /^  max_blocks: 4$/m.test(yaml));
  check("command_review.dev_repo_exempt emitted", /^  dev_repo_exempt: true$/m.test(yaml));
  check("orchestrator emitted", /^orchestrator: decide$/m.test(yaml));

  // And the hydrator reads them back into a fresh state.
  api._set(api._freshState());
  api.applyGuardrailConfig({
    runaway: { max_total: 500, max_consecutive: 3 },
    parallelism: { enabled: true, max_workers: 6 },
    decision_review: "binding",
    definition_of_done: { cmd: "npm test && npm run lint", max_blocks: 4 },
    command_review: { dev_repo_exempt: true },
    orchestrator: "decide",
  });
  const h = api._get();
  check("hydrate runaway.max_total", h.runaway.max_total === 500);
  check("hydrate parallelism.max_workers", h.parallelism.max_workers === 6);
  check("hydrate parallelism.enabled", h.parallelism.enabled === true);
  check("hydrate decision_review", h.decision_review === "binding");
  check("hydrate dod.cmd", /npm test/.test(h.definition_of_done.cmd));
  check("hydrate dev_repo_exempt", h.command_review.dev_repo_exempt === true);
  check("hydrate orchestrator", h.orchestrator === "decide");
}

// ── Test 2: defaults are NOT emitted (absent ⇒ default; no posture bloat) ─────
{
  api._set(api._freshState());
  const yaml = api.emitYaml();
  check("no runaway block at default", !/runaway:/.test(yaml));
  check("no parallelism block at default", !/parallelism:/.test(yaml));
  check("no decision_review at default", !/decision_review:/.test(yaml));
  check("no definition_of_done at default", !/definition_of_done:/.test(yaml));
  check("no dev_repo_exempt at default", !/dev_repo_exempt:/.test(yaml));
  check("no orchestrator at default", !/^orchestrator:/m.test(yaml));
}

// ── Test 3: runaway: off scalar form ─────────────────────────────────────────
{
  const s = api._freshState();
  s.runaway.off = true;
  api._set(s);
  const yaml = api.emitYaml();
  check("runaway: off scalar emitted", /^runaway: off$/m.test(yaml));
}

// ── Test 4: parallelism unlimited sentinel round-trips ───────────────────────
{
  const s = api._freshState();
  s.parallelism = { enabled: true, max_workers: 4, unlimited: true };
  api._set(s);
  const yaml = api.emitYaml();
  check("parallelism unlimited emitted", /^  max_workers: unlimited$/m.test(yaml));

  api._set(api._freshState());
  api.applyGuardrailConfig({ parallelism: { enabled: true, max_workers: "unlimited" } });
  check("hydrate parallelism unlimited", api._get().parallelism.unlimited === true);
}

if (failures) {
  console.error(`dashboard round-trip: ${failures} FAILED`);
  process.exit(1);
}
console.log("dashboard round-trip: all guardrail keys survive emit/hydrate; defaults stay absent");

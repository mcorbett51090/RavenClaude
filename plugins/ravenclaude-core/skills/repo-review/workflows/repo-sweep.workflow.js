// ─── repo-sweep — whole-repo systematic bug sweep (dynamic workflow) ─────────
// Docs: https://code.claude.com/docs/en/workflows · authoritative guidance:
//   the `workflow-authoring` skill.
// Shipped as a plugin asset at
//   plugins/ravenclaude-core/skills/repo-review/workflows/repo-sweep.workflow.js
// Orchestrates six phases — Map, Review, Merge, Verify, Fix, Report — over the
// five sibling scripts in ../scripts/*.py, coordinating AGENTS that do all the
// real filesystem/git work (this script itself has no fs/shell access — only
// agent() calls can touch the filesystem). Mirrors this repo's own
// forge-pipeline "artifact contract": a gate's subagent writes its own
// artifact to disk and returns a compact receipt, never the full payload — so
// findings bodies live on disk under the run dir and only small JSON receipts
// ever flow through this script's own memory.
//
// Runtime caps: ≤16 concurrent agents, 1,000 total/run, no mid-run user input,
// no direct fs/shell from the script (agents do the IO), resumable in-session.
export const meta = {
  name: "repo-sweep",
  description:
    "Whole-repo systematic bug sweep across 8 review dimensions (including ci-cd-actions-security for GitHub Actions/CI-gate defects) — maps the repo into risk-ranked batches, reviews each batch per dimension/model with a cache-hit skip, merges + dedupes findings, adversarially verifies every file's survivors, optionally auto-fixes CONFIRMED + fixable findings file-by-file, and reports coverage honestly.",
  whenToUse:
    "When the user wants a comprehensive, multi-dimension bug sweep over an entire repository (or a --only/--since-narrowed slice of it), with adversarial verification gating any fix. Requires args.effort to be one of high, xhigh, max, or ultra — low and medium are refused outright, no phase runs for them.",
  phases: [
    {
      title: "Map",
      detail:
        "One agent runs repo_map.py and returns a compact {plan_path, batch_ids, coverage} receipt.",
    },
    {
      title: "Review",
      detail:
        "Dimensions run SEQUENTIALLY (pipeline); within each dimension, models x batches run in PARALLEL. A cheap cache-check step precedes each real review agent and replays a full cache hit instead of re-reviewing.",
    },
    {
      title: "Merge",
      detail:
        "One agent runs findings_merge.py over the findings shards and returns {artifact, survivors_count, over_cap_count}.",
    },
    {
      title: "Verify",
      detail:
        "One adversarial verify agent per FILE with surviving findings, batching that file's findings. A global severity-sorted verifyCap bounds how many findings are ever verified.",
    },
    {
      title: "Fix",
      detail:
        "Gated behind args.autofix === true. Snapshots the tree first, then one fix agent per FILE applies only CONFIRMED + fixable_in_place findings, capped at args.fixCap; never commits, stages, or pushes.",
    },
    {
      title: "Report",
      detail:
        "Assembles counts + a coverage-honesty report.md whose first line states the reviewed/deferred split whenever files were deferred at this budget.",
    },
  ],
};

// ─── Resume-safe ordinal clock shim (Date.now()/new Date() THROW in a workflow
// script — they would break resume) — copied verbatim from the pattern used by
// plugins/ravenclaude-core/skills/rc-deep-research/rc-deep-research.js. These
// are monotonic ORDINALS, not wall-clock ms; good enough for a run-id suffix
// and a store --timestamp argument, never for anything a human reads as a
// real time.
let _wfClock = 1_000;
const _now = () => (_wfClock += 1);
const _isoNow = () => "1970-01-01T00:00:00.000Z";

// ─── The plugin-root fallback path prefix (this repo's own convention: a
// consumer gets the installed-cache CLAUDE_PLUGIN_ROOT; developing the plugin
// inside the marketplace repo itself falls back to the marketplace-relative
// path). Every sibling script + dimensions.md is resolved through this so the
// workflow is portable to any consumer repo, not just this marketplace. ────
const PLUGIN_ROOT_EXPR = "${CLAUDE_PLUGIN_ROOT:-plugins/ravenclaude-core}";
const SCRIPTS_DIR = `${PLUGIN_ROOT_EXPR}/skills/repo-review/scripts`;
const DIMENSIONS_MD = `${PLUGIN_ROOT_EXPR}/skills/repo-review/reference/dimensions.md`;

// ─── The 8 review dimensions ───────────────────────────────────────────────
// Names must match the section headers dimensions.md's sibling author uses.
// dead-code-simplification is the one dimension that stays single-model even
// when cross-model is enabled for the others (per the effort-tier ladder).
// ci-cd-actions-security is new (GitHub Actions / CI-gate specific findings,
// distinct from the generic `security` dimension) — it is NOT in
// HIGH_TIER_DIMENSIONS (narrower file scope than the core 4) and IS
// cross-model-eligible (not in SINGLE_MODEL_ONLY_DIMENSIONS), since subtle
// CI/CD attack vectors benefit from a second model's read the same way
// `security` does.
const ALL_DIMENSIONS = [
  "correctness",
  "security",
  "concurrency",
  "resource-leaks",
  "performance",
  "error-handling",
  "ci-cd-actions-security",
  "dead-code-simplification",
];
const HIGH_TIER_DIMENSIONS = ["correctness", "security", "concurrency", "resource-leaks"];
const SINGLE_MODEL_ONLY_DIMENSIONS = new Set(["dead-code-simplification"]);

// A run's default model pool when the caller doesn't supply args.models.
// Deliberately 3 distinct backbones so the third-model verifier rule (below)
// can always activate on an unqualified run — a caller-supplied args.models
// under 3 entries correctly narrows what that rule can do.
const DEFAULT_MODEL_POOL = ["claude-opus-4-8", "claude-sonnet-5", "claude-haiku-4-5-20251001"];
// The cheap, fast model used ONLY for the cache-lookup pre-check step (never
// for an actual review/verify/fix pass).
const CACHE_CHECK_MODEL = "claude-haiku-4-5-20251001";

// ─── Effort-tier ladder ─────────────────────────────────────────────────────
// low/medium are REFUSED entirely — see the very first script step below.
// budgetBatches/verifyCap/mergeCap scale with tier depth; every one of them
// is overridable via the matching args.* field (see "Derive run config").
const EFFORT_TIERS = {
  high: {
    dims: HIGH_TIER_DIMENSIONS,
    sampling: "risk-floor sampled",
    budgetBatches: 20,
    verifyCap: 40,
    mergeCap: 150,
    nearDupPolicy: "keep-separate",
  },
  xhigh: {
    dims: ALL_DIMENSIONS,
    sampling: "sampled, wider floor",
    budgetBatches: 40,
    verifyCap: 80,
    mergeCap: 300,
    nearDupPolicy: "keep-separate",
  },
  max: {
    dims: ALL_DIMENSIONS,
    sampling: "sampled, wider floor",
    budgetBatches: 80,
    verifyCap: 160,
    mergeCap: 600,
    nearDupPolicy: "keep-separate",
  },
  ultra: {
    dims: ALL_DIMENSIONS,
    sampling: "fullest, still hard-capped",
    budgetBatches: 160,
    verifyCap: 320,
    mergeCap: 1200,
    nearDupPolicy: "judge",
  },
};

// ─── Schemas ────────────────────────────────────────────────────────────────
const MAP_RECEIPT_SCHEMA = {
  type: "object",
  required: ["plan_path", "batch_ids", "coverage"],
  properties: {
    plan_path: { type: "string" },
    batch_ids: { type: "array", items: { type: "string" } },
    coverage: {
      type: "object",
      properties: {
        batches_planned: { type: "integer" },
        batches_budgeted: { type: "integer" },
        files_covered: { type: "integer" },
        files_deferred: { type: "integer" },
        deferred_reason: { type: "string" },
        top_deferred_dirs: { type: "array", items: { type: "string" } },
      },
    },
  },
};

const ESTIMATE_SCHEMA = {
  type: "object",
  required: ["estimate_summary"],
  properties: { estimate_summary: { type: "string" } },
};

// The cheap pre-check step's own return shape (NOT the on-disk shard shape).
const CACHE_CHECK_SCHEMA = {
  type: "object",
  required: ["allCached", "count", "files"],
  properties: {
    allCached: { type: "boolean" },
    count: { type: "integer" },
    files: { type: "array", items: { type: "string" } },
  },
};

// A review agent's own findings receipt — never the finding bodies.
const REVIEW_RECEIPT_SCHEMA = {
  type: "object",
  required: ["artifact", "count"],
  properties: {
    artifact: { type: "string" },
    count: { type: "integer" },
  },
};

const MERGE_RECEIPT_SCHEMA = {
  type: "object",
  required: ["artifact", "survivors_count", "over_cap_count"],
  properties: {
    artifact: { type: "string" },
    survivors_count: { type: "integer" },
    over_cap_count: { type: "integer" },
  },
};

const VERIFY_ENUM_SCHEMA = {
  type: "object",
  required: ["findings"],
  properties: {
    findings: {
      type: "array",
      items: {
        type: "object",
        required: ["id", "file", "severity"],
        properties: {
          id: { type: "string" },
          file: { type: "string" },
          severity: { type: "string" },
          source_models: { type: "array", items: { type: "string" } },
        },
      },
    },
  },
};

// A single verdict — CONFIRMED must name triggering inputs/state AND quote the
// line; REFUTED must quote the disproving line/guard and must never refute
// for being merely speculative when the state depended on is realistic (this
// repo's own house rule, restated verbatim in every verify agent's prompt).
const VERDICT_SCHEMA = {
  type: "object",
  required: ["id", "verdict", "evidence"],
  properties: {
    id: { type: "string" },
    verdict: { enum: ["CONFIRMED", "PLAUSIBLE", "REFUTED"] },
    evidence: { type: "string" },
    fixable_in_place: { type: "boolean" },
  },
};

const VERIFY_FILE_SCHEMA = {
  type: "object",
  required: ["file", "verdicts"],
  properties: {
    file: { type: "string" },
    verdicts: { type: "array", items: VERDICT_SCHEMA },
  },
};

// Documented on-disk shape a fix agent writes to <fix-receipts-dir>/<file>.json
// (this is what fix_summary.py expects to read back — it is NEVER passed as a
// `schema:` option itself, since it is a FILE the agent writes, not the
// agent's own final structured-output return value).
const FIX_RECEIPT_SCHEMA = {
  type: "object",
  required: ["file", "applied", "skipped"],
  properties: {
    file: { type: "string" },
    applied: {
      type: "array",
      items: {
        type: "object",
        required: ["id", "summary"],
        properties: { id: { type: "string" }, summary: { type: "string" } },
      },
    },
    skipped: {
      type: "array",
      items: {
        type: "object",
        required: ["id", "reason"],
        properties: { id: { type: "string" }, reason: { type: "string" } },
      },
    },
  },
};

// The fix agent's own returned structured output (a receipt about the receipt
// it just wrote — counts only, never finding bodies).
const FIX_AGENT_RESULT_SCHEMA = {
  type: "object",
  required: ["file", "applied_count", "skipped_count"],
  properties: {
    file: { type: "string" },
    applied_count: { type: "integer" },
    skipped_count: { type: "integer" },
  },
};

const FIX_SUMMARY_SCHEMA = {
  type: "object",
  required: ["summary_path", "patch_path", "stat_path"],
  properties: {
    summary_path: { type: "string" },
    patch_path: { type: "string" },
    stat_path: { type: "string" },
  },
};

const DOD_RESULT_SCHEMA = {
  type: "object",
  required: ["ran", "passed", "output_tail"],
  properties: {
    ran: { type: "boolean" },
    passed: { type: ["boolean", "null"] },
    output_tail: { type: "string" },
  },
};

// ─── Pure helpers (no Date.now()/Math.random() anywhere below) ────────────

function joinPath(base, ...rest) {
  let b = String(base).replace(/\/+$/, "");
  if (b === "" || b === ".") b = ".";
  const tail = rest
    .map((p) => String(p).replace(/^\/+|\/+$/g, ""))
    .filter(Boolean)
    .join("/");
  if (b === ".") return tail;
  return `${b}/${tail}`;
}

function modelTag(model) {
  const tag = String(model)
    .replace(/^claude-/, "")
    .replace(/[^a-zA-Z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 32);
  return tag || "model";
}

function sanitizeForPath(p) {
  return String(p)
    .replace(/[^a-zA-Z0-9._-]+/g, "_")
    .slice(0, 180);
}

// ─── Caller-input validation (command-injection + path-traversal fixes) ──
// Several args.* fields below are caller-controlled and later interpolated
// verbatim into literal shell-command text that an agent() call instructs a
// subagent to run via Bash ("Run this exact command..."). This workflow has
// no fs/shell APIs and therefore no shell-quoting primitive available to
// it, so the only defense is a strict allow-list regex per field, checked
// ONCE at the point the value is first derived from `args` — every
// downstream interpolation (Map/Merge/Fix phases) inherits the guarantee.
// A value that fails validation causes an immediate, explicit refusal
// (never silent stripping/sanitizing) via the same top-level
// `return { error }` shape the effort-tier refusal below uses.
const SAFE_PATH_RE = /^[A-Za-z0-9._\-/~]+$/;
const SAFE_PATHSPEC_RE = /^[A-Za-z0-9._\-/~:@,*?[\]^]+$/;
// A run id becomes a joinPath() SEGMENT under .ravenclaude/runs/<runId>/ —
// joinPath() only strips leading/trailing slashes per segment, it never
// rejects/strips ".." — so this charset additionally excludes "/" outright
// (an id can never introduce a new path segment, traversal or otherwise).
const SAFE_RUN_ID_RE = /^[A-Za-z0-9_-]+$/;
function isSafeShellArg(value, pattern) {
  return typeof value === "string" && pattern.test(value);
}

// Which of the run's configured models a given dimension actually uses.
// dead-code-simplification is single-model even when cross-model is on.
function resolveModelsForDimension(dim, models) {
  if (SINGLE_MODEL_ONLY_DIMENSIONS.has(dim)) return models.slice(0, 1);
  return models;
}

// How many distinct models per dimension the effort tier + crossModel flag
// resolve to. high is always M=1 (no cross-model). xhigh is M=1 unless
// args.crossModel is true (then M=2). max/ultra default to M=2 (cross-model
// ON by default per the ladder); an explicit args.crossModel === false drops
// max back to M=1 (a documented caller override — ultra's ladder row has no
// such conditional, so it always resolves to 2 regardless).
function resolveModelCount(tier, crossModelActive) {
  if (tier === "high") return 1;
  if (tier === "xhigh") return crossModelActive ? 2 : 1;
  if (tier === "max" || tier === "ultra") return crossModelActive ? 2 : 1;
  return 1;
}

// Build the run's effective model pool: args.models when the caller supplied
// one, else the workflow's own default pool — sliced/cycled to `count`.
function resolveModels(count, argsModels) {
  const supplied = Array.isArray(argsModels) && argsModels.length ? argsModels.slice() : null;
  const pool = supplied || DEFAULT_MODEL_POOL.slice();
  if (pool.length >= count) return pool.slice(0, count);
  const out = pool.slice();
  let i = 0;
  while (out.length < count) {
    out.push(pool[i % pool.length]);
    i += 1;
  }
  return out;
}

// pickVerifier(models, sourceModels) — the THIRD-MODEL VERIFIER RULE, exactly
// as specified: when a file's surviving findings were sourced from 2 distinct
// source_models, the verify agent's model should be a THIRD model tag
// distinct from both, IF the caller's configured model list has 3+ entries;
// otherwise use whichever configured model is NOT source_models[0].
// `models` here is the run's EFFECTIVE configured model list (args.models
// when the caller supplied one, else this workflow's own default pool) — a
// caller-supplied list under 3 entries correctly falls through to the
// "not source_models[0]" branch below, exactly as the caller intended.
function pickVerifier(models, sourceModels) {
  const pool = Array.isArray(models) ? models : [];
  const sources = Array.isArray(sourceModels) ? Array.from(new Set(sourceModels)) : [];
  if (sources.length >= 2 && pool.length >= 3) {
    const third = pool.find((m) => !sources.includes(m));
    if (third) return third;
  }
  const notFirst = pool.find((m) => m !== sources[0]);
  if (notFirst) return notFirst;
  return pool[0] || sources[0] || null;
}

// ─── Step 0: args parsing + the mandatory low/medium refusal ─────────────
// This MUST be the workflow's very first step — return an error object, do
// NOT proceed, before any phase()/agent() call of any kind.
const EFFORT =
  args && typeof args === "object" && typeof args.effort === "string" ? args.effort.trim() : "";

if (EFFORT === "low" || EFFORT === "medium") {
  return {
    error:
      `repo-sweep refuses effort tier '${EFFORT || "(empty)"}'. The minimum supported tier is ` +
      `'high' (4 dimensions, single model, risk-floor sampling). Pass args.effort as one of: ` +
      `high, xhigh, max, ultra.`,
  };
}
if (!EFFORT_TIERS[EFFORT]) {
  return {
    error:
      `repo-sweep requires args.effort to be one of: high, xhigh, max, ultra. Got: ` +
      `${JSON.stringify(args && args.effort)}.`,
  };
}

// ─── Derive run config (all pure, deterministic — no clock/random) ───────
const tierCfg = EFFORT_TIERS[EFFORT];

const REPO_PATH =
  args && typeof args === "object" && typeof args.repoPath === "string" && args.repoPath.trim()
    ? args.repoPath.trim()
    : ".";
if (!isSafeShellArg(REPO_PATH, SAFE_PATH_RE)) {
  return {
    error:
      `repo-sweep refuses args.repoPath = ${JSON.stringify(args && args.repoPath)} — it contains ` +
      `characters not allowed in a shell-interpolated path (must match ${SAFE_PATH_RE}). This guards ` +
      `against command injection into the "Run this exact command" instructions this workflow issues ` +
      `(--repo-root is interpolated verbatim into the Map/Fix-phase commands).`,
  };
}

const RUN_ID =
  args && typeof args === "object" && typeof args.runId === "string" && args.runId.trim()
    ? args.runId.trim()
    : `repo-sweep-${_now()}`;
if (!isSafeShellArg(RUN_ID, SAFE_RUN_ID_RE)) {
  return {
    error:
      `repo-sweep refuses args.runId = ${JSON.stringify(args && args.runId)} — run ids must match ` +
      `${SAFE_RUN_ID_RE} (letters, digits, "_", "-" only — no "/", no "..", no shell metacharacters). ` +
      `joinPath() only strips leading/trailing slashes per segment and never rejects ".." — an ` +
      `unvalidated runId could make RUN_DIR (and every path derived from it) escape the intended ` +
      `.ravenclaude/runs/<runId>/ sandbox.`,
  };
}

const RUN_DIR = joinPath(REPO_PATH, ".ravenclaude/runs", RUN_ID);
const FINDINGS_DIR = joinPath(RUN_DIR, "findings");
const PLAN_PATH = joinPath(RUN_DIR, "review-plan.json");
const CACHE_DIR = joinPath(REPO_PATH, ".ravenclaude/repo-review-cache");

const crossModelRequested = !!(args && args.crossModel === true);
// See resolveModelCount's comment for the per-tier default/override rules.
let crossModelActive;
if (EFFORT === "high") {
  crossModelActive = false;
} else if (EFFORT === "xhigh") {
  crossModelActive = crossModelRequested;
} else {
  crossModelActive = !(args && args.crossModel === false);
}

const modelCount = resolveModelCount(EFFORT, crossModelActive);
const models = resolveModels(modelCount, args && args.models);
const activeDimensions = tierCfg.dims;

const VERIFY_CAP =
  args && typeof args.verifyCap === "number" && args.verifyCap > 0
    ? args.verifyCap
    : tierCfg.verifyCap;
const FIX_CAP = args && typeof args.fixCap === "number" && args.fixCap > 0 ? args.fixCap : 25;
const MERGE_CAP =
  args && typeof args.mergeCap === "number" && args.mergeCap > 0 ? args.mergeCap : tierCfg.mergeCap;
const NEAR_DUP_POLICY =
  args && typeof args.nearDupPolicy === "string" && args.nearDupPolicy.trim()
    ? args.nearDupPolicy.trim()
    : tierCfg.nearDupPolicy;
// Enum check, not a regex allow-list — this value flows verbatim into
// findings_merge.py's --near-dup-policy flag, whose argparse `choices` is
// exactly ["keep-separate", "judge"] (scripts/findings_merge.py). Anything
// else is refused rather than passed through and left for argparse to
// reject (which would still be a shell-injection risk before argparse ever
// gets to see it).
const ALLOWED_NEAR_DUP_POLICIES = ["keep-separate", "judge"];
if (!ALLOWED_NEAR_DUP_POLICIES.includes(NEAR_DUP_POLICY)) {
  return {
    error:
      `repo-sweep refuses args.nearDupPolicy = ${JSON.stringify(args && args.nearDupPolicy)} — must be ` +
      `one of: ${ALLOWED_NEAR_DUP_POLICIES.join(", ")} (matches findings_merge.py's --near-dup-policy ` +
      `choices).`,
  };
}
const PER_AGENT_TOKENS =
  args && typeof args.perAgentTokens === "number" && args.perAgentTokens > 0
    ? args.perAgentTokens
    : 50000;
const BUDGET_BATCHES =
  args && typeof args.budgetBatches === "number" && args.budgetBatches > 0
    ? args.budgetBatches
    : tierCfg.budgetBatches;

log(
  `repo-sweep: effort=${EFFORT} dims=${activeDimensions.length} models/dim(max)=${modelCount} ` +
    `crossModel=${crossModelActive} sampling="${tierCfg.sampling}" runDir=${RUN_DIR}`,
);

// ─── Phase 1: Map ──────────────────────────────────────────────────────────
phase("Map");
const ONLY_VALUE = args && typeof args.only === "string" ? args.only.trim() : "";
if (ONLY_VALUE && !isSafeShellArg(ONLY_VALUE, SAFE_PATHSPEC_RE)) {
  return {
    error:
      `repo-sweep refuses args.only = ${JSON.stringify(args.only)} — it contains characters not ` +
      `allowed in a shell-interpolated --only value (must match ${SAFE_PATHSPEC_RE}).`,
  };
}
const onlyFlag = ONLY_VALUE ? ` --only ${ONLY_VALUE}` : "";

const SINCE_VALUE = args && typeof args.since === "string" ? args.since.trim() : "";
if (SINCE_VALUE && !isSafeShellArg(SINCE_VALUE, SAFE_PATHSPEC_RE)) {
  return {
    error:
      `repo-sweep refuses args.since = ${JSON.stringify(args.since)} — it contains characters not ` +
      `allowed in a shell-interpolated --since value (must match ${SAFE_PATHSPEC_RE}).`,
  };
}
const sinceFlag = SINCE_VALUE ? ` --since ${SINCE_VALUE}` : "";

const mapReceipt = await agent(
  [
    `Run this exact command (the shell expands ${PLUGIN_ROOT_EXPR} to the installed plugin root):`,
    `python3 ${SCRIPTS_DIR}/repo_map.py --repo-root ${REPO_PATH} --out ${PLAN_PATH} ` +
      `--per-agent-tokens ${PER_AGENT_TOKENS} --budget-batches ${BUDGET_BATCHES}${onlyFlag}${sinceFlag}`,
    `Then read ${PLAN_PATH} (JSON — the review-plan). Return ONLY a COMPACT structured receipt —`,
    `do NOT include the full "batches" array or any file lists in your response:`,
    `{plan_path: "${PLAN_PATH}", batch_ids: [<every batches[].id from the plan, as strings, in the plan's own order>], coverage: <the plan's top-level "coverage" object, verbatim>}`,
  ].join("\n"),
  { label: "map:repo-map", phase: "Map", schema: MAP_RECEIPT_SCHEMA },
);

if (!mapReceipt || !Array.isArray(mapReceipt.batch_ids) || mapReceipt.batch_ids.length === 0) {
  return {
    error: "Map phase failed — repo_map.py did not return a usable review plan (no batches).",
  };
}
log(
  `Map: ${mapReceipt.batch_ids.length} batch(es) planned. coverage=${JSON.stringify(mapReceipt.coverage || {})}`,
);

// Optional, best-effort cardinality log — never blocks the sweep on failure.
const estimate = await agent(
  [
    `Run this exact command and capture its stdout JSON:`,
    `python3 ${SCRIPTS_DIR}/estimate_cost.py --plan ${PLAN_PATH} --effort-tier ${EFFORT}` +
      `${crossModelActive ? " --cross-model" : ""} --agent-budget ${BUDGET_BATCHES} ` +
      `--verify-cap ${VERIFY_CAP} --fix-cap ${FIX_CAP}`,
    `Return ONLY structured output: {estimate_summary: "<one short line summarizing the cardinality estimate the tool reported>"}.`,
  ].join("\n"),
  { label: "map:estimate-cost", phase: "Map", schema: ESTIMATE_SCHEMA },
).catch(() => null);
if (estimate && estimate.estimate_summary)
  log(`Cardinality estimate: ${estimate.estimate_summary}`);

// ─── Phase 2: Review ────────────────────────────────────────────────────────
// Cardinality-bounding structure (deliberate, per the spec):
//   pipeline(dimensions, d => parallel(models.map(m => () => parallel(batchIds.map(b => () => agent(...))))))
// Dimensions run SEQUENTIALLY (pipeline, one dimension at a time); within a
// dimension, models x batches run in PARALLEL. This caps the LIVE concurrent
// agent count at models x batches, never dimensions x models x batches, and
// means an interrupted run still yields whole COMPLETED dimensions.
phase("Review");

// One (dimension, model, batch) triple's full pipeline: a cheap cache-check
// step first (replays a full cache hit with ZERO real review agents), then —
// only when the batch is not a full hit — the real review agent.
async function reviewBatch(dim, model, batchId) {
  const tag = modelTag(model);
  const shardPath = joinPath(FINDINGS_DIR, `${dim}.${tag}.${batchId}.json`);

  const cacheResult = await agent(
    [
      `You are the cache-check step for one repo-review batch. Do NOT review anything yourself.`,
      `1. Read ${PLAN_PATH} (JSON) and find the batch whose id is "${batchId}" in its "batches" array. Collect that batch's "files" list.`,
      `2. For EVERY file in that list, run:`,
      `   python3 ${SCRIPTS_DIR}/review_cache.py lookup --cache-dir ${CACHE_DIR} --repo-root ${REPO_PATH} --file <file> --dimension ${dim} --model ${model}`,
      `   Each call prints a JSON entry or the literal string "null".`,
      `3. If EVERY file returned a non-null entry (a full cache hit for the whole batch):`,
      `   - Merge the cached findings from every entry into ONE JSON array.`,
      `   - Write that array to ${shardPath} (create parent directories as needed).`,
      `   - Return {allCached: true, count: <total findings written>, files: [<the batch's file list>]}.`,
      `4. Otherwise (any miss): do NOT write anything, do NOT review. Return {allCached: false, count: 0, files: [<the batch's file list>]}.`,
      `Structured output only. Never include finding bodies in your final text response.`,
    ].join("\n"),
    {
      label: `cache:${dim}:${tag}:${batchId}`,
      phase: "Review",
      schema: CACHE_CHECK_SCHEMA,
      model: CACHE_CHECK_MODEL,
    },
  ).catch(() => null);

  if (cacheResult && cacheResult.allCached) {
    log(
      `review:${dim}:${tag}:${batchId} — full cache hit (${cacheResult.count} findings replayed, 0 review agents dispatched)`,
    );
    return {
      dimension: dim,
      model,
      batchId,
      artifact: shardPath,
      count: cacheResult.count || 0,
      cached: true,
    };
  }

  const batchFiles = cacheResult && Array.isArray(cacheResult.files) ? cacheResult.files : null;
  const label = `review:${dim}:${tag}:${batchId}`;

  const reviewResult = await agent(
    [
      `You are a repo-review agent — dimension "${dim}", batch "${batchId}", model tag "${tag}".`,
      `Repo root: ${REPO_PATH}`,
      batchFiles
        ? `This batch's files (already resolved): ${JSON.stringify(batchFiles)}`
        : `Read ${PLAN_PATH} and find the batch with id "${batchId}" in its "batches" array to get its file list.`,
      ``,
      `1. Read every file in this batch in full.`,
      `2. Also read the OTHER batches' "modules" fields in ${PLAN_PATH} (not just your own batch's) so you can reason about likely callers/callees living outside your batch — say so EXPLICITLY in a finding whenever you rely on out-of-batch context.`,
      `3. Read dimension "${dim}"'s prompt section from ${DIMENSIONS_MD} and use it VERBATIM as your review instructions for this pass.`,
      `4. Write your findings as a JSON array to ${shardPath} (create parent directories as needed). Each finding needs at minimum: id, file, line (or range), dimension:"${dim}", severity, description, source_model:"${model}".`,
      `5. For each file you actually reviewed, call:`,
      `   python3 ${SCRIPTS_DIR}/review_cache.py store --cache-dir ${CACHE_DIR} --repo-root ${REPO_PATH} --file <file> --dimension ${dim} --model ${model} --findings-file <that file's findings — slice from ${shardPath} if per-file slicing isn't practical> --timestamp ${_now()}`,
      `6. Return ONLY structured output: {artifact: "${shardPath}", count: <number of findings written>}. Never include finding bodies in your final text response.`,
    ].join("\n"),
    { label, phase: "Review", schema: REVIEW_RECEIPT_SCHEMA, model },
  ).catch((e) => {
    log(`${label}: agent errored — ${e && e.message ? e.message : e}`);
    return null;
  });

  if (!reviewResult) {
    log(`${label}: no usable result — treating as 0 findings for this triple.`);
    return {
      dimension: dim,
      model,
      batchId,
      artifact: shardPath,
      count: 0,
      cached: false,
      failed: true,
    };
  }
  return {
    dimension: dim,
    model,
    batchId,
    artifact: reviewResult.artifact || shardPath,
    count: reviewResult.count || 0,
    cached: false,
  };
}

const batchIds = mapReceipt.batch_ids;

const reviewByDimension = await pipeline(activeDimensions, async (dim) => {
  const dimModels = resolveModelsForDimension(dim, models);
  // Dedup at the dispatch site (not inside resolveModels()). resolveModels()
  // pads a caller-supplied args.models list shorter than the tier's
  // required model count by CYCLING through it, which can produce literal
  // duplicate entries (e.g. args.models:['claude-sonnet-5'] at a 2-model
  // tier yields ['claude-sonnet-5','claude-sonnet-5']). Without this dedup,
  // a duplicated model string would fan out into two CONCURRENT thunks both
  // calling reviewBatch(dim, model, batchId) for the same (dim, model,
  // batchId) triple — both computing the identical shardPath and writing it
  // with no coordination, so whichever write lands second silently
  // overwrites the first with no error signal. Deduping here (rather than
  // changing resolveModels' general "pad to N" contract) keeps that
  // contract intact for any other caller while guaranteeing at most one
  // thunk — and one write — per distinct model.
  const uniqueDimModels = Array.from(new Set(dimModels));
  if (uniqueDimModels.length < dimModels.length) {
    log(
      `Review: dimension "${dim}" — resolveModels() padded to ${dimModels.length} model slot(s) but ` +
        `only ${uniqueDimModels.length} are distinct; deduping at dispatch to avoid a concurrent ` +
        `duplicate-write race on the same shardPath.`,
    );
  }
  log(
    `Review: dimension "${dim}" starting — ${uniqueDimModels.length} model(s) x ${batchIds.length} batch(es)`,
  );
  const perModel = await parallel(
    uniqueDimModels.map(
      (model) => () => parallel(batchIds.map((batchId) => () => reviewBatch(dim, model, batchId))),
    ),
  );
  const shards = perModel.flat().filter(Boolean);
  const totalFindings = shards.reduce((sum, s) => sum + (s.count || 0), 0);
  const cachedCount = shards.filter((s) => s.cached).length;
  log(
    `Review: dimension "${dim}" complete — ${shards.length} shard(s), ${totalFindings} finding(s), ` +
      `${cachedCount} fully cache-replayed`,
  );
  return { dimension: dim, shards };
});

// ─── Phase 3: Merge ─────────────────────────────────────────────────────────
phase("Merge");
const MERGED_PATH = joinPath(RUN_DIR, "merged.json");

const mergeReceipt = await agent(
  [
    `Run this exact command:`,
    `python3 ${SCRIPTS_DIR}/findings_merge.py --in ${FINDINGS_DIR} --out ${MERGED_PATH} --cap ${MERGE_CAP} --near-dup-policy ${NEAR_DUP_POLICY}`,
    `Then read ${MERGED_PATH} (JSON). Return ONLY structured output: {artifact: "${MERGED_PATH}", survivors_count: <survivors.length>, over_cap_count: <over_cap.length>}. Never include finding bodies.`,
  ].join("\n"),
  { label: "merge:findings-merge", phase: "Merge", schema: MERGE_RECEIPT_SCHEMA },
);

if (!mergeReceipt || !mergeReceipt.artifact) {
  return { error: "Merge phase failed — findings_merge.py did not return a usable receipt." };
}
log(
  `Merge: ${mergeReceipt.survivors_count} survivor(s), ${mergeReceipt.over_cap_count} over cap=${MERGE_CAP} ` +
    `(near-dup policy: ${NEAR_DUP_POLICY})`,
);

// ─── Phase 4: Verify ────────────────────────────────────────────────────────
// One verify agent per FILE with surviving findings (never per finding),
// batching that file's findings into one verify call.
phase("Verify");

const SEVERITY_RANK = { critical: 0, high: 1, medium: 2, low: 3 };

let verifyResults = [];
let unverifiedBeyondCap = [];

if (mergeReceipt.survivors_count > 0) {
  const enumResult = await agent(
    [
      `Read ${mergeReceipt.artifact} (the merged findings JSON — it has a "survivors" array).`,
      `For EVERY survivor, extract: id, file, severity, and source_models (the distinct model(s) that produced/confirmed it — best-effort single-element array if only one attribution field exists).`,
      `Return ONLY structured output: {findings: [{id, file, severity, source_models}, ...]}. Never include a finding's description/body — ids and metadata only.`,
    ].join("\n"),
    { label: "verify:enumerate", phase: "Verify", schema: VERIFY_ENUM_SCHEMA },
  );

  const allSurvivorFindings =
    enumResult && Array.isArray(enumResult.findings) ? enumResult.findings : [];
  const sortedBySeverity = allSurvivorFindings
    .slice()
    .sort((a, b) => (SEVERITY_RANK[a.severity] ?? 9) - (SEVERITY_RANK[b.severity] ?? 9));

  const toVerify = sortedBySeverity.slice(0, VERIFY_CAP);
  unverifiedBeyondCap = sortedBySeverity.slice(VERIFY_CAP).map((f) => ({
    id: f.id,
    file: f.file,
    severity: f.severity,
    status: "unverified",
    reason: `beyond verifyCap=${VERIFY_CAP} — reported but never auto-fixed`,
  }));
  if (unverifiedBeyondCap.length) {
    log(
      `Verify: ${unverifiedBeyondCap.length} finding(s) beyond verifyCap=${VERIFY_CAP} — marked unverified, never auto-fixed.`,
    );
  }

  const byFile = new Map();
  for (const f of toVerify) {
    if (!byFile.has(f.file)) byFile.set(f.file, []);
    byFile.get(f.file).push(f);
  }
  const filesToVerify = Array.from(byFile.entries());
  log(
    `Verify: dispatching ${filesToVerify.length} verify agent(s), one per file with a to-verify finding.`,
  );

  verifyResults = await parallel(
    filesToVerify.map(([file, findings]) => () => {
      const sourceModels = Array.from(
        new Set(findings.flatMap((f) => (Array.isArray(f.source_models) ? f.source_models : []))),
      );
      const verifierModel = pickVerifier(models, sourceModels);
      const ids = findings.map((f) => f.id);
      return agent(
        [
          `You are a verify agent for exactly one file: "${file}".`,
          `Read the surviving findings with ids ${JSON.stringify(ids)} from ${mergeReceipt.artifact} — their full bodies (claim, quoted line, dimension, etc).`,
          `Read the actual source file "${file}" at repo root ${REPO_PATH}, and its enclosing function/callers when a claim depends on them.`,
          `For EACH finding id, return a verdict:`,
          `- CONFIRMED: name the triggering inputs/state AND quote the exact line that shows the bug.`,
          `- PLAUSIBLE: a real risk you could not fully confirm the triggering conditions for.`,
          `- REFUTED: quote the line/guard that disproves it. Do NOT refute for being merely speculative when the state the finding depends on is realistic — that is this repo's own house rule.`,
          `Also set fixable_in_place: true only if a minimal, single-file, non-signature-breaking fix is plausible.`,
          `Return ONLY structured output: {file: "${file}", verdicts: [{id, verdict, evidence, fixable_in_place}]}. Never restate whole finding bodies beyond what evidence requires.`,
        ].join("\n"),
        {
          label: `verify:${file}`,
          phase: "Verify",
          schema: VERIFY_FILE_SCHEMA,
          model: verifierModel,
        },
      ).catch((e) => {
        log(`verify:${file}: agent errored — ${e && e.message ? e.message : e}`);
        return null;
      });
    }),
  );
} else {
  log("Verify: 0 survivors from Merge — nothing to verify.");
}

// ─── Phase 5: Fix ───────────────────────────────────────────────────────────
// Gated behind args.autofix === true (default false — never fix without
// opt-in). CONFIRMED && fixable_in_place findings only; toVerify's own cap
// already excludes unverifiedBeyondCap items from ever reaching a verdict,
// so they are structurally never eligible here — no extra guard needed.
let fixSummaryPath = null;
let fixPatchPath = null;
let filesSkippedOverCap = [];

if (args && args.autofix === true) {
  phase("Fix");

  const confirmedFixable = [];
  for (const vr of verifyResults) {
    if (!vr) continue;
    for (const v of vr.verdicts || []) {
      if (v.verdict === "CONFIRMED" && v.fixable_in_place) {
        confirmedFixable.push({ file: vr.file, id: v.id });
      }
    }
  }

  if (confirmedFixable.length === 0) {
    log("Fix: no CONFIRMED + fixable_in_place findings — nothing to fix.");
  } else {
    // Pre-fix snapshot — never commits/stages/pushes anything.
    await agent(
      [
        `Run these two commands inside the repo at ${REPO_PATH} (ignore a nonzero exit from the first — a clean tree may have nothing to stash):`,
        `git stash create > ${joinPath(RUN_DIR, "pre-fix-stash.txt")}`,
        `git diff HEAD > ${joinPath(RUN_DIR, "pre-fix.patch")}`,
        `Report success/failure only. Do NOT commit, stage, or push anything.`,
      ].join("\n"),
      { label: "fix:snapshot", phase: "Fix" },
    );

    const byFileFix = new Map();
    for (const item of confirmedFixable) {
      if (!byFileFix.has(item.file)) byFileFix.set(item.file, []);
      byFileFix.get(item.file).push(item.id);
    }
    const allFixFiles = Array.from(byFileFix.entries());
    const fixFilesInCap = allFixFiles.slice(0, FIX_CAP);
    const fixFilesOverCap = allFixFiles.slice(FIX_CAP);
    filesSkippedOverCap = fixFilesOverCap.map(([file, ids]) => ({
      file,
      finding_ids: ids,
      reason: `skipped_over_cap — args.fixCap=${FIX_CAP}`,
    }));
    if (filesSkippedOverCap.length) {
      log(
        `Fix: ${filesSkippedOverCap.length} file(s) beyond fixCap=${FIX_CAP} — reported as skipped_over_cap, never silently dropped.`,
      );
    }

    const fixReceiptsDir = joinPath(RUN_DIR, "fix-receipts");

    const fixAgentResults = await parallel(
      fixFilesInCap.map(([file, ids]) => () => {
        const receiptPath = joinPath(fixReceiptsDir, `${sanitizeForPath(file)}.json`);
        return agent(
          [
            `You are a fix agent for exactly ONE file: "${file}". Never touch any other file.`,
            `Apply ONLY the CONFIRMED findings with ids ${JSON.stringify(ids)} — read their full bodies from ${mergeReceipt.artifact}.`,
            `Rules: minimal diff, do NOT reformat unrelated code, do NOT touch any other file, do NOT change public signatures.`,
            `If a fix would require touching a second file, SKIP that finding instead — do not reach outside "${file}" — and record why in "skipped".`,
            `Write a fix-receipt JSON to ${receiptPath} matching exactly: {file: "${file}", applied: [{id, summary}], skipped: [{id, reason}]}.`,
            `Return ONLY structured output: {file: "${file}", applied_count: <n>, skipped_count: <n>}.`,
          ].join("\n"),
          { label: `fix:${file}`, phase: "Fix", schema: FIX_AGENT_RESULT_SCHEMA },
        ).catch((e) => {
          log(`fix:${file}: agent errored — ${e && e.message ? e.message : e}`);
          return null;
        });
      }),
    );
    const appliedTotal = fixAgentResults
      .filter(Boolean)
      .reduce((s, r) => s + (r.applied_count || 0), 0);
    log(`Fix: ${fixFilesInCap.length} file(s) fixed, ${appliedTotal} finding(s) applied.`);

    const summaryMdPath = joinPath(RUN_DIR, "fix-summary.md");
    const patchPath = joinPath(RUN_DIR, "fix.patch");
    const statPath = joinPath(RUN_DIR, "fix-stat.json");

    const summaryReceipt = await agent(
      [
        `Run this exact command:`,
        `python3 ${SCRIPTS_DIR}/fix_summary.py --merged ${mergeReceipt.artifact} --fix-receipts-dir ${fixReceiptsDir} --out-summary ${summaryMdPath} --out-patch ${patchPath} --out-stat ${statPath} --repo-root ${REPO_PATH}`,
        `Return ONLY structured output: {summary_path: "${summaryMdPath}", patch_path: "${patchPath}", stat_path: "${statPath}"}.`,
      ].join("\n"),
      { label: "fix:summarize", phase: "Fix", schema: FIX_SUMMARY_SCHEMA },
    ).catch(() => null);

    fixSummaryPath = summaryReceipt ? summaryReceipt.summary_path : summaryMdPath;
    fixPatchPath = summaryReceipt ? summaryReceipt.patch_path : patchPath;

    // definition-of-done gate, IF the repo defines one — report only, NEVER
    // auto-revert on failure (loud, not a silent revert; matches this repo's
    // own documented dod-gate.sh posture). The tree is left dirty on purpose.
    const dodReceipt = await agent(
      [
        `Check whether ${joinPath(REPO_PATH, ".ravenclaude/comfort-posture.yaml")} exists and defines a top-level "definition_of_done" block with a "cmd" field.`,
        `If it does NOT: return {ran: false, passed: null, output_tail: ""}.`,
        `If it DOES: run that exact command inside ${REPO_PATH}, capture its exit code and the last ~40 lines of combined output.`,
        `Do NOT revert, stash, or discard the fix changes regardless of the result — report only. Do NOT commit, stage, or push.`,
        `Return ONLY structured output: {ran: <bool>, passed: <bool|null>, output_tail: "<last lines, truncated>"}.`,
      ].join("\n"),
      { label: "fix:definition-of-done", phase: "Fix", schema: DOD_RESULT_SCHEMA },
    ).catch(() => null);
    if (dodReceipt && dodReceipt.ran) {
      log(
        `Fix: definition_of_done ${dodReceipt.passed ? "PASSED" : "FAILED"} — reported only, tree left dirty for human review.`,
      );
    }
  }
} else {
  log("Fix: skipped — args.autofix !== true (autofix defaults to false).");
}

// ─── Phase 6: Report ────────────────────────────────────────────────────────
phase("Report");

const counts = { confirmed: 0, plausible: 0, refuted: 0, unverified: unverifiedBeyondCap.length };
for (const vr of verifyResults) {
  if (!vr) continue;
  for (const v of vr.verdicts || []) {
    if (v.verdict === "CONFIRMED") counts.confirmed += 1;
    else if (v.verdict === "PLAUSIBLE") counts.plausible += 1;
    else if (v.verdict === "REFUTED") counts.refuted += 1;
  }
}

const coverage = mapReceipt.coverage || {};
const filesDeferred = typeof coverage.files_deferred === "number" ? coverage.files_deferred : 0;
const filesCovered = typeof coverage.files_covered === "number" ? coverage.files_covered : null;

// ─── The coverage-honesty contract ─────────────────────────────────────────
// This repo's own recorded failure class is "silent partial coverage" — a
// repo-review report that hides its own coverage gap is exactly that defect.
// So this line is NEVER omitted whenever files_deferred > 0, and it is
// computed strictly from the real Map-phase coverage numbers (never
// estimated, never glossed) — see the coverage object read back verbatim in
// Phase 1 above.
let coverageLine;
if (filesDeferred > 0 && filesCovered != null) {
  const total = filesCovered + filesDeferred;
  const pct = total > 0 ? Math.round((filesCovered / total) * 100) : 0;
  coverageLine =
    `Reviewed ${filesCovered} of ${total} reviewable files (${pct}%); ${filesDeferred} lowest-risk ` +
    `files were not reviewed at this budget — re-run with a higher effort tier or --full for complete coverage.`;
} else if (filesDeferred > 0) {
  coverageLine =
    `${filesDeferred} file(s) were deferred at this budget (exact reviewable-file total unavailable ` +
    `from the Map receipt) — re-run with a higher effort tier or --full for complete coverage.`;
} else {
  coverageLine = "Every reviewable file at this budget was covered — no files were deferred.";
}

const reportMdPath = joinPath(RUN_DIR, "report.md");
const reportBody = [
  coverageLine,
  "",
  `# repo-sweep report — ${RUN_ID}`,
  "",
  `Effort tier: ${EFFORT}${crossModelActive ? " (cross-model)" : ""} — sampling: ${tierCfg.sampling}`,
  `Dimensions reviewed: ${activeDimensions.join(", ")}`,
  `Batches: ${batchIds.length}`,
  "",
  "## Verify results",
  `- CONFIRMED: ${counts.confirmed}`,
  `- PLAUSIBLE: ${counts.plausible}`,
  `- REFUTED: ${counts.refuted}`,
  `- Unverified (beyond verifyCap=${VERIFY_CAP}): ${counts.unverified}`,
  "",
  args && args.autofix === true
    ? [
        "## Fix",
        `- Patch: ${fixPatchPath || "(none — nothing fixable)"}`,
        `- Fix summary: ${fixSummaryPath || "(none)"}`,
        `- Files skipped over fixCap=${FIX_CAP}: ${filesSkippedOverCap.length}`,
      ].join("\n")
    : "## Fix\n- autofix was not enabled for this run (args.autofix !== true).",
  "",
  "## Artifacts",
  `- Findings shards: ${FINDINGS_DIR}/`,
  `- Merged findings: ${mergeReceipt.artifact}`,
  `- Plan: ${PLAN_PATH}`,
].join("\n");

await agent(
  `Write the following Markdown VERBATIM to ${reportMdPath} (create parent directories as needed). Content follows between the markers exactly as given, without alteration:\n---BEGIN---\n${reportBody}\n---END---`,
  { label: "report:write", phase: "Report" },
).catch(() => null);

log(`Report written to ${reportMdPath}`);

return {
  coverage,
  counts,
  findings_artifact: mergeReceipt.artifact,
  patch: args && args.autofix === true && fixPatchPath ? fixPatchPath : null,
  fix_summary: args && args.autofix === true && fixSummaryPath ? fixSummaryPath : null,
  report_md: reportMdPath,
};

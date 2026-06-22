// ─── Dynamic workflow (Claude Code official feature — research preview) ──────────
// Docs: https://code.claude.com/docs/en/workflows · authoritative guidance:
//   plugins/ravenclaude-core/knowledge/dynamic-workflows.md
// Saved under .claude/workflows/ → invoked as `/rc-deep-research` (or via the
// `ultracode` keyword); reads the global `args` (the research question).
// Renamed from `deep-research` on 2026-06-04: Claude Code now ships a BUNDLED
// `/deep-research`, and bundled-vs-project name precedence is undocumented, so we
// renamed to avoid the collision rather than depend on an unverified shadow rule.
// Runtime caps: ≤16 concurrent agents, 1,000 total/run, no mid-run user input, no
// direct fs/shell from the script (agents do the IO), resumable in-session.
export const meta = {
  name: "rc-deep-research",
  description:
    "Deep research harness — fan-out web searches, fetch sources, adversarially verify claims, synthesize a cited report. Includes an inline substrate adapter that reads .ravenclaude/run-config.json once at startup; when enabled:false (the default) all agent() calls are byte-identical to the pre-port baseline (Gate 51).",
  whenToUse:
    "When the user wants a deep, multi-source, fact-checked research report on any topic. BEFORE invoking, check if the question is specific enough to research directly — if underspecified (e.g., 'what car to buy' without budget/use-case/region), ask 2-3 clarifying questions to narrow scope. Then pass the refined question as args, weaving the answers in.",
  phases: [
    { title: "Scope", detail: "Decompose question (from args) into 5 search angles" },
    { title: "Search", detail: "5 parallel WebSearch agents, one per angle" },
    { title: "Fetch", detail: "URL-dedup, fetch top 15 sources, extract falsifiable claims" },
    {
      title: "Verify",
      detail: "Adversarial per-claim verification (vote count per sourceQuality)",
    },
    { title: "Synthesize", detail: "Merge semantic dupes, rank by confidence, cite sources" },
  ],
};

// ─── Resume-safe time source (added 2026-06-10) ───────────────────────────────
// The workflow runtime FORBIDS Date.now() / new Date() — they introduce
// non-determinism that breaks in-session resume, and calling them throws
// ("Date.now() / new Date() are unavailable in workflow scripts"). Before this
// shim the whole workflow crashed at startup (the top-level _runStartedMs +
// per-phase window timing below run unconditionally, even with no runId), so
// EVERY rc-deep-research invocation failed under the current runtime.
//
// We replace the time APIs with a deterministic monotonic counter so the run is
// resume-safe and the eval-stats fields stay structurally valid. CAVEAT: these
// are monotonic ORDINALS, not wall-clock ms — the eval grader's wall-clock
// transcript-bucketing (adaptive-run-classifier Phase 6, deferred) needs a
// separate runtime-legal time source (an agent-returned timestamp, or a base
// time passed via args) before it can bucket real transcript usage by phase.
// That rework is tracked as a follow-up; the research output itself does not
// depend on timing, so interactive runs are unaffected.
let _wfClock = 1_000;
const _now = () => (_wfClock += 1);
const _isoNow = () => "1970-01-01T00:00:00.000Z";

// ─── Substrate adapter (Phase 2 of docs/plans/2026-06-03-adaptive-run-classifier/plan.md) ───
//
// INVARIANT (Gate 51): when runCfg.enabled === false, adapterOpts() returns {}
// (empty object) on every call, so every agent() invocation's effective behaviour
// is identical to the pre-port runtime-generated baseline.
//
// Tier → Claude model mapping (verified 2026-05-31, [verify-at-use] before Phase 6):
//   fast     → claude-haiku-4-5-20251001   (no extended thinking — RM6)
//   balanced → claude-sonnet-4-6           (adaptive thinking available)
//   top      → claude-opus-4-8             (escalate sparingly)
//
// cache_control: {type:"ephemeral", ttl:"1h"} ONLY on verify phases. The 36-min
// baseline run vastly exceeds the 5-min default TTL; eat the 2× write penalty once
// to keep the verify system block warm for the full run (gap-delta C1, A6).
// The classifier prompt is ~800 tokens — below Haiku 4.5's 4,096-token cache
// minimum — so NO cache_control is applied there (pure write penalty, RM1).

const TIER_MODEL = {
  fast: "claude-haiku-4-5-20251001",
  balanced: "claude-sonnet-4-6",
  top: "claude-opus-4-8",
};

// Tiers that support extended/adaptive thinking (Haiku 4.5 does not — RM6).
const THINKING_TIERS = new Set(["balanced", "top"]);

// Phases that get the 1-hour cache_control on their system block.
const LONG_TTL_PHASES = new Set(["verify_default", "verify_judgment"]);

function adapterOpts(phaseName, runCfg) {
  // Gate 51 invariant: disabled → empty opts, byte-identical to baseline.
  if (!runCfg || !runCfg.enabled) return {};

  const tierLabel = (runCfg.tiers && runCfg.tiers[phaseName]) || "balanced";
  const reasoningLabel = (runCfg.reasoning && runCfg.reasoning[phaseName]) || "medium";
  const model = TIER_MODEL[tierLabel] || TIER_MODEL["balanced"];

  const opts = { model };

  // Thinking: emit ONLY for tiers that support it (RM6).
  if (THINKING_TIERS.has(tierLabel) && reasoningLabel !== "low") {
    opts.thinking = { type: "adaptive" };
  }

  // cache_control: 1-hour TTL only for long-running verify phases (gap-delta C1).
  if (LONG_TTL_PHASES.has(phaseName)) {
    opts.cache_control = { type: "ephemeral", ttl: "1h" };
  }

  return opts;
}

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ BEGIN copied block — agent-dispatch-evaluator wrapper (Phase 2)            ║
// ║                                                                           ║
// ║ PROVENANCE: copied (copy-paste, not import — workflow scripts have no      ║
// ║ module resolution) from the single source of truth:                       ║
// ║   plugins/ravenclaude-core/skills/agent-dispatch-evaluator/reference/      ║
// ║     evaluate-dispatch.js                                                   ║
// ║ When the evaluator logic changes (latency threshold, precedence rules,     ║
// ║ TIER_MODEL SKUs), update the reference file and re-copy this block.        ║
// ║ Drift between copies is accepted/intentional — the reference is the spec.  ║
// ║                                                                           ║
// ║ INTEGRATION NOTE: the reference's `TIER_MODEL` is renamed to               ║
// ║ DISPATCH_TIER_MODEL here to avoid a redeclaration clash with this file's   ║
// ║ pre-existing const TIER_MODEL. Values are identical. The rest of the       ║
// ║ copied body is faithful to the reference.                                 ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

// ─── Tier → SKU map (single source of truth; verify-at-use — 2026-05-31) ────────
// Sourced from adaptive-run-classifier/SKILL.md §"Substrate tier table".
// Do NOT re-author the table; copy updates from there.
const DISPATCH_TIER_MODEL = {
  fast: "claude-haiku-4-5-20251001",
  balanced: "claude-sonnet-4-6",
  top: "claude-opus-4-8",
};

// ─── Audit log path template ──────────────────────────────────────────────────
const DISPATCH_EVAL_LOG_DIR = ".ravenclaude/runs/dispatch-eval";

// ─── In-memory latency state (per-session, reset on workflow start) ───────────
const _latency = { window: [], tripped: false };

// ─────────────────────────────────────────────────────────────────────────────
// loadDispatchConfig()
//
// Read .ravenclaude/dispatch-config.json once at workflow start via an agent()
// Read call. Returns a frozen plain object. On any read/parse failure, returns
// the fail-safe default (enabled: false → everything passes through).
//
// INVARIANT: Call this ONCE. Store the result. Do NOT re-call mid-run.
// ─────────────────────────────────────────────────────────────────────────────
async function loadDispatchConfig() {
  const DEFAULTS = {
    schema_version: "1",
    enabled: false,
    mode: "shadow",
    subagent_type_allowlist: ["Explore", "statusline-setup", "claude"],
    downgrade_blocked_types: [],
    latency_circuit_breaker: { median_ms_threshold: 1500, window_size: 20 },
    tribunal_seat_mode: "shadow",
    async_mode: false,
  };

  try {
    const raw = await agent(
      "Read the file .ravenclaude/dispatch-config.json and return its contents verbatim as a JSON string. " +
        "If the file does not exist, return the string 'NOT_FOUND'. " +
        "Return ONLY the raw file contents or NOT_FOUND — no commentary.",
      { label: "load-dispatch-config", _predispatch: "skip" },
    );
    if (!raw || raw.trim() === "NOT_FOUND") return DEFAULTS;
    const cfg = JSON.parse(raw.trim());
    if (cfg.schema_version !== "1") {
      log(`[dispatch-eval] schema_version mismatch (got ${cfg.schema_version}); using defaults.`);
      return DEFAULTS;
    }
    return { ...DEFAULTS, ...cfg };
  } catch (e) {
    log(`[dispatch-eval] loadDispatchConfig error: ${e.message}; using defaults (fail-open).`);
    return DEFAULTS;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// evaluateDispatch({ subagent_type, description, prompt_head, requested_model,
//                    caller_context }, dispatchCfg)
//
// Fires a `claude -p --bare --output-format json --model haiku-4-5` subprocess
// (via an agent() call that asks Claude to shell out — RM7 structural exemption).
// Hard 2s wall-clock timeout. Returns a verdict envelope on success; null on
// timeout / error (caller treats null as pass-through).
//
// The classifier call is intentionally NOT cached (prompt < 1,024 tokens — below
// Haiku-4.5's 4,096-token cache minimum; setting cache_control would incur the
// write penalty with zero chance of a cache hit — see SKILL.md §NO cache_control).
// ─────────────────────────────────────────────────────────────────────────────
async function evaluateDispatch(
  { subagent_type, description, prompt_head, requested_model, caller_context },
  dispatchCfg,
) {
  const t0 = _now();
  const classifierPrompt = JSON.stringify({
    subagent_type,
    description: (description || "").slice(0, 200),
    prompt_head: (prompt_head || "").slice(0, 1800), // ~500 tokens
    requested_model,
    caller_context,
  });

  // The classifier runs as a subprocess spawned by the agent — NOT as a direct
  // agent() dispatch. This keeps it structurally exempt from runaway-brake.sh
  // (subprocesses spawned inside an agent() call never enter the tool-call stream).
  const subprocPrompt =
    `You are a dispatch-routing shell runner. Execute this exact command and return its raw stdout:\n\n` +
    `timeout 2 claude -p --bare --output-format json --model claude-haiku-4-5-20251001 ` +
    `'You are a dispatch evaluator. Given this dispatch envelope, return ONLY a JSON object with fields: ` +
    `verdict ("keep"|"upgrade"|"downgrade"), suggested_tier ("fast"|"balanced"|"top"), ` +
    `confidence ("low"|"medium"|"high"), rationale (one sentence). ` +
    `Envelope: ${classifierPrompt.replace(/'/g, '"')}'` +
    `\n\nReturn the raw JSON stdout only. If the command times out or fails, return the string "FAIL".`;

  try {
    const raw = await agent(subprocPrompt, {
      label: "dispatch-evaluator-classifier",
      _predispatch: "skip",
    });
    const latency = _now() - t0;
    _trackLatency(latency, dispatchCfg);

    if (!raw || raw.trim() === "FAIL") return null;
    const verdict = JSON.parse(raw.trim());
    // Validate minimum shape
    if (!verdict.verdict || !verdict.suggested_tier || !verdict.confidence) return null;
    return { ...verdict, latency_ms: latency };
  } catch (e) {
    return null; // fail-open
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// evaluatedAgent(prompt, opts, dispatchCfg)
//
// Drop-in replacement for agent(prompt, opts). Applies the dispatch evaluator
// around every agent() call. Returns the agent() result unchanged.
//
// Implements (in order):
//   1. enabled:false short-circuit (regression floor — byte-identical to no-wrapper)
//   2. latency circuit-breaker trip (session pass-through)
//   3. _predispatch:'skip' carve-out
//   4. subagent_type allowlist carve-out
//   5. evaluateDispatch call (fail-open on null return)
//   6. Verdict application per precedence rules (SKILL.md §Precedence rules)
//   7. Audit log (JSONL append via agent Read/Write)
// ─────────────────────────────────────────────────────────────────────────────
async function evaluatedAgent(prompt, opts = {}, dispatchCfg) {
  // Guard: if dispatchCfg was never loaded, pass through safely.
  if (!dispatchCfg) return agent(prompt, opts);

  // ① Regression floor: enabled:false → byte-identical to calling agent() directly.
  if (!dispatchCfg.enabled) return agent(prompt, opts);

  // ② Latency circuit-breaker trip: session-wide pass-through.
  if (_latency.tripped) return agent(prompt, opts);

  // ③ Per-call skip marker.
  if (opts._predispatch === "skip") return agent(prompt, opts);

  // ④ Allowlist carve-out.
  const subagentType = opts.subagent_type || opts.agentType || opts.label || "unknown";
  const allowlist = dispatchCfg.subagent_type_allowlist || [];
  if (allowlist.some((t) => subagentType.includes(t))) return agent(prompt, opts);

  // ⑤ Evaluate.
  const callerContext = opts._run_config_phase
    ? "workflow"
    : opts.caller_context === "tribunal_seat"
      ? "tribunal_seat"
      : "toplevel";

  const envelope = {
    subagent_type: subagentType,
    description: opts.label || opts.phase || "",
    prompt_head: typeof prompt === "string" ? prompt.slice(0, 1800) : "",
    requested_model: opts.model || DISPATCH_TIER_MODEL.balanced,
    caller_context: callerContext,
  };

  const verdict = await evaluateDispatch(envelope, dispatchCfg);
  const appliedOpts = { ...opts };
  let applied = "skip";

  // ⑥ Verdict application.
  if (verdict && dispatchCfg.mode === "binding" && verdict.confidence !== "low") {
    if (callerContext === "tribunal_seat") {
      // Shadow forever for MVP (RM2). Log only; never mutate.
      applied = "shadow";
    } else if (callerContext === "workflow" && opts._run_config_phase) {
      // Inside a run_config context: downgrade is binding; upgrade is advisory.
      if (verdict.verdict === "downgrade") {
        appliedOpts.model = DISPATCH_TIER_MODEL[verdict.suggested_tier] || appliedOpts.model;
        applied = "binding";
      } else if (verdict.verdict === "upgrade") {
        applied = "advisory"; // log only; keep original model
      } else {
        applied = "keep";
      }
    } else {
      // Top-level or plain workflow: full binding both directions.
      if (verdict.verdict === "downgrade" || verdict.verdict === "upgrade") {
        appliedOpts.model = DISPATCH_TIER_MODEL[verdict.suggested_tier] || appliedOpts.model;
        applied = "binding";
      } else {
        applied = "keep";
      }
    }
  } else if (verdict && dispatchCfg.mode === "shadow") {
    applied = "shadow"; // log the verdict but never mutate opts
  } else if (!verdict) {
    applied = "skip"; // fail-open
  }

  // ⑦ Audit log (fire-and-forget; failure here MUST NOT break the dispatch).
  _appendAuditLog(envelope, verdict, applied, dispatchCfg).catch(() => {});

  return agent(prompt, appliedOpts);
}

// ─── Internal helpers ─────────────────────────────────────────────────────────

function _trackLatency(latencyMs, dispatchCfg) {
  const threshold = dispatchCfg?.latency_circuit_breaker?.median_ms_threshold ?? 1500;
  const windowSize = dispatchCfg?.latency_circuit_breaker?.window_size ?? 20;
  _latency.window.push(latencyMs);
  if (_latency.window.length > windowSize) _latency.window.shift();

  const sorted = [..._latency.window].sort((a, b) => a - b);
  const median = sorted[Math.floor(sorted.length / 2)];
  if (median > threshold && !_latency.tripped) {
    _latency.tripped = true;
    log(
      `[dispatch-eval] LATENCY CIRCUIT-BREAKER TRIPPED: rolling median ${median}ms > ${threshold}ms. ` +
        `Session flipped to pass-through. (Emit evaluator-latency-trip event to hook-events.jsonl via shell.)`,
    );
    // NOTE: Heimdall amber event emission requires _emit_hook_event from _emit-event.sh,
    // which is shell-side only. A workflow cannot source shell functions directly.
    // TODO: Emit via a fire-and-forget agent() call that runs the shell helper:
    //   agent(`Run: source .../hooks/_emit-event.sh && _emit_hook_event evaluator-latency-trip ...`,
    //         { _predispatch: 'skip' })
    // This is marked TODO because the exact shell-sourcing path is substrate-specific.
  }
}

async function _appendAuditLog(envelope, verdict, applied, dispatchCfg) {
  if (!verdict && applied === "skip") return; // nothing to log on clean pass-through
  const sessionId = (typeof args !== "undefined" && args?._sessionId) || "unknown";
  const logPath = `${DISPATCH_EVAL_LOG_DIR}/${sessionId}.jsonl`;
  const line = JSON.stringify({
    ts: _isoNow(),
    subagent_type: envelope.subagent_type,
    description_first40: (envelope.description || "").slice(0, 40),
    requested_model: envelope.requested_model,
    caller_context: envelope.caller_context,
    verdict: verdict?.verdict ?? "passthrough",
    suggested_tier: verdict?.suggested_tier ?? null,
    confidence: verdict?.confidence ?? null,
    rationale_first120: (verdict?.rationale ?? "").slice(0, 120),
    applied,
    latency_ms: verdict?.latency_ms ?? null,
  });

  // Append via a pass-through agent() call (skip marker prevents re-evaluation).
  // In a real adoption, prefer a direct shell `echo '...' >> path` if available.
  await agent(
    `Append the following JSONL line (exactly as given, followed by a newline) to the file ${logPath}. ` +
      `Create the file and any missing parent directories if needed. ` +
      `LINE: ${line}`,
    { label: "dispatch-eval-audit-log", _predispatch: "skip" },
  );
}

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ END copied block — agent-dispatch-evaluator wrapper (Phase 2)              ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

// ─── Schemas (unchanged from baseline) ───────────────────────────────────────
const CLASSIFIER_SCHEMA = {
  type: "object",
  required: ["task_class", "rationale", "schema_version"],
  properties: {
    task_class: {
      type: "string",
      enum: ["research_loop_vendor_docs", "research_loop_contested", "research_loop_general"],
    },
    rationale: { type: "string" },
    schema_version: { type: "string" },
    tiers: { type: "object", additionalProperties: { type: "string" } },
    reasoning: { type: "object", additionalProperties: { type: "string" } },
    knobs: { type: "object" },
    verify_policy: { type: "object", additionalProperties: { type: "integer" } },
    use_specialized_mcp: { type: "boolean" },
    primary_source_host: { type: "string" },
    batch_verify: { type: "boolean" },
  },
};

// Baseline knobs matching the pre-port hardcoded constants (Gate 51 floor).
const BASELINE_KNOBS = {
  votes_per_claim: 3,
  refutations_required: 2,
  max_fetch: 15,
  max_verify_claims: 25,
  angle_count: 5,
};

const BASELINE_VERIFY_POLICY = {
  primary: 3,
  secondary: 3,
  blog: 3,
  forum: 3,
  unreliable: 3,
};

const SCOPE_SCHEMA = {
  type: "object",
  required: ["question", "angles", "summary"],
  properties: {
    question: { type: "string" },
    summary: { type: "string" },
    angles: {
      type: "array",
      minItems: 3,
      maxItems: 6,
      items: {
        type: "object",
        required: ["label", "query"],
        properties: {
          label: { type: "string" },
          query: { type: "string" },
          rationale: { type: "string" },
        },
      },
    },
  },
};
const SEARCH_SCHEMA = {
  type: "object",
  required: ["results"],
  properties: {
    results: {
      type: "array",
      maxItems: 6,
      items: {
        type: "object",
        required: ["url", "title", "relevance"],
        properties: {
          url: { type: "string" },
          title: { type: "string" },
          snippet: { type: "string" },
          relevance: { enum: ["high", "medium", "low"] },
        },
      },
    },
  },
};
const EXTRACT_SCHEMA = {
  type: "object",
  required: ["claims", "sourceQuality"],
  properties: {
    sourceQuality: { enum: ["primary", "secondary", "blog", "forum", "unreliable"] },
    publishDate: { type: "string" },
    claims: {
      type: "array",
      maxItems: 5,
      items: {
        type: "object",
        required: ["claim", "quote", "importance"],
        properties: {
          claim: { type: "string" },
          quote: { type: "string" },
          importance: { enum: ["central", "supporting", "tangential"] },
        },
      },
    },
  },
};
const VERDICT_SCHEMA = {
  type: "object",
  required: ["refuted", "evidence", "confidence"],
  properties: {
    refuted: { type: "boolean" },
    evidence: { type: "string" },
    confidence: { enum: ["high", "medium", "low"] },
    counterSource: { type: "string" },
  },
};
const REPORT_SCHEMA = {
  type: "object",
  required: ["summary", "findings", "caveats"],
  properties: {
    summary: { type: "string" },
    findings: {
      type: "array",
      items: {
        type: "object",
        required: ["claim", "confidence", "sources", "evidence"],
        properties: {
          claim: { type: "string" },
          confidence: { enum: ["high", "medium", "low"] },
          sources: { type: "array", items: { type: "string" } },
          evidence: { type: "string" },
          vote: { type: "string" },
        },
      },
    },
    caveats: { type: "string" },
    openQuestions: { type: "array", items: { type: "string" } },
  },
};

// ─── Preamble: resolve run config (async, frozen into closure) ────────────────
//
// Step 1: attempt to read .ravenclaude/run-config.json via agent() Read tool.
// Step 2: if enabled:true and task_class missing, call the classifier (one Haiku
//         Messages-API-shaped call via agent() with forced schema:).
// Step 3: snapshot result — all subsequent code uses the frozen `runCfg`.
// NO cache_control on classifier (~800 tokens < Haiku 4.5's 4,096-token minimum).

const RC_PATH = ".ravenclaude/run-config.json";
const RC_READ_SCHEMA = {
  type: "object",
  properties: {
    found: { type: "boolean" },
    enabled: { type: "boolean" },
    content: { type: "object" },
  },
  required: ["found"],
};

const rcRead = await agent(
  "Use the Read tool to read the file at path `" +
    RC_PATH +
    "`. " +
    "If the file exists and is valid JSON, set found:true and return the parsed object as content. " +
    "If absent, unreadable, or invalid JSON, set found:false. Do not error.",
  { label: "rc-read", schema: RC_READ_SCHEMA },
);

let runCfg;
if (!rcRead || !rcRead.found || !rcRead.content || rcRead.content.enabled !== true) {
  // Absent, unreadable, or explicitly disabled — Gate 51 baseline.
  runCfg = {
    enabled: false,
    schema_version: "1",
    knobs: BASELINE_KNOBS,
    verify_policy: BASELINE_VERIFY_POLICY,
    use_specialized_mcp: false,
    batch_verify: false,
    rationale: "baseline (enabled:false)",
  };
} else {
  const raw = rcRead.content;
  // If task_class already set, accept as-is. Otherwise run classifier.
  if (raw.task_class) {
    runCfg = {
      ...raw,
      knobs: raw.knobs || BASELINE_KNOBS,
      verify_policy: raw.verify_policy || BASELINE_VERIFY_POLICY,
    };
  } else {
    // Classifier: one Haiku call, forced tool_choice via schema: parameter.
    // Layout: stable system (classify instruction) above breakpoint; volatile
    // question below. No cache_control — prompt is ~800 tokens, below Haiku 4.5
    // minimum of 4,096 (RM1).
    const QUESTION_PRELIM =
      typeof args === "string"
        ? args.trim()
        : args && typeof args === "object" && typeof args.question === "string"
          ? args.question.trim()
          : "";
    const classified = await agent(
      "## Run classifier\n\n" +
        "You are a one-shot classifier for the rc-deep-research workflow. Classify the research question below into one of three task classes:\n\n" +
        "- `research_loop_vendor_docs` — the answer primarily lives in official vendor documentation (e.g. Microsoft Learn, Anthropic docs, AWS docs). Most sources will be primary vendor pages.\n" +
        '- `research_loop_contested` — the question has credible expert disagreement (comparisons, tradeoffs, "X vs Y", policy debates, empirical benchmarks where vendors disagree).\n' +
        "- `research_loop_general` — open-web question: academic, news, practitioner opinion, or multi-domain without a single authoritative vendor source.\n\n" +
        "## Research question\n" +
        QUESTION_PRELIM +
        "\n\n" +
        'Return the task_class, a one-sentence rationale, and schema_version:"1". Structured output only.',
      {
        label: "run-classifier",
        schema: CLASSIFIER_SCHEMA,
        // model pinned to fast tier for this one-shot call (not via adapterOpts —
        // this is a classifier bootstrap call, not a workflow phase).
        model: TIER_MODEL["fast"],
      },
    );

    const taskClass = classified ? classified.task_class : "research_loop_general";
    const rationale = classified
      ? classified.rationale
      : "classifier returned null; defaulting to general";

    // Merge classifier output with raw config; derive tier/knob defaults by task_class.
    const isMicrosoftDocs = taskClass === "research_loop_vendor_docs";
    runCfg = {
      enabled: true,
      schema_version: "1",
      task_class: taskClass,
      rationale,
      tiers: raw.tiers || {
        scope: "balanced",
        search: "fast",
        fetch: "fast",
        verify_default: "fast",
        verify_judgment: "balanced",
        synthesize: "balanced",
      },
      reasoning: raw.reasoning || {
        scope: "medium",
        search: "low",
        fetch: "low",
        verify_default: "low",
        verify_judgment: "high",
        synthesize: "high",
      },
      knobs: raw.knobs || BASELINE_KNOBS,
      verify_policy: raw.verify_policy || BASELINE_VERIFY_POLICY,
      use_specialized_mcp: isMicrosoftDocs,
      primary_source_host: isMicrosoftDocs ? "learn.microsoft.com" : null,
      batch_verify: raw.batch_verify || false,
    };

    // Emit classifier audit (fire-and-forget; no-op on failure).
    try {
      const tsSecs = Math.floor(budget.spent ? budget.spent() : 0);
      await agent(
        "Write the following JSON to `.ravenclaude/runs/run-classifier/run-" +
          tsSecs +
          ".json` using the Write tool. " +
          "Create parent directories if needed. Content:\n\n" +
          JSON.stringify(
            { task_class: taskClass, rationale, tiers: runCfg.tiers, reasoning: runCfg.reasoning },
            null,
            2,
          ),
        { label: "rc-audit-emit" },
      );
    } catch {}
  }
}

// runCfg is now frozen for the rest of the run (Panel-A R1, gap-delta C9).
log(
  "run-config: enabled=" +
    runCfg.enabled +
    " task_class=" +
    (runCfg.task_class || "n/a") +
    " rationale=" +
    (runCfg.rationale || "").slice(0, 80),
);

// ─── Load the dispatch-evaluator config ONCE (Phase 2; default {enabled:false}) ───
// Mirrors the run-config read above: a single agent() Read at startup, frozen for the run.
// With enabled:false (the default / file absent) every evaluatedAgent() call below is
// byte-identical to the unwrapped agent() baseline (Gate 52).
const dispatchCfg = await loadDispatchConfig();
log("dispatch-config: enabled=" + dispatchCfg.enabled + " mode=" + dispatchCfg.mode);

// Derive effective constants from runCfg (or baseline floor).
// votes_per_claim / refutations_required are NOT in the run-config.schema.json
// `knobs` allow-list (additionalProperties:false), so a classifier-emitted envelope
// omits them — fall back to BASELINE_KNOBS rather than dereferencing undefined.
const VOTES_PER_CLAIM =
  runCfg.knobs.votes_per_claim != null
    ? runCfg.knobs.votes_per_claim
    : BASELINE_KNOBS.votes_per_claim;
const REFUTATIONS_REQUIRED =
  runCfg.knobs.refutations_required != null
    ? runCfg.knobs.refutations_required
    : BASELINE_KNOBS.refutations_required;
const MAX_FETCH =
  runCfg.knobs.max_fetch != null ? runCfg.knobs.max_fetch : BASELINE_KNOBS.max_fetch;
const MAX_VERIFY_CLAIMS =
  runCfg.knobs.max_verify_claims != null
    ? runCfg.knobs.max_verify_claims
    : BASELINE_KNOBS.max_verify_claims;

// ─── Phase-timing scaffold (eval-harness wiring, mismatch 3) ──────────────────
// A workflow script CANNOT see per-agent token usage (agent() returns the result,
// not usage — knowledge/dynamic-workflows.md). The grader acquires tokens post-hoc
// from ~/.claude transcripts and buckets them into phases by these wall-clock
// windows. We record start/end ms + an agent count per phase; the grader attributes
// each transcript event to the phase whose [started_ms, ended_ms] contains its ts.
const _runStartedMs = _now();
const _phaseWindows = {}; // phase -> { started_ms, ended_ms, agent_count }
function _phaseStart(p) {
  _phaseWindows[p] = { started_ms: _now(), ended_ms: null, agent_count: 0 };
}
function _phaseEnd(p, agentCount) {
  if (_phaseWindows[p]) {
    _phaseWindows[p].ended_ms = _now();
    if (typeof agentCount === "number") _phaseWindows[p].agent_count = agentCount;
  }
}

// ─── Phase 0: Scope ───────────────────────────────────────────────────────────
phase("Scope");
// Args contract (eval-harness wiring): accept EITHER a plain string (legacy /
// interactive) OR a { question, runId } object. When runId is present the run
// persists its artifacts under .ravenclaude/runs/<runId>/ so an external grader
// (scripts/eval-adaptive-classifier.py) can read them back by a deterministic
// run-id. Absent runId → pre-port behavior (self-named audit dirs, no eval persist).
const QUESTION =
  typeof args === "string"
    ? args.trim()
    : args && typeof args === "object" && typeof args.question === "string"
      ? args.question.trim()
      : "";
const RUN_ID =
  args && typeof args === "object" && typeof args.runId === "string" && args.runId.trim()
    ? args.runId.trim()
    : null;
if (!QUESTION) {
  return {
    error:
      "No research question provided. Pass it as args: Workflow({name: 'rc-deep-research', args: '<question>'}) " +
      "or args: { question: '<question>', runId: '<run-id>' }.",
  };
}

// MCP-first instruction prefix (use_specialized_mcp flag).
const MCP_FETCH_PREFIX =
  runCfg.use_specialized_mcp && runCfg.primary_source_host === "learn.microsoft.com"
    ? "PREFER the `microsoft_docs_search` and `microsoft_docs_fetch` MCP tools over WebFetch for learn.microsoft.com URLs. Use WebFetch only as a fallback when the MCP returns no result.\n\n"
    : "";

_phaseStart("scope");
const scope = await evaluatedAgent(
  "Decompose this research question into complementary search angles.\n\n" +
    "## Question\n" +
    QUESTION +
    "\n\n" +
    "## Task\n" +
    "Generate 5 distinct web search queries that together cover the question from different angles. Pick angles that suit the question's domain. Examples:\n" +
    "- broad/primary  · academic/technical  · recent news  · contrarian/skeptical  · practitioner/implementation\n" +
    "- For medical: anatomy · common causes · serious differentials · authoritative refs · red flags\n" +
    "- For tech: state-of-art · benchmarks · limitations · industry adoption · cost/tradeoffs\n\n" +
    "Make queries specific enough to surface high-signal results. Avoid redundancy.\n" +
    "Return: the question (verbatim or lightly normalized), a 1-2 sentence decomposition strategy, and the angles.\n\nStructured output only.",
  {
    label: "scope",
    schema: SCOPE_SCHEMA,
    _run_config_phase: "scope",
    ...adapterOpts("scope", runCfg),
  },
  dispatchCfg,
);
if (!scope) {
  return { error: "Scope agent returned no result — cannot decompose the research question." };
}
_phaseEnd("scope", 1);
log("Q: " + QUESTION.slice(0, 80) + (QUESTION.length > 80 ? "…" : ""));
log(
  "Decomposed into " +
    scope.angles.length +
    " angles: " +
    scope.angles.map((a) => a.label).join(", "),
);

// ─── Dedup state ──────────────────────────────────────────────────────────────
const normURL = (u) => {
  try {
    const p = new URL(u);
    return (p.hostname.replace(/^www\./, "") + p.pathname.replace(/\/$/, "")).toLowerCase();
  } catch {
    return u.toLowerCase();
  }
};
const seen = new Map();
const dupes = [];
const budgetDropped = [];
const relRank = { high: 0, medium: 1, low: 2 };
let fetchSlots = MAX_FETCH;

// ─── Prompts ──────────────────────────────────────────────────────────────────
const SEARCH_PROMPT = (angle) =>
  "## Web Searcher: " +
  angle.label +
  "\n\n" +
  'Research question: "' +
  QUESTION +
  '"\n\n' +
  "Your angle: **" +
  angle.label +
  "** — " +
  (angle.rationale || "") +
  "\n" +
  "Search query: `" +
  angle.query +
  "`\n\n" +
  "## Task\nUse WebSearch with the query above (or a refined version). Return the top 4-6 most relevant results.\n" +
  "Rank by relevance to the ORIGINAL question, not just the search query. Skip obvious SEO spam/content farms.\n" +
  "Include a short snippet capturing why each result is relevant.\n\nStructured output only.";

const FETCH_PROMPT = (source, angle) =>
  MCP_FETCH_PREFIX +
  "## Source Extractor\n\n" +
  'Research question: "' +
  QUESTION +
  '"\n\n' +
  "Fetch and extract key claims from this source:\n" +
  "**URL:** " +
  source.url +
  "\n**Title:** " +
  source.title +
  "\n**Found via:** " +
  angle +
  " search\n\n" +
  "## Task\n1. Use WebFetch to retrieve the page content.\n" +
  "2. Assess source quality: primary research/institution? secondary reporting? blog/opinion? forum? unreliable?\n" +
  "3. Extract 2-5 FALSIFIABLE claims that bear on the research question. Each claim must:\n" +
  "   - be a concrete, checkable statement (not vague generalities)\n" +
  "   - include a direct quote from the source as support\n" +
  "   - be rated central/supporting/tangential to the research question\n" +
  "4. Note publish date if available.\n\n" +
  'If the fetch fails or the page is irrelevant/paywalled, return claims: [] and sourceQuality: "unreliable".\n\nStructured output only.';

const VERIFY_PROMPT = (claim, v, voteMax) =>
  "## Adversarial Claim Verifier (voter " +
  (v + 1) +
  "/" +
  voteMax +
  ")\n\n" +
  "Be SKEPTICAL. Try to REFUTE this claim. ≥" +
  REFUTATIONS_REQUIRED +
  "/" +
  voteMax +
  " refutations kill it.\n\n" +
  "## Research question\n" +
  QUESTION +
  "\n\n" +
  '## Claim under review\n"' +
  claim.claim +
  '"\n\n' +
  "**Source:** " +
  claim.sourceUrl +
  " (" +
  claim.sourceQuality +
  ")\n" +
  '**Supporting quote:** "' +
  claim.quote +
  '"\n\n' +
  "## Checklist\n" +
  "1. Is the claim actually supported by the quote, or is it an overreach/misread?\n" +
  "2. WebSearch for contradicting evidence — does any credible source dispute or heavily qualify this?\n" +
  "3. Is the source quality sufficient for the claim's strength? (extraordinary claims need primary sources)\n" +
  "4. Is the claim outdated? (check dates — old claims about fast-moving fields are suspect)\n" +
  "5. Is this a marketing claim / press release / cherry-picked benchmark / forum speculation?\n\n" +
  "**refuted=true** if: unsupported by quote / contradicted / low-quality source for strong claim / outdated / marketing fluff.\n" +
  "**refuted=false** ONLY if: claim is well-supported, current, and source quality matches claim strength.\n" +
  "Default to refuted=true if uncertain.\n\nStructured output only. Evidence MUST be specific.";

// ─── Per-claim vote resolver (gap-delta C4 / A4) ──────────────────────────────
//
// Primary: upfront lookup via verify_policy[sourceQuality] (deterministic).
// Optional escalation: if any vote returns confidence:low, fire one additional
// vote at verify_judgment tier.

function resolveVerifyVotes(claim, cfg) {
  const policy = cfg.verify_policy || BASELINE_VERIFY_POLICY;
  return policy[claim.sourceQuality] || VOTES_PER_CLAIM;
}

// ─── Pipeline: search → dedup → fetch+extract ────────────────────────────────
_phaseStart("search");
const searchResults = await pipeline(
  scope.angles,

  (angle) =>
    evaluatedAgent(
      SEARCH_PROMPT(angle),
      {
        label: "search:" + angle.label,
        phase: "Search",
        schema: SEARCH_SCHEMA,
        _run_config_phase: "search",
        ...adapterOpts("search", runCfg),
      },
      dispatchCfg,
    ).then((r) => {
      if (!r) return null;
      log(angle.label + ": " + r.results.length + " results");
      return { angle: angle.label, results: r.results };
    }),

  (searchResult) => {
    const sorted = [...searchResult.results].sort(
      (a, b) => relRank[a.relevance] - relRank[b.relevance],
    );
    const novel = sorted.filter((r) => {
      const key = normURL(r.url);
      if (seen.has(key)) {
        dupes.push({ ...r, angle: searchResult.angle, dupOf: seen.get(key) });
        return false;
      }
      if (fetchSlots <= 0 && relRank[r.relevance] >= 1) {
        budgetDropped.push({ ...r, angle: searchResult.angle });
        return false;
      }
      seen.set(key, { angle: searchResult.angle, title: r.title });
      fetchSlots--;
      return true;
    });
    if (novel.length < searchResult.results.length) {
      log(
        searchResult.angle +
          ": " +
          novel.length +
          " novel (" +
          (searchResult.results.length - novel.length) +
          " filtered)",
      );
    }
    return parallel(
      novel.map((source) => () => {
        let host = "unknown";
        try {
          host = new URL(source.url).hostname.replace(/^www\./, "");
        } catch {}
        return evaluatedAgent(
          FETCH_PROMPT(source, searchResult.angle),
          {
            label: "fetch:" + host,
            phase: "Fetch",
            schema: EXTRACT_SCHEMA,
            _run_config_phase: "fetch",
            ...adapterOpts("fetch", runCfg),
          },
          dispatchCfg,
        )
          .then((ext) => {
            if (!ext) return null;
            return {
              url: source.url,
              title: source.title,
              angle: searchResult.angle,
              sourceQuality: ext.sourceQuality,
              publishDate: ext.publishDate,
              claims: ext.claims.map((c) => ({
                ...c,
                sourceUrl: source.url,
                sourceQuality: ext.sourceQuality,
              })),
            };
          })
          .catch((e) => {
            log("fetch failed: " + source.url + " — " + (e.message || e));
            return {
              url: source.url,
              title: source.title,
              angle: searchResult.angle,
              sourceQuality: "unreliable",
              claims: [],
            };
          });
      }),
    );
  },
);

const allSources = searchResults.flat().filter(Boolean);
_phaseEnd("search", scope.angles.length);
_phaseStart("fetch");
_phaseEnd("fetch", allSources.length);
const allClaims = allSources.flatMap((s) => s.claims);
const impRank = { central: 0, supporting: 1, tangential: 2 };
const qualRank = { primary: 0, secondary: 1, blog: 2, forum: 3, unreliable: 4 };

const rankedClaims = [...allClaims]
  .sort(
    (a, b) =>
      impRank[a.importance] - impRank[b.importance] ||
      qualRank[a.sourceQuality] - qualRank[b.sourceQuality],
  )
  .slice(0, MAX_VERIFY_CLAIMS);

log(
  "Fetched " +
    allSources.length +
    " sources → " +
    allClaims.length +
    " claims → verifying top " +
    rankedClaims.length,
);

if (rankedClaims.length === 0) {
  return {
    question: QUESTION,
    summary:
      "No claims extracted. " +
      allSources.length +
      " sources fetched, all empty/failed. " +
      dupes.length +
      " URL dupes, " +
      budgetDropped.length +
      " budget-dropped.",
    findings: [],
    refuted: [],
    sources: allSources.map((s) => ({ url: s.url, quality: s.sourceQuality })),
    stats: {
      angles: scope.angles.length,
      sources: allSources.length,
      claims: 0,
      dupes: dupes.length,
    },
    run_config: {
      enabled: runCfg.enabled,
      task_class: runCfg.task_class,
      rationale: runCfg.rationale,
    },
  };
}

// ─── Verify: per-claim adversarial (policy-driven vote count + optional escalation) ─
// cache_control {ttl:"1h"} applied via adapterOpts for verify_default and verify_judgment
// (gap-delta C1 / A6 — 36-min run exceeds 5-min default TTL).
phase("Verify");
_phaseStart("verify_default");

// Batch gate (gap-delta C2 / A5): present in schema, default false in MVP.
const USE_BATCH = runCfg.batch_verify && rankedClaims.length >= 10;
if (USE_BATCH) log("batch_verify: enabled for " + rankedClaims.length + " claims");

const claimTierAudit = [];
// Actual count of verify agents dispatched, summed across claims (per-claim vote
// fan-out can differ when verify_policy is non-uniform, and escalation fires one
// extra). The stats below use this instead of `voted.length * VOTES_PER_CLAIM`,
// which assumed a flat fan-out and never counted escalations. Baseline (uniform
// policy, no escalation) yields the identical number, so the eval baseline holds.
let verifyAgentsFired = 0;

const voted = (
  await parallel(
    rankedClaims.map((claim, claimIdx) => () => {
      const voteCount = resolveVerifyVotes(claim, runCfg);
      const verifyPhaseName = "verify_default";
      return parallel(
        Array.from(
          { length: voteCount },
          (_, v) => () =>
            evaluatedAgent(
              VERIFY_PROMPT(claim, v, voteCount),
              {
                label: "v" + v + ":" + claim.claim.slice(0, 40),
                phase: "Verify",
                schema: VERDICT_SCHEMA,
                _run_config_phase: "verify_default",
                ...adapterOpts(verifyPhaseName, runCfg),
              },
              dispatchCfg,
            ),
        ),
      ).then(async (verdicts) => {
        const valid = verdicts.filter(Boolean);
        const refutedCount = valid.filter((v) => v.refuted).length;
        const abstained = voteCount - valid.length;
        let survives = valid.length >= REFUTATIONS_REQUIRED && refutedCount < REFUTATIONS_REQUIRED;

        // Optional escalation: if any voter returned confidence:low, fire one
        // additional vote at verify_judgment tier (gap-delta C4 / A4).
        let escalated = false;
        if (survives && valid.some((v) => v.confidence === "low")) {
          const extra = await evaluatedAgent(
            VERIFY_PROMPT(claim, voteCount, voteCount + 1),
            {
              label: "v_esc:" + claim.claim.slice(0, 40),
              phase: "Verify",
              schema: VERDICT_SCHEMA,
              _run_config_phase: "verify_judgment",
              ...adapterOpts("verify_judgment", runCfg),
            },
            dispatchCfg,
          );
          if (extra) {
            valid.push(extra);
            if (extra.refuted) {
              const newRefuted = valid.filter((v) => v.refuted).length;
              survives = newRefuted < REFUTATIONS_REQUIRED;
            }
            escalated = true;
          }
        }

        const voteStr =
          valid.length -
          valid.filter((v) => v.refuted).length +
          "-" +
          valid.filter((v) => v.refuted).length;
        log(
          '"' +
            claim.claim.slice(0, 50) +
            '…": ' +
            voteStr +
            (abstained > 0 ? " (" + abstained + " abstain)" : "") +
            (escalated ? " [escalated]" : "") +
            " " +
            (survives ? "✓" : "✗"),
        );

        verifyAgentsFired += voteCount + (escalated ? 1 : 0);
        // Per-claim audit row (gap-delta C4 / RM4).
        claimTierAudit.push({
          claim_idx: claimIdx,
          initial_tier: (runCfg.tiers && runCfg.tiers["verify_default"]) || "fast",
          votes_fired: valid.length,
          escalated_to: escalated
            ? (runCfg.tiers && runCfg.tiers["verify_judgment"]) || "balanced"
            : null,
          final_verdict: survives ? "survive" : "killed",
        });

        return {
          ...claim,
          verdicts: valid,
          refutedVotes: valid.filter((v) => v.refuted).length,
          survives,
        };
      });
    }),
  )
).filter(Boolean);

// Emit claim tier audit (fire-and-forget via agent write, no-op on error).
if (runCfg.enabled && claimTierAudit.length > 0) {
  try {
    const runId = "run-" + Math.floor(budget.spent ? budget.spent() : 0);
    await agent(
      "Write the following JSONL content (one JSON object per line) to `.ravenclaude/runs/" +
        runId +
        "/claim_tier_audit.jsonl` using the Write tool. Create parent directories if needed. Content:\n\n" +
        claimTierAudit.map((r) => JSON.stringify(r)).join("\n"),
      { label: "claim-audit-emit" },
    );
  } catch {}
}

_phaseEnd("verify_default", verifyAgentsFired);
const confirmed = voted.filter((c) => c.survives);
const killed = voted.filter((c) => !c.survives);
log(
  "Verify done: " +
    voted.length +
    " claims → " +
    confirmed.length +
    " confirmed, " +
    killed.length +
    " killed",
);

if (confirmed.length === 0) {
  return {
    question: QUESTION,
    summary:
      "All " +
      voted.length +
      " claims refuted by adversarial verification. Research inconclusive — sources may be low-quality or claims overstated.",
    findings: [],
    refuted: killed.map((c) => ({
      claim: c.claim,
      vote: c.verdicts.length - c.refutedVotes + "-" + c.refutedVotes,
      source: c.sourceUrl,
    })),
    sources: allSources.map((s) => ({
      url: s.url,
      quality: s.sourceQuality,
      claimCount: s.claims.length,
    })),
    stats: {
      angles: scope.angles.length,
      sources: allSources.length,
      claims: allClaims.length,
      verified: voted.length,
      confirmed: 0,
      killed: killed.length,
    },
    run_config: {
      enabled: runCfg.enabled,
      task_class: runCfg.task_class,
      rationale: runCfg.rationale,
    },
  };
}

// ─── Synthesize ───────────────────────────────────────────────────────────────
phase("Synthesize");
_phaseStart("synthesize");
const confRank = { high: 0, medium: 1, low: 2 };
const block = confirmed
  .map((c, i) => {
    const best = c.verdicts
      .filter((v) => !v.refuted)
      .sort((a, b) => confRank[a.confidence] - confRank[b.confidence])[0];
    return (
      "### [" +
      i +
      "] " +
      c.claim +
      "\n" +
      "Vote: " +
      (c.verdicts.length - c.refutedVotes) +
      "-" +
      c.refutedVotes +
      " · Source: " +
      c.sourceUrl +
      " (" +
      c.sourceQuality +
      ")\n" +
      'Quote: "' +
      c.quote +
      '"\nVerifier evidence (' +
      best.confidence +
      "): " +
      best.evidence +
      "\n"
    );
  })
  .join("\n");

const killedBlock =
  killed.length > 0
    ? "\n## Refuted claims (for transparency)\n" +
      killed
        .map(
          (c) =>
            '- "' +
            c.claim +
            '" (' +
            c.sourceUrl +
            ", vote " +
            (c.verdicts.length - c.refutedVotes) +
            "-" +
            c.refutedVotes +
            ")",
        )
        .join("\n")
    : "";

const report = await evaluatedAgent(
  "## Synthesis: research report\n\n" +
    "**Question:** " +
    QUESTION +
    "\n\n" +
    confirmed.length +
    " claims survived " +
    VOTES_PER_CLAIM +
    "-vote adversarial verification. Merge semantic duplicates and synthesize.\n\n" +
    "## Confirmed claims\n" +
    block +
    "\n" +
    killedBlock +
    "\n\n" +
    "## Instructions\n" +
    "1. Identify claims that say the same thing — merge them, combine their sources.\n" +
    "2. Group related claims into coherent findings. Each finding should directly address the research question.\n" +
    "3. Assign confidence per finding: high (multiple primary sources, unanimous votes), medium (secondary sources or split votes), low (single source or blog-quality).\n" +
    "4. Write a 3-5 sentence executive summary answering the research question.\n" +
    "5. Note caveats: what's uncertain, what sources were weak, what time-sensitivity applies.\n" +
    "6. List 2-4 open questions that emerged but weren't answered.\n\nStructured output only.",
  {
    label: "synthesize",
    schema: REPORT_SCHEMA,
    _run_config_phase: "synthesize",
    ...adapterOpts("synthesize", runCfg),
  },
  dispatchCfg,
);
_phaseEnd("synthesize", 1);

if (!report) {
  return {
    question: QUESTION,
    summary:
      "Synthesis step was skipped or failed — returning " +
      confirmed.length +
      " verified claims unmerged.",
    findings: [],
    confirmed: confirmed.map((c) => ({
      claim: c.claim,
      source: c.sourceUrl,
      quote: c.quote,
      vote: c.verdicts.length - c.refutedVotes + "-" + c.refutedVotes,
    })),
    refuted: killed.map((c) => ({
      claim: c.claim,
      vote: c.verdicts.length - c.refutedVotes + "-" + c.refutedVotes,
      source: c.sourceUrl,
    })),
    sources: allSources.map((s) => ({
      url: s.url,
      quality: s.sourceQuality,
      claimCount: s.claims.length,
    })),
    stats: {
      angles: scope.angles.length,
      sources: allSources.length,
      claims: allClaims.length,
      verified: voted.length,
      confirmed: confirmed.length,
      killed: killed.length,
      afterSynthesis: 0,
    },
    run_config: {
      enabled: runCfg.enabled,
      task_class: runCfg.task_class,
      rationale: runCfg.rationale,
    },
  };
}

// ─── Eval-harness persistence (mismatch 2) ────────────────────────────────────
// When invoked with a runId (the eval harness path), persist the two artifacts the
// grader reads back: structured-output.json (the SOP JSON incl. the stats contract)
// and synthesis.md (the synthesize-phase report text). Uses the rc-audit-emit
// agent()-write pattern (the script has no direct fs access). Fire-and-forget:
// a persistence failure must never corrupt the run's returned result.
if (RUN_ID) {
  const _evalStats = {
    subagent_tokens: 0,
    agent_count: 1 + scope.angles.length + allSources.length + verifyAgentsFired + 1,
    duration_ms: _now() - _runStartedMs,
    confirmed_claim_count: confirmed.length,
    run_window: { started_ms: _runStartedMs, ended_ms: _now() },
    per_phase: _phaseWindows,
  };
  const _evalSO = {
    question: QUESTION,
    run_id: RUN_ID,
    run_config: {
      enabled: runCfg.enabled,
      task_class: runCfg.task_class,
      rationale: runCfg.rationale,
      tiers: runCfg.tiers,
      use_specialized_mcp: runCfg.use_specialized_mcp,
      batch_verify: runCfg.batch_verify,
    },
    stats: _evalStats,
    findings: report.findings,
  };
  const _synMd =
    "# Synthesis — " +
    QUESTION +
    "\n\n## Summary\n\n" +
    (report.summary || "") +
    "\n\n## Findings\n\n" +
    report.findings
      .map(
        (f, i) =>
          "### [" +
          i +
          "] " +
          f.claim +
          "\n\n- confidence: " +
          f.confidence +
          "\n- sources: " +
          (f.sources || []).join(", ") +
          "\n\n" +
          (f.evidence || ""),
      )
      .join("\n\n") +
    "\n\n## Caveats\n\n" +
    (report.caveats || "");
  try {
    await agent(
      "Write the following JSON to `.ravenclaude/runs/" +
        RUN_ID +
        "/structured-output.json` using the Write tool. Create parent directories if needed. Content:\n\n" +
        JSON.stringify(_evalSO, null, 2),
      { label: "eval-persist-so", _predispatch: "skip" },
    );
  } catch {}
  try {
    await agent(
      "Write the following Markdown to `.ravenclaude/runs/" +
        RUN_ID +
        "/synthesis.md` using the Write tool. Create parent directories if needed. Content:\n\n" +
        _synMd,
      { label: "eval-persist-syn", _predispatch: "skip" },
    );
  } catch {}
}

return {
  question: QUESTION,
  ...report,
  refuted: killed.map((c) => ({
    claim: c.claim,
    vote: c.verdicts.length - c.refutedVotes + "-" + c.refutedVotes,
    source: c.sourceUrl,
  })),
  sources: allSources.map((s) => ({
    url: s.url,
    quality: s.sourceQuality,
    angle: s.angle,
    claimCount: s.claims.length,
  })),
  stats: {
    // ── Grader contract (scripts/eval-adaptive-classifier.py collect_metrics) ──
    // subagent_tokens is a PLACEHOLDER (0): the workflow cannot see per-agent token
    // usage; the grader fills it from ~/.claude transcripts, bucketed by per_phase.
    subagent_tokens: 0,
    agent_count: 1 + scope.angles.length + allSources.length + verifyAgentsFired + 1,
    duration_ms: _now() - _runStartedMs,
    confirmed_claim_count: confirmed.length,
    run_window: { started_ms: _runStartedMs, ended_ms: _now() },
    per_phase: _phaseWindows,
    // ── Legacy human-readable fields (kept for the /workflows drill-in + existing readers) ──
    angles: scope.angles.length,
    sourcesFetched: allSources.length,
    claimsExtracted: allClaims.length,
    claimsVerified: voted.length,
    confirmed: confirmed.length,
    killed: killed.length,
    afterSynthesis: report.findings.length,
    urlDupes: dupes.length,
    budgetDropped: budgetDropped.length,
    agentCalls: 1 + scope.angles.length + allSources.length + verifyAgentsFired + 1,
  },
  run_config: {
    enabled: runCfg.enabled,
    task_class: runCfg.task_class,
    rationale: runCfg.rationale,
    tiers: runCfg.tiers,
    use_specialized_mcp: runCfg.use_specialized_mcp,
    batch_verify: runCfg.batch_verify,
  },
};

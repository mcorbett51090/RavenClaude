// evaluate-dispatch.js — Agent-Dispatch Evaluator reference snippet
// Phase 2 of docs/plans/2026-06-03-agent-dispatch-evaluator/plan.md
//
// USAGE (workflow scripts cannot use `import`):
//   1. Copy this entire file's contents to the TOP of your workflow script.
//   2. Call `loadDispatchConfig()` ONCE at workflow start; store as `dispatchCfg`.
//      NEVER re-call it mid-run (RM3 mid-run-toggle invariant).
//   3. Replace every `agent(prompt, opts)` call with `evaluatedAgent(prompt, opts, dispatchCfg)`.
//
// CRITICAL — RM7 subprocess exemption:
//   The classifier fires as `claude -p --bare` spawned by an agent() call that asks
//   Claude to shell out. It NEVER fires as a direct agent() dispatch — doing so would
//   enter the tool-call stream and count against runaway-brake.sh's max_total/max_consecutive.
//
// Invariants:
//   - Fail-open: any timeout / error / disabled config → pass-through (original opts unchanged).
//   - Mid-run freeze: dispatchCfg is the closure snapshot; it NEVER re-reads during a run.
//   - Tribunal seats: verdicts are ALWAYS shadow (logged only); opts.model is NEVER mutated.
//   - No cache_control: evaluator prompt is <1,024 tokens → below Haiku-4.5 minimum (4,096).

// ─── Tier → SKU map (single source of truth; verify-at-use — 2026-05-31) ────────
// Sourced from adaptive-run-classifier/SKILL.md §"Substrate tier table".
// Do NOT re-author the table; copy updates from there.
const TIER_MODEL = {
  fast: "claude-haiku-4-5-20251001",
  balanced: "claude-sonnet-4-6",
  top: "claude-opus-4-7",
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
  const t0 = Date.now();
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
    const latency = Date.now() - t0;
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
    requested_model: opts.model || TIER_MODEL.balanced,
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
        appliedOpts.model = TIER_MODEL[verdict.suggested_tier] || appliedOpts.model;
        applied = "binding";
      } else if (verdict.verdict === "upgrade") {
        applied = "advisory"; // log only; keep original model
      } else {
        applied = "keep";
      }
    } else {
      // Top-level or plain workflow: full binding both directions.
      if (verdict.verdict === "downgrade" || verdict.verdict === "upgrade") {
        appliedOpts.model = TIER_MODEL[verdict.suggested_tier] || appliedOpts.model;
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
    ts: new Date().toISOString(),
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

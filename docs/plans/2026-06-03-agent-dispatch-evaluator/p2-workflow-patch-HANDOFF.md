# Phase-2 workflow integration — HANDOFF patch for `.claude/workflows/rc-deep-research.js`

> **Why this file exists:** the background worktree agent that built Phase 2 is **structurally blocked from writing any file under `.claude/workflows/`** (Edit, Write, and Bash-redirect are all denied by the harness in the background-agent context — a self-modification guard on the session's own workflow scripts; every other path in the repo is writable, proven by the Gate-52 edits to `scripts/` + `plugins/`). Everything else in Phase 2 (Gate 52 checker, gate fixture test, audit-gates wiring, version cascade, CLAUDE.md milestone) is committed. **The main interactive session must apply the four edits below to `.claude/workflows/rc-deep-research.js`** — then Gate 52 goes green (it currently reports the wrapper block as missing, by design).
>
> After applying: run `node scripts/check-dispatch-evaluator-floor.mjs .claude/workflows/rc-deep-research.js` (must pass), `bash scripts/audit-gates.sh --check 52`, `bash scripts/audit-gates.sh --check 51`, and `npx --yes prettier --write .claude/workflows/rc-deep-research.js`.

## Edit 1 — insert the copied wrapper block after `adapterOpts()`

Find the end of `function adapterOpts(...)` (the `return opts; }` that closes it, immediately followed by `// ─── Schemas (unchanged from baseline) ───`). Insert the entire block below **between** them — i.e. after the `}` that closes `adapterOpts`, before the `// ─── Schemas` comment.

```js

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

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ END copied block — agent-dispatch-evaluator wrapper (Phase 2)              ║
// ╚═══════════════════════════════════════════════════════════════════════════╝
```

## Edit 2 — load `dispatchCfg` once, right after `runCfg` is frozen

Find the `runCfg is now frozen for the rest of the run` block (the `log("run-config: ...")` call near the end of the run-config preamble). Immediately **after** that `log(...)` statement and before `// Derive effective constants from runCfg`, insert:

```js

// ─── Load the dispatch-evaluator config ONCE (Phase 2; default {enabled:false}) ───
// Mirrors the run-config read above: a single agent() Read at startup, frozen for the run.
// With enabled:false (the default / file absent) every evaluatedAgent() call below is
// byte-identical to the unwrapped agent() baseline (Gate 52).
const dispatchCfg = await loadDispatchConfig();
log("dispatch-config: enabled=" + dispatchCfg.enabled + " mode=" + dispatchCfg.mode);
```

## Edit 3 — swap the 6 phase dispatch sites to `evaluatedAgent(..., dispatchCfg)`

Each site already threads `...adapterOpts("<phase>", runCfg)` in its opts. Add a `_run_config_phase: "<phase>"` marker to opts and change `agent(` → `evaluatedAgent(` with `, dispatchCfg` as the third arg. The 4 infrastructure calls (`label: "rc-read"`, `"run-classifier"`, `"rc-audit-emit"`, `"claim-audit-emit"`) stay **plain `agent()`** — do NOT wrap them.

| Phase | Locate by | Change |
|---|---|---|
| **scope** | `const scope = await agent(` … `{ label: "scope", schema: SCOPE_SCHEMA, ...adapterOpts("scope", runCfg) }` | `await evaluatedAgent(` …, opts `{ label: "scope", schema: SCOPE_SCHEMA, _run_config_phase: "scope", ...adapterOpts("scope", runCfg) }`, `, dispatchCfg)` |
| **search** | inside `pipeline(...)`: `agent(SEARCH_PROMPT(angle), { label: "search:" + angle.label, phase: "Search", schema: SEARCH_SCHEMA, ...adapterOpts("search", runCfg) })` | `evaluatedAgent(SEARCH_PROMPT(angle), { ..., _run_config_phase: "search", ...adapterOpts("search", runCfg) }, dispatchCfg)` |
| **fetch** | `agent(FETCH_PROMPT(source, searchResult.angle), { label: "fetch:" + host, phase: "Fetch", schema: EXTRACT_SCHEMA, ...adapterOpts("fetch", runCfg) })` | `evaluatedAgent(..., { ..., _run_config_phase: "fetch", ...adapterOpts("fetch", runCfg) }, dispatchCfg)` |
| **verify_default** | `agent(VERIFY_PROMPT(claim, v, voteCount), { label: "v" + v + ...", phase: "Verify", schema: VERDICT_SCHEMA, ...adapterOpts(verifyPhaseName, runCfg) })` | `evaluatedAgent(..., { ..., _run_config_phase: "verify_default", ...adapterOpts(verifyPhaseName, runCfg) }, dispatchCfg)` |
| **verify_judgment** | the escalation `const extra = await agent(VERIFY_PROMPT(claim, voteCount, voteCount + 1), { label: "v_esc:" + ..., phase: "Verify", schema: VERDICT_SCHEMA, ...adapterOpts("verify_judgment", runCfg) })` | `await evaluatedAgent(..., { ..., _run_config_phase: "verify_judgment", ...adapterOpts("verify_judgment", runCfg) }, dispatchCfg)` |
| **synthesize** | `const report = await agent(` … `{ label: "synthesize", schema: REPORT_SCHEMA, ...adapterOpts("synthesize", runCfg) }` | `await evaluatedAgent(` …, `{ label: "synthesize", schema: REPORT_SCHEMA, _run_config_phase: "synthesize", ...adapterOpts("synthesize", runCfg) }, dispatchCfg)` |

(The `_run_config_phase` marker is what makes `evaluatedAgent` classify these as `caller_context: "workflow"` and apply the run_config precedence rule — downgrade binding, upgrade advisory — instead of treating them as top-level dispatches.)

## Edit 4 — none

The 4 infrastructure calls need no change: by staying plain `agent()` they are never evaluated (SKILL carve-out contract). The reference's internal `loadDispatchConfig`/`evaluateDispatch`/`_appendAuditLog` agent() calls already carry `_predispatch:'skip'`.

## After applying — validation

```sh
node scripts/check-dispatch-evaluator-floor.mjs .claude/workflows/rc-deep-research.js   # must pass (was: "wrapper block missing")
bash scripts/audit-gates.sh --check 52                                                  # must pass
bash scripts/audit-gates.sh --check 51                                                  # unchanged, must pass
npx --yes prettier --write .claude/workflows/rc-deep-research.js
node --check .claude/workflows/rc-deep-research.js  # (note: top-level await/`export const` — `node --check` may flag; the workflow runtime tolerates it. The real check is Gate 52 + prettier.)
chmod +x plugins/ravenclaude-core/hooks/tests/test-gate52-dispatch-evaluator-floor.sh   # the background agent could not chmod
```

Once Gate 52 passes, **delete this handoff file** — it is a transient build artifact, not durable docs.

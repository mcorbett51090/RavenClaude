---
name: prompt-optimizer
description: "Rewrites an ambiguous-but-single-domain (domain_count<=1) user prompt via emit_optimized_prompt before the turn runs — surfacing constraints, missing context, and wild assumptions instead of silently guessing. Companion generator to prompt-optimizer-gate.sh's Tier-1 classifier."
allowed-tools: Bash, Read
---

# Skill: prompt-optimizer (rewrite generator)

This file documents the **rewrite path** of the `prompt-optimizer` feature: the
`emit_optimized_prompt` forced-tool schema and the generator that fills it. The
classifier that decides whether the rewrite path fires at all is Phase 2's
[`scripts/prompt-optimizer-gate.sh`](../../scripts/prompt-optimizer-gate.sh); the
dispatch-plan path for `domain_count >= 2` is a separate generator (Phase 4, not
covered here). Nothing in this file is wired into `hooks.json`/`settings.json` yet
— that is Phase 6's job. `prompt_optimizer.enabled: false` is the shipped default;
every mechanism this file describes is inert on a project that has not opted in.

Source of truth for the schema below: `docs/plans/2026-09-03-prompt-optimizer/design-lock.md`
§2. If this file and that one ever disagree, the design-lock file wins — it is the
frozen contract; this file is the operating doc built against it.

---

## When this fires

`prompt-optimizer-gate.sh`'s Tier-1 classifier (`emit_prompt_classification`)
emits `action: "rewrite"` whenever `domain_count <= 1` — i.e. the prompt is
single-domain, however complex, ambiguous, or under-specified it may be. That
routing rule is the classifier's own schema (frozen in Phase 0), not a decision
this file makes; the rewrite generator documented here is invoked **after** that
routing decision has already been made, and does not re-derive or re-check
`domain_count` itself.

```
classifier action == "skip"          -> nothing happens, this skill never runs
classifier action == "rewrite"       -> THIS skill (domain_count <= 1)
classifier action == "dispatch_plan" -> Phase 4's generator (domain_count >= 2)
```

---

## The `emit_optimized_prompt` schema (frozen, design-lock.md §2)

```json
{
  "type": "object",
  "required": ["rewritten_prompt", "explicit_constraints", "surfaced_missing_context", "wild_assumption"],
  "properties": {
    "rewritten_prompt": {
      "type": "string",
      "description": "The rewritten prompt text. Must preserve every constraint present in the original."
    },
    "persona": {
      "type": "string",
      "description": "OPTIONAL. A persona/role framing to prepend if the rewrite benefits from one; absent when not applicable."
    },
    "explicit_constraints": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Constraints the rewrite made explicit (including ones implicit in the original prompt)."
    },
    "surfaced_missing_context": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Context the original prompt was missing and that the rewrite surfaces as a gap (not silently fabricates)."
    },
    "wild_assumption": {
      "type": "object",
      "required": ["present", "confidence"],
      "properties": {
        "present": { "type": "boolean" },
        "description": {
          "type": "string",
          "description": "REQUIRED when present==true; omitted/empty when present==false. Free text describing the assumption."
        },
        "confidence": { "type": "string", "enum": ["low", "medium", "high"] }
      }
    }
  }
}
```

Every field above is enforced **exactly** by the generator script's own Python
validator (see "Implementation" below) — a model response missing a required
field, using the wrong type, or omitting `description` while `present: true` is
treated as unparseable and fails open (nothing printed), never partially printed.

`rewritten_prompt` / `persona` / `explicit_constraints` / `surfaced_missing_context`
are **not** on Phase 5's semantic-screen list — design-lock.md §2 explains why:
`rewritten_prompt` **becomes** the working prompt for the turn rather than being
injected as advisory narrative alongside it, and the other three are short,
schema-constrained list items produced under a forced tool call, not open
narrative.

**`wild_assumption.description`, when present, is the one genuinely open-ended,
injection-shaped prose field on this path.**

> [MARKER, per task brief item 4 / design-lock.md §2 & §4a]: `wild_assumption.description`
> requires Phase 5's semantic screen before any downstream injection into a
> model's live context — mirroring the identical marker Phase 2 already carries
> on the classifier's `ambiguity_reason` field. **This phase does not build that
> screen** (out of scope, per the task brief's "What NOT to do"). The generator
> script prints the raw, schema-validated field to stdout only; it never formats
> or injects `additionalContext` itself. A later phase's semantic screen must run
> on this field before it is ever placed into a live turn.

---

## Implementation — the split, and why it's split this way

The schema + a short forced-tool-call wrapper could reasonably live entirely in
this file or entirely in a script. This build splits it:

- **This file (`SKILL.md`)** — the schema (above, byte-for-byte matching
  design-lock.md §2), the routing contract, the semantic-screen marker, and the
  operating notes below (tier resolution, fail-open contract, testing).
- **[`scripts/prompt-optimizer-rewrite.sh`](../../scripts/prompt-optimizer-rewrite.sh)**
  — the actual subprocess invocation, robust JSON extraction, and shape
  validation. This is substantial, imperative logic (a `claude -p` subprocess
  call with markdown-fence stripping and a hand-rolled JSON-object locator,
  mirroring `prompt-optimizer-gate.sh`'s own Tier-1 implementation almost
  exactly) — the same kind of logic that earned Phase 2's classifier its own
  script rather than living inline in prose. The split boundary is clean:
  **the schema and the "why" live here; the "how" lives in the script.**

The two files also share a design decision worth stating explicitly: the script
accepts the **same stdin contract** `prompt-optimizer-gate.sh` does (a
UserPromptSubmit-shaped JSON payload with a `.prompt`/`.promptText` field), so
Phase 6's eventual wiring can pipe the identical raw hook payload into both
scripts in sequence with zero reshaping in between.

---

## Tier resolution — FAST, via `substrate-tier-map.json`'s `resolve_tier()`

This generator runs at the **FAST** tier (design-lock.md §2, and the task brief's
own line: "This generator runs at the FAST tier per the plan"). The script
resolves it by invoking the real, existing mechanism other skills in this repo
already use —
[`scripts/load-substrate-tier-map.py`](../../scripts/load-substrate-tier-map.py)'s
`resolve_tier(host, tier)` — rather than hardcoding a model string:

```bash
python3 plugins/ravenclaude-core/scripts/load-substrate-tier-map.py "" fast
# -> {"model": "claude-haiku-4-5-20251001"}
```

`host` is left blank because a standalone hook script has no host-detection
signal available to it — `resolve_tier()`'s own documented behavior ("blank host
-> claude") is exactly the fallback wanted here, not a workaround around it.

**Corrected precedent citation (task review, 2026-09-08).** This paragraph
originally claimed the CLI-subprocess invocation form "mirrors how
`claude-orchestrate.sh` and `cheap-lane-delegate.sh` invoke tier resolution."
Checked directly against both files: neither references `substrate-tier-map.json`
or `resolve_tier()` at all (`claude-orchestrate.sh` hardcodes its own model
defaults with env-var overrides; `cheap-lane-delegate.sh` is a thin dispatcher
that passes `--agent`/flags through to `grok-delegate.sh`/`copilot-delegate.sh`
verbatim and does no tier resolution itself). The real precedent for reading
`substrate-tier-map.json` via a subprocess/inline-read (rather than
`thing-decide.py`'s `importlib`-based function call) is
[`scripts/grok-delegate.sh`](../../scripts/grok-delegate.sh), which reads the
same map file directly for its own tier/model/effort resolution. This script is
the **first** caller to invoke `resolve_tier()` specifically via
`load-substrate-tier-map.py`'s documented CLI form (`python3
load-substrate-tier-map.py <host> <tier>`) — a real, working, and now-precedented
pattern, but not one two other named scripts were already doing; the claim that
a wider precedent existed for *this exact invocation shape* was inaccurate and is
not repeated. If the resolver script is ever unreadable, the generator falls back
to the literal `claude-haiku-4-5-20251001` — `substrate-tier-map.json`'s own
`hosts.claude.fast` value, restated as a documented fallback of the resolved
value rather than an independently invented one.

---

## Fail-open contract (AT5)

The generator script fails open — exit 0, **nothing** printed to stdout, no
crash, no partial or malformed object ever emitted — on any of:

- `claude` binary missing from `PATH`
- `jq` or `python3` missing from `PATH`
- the subprocess times out (`PROMPT_OPTIMIZER_REWRITE_TIMEOUT_S`, default 30s)
- the subprocess produces empty output
- the output is not extractable as a single well-formed JSON object
- the extracted object fails the frozen required-field shape check (missing
  field, wrong type, or `wild_assumption.present == true` with no non-empty
  `description`)

This is the same fail-open discipline `prompt-optimizer-gate.sh`'s Tier-1
classifier already carries, applied to the generator call. A caller that invokes
this script and gets no stdout should treat that identically to a `skip` verdict
for this turn — never as a signal to retry, block, or surface an error to the
user.

---

## Testing this generator directly

```bash
# 1. Enable the feature for a scratch project dir:
mkdir -p /tmp/pg-test/.ravenclaude
cat > /tmp/pg-test/.ravenclaude/comfort-posture.yaml <<'YAML'
prompt_optimizer:
  enabled: true
  mode: shadow
YAML

# 2. Feed a UserPromptSubmit-shaped payload on stdin:
printf '%s' '{"prompt":"Make the login faster."}' | \
  CLAUDE_PROJECT_DIR=/tmp/pg-test \
  bash plugins/ravenclaude-core/scripts/prompt-optimizer-rewrite.sh
```

A successful run prints one JSON object matching the schema above. A disabled
posture, a missing `claude` binary, or an unparseable model response all print
nothing and exit 0 — verify with `echo $?` and `PROMPT_OPTIMIZER_DEBUG=1` for the
stderr trace of which fail-open branch fired.

---

## What this file/skill deliberately does NOT do

- Does not build Phase 4's `emit_dispatch_plan` dispatch-plan generator (a
  separate phase, dispatched independently — the two generators are
  functionally independent per the task brief's Independence note).
- Does not build Phase 5's semantic screen, `additionalContext` template
  formatting, or delivery-shape logic (inline vs. file-pointer). The generator
  prints raw, validated JSON to stdout only.
- Does not build Phase 9's held-out LLM-judge quality-scoring pass — a
  **separate, scheduled** gate using a model distinct from this generator,
  scored against golden-set notes. Not a per-PR `audit-gates.sh` check this
  skill runs on itself.
- Does not wire anything into `hooks.json`/`settings.json` (Phase 6).
- Does not modify `agent-dispatch-evaluator.sh`, `dispatch-config.json`,
  `evaluate-dispatch.js`, `adaptive-run-classifier`'s files,
  `agent-routing-matrix.json`/`.schema.json`, or `route-task.py`.

`depends_on_claims: [1]` (informational, references an upstream FORGE artifact).
`reversibility: two-way-door`.

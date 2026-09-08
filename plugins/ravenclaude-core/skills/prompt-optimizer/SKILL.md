---
name: prompt-optimizer
description: "Rewrites an ambiguous-but-single-domain (domain_count<=1) user prompt via emit_optimized_prompt, or drafts an advisory multi-domain dispatch plan via emit_dispatch_plan (domain_count>=2), before the turn runs — surfacing constraints, missing context, and wild assumptions instead of silently guessing or fragmenting. Phase 5 screens/formats either generator's output before injection. Companion generators to prompt-optimizer-gate.sh's Tier-1 classifier."
allowed-tools: Bash, Read
---

# Skill: prompt-optimizer (rewrite + dispatch-plan generators + Phase 5 formatting)

This file documents **both generator paths**, plus the Phase 5 formatter that
sits downstream of them, in the `prompt-optimizer` feature:

- The **rewrite path** (Phase 3) — the `emit_optimized_prompt` forced-tool schema
  and its generator, for `domain_count <= 1`.
- The **dispatch-plan path** (Phase 4) — the `emit_dispatch_plan` forced-tool
  schema and its generator, for `domain_count >= 2`.
- The **formatter** (Phase 5) — the semantic screen, delivery-shape branching,
  approval-gate wording, and on-disk audit artifact that turn either
  generator's raw JSON into the exact `additionalContext` text a live turn
  would see. See "Phase 5 — formatting..." below.

The classifier that decides which path fires at all (or neither) is Phase 2's
[`scripts/prompt-optimizer-gate.sh`](../../scripts/prompt-optimizer-gate.sh).
Nothing in this file is wired into `hooks.json`/`settings.json` yet — that is
Phase 6's job. `prompt_optimizer.enabled: false` is the shipped default; every
mechanism this file describes is inert on a project that has not opted in.

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

## The `emit_dispatch_plan` schema (frozen, design-lock.md §3) — Phase 4

Invoked when the classifier returns `action: "dispatch_plan"` (`domain_count >= 2`).
Runs at the **BALANCED** tier (heavier judgment than the rewrite path — see
"Tier resolution" below).

```json
{
  "type": "object",
  "required": ["domains", "per_domain", "wild_assumption"],
  "properties": {
    "domains": { "type": "array", "items": { "type": "string" } },
    "per_domain": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["domain", "recommended_agents", "tailored_brief"],
        "properties": {
          "domain": { "type": "string" },
          "recommended_agents": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["agent", "rationale", "matrix_basis"],
              "properties": {
                "agent": {
                  "type": "string",
                  "description": "MUST resolve to a real, currently-enabled agent name, validated against the live roster before injection (roster-hallucination guard). On failure the entry is dropped, never injected with a hallucinated name."
                },
                "rationale": { "type": "string", "description": "Requires Phase 5's semantic screen." },
                "matrix_basis": { "type": "string", "description": "Cites the agent-routing-matrix.json task_class this recommendation is grounded in." }
              }
            }
          },
          "tailored_brief": { "type": "string", "description": "Requires Phase 5's semantic screen." }
        }
      }
    },
    "wild_assumption": {
      "type": "object",
      "required": ["present", "confidence"],
      "properties": {
        "present": { "type": "boolean" },
        "description": { "type": "string", "description": "Requires Phase 5's semantic screen." },
        "confidence": { "type": "string", "enum": ["low", "medium", "high"] }
      }
    }
  }
}
```

**Never-dispatches invariant (load-bearing, security-relevant).** This
generator's tool definition grants no `Agent`/`Bash`/`Write`/`Edit` capability —
it is pure JSON emission. The nested `claude -p` call the generator script makes
uses `--tools=""`, the same mechanism Phase 2/3 already use to strip all tool
access from that nested call; nothing in the script adds a tool grant back, and
nothing in the script's own control flow reads its emitted JSON back and acts on
it. See
[`scripts/prompt-optimizer-dispatch.sh`](../../scripts/prompt-optimizer-dispatch.sh)'s
own header for the full static-inspection argument.

**The roster-hallucination guard (an ADDITION to the matrix-citation check, not
a replacement — both run, independently, on every `recommended_agents[]`
entry):**

1. `agent` must resolve to a real, live agent name.
2. `matrix_basis` must cite a real `agent-routing-matrix.json` `task_classes`
   key, read directly from the real file at generation time.

Either check failing drops that one entry (never the whole plan) and caps
`wild_assumption.confidence` at `"low"` — see the script's own "ROSTER
ENUMERATION — A JUDGMENT CALL" and "CONFIDENCE INTERPRETATION" header sections
for the honest limits of what "live, currently-enabled" means here (there is no
verified, portable, on-disk registry of enabled agents reachable from a
standalone hook script; this generator scans this marketplace's own shipped
`agents/*.md` frontmatter instead, degrading conservatively — narrower, never
wider — when its directory-climbing guesses miss).

> [MARKER, per task brief item 4 / design-lock.md §3 & §4a]: `rationale` (each
> `recommended_agents[]` entry), `tailored_brief` (each `per_domain[]` entry),
> and `wild_assumption.description` (when present) ALL REQUIRE PHASE 5'S
> SEMANTIC SCREEN before any downstream injection into a model's live context.
> This phase does not build that screen. `domain`, `agent`, and `matrix_basis`
> are NOT on the screen list — `domain` is a short classifier-emitted label,
> `agent`/`matrix_basis` are validated against real, on-disk rosters/registries
> by the generator's own guards, not arbitrary model text.

**Implementation split** — same boundary Phase 3 established: the schema + the
"why" live here; the "how" (the subprocess call, robust JSON extraction, shape
validation, and the roster/matrix guard application) lives in
[`scripts/prompt-optimizer-dispatch.sh`](../../scripts/prompt-optimizer-dispatch.sh).
The script accepts the same stdin contract (`.prompt`/`.promptText`) as the
other two prompt-optimizer scripts.

**Tier resolution — BALANCED**, via the same `resolve_tier()` mechanism Phase 3
uses for FAST:

```bash
python3 plugins/ravenclaude-core/scripts/load-substrate-tier-map.py "" balanced
```

**Fail-open contract** — identical discipline to Phase 2/3: exit 0, nothing
printed, no crash, on a missing `claude`/`jq`/`python3` binary, a subprocess
timeout (`PROMPT_OPTIMIZER_DISPATCH_TIMEOUT_S`, default 40s), empty subprocess
output, unparseable JSON, a structural schema miss, OR an empty roster scan
(the guard has nothing real to validate against — fails open rather than ever
validate against nothing or drop everything).

### Testing this generator directly

```bash
mkdir -p /tmp/pd-test/.ravenclaude
cat > /tmp/pd-test/.ravenclaude/comfort-posture.yaml <<'YAML'
prompt_optimizer:
  enabled: true
  mode: shadow
YAML

printf '%s' '{"prompt":"Rebuild our checkout flow to support Apple Pay, make sure it'"'"'s PCI compliant, and load in under 200ms."}' | \
  CLAUDE_PROJECT_DIR=/tmp/pd-test \
  bash plugins/ravenclaude-core/scripts/prompt-optimizer-dispatch.sh
```

`PROMPT_OPTIMIZER_DEBUG=1` traces which branch fired (`ROSTER_SCAN`,
`TIER_RESOLVE_FALLBACK`, `FAILOPEN reason=...`, or `GENERATED model=...`).

---

## Phase 5 — formatting, the semantic screen, delivery shape, the audit artifact

[`scripts/prompt-optimizer-format.py`](../../scripts/prompt-optimizer-format.py)
is the companion formatter: it takes the classifier's `action`/`confidence`/
`ambiguity_reason` plus either generator's raw, schema-validated JSON and
produces (a) the exact `additionalContext` text frozen in design-lock.md §4,
(b) the dispatch-plan delivery-shape decision (§7's frozen `≤2 inline / >2
file-pointer` threshold), and (c) the on-disk audit artifact (§5's frozen
path). It is a pure, offline, no-network text transform — no `claude -p` call,
no filesystem scan beyond writing its own artifact.

**Input envelope** (stdin, one JSON object):

```json
{
  "action": "rewrite" | "dispatch_plan",
  "classifier": { "confidence": "low|medium|high", "ambiguity_reason": "<optional>" },
  "generator": { "<the raw JSON printed by the rewrite or dispatch generator>" }
}
```

`classifier.ambiguity_reason` is deliberately NOT read from
`prompt-optimizer-gate.sh`'s stdout (Phase 2 omits it there by design, AT3) —
a real Phase 6 wiring reads it from the on-disk audit artifact `gate.sh`
already writes, and passes the extracted value into this envelope. This
script has no filesystem-scanning logic of its own to locate that file.

**The semantic screen (red-team Finding 3).** Before any of the four fields
design-lock.md §4a names (`ambiguity_reason`, `wild_assumption.description`,
per-recommendation `rationale`, per-domain `tailored_brief`) is rendered, a
cheap, deterministic keyword/phrase regex screen
(`is_directive_shaped()`) checks it for imperative/directive-shaped language
("skip confirmation", "proceed without", "do not ask", "full access",
"without waiting", "ignore the above", and related phrasings — mirroring
[`hooks/_scrub.sh`](../../hooks/_scrub.sh)'s SHAPE, a pattern array + a scrub
function, for a different concern). A flagged field is ALWAYS degraded to a
FIXED fallback string — this implementation deliberately never attempts the
"stripped/rewritten" disposition design-lock.md §4 also allows, because a
strip transform is itself an attack surface; the fixed-fallback disposition
admits a trivial safety proof (the rendered text is always one of two
hardcoded constants when the screen fires, never a function of the flagged
content):

- `GENERIC_FALLBACK` (ambiguity_reason / rationale / tailored_brief):
  `"content flagged for review — see the audit artifact"` (design-lock.md §4's
  own frozen fallback text).
- `WILD_ASSUMPTION_FALLBACK` (wild_assumption.description only):
  `"A wild assumption was flagged — see the audit artifact for detail before
  proceeding."` (design-lock.md §4 Variant 2's own frozen fallback text).

The `AskUserQuestion`-as-first-tool-call instruction line (the approval-gate
wording, tiebreak Conflict 2 → A) is a FIXED string emitted whenever
`wild_assumption.present == true` — it is never itself screened and never
degrades alongside the (possibly-fallback) description line, satisfying
design-lock.md §4 Variant 2's "the approval pause must survive even a fully
degraded description" invariant. **This is explicitly best-effort on the
hook path** — a `UserPromptSubmit` hook can only inject advisory
`additionalContext`, it cannot force the next turn's first tool call; nothing
here or in a future Phase 6 wiring should overstate that it can.

A test-only environment variable, `PROMPT_OPTIMIZER_FORMAT_DISABLE_SCREEN=1`,
makes the screen report "not flagged" unconditionally — it exists solely so a
caller can prove the screen is load-bearing (run an identical fixture twice:
caught, then leaked) and is never referenced by any real wiring or posture
key.

**Delivery-shape branching (red-team Finding 5, design-lock.md §7).**
`rewrite` is always inline. `dispatch_plan` is inline only when
`sum(len(recommended_agents) for each per_domain entry) <= 2`; above that,
file-pointer delivery is mandatory (a short pointer + truncated domains line,
never the per-domain/per-agent detail — that only ever lives in the on-disk
artifact).

**The on-disk audit artifact (design-lock.md §5).** Frozen path:
`.ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json`. It retains the
RAW, unscreened classifier + generator content in full, plus a `screen`
object recording each field's disposition (`absent`/`clean`/`flagged`) — this
is design-lock's own stated architecture, not a leak: acceptance test 5's own
framing is that the no-egress bar governs the `additionalContext` STDOUT
surface, and the on-disk artifact is expected to be complete.

**Composition with `decision-review` (design-lock/plan requirement).** A
wild-assumption question is a genuine-preference call, and this repo's
`decision-review` tribunal ([`scripts/thing-decide.py`](../../scripts/thing-decide.py)
`decide` mode) defers such calls even under `decision_review: binding` — it
never auto-resolves them to a `yes`/`no`. Live-verified this session (see
`task-5-report.md` for the actual command + output): a wild-assumption-shaped
question routed through `thing-decide.py decide` with `decision_review:
binding` set came back `verdict: "defer"`, `binding: false`, with all three
convened seats (Forseti/Mímir/Heimdall) independently voting `defer`.

**Fail-open contract, same discipline as Phases 2-4.** Any error (unparseable
stdin, an unsupported/missing `action`, a filesystem error writing the audit
artifact) causes this script to exit 0 with no stdout — never a partial or
malformed JSON object.

### Testing this formatter directly

```bash
mkdir -p /tmp/pof-test/.ravenclaude
cat > /tmp/pof-test/.ravenclaude/comfort-posture.yaml <<'YAML'
prompt_optimizer:
  enabled: true
  mode: shadow
YAML

echo '{"action":"rewrite","classifier":{"confidence":"medium"},"generator":{"rewritten_prompt":"Fix the bug.","explicit_constraints":[],"surfaced_missing_context":[],"wild_assumption":{"present":false,"confidence":"high"}}}' | \
  python3 plugins/ravenclaude-core/scripts/prompt-optimizer-format.py --project-dir /tmp/pof-test --session demo

# Internal self-test (screen positives/negatives, all-6-template byte checks,
# delivery-shape boundary cases, and the must-fail-teeth mechanism):
python3 plugins/ravenclaude-core/scripts/prompt-optimizer-format.py --self-test
```

---

## What this file/skill deliberately does NOT do

- Does not wire the semantic screen, delivery-shape branching, or the audit
  artifact into a live `UserPromptSubmit` hook — see the Phase 5 section
  above for what exists (a standalone formatter script), and Phase 6 for the
  wiring itself.
- Does not build Phase 9's held-out LLM-judge quality-scoring pass — a
  **separate, scheduled** gate using a model distinct from either generator,
  scored against golden-set notes. Not a per-PR `audit-gates.sh` check this
  skill runs on itself.
- Does not wire anything into `hooks.json`/`settings.json` (Phase 6).
- Does not modify `agent-dispatch-evaluator.sh`, `dispatch-config.json`,
  `evaluate-dispatch.js`, `adaptive-run-classifier`'s files,
  `agent-routing-matrix.json`/`.schema.json` (read-only, always), or
  `route-task.py`.

`depends_on_claims: [1, 3, 4, 6]` (informational, references upstream FORGE
artifacts — Phase 4's set; Phase 3's own `[1]` is a subset).
`reversibility: two-way-door`.

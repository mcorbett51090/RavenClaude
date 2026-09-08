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
are **not** on Phase 5's semantic-screen list — design-lock.md §2 explains why, with
a corrected rationale for `rewritten_prompt` (final whole-branch review Finding 3):
the shipped hook mechanism emits `hookSpecificOutput.additionalContext`, which Claude
Code **appends** to context — it never substitutes for the user's prompt — so
`rewritten_prompt` is injected unscreened **alongside** the original prompt, not in
its place. It stays unscreened anyway, on narrower, honestly-stated grounds (Haiku
output derived from the user's own prompt, default-off, advisory-only) — see
design-lock.md §2's own note for the full accept/reject record. `explicit_constraints`
/ `surfaced_missing_context` are short, schema-constrained list items produced under
a forced tool call, not open narrative.

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

## Worked examples — one full walkthrough per outcome

Three real prompts from the golden-set fixtures ([`eval/golden-set.jsonl`](eval/golden-set.jsonl)),
each carried end to end through classifier verdict, generator output, and Phase 5's rendered
`additionalContext`. **These are hand-constructed, schema-conformant walkthroughs, not a captured live
transcript** — building all three from a real `claude -p` run was out of scope for a documentation
pass and would report a specific run's variance as if it were the contract; the frozen schemas above are
what's load-bearing, and every field below conforms to them exactly. Prompt-level details are quoted
verbatim from the golden set's own `notes`.

### Example 1 — `skip` (Tier-0, zero paid classification)

**Prompt:** `"What's the capital of France?"` (golden-set: *"Pure factual recall with no code/system
anchor and no ambiguity to resolve — the canonical Tier-0 zero-cost skip case."*)

Phase 2's Tier-0 pre-filter — not this skill, which never runs — rejects this prompt on anchor count and
domain-keyword-cluster signals alone, before any Haiku call. Nothing is injected; the turn proceeds with
the prompt exactly as typed. This is the cheapest of the three paths and the one R5 below is careful not
to claim applies to every "skip" outcome — see that section for the Tier-1-reaches-and-still-resolves-
skip case, which pays a real (small) cost this Tier-0 case does not.

**Measured, not asserted.** An earlier revision of `prompt-optimizer-gate.sh`'s Tier-0 rule required
`anchor_count == 1` exactly — which meant this specific zero-anchor prompt, and every other zero-anchor
trivial ask, always fell through to a paid Tier-1 call; run against the full 42-entry golden-set corpus
that version Tier-0-skipped **0/42** entries, contradicting the "canonical Tier-0 zero-cost skip case"
claim above. The rule now also skips a zero-anchor prompt when it matches a narrow trivial-shape
whitelist (see the rule's own header comment for the full rationale and the false-skip trap a blanket
`anchor_count <= 1` widening fell into). Re-run against the same corpus with a stub `claude` binary, the
fix measures **9/42 Tier-0-skip** — exactly the 9 golden-set entries in this trivial-ask category,
including this one — with zero false-skips among the other 33 (the wild-assumption, complex-single-
domain, and multi-domain dispatch entries all still correctly reach Tier-1).

### Example 2 — `rewrite` (Tier-1, single-domain, wild assumption flagged)

**Prompt:** `"Add caching to this."` (golden-set: *"'This' has no antecedent in the prompt and no layer
(HTTP/DB/application) is specified — any answer necessarily guesses a target, which must be surfaced as
a wild assumption."*)

Tier-0 does not catch this (it has a domain-relevant keyword — "caching" — dense enough relative to its
length to clear the pre-filter), so it reaches the Tier-1 Haiku classifier:

```json
{
  "action": "rewrite",
  "confidence": "medium",
  "domain_count": 1,
  "anchor_count": 0,
  "assumption_count": 1,
  "ambiguity_reason": "No named target for \"this\" and no cache layer specified — the prompt has zero anchors for what to cache."
}
```

`domain_count <= 1` routes to this skill's rewrite generator (`emit_optimized_prompt`):

```json
{
  "rewritten_prompt": "Add response caching to the [ASSUMED: the application's primary HTTP read path] to reduce repeated computation. Use an in-memory cache with a sensible TTL, and leave a comment noting the cached layer is a starting guess pending confirmation.",
  "explicit_constraints": [
    "Preserve current response correctness",
    "Keep the change small and reviewable"
  ],
  "surfaced_missing_context": [
    "No target file, function, or layer (HTTP/DB/application) named in the original prompt",
    "No cache invalidation strategy specified"
  ],
  "wild_assumption": {
    "present": true,
    "description": "Assumed the caching target is the application's primary HTTP read path, not the database layer or a background job — the prompt gave no antecedent for \"this.\"",
    "confidence": "low"
  }
}
```

Phase 5's screen finds no directive-shaped language in `ambiguity_reason` or
`wild_assumption.description`, so both render clean (Variant 2, `wild_assumption.present: true` —
design-lock.md §4):

```
[RavenClaude prompt-optimizer] A rewritten version of your prompt is offered below as
additional context for this turn (not substituted for what you typed), and a wild
assumption was flagged. Call AskUserQuestion as your first tool call this turn, presenting
the flagged assumption below, before proceeding.

- Confidence: medium
- Constraints preserved: 2
- Missing context surfaced: 2
- Why: No named target for "this" and no cache layer specified — the prompt has zero anchors for what to cache.
- Flagged assumption (confidence: low): Assumed the caching target is the application's primary HTTP read path, not the database layer or a background job — the prompt gave no antecedent for "this."

Rewritten prompt offered as additional context for this turn:
<rewritten-prompt>
Add response caching to the [ASSUMED: the application's primary HTTP read path] to reduce repeated computation. Use an in-memory cache with a sensible TTL, and leave a comment noting the cached layer is a starting guess pending confirmation.
</rewritten-prompt>

Full record: .ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json
```

### Example 3 — `dispatch_plan` (Tier-1, multi-domain, file-pointer delivery)

**Prompt:** `"Rebuild our checkout flow to support Apple Pay, make sure it's PCI compliant, and load in
under 200ms."` (the same prompt the dispatch generator's own "Testing this generator directly" section
above uses — reused deliberately so the two sections corroborate each other end to end.)

```json
{
  "action": "dispatch_plan",
  "confidence": "high",
  "domain_count": 3,
  "anchor_count": 1,
  "assumption_count": 1,
  "ambiguity_reason": "Spans payments integration, PCI compliance, and load-time performance — three distinct remediation domains with different specialists and constraints."
}
```

`domain_count >= 2` routes to `emit_dispatch_plan`. Every `recommended_agents[].agent` below is a real,
currently-enabled agent name (verified against the live roster this session — `web-commerce:commerce-
integration-engineer`, `web-commerce:commerce-webhook-security-reviewer`, and `web-design:performance-
engineer` all resolve). Every `matrix_basis` cites one of [`agent-routing-matrix.json`](../../knowledge/agent-routing-matrix.json)'s
five real `task_classes` keys (`coding-implementation`, `coding-debugging-design`, `research-deep`,
`writing-documentation`, `data-analysis`) — not an invented one:

```json
{
  "domains": ["payments", "security", "performance"],
  "per_domain": [
    {
      "domain": "payments",
      "recommended_agents": [
        {
          "agent": "web-commerce:commerce-integration-engineer",
          "rationale": "Owns wiring a new checkout provider path, including a new payment method, into an existing site.",
          "matrix_basis": "coding-implementation"
        }
      ],
      "tailored_brief": "Wire Apple Pay into the existing checkout flow without touching PCI-scoped card storage."
    },
    {
      "domain": "security",
      "recommended_agents": [
        {
          "agent": "web-commerce:commerce-webhook-security-reviewer",
          "rationale": "PCI card-isolation and webhook-verification audit is exactly this agent's scope.",
          "matrix_basis": "coding-debugging-design"
        }
      ],
      "tailored_brief": "Confirm the new Apple Pay path never routes raw card data through app-owned storage."
    },
    {
      "domain": "performance",
      "recommended_agents": [
        {
          "agent": "web-design:performance-engineer",
          "rationale": "Owns Core Web Vitals and load-time budget work for checkout-critical pages.",
          "matrix_basis": "coding-implementation"
        }
      ],
      "tailored_brief": "Get the rebuilt checkout flow under a 200ms load budget without regressing the payment integration."
    }
  ],
  "wild_assumption": { "present": false, "confidence": "high" }
}
```

Three domains × one agent each = **3 total recommended agents**, which is `> 2` — design-lock.md §7's
frozen threshold makes file-pointer delivery **mandatory**, regardless of how short any individual entry
is. Phase 5 renders Variant 3's file-pointer sub-shape (`wild_assumption.present: false`):

```
[RavenClaude prompt-optimizer] This prompt spans 3 domains — a dispatch plan naming 3
agents was drafted (advisory only; nothing was dispatched).

- Confidence: high
- Why: Spans payments integration, PCI compliance, and load-time performance — three distinct remediation domains with different specialists and constraints.
- Domains: payments, security, performance (3 total)

Full plan: .ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json
Read that file before acting on this dispatch plan.
```

The full per-domain detail — the three `rationale` / `tailored_brief` lines above — never reaches
`additionalContext` in this shape. It lives only in the on-disk audit artifact, exactly as design-lock.md
§7 requires above the threshold.

---

## Composition — how this fits with the marketplace's other model/dispatch-tiering mechanisms

`prompt-optimizer` is upstream of, and a genuinely different mechanism from, three other pieces of
RavenClaude machinery that also reason about "which model or agent should do this." Conflating them is
an easy mistake, so the distinction is stated explicitly here:

- **`prompt-optimizer` (this skill) classifies the raw user prompt, before any dispatch decision exists.**
  Its only three possible outcomes are: do nothing (`skip`), rewrite the prompt in place for this one turn
  (`rewrite`), or draft an advisory dispatch plan naming specialists a human/assistant *might* want to
  spawn (`dispatch_plan`). Per the Never-dispatches invariant above, it is architecturally incapable of
  spawning anything itself — its generator call carries no `Agent`/`Bash`/`Write`/`Edit` tool grant.
  **It is NOT a dispatch right-sizer** — it never tunes a model tier for an existing dispatch, because at
  the point it runs, no dispatch has been decided on yet.

- [`agent-dispatch-evaluator`](../agent-dispatch-evaluator/SKILL.md) right-sizes an individual dispatch
  **after** the decision to dispatch has already been made — it evaluates `{subagent_type, description,
  prompt_head}` at the moment of an actual Agent dispatch / Workflow `agent()` call / tribunal seat
  dispatch, and binds the model tier for that one call.

- [`adaptive-run-classifier`](../adaptive-run-classifier/SKILL.md) right-sizes an entire multi-phase
  **workflow run** (e.g. the `rc-deep-research` loop) — it emits one `run_config` envelope covering
  every phase's tier and cardinality knobs for the whole run, read once at workflow start.

- [`agent-routing-matrix.json`](../../knowledge/agent-routing-matrix.json) is a data registry, not a
  live mechanism: task shape → `{agent surface, model, effort tier}` across five coding-agent hosts
  (Claude Code, Codex CLI, Copilot CLI, Copilot Chat, Grok Build CLI) — see its own five `task_classes`
  keys used in Example 3 above. It is **not** a registry of which RavenClaude specialist handles a
  domain; that is a separate roster (`agents/*.md` frontmatter) this skill's dispatch generator validates
  `recommended_agents[].agent` against independently. Both
  [`cheap-lane-delegation`](../cheap-lane-delegation/SKILL.md)'s agent choice and
  [`spawn-team`](../spawn-team/SKILL.md)'s host choice may consult the routing matrix as an optional
  reference; this skill's dispatch generator cites one of its `task_classes` keys via `matrix_basis`
  purely as a grounding anchor for *what shape of work* a recommendation is — the recommendation itself
  never comes from the matrix. Its `model_ref.tier` vocabulary (`fast`/`balanced`/`top`) is the same
  vocabulary this skill's own generators resolve via
  [`substrate-tier-map.json`](../../knowledge/substrate-tier-map.json)'s `resolve_tier()` (see "Tier
  resolution" above) — one shared tier vocabulary, two independent consumers.

- [`spawn-team`](../spawn-team/SKILL.md) is the Team Lead's actual dispatch playbook — the mechanism
  that performs a real Agent dispatch. This skill's `dispatch_plan` output is advisory context the
  assistant reads in a later turn; if the assistant decides to act on it, `spawn-team` (which may itself
  consult `agent-routing-matrix.json` for a non-Claude host, and — per its own Step 4.5 — the
  `orchestrator` knob that can route through
  [`claude-orchestrate.sh`](../../scripts/claude-orchestrate.sh) under a non-Claude host) is what
  actually invokes the recommended specialists.

**The ordering, when every mechanism above is live on the same turn:** `prompt-optimizer` classifies the
raw prompt → the human/assistant reads the advisory `dispatch_plan` and decides whether to act on it →
`spawn-team` performs the actual dispatch (optionally via `claude-orchestrate.sh` for host routing) →
`agent-dispatch-evaluator` right-sizes each individual resulting dispatch call and/or
`adaptive-run-classifier` right-sizes a multi-phase workflow built from those dispatches. `prompt-
optimizer` never calls, is called by, or shares a schema with any of the other three — "composes with"
here means "sits upstream of, and hands off advisory context to."

A wild-assumption question this skill flags does not resolve itself, either: if it were ever surfaced as
an `AskUserQuestion` under this repo's binding decision-routing convention, the
[`decision-review`](../decision-review/SKILL.md) tribunal defers a genuine-preference call like this one
rather than auto-resolving it — see "Composition with `decision-review`" in the Phase 5 section above for
the live-verified `thing-decide.py` result this claim rests on.

---

## Output Contract — Structured Output Protocol applicability

This skill, like [`adaptive-run-classifier`](../adaptive-run-classifier/SKILL.md), emits no runtime
artifact of its own in the agent-handoff sense the Structured Output Protocol governs (see
[`plugins/ravenclaude-core/CLAUDE.md`](../../CLAUDE.md) §"Structured Output Protocol"). Its three
generator scripts and the Phase 5 formatter are **not agents** — they are `claude -p` subprocess
invocations and a pure text transform, invoked from a hook, never dispatched via the Agent tool and never
reporting back to a Team Lead. The Protocol's `---RESULT_START---`/`---RESULT_END---` delimited-JSON
convention is built for a sub-agent's report to the orchestrator; nothing in this pipeline is that shape,
so applying the convention literally here (wrapping the generator's schema-validated JSON output in the
Protocol's delimiters as if it were an agent handoff) would be decorative rather than load-bearing —
matching [`structured-output/SKILL.md`](../structured-output/SKILL.md)'s own scope, which is "handoff-
bearing reports," not every JSON-emitting script in the marketplace.

Where the Protocol genuinely applies: when [`prompt-engineer`](../../agents/prompt-engineer.md) or
[`architect`](../../agents/architect.md) **critiques an instance of this contract** — reviewing a
generated `dispatch_plan` in a PR, or auditing whether a real `wild_assumption.description` survived
Phase 5's screen correctly — that agent's own report to the Team Lead ends with the cross-plugin
Structured Output JSON block per [`structured-output/SKILL.md`](../structured-output/SKILL.md), exactly
as [`adaptive-run-classifier`](../adaptive-run-classifier/SKILL.md)'s Output Contract states for the
identical situation. The contract is on the *reviewer's* handoff, never on this skill's own generator
output.

---

## Honest ROI — what this build actually adds, stated without inflation

Per plan.md §7 (the plan's own "Honest ROI note", R1/R5 in the risk matrix): **the real counterfactual
this build competes against is not "the assistant blindly guesses."** It is a standing AGENTS.md
instruction — *"ask ONE question on an under-specified request"* (Claim-Grounding Rule 1c, this repo's
own constitution) — plus `ask-on-ambiguity.sh`'s existing advisory `UserPromptSubmit` sliver, plus
[`spawn-team`](../spawn-team/SKILL.md)'s playbook already pointing at
[`agent-routing-matrix.json`](../../knowledge/agent-routing-matrix.json) when a non-Claude host is in
play. All three of those mechanisms predate this feature and are not replaced by it.

**What genuinely survives as new value, stated as exactly two things:**

1. **Coverage/consistency.** `ask-on-ambiguity.sh` matches a narrow input *shape* (short, no anchor, an
   open-ended verb) and cannot see whether the assistant then actually asks — Rule 1c is itself
   behavioral, dependent on the assistant's own attention that turn. This skill's classifier fires on
   *every* turn a posture opts into, independent of whether the assistant would have noticed the
   ambiguity on its own. That is a real difference in kind — a gate that fires by construction versus a
   discipline the assistant might apply.
2. **Triage.** The classifier is a cheap upstream judgment (`fast` tier — Haiku 4.5 per the "Tier
   resolution" section above) that decides whether a prompt is worth the more expensive path (a rewrite,
   or naming specialists) before any expensive model spends tokens reasoning about it. That "is this
   worth stopping for" judgment, offloaded onto a cheap model before the main turn runs, is genuinely new.

**Neither of those is "produces a routing decision that wouldn't otherwise exist."** A well-attended
Claude Code session following its own AGENTS.md already asks the one clarifying question, and
`spawn-team` already knows to consult the routing matrix on a genuinely multi-domain ask. This plan
proceeds on that thinner, honestly-stated margin — not the stronger, implicit "nothing like this exists
today" framing an earlier draft of this feature carried.

**R5 — the non-zero tax, stated plainly.** scope.md's own framing implies "zero added latency/cost on
trivial single-step asks." That is true only for the subset Tier-0's zero-cost pre-filter actually
catches (Example 1 above). It is **not** true for every prompt that ends up resolving to `skip` — a
prompt can clear Tier-0's anchor/keyword heuristics, reach the paid Tier-1 Haiku classifier, and still
resolve to `skip` (either because the classifier itself judged `action: "skip"`, or because
`prompt-optimizer-gate.sh`'s own low-confidence downgrade rule forces `action` to `skip` regardless of
what the classifier returned — a real branch in the shipped script, not a hypothetical). That bucket pays
one Haiku call's real latency and real (small) cost for a turn that ultimately runs unmodified. Anyone
reading this file as "trivial asks are free" should read that sentence as false for this bucket
specifically — free only holds for the Tier-0-caught subset.

**How big is the Tier-0-caught subset, measured, not assumed?** Against the shipped 42-entry golden-set
corpus, Tier-0 free-skips exactly **9/42** entries — the trivial factual/creative/deterministic-transform
category. The other **33/42** — every wild-assumption ask, every complex-but-single-domain ask, every
multi-domain dispatch case — clear Tier-0 and pay at least one Tier-1 Haiku call, whether they ultimately
resolve to `rewrite`, `dispatch_plan`, or a Tier-1-judged `skip`. Before this rule was corrected, the
Tier-0-caught subset measured **0/42** — every prompt in this eval set, trivial or not, paid the Tier-1
tax — meaning the "paid-then-skip bucket" this paragraph warns about was not a subset of the trivial-ask
set at all; it *was* the trivial-ask set, in its entirety. That was the actual, measured state this
paragraph's honesty was protecting against, whether or not the prose said so explicitly.

---

## Self-score against `agent-quality-rubric`

Applied per [`agent-quality-rubric/SKILL.md`](../agent-quality-rubric/SKILL.md)'s 6-dimension checklist,
scored here in the file itself per this phase's own acceptance test. **One adaptation stated up front,
honestly:** the rubric's own text says *"You are reviewing an agent file (typically
`plugins/<plugin>/agents/<role>.md`)."* This is a skill file, not an agent file, and three of the six
dimensions (3, 4, 6) have anchors written for an agent's own Output Contract / CGP-inheritance /
scenario-authoring frontmatter — none of which a `SKILL.md` structurally carries (`check-frontmatter.py`
only gates `agents/*.md`, per `AGENTS.md` house rule 7-9). Scoring those dimensions against their literal
anchors would either force a false 1 (frontmatter this file type doesn't have) or require inventing a
looser analogue. Both are named below rather than silently picked.

| # | Dimension | Score | Reasoning |
|---|---|---|---|
| 1 | Mission clarity | **4** | The opening paragraph states it in one compound sentence — *"This file documents **both generator paths**, plus the Phase 5 formatter that sits downstream of them, in the `prompt-optimizer` feature"* — parseable in a single read, but needs the following bullet list to fully unpack the three sub-mechanisms, so it does not clear the bar for a bare one-sentence-no-hedge "5". |
| 2 | Scope sharpness | **5** | An explicit "Not for X" list exists twice over: the "What this file/skill deliberately does NOT do" section below names concrete exclusions with pointers (Phase 6 hook wiring, Phase 9's judge, the untouched files), and the new Composition section above adds the agent-level test directly — *"**It is NOT a dispatch right-sizer**"* — with the two named alternatives (`agent-dispatch-evaluator`, `adaptive-run-classifier`) it defers to. |
| 3 | Capability Grounding alignment | **3 (adapted)** | This file never states "inherits the Capability Grounding Protocol" — it can't meaningfully, since it documents scripts and a hook contract, not an agent turn. Its honest analogue is the **fail-open contract** each phase carries verbatim (e.g. *"exit 0, nothing printed... never as a signal to retry, block, or surface an error to the user"*) — the script-level equivalent of "don't falsely claim blocked" and "enumerate the failure mode explicitly" rather than silently degrading. That discipline is real and thorough, but it is not CGP by name, and dimension 3's literal anchors (an "inherits the Protocol" line, a "Grounding checks performed" output line) are genuinely absent. Scored down from 4/5 rather than credited for an analogue the rubric didn't ask for. |
| 4 | Output-Contract completeness | **3 (adapted)** | The new "Output Contract" section above states explicitly which Structured-Output cases apply (a reviewing agent's own handoff) and which don't (this skill's own generator output) — closer to complete than absent. It does not carry the five-line agent-report shape (Status / files-changed / a mandatory plugin-specific line / the JSON block / a reporting cap) because this file is never itself the thing producing a turn-ending report; that shape belongs to the agent that reviews an instance of this contract, not to this file. |
| 5 | Escalation paths | **4** | Named, not generic: a flagged `wild_assumption` escalates to an `AskUserQuestion` and, if routed through decision-routing, to the `decision-review` tribunal (which defers rather than auto-resolves — cited with a live-verified test result in the Phase 5 section and again in Composition above); a fail-open failure escalates to "treat identically to a skip verdict" (an explicit, named non-escalation); Phase boundaries are named for what's deferred (Phase 6, Phase 9). Held at 4 rather than 5 because these are prose call-outs scattered across sections, not one consolidated table the rubric's "5" anchor describes. |
| 6 | Example scenarios | **4 (adapted)** | The rubric's literal test is the `agent-scenario-authoring` YAML frontmatter (`audience`/`works_with`/`scenarios`/`quickstart`) — a schema `SKILL.md` files do not carry at all (it is agent-only, per `AGENTS.md`'s own house rule); scoring this dimension against that literal anchor would read as a false "1" for a gap that isn't this file's to close. The skill-file analogue — worked, trigger-phrase-realistic examples covering every distinct outcome — is now present (the three examples above, one per `skip`/`rewrite`/`dispatch_plan`, each with a real golden-set prompt and its full pipeline trace). Held at 4 rather than 5 because three examples is the acceptance-test floor, not a generous margin above it, and none demonstrates the file-pointer *and* wild-assumption combination (Variant 4) together. |

**Total: 24/30 (avg 4.0).** Per the rubric's own disposition table, this lands in **"22-26 (avg 3.7+) —
Ship with minor edits — note the weakest dimensions in the PR description."** The two weakest are
Dimensions 3 and 4 (both 3, both explicitly adapted rather than literally satisfied) — noted here rather
than averaged away, per the rubric's own "Anti-patterns" warning against an average-only verdict. Neither
is a block: no dimension scored ≤2, and Mission clarity (the rubric's stated hard-block trigger) scored 4.

---

## What this file/skill deliberately does NOT do

- Phase 5 itself did not wire the semantic screen, delivery-shape branching, or
  the audit artifact into a live `UserPromptSubmit` hook — that was Phase 6's
  job, and Phase 6 is now merged into this branch: `prompt-optimizer-gate.sh` is
  WIRED into both `hooks/hooks.json` (plugin-canonical) and
  `.claude/settings.json` (dev-mirror), and invokes this formatter + the two
  generator scripts directly (see gate.sh's own "PHASE 6 WIRING" section). This
  bullet records Phase 5's own scope boundary at the time it was written, not
  the current state of the pipeline.
- Does not build Phase 9's held-out LLM-judge quality-scoring pass — a
  **separate, scheduled** gate using a model distinct from either generator,
  scored against golden-set notes. Not a per-PR `audit-gates.sh` check this
  skill runs on itself.
- This formatter script has no wiring code of its own — it is invoked by
  gate.sh, which IS wired into `hooks.json`/`settings.json` as of Phase 6 (see
  the bullet above; not an open task).
- Does not modify `agent-dispatch-evaluator.sh`, `dispatch-config.json`,
  `evaluate-dispatch.js`, `adaptive-run-classifier`'s files,
  `agent-routing-matrix.json`/`.schema.json` (read-only, always), or
  `route-task.py`.

`depends_on_claims: [1, 3, 4, 6]` (informational, references upstream FORGE
artifacts — Phase 4's set; Phase 3's own `[1]` is a subset).
`reversibility: two-way-door`.

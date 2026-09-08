# Design lock — `prompt-optimizer` (Phase 0)

Source: [`plan.md`](./plan.md) §4 Phase 0. This is a documentation-only freeze — no code ships in this
phase. Every schema below is a **contract for later phases**, not an implementation; the four
`additionalContext` template variants are the exact strings later phases must byte-diff their output
against (Phase 5 acceptance test 1).

**Global constraints this design honors** (restated from the task brief, binding on every later phase):
ships `prompt_optimizer.enabled: false` by default; every mechanism only (a) reads already-committed
data (`agent-routing-matrix.json`, `substrate-tier-map.json`), (b) writes new, gitignored artifacts
under `.ravenclaude/runs/`, (c) injects advisory `additionalContext`; nothing here edits
`agent-dispatch-evaluator.sh`, `dispatch-config.json`, `evaluate-dispatch.js`,
`adaptive-run-classifier`'s schema/templates, `agent-routing-matrix.json`/`.schema.json`, or
`route-task.py` — all five are cited as read-only precedent below, none modified.

---

## 1. Classifier output schema — Tier-1 Haiku forced-tool call

The Tier-1 call (Phase 2) is a single forced-tool Messages API call, matching
`agent-dispatch-evaluator`'s proven shape (`claude -p --bare --output-format json --model
claude-haiku-4-5-<pinned-date> --tools ""`). The forced tool is named `emit_prompt_classification`.

```json
{
  "type": "object",
  "required": ["action", "confidence", "domain_count", "anchor_count", "assumption_count"],
  "properties": {
    "action": {
      "type": "string",
      "enum": ["skip", "rewrite", "dispatch_plan"]
    },
    "confidence": {
      "type": "string",
      "enum": ["low", "medium", "high"]
    },
    "domain_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Distinct-domain count the prompt's remediation would span. 0-1 -> rewrite path; >=2 -> dispatch_plan path (Phase 3/4 routing rule, uncontested by either source plan)."
    },
    "anchor_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Count of file/code/system anchors named in the prompt, read RELATIVE TO SCOPE (anchor-density) — not raw prompt length. Feeds Tier-0's pre-filter signal and is re-derived (not trusted) at Tier-1."
    },
    "assumption_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Count of unstated assumptions the classifier judges the prompt is making. Non-zero is what routes wild_assumption.present downstream in the generator schemas (§2, §3) but is NOT itself the wild_assumption field — the classifier flags COUNT; the generator that runs next produces the DESCRIPTION."
    },
    "ambiguity_reason": {
      "type": "string",
      "maxLength": 300,
      "description": "OPTIONAL free text — why the classifier judged the prompt ambiguous/multi-domain/assumption-laden. Requires Phase 5's semantic screen before any downstream injection (task brief item 4; Phase 2 acceptance test 3 cross-references this exact field)."
    }
  }
}
```

**Discrimination axes, as required by the brief:** `domain_count` (distinct-domain count),
`anchor_count` read as anchor-density-relative-to-scope (not a bare count of file mentions — Tier-0's
own pre-filter, per plan Fork 7, already discriminates on count==1 vs count>=2 combined with a
domain-keyword-cluster hit; Tier-1 re-derives the same axis under paid, not free, judgment), and
`assumption_count`. Raw prompt length is deliberately not a schema field — the plan states this
constraint verbatim in Phase 2's rubric description and both source plans agreed on it.

**Deterministic post-processing invariant (Phase 2 acceptance test 5) — not expressible as a pure JSON
Schema constraint on this object alone, so it is stated here as a binding contract on the *caller*, not
on the model:**

> `confidence == "low"` forces the **caller** (`prompt-optimizer-gate.sh`) to treat `action` as
> `"skip"` regardless of what the model returned in the `action` field. This is a deterministic
> override applied downstream of the tool call, not a constraint the model itself is trusted to honor
> unsupervised — matching the fail-open discipline the rest of this hook family uses (Gate 33's golden
> eval, the tribunal's own fail-closed/fail-open split) of never trusting a single model call as the
> sole gate on a mutating action.

A JSON Schema `if`/`then` conditional could partially express "if confidence==low, prefer action==skip"
but cannot express "override, don't merely prefer" — hence the explicit prose contract above rather than
a schema-only encoding.

---

## 2. Rewrite-generator schema — `emit_optimized_prompt`

Invoked when `domain_count <= 1` (Phase 3). Fast tier via `substrate-tier-map.json`'s `resolve_tier()`.

```json
{
  "type": "object",
  "required": ["rewritten_prompt", "explicit_constraints", "surfaced_missing_context", "wild_assumption"],
  "properties": {
    "rewritten_prompt": {
      "type": "string",
      "description": "The rewritten prompt text. Must preserve every constraint present in the original (Phase 3 acceptance test 2's mechanical diff check)."
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
          "description": "REQUIRED when present==true; omitted/empty when present==false. Free text describing the assumption. Requires Phase 5's semantic screen (task brief item 4)."
        },
        "confidence": { "type": "string", "enum": ["low", "medium", "high"] }
      }
    }
  }
}
```

`rewritten_prompt` / `persona` / `explicit_constraints` / `surfaced_missing_context` are **not** on
the brief's semantic-screen list (item 4 names exactly `rationale`, `ambiguity_reason`,
`tailored_brief`, `wild_assumption.description`) — deliberately, and the reason is structural, not an
oversight: on the rewrite path, `rewritten_prompt` is not injected as advisory narrative the assistant
might read as an instruction alongside its own reasoning — it **becomes** the working prompt for the
turn. `explicit_constraints` / `surfaced_missing_context` are short, schema-constrained list items
generated under a forced tool call, not open narrative. `wild_assumption.description` is the one place
genuinely open-ended, injection-shaped prose can arise on this path, and it is on the screen list.

---

## 3. Dispatch-plan-generator schema — `emit_dispatch_plan`

Invoked when `domain_count >= 2` (Phase 4). Balanced tier. Reads `agent-routing-matrix.json` read-only.

```json
{
  "type": "object",
  "required": ["domains", "per_domain", "wild_assumption"],
  "properties": {
    "domains": {
      "type": "array",
      "items": { "type": "string" }
    },
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
                  "description": "MUST resolve to a real, currently-enabled agent name, validated against the live roster before injection (plan §3 Fork 6, the roster-hallucination guard — an addition, not a replacement, to the matrix-citation check below). On validation failure the entry is dropped and confidence lowered, never injected with a hallucinated name."
                },
                "rationale": {
                  "type": "string",
                  "description": "Requires Phase 5's semantic screen."
                },
                "matrix_basis": {
                  "type": "string",
                  "description": "Cites the agent-routing-matrix.json task_class this recommendation is grounded in."
                }
              }
            }
          },
          "tailored_brief": {
            "type": "string",
            "description": "Requires Phase 5's semantic screen."
          }
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

**Never-dispatches invariant (Phase 4, restated as a schema-adjacent fact):** this tool definition
grants no `Agent`/`Bash`/`Write`/`Edit` capability — it is pure JSON emission. Nothing in this schema,
or in the generator that fills it, invokes the agents it names.

### 3a. Diff against `claude-orchestrate.sh`'s "decide" mode envelope — task brief item 3 / acceptance test 2

Read directly this session: [`plugins/ravenclaude-core/scripts/claude-orchestrate.sh`](../../../plugins/ravenclaude-core/scripts/claude-orchestrate.sh) lines 234–254. Its `decide`-mode
system prompt fixes this exact envelope shape:

```json
{
  "agents": [
    { "role": "<role>", "brief": "<brief>", "depends_on": [] }
  ],
  "parallelism": "sequential|parallel",
  "reasoning": "<= 200 chars"
}
```

**Where `emit_dispatch_plan` reuses it:** the core repeated shape — an array of
`{agent-identifier, instruction-text}` objects — is the same pattern in both schemas.
`recommended_agents[]` is structurally `agents[]` one level deeper (nested under `domains[]` rather
than flat).

**Where it diverges, and why (five points, each independently justified):**

| # | claude-orchestrate `decide` envelope | `emit_dispatch_plan` | Why the divergence is correct, not accidental |
|---|---|---|---|
| 1 | Flat `agents[]`, keyed by `role` | Nested `domains[] -> per_domain[].recommended_agents[]` | `emit_dispatch_plan`'s job is to identify **which domains** a prompt spans and ground each recommendation in a domain-scoped `matrix_basis`. The domain is the load-bearing grouping unit here; claude-orchestrate's caller already knows its domains and just needs a flat worker list. Flattening `emit_dispatch_plan` would strip the grouping `matrix_basis` needs to cite. |
| 2 | `depends_on: []` per agent + top-level `parallelism` (execution ordering) | No ordering fields anywhere | claude-orchestrate's envelope is **executable** — a host will actually invoke the named agents in the stated order. `emit_dispatch_plan` is asserted, by the Never-dispatches invariant above, to never invoke anything it names — it is advisory content for a human/assistant reading `additionalContext` in a later turn. Execution ordering is meaningless for content nobody programmatically walks. |
| 3 | No matrix/citation field at all | `matrix_basis` (required) | claude-orchestrate's nested `claude -p --tools ""` call is explicitly **untooled** — its own system prompt states *"You have NO tools — reason only"* and never mentions `agent-routing-matrix.json`. `emit_dispatch_plan`'s generator (Phase 4) is deliberately grounded in that matrix as a read-only consulted reference; `matrix_basis` is the citation field that grounding requires and claude-orchestrate structurally cannot have. |
| 4 | `role` — a free-form label the orchestrator may invent, not validated against any real roster | `agent` — MUST resolve to a real, currently-enabled agent name (roster-hallucination guard, Fork 6) | claude-orchestrate's `role` names a job for a host that will execute it directly, so an invented-but-reasonable role can still be useful. `emit_dispatch_plan`'s output is read by a human/assistant who may act on the name later without re-verifying it exists — the stricter contract earns the renamed field so the two are never confused at the schema-name level. |
| 5 | One `reasoning` string (<=200 chars) for the WHOLE plan | Per-recommendation `rationale`, no single top-level field | `emit_dispatch_plan` recommendations are matrix-grounded per-agent (see #3); a single blob covering a whole multi-domain plan would force Phase 5's semantic screen into an all-or-nothing degrade of the entire plan on one flagged phrase, rather than neutralizing just the offending recommendation. Finer grain is a direct consequence of Phase 5's per-field screening design, not an arbitrary choice. |

This diff is itself the artifact acceptance test 2 checks for — it was produced by reading the real
script, not guessed from its docstring comment.

---

## 4. Four `additionalContext` template variants

The four variants are `action ∈ {rewrite, dispatch_plan}` × `wild_assumption.present ∈ {true, false}`.
`action == "skip"` injects nothing (no template — the whole point of `skip` is that the mechanism is
invisible on that turn).

**Design invariant applied to every variant (task brief item 4 — "unmissable, derived-values-only"):**
every line is either a fixed string, a validated/typed value (an enum member, a bounded integer, a
literal file path), or a free-text field explicitly marked below as **[SCREENED]** — meaning Phase 5's
semantic screen runs on that field's content before this template is ever rendered with a real value.
No variant echoes raw generator/classifier free text with no structural wrapper — this mirrors the
existing SessionStart capability banner (`capability-orientation.sh`) and `compact-anchor.sh`'s own
practice of derived-labels/fixed-strings-only, cross-checked against [Gate
19](../../../plugins/ravenclaude-core/hooks/tests/) 's no-egress-of-raw-content family.

A field marked **[SCREENED]** below is rendered as: the screened text if it passed Phase 5's screen
unmodified, a stripped/rewritten version if the screen flagged and could safely rewrite it, or the
fixed fallback string *"content flagged for review — see the audit artifact"* if the screen forced a
full degrade (Phase 5's third disposition, per plan §Phase 5 item 1). Phase 0 freezes the **shape**;
the actual screening logic ships in Phase 5.

### Variant 1 — `action: "rewrite"`, `wild_assumption.present: false`

```
[RavenClaude prompt-optimizer] Your prompt was rewritten before this turn ran.

- Confidence: {confidence}
- Constraints preserved: {explicit_constraints_count}
- Missing context surfaced: {surfaced_missing_context_count}
- Why: {ambiguity_reason}                                            [SCREENED, optional]

Rewritten prompt used for this turn:
<rewritten-prompt>
{rewritten_prompt}
</rewritten-prompt>

Full record: .ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json
```

`{confidence}` — enum, safe verbatim. `{explicit_constraints_count}` / `{surfaced_missing_context_count}`
— derived integers (counts, not the list contents), safe verbatim. `{ambiguity_reason}` — **[SCREENED]**,
line omitted entirely when the classifier emitted none. `{rewritten_prompt}` — **not** screened (§2's
rationale: it is the working prompt, not injected narrative) but IS the content the assistant will act
on for the turn, delivered inline always (rewrite's output_shape is always inline, task brief item 7).

### Variant 2 — `action: "rewrite"`, `wild_assumption.present: true`

```
[RavenClaude prompt-optimizer] Your prompt was rewritten before this turn ran, and a wild
assumption was flagged. Call AskUserQuestion as your first tool call this turn, presenting
the flagged assumption below, before proceeding.

- Confidence: {confidence}
- Constraints preserved: {explicit_constraints_count}
- Missing context surfaced: {surfaced_missing_context_count}
- Why: {ambiguity_reason}                                            [SCREENED, optional]
- Flagged assumption (confidence: {wild_assumption.confidence}): {wild_assumption.description}   [SCREENED]

Rewritten prompt used for this turn:
<rewritten-prompt>
{rewritten_prompt}
</rewritten-prompt>

Full record: .ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json
```

Adds the fixed `AskUserQuestion`-as-first-tool-call instruction (plan Phase 5 item 3, tiebreak
Conflict 2 → A) and the required `{wild_assumption.description}` line — **[SCREENED]**, and if the
screen forces a full degrade the line renders as *"A wild assumption was flagged — see the audit
artifact for detail before proceeding."* rather than dropping the AskUserQuestion instruction (the
approval pause must survive even a fully degraded description).

### Variant 3 — `action: "dispatch_plan"`, `wild_assumption.present: false`

Two delivery sub-shapes, keyed by the frozen threshold (task brief item 7 / §5 below): **inline when
`recommended_agents` across the whole plan names ≤2 agents total; file-pointer mandatory above that.**

**Inline sub-shape (≤2 agents):**
```
[RavenClaude prompt-optimizer] This prompt spans {domain_count} domains — a dispatch plan
was drafted (advisory only; nothing was dispatched).

- Confidence: {confidence}
- Why: {ambiguity_reason}                                            [SCREENED, optional]

Domain: {domain}
  Recommended: {agent} — {rationale}                                 [SCREENED]
  Matrix basis: {matrix_basis}
  Brief: {tailored_brief}                                            [SCREENED]
  ... (repeated per domain/agent, ≤2 agents total)

Full record: .ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json
```

**File-pointer sub-shape (>2 agents, mandatory):**
```
[RavenClaude prompt-optimizer] This prompt spans {domain_count} domains — a dispatch plan
naming {total_agent_count} agents was drafted (advisory only; nothing was dispatched).

- Confidence: {confidence}
- Why: {ambiguity_reason}                                            [SCREENED, optional]
- Domains: {domain_1}, {domain_2}, ... ({domain_count} total)

Full plan: .ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json
Read that file before acting on this dispatch plan.
```

`{domain_count}` / `{total_agent_count}` — derived integers, safe verbatim. `{domain}` /
`{domain_1..n}` — the domain LABEL only (a short classifier-emitted string, not itself flagged for
screening by the task brief's four-field list; treated as low-risk relative to `rationale`/
`tailored_brief` because domain labels are short category names, not free narrative). `{agent}` —
validated against the live roster (§3's guard) before this template ever sees it, so it is a real
agent name, not arbitrary text. `{rationale}`, `{tailored_brief}` — **[SCREENED]**, per-entry (not
one blob — a single flagged entry degrades only that entry's line, matching §3a point 5's reasoning).

### Variant 4 — `action: "dispatch_plan"`, `wild_assumption.present: true`

Same two delivery sub-shapes as Variant 3, each additionally carrying the fixed AskUserQuestion
instruction and the wild-assumption line, exactly as Variant 2 adds them to Variant 1:

**Inline sub-shape (≤2 agents):**
```
[RavenClaude prompt-optimizer] This prompt spans {domain_count} domains — a dispatch plan
was drafted (advisory only; nothing was dispatched), and a wild assumption was flagged.
Call AskUserQuestion as your first tool call this turn, presenting the flagged assumption
below, before acting on this plan.

- Confidence: {confidence}
- Why: {ambiguity_reason}                                            [SCREENED, optional]
- Flagged assumption (confidence: {wild_assumption.confidence}): {wild_assumption.description}   [SCREENED]

Domain: {domain}
  Recommended: {agent} — {rationale}                                 [SCREENED]
  Matrix basis: {matrix_basis}
  Brief: {tailored_brief}                                            [SCREENED]
  ... (repeated per domain/agent, ≤2 agents total)

Full record: .ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json
```

**File-pointer sub-shape (>2 agents, mandatory):**
```
[RavenClaude prompt-optimizer] This prompt spans {domain_count} domains — a dispatch plan
naming {total_agent_count} agents was drafted (advisory only; nothing was dispatched), and
a wild assumption was flagged. Call AskUserQuestion as your first tool call this turn,
presenting the flagged assumption below, before reading or acting on the full plan.

- Confidence: {confidence}
- Why: {ambiguity_reason}                                            [SCREENED, optional]
- Flagged assumption (confidence: {wild_assumption.confidence}): {wild_assumption.description}   [SCREENED]
- Domains: {domain_1}, {domain_2}, ... ({domain_count} total)

Full plan: .ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json
Read that file before acting on this dispatch plan.
```

### 4a. Semantic-screen field summary (task brief item 4, restated as one table)

| Field | Appears in | Requires Phase 5 semantic screen? |
|---|---|---|
| `ambiguity_reason` | All four variants (optional line) | **Yes** |
| `wild_assumption.description` | Variants 2 and 4 (required when present) | **Yes** |
| `rationale` (per recommended agent) | Variants 3 and 4 | **Yes** |
| `tailored_brief` (per domain) | Variants 3 and 4 | **Yes** |
| `rewritten_prompt` | Variants 1 and 2 | No — becomes the working prompt itself, not injected narrative (§2) |
| `persona` / `explicit_constraints` / `surfaced_missing_context` | Variants 1 and 2 (counts/labels only in the template; full content lives in the audit artifact) | No — short, schema-constrained values, not open narrative |
| `domain` / `agent` / `matrix_basis` / counts / `confidence` enums | All variants | No — enum members, validated roster names, or derived integers |

This is the exact four-field list the task brief names (`rationale`, `ambiguity_reason`,
`tailored_brief`, `wild_assumption.description`) — confirmed against every template variant above, not
asserted independently of them.

---

## 5. On-disk audit-artifact path convention

**Frozen path:** `.ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json`

### Precedent, verified by reading real files rather than assumed

This repo has **two** distinct existing shapes for a component's own audit-artifact path, and the
frozen path is a hybrid of both — worth stating honestly rather than claiming a single clean precedent:

**Shape A — component-first, no session subdirectory.** The most directly analogous precedent named
in the task brief: `adaptive-run-classifier`. Read directly this session,
[`plugins/ravenclaude-core/skills/adaptive-run-classifier/SKILL.md`](../../../plugins/ravenclaude-core/skills/adaptive-run-classifier/SKILL.md)
line 160 and line 189:

> *"`enabled: true` — `loadRunConfig()` invokes the classifier (one Haiku call), persists the returned
> envelope to `.ravenclaude/runs/run-classifier/<timestamp>.json`... Every classifier verdict is logged
> to `.ravenclaude/runs/run-classifier/<UTC-timestamp>.json` (parallel to
> `.ravenclaude/runs/thing/decisions/`)."*

That is `.ravenclaude/runs/<component-name>/<UTC-ts>.json` — component name first, one flat directory,
**no per-session subdirectory at all**. The same shape is used by the command-review tribunal
(`.ravenclaude/runs/thing/decisions/`, `.ravenclaude/runs/thing/runaway/`) and by
`archive-branch.sh`/`cleanup-worktrees` (`.ravenclaude/runs/branch-archive/`,
`.ravenclaude/runs/branch-cleanup/`).

**Shape B — session-first, flat file with a component-prefixed name.** `precompact-digest.sh` (grepped
directly this session): `.ravenclaude/runs/<session>/precompact-digest-<timestamp>.md`. Also
`hook-events.jsonl` (`.ravenclaude/runs/${CLAUDE_SESSION_ID:-unknown}/hook-events.jsonl`) and
`parallelism-observations.json` (`.ravenclaude/runs/<session>/parallelism-observations.json`) — both
session-first, but as a **flat file directly under the session directory**, not inside a further
component subdirectory.

**The frozen `prompt-optimizer` path is neither shape exactly — it is session-first (Shape B) *and*
uses a component subdirectory (Shape A's grouping), i.e.**
`.ravenclaude/runs/<session>/prompt-optimizer/<UTC-ts>.json`. This is a real, stated divergence from
both individual precedents, not a clean match to either — recorded here rather than silently claimed
as "the same pattern `adaptive-run-classifier` uses" (it is not; that skill's own path has no session
directory at all). The rationale for the hybrid, stated so a later reader does not have to guess it:
`prompt-optimizer` fires many times per session (once per qualifying `UserPromptSubmit`, unlike
`adaptive-run-classifier`'s once-per-workflow-run cadence), so grouping by session first keeps a
session's own record contiguous and easy to `Read` in one glob during that session (matching Shape B's
motivation); nesting under a `prompt-optimizer/` subdirectory inside that session (borrowing Shape A's
per-component grouping) keeps the directory from colliding with `hook-events.jsonl` and any future
per-session artifact another component adds, and gives the file-pointer delivery shape (§4, Variant
3/4's >2-agent case) an unambiguous glob (`.ravenclaude/runs/<session>/prompt-optimizer/*.json`) to
point the assistant's `Read` at, distinct from every other artifact under that session directory.

---

## 6. Posture-knob schema — `prompt_optimizer` under `.ravenclaude/comfort-posture.yaml`

**Frozen shape:**

```yaml
prompt_optimizer:
  enabled: false
  mode: shadow # shadow | advisory | binding-context
```

### 6a. Diff against `dispatch_config`'s and `cheap_lane`'s real, existing shapes — verified, not asserted (task brief item 6 / acceptance test 3)

Both real files were read directly this session.

**`cheap_lane` — a genuine nested `comfort-posture.yaml` key.**
[`plugins/ravenclaude-core/templates/comfort-posture-balanced.yaml`](../../../plugins/ravenclaude-core/templates/comfort-posture-balanced.yaml)
lines 95–97:

```yaml
cheap_lane:
  mode: off
  tier: fast # fast (default) | balanced — the Grok tier for delegated work
```

**`dispatch_config` — NOT a nested `comfort-posture.yaml` key.** It is a **standalone top-level JSON
file**, `.ravenclaude/dispatch-config.json`, whose shipped template is
[`plugins/ravenclaude-core/skills/agent-dispatch-evaluator/templates/dispatch-config.json`](../../../plugins/ravenclaude-core/skills/agent-dispatch-evaluator/templates/dispatch-config.json):

```json
{
  "schema_version": "1",
  "enabled": false,
  "mode": "shadow",
  "subagent_type_allowlist": ["Explore", "statusline-setup", "claude"],
  "downgrade_blocked_types": [],
  "quality_sampler": { "rate": 0.2, "judge_model": "claude-haiku-4-5-20251001", "use_batch_api": true },
  "latency_circuit_breaker": { "median_ms_threshold": 1500, "window_size": 20 },
  "tribunal_seat_mode": "shadow",
  "async_mode": false,
  "rationale": "default baseline — disabled"
}
```

**A correction to the plan's own Fork 4 rationale, found by verifying rather than trusting the citation
list.** `plan.md` §3 Fork 4 justifies the nested shape by citing three precedents in one parenthetical —
*"`dispatch_config`, `cheap_lane: {mode, agent}`, `context_handoff: {mode, spawn, ...}`"* — phrased as if
all three are the same kind of thing (a nested key inside `comfort-posture.yaml`). Verified: **two of
the three are** (`cheap_lane`, and `context_handoff` per the `CLAUDE.md` v0.297.0 milestone's own
description of that key's shape) — **`dispatch_config` is not**; it lives in a separate file entirely.
The parenthetical's implicit claim ("all three live in `comfort-posture.yaml`") is inaccurate for
`dispatch_config` specifically. This does not undermine Fork 4's conclusion — see below — but it should
not be repeated as written.

**A second, smaller inaccuracy also worth naming exactly:** Fork 4 cites `cheap_lane: {mode, agent}`,
but the real, currently-shipped template (above) has `{mode, tier}` — no `agent` key. (`cheap_lane.agent`
does exist as a real, documented posture knob per the `CLAUDE.md` v0.305.0 milestone, but it is not
present in the *shipped seed template* read above — a consumer sets it by hand, it is not pre-seeded.)
Neither inaccuracy changes the structural conclusion below, but "verified, not asserted" means naming
them rather than silently repeating the plan's citation as if it had been re-checked.

**What DOES hold, confirmed by direct comparison:**

1. **The field-naming pattern `{enabled: <bool>, mode: <enum>}` is real and is shared by
   `dispatch_config.json` and the frozen `prompt_optimizer` shape — same two field names, same
   semantics (a master on/off switch plus a rollout-stage enum), and `dispatch_config.json`'s literal
   default value `"mode": "shadow"` is the exact string `prompt_optimizer`'s own frozen default reuses.**
   This is real, verified precedent for the specific value `"shadow"` as a rollout-stage enum member in
   this repo, not merely a plausible-sounding string invented for this plan.
2. **The "small nested object, not a flat scalar, for a multi-field knob" convention is real and is
   shared by `cheap_lane` (a genuine nested `comfort-posture.yaml` key) and the frozen
   `prompt_optimizer` shape** — both are `{primary-toggle, secondary-enum}` pairs living directly under
   `comfort-posture.yaml`. `prompt_optimizer`'s placement (nested inside `comfort-posture.yaml`, not a
   standalone file) follows `cheap_lane`'s placement precedent specifically — not `dispatch_config`'s,
   which is a separate file for a different reason (it is machine-written/read by
   `evaluate-dispatch.js`'s own workflow-wrapper binding, a distinct mechanism this build does not
   touch or extend).
3. **`prompt_optimizer` does not need a `cheap_lane`-style secondary tier axis** (`fast`/`balanced`)
   because its Tier-1 classifier is fixed-cheap (Haiku only, per Phase 2) — there is no cost/quality
   lever to expose the way `cheap_lane.tier` exposes one for Grok delegation. The three-way `mode` enum
   (`shadow`/`advisory`/`binding-context`) carries the equivalent "how aggressively does this behave"
   axis in a single field instead of a stacked toggle+tier, which is why the frozen shape has exactly
   two keys rather than three.

**Conclusion:** the posture schema IS structurally consistent with the real, verified shapes of both
cited precedents — `{enabled, mode}` naming from `dispatch_config.json`, nested-nonscalar placement
from `cheap_lane` — but the plan's own citation of the *reason* ("all three precedents are nested
`comfort-posture.yaml` keys") was not fully accurate on inspection, and that correction is recorded
here rather than silently repeated.

---

## 7. Dispatch-plan delivery-shape threshold

**Frozen constant: `2`.**

- `rewrite` `output_shape` is **always inline** (Variant 1/2, §4).
- `dispatch_plan` `output_shape` is **inline only when the plan names ≤2 agents total** across all
  `per_domain[].recommended_agents[]` entries combined (Variant 3/4's inline sub-shape, §4).
- Above 2 agents, **file-pointer delivery is mandatory** — a short summary + a pointer to the on-disk
  audit artifact (§5), instructing the assistant to `Read` that file before acting (Variant 3/4's
  file-pointer sub-shape, §4).

This is the exact number Phase 5 acceptance test 4 will check against literally: *"a fixture dispatch
plan naming 4 agents is asserted to produce file-pointer delivery... a fixture naming 1 agent is
asserted to produce inline delivery."* The boundary case — exactly 2 agents — is inline (the threshold
is `≤2`, not `<2`); exactly 3 is the first file-pointer-mandatory case. A later phase's fixture set
should include the boundary (2 agents, exactly) and the first file-pointer case (3 agents, exactly) as
explicit test cases, not just the 1-agent and 4-agent examples named in Phase 5's own acceptance test.

---

## Acceptance-test cross-reference (self-check against the task brief's four tests)

1. **All four `additionalContext` template variants, exact text, each stating which free-text
   sub-fields require the semantic screen** → §4 (all four variants with exact template text) + §4a
   (the four-field summary table, cross-checked against every variant above it).
2. **Dispatch-plan schema diffed against `claude-orchestrate.sh`'s real "decide" mode envelope, read
   from the actual script, divergence justified in writing** → §3a (the script was read at
   `plugins/ravenclaude-core/scripts/claude-orchestrate.sh:234-254`; five-point diff table with a
   stated reason per divergence, plus the one point of genuine reuse).
3. **Posture schema diffed against `dispatch_config`'s and `cheap_lane`'s real, existing shapes, found
   by reading real files, confirming structural consistency** → §6a (`comfort-posture-balanced.yaml:95-97`
   and `agent-dispatch-evaluator/templates/dispatch-config.json` both read directly; structural
   consistency confirmed on two independent axes, with two inaccuracies in the plan's own citation
   named explicitly rather than silently inherited).
4. **The inline/file-pointer threshold written down as an explicit, testable number** → §7 (`2`,
   stated as `≤2 inline`, `>2 file-pointer mandatory`, with the two boundary fixture cases named).

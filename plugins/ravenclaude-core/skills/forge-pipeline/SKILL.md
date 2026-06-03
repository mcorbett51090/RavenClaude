---
name: forge-pipeline
description: "The FORGE gated-planning pipeline that /forge runs: depth-scaled gates that turn any idea into a two-panel-reviewed, critic-checked, tiebroken, routed plan. Mimics Claude Code Ultraplan's deep-plan loop and improves it with cross-model divergence, a fact-verification gate, a correlated-error critic, and a binding tribunal for conflicts."
---

# Skill: forge-pipeline

> Invoked by **`/forge`**. This skill holds the gate logic; the command file is the thin entry.
> The whole pipeline is the formalization of the hand-run pattern: *clarify → research+verify →
> two divergent panels (different models) → critic → gap-analysis → per-conflict expert tiebreak →
> red-team → synthesize → route → exit.*

## 0. Provenance & the two influences

- **Claude Code Ultraplan (deep variant)** — community-reported pipeline: parallel explore agents
  → synthesize → **single same-model critic** → revise → emit; plus cloud-vs-local routing and the
  `ExitPlanMode`/cloud handoff. `[unverified — community reverse-engineering; Ultraplan is a research
  preview, behavior changes]`. FORGE reproduces this shape and **improves it**: cross-model two-panel
  divergence (research shows cross-model debate > self-critique), a fact-verification gate Ultraplan
  doesn't expose, and a binding tribunal instead of an opaque merge.
- **OpenAI Codex** — its gate is a *graduated-trust ladder* (read-only → workspace-auto → full-access)
  + explicit-only subagents. FORGE borrows the ladder (it maps onto routing/exit + comfort-posture)
  and the explicit-spawn discipline (already enforced by `guard-recursive-spawn.sh`).

## 1. Depth ladder — **the gate SET scales with depth** (tiebreak F4)

A 0-call gate is just overhead, so depth *collapses* the pipeline, it doesn't thin it. `--depth quick`
is the **default** (cheap-by-default so the command is used for *every* idea — tiebreak F1).

| Depth | Gates run | ~calls | Use for |
|-------|-----------|--------|---------|
| **micro** | G0 · G6 · G7 | 1-2 | a truly atomic idea needing only a structured sanity pass |
| **quick** *(default)* | G0 · G1-lite · G2 · G3 · G6 · G7 | 3-5 | most ideas (a new skill, a hook tweak, a knowledge doc) |
| **standard** | + G4a critic · G4b tiebreak · G5 red-team | 6-10 | a non-trivial multi-file change |
| **deep** | standard, no conflict cap, 2nd red-team, **checkpoint/resume** | 11-18 | a substantial multi-plugin build |

## 2. The gates

Each gate is **fail-closed** (no advance without an explicit pass or a recorded waiver) and **emits a
typed artifact** into the Sága run dir `.ravenclaude/runs/forge/<slug>/`. Only `plan.md` (G6) is a
candidate to land in the repo; the per-gate artifacts stay in the run dir (avoids `docs/` sprawl).

### G0 — Scope / Clarify + routing triage
Ask ≤2-3 **batched** clarifying questions via `AskUserQuestion` (auto-routes through the
decision-review hook). Produce a one-paragraph scoped intent, an explicit out-of-scope list, a named
owner, and a one-line success signal. **Fast triage:** if the idea is plainly large + cloud-suited +
privacy-clean, offer to hand to Ultraplan *now* before spending tokens. → `scope.md`.

### G1 — Research + Fact-Verification (TIERED — tiebreak F2)
Build a claims table of every load-bearing fact the plan rests on. **Tiered enforcement:**
- **BLOCK** (cannot advance): a claim about anything **outside the repo** — third-party API behavior,
  tool/SDK versions, pricing, performance numbers — without **either** a this-session source (`url` +
  retrieval date) **or** an `[unverified — training knowledge]` marker carrying a claim-specific
  one-sentence justification (why it can't be verified now + what route would verify it).
- **WARN, continue**: a repo-structural claim (a file exists, a skill is present, a gate slot is free)
  the model **just confirmed via a visible in-session tool call** — that *is* grounded; demanding a
  second citation is theater. If it wasn't confirmed in-session, it's BLOCK-tier.
- **Skip** entirely at micro depth.
→ `claims-table.md` (columns: claim · tier · source/marker · settling-gate). This is the accuracy
discipline from `docs/accuracy-near-guarantee-design.md` applied to planning: a plan must rest on
**tested facts, not assumptions**.

### G2 / G3 — Two divergent panels (different models, in parallel)
Dispatch **one worker subagent per panel**, models pinned per `--models` (B **must** differ from A —
cross-model divergence is the improvement over Ultraplan's same-model critic). Each panel returns a
complete phased plan that **must** include: per-phase acceptance tests + pre-build gates, a
**dependency DAG** (what blocks what; what parallelizes; the critical path), and **≥2 alternative
approaches** with one-line trade-offs (the Ultraplan deep-plan structural inheritance — a plan, not a
task list). Panel **B additionally emits a gap-delta**: every place A and B disagree or one is silent,
plus a note if A's sequencing over-serializes. → `plan-A.md`, `plan-B.md`, `gap-delta.md`.

### G4a — Critic (standard+; tiebreak F5) — catches *correlated* error
A subagent that did **not** author either plan reads **both** and does what a gap-analysis structurally
cannot: find **where A and B AGREE on something that's wrong** (shared-anchoring / correlated cross-model
error — invisible to a disagreement-keyed gap-delta). It also attacks the **premise of the idea itself**
and emits a probability×impact **risk matrix**. It produces **no third plan**. Distinct from red-team:
the critic attacks the *input plans' shared premises before synthesis*; red-team attacks the *synthesized
plan's execution failure modes*. → `critic-brief.md`.

### G4b — Per-conflict expert tiebreak (standard+)
For each real conflict (from `gap-delta.md` + `critic-brief.md`): a **clean yes/no** routes to the
tribunal — `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/thing-decide.py` (binding/advisory/off per posture;
high-blast/`defer`/preference → ask Matt). A **substantive design fork** gets **one expert subagent**
ruling `A` / `B` / `synthesis` + a one-line rationale. Cap at the **top-N highest-impact** conflicts
(N≈5 at standard; uncapped at deep). The rest are recorded "minor — defaulted to A". → `tiebreaks.md`.

### G5 — Red-team / Risk (standard+, unless `--no-redteam`)
A subagent surfaces **≥5 real, reproducible** failure modes — each with a trigger/repro, severity, and
a mitigation *or* an accepted-risk waiver. **Not** performative dissent (research warns devil's-advocate
agents fabricate opposition — demand real, reproducible modes). Reference the G4a risk matrix; verify,
don't duplicate. An unmitigated **high-severity** with no waiver → loop back to G2/G4. → `red-team.md`.

### G6 — Synthesize
Merge into a single `plan.md`: the reconciled **dependency DAG**, the **risk matrix** (critic +
red-team), the **alternatives** section, every tiebreak verdict, every red-team mitigation. No dangling
conflict; every G1 `[unverified]` claim carries the step that will settle it. This is the authoritative
artifact.

### G7 — Route (deterministic — no model judgment)
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/forge-route.py --plan <run-dir>/plan.md --size
small|medium|large [--research-done] [--privacy clean|sensitive]` → JSON:
- **`execution`** ∈ `use_local` | `consider_ultraplan` | `lean_ultraplan` (three-signal rubric;
  privacy=sensitive is a hard cap to local).
- **`landing`** ∈ `main` | `pr` — a plan carrying an **engineering pre-commitment** (a concrete
  version-bump target, a reserved `Gate N` slot, a `.repo-layout.json`/`allowed_globs` edit, a named
  PR/branch target) lands via a `forge/<slug>` **draft PR**; a pure design/analysis plan lands straight
  to **main** (tiebreak F3 — a stale pre-commitment must not sit canonically in main).

The script also runs `--self-test` (its own fixtures) — a registered, citable canonical route.

### G8 — DoD / Exit
Verify the plan carries its definition-of-done (acceptance tests, version bumps, layout allow-list,
prettier/audit-gates per `AGENTS.md`). Then the single exit:
- `execution=use_local` → call **`ExitPlanMode(plan.md)`**.
- `execution=lean_ultraplan`/`consider_ultraplan` → **decline `ExitPlanMode` with a "sending to
  Ultraplan" note** (the harness opens the browser session, seeded with `plan.md`).
- `reject` (G5 left an unmitigated blocker, or G0 scope is incoherent) → report the blocker, no exit.
- Land `plan.md` per the G7 `landing` verdict (main, or open the draft PR).

## 3. Resume / checkpoint (deep depth only — tiebreak F6)
At **deep** depth, each gate writes its artifact **atomically** (`<artifact>.tmp` → rename on success),
so a half-written file is never a valid skip signal. `/forge --resume <slug>` skips any gate whose
artifact exists and is **non-empty**, restarting from the first missing/empty one. Resume is scoped to
the **same `<slug>`** (same inputs); changed inputs mint a new slug. micro/quick/standard always restart
from scratch (a restart there costs only a few calls — not worth the partial-state complexity).

## 4. Cost / latency controls
- **Depth default `quick`** + the gate-set scaling above are the primary levers.
- **Conflict cap** top-N≈5 at standard (uncapped only at deep).
- **Claims cache:** G1 entries are content-addressed by `(claim, source-url)`; a re-run reuses verified
  claims whose retrieval date is < 90 days (matches the repo's knowledge-freshness contract). WebFetch
  is already 15-min URL-cached.
- **Parallel where independent** (G1 explore subagents; G2/G3 panels = one batch of `Task` calls),
  **serial where dependent** (G4→G5→G6). Wall-clock ≈ the slowest panel, not the sum.
- **Brakes reused:** `runaway-brake.sh` (PreToolUse call caps) + `guard-recursive-spawn.sh` (tree
  topology) fire automatically — a thrashing gate trips the brake deterministically.
- **Fail-fast:** G1 BLOCK and a G7 `reject` short-circuit the expensive G2–G6 core when an idea is
  under-specified or non-viable.

## 5. Shared rubric (tiebreak F7 — don't re-author)
The two-panel lens definitions, the P0/P1 severity rubric, and the routing-signal schema are the **same**
ones `.claude/workflows/two-panel-plan-review.js` uses. FORGE shares those constants (one source of
truth) and adds the scope, critic, depth-tiering, and routing **layers** — it does **not** runtime-compose
that workflow (it's a standalone harness entry point that consumes a *pre-written* strategic plan, a
different input contract than FORGE's "raw idea → plan").

## 6. Honest scope
FORGE makes a plan **divergently reviewed, fact-grounded, critic-checked, and routed** — it raises the
floor on plan quality and shifts the odds against a confidently-wrong plan. It does **not** guarantee the
plan is correct (no process does); the critic + red-team + tiebreak reduce, not eliminate, the residual.
Stating otherwise would be the over-claim the accuracy work in this repo exists to prevent.

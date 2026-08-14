---
name: forge-pipeline
description: "The FORGE gated-planning pipeline that /forge runs: depth-scaled gates that turn any idea into a two-panel-reviewed, critic-checked, tiebroken, routed plan. Mimics Claude Code Ultraplan's deep-plan loop and improves it with cross-model divergence, a fact-verification gate, a correlated-error critic, and a binding tribunal for conflicts."
---

# Skill: forge-pipeline

> Invoked by **`/forge`**. This skill holds the gate logic; the command file is the thin entry.
> The whole pipeline formalizes the hand-run pattern: *clarify → research+verify → two divergent
> panels (different models) → critic → gap-analysis → per-conflict expert tiebreak → red-team →
> synthesize → route → exit.*

**This file is the always-loaded core: the artifact contract, the depth ladder, and the gates every
depth runs.** Load a reference file **only** when the depth or the situation calls for it:

| Load | When | Holds |
|---|---|---|
| [`reference/gates-standard.md`](reference/gates-standard.md) | depth ≥ **standard** | the **domain-prior lens** (G2/G3) · G4a critic · G4b tiebreak · G5 red-team |
| [`reference/deep-resume.md`](reference/deep-resume.md) | depth = **deep**, or `--resume` | checkpoint/resume + the uncapped-conflict rules |
| [`reference/regen-discipline.md`](reference/regen-discipline.md) | **G8 only**, and only if a phase adds/removes a skill, agent, or other counted artifact | the marketplace count/regen DoD criteria |
| [`reference/provenance.md`](reference/provenance.md) | a human asks *why* FORGE is shaped this way | provenance, the shared rubric, honest scope |

Never load a reference file the depth doesn't reach — that is the point of the split.

## 0. The artifact contract — **read this before dispatching any gate**

Every gate's payload lives **on disk**; only a **receipt** crosses back into this session.

- The gate's subagent **writes its own artifact** to `.ravenclaude/runs/forge/<slug>/<artifact>.md`.
  Put the absolute run-dir path in its brief. **The orchestrator does not write gate artifacts and
  does not ask a subagent for its artifact's text.**
- The subagent returns **only** this receipt — no plan body, no prose report:

  ```
  ---RESULT_START---
  {"gate":"G3","status":"pass|fail|waived","artifact":"<abs path>","bytes":N,
   "digest":["≤5 one-line findings a downstream gate must route on"],
   "blockers":[],"confidence":0.0-1.0}
  ---RESULT_END---
  ```

- A downstream gate that needs an upstream payload is handed the **path** and **reads it itself**.
  Never paste `plan-A` / `plan-B` / `critic-brief` / `red-team` text into a brief.
- **Fail-closed is preserved:** a gate advances on `status` + `blockers` + the artifact existing and
  being non-empty. The payload was never the pass signal — so routing on a receipt loses nothing.
- **The Sága run record** (`commands/forge.md` Step 5) = each receipt appended verbatim (+ `model` /
  `subagent_type`, `"generic"` today / `effort`) to `.ravenclaude/runs/forge/<slug>/run-log.jsonl`, one
  line per gate. A pure append of data in hand.

**Why this is load-bearing.** A relayed artifact is paid for twice — once on return, then again in
every later turn's resent context — and relaying pins two complete plans *plus* the critic *plus* the
red-team in context through G6. Reading from disk hands each downstream gate the **identical bytes**
at a fraction of the resident context. This buys efficiency with **no** loss of gate input; it is the
single largest cost lever in the pipeline, and it is free.

## 0.5 Provisioning — **always a worktree, always checkpointed** (every depth)

Before G0 at **every** depth, FORGE provisions an isolated git worktree and checkpoints the run's
tracked work at each gate boundary. This is a **deterministic script step, not an LLM gate** — it
dispatches no subagent and costs ~0 tokens, so it runs identically at `micro` through `deep`.

**Provision (once, at run start).** Run
`bash ${CLAUDE_PLUGIN_ROOT}/scripts/forge-worktree.sh init <slug>` — it creates (or, on a
`--resume`, **reuses**) the branch `forge/<slug>` in the worktree `.claude/worktrees/forge-<slug>/`.
The plan's landing (G7 `landing=pr` writes `plan.md` there) **and** any subsequent implementation
happen on that branch, isolated from the primary checkout — which is exactly what the `worktree_guard`
posture nudges toward, and what keeps two concurrent `/forge` runs (or a forge run + the user's own
edits on `main`) from stomping one shared tree. It prints a JSON receipt and, on success, a
`FORGE_WORKTREE <abs-path>` line; hand that path to the implementation phase.

**Checkpoint (at each gate boundary and at exit).** After each gate and before the single exit, run
`bash ${CLAUDE_PLUGIN_ROOT}/scripts/forge-worktree.sh checkpoint <slug> <gate>` — it commits the
worktree's tracked changes as `forge(<slug>): checkpoint — <gate>`. During pure planning most
checkpoints are **no-ops** (the run-dir under `.ravenclaude/runs/forge/<slug>/` is git-ignored, so
there is nothing tracked to commit); the checkpoints that carry weight are the landed `plan.md` (G6/G7)
and the implementation phases, where a commit-per-boundary makes an interrupted run recoverable from
the branch. This is the **git-checkpoint layer**; it composes with — does not replace — the deep-depth
atomic-write/resume in [`reference/deep-resume.md`](reference/deep-resume.md), which is the gate-skip
layer over the (git-ignored) run-dir.

**Fail-safe by contract — provisioning is a safety anchor, never a gate.** Every case the script
can't provision exits 0 with a `status` receipt and FORGE **proceeds in the primary checkout**:
`not-a-git-repo`, `already-in-worktree` (the nesting guard — a FORGE run launched from inside a linked
worktree does not nest a second one), or opted out. **Opt-out:** `forge_worktree: off` in
`.ravenclaude/comfort-posture.yaml`, or the `FORGE_WORKTREE=off` env var (absent ⇒ **on**, the
default). The script is idempotent, `bash`-3.2-safe, and carries a `--self-test` (its own scratch-repo
fixtures) — a registered, citable canonical route, mirroring `forge-route.py --self-test`.

## 1. Depth ladder — **the gate SET scales with depth** (tiebreak F4)

A 0-call gate is just overhead, so depth *collapses* the pipeline, it doesn't thin it. `--depth quick`
is the **default** (cheap-by-default so the command is used for *every* idea — tiebreak F1).

| Depth | Gates run | ~calls | Also load | Use for |
|-------|-----------|--------|-----------|---------|
| **micro** | G0 · G6 · G7 · G8 | 1-2 | — | a truly atomic idea needing only a structured sanity pass |
| **quick** *(default)* | G0 · G1-lite · G2 · G3 · **G3b** · G6 · G7 · G8 | 3-5 | — | most ideas (a new skill, a hook tweak, a knowledge doc) |
| **standard** | + G4a · G4b · G5 | 6-10 | `gates-standard.md` | a non-trivial multi-file change |
| **deep** | standard, no conflict cap, 2nd red-team, checkpoint/resume | 11-18 | `gates-standard.md` + `deep-resume.md` | a substantial multi-plugin build |

**Before G0 at every depth**, §0.5 provisioning runs (worktree + checkpoints) — a deterministic
script step, **not** counted in `~calls` (it dispatches no subagent).

## 2. The gates every depth runs

Each gate is **fail-closed** (no advance without an explicit pass or a recorded waiver) and emits a
typed artifact into the Sága run dir `.ravenclaude/runs/forge/<slug>/`, per §0. Only `plan.md` (G6)
is a candidate to land in the repo; per-gate artifacts stay in the run dir (avoids `docs/` sprawl).

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

**Every row also carries `kind` ∈ `observation` | `inference`** — the gap that let a false premise
through. G1's BLOCK/WARN split keys on *provenance* ("is it sourced?"), and the costliest false claim
this pipeline has seen **was** sourced: an in-session `curl` returned 404, and from that true
OBSERVATION an agent drew the false INFERENCE "the decoder is broken, every visitor is affected" —
then built 16 files on it. Grounding an observation ≠ grounding an inference drawn from it. Type each
row with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/classify_claim.py` (grammatical, **upward-only** — an author may raise a row
to `inference`, never lower it) and settle any `inference` a build phase depends on at **G3b**.

→ `claims-table.md` (columns: claim · **kind** · tier · source/marker · settling-gate). This is the accuracy
discipline from `docs/accuracy-near-guarantee-design.md` applied to planning: a plan must rest on
**tested facts, not assumptions**.

### G2 / G3 — Two divergent panels (different models, in parallel)
Dispatch **one worker subagent per panel**, models pinned per `--models` (B **must** differ from A —
cross-model divergence is the improvement over Ultraplan's same-model critic). Each panel **writes**
a complete phased plan that must include: per-phase acceptance tests + pre-build gates, a
**dependency DAG** (what blocks what; what parallelizes; the critical path), **≥2 alternative
approaches** with one-line trade-offs (the Ultraplan deep-plan structural inheritance — a plan, not a
task list), and — **required, this is load-bearing** — a `depends_on_claims: [<row ids>]` line on every
phase, naming the `claims-table.md` rows that phase rests on. A phase resting on nothing says
`depends_on_claims: []` explicitly; silence is not an answer.

⛔ **Do not treat this as bookkeeping.** G3b's trigger READS this field, so a plan that omits it makes
the premise gate structurally unsatisfiable — the gate runs, finds no claim edges, and passes green
while checking nothing. That exact defect shipped in a draft of this design: the trigger was specified
against a field the plan schema never emitted, and the accompanying gate supplied it in a **synthetic
fixture**, so the gate would have gone green while the mechanism was inert in production. A fixture is
not a wiring proof. Panel **B additionally writes a gap-delta**: every place A and B disagree or one is
silent, plus a note if A's sequencing over-serializes. → `plan-A.md`, `plan-B.md`, `gap-delta.md`.

Both panels are dispatched in **one batch** (wall-clock ≈ the slower panel, not the sum). Per §0 each
returns a receipt only. **Panel B is handed `plan-A.md`'s path** and reads it for the gap-delta —
never A's text inline, and B must draft *its own* plan **before** reading A, or the divergence the
whole design rests on collapses into anchoring.

### G3b — Premise gate (deterministic — no model judgment)
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/premise-gate.py --run-dir <run-dir>` after the panels, **before** G6. Fails closed
when a phase's `depends_on_claims` names a row that is `kind: inference` **and** unsettled **and** the
phase's blast radius is over the floor. Three exits, none of which is "block and stop": run the probe
(`cost ≤ CHEAP_FLOOR`), run the **cheapest partial** (mandatory when the full kill-shot needs prod or
credentials), or **owner-gate** it — which *reshapes* rather than blocks: citing phases are capped to
one reversible file and flagged, non-citing work proceeds. Every exit other than a run probe writes an
inline `[unverified — premise not disconfirmed: <reason>]` marker into the artifact.
Full contract, conjuncts and escape syntax: [`reference/premise-gate.md`](reference/premise-gate.md).

### G6 — Synthesize
**Dispatch this as a subagent** and hand it the run-dir path; it reads the gate artifacts from disk
and merges them into a single `plan.md`: the reconciled **dependency DAG**, the **risk matrix**
(critic + red-team, when those gates ran), the **alternatives** section, every tiebreak verdict, every
red-team mitigation. No dangling conflict; every G1 `[unverified]` claim carries the step that will
settle it. This is the authoritative artifact — and the only one the orchestrator later reads in full
(once, at G8).

### G7 — Route (deterministic — no model judgment)
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/forge-route.py --plan <run-dir>/plan.md --size
small|medium|large [--research-done] [--privacy clean|sensitive]` → JSON:
- **`execution`** ∈ `use_local` | `consider_ultraplan` | `lean_ultraplan` (three-signal rubric;
  privacy=sensitive is a hard cap to local).
- **`landing`** ∈ `main` | `pr` — a plan carrying an **engineering pre-commitment** (a concrete
  version-bump target, a reserved `Gate N` slot, a `.repo-layout.json`/`allowed_globs` edit, a named
  PR/branch target) lands via a `forge/<slug>` **draft PR**; a pure design/analysis plan lands straight
  to **main** (tiebreak F3 — a stale pre-commitment must not sit canonically in main).

The script reads `plan.md` from disk — it never needs the plan in context. It also runs `--self-test`
(its own fixtures) — a registered, citable canonical route.

### G8 — DoD / Exit
Verify the plan carries its definition-of-done (acceptance tests, version bumps, layout allow-list,
prettier/audit-gates per `AGENTS.md`). **If any phase adds or removes a skill, agent, or other
artifact whose count is encoded in marketplace prose, load
[`reference/regen-discipline.md`](reference/regen-discipline.md) now** and fold its criteria into that
phase's DoD — skipping this is what caused the 2026-06-03 three-PR hotfix chain (PRs #244-#247).

Then the single exit:
- `execution=use_local` → call **`ExitPlanMode(plan.md)`**.
- `execution=lean_ultraplan`/`consider_ultraplan` → **decline `ExitPlanMode` with a "sending to
  Ultraplan" note** (the harness opens the browser session, seeded with `plan.md`).
- `reject` (G5 left an unmitigated blocker, or G0 scope is incoherent) → report the blocker, no exit.
- Land `plan.md` per the G7 `landing` verdict (main, or open the draft PR).

## 3. Cost / latency controls

- **The §0 artifact contract is the primary lever** — it bounds *resident* context, which every later
  turn re-pays. Everything below trims *marginal* calls.
- **Depth default `quick`** + the gate-set scaling (§1) + the reference-file split (load only what the
  depth reaches).
- **Conflict cap** top-N≈5 at standard (uncapped only at deep — see `deep-resume.md`).
- **Claims cache:** G1 entries are content-addressed by `(claim, source-url)`; a re-run reuses verified
  claims whose retrieval date is < 90 days (matches the repo's knowledge-freshness contract). WebFetch
  is already 15-min URL-cached.
- **Parallel where independent** (G1 explore subagents; G2/G3 panels = one batch of `Task` calls),
  **serial where dependent** (G4→G5→G6) — capped by the `.ravenclaude/comfort-posture.yaml`
  `parallelism:` posture like [`spawn-team`](../spawn-team/SKILL.md) Step 5 (`enabled: false` → serial;
  `max_workers: N` → batches of ≤N; absent → unchanged). A **cap, not a floor**.
- **Brakes reused:** `runaway-brake.sh` (PreToolUse call caps) + `guard-recursive-spawn.sh` (tree
  topology) fire automatically — a thrashing gate trips the brake deterministically.
- **Fail-fast:** G1 BLOCK and a G7 `reject` short-circuit the expensive G2–G6 core when an idea is
  under-specified or non-viable.

### Thinking budget (cost ↔ depth lever)
Raise **`effort`** — the `Task`/`Agent` dispatch option (`low`|`medium`|`high`|`xhigh`|`max`), **not** a
brief keyword — to `xhigh` **only** for the gates that do adversarial reasoning over a whole plan: the
**G2/G3 panels**, and — at standard+ — the **G4a critic** and **G5 red-team** (their policy travels with
them in `gates-standard.md`). G0 scope, G1 fact-lookup, G4b tiebreaks, G6 synthesis, and G7 routing are
shallow or deterministic and do **not** warrant it — leave them at the session default. `--depth quick`
may skip the escalation entirely.

Anthropic's Opus 4.8 guidance is to *"raise effort … rather than prompting around it"*, and `xhigh` is
its recommended starting point for coding and agentic work (the API default is `high`). The pipeline's
old `ultrathink`-in-the-brief instruction was a workaround for a flag that did not exist when it was
written; `--effort` / `effortLevel` / the `Task` `effort` option all exist now. Dated correction, the
per-model inversion (Opus 4.8 → `xhigh`, Fable 5 → `high`), and sources: `reference/provenance.md`.

**Do not buy tokens here.** Trimming reasoning on the critic or red-team, or collapsing G3 into a
review-of-A instead of an independent plan, saves tokens by deleting the divergence and adversarial
depth the pipeline exists for. §0 and the depth/reference splits are free; these are not.

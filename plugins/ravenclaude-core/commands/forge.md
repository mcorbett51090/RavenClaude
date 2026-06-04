---
description: "Forge any idea into a gated, two-panel-reviewed, critic-checked, tiebroken, routed plan. Runs the FORGE pipeline (depth-scaled gates) and ends at ExitPlanMode or an Ultraplan cloud handoff. Backed by skills/forge-pipeline."
allowed-tools: Bash, Read, Write, Edit, Task, AskUserQuestion, WebSearch, WebFetch
argument-hint: <idea> [--depth micro|quick|standard|deep] [--models A=opus,B=sonnet] [--auto-route] [--no-redteam] [--resume <slug>]
---

# /forge

Run the **FORGE** gated-planning pipeline on `$ARGUMENTS`. This command is the thin entry
point; the full gate logic, subagent prompts, per-gate emit schemas, and depth ladder live
in **`skills/forge-pipeline/SKILL.md`** — load that skill and follow it exactly.

FORGE is the formalization of the pattern this marketplace's maintainer runs by hand:
**clarify → research+verify → two divergent panels on different models → critic → gap-analysis
→ per-conflict expert tiebreak → red-team → synthesize → route (Ultraplan vs local) → exit.**
It mimics the deep-plan shape now shipped as Claude Code's official **dynamic workflows / `ultracode`**
feature (parallel-research → synthesize → critic → revise — docs:
<https://code.claude.com/docs/en/workflows>, retrieved 2026-06-04) and improves it with **cross-model**
divergence, a **fact-verification** gate, and a **binding tribunal** for conflicts. FORGE is a *static*
harness (hand-authored, Team-Lead-run); see [`../knowledge/dynamic-workflows.md`](../knowledge/dynamic-workflows.md)
for when to reach for a dynamic workflow instead.

## Defaults & flags (tiebreak rulings baked in)

- **`--depth quick` is the DEFAULT** (cheap-by-default so it's actually used for *every* idea).
  Ladder, gate-set scales with depth (not a fixed gate count):
  - **micro** (~1-2 calls): G0 scope · G6 synthesize · G7 route. A structured sanity pass.
  - **quick** (~3-5 calls, default): G0 · G1-lite · G2 panel-A · G3 panel-B+gap · G6 · G7.
  - **standard** (~6-10 calls): + G4a critic · G4b tiebreak · G5 red-team.
  - **deep** (~11-18 calls): standard with no conflict cap + a second red-team + checkpoint/resume.
- `--models A=opus,B=sonnet` — the two panels MUST run on **different** models (cross-model
  divergence; verified available in this harness). B defaults to a model ≠ A.
- `--auto-route` — act on G7's verdict without pausing (else present it to Matt).
- `--no-redteam` — skip G5 (quick/micro only; emits a waiver).
- `--resume <slug>` — **deep depth only**: resume a failed run from its first missing gate
  artifact under `.ravenclaude/runs/forge/<slug>/`.

## Steps (each maps to a gate in the skill — run only the gates the depth includes)

1. **Parse args.** idea, `--depth` (default quick), `--models` (B≠A), `--auto-route`,
   `--no-redteam`, `--resume`. Mint a `<slug>` and a Sága run dir `.ravenclaude/runs/forge/<slug>/`.
2. **G0 Scope/Clarify.** ≤2-3 batched clarifying questions via `AskUserQuestion` (auto-routed
   through the decision-review hook). Emit `scope.md`. A fast routing triage here can short-circuit
   to Ultraplan *before* spending tokens if the idea is plainly large+cloud-suited.
3. **G1 Research + Verify (TIERED — F2).** **BLOCK** on a load-bearing claim about anything
   **outside the repo** (third-party API behavior, tool/SDK versions, pricing, performance) that
   lacks a this-session source (url+date) or an `[unverified]`+justification marker. **WARN, don't
   block**, on a repo-structural claim the model just confirmed via a visible in-session tool call.
   Emit `claims-table.md`. (Skip at micro.)
4. **G2 / G3 Two panels.** Dispatch Panel A (model A) and Panel B (model B≠A) **in parallel** as
   worker subagents. B also emits the gap-delta (every A/B conflict). Each plan must include a
   **dependency DAG** + **≥2 alternatives w/ trade-offs**. Emit `plan-A.md`, `plan-B.md`, `gap-delta.md`.
5. **G4a Critic (standard+; F5).** A subagent that did **not** write either plan reads BOTH and
   hunts for **where they AGREE on something wrong** (correlated error the gap-analysis misses),
   attacks the idea's premise, and emits a probability×impact **risk matrix**. No third plan.
   Emit `critic-brief.md`.
6. **G4b Tiebreak (standard+).** One expert subagent per real conflict (from gap-delta + critic);
   a clean yes/no goes to the tribunal `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/thing-decide.py`;
   defer/high-blast → ask Matt. Emit `tiebreaks.md`.
7. **G5 Red-team (standard+, unless `--no-redteam`).** ≥5 **real, reproducible** failure modes
   (not performative dissent) + mitigations; an unmitigated high-severity with no waiver loops
   back to G2/G4. Emit `red-team.md`.
8. **G6 Synthesize.** Merge tiebreak verdicts + critic risk matrix + red-team mitigations into
   `plan.md` (with the reconciled DAG, risk matrix, alternatives). No dangling conflict; every
   G1 `[unverified]` claim has a settling step.
9. **G7 Route (deterministic).** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/forge-route.py --plan
   <plan.md> --size <s> [--research-done] [--privacy clean|sensitive]` → `{execution, landing}`.
   Execution ∈ use_local | consider_ultraplan | lean_ultraplan; **landing ∈ main | pr** (engineering
   pre-commitments → a `forge/<slug>` draft PR; pure design → straight to main — F3).
10. **G8 Exit.** Verify DoD (acceptance tests, version bumps, layout/prettier/audit-gates per
    `AGENTS.md`). `use_local` → call `ExitPlanMode(plan.md)`. `lean_ultraplan`/`consider_ultraplan`
    → **decline `ExitPlanMode` with a "sending to Ultraplan" note** so the harness opens the cloud
    session, seeded with `plan.md`. `reject` → report the blocker, no exit. Land `plan.md` per the
    G7 landing verdict.
11. Write the Sága run record (one entry per gate: pass/fail/waiver, who ran it, model, cost).

## Guardrails (reused, not rebuilt)

- Subagents are dispatched by **this** session only — `guard-recursive-spawn.sh` keeps the call
  graph a tree (a worker can't fan out a second generation), matching Codex's explicit-only spawn.
- `runaway-brake.sh` caps total/consecutive tool calls — a thrashing gate trips the brake, not Matt.
- The two-panel **lens/severity/routing rubric** is shared with `.claude/workflows/two-panel-plan-review.js`
  via a common constants module (don't re-author the rubric — F7); FORGE adds the scope, critic,
  depth-tiering, and routing layers on top.

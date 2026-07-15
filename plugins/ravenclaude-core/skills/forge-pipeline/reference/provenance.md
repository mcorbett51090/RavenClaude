# FORGE reference — provenance, shared rubric, honest scope

> Loaded by [`../SKILL.md`](../SKILL.md) **only when a human asks why FORGE is shaped this way.** None
> of it is needed to *run* a gate, which is why it does not sit in the always-loaded core.

## Provenance & the two influences

- **Claude Code dynamic workflows / `ultracode`** — the community-named "Ultraplan deep-plan" shape
  (parallel explore agents → synthesize → **single same-model critic** → revise → emit; plus
  cloud-vs-local routing and the `ExitPlanMode`/cloud handoff) is now the **officially-documented**
  dynamic-workflows feature — Claude writes a JS harness that orchestrates subagents. `[verified —
  official docs https://code.claude.com/docs/en/workflows, retrieved 2026-06-04; the trigger keyword
  is `ultracode` as of v2.1.160, was `workflow` before]`. The exact internal critic/revise loop of any
  bundled workflow is still `[unverified — not enumerated in the docs]`. FORGE is a **static** harness
  (hand-authored, run by the Team Lead — see [`../../../knowledge/dynamic-workflows.md`](../../../knowledge/dynamic-workflows.md))
  that reproduces this shape and **improves it**: cross-model two-panel divergence (research shows
  cross-model debate > self-critique), a fact-verification gate the bundled workflows don't expose, and
  a binding tribunal instead of an opaque merge.
- **OpenAI Codex** — its gate is a *graduated-trust ladder* (read-only → workspace-auto → full-access)
  + explicit-only subagents. FORGE borrows the ladder (it maps onto routing/exit + comfort-posture)
  and the explicit-spawn discipline (already enforced by `guard-recursive-spawn.sh`).

## The two-panel rubric is NOT shared (tiebreak F7 — corrected 2026-07-15)

**F7 previously claimed** FORGE shares the two-panel lens definitions, the P0/P1 severity rubric, and
the routing-signal schema with the two-panel workflow — stated here as *"FORGE shares those constants
(one source of truth)"* and, until v0.192.0 deleted it, in `commands/forge.md` as *"via a common
constants module"*. **That was false in every part**, and it was load-bearing enough to mislead: it told
an agent not to re-author the rubric while giving no way to obtain it.

> `[verified 2026-07-15]` The workflow's `DEFAULT_SEVERITY_RUBRIC`, `DEFAULT_PANEL1_LENSES`,
> `DEFAULT_PANEL2_LENSES`, `GAP_SCHEMA` and `ROUTING_SCHEMA` are **module-private consts** — only
> `export const meta` is exported, so nothing can import them; no shared module exists anywhere in the
> tree; and forge-pipeline contained no lens or severity text at all. The claim was additionally
> asserted in two **shipped** files one hop away (this plugin's `two-panel-plan-review/SKILL.md` and
> `knowledge/dynamic-workflows.md`) — both corrected in the same change.

What is actually true, per item:

- **Lens definitions — deliberately NOT shared.** The workflow's 8 role-bound lenses are authored for
  *reviewing a pre-written plan* with a specialist panel. FORGE's panels **author** a plan from a raw
  idea. Different input contract ⇒ the lenses don't transfer, and running 8 lens-agents would blow
  FORGE's 6-10-call `standard` budget and collapse it into the workflow.
- **Severity — NOT shared, and deliberately not ported.** The workflow's P0/P1/P2 tiers are anchored to
  build/merge semantics ("must-fix before merge", "blocks PR approval") that are meaningless when
  comparing two *unbuilt drafts*. FORGE defines a bar only where severity **mechanically routes** — G5's
  loop-back trigger — in G5's own words. See [`gates-standard.md`](gates-standard.md).
- **Routing — two independent implementations, no coupling.** FORGE routes via the deterministic
  [`forge-route.py`](../../../scripts/forge-route.py); the workflow's `ROUTING_SCHEMA` is model-emitted.
  They share a 3-value verdict vocabulary (`use_local` / `consider_ultraplan` / `lean_ultraplan`) and
  **no code path** — different consumers, nothing to drift *functionally*. Keep the enum consistent by
  hand; a gate would be ceremony.

FORGE does **not** runtime-compose that workflow. The workflow ships as its own skill —
[`two-panel-plan-review`](../../two-panel-plan-review/SKILL.md), whose runnable copy is
[`two-panel-plan-review.js`](../../two-panel-plan-review/two-panel-plan-review.js) (a byte-identical
mirror of the marketplace's `.claude/workflows/` copy, enforced by Gate 126).

> **Why FORGE does not port the rubric — don't "close this gap".** Reviewed 2026-07-15 and rejected on
> evidence, not taste: the severity tiers are anchored to semantics FORGE's gates don't have; the lens
> list is 50% already covered structurally (G1 ≈ evidence, the panels' acceptance tests ≈ testability,
> G4a's premise attack ≈ devil's advocate); and G4b's "top-N highest-impact" cap **demonstrably executes
> without a formal scale** — the run that produced this correction ranked 12 gaps and capped at 5
> sensibly, with no rubric. Zero observed failures across FORGE's run history. If you are about to port
> P0/P1/P2 or the lenses here, first produce a FORGE run where their absence caused a wrong outcome.

## Honest scope

FORGE makes a plan **divergently reviewed, fact-grounded, critic-checked, and routed** — it raises the
floor on plan quality and shifts the odds against a confidently-wrong plan. It does **not** guarantee the
plan is correct (no process does); the critic + red-team + tiebreak reduce, not eliminate, the residual.
Stating otherwise would be the over-claim the accuracy work in this repo exists to prevent.

## Why the thinking budget is a brief instruction, not a CLI flag

`claude -p` exposes **no** thinking-budget flag (verified: `claude --help` shows only
`--max-budget-usd`). The sanctioned lever on this surface is the in-prompt `ultrathink` keyword —
which is why the budget policy lives in the seat **briefs**, not in engine config. Background:
[`docs/token-budget-playbook.md`](../../../../../docs/token-budget-playbook.md).

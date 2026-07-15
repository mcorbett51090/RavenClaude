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

## Shared rubric (tiebreak F7 — don't re-author)

The two-panel lens definitions, the P0/P1 severity rubric, and the routing-signal schema are the **same**
ones `.claude/workflows/two-panel-plan-review.js` uses. FORGE shares those constants (one source of
truth) and adds the scope, critic, depth-tiering, and routing **layers** — it does **not** runtime-compose
that workflow (it's a standalone harness entry point that consumes a *pre-written* strategic plan, a
different input contract than FORGE's "raw idea → plan").

> `[unverified — not re-checked this session]` The "shares those constants" claim describes intent, not
> a located module: the constants live inside `.claude/workflows/two-panel-plan-review.js`, and no
> extracted shared module was found in the tree. Treat F7 as *"don't re-author the rubric — go read it
> there"* until a real module exists. Verifying route: `grep -n` the lens/severity constants in that
> workflow file and check whether any importable module exports them.

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

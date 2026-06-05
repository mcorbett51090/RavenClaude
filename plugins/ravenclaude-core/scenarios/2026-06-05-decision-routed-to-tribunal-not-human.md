---
scenario_id: 2026-06-05-decision-routed-to-tribunal-not-human
contributed_at: 2026-06-05
plugin: ravenclaude-core
product: orchestration
product_version: "n/a"
scope: likely-general
tags: [decision-review, tribunal, comfort-posture, high-blast, defer-to-human, genuine-preference]
confidence: medium
reviewed: false
---

## Problem

A session about to ask Matt a yes/no question routed it through the decision-review tribunal (the Thing) — correct, that is the rule: *all yes/no decisions route through the tribunal before they reach the human*. But the question was **"should we force-push the rebased branch to overwrite origin?"** — a high-blast, irreversible action. The session treated the tribunal's verdict as authoritative and was about to act on a `yes`. That inverts the safety envelope: high-blast / irreversible decisions (force-push, deletes, prod actions, the `security_deny` family) **never auto-resolve** — they always `defer` to the human, regardless of decision-review mode. The mirror failure also showed up the same week: a *genuine preference* ("which of these two equally-valid naming conventions do you prefer?") was *not* routed and was silently auto-decided, when a preference is exactly what the panel should `defer`.

## Context

- Surface: domain-neutral, `ravenclaude-core`. Governing docs: CLAUDE.md §"Decision review — route yes/no decisions through the tribunal" and the engine [`../scripts/thing-decide.py`](../scripts/thing-decide.py).
- The verdict vocabulary is `yes` / `no` / `defer`. A **binding** `yes`/`no` lets the agent act without pausing the human; `defer` means **ask the human**. The panel defers genuine preferences, low-confidence / split calls, and anything tagged high-blast.
- The safety envelope is owned by the engine, not the agent's memory: off→defer, high-blast→defer, abstain/split/injection→defer, and every routed decision is Sága-logged under `.ravenclaude/runs/thing/decisions/`. The mode knob `decision_review: off | advisory | binding` lives in `.ravenclaude/comfort-posture.yaml` and is **off by default** — nothing auto-decides unless the human opts in.
- The enforced complement: a `PreToolUse(AskUserQuestion)` hook ([`../hooks/route-decision-review.sh`](../hooks/route-decision-review.sh)) intercepts the question so routing doesn't depend on the model *remembering*. It is conservative + fail-safe — it only auto-routes a single, non-multiselect, binary yes/no question; **defer / advisory / high-blast / low-confidence / any engine error → allow** (the human answers).
- Why both directions slipped: the agent conflated "route it through the tribunal" with "let the tribunal decide it." Routing is mandatory; *binding resolution* is reserved for the rule-derivable, reversible, non-preference calls.

## Attempts

- Tried: route the force-push yes/no through the panel and treat a `yes` as binding. Outcome: a high-blast irreversible action one step from auto-executing — the exact class the envelope says must `defer`.
- Tried: route the naming-convention preference *not at all* and pick one silently. Outcome: a genuine-preference call made for the human — the other half of the same defect (a preference is a `defer`, not an auto-decision).
- Tried (the move that worked): let the engine's safety envelope do its job. The force-push is tagged **high-blast → `defer`** (ask Matt; never auto-resolve regardless of mode); the naming preference is **genuine preference → `defer`** (ask Matt). Both reach the human; the only calls the panel binds are reversible, rule-derivable, non-preference yes/nos. Outcome: the human is interrupted only for the two decisions that genuinely need a human, and each is Sága-logged.

## Resolution

The defect was **conflating "route through the tribunal" with "let the tribunal bind it"** — in both directions: binding a high-blast call that must defer, and skip-routing a preference that must defer. The rule is: route *every* yes/no through the panel; the engine then binds only the reversible, rule-derivable, non-preference calls and `defer`s everything else (off, high-blast, abstain/split, genuine preference). High-blast / irreversible never auto-resolve. The goal is to shrink the human's interrupts to genuine-preference + high-blast calls, and give the rule-derivable ones an auditable verdict instead of a silent autonomous choice.

**Action for the next session facing a yes/no:** route it through the tribunal (the hook does this automatically for a single binary question) — but never override a `defer`, and never treat a high-blast/irreversible `yes` as binding. Force-push, deletes, prod actions, and the `security_deny` family always defer to the human. A genuine preference is a `defer`, not an auto-decision. `[verify-at-use]` the active `decision_review` mode and whether high-blast tagging is configured in the consumer's `.ravenclaude/comfort-posture.yaml` — the envelope is off by default and per-repo.

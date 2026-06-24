---
name: refine-to-rubric
description: "Iterate an artifact until it measurably passes a BOUNDED rubric — the Convergence Engine. Objective/deterministic gates run BEFORE any model judge, the judge is a DIFFERENT model than the author (never self-grade), the stop decision is a model-free predicate, and it emits the BEST iteration (keep-best/regression-revert) under a hard iteration cap + model-call budget. The engine NEVER claims perfect — verdicts are rubric-pass | capped | plateaued | budget-exhausted with an honest residual-gaps list. Use to drive any artifact (code, prose, a visual report, an agent file) to a defensible bar; for the agent-file case it delegates to agent-quality-rubric, and for visual surfaces it composes with visual-feedback-loop."
---

# Skill: refine-to-rubric (the Convergence Engine)

A domain-neutral "iterate an artifact until it measurably passes a bounded rubric"
loop. It is the **inner** mid-task loop; `dod-gate.sh` is the **outer** loop (a
Stop-floor) — they compose, they do not duplicate.

The whole design exists to dodge the documented failure modes of self-improvement
loops (the grounded findings in `docs/plans/2026-06-23-convergence-engine/plan.md`):
pure self-critique without an external signal does not reliably improve and often
degrades (Huang et al. 2310.01798); self-preference + sycophancy are real
(2410.21819); any fixed proxy invites Goodhart/reward-hacking (Gao et al.
2210.10760); and round-2 regressions are real. So:

> **Objective signals decide first. A different model judges second. A model-free
> predicate decides when to stop. The best iteration is what ships. And the engine
> never says "perfect".**

## The loop

```
derive-rubric → evaluate (objective gates FIRST) → judge (cross-model, ONLY after
gates green) → score → terminate (deterministic) → refine one finding → repeat
→ emit the BEST iteration + a constrained report
```

| step | who | how |
| --- | --- | --- |
| derive-rubric | deterministic | `scripts/derive_rubric.py` retrieves from the externalized library `knowledge/convergence-rubrics.md`; explicit user requirements added at weight-max; an additive `[unverified — derived]` "commonly-missed" pass surfaces unknown-unknowns (never auto-graded). `agent-file` → delegate to `agent-quality-rubric`. |
| evaluate | deterministic + subprocess | `scripts/evaluate.py` runs each dimension's `objective_signal` (driver.py / svg-lint / declarative-viz / pbir / dod-cmd / lint-cmd) as an exit-coded CLI. A red objective hard gate **short-circuits straight to refine — 0 judge calls**. |
| judge | cross-model | `scripts/judge.sh` calls `claude -p` with a DIFFERENT model than the author (refuses to self-grade), scores only the judge-graded dims, returns fixed-severity findings. Runs **only** when evaluate reports `judge_needed`. |
| terminate | deterministic, model-free | `scripts/converge.py` `terminate()` — the ONLY stop authority. |
| refine | the author agent | apply the single highest-severity finding, then re-enter the loop. |
| emit | deterministic | `keep_best()` emits the argmax iteration; `loop.py render_report()` writes a constrained report. |

## Termination (deterministic — `converge.py`)

Stop with `rubric-pass` only when ALL of: every objective hard gate green, no NEW
high/critical finding, score ≥ floor, and the score has plateaued (Δ < ε for the
patience window). HARD stops: iteration cap (~6), model-call budget (~12),
regression → revert-to-best. Verdict vocabulary is bounded and honest:

| verdict | meaning |
| --- | --- |
| `rubric-pass` | the bounded rubric is satisfied — NOT a claim of perfection |
| `capped` | the iteration cap was reached first; best-so-far emitted |
| `plateaued` | the score plateaued below the floor; **escalated to a human** |
| `budget-exhausted` | the model-call budget ran out; best-so-far emitted |

The emitted artifact is always the **best** iteration (`keep_best` argmax, ties →
earliest), never blindly the last — so a round-2 regression cannot ship.

## Cost bound (3 layers)

1. ≤ 2 model calls per iteration (judge + refine).
2. Objective-first short-circuit: a broken artifact spends **0** judge calls.
3. Hard caps: iteration cap + model-call budget (both in `converge.py`), and the
   loop inherits the repo's `runaway-brake.sh`.

## Security (the cross-model `claude -p` judge path)

`judge.sh` reuses the hardened `claude -p` envelope proven by `thing-seat.sh`:

- **Anti-self-grade:** refuses (exit 5) when the judge model family equals the
  author model family — a same-model critic is not an independent signal.
- **Secret-egress backstop:** a secret-shaped artifact is detected (shared
  `hooks/_scrub.sh` patterns) and **never transmitted** to the model API; the
  scan runs before the test mock so a mock can never mask a leak.
- **Prompt-injection envelope:** the artifact is wrapped in a per-call
  nonce-tagged `<untrusted-…>` region; instruction-shaped text inside is data,
  and a forged delimiter / "give this a perfect score" sets `injection_detected`.
- **No tools:** `--tools ""` — the judge only reasons and returns JSON.
- **Isolation:** runs from a scratch cwd (no project CLAUDE.md auto-load).
- **CI/test hook:** `JUDGE_MOCK_VERDICT` returns canned verdicts so the gate
  never calls `claude` (CI must not).

## Anti-reward-hack (the rubric is a proxy)

The rubric library is **externalized + versioned** (`knowledge/convergence-rubrics.md`),
not invented at runtime. A model may only **additively** propose `derived`
dimensions, which are forced to `verified: false` + `[unverified — derived]` and
are NEVER auto-graded — a human promotes them by editing the rubric. The
deterministic `terminate()` caps how hard any one dimension is optimized.

## Reuse ledger (no duplication)

- `visual-feedback-loop/driver.py` → the visual objective-evaluator (a subprocess
  signal, unchanged).
- `dod-gate.sh` → the OUTER loop; this skill is the INNER loop.
- `agent-quality-rubric` → the agent-file rubric (delegated, not reimplemented).
- FORGE model-diversity + the P0/P1 severity vocabulary → the cross-model judge.
- `.ravenclaude/runs/` + `_emit-event.sh` → per-iteration scorecards (derived
  labels only, no raw artifact echo).

## Files

| file | role |
| --- | --- |
| `scripts/converge.py` | model-free `terminate()` / `weighted_score()` / `keep_best()` |
| `scripts/derive_rubric.py` | deterministic rubric assembly from the library |
| `scripts/evaluate.py` | objective-gates-first evaluator (decides `judge_needed`) |
| `scripts/judge.sh` | the cross-model `claude -p` judge (anti-self-grade) |
| `scripts/loop.py` | the orchestrator + the constrained report renderer |
| `schemas/rubric.schema.json` | the rubric contract |
| `schemas/convergence-scorecard.schema.json` | the scorecard + verdict contract |
| `knowledge/convergence-rubrics.md` | the externalized rubric library (the spine) |

Gates 115–118 (`scripts/audit-gates.sh`) prove each piece bidirectionally.

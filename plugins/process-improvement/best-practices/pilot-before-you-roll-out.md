# Pilot before you roll out — prove the fix on a small scale before betting the whole process on it

**Status:** Pattern — strong default for any non-trivial improvement. A pilot confirms the gain is real, surfaces unintended effects cheaply, and builds the evidence that earns full rollout. Deviate only for a reversible, low-blast change where the pilot would cost more than a fast rollback.

**Domain:** DMAIC / process improvement (Improve)

**Applies to:** `process-improvement`

---

## Why this exists

An Analyze phase can prove the root cause and a countermeasure can look obviously correct — and the full-scale rollout can still fail, because real processes have interactions the analysis didn't model: a fix that speeds one team overloads the next, a new check that eliminates one defect introduces another, a change that works for the common case breaks the edge cases. A pilot contains that risk to a small, reversible slice (one team, one region, one product line, a defined time-box) where the *same* baseline metric is re-measured under the change. If the gain holds and nothing bad appears, scale with confidence; if it doesn't, you've spent a pilot, not a process.

The pilot is also where the **control mechanisms get rehearsed** — the control chart, the reaction plan, the standard work — so that what rolls out is the whole sustainment system, not just the change.

## How to apply

1. **Pick a representative slice** — small enough to revert quickly, representative enough that success predicts the whole. Define the boundary explicitly.
2. **Re-measure the same metric, same operational definition** as the baseline — a pilot without a remeasure is just an early rollout.
3. **Pre-state the success criteria** — the threshold (effect size / capability / defect-rate target) that the pilot must clear to proceed, decided before the data comes in. Route the "is the difference real, not noise?" question to `applied-statistics`.
4. **Watch for unintended effects** — measure the obvious downstream metrics too (did fixing step 3 break step 4?), not only the target.
5. **Rehearse the control plan** during the pilot so the Control phase ships a proven sustainment system.
6. **Decide explicitly: scale, adjust, or abandon** — a pilot that "sort of worked" with no decision criterion becomes a permanent half-rollout.

**Do:**
- Define the rollback before you start the pilot (how to revert, and the trigger).
- Compare against a control (the un-piloted slice) where feasible, to separate the change from a coincident trend.

**Don't:**
- Roll out org-wide off a slide deck and a plausible mechanism — that's a bet, not a test.
- Move the success bar after seeing the pilot data.
- Skip measuring downstream/adjacent metrics — unintended effects hide there.

## Edge cases / when the rule has nuance

- **Reversible, low-blast change** — a one-click, instantly-revertible tweak may be cheaper to roll out behind a fast rollback than to pilot. Make that call explicitly.
- **Safety/compliance fix that can't wait** — act, but instrument heavily and treat the first cohort as a monitored pilot.
- **Statistical sufficiency** — a pilot too small to detect the effect proves nothing; size it with `applied-statistics` (power/sample size) before running it.

## See also

- Skill: [`../skills/control-plan-and-sustain/SKILL.md`](../skills/control-plan-and-sustain/SKILL.md) — the control system the pilot rehearses
- Best-practice: [`./a-fix-without-a-control-plan-didnt-happen.md`](./a-fix-without-a-control-plan-didnt-happen.md) — what ships after a successful pilot
- `applied-statistics/agents/applied-statistician.md` — power/sample-size for the pilot and the "is the gain real?" test

## Provenance

Distilled from `CLAUDE.md` §3 house opinions #5 (the statistics seam — pilot results are validated, not eyeballed) and #6 (sustain the gain — the pilot rehearses the control plan). Pilot-before-rollout is standard DMAIC Improve-phase practice (the Improve tollgate expects a piloted, validated solution before Control). `[unverified — training knowledge]` — framing recalled from standard Lean Six Sigma practice, not re-verified against a source this session.

---

_Last reviewed: 2026-06-03 by `claude`_

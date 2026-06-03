# Optimize the constraint, not a sub-process — speeding a non-bottleneck step doesn't speed the system

**Status:** Pattern — strong default whenever the goal is throughput/lead-time. Local improvements away from the constraint feel productive and change nothing the customer sees. Deviate only when the "sub-process" is itself the constraint, or the work is a quick win with near-zero cost.

**Domain:** DMAIC / process improvement (Analyze → Improve) · Theory of Constraints / Lean

**Applies to:** `process-improvement`

---

## Why this exists

A process moves only as fast as its slowest step. Improve a step that is *not* the bottleneck and the system throughput is unchanged — the work just piles up sooner in front of the real constraint. This is the most common way well-intentioned improvement effort is wasted: a team optimizes the step that's easiest to fix or most visibly painful, ships a real local gain, and the end-to-end lead time the customer experiences doesn't budge. Worse, speeding a feeder step *before* the constraint usually grows work-in-process inventory (a Lean waste) without adding output.

The discipline is to find the constraint first — the step with the longest cycle time relative to takt, the deepest queue in front of it, or the highest utilization — and direct the improvement there. Once that constraint is elevated, the bottleneck moves; re-find it and repeat.

## How to apply

1. **Map cycle time per step against takt** (the `lean-waste-analysis` and `process-mapping` skills) — the constraint is where cycle time exceeds takt or where the largest queue accumulates.
2. **Confirm the constraint with data, not intuition** — the loudest-complaint step is often not the throughput constraint. Use queue depth / wait time, not opinion.
3. **Exploit before you elevate** — first get the most out of the existing constraint (reduce its downtime, stop feeding it defects, offload non-constraint work from it) before spending capital to add capacity.
4. **Subordinate the rest** — non-constraint steps should run at the constraint's pace, not flat-out (running them faster only builds WIP).
5. **Re-find the constraint after each gain** — elevating one bottleneck promotes the next; the target moves.

**Do:**
- Quantify each step's cycle time and queue before choosing where to improve.
- Protect the constraint from starvation and from defects (a defect that reaches the constraint wastes the scarcest capacity).

**Don't:**
- Optimize the step that's easiest or most annoying just because it's tractable.
- Speed up a pre-constraint step — you'll grow WIP, not throughput.
- Declare victory on a local cycle-time win without showing the end-to-end lead-time effect.

## Edge cases / when the rule has nuance

- **Quality/defect goals (not throughput)** — when the objective is defect reduction rather than speed, the "constraint" framing maps to the vital-few defect source (Pareto), not the slowest step; the same "fix the dominant driver first" logic applies.
- **The constraint is external** (a supplier, an approval outside the team) — elevating it may be out of scope; surface it and route the cross-boundary part to `project-management`.
- **A true quick win off the constraint** — a near-zero-cost fix can be worth doing for morale/quality even if it doesn't move throughput; just don't *count* it as the throughput improvement.

## See also

- Skill: [`../skills/lean-waste-analysis/SKILL.md`](../skills/lean-waste-analysis/SKILL.md) — takt/cycle-time and bottleneck identification
- Knowledge: [`../knowledge/process-improvement-decision-trees.md`](../knowledge/process-improvement-decision-trees.md) — the waste→countermeasure tree (the *Waiting* leaf is the constraint attack)
- Best-practice: [`./prove-root-cause-with-data-before-improving.md`](./prove-root-cause-with-data-before-improving.md) — confirm the constraint with data before acting

## Provenance

Distilled from `CLAUDE.md` §3 house opinion #3 (Lean removes waste / pick the tool the problem's shape calls for). Rooted in Goldratt's Theory of Constraints (identify → exploit → subordinate → elevate → repeat). `[unverified — training knowledge]` — the five-focusing-steps framing is standard ToC, recalled from training, not re-verified against a source this session.

---

_Last reviewed: 2026-06-03 by `claude`_

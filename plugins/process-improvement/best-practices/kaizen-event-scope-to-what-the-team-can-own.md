# Kaizen Event Scope to What the Team Can Change in 3–5 Days

**Status:** Pattern
**Domain:** Process Improvement — Kaizen / rapid improvement
**Applies to:** `process-improvement`

---

## Why this exists

A Kaizen event that overreaches its scope is the most common cause of Kaizen failure. When the team identifies a root cause or countermeasure that requires an IT system change, capital approval, or a vendor negotiation — none of which can complete in the 3–5 day window — the event ends with an action list instead of an implemented improvement. The action list gets deprioritized, the gain never materializes, and the team is left with the impression that "Kaizen doesn't work here." Scoping to what the team *can own and implement* in the event window is the design principle that prevents this.

## How to apply

**Kaizen event scoping checklist (complete before scheduling the event):**

- [ ] The targeted process step(s) are owned by people who will be *in the room* during the event.
- [ ] Countermeasures do not require capital expenditure above the pre-authorized limit (establish the limit before the event).
- [ ] No IT system changes are required (or they are limited to configuration changes an IT rep in the room can make).
- [ ] The team can re-measure the metric by Day 4 to confirm the improvement.
- [ ] A named process owner is committed to sustain the change after the event closes.

**Event structure (5-day model):**

| Day | Activity |
|---|---|
| 1 | Scope, current-state data review, process walk, waste identification |
| 2–3 | Root-cause analysis (rapid 5 Whys / fishbone), countermeasure design, implement |
| 4 | Implement remaining countermeasures, re-measure, document standard work |
| 5 | Present results, finalize control plan, 30/60/90-day follow-up schedule |

**Do:**
- Prepare current-state data *before* the event starts (Day 1 is not the day to collect baseline data).
- Assign a 30-day follow-up review with the process owner to confirm the gain is holding.
- Record out-of-scope findings in a parking lot and route them to the backlog as separate projects.

**Don't:**
- Let the event scope grow to include systemic issues that warrant a full DMAIC.
- Schedule the event before the current-state data collection and VOC is complete.
- Declare success on Day 5 before remeasuring the target metric.

## Edge cases / when the rule does NOT apply

- **3-day "mini-Kaizen"** for a single-step improvement: the structure compresses but the scoping rule is *more* important, not less — the window is shorter.
- **DMAIC Improve phase Kaizen bursts**: a Kaizen event *within* a DMAIC project is scoped by the DMAIC root-cause findings and operates as an implementation sprint, not a discovery exercise.

## See also

- [`../agents/lean-six-sigma-blackbelt.md`](../agents/lean-six-sigma-blackbelt.md) — determines whether the problem warrants a Kaizen or a full DMAIC
- [`./a-fix-without-a-control-plan-didnt-happen.md`](./a-fix-without-a-control-plan-didnt-happen.md) — the Day 4/5 deliverable that makes the gain stick

## Provenance

Standard Lean rapid-improvement event practice (Rother & Shook; Lean Enterprise Institute Kaizen workshop guide; MoreSteam). 5-day structure is conventional; exact cadence may vary by organization. _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_

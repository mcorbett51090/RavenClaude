# DMAIC Phase Gates Are Not Optional

**Status:** Absolute rule
**Domain:** Process Improvement — DMAIC governance
**Applies to:** `process-improvement`

---

## Why this exists

DMAIC's value is as a *structured inference chain*: each phase produces evidence that qualifies entry to the next. Skipping a gate — most commonly jumping from Define straight to Improve, or from Analyze to Control before the pilot is complete — breaks the chain and converts a data-driven project into an expensive opinion. The gate exists precisely because human bias to act is highest when the correct action is to measure and analyze.

## How to apply

Each phase ends with a tollgate review. The following criteria must be met before moving forward:

| Phase | Gate criteria (all required) |
|---|---|
| **Define → Measure** | Problem statement quantified; project charter signed; SIPOC drafted; CTQs identified from VOC |
| **Measure → Analyze** | Baseline metric collected; operational definition written; Gage R&R / attribute agreement passed; data collection plan executed |
| **Analyze → Improve** | Root cause(s) **proven with data** (not merely plausible); Pareto or confirmatory test result in hand; `applied-statistics` verdict attached if inferential |
| **Improve → Control** | Pilot results documented; same metric used in baseline re-measured post-pilot; improvement statistically confirmed (route to `applied-statistics`) |
| **Control → Close** | Control plan written (chart + reaction plan + standard work + named owner); capability re-confirmed; project charter closed; sponsor sign-off |

**Do:**
- Surface the gate criteria at project kickoff so the sponsor knows what evidence is required.
- Document the tollgate outcome (pass / conditional pass / return) in the project charter.
- Return a phase if the gate is not met — a conditional pass with documented open items is acceptable; an undocumented skip is not.

**Don't:**
- Combine Analyze and Improve into one meeting because "we already know the root cause."
- Declare the Control phase complete before the control chart has run for at least one monitoring cycle.
- Let schedule pressure from the project-management seam override a gate that requires more data.

## Edge cases / when the rule does NOT apply

- **Just-do-it actions** (trivial + reversible, root cause known): these bypass DMAIC entirely per the methodology-selection tree. They are *not* DMAICs and have no gates — but they still require a post-implementation check that the fix held.
- **Kaizen events** (rapid 3–5 day improvements): the gate cadence compresses, but the Define and Measure data must exist *before* the event starts (usually gathered in the week prior). Post-event remeasure is still required.

## See also

- [`../agents/lean-six-sigma-blackbelt.md`](../agents/lean-six-sigma-blackbelt.md) — the agent that owns gate traversal
- [`./prove-root-cause-with-data-before-improving.md`](./prove-root-cause-with-data-before-improving.md) — the Analyze→Improve gate criterion in detail

## Provenance

Codifies the DMAIC backbone (house opinion #2) and the phase-gate convention from `CLAUDE.md` §3. Phase-gate criteria are standard DMAIC practice (ASQ Six Sigma Body of Knowledge; MoreSteam DMAIC guide). _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_

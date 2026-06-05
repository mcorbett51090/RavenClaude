# Document the Planning Calendar, RACI, and Lock Dates

**Status:** Absolute rule
**Domain:** FP&A / planning process
**Applies to:** `finance`

---

## Why this exists

A budget or forecast cycle that lacks a written calendar, an explicit RACI, and locked submission deadlines produces a chaotic deliverable: business units submit late, finance consolidates on shifting assumptions, and the board sees a plan that reflects whichever department updated last. Lock dates are not administrative courtesies — they are the mechanism that gives finance a stable denominator to consolidate against. Without them, the plan is perpetually provisional and variance commentary in future periods compares actuals to a moving target.

## How to apply

Publish the planning calendar as a standalone document at the kick-off of every budget or forecast cycle, before any template goes out.

```
Planning Calendar — Minimum Required Fields
────────────────────────────────────────────
Milestone                 | Owner       | Date      | Notes
──────────────────────────|─────────────|───────────|──────────────────
Guidance issued           | FP&A Lead   | YYYY-MM-DD | Macro + top-down targets
Templates distributed     | FP&A Analyst| YYYY-MM-DD |
BU submission deadline    | BU Finance  | YYYY-MM-DD | LOCK — no changes after
Consolidation complete    | FP&A Lead   | YYYY-MM-DD |
CFO / leadership review   | CFO         | YYYY-MM-DD |
Board submission          | FP&A Lead   | YYYY-MM-DD |
Board deck finalized      | Board-Pack  | YYYY-MM-DD |
```

RACI minimum: every milestone names an **Accountable** (one person, not a team), a **Responsible** (who does the work), **Consulted** (BU owners, department heads), and **Informed** (exec team, board).

**Do:**
- Distribute the calendar to all contributors before the first template ships.
- Enforce the BU submission lock — accept one formal extension request per BU maximum, documented with a reason and a revised date.
- Tie the lock date to a version stamp in the consolidation workbook (e.g., "Plan v1.0 locked 2025-09-15").
- For a rolling forecast, document which months are open for revision vs. locked.

**Don't:**
- Run a "soft" deadline that everyone knows will slip — it trains teams to ignore future deadlines.
- Let the RACI default to "FP&A" as both accountable and responsible for a BU's own numbers.
- Skip the calendar for a reforecast because "it's just a quick update" — even a 1-period reforecast needs a lock date.

## Edge cases / when the rule does NOT apply

- **Ad hoc scenario analysis** (e.g., a one-off M&A sensitivity) — does not require a formal calendar, but still needs a clearly stated assumption-lock date.
- **Month-end reforecast as part of close** — the close calendar governs; the planning-calendar rule augments it only for the forward-looking elements.

## See also

- [`../agents/fpa-analyst.md`](../agents/fpa-analyst.md) — owns the planning calendar and rolling-forecast process.
- [`./fpa-rolling-forecast-beside-the-budget.md`](./fpa-rolling-forecast-beside-the-budget.md) — the sister rule on keeping budget and forecast as separate instruments.

## Provenance

Codifies the FP&A planning-calendar and RACI discipline from the finance plugin's knowledge file `knowledge/fpa-operating-model-and-planning.md` and house opinion #6 (audit trail in every workpaper). The lock-date discipline reflects standard FP&A practice: the RACI/milestone structure is drawn from the `driver-based-forecasting` skill's planning section.

---

_Last reviewed: 2026-06-05 by `claude`_

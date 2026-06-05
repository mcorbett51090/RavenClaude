# Earned Value Tells Two Stories — Schedule and Cost — Report Both

**Status:** Pattern
**Domain:** Project Management — Predictive / Earned Value
**Applies to:** `project-management`

---

## Why this exists

Earned value management (EVM) generates two independent performance signals: the **Schedule Performance Index (SPI)** and the **Cost Performance Index (CPI)**. A project that reports only "we're 10% over budget" omits the schedule picture; one that reports only "we're two weeks behind" omits the cost trajectory. The real insight — and the management decision — often lives in the *combination*: a CPI of 0.85 with an SPI of 1.10 (spending too much, but fast) calls for a completely different response than a CPI of 0.95 with an SPI of 0.80 (slightly overspent and behind schedule). Reporting one index without the other is not EVM — it is a partial look at a two-dimensional problem.

## How to apply

**Core EVM formulas:**

```
EV   = Earned Value   = % complete (physical) × BAC (Budget at Completion)
PV   = Planned Value  = what you planned to have done by today × BAC
AC   = Actual Cost    = what you have actually spent to date

SPI  = EV / PV        (> 1 = ahead; < 1 = behind)
CPI  = EV / AC        (> 1 = under budget; < 1 = over)

EAC  = BAC / CPI      (Estimate at Completion — assumes current efficiency holds)
VAC  = BAC - EAC      (Variance at Completion — the projected over/under-run)
```

**Minimum EVM status report block:**

```
Status date:     [YYYY-MM-DD]
BAC:             $[X]
PV (today):      $[X]   EV (today): $[X]   AC (today): $[X]
SPI:             [X.XX] → [ahead of schedule / on track / behind schedule]
CPI:             [X.XX] → [under budget / on budget / over budget]
EAC:             $[X]   (assumes CPI holds)
VAC:             $[X]   ([surplus / overrun] projection)
Narrative:       [1–3 sentences: what is driving the variance and what the PM is doing about it]
```

**Interpreting the quadrants:**

| SPI | CPI | Situation | Response |
|---|---|---|---|
| > 1 | > 1 | Ahead and under budget | Monitor; check for scope omission |
| > 1 | < 1 | Fast but expensive | Re-examine resourcing; check for gold-plating |
| < 1 | > 1 | Behind but efficient | Replan the schedule; more resources may help |
| < 1 | < 1 | Behind and over budget | High urgency; escalate; scope/approach may need to change |

**Do:**
- Report SPI *and* CPI together in every status report, with the EAC.
- Use physical percent complete (work accomplished), not time-elapsed or budget-spent, as the basis for EV.
- Trend EAC over time — a rising EAC curve earlier than mid-project is the signal to act.

**Don't:**
- Use the "50/50 rule" (claim 50% EV at start, 50% at finish) as a substitute for real percent-complete tracking on tasks longer than one reporting period.
- Report only CPI to a sponsor who asked "are we on track?" — schedule is the other half.
- Rebaseline the project to improve an SPI/CPI without documenting the change request.

## Edge cases / when the rule does NOT apply

- **Agile projects**: EVM applies at the release level (milestone burn-up vs plan), not at the sprint level; the sprint's measure is velocity and done stories. Hybrid projects use EVM at the outer milestone layer and velocity internally.
- **Time-and-material contracts with no fixed BAC**: CPI is undefined; report actual spend vs forecast and scope-delivered vs plan.

## See also

- [`../agents/delivery-lead.md`](../agents/delivery-lead.md) — the agent that owns baseline, EV tracking, and EAC forecasting
- [`./status-leads-with-narrative-and-matches-the-numbers.md`](./status-leads-with-narrative-and-matches-the-numbers.md) — the companion rule that the narrative must be consistent with the EV numbers

## Provenance

Codifies EVM discipline from PMBOK 6th edition (PMI) §7 (Cost Management) and §6 (Schedule). EVM formulas are standard PMI/ANSI EIA-748. _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_

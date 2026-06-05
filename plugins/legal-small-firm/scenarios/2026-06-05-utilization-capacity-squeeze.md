---
scenario_id: 2026-06-05-utilization-capacity-squeeze
contributed_at: 2026-06-05
plugin: legal-small-firm
product: capacity
product_version: "n/a"
scope: likely-general
tags: [utilization, non-billable, capacity, delegation, hiring]
confidence: medium
reviewed: false
---

## Problem

A 2-attorney firm felt permanently maxed out and was about to hire a third lawyer "to keep up," but revenue had been flat for a year. The owner was working 60-hour weeks and assumed the problem was a shortage of lawyer hours. The risk: hiring into a **utilization** problem (lawyer time consumed by non-billable admin and delegable work) instead of a genuine **demand** problem just adds a second under-utilized attorney and a salary, deepening the hole rather than filling it.

## Context

- Segment: transactional + family-law mix, independent, 2 attorneys + 1 part-time admin, no paralegal.
- Constraint: this is a **capacity-composition** problem, not a headcount problem. Utilization (billable hours ÷ available hours) was low *despite* the long weeks because the non-billable/admin load (intake, billing, scheduling, document assembly, collections follow-up) sat on the attorneys. Clio's 2025 benchmark frames the scale of the leak: average utilization is **~38%** — most of an 8-hour day is *not* captured as billable. `[verify-at-use]` — aggregate, not this firm's figure.
- The owner reasoned from "we're slammed" without measuring how much of the slam was billable.

## Attempts

- Tried: measured **utilization** and categorized the **non-billable load** before any hiring decision — split every tracked hour into billable, delegable-non-billable (admin a paralegal/assistant could do), and genuine attorney-only non-billable (BD, firm management). Outcome: the bottleneck was delegable admin sitting on attorney time, not a shortage of attorney capacity. Non-billable time must be *categorized*, not just excluded (best-practices/non-billable-time-must-be-categorized).
- Tried: checked the cheaper capacity levers before headcount — **delegate** delegable work to a paralegal/assistant, tighten intake and billing workflow, and recover attorney hours — per the cheap-levers-first discipline. Outcome: confirmed a paralegal hire (or shifting work to the existing admin) recovered far more billable attorney capacity per dollar than a second attorney would.
- Tried: framed the economics with the **Rule of Thirds** as a sanity check — a billable hire should generate roughly **3× their fully-loaded cost** (comp + benefits + overhead), so a lawyer costing ~$150k should be billing/collecting ~$450k. The firm's demand didn't support that for a third *attorney*, but it easily justified a paralegal who frees attorney hours that are already in demand. Outcome: a defensible hire decision (support staff, not another lawyer) with a target, not a gut call.

## Resolution

The squeeze was **low utilization from a delegable non-billable load**, not a lawyer shortage. Delegating admin/paralegal work and tightening intake/billing workflow recovered billable attorney capacity for a fraction of a second attorney's cost; the Rule-of-Thirds threshold showed demand didn't yet support another lawyer. Utilization and the non-billable load are a capacity story (§3 #5); rule out the cheap levers before the expensive ones.

**Action for the next consultant hitting this pattern:** measure utilization and **categorize** the non-billable load before any hire. If delegable admin is sitting on attorney time, a paralegal/assistant (or workflow fix) is the cheaper, faster lever than a lawyer. Pressure-test any billable hire against the Rule of Thirds (≥3× fully-loaded cost in collected revenue) — and remember it is a guideline, not a commandment (`[verify-at-use]`). The [`../scripts/legal_calc.py`](../scripts/legal_calc.py) `utilization` mode reads the billable ratio and the non-billable split; `rule-of-thirds` mode does the hire-threshold arithmetic.

**Sources (retrieved 2026-06-05):**
- Clio — 2025 Legal Trends benchmarks (utilization ~38%): https://www.clio.com/resources/legal-trends/benchmarks/
- LeanLaw — The Rule of Thirds for law firm profitability (3× cost-of-employment threshold; comp/overhead/profit ≈ 1/3 each): https://www.leanlaw.co/blog/the-rule-of-thirds-a-simple-framework-for-allocating-law-firm-revenue/
- CARET Legal — How to calculate your firm's Rule of Thirds: https://caretlegal.com/blog/simplifying-your-law-firms-rule-of-thirds-calculation/

The Rule of Thirds is a guideline (overhead commonly runs 45–50% in practice, not 33%) and the utilization benchmark is an aggregate — both are `[verify-at-use]`, calibrate to the firm's segment and actual numbers (§3 #8).

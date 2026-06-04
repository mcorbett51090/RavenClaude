---
name: bill-rate-margin-modeling
description: Decompose staffing margin into bill minus pay minus burden, itemize the burden stack, and locate whether a compression is pricing, pay, burden, or mix — before anyone calls it a pricing problem. Reach for this when gross margin or spread is moving and the cause is unclear.
---

# Skill: Bill-rate / margin modeling

A "margin is down" finding with no decomposition sends operators to reprice when the problem is often a burden line or a mix shift. This skill decomposes before diagnosing (§3 #3).

## Step 1 — Write the identity
Margin $ = bill − pay − burden. Margin % = (bill − pay − burden) ÷ bill. Compute both for the period in question and a healthy baseline. Never reason about margin % without the dollar bridge — a % move can be a denominator (bill-rate) effect.

## Step 2 — Itemize the burden stack
Employer payroll taxes (FICA/FUTA/SUTA), workers' comp, **professional/general liability + malpractice** (heavy in locums), benefits, **housing/lodging/per-diem stipends + travel** (travel nursing), credentialing/onboarding cost, and **bench/idle time**. Pull each as a line; compression hides here more than in the headline markup. See [`../../knowledge/healthcare-staffing-economics.md`](../../knowledge/healthcare-staffing-economics.md) §1.

## Step 3 — Run the four-way attribution
Decompose the margin move into:
- **Bill rate down** — rate-cycle pressure, MSP caps, or mix to lower-bill segments.
- **Pay rate up** — candidate-supply scarcity forcing pay.
- **Burden line up** — which one (malpractice? stipends? bench?).
- **Mix shift** — more low-margin per-diem / less high-margin allied, at the portfolio level.

Quantify each contribution; usually one or two dominate.

## Step 4 — Place it against the rate cycle
A travel-nurse bill rate is only "low" relative to a dated benchmark — anchor to the SIA/NATHO series (~$133→$90/hr, 2022→2025) with the date. An operator anchored to 2021 peak rates will misread a normalized rate as a crisis (§3 #9).

## Step 5 — Check bench/idle and redeployment
Unbilled bench time is a margin leak that looks like a rate problem. If idle time is the driver, the lever is redeployment rate (the cheapest placement), not pricing.

## Step 6 — Flag the compliance landmines, don't advise on them
Per-diem stipend structure (IRS tax-home rules) and worker classification (1099 vs. W-2, gig-platform reclassification) are margin levers *and* legal exposures. Surface them; route the actual treatment to the client's tax/legal counsel. Do not give the advice.

## Step 7 — Output the bridge
A waterfall from baseline margin to current margin with each driver's contribution, the dominant line named, and the recommended lever (reprice / renegotiate burden / shift mix / cut bench) with its expected movement.

## Reference
Economics + burden detail: [`../../knowledge/healthcare-staffing-economics.md`](../../knowledge/healthcare-staffing-economics.md). Decision tree: [`../../knowledge/staffing-decision-trees.md`](../../knowledge/staffing-decision-trees.md) (Margin/spread tree). Template: [`../../templates/bill-rate-margin-model.md`](../../templates/bill-rate-margin-model.md).

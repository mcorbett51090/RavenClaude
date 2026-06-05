---
scenario_id: 2026-06-05-payer-contract-underpayment
contributed_at: 2026-06-05
plugin: medical-revenue-cycle
product: payer-contract
product_version: "n/a"
scope: likely-general
tags: [payer-contract, underpayment, allowed-amount, variance, co-45]
confidence: medium
reviewed: false
---

## Problem

A practice's net collection rate had slipped a couple of points and the assumption was "coding is getting worse." But the coding denial rate was flat. The real leak was quieter and more insidious: one commercial payer was **paying below the contracted allowed amount** on a subset of codes — a silent underpayment that never shows up as a denial, so it never enters the denial worklist. The contractual-adjustment write-off was absorbing the gap as if it were a normal allowed-amount reduction.

## Context

- Segment: physician-group, commercial-heavy, multiple contracted payers with different fee schedules.
- Constraint: the team had no **expected-allowed-amount** loaded per payer/CPT, so every payment was reconciled against billed charges (a vanity number, §3 #4) rather than against the contracted rate. Without the contracted ceiling loaded, an underpayment is indistinguishable from a normal contractual adjustment — it disappears into the write-off.
- The team conflated a falling net collection rate with "coding" (one cause) when the coding denial rate was unchanged — the §3 #4 misread (reading against gross charges, not the allowed amount, hides a payer-side underpayment).

## Attempts

- Tried: **decomposed the net-collection-rate drop by payer before blaming coding** (the rcm-decision-trees "low NCR — coding or payer?" tree). The drop was concentrated in one payer with a stable coding denial rate and a stable clean-claim rate — the signature of a payer-side adjudication/payment change, not an internal process failure (§3 #4, §3 #5). Outcome: reframed from "fix coding" to "audit this payer's payments against contract."
- Tried: **loaded the contracted allowed amounts** for the suspect payer's top codes and compared actual paid to expected allowed line by line — pulling EOBs/ERAs and the remittance CARCs. The variance was a real underpayment (paid < contracted), distinct from a legitimate CARC **CO-45** "charge exceeds the contracted fee" adjustment, which is the *correct* contractual write-down, not a recoverable balance. Outcome: a quantified, defensible underpayment total.
- Tried: routed the recoverable variance to **payer relations / contract escalation** (not the denial appeal queue — an underpayment isn't a denial) and instituted ongoing expected-vs-actual reconciliation so the next underpayment surfaces in days, not quarters. Outcome: recovered the variance and closed the blind spot.

## Resolution

The net-collection-rate slip was a **silent payer underpayment**, not a coding regression. The fix required loading the contracted allowed amount as the reconciliation baseline (§3 #4 — measure against allowed, never against gross charges), decomposing NCR by payer, and separating a recoverable underpayment from a legitimate CO-45 contractual adjustment. The recoverable variance went to contract escalation, and a standing expected-vs-actual reconciliation made the blind spot permanent-fixed.

**Action for the next consultant hitting this pattern:** when net collection rate drops with a **flat coding-denial rate**, suspect the **payer side**, not coding — decompose NCR by payer and audit actual-paid against the **contracted allowed amount** (§3 #4). You can only see an underpayment if the expected allowed amount is loaded; reconciling against billed charges hides it. Separate a recoverable underpayment from a legitimate CARC **CO-45** contractual adjustment (the latter is the correct write-down, not a balance to chase), and route recoverable variance to **payer relations / contract escalation**, not the appeal queue (§3 #4 — write-off discipline separates contractual adjustment from recoverable balance).

**Sources (retrieved 2026-06-05):** net-collection-rate vs gross / allowed framing — https://www.mdclarity.com/blog/rcm-benchmarks and https://www.medicalbillersandcoders.com/blog/net-collection-ratio-benchmarks-multi-specialty-groups/ ; CARC CO-45 (charge exceeds fee schedule / contracted amount) — https://www.sprypt.com/denial-codes/carc-and-rarc-codes and https://x12.org/codes/claim-adjustment-reason-codes . Specific variance figures are payer- and contract-dependent; treat any number here as `[ESTIMATE]` and validate against the client's contract and ERAs (§3 #8).

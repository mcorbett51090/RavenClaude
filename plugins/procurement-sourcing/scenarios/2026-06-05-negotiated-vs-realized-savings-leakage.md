---
scenario_id: 2026-06-05-negotiated-vs-realized-savings-leakage
contributed_at: 2026-06-05
plugin: procurement-sourcing
product: savings
product_version: "n/a"
scope: likely-general
tags: [savings, realization, leakage, maverick-spend, finance-baseline]
confidence: medium
reviewed: false
---

## Problem

A category team reported a large negotiated-savings number from a completed sourcing event, but Finance refused to recognize it — the P&L showed almost none of it. The CPO scorecard and the Finance ledger were telling two different stories, and the team was being accused of "savings theater." The real question was not "who's right" but **where the negotiated number leaked between contract signature and invoice payment**.

## Context

- Segment: indirect category, mid-size enterprise, no automated savings-tracking — savings were claimed at contract signature and never re-checked against invoices.
- Constraint: there was **no baseline agreed with Finance before the event**, so the "savings" was a claim, not a measurement (the §3 #3 precondition was skipped).
- The team conflated "negotiated rate" with "P&L impact" — the classic single-number story the decision trees warn against. Off-contract (maverick) buying and a volume miss were both invisible because nobody decomposed the gap.

## Attempts

- Tried: walked the negotiated number down the realization chain instead of defending it. Sources of the gap, in order found: (1) **volume miss** — the business bought materially less than the contracted volume the savings assumed; (2) **maverick spend** — a chunk of spend kept going to the old supplier at the old price (off-contract); (3) **in-budget offset** — part of the "saving" was already in the AOP, so it was cost avoidance, not incremental. Outcome: reframed from "prove the saving" to "fix the leak."
- Tried: ran `scripts/sourcing_calc.py savings` with the realized-volume / compliance / in-budget fractions to size each leak quantitatively — negotiated → realized → incremental — so the conversation with Finance moved from anecdote to arithmetic. Outcome: a defensible realized number both sides could sign.
- Tried: instituted a **finance-agreed baseline before the next event** and a quarterly identified → committed → implemented → realized stage gate with named owners. Outcome: future claims tracked to the ledger by construction.

## Resolution

The negotiated number was real but **leaked 30-60% between signature and invoice** — the published benchmark range for untracked savings — driven mostly by volume miss and maverick spend, with a slice that was never incremental (already in budget). The fix was process, not re-negotiation: a Finance-agreed baseline up front, a realization stage gate, and a maverick-spend clamp (route the off-contract buyers back to the contract).

**Action for the next consultant hitting this pattern:** never report negotiated savings as P&L impact. **Agree the baseline with Finance before the event** (§3 #3), then walk negotiated → realized → incremental: multiply by realized-volume fraction, by on-contract-compliance fraction, and strip the in-budget portion to cost avoidance. A realization rate below ~60% is the "untracked-leakage" signal — locate the leak (volume miss vs maverick) before blaming the rate or re-sourcing.

**Sources (retrieved 2026-06-05):** savings leakage / realization range — https://www.traceconsultants.com.au/thinking/why-procurement-savings-leak-after-award ; https://umbrex.com/resources/company-analysis/finance/procurement-savings-realization-rate/ ; negotiated-vs-realized + leakage points — https://procurpal.in/expected-vs-realized-savings-why-procurement-needs-better-analytics/ . The "30-60% leak" / "<60% realization" figures are public-benchmark ranges, not the client's — treat as `[ESTIMATE]` and validate against the actual ledger (§3 #8).

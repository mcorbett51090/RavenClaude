---
scenario_id: 2026-06-05-dscr-breach-on-refi-rate-reset
contributed_at: 2026-06-05
plugin: commercial-real-estate
product: debt-finance
product_version: "n/a"
scope: likely-general
tags: [dscr, refinance, rate-reset, debt-yield, cash-in]
confidence: medium
reviewed: false
---

## Problem

A stabilized asset acquired in a low-rate vintage was approaching loan maturity, and the sponsor had modeled the refinance as a routine roll — same LTV, slightly higher rate, cash-out or at worst cash-neutral. The take-out lender's term sheet came back at a materially higher rate, and at that rate the in-place NOI no longer cleared the lender's minimum DSCR. The deal didn't fail on value — it failed at the refi (CLAUDE.md §3 #6, debt is the swing factor).

## Context

- Segment: stabilized commercial (the pattern is asset-class-agnostic — multifamily, industrial, office, retail all hit it on a rate reset).
- Constraint: the original loan was sized when rates were low, so debt service was small relative to NOI and the loan looked safe. The refinance re-sizes debt service at today's rate, and in a higher-rate environment the **binding constraint flips** — proceeds get capped by DSCR or debt yield, not by LTV.
- The sponsor was reasoning from "the asset is worth more than the loan, so the refi is fine," which conflates value (an LTV question) with the income's ability to carry new debt service (a DSCR/debt-yield question).

## Attempts

- Tried: re-sized the loan against **all three lender constraints** — max LTV, min DSCR, and min debt yield — instead of assuming LTV would bind. Current-market reference points used to frame the conversation (dated, `[verify-at-use]`): a general commercial-mortgage starting point of ~1.25x minimum DSCR, with riskier asset classes (hotel/retail) pushed to 1.40x–1.50x; agency multifamily (Fannie/Freddie) commonly ~1.25x; lenders pairing ~75% max LTV, ~1.25x min DSCR, and ~10% min debt yield. Outcome: the binding constraint was **debt yield**, then DSCR — LTV had the most room. Max proceeds came in well below the maturing balance.
- Tried: quantified the **cash-in** required to refinance — the gap between the maturing loan balance and the new (smaller) proceeds the asset could carry. Outcome: turned a vague "the refi is tight" into a specific equity check the sponsor had to write to close the gap.
- Tried: priced the two alternatives to a cash-in refi — (a) sell now into the clearing market, (b) negotiate a maturity extension / modification with the existing lender — so the cash-in number had something to be compared against rather than being accepted by default.

## Resolution

The refinance was re-underwritten to the binding constraint (debt yield/DSCR, not LTV), which surfaced a required cash-in well before maturity — early enough to weigh it against a sale-now and a lender-extension path rather than discovering it at the closing table. The output was a dated debt-sizing model showing each constraint's max proceeds and the cash-in gap, not a "should be fine" assumption.

**Action for the next analyst hitting this pattern:** **never size a refinance on LTV alone in a higher-rate market — model the binding of LTV / DSCR / debt yield, because the binding constraint flips on a rate reset.** Surface the cash-in gap early and price it against sell-now and extend-and-modify. The [`../scripts/cre_calc.py`](../scripts/cre_calc.py) `debt-size` mode prints each constraint's max proceeds and names the binding one; the [`../knowledge/cre-decision-trees.md`](../knowledge/cre-decision-trees.md) "Sell or hold through the refi?" tree sequences the comparison.

**Sources (retrieved 2026-06-05 — `[verify-at-use]`, these move):**
- Commercial Loan Direct — 2026 DSCR requirements for CRE loans: https://commercialloandirect.com/2026-dscr-requirements-commercial-real-estate-loans
- Cor Advisors — DSCR loan requirements 2026 (minimum ratios, lender changes): https://www.coradvisors.net/2026/04/dscr-loan-requirements-2026.html
- Altus Group — how to calculate debt yield in CRE (debt yield as the binding proceeds cap in a rising-rate market): https://www.altusgroup.com/insights/how-to-calculate-debt-yield-in-cre/

DSCR/LTV/debt-yield thresholds are lender- and asset-class-specific and rate-sensitive — treat every number above as `[verify-at-use]` against a current term sheet (§3 #8).

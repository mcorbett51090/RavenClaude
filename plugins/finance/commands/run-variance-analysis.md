---
description: "Run a variance analysis the right way: reconcile before you narrate, decompose revenue/unit-cost lines into price/volume/mix that sum to the total, apply a materiality threshold, and name the driver (with its owner) — not just the variance."
argument-hint: "[the line + period, e.g. 'Q3 gross margin down 200bps vs plan']"
---

# Run a variance analysis

You are running `/finance:run-variance-analysis`. Diagnose and narrate the variance the user described (`$ARGUMENTS`), following this plugin's `fpa-analyst` discipline. Commentary written on an unreconciled account describes bookkeeping noise, not business performance.

## When to use this

A material budget/forecast/prior-period variance needs explaining for a board pack, a monthly close, or an exec review. Not for variances below the engagement's materiality threshold (no commentary is owed) and not before the account is reconciled (route to the controller first).

## Steps

1. **Reconcile before you narrate** (`reconcile-before-you-narrate`): confirm the account is reconciled and the sub-ledger ties to the GL, with preparer + reviewer sign-off, *before* drafting a word. If recon is incomplete, ship the deliverable as partial with an open question routed to `controller` — do not narrate a cause on a number that is about to move.
2. **Apply the materiality threshold** (per house opinion #5): state the threshold (typically the greater of $50K or 5%) and only explain variances that breach it — materiality is a design constraint, not a footnote.
3. **Decompose revenue / unit-driven-cost lines into price, volume, mix** (`fpa-build-the-variance-bridge-price-volume-mix`): compute volume (qty change at budget price), price (price change at actual qty), and mix; the three must sum exactly to the total variance, and net any FX out first (constant-currency). Where data won't support a clean three-way split, a two-way rate x volume bridge is the honest fallback.
4. **Name the driver, not the variance** (`fpa-build-the-variance-bridge-price-volume-mix`): hand each slice to its owner — price → pricing/sales, volume → demand/sales, mix → product/segment. "Revenue missed by $X" with no driver is half a deliverable.
5. **Source-cite every number** (house opinion #1): each load-bearing figure carries its source (GL account + period, model tab + cell). The advisory hook flags a variance file with no `Source:` line.

## Guardrails

- Don't let a stakeholder's pre-offered explanation ("sales said the deal slipped") substitute for tying the account first.
- Confuse-proof the mix vs volume call: a customer-base tier shift is mix, not lost units.
- Non-unit-driven lines (fixed opex, a one-time accrual) have no PVM structure — traverse to the timing / one-time / decision leaf of `variance-root-cause-triage` instead.

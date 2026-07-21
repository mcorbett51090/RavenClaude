---
name: model-plans-and-pricing
description: "Model the plan / price / entitlement structure for a recurring-billing system — choose flat vs tiered vs per-seat vs usage/metered vs hybrid, define entitlements, and set proration/trial/coupon rules. Use when starting a billing build or re-pricing an existing product."
---

# Skill: Model Plans and Pricing

Turn a pricing intent into a concrete, buildable **plan / price / entitlement model** — the shape everything downstream (proration, metering, dunning, entitlements) depends on. Get this wrong and every customer must be re-priced to fix it.

## When to use

- Standing up a new subscription-billing system.
- Re-pricing or re-packaging an existing product (adding usage, seats, tiers, add-ons).
- Deciding what a "plan" even is before touching a provider API.

## Steps

1. **Establish how value is delivered and metered.** Is value per-user (seats), per-consumption (API calls, GB, events), per-feature-tier, or flat access? The billing model should mirror the value axis — this is the single most important decision. Traverse [`../../knowledge/billing-model-decision-tree.md`](../../knowledge/billing-model-decision-tree.md).
2. **Pick the model** — flat, tiered (feature tiers), per-seat, usage/metered, or hybrid (base + overage). Name explicitly what you are **not** adopting yet and why (e.g. "no per-seat until we have team accounts").
3. **Define the price objects.** Currency(ies), billing interval(s) (monthly/annual + annual discount), plan/price ids, add-ons. Keep prices immutable and versioned — never mutate a live price; create a new one and migrate.
4. **Define entitlements separately from plans.** List what each plan *allows* (limits, features, quotas). Entitlements are derived from billing state but are their own first-class model, so a plan change or dunning downgrade updates them predictably.
5. **Set the mid-cycle-change rules.** Proration on upgrade/downgrade (immediate vs next-cycle, credit vs invoice), seat add/remove, trial-to-paid conversion, plan switch. This becomes the [`proration-upgrade-test-matrix`](../../templates/proration-upgrade-test-matrix.md).
6. **Set trial and discount rules.** Trial length, card-required-or-not, trial-end behavior; coupon/discount stacking rules and whether they apply to overage.
7. **Trace the correctness seams.** Where does recognized revenue (ASC 606) come from, and where does sales-tax/VAT get calculated? A model that can't produce them is incomplete — flag the seam even if `finance` / `regulatory-compliance` owns it.

## Anti-patterns

- Baking per-seat into the schema when the product is really consumption (or vice versa) — the most expensive model mistake.
- Treating entitlements as an afterthought derived ad-hoc from the plan name in application code.
- Mutating a live price instead of versioning a new one.
- Selling usage-based before you can meter the usage accurately and idempotently.
- No explicit proration spec — "the provider handles it" until an upgrade produces a surprising invoice.

## Output

A plan/price/entitlement model doc: value axis → chosen model (+ what's excluded) → price objects → entitlement map → proration/trial/coupon rules → revrec + tax seams. Feed it to [`billing-implementation-engineer`](../../agents/billing-implementation-engineer.md) and the [`billing-integration-runbook`](../../templates/billing-integration-runbook.md).

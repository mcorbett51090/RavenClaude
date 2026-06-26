# Pricing & monetization — 2026 reference

> Dated reference for volatile, fast-moving pricing facts. Every figure or trend
> here carries the spirit of the ravenclaude-core Claim Grounding protocol: it is a
> **2026-dated snapshot, re-verify at use**. Pricing benchmarks, competitor prices,
> and "what's standard now" rot faster than almost any other knowledge in this repo.
> Treat the *reasoning* as durable and the *specific figures* as needing a fresh
> check before they gate a decision.

_Compiled 2026-06-26. Trends below reflect the author's training knowledge + the
durable economics; mark any figure you quote downstream as `[2026 snapshot —
re-verify]` and prefer a live source for a number that gates a real price._

## Model trends (the durable shifts)

- **Usage-based and hybrid pricing keep gaining share** over pure per-seat,
  especially for infrastructure, API, and data products. The dominant pattern is
  **hybrid**: a committed platform/base fee + an included allowance + metered overage.
  It gives the vendor a revenue floor and the customer a predictable base while still
  aligning price with value at the margin.
- **Per-seat is under pressure where AI does the work.** When an AI feature reduces
  the number of humans needed, per-seat *shrinks the account as the product
  succeeds* — the opposite of a good value metric. Products with heavy AI cost are
  moving toward usage, outcome, or hybrid metrics.
- **"Outcome-based" pricing is much-discussed and rarely clean.** Charging on the
  customer's result (e.g. per resolved ticket, per qualified lead) aligns value
  perfectly but is hard to meter, attribute, and defend in a dispute. Treat it as a
  *premium overage dimension* on top of a steadier base, not the whole model, unless
  attribution is genuinely clean.

## AI-product pricing (the live frontier)

- Marginal cost is **real and variable** (tokens/compute), so a flat per-seat plan
  on a heavy-AI product invites negative-margin power users. Favor **usage or hybrid**,
  with an included allowance sized to the median user and metered overage for heavy use.
- **Credits** are a common UX wrapper over usage — they decouple the customer-facing
  unit from the underlying cost so you can re-cost without re-pricing. Useful, but
  watch for credit-hoarding and breakage that distorts your revenue read.
- Price the **base on a predictable proxy** (seats, workspaces) and the **AI
  consumption on usage** — a clean instance of "predictable base + value-aligned
  expansion" from the value-metric tree.

## WTP-method tradeoffs (quick reference)

| Method | Best for | Gives you | Cost | Watch |
|---|---|---|---|---|
| Van Westendorp PSM | Earliest, cheapest sanity check | An *acceptable range* + too-cheap/too-expensive points | Low | A range, not a price; stated > real |
| Gabor-Granger | Picking a number once you have a band | Demand + revenue curve at tested points | Low-Med | Tests only the points you choose |
| Conjoint / MaxDiff | Packaging & feature-value tradeoffs | Relative value of features → tier design | Med-High | Survey complexity; needs decent n |
| Live price A/B test | When you have traffic | Observed behavior (the gold standard) | Med | Significance → `applied-statistics` |

## Packaging patterns that hold up

- **Good-better-best with a fenced middle** — three tiers where the *middle* is the
  intended default, fenced so most of the target lands there; the top tier anchors
  and the bottom captures the price-sensitive.
- **Fence on a self-selection dimension** — scale (seats/volume), use case, support
  level, security/compliance. Customers should sort *themselves* into the right tier.
- **Add-ons for the long tail** — features only some customers value belong as
  add-ons, not as a reason to create a fourth tier.
- **Anchor with a visible enterprise tier** even if most don't buy it — it reframes
  the middle tier as reasonable.

## Price-change playbook (the durable steps)

1. **Decide the goal** — margin recovery, repackaging, model migration, or simplification. The goal sets the mechanics.
2. **Grandfather deliberately** — existing customers at the old price for a defined window; a price increase that hits the loyal base first is how you manufacture churn.
3. **Sequence by cohort & renewal date** — never migrate everyone at once; read the churn/contraction/leakage signal on the first cohort before committing the base.
4. **Time to the renewal** — change at renewal, not mid-term, to respect contracts and reduce surprise.
5. **Comms before invoice** — the increase should never first appear on a bill; lead with the value narrative.
6. **Instrument the guardrails** — watch GRR, contraction, discount leakage, and win-rate on the changed cohort; have a rollback/concession plan ready.

## Legal boundary (not advice — route to counsel)

Price-fixing, **resale-price maintenance / MAP** enforcement, regional price
regulation, and anti-trust exposure are **legal** questions. This plugin flags them
and routes to counsel (`legal-ops-clm` for contract language); it does not issue a
legal verdict.

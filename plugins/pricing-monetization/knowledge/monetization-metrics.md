# Monetization metrics — glossary, formulas, and what each one is allowed to tell you

The metric set the `monetization-analyst` defines before measuring. Each entry: the
formula, what it tells you, and the trap it hides. **Realized (net-of-discount)
figures are the truth; list-price figures are marketing.**

---

## Revenue-per-customer

| Metric | Formula | Tells you | Trap |
|---|---|---|---|
| **ARPA / ARPU** | Recurring revenue ÷ # accounts (or users) in the period | The average price you actually realize | An *average* hides mix — a rising ARPA can be a real price lift **or** low-end churn dragging the mean up. Always decompose. |
| **Realized vs list price** | ARPA ÷ list price for the same package | How much of your list price survives the deal desk | The gap *is* discount leakage; if it's >~15–20% your list price is fiction. |
| **Gross margin per customer** | (Revenue − cost-to-serve) ÷ # customers | Whether a customer is worth keeping at this price | A usage/AI product can have a *negative*-margin heavy user that ARPA hides. |

## Retention & expansion (the monetization scoreboard)

| Metric | Formula | Tells you | Trap |
|---|---|---|---|
| **NRR (Net Revenue Retention)** | (Starting MRR + expansion − contraction − churn) ÷ starting MRR, for a cohort, excl. new logos | Whether the monetization *design* compounds — the single best pricing scoreboard | NRR > 100% can coexist with bad logo retention if a few accounts expand hard; read it **with** GRR. |
| **GRR (Gross Revenue Retention)** | (Starting MRR − contraction − churn) ÷ starting MRR (no expansion credit) | The floor — how much you keep before any expansion | Capped at 100%; a low GRR with high NRR means you're masking churn with a few whales. |
| **Expansion rate** | Expansion MRR ÷ starting MRR | Whether the value metric creates automatic growth | High expansion is the *signal a good value metric is working*; near-zero expansion often means a flat/seat-capped metric. |
| **Contraction rate** | Downgrade MRR ÷ starting MRR | Whether customers are right-sizing *down* | Rising contraction after a price change = you over-fenced or over-priced a tier. |

## Discount & deal health

| Metric | Formula | Tells you | Trap |
|---|---|---|---|
| **Discount leakage** | 1 − (realized ARPA ÷ list ARPA) | The revenue lost between the price card and the signed deal | Report it **decomposed** by segment / deal-size / quarter — leakage almost always concentrates; the average is not the finding. |
| **Discount depth distribution** | Histogram of discount % across closed deals | Whether discounting is policy or chaos | A long tail past your approval threshold = governance is being bypassed. |

## Efficiency

| Metric | Formula | Tells you | Trap |
|---|---|---|---|
| **CAC payback** | CAC ÷ (ARPA × gross margin %) | Months to recover acquisition cost at this price | Improves directly with price — a pricing lever, not just a sales-efficiency one. |
| **LTV\:CAC** | (ARPA × GM% × avg lifetime) ÷ CAC | Whether unit economics support the spend | The *LTV math itself routes to `finance`* — this plugin supplies the price inputs, finance models lifetime/discounting. |

## The rule-of-40 caveat

> **Rule of 40:** growth rate % + profit margin % ≥ 40 is a rough health bar for a
> software business. It is a **portfolio sanity check, not a pricing instrument.**

- It says nothing about *whether your price is right* — a company can hit 40 with a
  mispriced product (growing fast, leaving money on the table) or miss it while
  perfectly priced (a healthy mature business in a slow market).
- Do **not** back-solve a price from the rule of 40. Use NRR, expansion, realized
  ARPA, and discount leakage to judge the *pricing*; use the rule of 40 only to
  sanity-check the *whole business* alongside `finance`.

## What to lead with

For a "is our monetization working?" question, lead with **NRR + expansion rate**
(does the design compound?), then **realized ARPA + discount leakage** (are we
keeping our price?), then **GRR** (are we keeping customers at all?). One average
ARPA number, undeclined and undecomposed, is the most common way to *sound*
analytical while saying nothing.

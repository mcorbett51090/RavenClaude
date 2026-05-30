# Manage the cash-conversion cycle — DSO + DIO − DPO is cash you can free without financing

**Status:** Pattern
**Domain:** Treasury / working capital
**Applies to:** `finance`

---

## Why this exists

Working capital is the cheapest source of cash a company has — money trapped in receivables and inventory, or released by supplier terms, that needs no lender's approval and pays no interest. The **cash-conversion cycle** measures how long a dollar is tied up: `CCC = DSO + DIO − DPO` (days sales outstanding + days inventory outstanding − days payable outstanding). A company growing revenue with a lengthening CCC is *consuming* cash even while it reports profit — the classic "profitable but insolvent" trap. The `treasury-analyst` agent owns DSO/DPO/DIO trends and collections strategy, and the `financial-modeler` drives the AR/AP/inventory rolls off exactly these days-metrics. Managing the CCC is the lever that turns a tight 13-week forecast into a survivable one without drawing the revolver.

## How to apply

Compute each leg, trend it, and convert a days-improvement into a one-time cash release — then attack the worst leg first:

```
DSO = AR / revenue × days            # collect faster -> cash in
DIO = inventory / COGS × days        # turn inventory faster -> cash freed
DPO = AP / COGS × days               # pay slower (within terms) -> cash retained
CCC = DSO + DIO − DPO                 # lower is better; trend it, don't snapshot it

Cash release from a 1-day DSO improvement ≈ daily revenue   (one-time, sustained)
Lever order:  collections (DSO) -> inventory turns (DIO) -> supplier terms (DPO, without breaking supplier trust)
```

**Do:**
- Trend the CCC across periods — a rising CCC during growth is an early warning that growth is eating cash.
- Quantify each lever in **dollars of cash released** (days × daily revenue/COGS), so the collections vs. inventory vs. terms decision is comparable.
- Tie the working-capital actions back into the 13-week forecast and the model's AR/AP/inventory rolls — same days-drivers, two places.

**Don't:**
- Stretch DPO past agreed terms to flatter the cycle — that is supplier financing taken without consent and breaks the relationship (and sometimes the contract).
- Treat a CCC snapshot as a result — it is a trend; a single month is noise.
- Optimize one leg in isolation — pulling DSO down while DIO balloons nets to nothing.

## Edge cases / when the rule does NOT apply

- **Negative-working-capital businesses** (subscription prepaid, marketplaces that collect before they pay) run a *negative* CCC by design — growth *generates* cash; the rule is to protect that structure, not "improve" it toward positive.
- **Service businesses with no inventory** drop the DIO term — CCC is DSO − DPO, and the same trending discipline applies.
- **A deliberate inventory build** ahead of a known demand spike or a supply-risk hedge legitimately raises DIO — disclose it as a decision, not a deterioration.

## See also

- [`./treasury-forecast-cash-direct-method-thirteen-weeks.md`](./treasury-forecast-cash-direct-method-thirteen-weeks.md) — the forecast the freed cash flows into.
- [`./model-drive-the-forecast-off-operational-drivers.md`](./model-drive-the-forecast-off-operational-drivers.md) — DSO/DPO/DIO as the working-capital drivers in the model.
- [`../agents/treasury-analyst.md`](../agents/treasury-analyst.md) — working-capital surface area (DSO/DPO/DIO, collections strategy, inventory turns).
- [`../skills/thirteen-week-cash-forecast/SKILL.md`](../skills/thirteen-week-cash-forecast/SKILL.md) — where working-capital actions are ranked by cash impact.

## Provenance

Codifies the `treasury-analyst` working-capital surface area (DSO/DPO/DIO trends, collections strategy, payment-terms negotiation, inventory turns) in [`../agents/treasury-analyst.md`](../agents/treasury-analyst.md) and the `financial-modeler` working-capital-driver mechanics ([`../CLAUDE.md`](../CLAUDE.md) §8). The CCC = DSO + DIO − DPO identity is standard corporate-finance definition. New.

---

_Last reviewed: 2026-05-30 by `claude`_

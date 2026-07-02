# Fitness Studio / Gym Operations — 2026 Reference

> Dated reference for the `fitness-studio-gym-operations` team: the concepts that distinguish fitness-membership economics and the benchmarks agents reach for. The durable reasoning lives in [`fitness-studio-decision-trees.md`](fitness-studio-decision-trees.md); this file is the freshness-anchored "what the numbers and rules are."
>
> **Advisory, not legal, financial, or medical/exercise-prescription advice.** Every churn/LTV number, class-fill target, and instructor-pay norm below is **volatile and model-/market-specific**. Each row carries a **source placeholder + retrieval date + `[verify-at-use]`** — re-confirm against your own books and current market data before it drives a price, a pay model, or a growth decision. No member PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Treat every specific as `[verify-at-use]` unless re-confirmed this session._

---

## 1. Membership economics — the core identities (durable)

| Concept | Formula / definition | Note | Flag |
|---|---|---|---|
| Monthly churn rate | members lost in month / members at start of month | The denominator of LTV — the highest-leverage number | durable identity |
| Member LTV (simple) | monthly ARPU / monthly churn rate | Add ancillary ARPU for full LTV | durable identity |
| Net member change | joins − churned members | Gross joins alone is a vanity metric | durable identity |
| LTV : CAC | member LTV / cost to acquire a member | Under target = acquisition is unprofitable | durable identity |
| Class break-even headcount | (instructor pay + allocated room cost) / contribution per attendee | Per slot; the number that justifies a class | durable identity |
| Ancillary revenue per member | total ancillary revenue / active members | The margin dues can't reach | durable identity |

> These identities are durable; the **inputs** (churn, ARPU, CAC, contribution margin) are your own and must be pulled from current books, not assumed.

---

## 2. Benchmarks `[ESTIMATE]` — planning anchors only

| Metric | Reference character `[ESTIMATE]` | Source / retrieved | Flag |
|---|---|---|---|
| Monthly member churn | Varies widely by model (contract big-box vs month-to-month boutique); boutique studios typically run materially higher monthly churn than annual-contract clubs | _<source placeholder — industry benchmark>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Target average class fill rate | A healthy grid keeps most slots comfortably above break-even with waitlist pressure on peak times; exact target is capacity- and model-specific | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| No-show / late-cancel rate | Uncontrolled booking cultures can lose a meaningful share of booked spots to no-shows; policy pulls this down | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Ancillary (PT/retail/café) share of revenue | Often a large secondary revenue stream at higher margin than dues; mix varies by concept | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Early-frequency habit threshold | A minimum visits/week in the first weeks strongly predicts retention; the exact number is cohort-specific | _<source placeholder — retention research>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |

> These are planning anchors, not quotable facts. Confirm the current benchmark **and the studio's own baseline** before setting a target with an owner.

---

## 3. Instructor pay models — the trade space (durable)

| Model | Who carries empty-class risk | Best fit | Flag |
|---|---|---|---|
| Flat per class | Studio | High, predictable fill | pay amounts `[verify-at-use]` |
| Per head | Instructor | Variable fill / growth phase | pay amounts `[verify-at-use]` |
| Base + per head | Shared | Most boutique studios | pay amounts `[verify-at-use]` |

> The **structure** is durable; the dollar amounts, and any employment-classification (W-2 vs contractor) and wage-law implications, are `[verify-at-use]` and escalate to [`../../people-operations-hr/CLAUDE.md`](../../people-operations-hr/CLAUDE.md).

---

## 4. Pricing / tier architecture (durable trade-offs)

| Tier | Commitment | Churn / LTV character | Flag |
|---|---|---|---|
| Unlimited + contract | High | Lowest churn, highest LTV per member | prices `[verify-at-use]` |
| Month-to-month unlimited | Medium | Higher churn; price the flexibility | prices `[verify-at-use]` |
| Class-pack / punch card | Low | No recurring anchor; a win-back path | prices `[verify-at-use]` |

---

## 5. How to use this file

1. Find the concept/benchmark/model you need.
2. Read its retrieval date — if stale or unconfirmed this session, **re-verify** against the cited source type and your own books before quoting.
3. Quote it with its flag (`[ESTIMATE]` / `[verify-at-use]`) intact when it informs an owner-facing number.
4. For anything that drives a price, a pay model, or a capital decision: confirm against current data and your own P&L first.

---

## See also

- [`fitness-studio-decision-trees.md`](fitness-studio-decision-trees.md) — the durable churn-save / pricing / grid / instructor-pay trees.
- Retail-attach mechanics → [`../../retail-store-operations/CLAUDE.md`](../../retail-store-operations/CLAUDE.md); café P&L → [`../../restaurant-operations/CLAUDE.md`](../../restaurant-operations/CLAUDE.md); instructor staffing/pay law → [`../../people-operations-hr/CLAUDE.md`](../../people-operations-hr/CLAUDE.md).

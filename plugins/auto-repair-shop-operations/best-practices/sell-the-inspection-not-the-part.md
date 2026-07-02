# Sell the inspection, not the part

**Status:** Absolute rule
**Domain:** Front counter / estimating
**Applies to:** `auto-repair-shop-operations`

> Advisory operations rule. State estimate-authorization and disclosure specifics are `[verify-at-use]`. No customer PII.

---

## Why this exists

Customers don't buy parts they can't see the need for — they buy the **evidence** and the **consequence of waiting**. A digital vehicle inspection (DVI) with a photo, a measurement, or a reading against each recommended line turns "trust me, your brakes are low" into "here is the pad at 2mm and the spec." Evidence-led selling raises close rate and builds the trust that earns the next visit, and it keeps the upsell honest: you present what the vehicle needs, ranked by risk, and let the customer choose the pace. Leading with the price of a part the customer doesn't yet believe they need is how a good inspection dies at the counter.

## How to apply

- Attach DVI evidence (photo/measurement/reading) to **every** recommended line before you present it.
- Lead with the finding and the consequence of deferring, then the price — not the reverse.
- Present ranked **sell-now vs sell-later**: safety/failure-imminent now, wear items with life left as a dated deferred-service recommendation.
- Verify the complaint and get diagnostic authorization before you inspect and price (`[verify-at-use]` on the local disclosure rule).

**Do:** show the evidence; triage by safety and failure risk; log every decline for follow-up.
**Don't:** quote a part before the customer has seen why; hide deferred work; pressure past an honest no.

## Edge cases / when the rule does NOT apply

A customer who arrives with a specific authorized repair and declines any inspection is within their right — note it and proceed; the rule governs *how you recommend additional work*, not a mandate to inspect over refusal.

## See also

- [`../skills/estimate-and-dvi-workflow/SKILL.md`](../skills/estimate-and-dvi-workflow/SKILL.md)
- Template: [`../templates/repair-order-workflow.md`](../templates/repair-order-workflow.md)

## Provenance

Codifies `service-advisor-estimator` house opinion and the price-a-job and declined-work decision trees. Rates/labor times: [`../knowledge/auto-repair-shop-reference-2026.md`](../knowledge/auto-repair-shop-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_

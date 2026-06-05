# Client Retention Rate Is the Leading Indicator of Practice Health

**Status:** Primary diagnostic
**Domain:** Practice growth / client retention
**Applies to:** `veterinary-practice`

---

## Why this exists

New-client acquisition cost in veterinary medicine is 5–7x higher than the cost of retaining an existing client. [unverified — training knowledge] A practice that is losing 25%+ of its active clients annually requires constant and expensive new-client flow just to maintain a flat census — and new clients have lower ACT in their first year than established clients. Client retention rate is the leading indicator of practice health because it captures whether the client experience, pricing, and clinical relationship are delivering enough value to bring the client back. A declining retention rate predicts a revenue problem 12–18 months before it shows in production numbers.

## How to apply

Track annual client retention as a named metric separate from the new-client count.

```
Client retention metrics:
Definition: active client in Year 1 who returns for at least one visit in Year 2
Annual retention rate = returning clients ÷ total clients active in the prior period × 100
Target: ≥75–80% annual retention for a healthy general practice [unverified — training knowledge]

Segmentation (quarterly review):
  - Retention by patient life stage: puppy/kitten clients vs. adult vs. senior
    (puppy/kitten cohorts have the highest initial acquisition value; early attrition is expensive)
  - Retention by service type: wellness-plan clients vs. non-plan
    (plan clients should show significantly higher retention — validates plan value)
  - Retention by DVM: each DVM's client retention rate
    (>15 percentage-point variation between DVMs → investigate client experience factors)

Attrition reason tracking:
  - Configure client communication platform to send a re-engagement message
    at 15 months with no visit: "We miss [pet name] — is everything okay?"
  - Track: how many respond, how many rebook, what reasons are given for not returning
  - Common drivers: pricing, moved, pet deceased, wait time, communication
```

**Do:**
- Report client retention rate alongside new-patient count and ACT — it tells a fundamentally different story about practice health.
- Investigate a retention rate below 70% before investing in new-client marketing; plugging the retention leak is more efficient.
- Use the puppy/kitten cohort retention specifically — losing the first-year bond is a multi-year revenue loss.

**Don't:**
- Confuse visit frequency with retention — a client who visits once a year for the past 3 years is retained; a client who visited 5 times in one year and then disappeared is not.
- Measure retention on active-patient count without controlling for patient deaths (geriatric patients leaving due to death inflates apparent attrition).
- Treat retention as a marketing problem before investigating the clinical experience and pricing factors that drive it.

## Edge cases / when the rule does NOT apply

Emergency and specialty hospitals have structurally different client relationships — episodic, referral-based, and typically not year-over-year continuous. Retention metrics apply to the general-practice patient-base; emergency/specialty practices track referring-DVM relationships instead.

## See also

- [`../agents/vet-practice-lead.md`](../agents/vet-practice-lead.md) — client retention is an engagement-level practice health indicator.
- [`./wellness-plan-programs-smooth-revenue-and-improve-compliance.md`](./wellness-plan-programs-smooth-revenue-and-improve-compliance.md) — wellness plans are the most effective structural intervention for improving retention rate.

## Provenance

Standard veterinary practice management; grounded in client lifetime value modeling frameworks and veterinary practice consulting benchmarks; retention rate targets are [unverified — training knowledge] and should be benchmarked against current VetSuccess/Covetrus/AAHA published practice benchmarks.

---

_Last reviewed: 2026-06-05 by `claude`_

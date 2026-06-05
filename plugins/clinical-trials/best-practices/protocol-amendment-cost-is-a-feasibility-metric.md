# Protocol Amendment Cost Is a Feasibility Metric

**Status:** Pattern
**Domain:** Protocol design / trial economics
**Applies to:** `clinical-trials`

---

## Why this exists

The average Phase III trial incurs 2.3 protocol amendments; each substantial amendment costs an estimated $141,000–$535,000 in direct costs (IRB/EC fees, site notifications, training, regulatory submissions) and adds 3–4 months to the timeline. These costs are almost entirely avoidable — the top drivers are overly restrictive eligibility criteria, operationally infeasible procedures, and endpoints that didn't survive site feasibility review. Treating amendment cost as a design-phase feasibility metric rather than an operational surprise changes which protocol decisions get challenged upfront.

## How to apply

At every protocol review gate, run an amendment-risk assessment against the five most common amendment drivers:

```
Amendment Risk Checklist (complete before protocol lock):
  [ ] Eligibility criteria: any criterion with <10% prevalence in the target population? → high risk
  [ ] Visit burden: >12 study visits or any single visit >4 hours? → high risk
  [ ] Procedures: any procedure not routinely available at ≥80% of planned sites? → high risk
  [ ] Endpoints: primary endpoint based on a biomarker with <70% assay availability? → high risk
  [ ] Comparator: any off-label comparator or dose that requires a local exception? → high risk

  Risk count:  ___  (0–1 = acceptable; 2–3 = design review required; 4–5 = protocol redesign before IND)
```

For each high-risk item, estimate the amendment cost if the item is not resolved at design:
- Minor amendment: ~$50k–$100k + 6–8 weeks
- Substantial amendment (IRB/EC + HA): ~$141k–$535k + 3–4 months

Bring this estimate to the protocol sponsor review meeting so the "it's just a small protocol tweak" decision gets made with the real cost attached.

**Do:**
- Complete the amendment-risk checklist at protocol design, not at submission.
- Assign a named owner to each high-risk item with a resolution deadline before IND filing.
- Document amendment-risk findings in the feasibility report alongside enrollment projections.

**Don't:**
- Treat protocol design as purely scientific — every design choice has an operational cost.
- Assume IRB/EC turnaround for a substantial amendment is <60 days; plan 90+ days.
- Bundle multiple substantive changes into a single amendment to "save time" — reviewers often return bundled amendments for separation.

## Edge cases / when the rule does NOT apply

Early-phase (Phase I) first-in-human studies intentionally carry higher amendment risk because the dose/safety space is unknown; the risk checklist still applies to procedures and eligibility, but endpoint amendment risk is expected and budgeted differently. Rare-disease trials may also accept higher eligibility-restriction risk when the patient population is small and criteria cannot be loosened without changing the study question.

## See also

- [`../agents/protocol-design-specialist.md`](../agents/protocol-design-specialist.md) — owns feasibility and protocol operability review.
- [`../agents/trials-engagement-lead.md`](../agents/trials-engagement-lead.md) — brings amendment-risk findings to sponsor/steering committee decisions.
- [`./budget-by-phase-and-category-the-shape-differs.md`](./budget-by-phase-and-category-the-shape-differs.md) — amendment costs must be budgeted by phase; Phase III amendments are costlier than Phase II.

## Provenance

Amendment cost figures from Tufts Center for the Study of Drug Development (CSDD) Impact Reports on protocol amendments [unverified — training knowledge; cite primary source when using in a deliverable]. Amendment-risk framing as a design-phase metric is standard practice at major CROs.

---

_Last reviewed: 2026-06-05 by `claude`_

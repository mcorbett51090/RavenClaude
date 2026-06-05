# Challenge every PII field at schema design time — if you don't need it, don't collect it

**Status:** Absolute rule
**Domain:** Privacy / data minimization
**Applies to:** `data-governance-privacy`

---

## Why this exists

The cheapest PII to protect is the PII that was never collected. Every PII column added to a schema creates a compliance obligation: classify it, protect it, honor DSR requests for it, delete it when the retention period ends, and propagate its masking to every downstream table and mart that joins or copies it. A form field that collects date of birth "in case we need it for age verification" but has no current use case is not a feature — it is a liability. Data minimization at schema design time is the highest-leverage governance intervention because it eliminates obligations before they are incurred.

## How to apply

Before adding a PII field to a schema, answer these four questions:

```markdown
## Data minimization review — [field name]

1. **What specific, current use case requires this field?**
   [ ] There is a live use case: _______________
   [ ] We might need it in the future — REJECT (collect when needed)

2. **Can the use case be served with a less-sensitive data point?**
   e.g., age bracket instead of date of birth; country instead of postal code
   [ ] No less-sensitive alternative exists
   [ ] A less-sensitive alternative works — USE THAT INSTEAD

3. **What is the retention period for this field?**
   [ ] Defined: ___ months/years for purpose: _______________
   [ ] Not defined — DEFINE BEFORE APPROVING

4. **What is the lawful basis for collecting this field?**
   [ ] Consent / Contract / Legal obligation / Legitimate interest
   [ ] Not defined — DEFINE BEFORE APPROVING
```

All four questions must be answered YES before the field is added to the schema.

**Do:**
- Run this review during the data model design phase, not after the pipeline is live.
- Prefer aggregate or bucketed fields (age group 25-34) over precise values (date of birth) when the use case allows.
- Document the minimization decision (what was considered and rejected) in the schema's ADR.

**Don't:**
- Add a PII field "for future use" — YAGNI applies here with extra force because the collection itself creates a compliance obligation.
- Inherit PII fields from a source system without asking whether they are needed for this engagement's use cases.

## Edge cases / when the rule does NOT apply

- Legally mandated data retention (financial records, medical records) may require collecting fields the use case doesn't actively consume. Document the legal obligation as the basis.

## See also

- [`../agents/privacy-compliance-engineer.md`](../agents/privacy-compliance-engineer.md) — runs the minimization review as part of schema approval
- [`./privacy-by-design-and-default.md`](./privacy-by-design-and-default.md) — the parent privacy-by-design rule this implements

## Provenance

Codifies data-governance-privacy CLAUDE.md §2 house opinion #2 ("Minimize what you collect, restrict by default, and bake privacy into the data model — the cheapest PII to protect is the PII you didn't collect"). GDPR Article 5(1)(c) (data minimisation principle).

---

_Last reviewed: 2026-06-05 by `claude`_

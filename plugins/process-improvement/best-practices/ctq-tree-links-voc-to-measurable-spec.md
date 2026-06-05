# CTQ Tree Links VOC to a Measurable Spec

**Status:** Absolute rule
**Domain:** Process Improvement — Define phase
**Applies to:** `process-improvement`

---

## Why this exists

"Customers want it to be fast" is not a specification — it cannot be baselined, cannot be confirmed in a Gage R&R, and cannot be passed to `applied-statistics` for a hypothesis test. A Critical-to-Quality (CTQ) tree translates raw Voice-of-Customer (VOC) language into a measurable performance requirement with a spec limit. Without this translation, defects are defined by internal preference rather than customer need (house opinion #8), and the project has no objective definition of success.

## How to apply

The CTQ tree is a three-level drill-down:

```
VOC Need  →  Driver (quality dimension)  →  CTQ (measurable characteristic + spec limit)
```

**Example:**

```
"Invoices are always wrong"
  → Accuracy
    → Invoice line-item error rate ≤ 0.5%   ← CTQ
    → Credit-note cycle time ≤ 2 business days when an error is corrected  ← CTQ
```

**Steps:**
1. Collect raw VOC (interviews, complaints, CSAT verbatims, warranty returns).
2. Cluster into **Quality Drivers** — the themes a customer cares about (accuracy, speed, availability, ease-of-use).
3. For each Driver, write one or more **CTQs**: a measurable characteristic + spec direction (≤, ≥, nominal) + unit.
4. Verify the CTQ can be *measured* and *operationally defined* (a failing CTQ is one no one can agree how to measure).
5. Pass CTQs to the baseline measurement plan.

**Do:**
- Express CTQs in customer-facing terms, not system metrics ("invoice error rate" not "ERP rejection code count").
- Attach a spec limit — without it you cannot count a defect.
- Validate the CTQ with a real customer or proxy, not by internal committee alone.

**Don't:**
- Skip the tree and go directly from a vague complaint to a metric.
- Let the same VOC need generate more than 2–3 CTQs for a single project scope (prioritize the vital few).
- Treat an internal SLA as a customer CTQ without checking whether the customer actually cares.

## Edge cases / when the rule does NOT apply

- **Redesign (DMADV) projects** use CTQs *earlier*, to design to a target — the tree is even more important, not less.
- **Lean waste-removal projects** where the only metric is cycle time still need an operational definition of the start/stop point (the tree degenerates to one node, but the spec limit is still required).

## See also

- [`../agents/process-analyst.md`](../agents/process-analyst.md) — the agent that runs the VOC collection and CTQ translation
- [`./voice-of-the-customer-defines-the-defect.md`](./voice-of-the-customer-defines-the-defect.md) — companion rule on defect definition

## Provenance

Codifies house opinion #8 ("Voice of the Customer defines the defect") from `CLAUDE.md` §3. CTQ-tree methodology is standard ASQ/DMAIC Define-phase practice (ASQ Quality Glossary; iSixSigma CTQ Guide). _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_

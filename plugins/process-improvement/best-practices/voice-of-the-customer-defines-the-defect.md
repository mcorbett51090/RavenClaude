# Voice of the Customer defines the defect

**Status:** Absolute rule
**Domain:** Process improvement — Define phase
**Applies to:** `process-improvement`

---

## Why this exists

A "defect" counted without a Customer-grounded definition is an arbitrary internal number. Teams routinely measure what is easy to count (keystrokes, complaints logged by the first agent, emails missed) rather than what the Customer actually requires. When the measurement does not match a stated Customer CTQ (Critical-to-Quality), two things break: the baseline is wrong (you are measuring something the customer does not care about), and the Improve-phase solution optimizes a metric that does not move customer satisfaction. The DMAIC project then closes with a "green" result that the customer never felt.

## How to apply

Before collecting a single data point, answer these three questions in writing:

1. **Who is the customer?** (internal next-step, external buyer, regulator — be specific)
2. **What do they require?** (stated as a measurable output, e.g., "invoice arrives within 3 business days of delivery")
3. **What is the operational definition of a defect?** (a unit that fails the CTQ — start event, stop event, pass/fail rule, and who records it)

Only then define your DPMO numerator and denominator.

```
CTQ statement example:
  Customer: Accounts-payable team at each client site
  CTQ:      Invoice received and actionable within 3 business days of shipment
  Defect:   An invoice that reaches AP more than 3 business days after shipment scan
             — as recorded by the EDI timestamp in the billing system (not by email date)
  Unit:     Each invoice issued in the period
```

**Do:**
- Conduct Voice of the Customer (VoC) interviews or survey data to establish the spec limit (LSL, USL, or directional CTQ) before baselining.
- Express the CTQ in the *customer's* language, then translate it to a measurable data field you actually have (or will instrument).
- State the 1.5σ-shift convention and the short-term/long-term distinction any time you report a sigma level to avoid misinterpretation.

**Don't:**
- Let the process owner define the defect unilaterally — they will optimize what is internally convenient.
- Redefine the defect mid-project to make the baseline look better.
- Use a proxy metric (e.g., "call volume") as a CTQ unless there is documented evidence the customer cares about it directly.

## Edge cases / when the rule does NOT apply

- **Pure internal efficiency projects with no external customer** (e.g., reducing server provisioning time for an internal DevOps team): the "customer" is the internal consuming team; the CTQ still applies — just scope it to their stated requirement, not to what the improvement team finds convenient.
- **Exploratory / pre-DMAIC scoping work** where VoC collection is literally the deliverable: the rule cannot be satisfied until that VoC work completes. Flag this explicitly in the project charter so the Measure phase cannot start without it.

## See also

- [`../agents/lean-six-sigma-blackbelt.md`](../agents/lean-six-sigma-blackbelt.md) — owns the Define phase and the CTQ tree; routes VoC collection as a Measure-phase gate requirement
- [`./operational-definition-of-the-metric.md`](./operational-definition-of-the-metric.md) — companion rule: once the CTQ is defined, the metric that measures it needs an operational definition

## Provenance

Codifies house opinion #8 in [`../CLAUDE.md`](../CLAUDE.md) ("Voice of the Customer defines the defect"). Standard Lean Six Sigma Define-phase discipline: DMAIC toolset, ASQ Body of Knowledge, *The Six Sigma Handbook* (Pyzdek & Keller). The operationalization (CTQ tree → defect → DPMO denominator) is the backbone of the `dmaic-project-charter` skill's Define-phase output.

---

_Last reviewed: 2026-06-05 by `claude`_

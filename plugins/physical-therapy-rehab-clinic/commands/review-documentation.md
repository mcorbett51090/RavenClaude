---
description: "Review a PT/rehab daily note or plan of care for defensibility — medical necessity, skilled-care justification, POC-goal traceability, and certification timing — and flag boilerplate before it becomes a denial."
argument-hint: "[de-identified note or plan-of-care text to review]"
---

You are running `/physical-therapy-rehab-clinic:review-documentation`. Use `clinical-documentation-compliance`.

> Advisory only — not legal/clinical advice. Signature and certification rules are `[verify-at-use]`. Work from de-identified text; no patient PII.

## Steps
1. Check the note **states why skilled therapy was needed today** (medical necessity).
2. Check it **reads as skilled** — clinical decision-making, progression, cueing — not "tolerated well" boilerplate.
3. Check it **traces to a plan-of-care goal** and records objective functional change.
4. For a plan of care, check **certification / recertification timing** and signature requirement.
5. Traverse the defensibility and certification-timing trees in [`../knowledge/pt-clinic-decision-trees.md`](../knowledge/pt-clinic-decision-trees.md).
6. Report findings by severity + fixes, name verify-at-use items, and emit the Structured Output block.

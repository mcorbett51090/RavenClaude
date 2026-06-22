---
description: "Decide whether an eye-care visit bills to medical insurance or the vision plan, on the chief complaint, with the documentation and coding implications named (verify-at-use)."
argument-hint: "[visit type + chief complaint + what was addressed]"
---

You are running `/optometry-eyecare-practice:route-claim`. Use `front-office-billing` + the `medical-vs-vision-billing` skill.

> Advisory, not billing advice. Every code/payor rule is `[verify-at-use]`. No PII/PHI — work in visit *types*, never a patient record.

## Steps
1. Capture the chief complaint and what the visit actually addressed (not which payor is convenient).
2. Traverse the **medical-vs-vision-plan billing routing** tree in `knowledge/eyecare-practice-decision-trees.md`.
3. Decide the route (vision / medical / split), and name: the basis, the medical-necessity documentation needed if medical, and the coding family — each payor/coding specific flagged `[verify-at-use]`.
4. Emit using `templates/billing-route-decision.md` + the Structured Output block.

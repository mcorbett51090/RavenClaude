# Failure Mode and Effects Analysis (FMEA) — {{Process / System Name}}

> Use an FMEA when the risk of failure is high enough to warrant pre-emptive prioritization before solution design. Most appropriate for: safety-adjacent processes, high-compliance processes (billing, payroll, regulatory submissions), complex multi-step processes with many failure opportunities, and any process where a failure's first detection is by the customer.
>
> **Process / system:** {{name}}
> **FMEA scope:** {{start step → end step, matching the charter SIPOC}}
> **Date:** {{YYYY-MM-DD}}
> **Author:** {{...}}
> **Reviewed by:** {{...}}

---

## RPN scoring guide

> RPN (Risk Priority Number) = Severity × Occurrence × Detection. Higher RPN = higher risk priority.
> Maximum RPN = 1,000 (10 × 10 × 10). Typical action threshold: RPN ≥ 100 or Severity ≥ 8.

### Severity (S) — impact if the failure reaches the customer

| Score | Criterion |
|---|---|
| 1–2 | No customer impact; cosmetic or trivial |
| 3–4 | Minor inconvenience; customer may notice but does not complain |
| 5–6 | Moderate dissatisfaction; customer complains; partial function lost |
| 7–8 | High dissatisfaction; significant function lost; regulatory risk |
| 9 | Critical failure; safety, legal, or financial loss to customer |
| 10 | Catastrophic; failure without warning; severe regulatory / legal consequence |

### Occurrence (O) — likelihood the failure mode occurs

| Score | Criterion | Approximate frequency |
|---|---|---|
| 1–2 | Remote — failure is unlikely | < 1 in 1,000 |
| 3–4 | Low — isolated occurrences | 1 in 100 to 1 in 1,000 |
| 5–6 | Moderate — occasional occurrences | 1 in 10 to 1 in 100 |
| 7–8 | High — repeated occurrences | 1 in 2 to 1 in 10 |
| 9–10 | Very high — failure is almost certain | > 1 in 2 |

### Detection (D) — ability of current controls to catch the failure before it reaches the customer

| Score | Criterion |
|---|---|
| 1–2 | Almost certain to detect — automatic check; SPC in place; defect cannot pass |
| 3–4 | High likelihood of detection — systematic review catches most cases |
| 5–6 | Moderate detection — manual review; some escapes expected |
| 7–8 | Low detection — visual inspection or ad-hoc; likely to escape |
| 9–10 | Almost no detection — no current control; defect reaches customer undetected |

> **Lower Detection score = better detection.** Detection = 1 means you almost always catch it. Detection = 10 means it almost always escapes.

---

## FMEA table

> Fill one row per failure mode. A single process step may have multiple failure modes. A failure mode is a specific way the step can fail — not the step itself.

| # | Process step | Failure mode | Effect of failure | Cause of failure | S | O | D | RPN | Current controls | Recommended action | Target date | Owner | New S | New O | New D | New RPN |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | {{Step name}} | {{How this step can fail — specific}} | {{What the customer or downstream process experiences}} | {{Why this failure mode occurs — mechanism}} | {{1–10}} | {{1–10}} | {{1–10}} | {{S×O×D}} | {{Existing controls, if any}} | {{Poka-yoke / SPC / standard work / training}} | {{YYYY-MM-DD}} | {{Name}} | {{}} | {{}} | {{}} | {{}} |
| 2 | {{...}} | {{...}} | {{...}} | {{...}} | | | | | | | | | | | | |
| 3 | {{...}} | {{...}} | {{...}} | {{...}} | | | | | | | | | | | | |
| 4 | {{...}} | {{...}} | {{...}} | {{...}} | | | | | | | | | | | | |
| 5 | {{...}} | {{...}} | {{...}} | {{...}} | | | | | | | | | | | | |

---

## Priority actions — RPN ≥ 100 or Severity ≥ 8

> List every row where RPN ≥ 100 OR Severity ≥ 8 here for Improve-phase action. Severity ≥ 8 is actioned regardless of RPN because the failure impact is severe even if rare.

| # | Failure mode | RPN | Priority trigger | Recommended action | Owner | Target date |
|---|---|---|---|---|---|---|
| {{ref}} | {{...}} | {{...}} | RPN ≥ 100 / S ≥ 8 | {{...}} | {{...}} | {{...}} |
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

---

## Action categories (how to reduce each component of RPN)

| To reduce... | Approach |
|---|---|
| **Severity** | Change the design so the failure has less impact; add containment so the failure doesn't propagate |
| **Occurrence** | Eliminate the root cause (poka-yoke — prevention); add error-proofing so the defect cannot be produced |
| **Detection** | Add or improve a detection control at or before the step (immediate detection > downstream detection > audit) |

> Reducing Detection is the easiest but weakest lever — it catches defects after they occur. Reducing Occurrence (preventing the defect) is always preferred.

---

## FMEA maintenance

- **Trigger a FMEA update when:** a new failure mode is observed; the process is changed; a recommended action is implemented; the FMEA is > 12 months old
- **Owner of this FMEA:** {{named person — usually the Process Owner}}
- **Next scheduled review:** {{YYYY-MM-DD}}

---

*Produced by the `process-improvement/skills/root-cause-analysis` skill (when high-severity failure modes are present) or the `process-improvement/skills/control-plan-and-sustain` skill (for poka-yoke design). High-RPN rows feed the control-plan action column in `control-plan.md`.*

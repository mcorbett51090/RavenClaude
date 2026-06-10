# CAPA Report

> Output of `quality-and-capa-lead` / the `capa-and-spc` skill. A CAPA with containment but no root cause,
> no preventive action, or no effectiveness check is not closed — it's scheduled to recur. Regulated/safety-critical
> dispositions are drafted here and escalated to the accountable human, never auto-closed.

## 1. Nonconformance (NCR)

- **Defect / what:** <description>
- **Where / when found:** <process step, date, by what control>
- **Affected product / quantity:** <lots, serials, quantity>
- **SPC/inspection data:** <chart, special vs common cause call, Cpk + stability basis>

## 2. Containment (stop the bleeding)

| Action | Scope | Done? |
|---|---|---|
| <quarantine / sort / hold> | <affected lots> | |

_Containment is not the fix — it buys time for the CAPA._

## 3. Root-cause analysis

- **Method:** <5-Whys / fishbone (Ishikawa) / is–is-not>
- **Root cause (not symptom):** <the actual cause>

## 4. Corrective + preventive action

| Type | Action | Owner | Due |
|---|---|---|---|
| Corrective (fix this batch) | | | |
| Preventive (remove the cause) | | | |

## 5. Effectiveness check

- **How verified:** <metric, sample, window>
- **Result:** <held / recurred — reopen if recurred>

## 6. Control-plan / FMEA update

| Characteristic | New/changed control | Prevention or detection? |
|---|---|---|
| <char> | <SPC / poka-yoke / inspection> | <prevention > detection > scrap> |

## 7. Handoff & sign-off

| What | Routed to |
|---|---|
| Gage R&R / MSA / capability-study math | `applied-statistics` |
| Designing the failure mode out (kaizen / poka-yoke) | `process-improvement` |
| Supplier selection / contract behind a supplier defect | `procurement-sourcing` |
| **Regulated/safety-critical closure or recall call** | **escalate to the accountable human — do NOT auto-close** |

---

```
Status: ...
Files changed: ...
Constraint respected: ...
Assumptions stated: ...
Handoff to method teams: ...
Open questions: ...
Grounding checks performed: ...
```

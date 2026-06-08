# RFI — Request for Information

> Output of `project-engineer` / the `rfi-and-submittal-workflow` skill. One answerable question, referenced,
> with a proposed resolution, the impact flagged, a needed-by date, and the log fields filled.

## Header

| Field | Value |
|---|---|
| RFI No. | <project-NNN> |
| Project | <name / number> |
| To | <architect / engineer of record> |
| From | <GC / project engineer> |
| Date sent | <YYYY-MM-DD> |
| **Needed by** | <YYYY-MM-DD — back-calculated from the activity it gates> |
| **Ball-in-court** | <who owes the answer> |
| Spec / drawing references | <sheet(s) + spec section(s)> |

## 1. The question (exactly one)

<One specific, answerable question. If you have several, split into separate RFIs.>

## 2. The condition / conflict

<Describe the field condition or documents conflict, with the drawing/sheet and spec references. State whether design intent is ambiguous.>

## 3. Proposed resolution

<The GC's recommended answer — what you'd do absent direction.>

## 4. Impact (flag it)

| Impact | Yes/No | Detail |
|---|---|---|
| Cost impact (potential change) | <Y/N> | <if Y, route to cost-and-change-controls-lead to price as a PCO> |
| Schedule impact | <Y/N> | <activity affected; critical path?> |
| Holds work / hold point | <Y/N> | <what is blocked until answered> |

## 5. Log (close-out fields)

| Field | Value |
|---|---|
| Date returned | <YYYY-MM-DD> |
| Response / disposition | <answer> |
| Is the answer scope-bearing? | <Y/N → if Y, hand to cost-and-change-controls-lead before building> |
| Closed | <Y/N> |

---

```
Status: ...
Files changed: ...
Field/cost/schedule impact: ...
Ball-in-court: ...
Handoff: ...
Open questions: ...
Grounding checks performed: ...
```

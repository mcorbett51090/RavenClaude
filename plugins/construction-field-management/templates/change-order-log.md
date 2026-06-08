# Change Order Log

> Output of `cost-and-change-controls-lead` / the `change-order-and-pay-application` skill. Track every change from
> proposed (PCO/COR) through priced + time-impacted to executed (CO). Nothing scope-bearing gets built unpriced.

## Project

| Field | Value |
|---|---|
| Project | <name / number> |
| Contract form | <AIA / EJCDC / ConsensusDocs — `[verify-at-build]`> |
| Original contract sum | <$> |
| Approved COs to date | <$> |
| Revised contract sum | <$> |

## Change register

| No. | Description | Trigger (RFI / field event / directive) | Cost | Time impact (days) | Status (PCO → COR → CCD → CO) | Ball-in-court | Date | Schedule routed? |
|---|---|---|---|---|---|---|---|---|
| PCO-001 | <added scope> | <RFI-NNN / condition> | <$> | <+N / TBD> | <PCO> | <owner who owes the next action> | <YYYY-MM-DD> | <project-management Y/N> |
| | | | | | | | | |

_Each row: a change with no time-impact analysis is half-priced — assess days and route the schedule effect to `project-management`. A change built on a verbal with no written CO/directive is a claim risk._

## Per-change detail (repeat per change)

- **Number / title:** <PCO-NNN>
- **Trigger:** <the RFI answer / field condition / owner directive — route to `project-engineer` for the source>
- **Scope of the change:** <what's added/changed vs. contract documents>
- **Cost:** <breakdown; subcontractor pricing routed to `skilled-trades-contracting`>
- **Time impact:** <days; critical path? — routed to `project-management`>
- **Authorization:** <signed CO / CCD / written directive — date>
- **Built before priced?** <must be No>
- **Reflected in:** <SOV line / budget cost code / pay app>

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

# Service-Recovery Playbook + Comment-to-Action

> Output of `guest-experience-analyst` / the `guest-experience-and-reputation` skill. A playbook with no
> comp authority, no follow-up step, or a comment-to-action list that never reaches operations is not ready.

## 1. Reputation baseline

- **Review score / NPS / GSS now:** <value + trend>
- **Sources coded:** <TripAdvisor / Google / Booking.com / survey verbatims>

## 2. Comment-to-action list (ranked)

| Theme | Frequency | Score / repeat-rate impact | Operational root cause | Fix → owner | Re-measure by |
|---|---|---|---|---|---|
| <e.g. "room not ready"> | | | <room-status handoff> | <SOP fix → `hotel-operations-lead`> | <next cycle> |
| | | | | | |

_Rank by frequency × impact — a rare high-impact defect can outrank a frequent minor one. One-offs: respond + recover, don't change the SOP._

## 3. Service-recovery flow

| Step | What happens | Owner |
|---|---|---|
| Acknowledge | <recognize the failure, no defensiveness> | front line |
| Own | <take responsibility, no blame-shifting> | front line |
| Fix | <resolve in-stay where possible> | front line / ops |
| Follow-up | <post-resolution contact — converts to loyalty> | <who> |

## 4. Comp-authority tiers

| Severity | Example | Comp authority | Approver |
|---|---|---|---|
| Minor | <slow service> | <amenity / points> | front line |
| Moderate | <room defect, moved> | <partial night / upgrade> | supervisor |
| Severe | <walked / safety> | <full comp + future stay> | manager |

## 5. Loyalty / repeat measurement

| Metric | How collected | Vanity risk flagged |
|---|---|---|
| Repeat rate | | |
| Direct-booking share | | |
| CLV lift | | |
| Recovered-guest repeat rate | | |

_Never measure loyalty by enrolled-member count. Pair the repeat-value case with `revenue-manager`._

## 6. Handoffs

| What | Routed to |
|---|---|
| The operational root-cause fix (SOP / maintenance / staffing) | `hotel-operations-lead` |
| The revenue value of repeat / direct lift | `revenue-manager` |
| The reputation / loyalty dashboard + verbatim pipeline | `data-platform` |
| A satisfaction-driver significance test | `applied-statistics` |

---

```
Status: ...
Files changed: ...
KPI impact: ...
Guest impact: ...
Handoff to neighbours: ...
Open questions: ...
Grounding checks performed: ...
```

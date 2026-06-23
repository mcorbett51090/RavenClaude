# Incident Record — <id / short title>

> Output of the `incident-and-problem-manager`. An incident restores service; if it recurs, open a problem too (§2 #1).

## Headline
<service affected + current status, in one line>

## Classification
- **Type:** incident / major incident
- **Priority:** <impact × urgency>
- **Service(s) affected:** <from the CMDB where available>

## Timeline
| Time | Event | By |
|---|---|---|
| | detected | |
| | restored | |

## Restoration
- **Workaround / fix applied:** <what restored service>
- **Restored at:** <time>; **time-to-restore:** <duration>

## Follow-up
- [ ] Recurring or unknown cause? → open a PROBLEM record (RCA + known error)
- [ ] Permanent fix needs a change? → change-and-release-manager
- **Next actions:** <item — owner — date>

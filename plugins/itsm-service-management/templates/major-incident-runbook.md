# Major Incident Runbook — <id / title>

> Output of the `incident-and-problem-manager`. A major incident needs a commander and comms, not just engineers (§2 #5).

## Declaration
- **Criteria met:** <broad impact / critical service / high urgency>
- **Severity:** <Sev1/Sev2> · **Declared at:** <time>

## Roles (assign immediately, keep distinct)
| Role | Person | Owns |
|---|---|---|
| Incident Commander | | coordination + decisions |
| Communications Lead | | stakeholder + customer updates |
| Technical Lead(s) | | the fix |
| Scribe | | the timeline |

## Communications cadence
- **Audience + channel + frequency:** <e.g. stakeholders, every 30 min, status page> — update even with 'nothing new'.

## Timeline (kept live)
| Time | Event | By |
|---|---|---|

## Restoration & review
- **Restored at:** <time>
- [ ] Open a PROBLEM record for the cause (RCA + known error)
- [ ] Schedule the blameless review; coordinate the engineering postmortem with `observability-sre`
- **Action items:** <item — owner — date>

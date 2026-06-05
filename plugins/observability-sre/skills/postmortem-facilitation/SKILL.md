---
name: postmortem-facilitation
description: "Blameless postmortem facilitation guide — timeline reconstruction, five-whys causal analysis, contributing factor classification, and action item extraction with owners and due dates."
---

# Postmortem Facilitation

## When to Use This

An incident has been resolved. Use this skill within 48–72 hours while participants' memories are fresh, to produce a blameless postmortem that extracts durable system improvements rather than assigning fault.

## Pre-Meeting: Gather Evidence

Before the session, collect:
- Incident timeline from monitoring/alerting tools (exact timestamps, not approximations).
- Alert fire times and page acknowledgement times.
- All relevant dashboard snapshots and log excerpts (link, don't paste wall-of-text).
- Deployment/change log for 48 hours before the incident.
- Customer/status-page communications sent.

Circulate these to participants before the meeting so the session time goes to analysis, not reconstruction.

## Postmortem Meeting Structure (60–90 min)

| Phase | Duration | Facilitator goal |
|---|---|---|
| Ground rules | 5 min | Establish blamelessness; "we're improving the system, not judging people" |
| Timeline walk | 20 min | Fill gaps; agree on the sequence of events |
| Impact statement | 5 min | Quantify: duration, % users/requests affected, SLO budget consumed |
| Contributing factors | 20 min | Five-whys per causal thread; classify factors |
| Action items | 20 min | One owner, one due date, per item |
| Close | 5 min | Confirm doc owner, publish timeline |

## Timeline Reconstruction

Use a table — never prose — for the incident timeline:

| UTC time | Event | Source |
|---|---|---|
| 14:02 | Deploy of v2.3.1 completed | CI log |
| 14:07 | Error rate climbs above 5% | Prometheus alert |
| 14:11 | Page fires; on-call acknowledges | PagerDuty |
| 14:23 | Root cause identified: missing DB index | On-call notes |
| 14:35 | Rollback complete; error rate returns to baseline | Dashboard |

## Contributing Factor Classification

After the five-whys, classify each factor:

| Class | Description | Example |
|---|---|---|
| **Triggering** | The immediate cause that started the degradation | New deploy removed index |
| **Contributing** | Made the impact worse or recovery slower | No staging environment with production data volume |
| **Latent** | Pre-existing condition that enabled the trigger | No automated index-existence check in CI |
| **Recovery** | Slowed or complicated mitigation | Rollback playbook was out of date |

This classification prevents action items that only treat the trigger while ignoring the latent conditions that will cause the next incident.

## Action Item Quality Bar

Each action item must have:
- **What:** specific, testable deliverable (not "improve monitoring")
- **Owner:** one name, not "team"
- **Due date:** a date, not "soon"
- **Type:** prevent recurrence / detect faster / recover faster / reduce impact

| Bad | Good |
|---|---|
| "Improve monitoring" | "Add a synthetic canary for checkout flow; fires within 60s of degradation. Owner: @alice. Due: 2026-06-19." |
| "Fix the deploy process" | "Add index-existence assertion to migration CI check. Owner: @bob. Due: 2026-06-12." |

## Five-Whys Template

```
Symptom: <what users experienced>

Why 1: <immediate technical cause>
Why 2: <why that happened>
Why 3: <why that happened>
Why 4: <why that happened>
Why 5: <systemic/organizational root>

Stop when the answer is "we made a deliberate trade-off" or "organizational constraint."
```

Stop at the level where an action item is tractable — "humans make mistakes" is never a root cause.

## Postmortem Document Sections

1. **Summary** — one paragraph; what happened, impact, duration, resolution.
2. **Timeline** — table as above.
3. **Impact** — quantified (users affected, requests failed, SLO budget consumed, revenue/support cost if known).
4. **Contributing factors** — classified table.
5. **What went well** — detection speed, escalation, communication. Reinforces good behaviors.
6. **What went poorly** — gaps the action items address.
7. **Action items** — table: what / owner / due / type.
8. **Lessons learned** — 2–3 sentences of system-level insight that didn't fit elsewhere.

## Pitfalls

- Waiting more than 72 hours — memories degrade; log retention windows close; the team moves on.
- Passive-voice writing ("a config was changed") — it obscures the causal chain without adding blamelessness. Blameless means no judgment, not no subject: "the auto-scaler config was changed by the deployment pipeline" is both accurate and blameless.
- Action items without owners or dates — they never close. Track them in a reliability backlog with a monthly review.
- Only addressing the triggering cause — if the latent conditions remain, the next deploy or traffic spike triggers the same incident.
- Publishing the postmortem but never reviewing action-item completion — the postmortem process loses credibility within one quarter.

## See Also

- [`../../agents/incident-commander.md`](../../agents/incident-commander.md) — incident response and postmortem ownership
- [`../../agents/sre-reliability-engineer.md`](../../agents/sre-reliability-engineer.md) — SLO budget consumed during incident

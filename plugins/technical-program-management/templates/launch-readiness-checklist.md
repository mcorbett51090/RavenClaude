# Launch-readiness checklist: <program / release name>

> Criteria are **measurable, owner-assigned, and agreed before the review**. A
> waiver is recorded with its risk acceptance. See the
> [`launch-readiness-review`](../skills/launch-readiness-review/SKILL.md) skill.

## Go/no-go criteria (agreed on <date>, before the review)

| # | Criterion (measurable) | Owner | GO / NO-GO / WAIVED | Evidence |
| - | ---------------------- | ----- | ------------------- | -------- |
| 1 | e.g. p99 < 300ms @ 2× load | SRE |              |          |
| 2 | Runbook + on-call rota in place | EM |          |          |
| 3 | Rollback tested in staging | DevOps |              |          |
| 4 | Support + comms briefed | CS lead |              |          |

## Decision

- **Decision:** GO / NO-GO / CONDITIONAL GO
- **Made by (name):** **\_\_** — **Date:** **\_\_**

## Waivers (if conditional GO)

| Criterion waived | Risk accepted | Accepted by (name) | Mitigation / re-check date |
| ---------------- | ------------- | ------------------ | -------------------------- |
|                  |               |                    |                            |

## Staged rollout

| Stage | Audience % | Gate metric + threshold | Advance owner |
| ----- | ---------- | ----------------------- | ------------- |
| Canary |           |                         |               |
| Ramp   |           |                         |               |
| Full   |           |                         |               |

## Rollback

- **Path:** <how>
- **Who can pull it:** <name>
- **Tested before go-live?** ☐ (an untested rollback is not a plan)

# Velocity Is a Description of What the Team Did, Not a Target

**Status:** Pattern
**Domain:** Project Management — Agile / metrics
**Applies to:** `project-management`

---

## Why this exists

Treating velocity as a performance target — telling a team to "increase velocity by 20% next sprint" — is the fastest way to destroy the metric's usefulness. Velocity is meaningful only when stories are sized consistently and honestly; pressure to increase it produces inflated estimates, partial-done stories counted as complete, and a number that grows while actual throughput doesn't. The correct use of velocity is forecasting: given a stable team and consistent sizing, velocity tells you how many sprints until the backlog is done. The correct management goal is removing impediments and stabilizing the team — not increasing the number.

## How to apply

**What velocity is for:**

| Use | Description |
|---|---|
| **Release forecasting** | `Remaining backlog points ÷ average velocity = sprints to done` |
| **Capacity confirmation** | Comparing this sprint's commitment to recent velocity before planning closes |
| **Trend analysis** | Identifying whether the team's throughput is stable, growing (learning), or declining (impediments/debt) |

**What velocity is not for:**

- Comparing teams (different sizing conventions, different backlogs)
- Performance reviews or individual contribution measurement
- Setting targets that the team is pressured to hit

**Healthy velocity management checklist:**
- [ ] Story sizing is reviewed for consistency at least once per quarter (do a relative-sizing calibration).
- [ ] Velocity is reported as a rolling 3–5 sprint average, not sprint-by-sprint.
- [ ] New team members, tech-debt sprints, and ops-heavy sprints are noted as context alongside the number.
- [ ] Impediment removal, not velocity targets, is the management lever when throughput is low.

**Do:**
- Publish the velocity trend with context (new team member joined; major incident consumed 20% of capacity).
- Use velocity to surface conversations about backlog sizing drift ("why did we deliver 40 points but complete only 6 stories?").
- Re-baseline velocity after a significant team composition change.

**Don't:**
- Set a velocity target in OKRs or performance plans.
- Inflate estimates to hit a velocity number.
- Compare velocity across teams without a shared sizing calibration session.

## Edge cases / when the rule does NOT apply

- **Kanban flow**: Kanban uses throughput (stories/week) and cycle time instead of velocity; the same "describe, don't target" principle applies to those metrics.
- **SAFe / PI Planning**: velocity feeds team-level capacity for PI objectives, which is appropriate *forecasting* use; still not a target.

## See also

- [`../agents/scrum-master.md`](../agents/scrum-master.md) — owns velocity reporting and capacity sizing
- [`./capacity-before-commitment-agile.md`](./capacity-before-commitment-agile.md) — uses velocity as input to sprint sizing, not as a goal

## Provenance

Codifies the anti-pattern "Sprint commitment that ignores capacity" and house opinion #6 from `CLAUDE.md` §3–4. Velocity-as-forecasting-not-target is established Agile coaching practice (Mike Cohn, "Agile Estimating and Planning"; Martin Fowler on velocity as a planning tool). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_

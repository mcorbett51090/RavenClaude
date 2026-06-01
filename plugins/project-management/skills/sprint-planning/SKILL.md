---
name: sprint-planning
description: Plan a sprint from a backlog — set a single sprint goal, size the commitment to demonstrated capacity (not aspiration), attach acceptance criteria + a single owner to every committed item, and make carry-over explicit. Reach for this when a team is starting a sprint, replanning mid-flight, or diagnosing erratic velocity. Used by `scrum-master` (primary).
---

# Skill: sprint-planning

**Purpose:** Run a sprint-planning session that produces a *committable* plan — a goal the increment serves, a commitment that fits real capacity, and items that are "done"-defined before work starts. Used by `scrum-master`.

## When to use

- Starting a new sprint / iteration.
- Mid-sprint replanning after a material change.
- Diagnosing erratic velocity ("we never finish what we commit").
- Onboarding a team to a cadence for the first time.

## The procedure

1. **Set the sprint goal first.** One sentence: the outcome this sprint delivers. A sprint is a goal, not a bucket of tickets — items earn their place by serving the goal.
2. **Establish capacity, not aspiration.** Start from demonstrated velocity (last 3 sprints' average) OR available person-days minus leave, ceremonies, and a support/interrupt buffer. Plan *to* that number.
3. **Pull items that serve the goal**, in priority order, until you reach capacity. Stop there. Everything else stays in the backlog — visibly, not silently dropped.
4. **Every committed item gets, before commitment:** a single named owner (never "the team"), **acceptance criteria** (the definition of done for *this* item), and an estimate. An item that can't be sized is too big — split it.
5. **Make carry-over explicit.** Unfinished items from the prior sprint are re-decided (re-commit / re-prioritize / drop), not auto-rolled.
6. **Name the risks + dependencies** that could block the goal, and who clears each (route depth to `risk-and-raid-analyst`).

## Scrum vs Kanban (a work-shape call)

- **Scrum** — cadenced deliverables + a planning rhythm → sprint goal + ceremonies + velocity.
- **Kanban** — continuous, interrupt-driven, variable-priority work (support/ops) → WIP limits + flow metrics, no sprint. Don't impose sprints on a queue.

## Anti-patterns this skill prevents

- A sprint backlog with no sprint goal.
- Committing beyond capacity every sprint (a planning defect, not a motivation problem).
- Items with no acceptance criteria, or owned by "the team."
- Mid-sprint scope injection absorbed silently (the #1 velocity-killer).
- Velocity weaponized as a cross-team productivity KPI (it's a planning aid).

## Output

A sprint plan (see [`../../templates/sprint-plan.md`](../../templates/sprint-plan.md)): goal, committed items (owner + acceptance + estimate), capacity basis, carry-over decisions, and named impediments. End with the `scrum-master` Output Contract block.

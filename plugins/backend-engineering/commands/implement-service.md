---
description: "Implement business logic cleanly: framework at the edges, explicit error modeling, boundary validation, idempotency, outbox."
argument-hint: "[logic + failure cases]"
---

You are running `/backend-engineering:implement-service`. Use `service-implementation-engineer` + the `backend-implementation` skill.

## Steps
1. Layer it (from `templates/service-layering.md`): logic in use-cases, framework at edges.
2. Model errors explicitly; validate inputs at the boundary.
3. Add idempotency for retried ops; outbox for write-then-publish (`templates/idempotency-and-outbox.md`).
4. Emit + Structured Output block.

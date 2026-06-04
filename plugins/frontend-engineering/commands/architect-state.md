---
description: "Architect frontend state and data: server-cache vs client state, scope, invalidation, optimistic updates."
argument-hint: "[data + interactions]"
---

You are running `/frontend-engineering:architect-state`. Use `frontend-state-and-data-engineer` + the `frontend-state-architecture` skill.

## Steps
1. Traverse the state-location tree; server data -> server-cache lib, never a global store.
2. Place client state at the narrowest scope; derive don't duplicate.
3. Define invalidation + optimistic updates with rollback.
4. Emit (from `templates/data-fetching.md`) + Structured Output block.

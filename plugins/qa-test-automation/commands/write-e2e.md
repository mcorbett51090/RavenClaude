---
description: "Write deterministic E2E tests for a critical journey with resilient selectors and condition-based waits."
argument-hint: "[journey + app/stack]"
---

You are running `/qa-test-automation:write-e2e`. Use `e2e-automation-engineer` + the `e2e-automation` skill.

## Steps
1. Confirm the journey is critical (else push to a lower level).
2. Use role/test-id selectors; request testability from frontend-engineering if missing.
3. Wait on conditions; isolate test data; structure with page objects.
4. Emit the tests (pattern in `templates/e2e-test-skeleton.md`) + Structured Output block.

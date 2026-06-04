---
description: "Design a pyramid-shaped test strategy: map defect classes to levels, prioritize by risk, set coverage-as-floor + mutation, and list what not to test."
argument-hint: "[app + where defects escape]"
---

You are running `/qa-test-automation:design-test-strategy`. Use `test-strategy-architect` + the `test-strategy-design` skill.

## Steps
1. Map defect classes to the cheapest catching level; traverse the test-level tree.
2. Identify the critical journeys for E2E (keep them few).
3. Set coverage as a floor + mutation on critical modules.
4. List what NOT to test.
5. Emit the strategy (from `templates/test-strategy.md`) + Structured Output block.

---
description: "Stand up characterization / golden-master tests to pin a legacy system's current behavior before a risky edit. Reach for this before touching untested legacy code."
argument-hint: "[the code / module about to change]"
---

# Characterize before change

You are running `/legacy-modernization:characterize-before-change` for `$ARGUMENTS`. Run it the way the `refactoring-engineer` would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §2.

## Steps (traverse top-to-bottom; do not skip)
1. Find the seam — a substitution point to drive the code and observe output; if none, ask `codebase-archaeologist`.
2. Capture current behavior — assert what it does today, bugs included (not desired behavior).
3. Use approval/golden-master — snapshot large or unspecified outputs and lock them.
4. Cover the change area — drive the branches you are about to touch.
5. Refactor against the net — every refactor green; any red is an unintended behavior change.

## Output
A characterization-test safety net around the change area. See [`../skills/characterization-testing/SKILL.md`](../skills/characterization-testing/SKILL.md).

## Guardrails
- Characterize before you change (§2 #1) — no edit to untested legacy code without a net.
- Refactoring and behavior change never share a commit (§2 #3).
- Broader test-suite strategy routes to `qa-test-automation`.

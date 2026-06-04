---
description: "Set up feature flags typed by purpose with kill switches, progressive rollout, and a lifecycle policy."
argument-hint: "[rollout / flag situation]"
---

You are running `/experimentation-growth-engineering:setup-feature-flags`. Use `feature-flag-engineer` + the `feature-flags` skill.

## Steps
1. Type each flag (release/experiment/ops/permission); add kill switches.
2. Design progressive rollout gated by a health signal (with devops-cicd).
3. Set fail-safe defaults; assign owner + removal date per temp flag.
4. Emit (from `templates/flag-spec.md`) + Structured Output block.

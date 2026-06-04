---
description: "Set up test infrastructure: isolated factory data, ephemeral environments, flake quarantine automation, and coverage+mutation reporting."
argument-hint: "[current test data/env + pain]"
---

You are running `/qa-test-automation:setup-test-infra`. Use `test-infrastructure-engineer` + the `test-infrastructure` skill.

## Steps
1. Replace shared fixtures with per-test factories (pattern in `templates/test-data-factory.md`).
2. Add ephemeral per-run environments (Testcontainers) so local==CI.
3. Automate flake detection + quarantine.
4. Wire coverage (floor) + mutation (critical) reporting; coordinate gating with devops-cicd.
5. Emit + Structured Output block.

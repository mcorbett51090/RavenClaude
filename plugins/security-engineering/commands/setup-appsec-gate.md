---
description: "Stand up tuned SAST/SCA/secret-scanning/DAST gates in CI with exploitability-based triage."
argument-hint: "[stack + CI + current scanning]"
---

You are running `/security-engineering:setup-appsec-gate`. Use `appsec-engineer` + the `appsec-scanning` skill.

## Steps
1. Place SAST+SCA on PR, DAST on a deployed build, secret-scanning on every commit.
2. Tune for signal; define triage by exploitability×blast-radius.
3. Add class-level fixes + lint rules for recurring patterns.
4. State that verdicts route to security-reviewer.
5. Emit the gate (from `templates/security-ci-gate.md`) + Structured Output block.

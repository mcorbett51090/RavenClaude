---
description: "Plan code-signing + notarization (Win + macOS) and a safe signed auto-update (channels, staged rollout, rollback, version floor)."
argument-hint: "[targets + current signing/update setup]"
---

You are running `/desktop-app-engineering:plan-release-signing`. Use `desktop-platform-engineer` + the `packaging-signing-and-updates` skill.

## Steps

1. Traverse the signing/update tree; set per-OS signing (macOS Dev ID + notarytool + staple; Windows Authenticode/EV).
2. Confirm keys live in CI secrets/HSM, not a laptop.
3. Design the signed auto-update: verify-signature-before-apply, channels, staged rollout %, rollback, version floor.
4. Fill `templates/release-signing-checklist.md`; route CI pipeline wiring to `devops-cicd`.
5. Emit the plan + a Structured Output block. Mark tool-name/OS specifics `[verify-at-use]`.

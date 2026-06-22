---
description: "Classify a change (standard/normal/emergency), assess risk, and build the RFC. Reach for this on any 'does this need a CAB/approval?' question."
argument-hint: "[the change]"
---

# Plan change

You are running `/itsm-service-management:plan-change` for `$ARGUMENTS`. Run it the way the `change-and-release-manager` would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §2.

## Steps (traverse top-to-bottom; do not skip)
1. Classify the type — standard (pre-authorized) / normal (assess + CAB) / emergency (expedited).
2. Assess risk — impact × likelihood × reversibility; set approval level to match.
3. Pre-authorize if repeatable — build a standard-change model so it skips the CAB.
4. Build the RFC — for a normal change (rollback + schedule + risk).
5. Coordinate the release — scope, timing, rollback; automation → devops-cicd.

## Output
The change type + an RFC or standard-change model. See [`../skills/run-change-enablement/SKILL.md`](../skills/run-change-enablement/SKILL.md), the change-type tree in [`../knowledge/itsm-decision-trees.md`](../knowledge/itsm-decision-trees.md), and the [`../templates/change-request-rfc.md`](../templates/change-request-rfc.md) template.

## Guardrails
- Change enablement balances speed and risk — not bureaucracy (§2 #2); standard changes skip the CAB (§2 #3).
- Deployment automation → `devops-cicd`; a failed change causing an outage → incident-and-problem-manager.
- End with next actions: owner + date.

---
description: "Define an SLA backed by the OLAs and underpinning contracts that make it deliverable. Reach for this when setting service targets."
argument-hint: "[the service]"
---

# Design SLA

You are running `/itsm-service-management:design-sla` for `$ARGUMENTS`. Run it the way the `service-desk-and-request-manager` would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §2.

## Steps (traverse top-to-bottom; do not skip)
1. Define the service — consumers and what 'good' means to them.
2. Set the SLA targets — specific, measurable, deliverable.
3. Back them with OLAs + underpinning contracts — the internal + vendor commitments that must hold.
4. Surface any gap — an SLA target with no backing commitment is a future breach.
5. Shift left — add the self-service that deflects the request volume behind the service.

## Output
An SLA backed by OLAs/UCs in the [`../templates/sla-ola-definition.md`](../templates/sla-ola-definition.md) shape. See [`../skills/design-slas-and-catalog/SKILL.md`](../skills/design-slas-and-catalog/SKILL.md).

## Guardrails
- Every SLA is backed by OLAs and underpinning contracts (§2 #4) — the chain must hold end-to-end.
- Cite a source + date for any benchmark or SLA-norm figure (or mark it).
- End with next actions: owner + date.

# Shift left: knowledge and self-service deflect tickets

**Status:** Pattern. **Constitution:** §2 #7.

## Use when
Any ITSM deliverable where this question is in play — read, applied, and cited whole.

## The rule
The cheapest ticket is the one a good knowledge article or self-service action prevented. Measure deflection, not just handle time.

## Why it matters
This is a house opinion distilled into a citable rule. IT teams and users live with these decisions daily; a service-management process that ignores this rule doesn't fail loudly — it erodes trust ticket by ticket, breach by breach. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a practice — it sets the framing, not the conclusion.
- Identify the top repetitive ticket types and design knowledge/self-service to deflect them.
- Instrument the deflection rate as a first-class metric, not just average handle time.
- Route repetitive service requests to standard-change models and the catalog.
- Cite a source + date for any benchmark, SLA target, or tool capability, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`service-management-lead`](../agents/service-management-lead.md) to sequence them.

## The anti-pattern this prevents
Optimizing handle time on a flood of repetitive password-reset / access tickets that good self-service would have prevented entirely. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #7 — the house opinion this rule encodes.
- [`../skills/design-slas-and-catalog/SKILL.md`](../skills/design-slas-and-catalog/SKILL.md) — the catalog + self-service method.

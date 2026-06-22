# Every service has an SLA backed by OLAs and underpinning contracts

**Status:** Absolute rule. **Constitution:** §2 #4.

## Use when
Any ITSM deliverable where this question is in play — read, applied, and cited whole.

## The rule
A customer-facing SLA you can't deliver because the internal/vendor commitments behind it don't exist is a promise you'll break. The chain has to hold end-to-end.

## Why it matters
This is a house opinion distilled into a citable rule. IT teams and users live with these decisions daily; a service-management process that ignores this rule doesn't fail loudly — it erodes trust ticket by ticket, breach by breach. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a practice — it sets the framing, not the conclusion.
- For each SLA target, name the OLAs (internal) and underpinning contracts (vendor) that must hold.
- Surface any gap between the SLA and its backing commitments as a future breach, now.
- Set SLA targets to the customer's need AND to what the backing chain can actually deliver.
- Cite a source + date for any benchmark, SLA target, or tool capability, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`service-management-lead`](../agents/service-management-lead.md) to sequence them.

## The anti-pattern this prevents
Publishing a 99.9% / 1-hour SLA with no OLA or vendor SLA behind it — a promise that breaches the first time the chain is tested. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #4 — the house opinion this rule encodes.
- [`../skills/design-slas-and-catalog/SKILL.md`](../skills/design-slas-and-catalog/SKILL.md) — the method that applies it.
- [`../templates/sla-ola-definition.md`](../templates/sla-ola-definition.md) — the template it produces.

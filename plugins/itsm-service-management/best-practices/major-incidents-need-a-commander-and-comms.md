# A major incident needs a commander and communications

**Status:** Absolute rule. **Constitution:** §2 #5.

## Use when
Any ITSM deliverable where this question is in play — read, applied, and cited whole.

## The rule
Someone owns coordination and stakeholder communications while the technical responders fix it. Silence during an outage is its own incident.

## Why it matters
This is a house opinion distilled into a citable rule. IT teams and users live with these decisions daily; a service-management process that ignores this rule doesn't fail loudly — it erodes trust ticket by ticket, breach by breach. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a practice — it sets the framing, not the conclusion.
- Declare a major incident by criteria, then assign a commander and a comms lead distinct from the technical responders.
- Run a status cadence to stakeholders even when there is 'nothing new' — silence reads as chaos.
- Keep a timeline during, not after, for the review.
- Cite a source + date for any benchmark, SLA target, or tool capability, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`service-management-lead`](../agents/service-management-lead.md) to sequence them.

## The anti-pattern this prevents
A major outage where everyone is heads-down fixing, nobody owns comms, and leadership/customers learn about it from social media. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #5 — the house opinion this rule encodes.
- [`../templates/major-incident-runbook.md`](../templates/major-incident-runbook.md) — the runbook it produces.

# Warm up gradually and protect sender reputation.

**Status:** Pattern. **Constitution:** §3 #7, §4.

## Use when
Any marketing operations deliverable involving a new sending IP/domain, a volume ramp, or a deliverability decline — read, applied, and cited whole.

## The rule
Reputation is built by consistent, *engaged* volume over time; ramp a new IP/domain gradually starting with the most-engaged segment, send permission-only, suppress hard bounces and complaints immediately, sunset inactive recipients, and monitor reputation (Postmaster, SNDS, DMARC RUA) as a leading signal — not the bounce report after the fact.

## Why it matters
This is house opinion §3 #7 applied to sender reputation. Practitioners act on these deliverables, so a framing error here is not academic — it sends real operating decisions the wrong way. A cold IP blasted at full volume gets throttled; a stale list raises complaint rate and decays reputation faster than any campaign can rebuild it.

## How to apply
- Apply this **before** scaling volume — it sets the framing, not the conclusion.
- Ramp from the most-engaged segment; raise the cap only while complaint/bounce rates stay low.
- Watch the **complaint rate** first — it is the earliest reputation warning.
- Mark every provider threshold `[unverified — training knowledge]` and verify against current, dated provider guidance (§3 #8).
- When this rule and another both apply, route to [`marketing-ops-lead`](../agents/marketing-ops-lead.md) to sequence them.
- Keep customer/lead PII out of the deliverable; route consent/privacy-law determinations to the qualified authority (§2).
- Close with a recommendation that has an owner, a date, and an expected metric movement.

## The anti-pattern this prevents
The §4 failure mode: scaling volume on a cold IP or a stale, unengaged list, then reading the bounce report as the first signal something is wrong. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §3 #7 — the house opinion this rule encodes.
- [`../knowledge/email-deliverability.md`](../knowledge/email-deliverability.md) — the dedicated-vs-shared-IP decision tree and warmup guidance.

# Authenticate SPF, DKIM, and DMARC (with alignment) before you send.

**Status:** Absolute rule. **Constitution:** §3 #7, §4.

## Use when
Any marketing operations deliverable involving outbound email or deliverability — read, applied, and cited whole.

## The rule
Publish SPF and DKIM, confirm both **align** with the visible `From:` domain, and stage DMARC `none → quarantine → reject` only as aggregate reports show every legitimate stream authenticates cleanly. A passing SPF/DKIM check that fails alignment does not satisfy DMARC — and unauthenticated bulk mail is filtered or rejected by major providers.

## Why it matters
This is house opinion §3 #7 (integrity precedes the work) applied to email. Practitioners act on these deliverables, so a framing error here is not academic — it sends real operating decisions the wrong way. Publishing `p=reject` before legitimate streams align silently blackholes real mail; skipping authentication caps inbox placement no campaign can recover.

## How to apply
- Apply this **before** scaling any send — it sets the framing, not the conclusion.
- Verify SPF + DKIM **alignment** with the `From:` domain, not just a pass.
- Stage DMARC policy; collect RUA reports at `p=none` before any enforcement.
- Mark every provider threshold `[unverified — training knowledge]` and verify against current, dated provider guidance (§3 #8).
- When this rule and another both apply, route to [`marketing-ops-lead`](../agents/marketing-ops-lead.md) to sequence them.
- Keep customer/lead PII out of the deliverable; route consent/privacy-law determinations to the qualified authority (§2).
- Close with a recommendation that has an owner, a date, and an expected metric movement.

## The anti-pattern this prevents
The §4 failure mode: scaling sends on an unauthenticated or unaligned domain, then blaming "spam filters" — the most common way an email program quietly caps its own inbox placement. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §3 #7 — the house opinion this rule encodes.
- [`../knowledge/email-deliverability.md`](../knowledge/email-deliverability.md) — the authentication decision tree that routes to it.

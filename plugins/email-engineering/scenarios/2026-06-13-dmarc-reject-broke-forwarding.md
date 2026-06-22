---
scenario_id: 2026-06-13-dmarc-reject-broke-forwarding
contributed_at: 2026-06-13
plugin: email-engineering
product: authentication
product_version: "n/a"
scope: likely-general
tags:
  [dmarc, p-reject, spf, forwarding, dkim-alignment, mailing-list]
confidence: medium
reviewed: false
---

## Problem

After publishing `p=reject`, a portion of legitimate mail started bouncing — specifically messages to recipients who **auto-forward** their mail (e.g. a university alias forwarding to Gmail) and messages sent to an internal **mailing list** that re-sent to members. The team had verified "SPF passes" before flipping to reject.

## Context

- Sending domain `example.com`, single ESP, ~`[ESTIMATE] 20k`/day.
- Auth was set up with SPF aligned (custom return-path) but DKIM signing was on the ESP's shared `d=` domain — i.e. **DKIM did not align** with `From:`.
- DMARC passed in normal direct delivery **because SPF aligned**; nobody noticed DKIM wasn't aligning.

## Attempts

1. Assumed it was a content/spam-filter issue — chased the message body. No change (wrong layer).
2. Read the DMARC **RUA aggregate reports** and saw the failing slice was all `spf=fail dkim=fail` — and every failing case was a **forwarded** message. SPF breaks on forwarding (the return-path changes to the forwarder), and with no aligned DKIM there was no second identifier to carry DMARC.

## Resolution

Configured the ESP to sign DKIM with a key whose `d=` is a subdomain of `example.com` so **DKIM aligns**. DKIM survives forwarding (the signature travels with the message), so forwarded mail now passes DMARC on the DKIM identifier even though SPF fails. Re-confirmed via RUA that the forwarded slice flipped to `dkim=pass`, then left `p=reject` in place.

**Lesson:** before `p=reject`, make **DKIM alignment** the durable identifier — SPF alone fails on forwarding and mailing lists. The `p=none` + RUA monitoring stage exists precisely to catch this before enforcement bites real mail.

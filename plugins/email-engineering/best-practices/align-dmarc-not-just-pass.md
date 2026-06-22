# Check DMARC alignment, not just SPF/DKIM pass

**Status:** Absolute rule
**Domain:** Domain authentication
**Applies to:** `email-engineering`

---

## Why this exists

The single most common authentication mistake is "we have SPF and DKIM, why does DMARC fail?" DMARC passes only when an authenticated identifier **aligns** with the visible `From:` domain — SPF alignment means the return-path domain matches `From:`; DKIM alignment means the `d=` domain matches `From:`. An ESP that signs with its own shared `d=` and uses its own return-path will **pass** SPF and DKIM yet **fail** DMARC, because neither aligns with your `From:`. Pass/fail is not the deliverable — alignment is.

## How to apply

- Configure a **custom return-path** (for SPF alignment) and a **custom DKIM `d=`** on a subdomain of your domain (for DKIM alignment) at the ESP.
- Verify in a real message's `Authentication-Results` and in DMARC RUA reports that an identifier shows aligned.
- Prefer **DKIM** alignment as the durable one — it survives forwarding; SPF does not.

**Do:** read the RUA reports to confirm each source aligns.
**Don't:** flip to `p=quarantine`/`reject` on the strength of "SPF passes" — an unaligned pass still fails DMARC and gets enforced against.

## Edge cases / when the rule does NOT apply

- Relaxed alignment (DMARC default) allows a subdomain to align with the org domain; strict (`aspf=s`/`adkim=s`) requires exact match — only use strict with a reason.

## See also

- [`../knowledge/email-authentication-decision-tree.md`](../knowledge/email-authentication-decision-tree.md) — the alignment table + forwarding note.
- [`../scenarios/2026-06-13-dmarc-reject-broke-forwarding.md`](../scenarios/2026-06-13-dmarc-reject-broke-forwarding.md).

## Provenance

RFC 7489 §3 (alignment); the forwarding scenario in this plugin's bank.

---

_Last reviewed: 2026-06-13 by `claude`_

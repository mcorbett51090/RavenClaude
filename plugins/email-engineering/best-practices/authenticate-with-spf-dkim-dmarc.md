# Authenticate every sending domain with SPF, DKIM, and DMARC

**Status:** Absolute rule
**Domain:** Domain authentication
**Applies to:** `email-engineering`

---

## Why this exists

Unauthenticated mail is the easiest thing for a mailbox provider to junk or drop, and it lets anyone spoof your domain. The three mechanisms are complementary: **SPF** (RFC 7208) authorizes which servers may send for the envelope domain; **DKIM** (RFC 6376) cryptographically signs the message so the `d=` domain is verified; **DMARC** (RFC 7489) ties them to the visible `From:` and tells receivers what to do on failure (and sends you reports). Since Feb 2024, Gmail/Yahoo **require** all three for bulk senders.

## How to apply

- Publish **SPF** as a single `v=spf1` TXT, ESP `include:`s, `~all`/`-all`, within the 10-lookup limit.
- Enable **DKIM** with a 2048-bit ESP-managed key (CNAME pattern allows rotation).
- Publish **DMARC** at `_dmarc.<domain>`, starting `p=none; rua=...`.

**Do:** authenticate before any meaningful volume; keep `rua` reporting on permanently.
**Don't:** rely on SPF alone (it breaks on forwarding); leave DKIM unsigned; skip DMARC ("we have SPF/DKIM" is not authenticated to a DMARC-checking receiver).

## Edge cases / when the rule does NOT apply

- A domain that **never** sends mail should still publish a **null** SPF (`v=spf1 -all`) and a restrictive DMARC to prevent spoofing.
- Third-party senders (CRM, support tool) each need their alignment handled — enumerate every source.

## See also

- [`../knowledge/email-authentication-decision-tree.md`](../knowledge/email-authentication-decision-tree.md) — Tree 1, the setup branch.
- [`align-dmarc-not-just-pass.md`](align-dmarc-not-just-pass.md) — the alignment companion.

## Provenance

RFC 7208 / 6376 / 7489; Gmail & Yahoo bulk-sender requirements (enforced 2026-06 guidance, `[verify-at-use]`).

---

_Last reviewed: 2026-06-13 by `claude`_

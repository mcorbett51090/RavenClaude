# Honor one-click unsubscribe and suppress bounces/complaints immediately

**Status:** Absolute rule
**Domain:** List hygiene / compliance
**Applies to:** `email-engineering`

---

## Why this exists

A spam complaint is the strongest negative reputation signal a mailbox provider records, and re-sending to a hard bounce is the fastest path to a blocklist. A frictionless **one-click unsubscribe** (RFC 8058) prevents complaints by giving an unhappy recipient an easier exit than "report spam" — and an unsubscribe is far less damaging than a complaint. For bulk senders to Gmail/Yahoo, one-click unsubscribe is a hard requirement, not a courtesy.

## How to apply

- For bulk mail, send both `List-Unsubscribe` and `List-Unsubscribe-Post: List-Unsubscribe=One-Click`; honor the opt-out fast (provider guidance: ~2 days).
- Suppress **hard bounces** and **complaints** immediately and globally; enforce a suppression check as a hard pre-send gate at the lowest layer (no caller can bypass).
- Reconcile your suppression list with the ESP's; scope unsubscribes per stream so a marketing opt-out doesn't kill transactional mail.

**Do:** make unsubscribe one click and instant; suppress on the first hard bounce/complaint.
**Don't:** require a login to unsubscribe; re-send to a complainer or hard bounce; let an unsubscribe leak across streams.

## Edge cases / when the rule does NOT apply

- **Transactional** mail (receipts, legally-required notices) is generally exempt from marketing unsubscribe — but still suppress hard bounces, and never send marketing under a transactional pretext.

## See also

- [`../skills/bounce-complaint-suppression/SKILL.md`](../skills/bounce-complaint-suppression/SKILL.md) — the suppression model.
- [`../knowledge/deliverability-fundamentals.md`](../knowledge/deliverability-fundamentals.md) — one-click unsubscribe; the two rates.

## Provenance

RFC 8058 (one-click unsubscribe); Gmail/Yahoo bulk-sender requirements (`[verify-at-use]`).

---

_Last reviewed: 2026-06-13 by `claude`_

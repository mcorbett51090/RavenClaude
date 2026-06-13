# Roll out DMARC from p=none to p=reject — never publish reject blind

**Status:** Absolute rule
**Domain:** Domain authentication
**Applies to:** `email-engineering`

---

## Why this exists

`p=reject` tells receivers to **bounce** any mail that fails DMARC. Publish it before you've confirmed every legitimate stream aligns and you silently drop real mail — receipts, password resets, invoices — with no warning. The aggregate-report (`rua`) feedback loop at `p=none` exists precisely to find unaligned sources before enforcement bites them. Enforcement without monitoring is gambling with production mail.

## How to apply

The staged ramp (see the rollout template):

1. `p=none; rua=mailto:...` — monitor ~2 weeks; confirm all legitimate sources align.
2. `p=quarantine; pct=25` → ramp `pct` to 100 — reversible, borderline mail to spam.
3. `p=reject` — only after reports show legitimate streams clean. Keep `rua` forever.

**Do:** gate each stage on report evidence; enumerate every sending source first.
**Don't:** copy a `p=reject` record off a blog and publish it on a live domain; forget `rua` (then you're enforcing with zero visibility — the hook flags this).

## Edge cases / when the rule does NOT apply

- A **parked / non-sending** domain can go straight to `p=reject` (nothing legitimate to break) — ideally with `v=spf1 -all` too.
- A brand-new domain with a single known source can move faster, but still verify alignment at `p=none` briefly.

## See also

- [`../templates/dmarc-rollout-plan.md`](../templates/dmarc-rollout-plan.md) — the staged plan.
- [`../scripts/email_auth_lint.py`](../scripts/email_auth_lint.py) — flags `p=reject` with no `rua`.

## Provenance

RFC 7489 §6.3 (policy); DMARC deployment guidance (M3AAWG-style staged rollout).

---

_Last reviewed: 2026-06-13 by `claude`_

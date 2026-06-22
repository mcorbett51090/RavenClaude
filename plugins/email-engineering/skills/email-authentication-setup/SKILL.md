---
name: email-authentication-setup
description: Stand up SPF, DKIM, and DMARC (and optionally BIMI) for a sending domain and reach enforcement safely. Traverse the authentication decision tree (authenticate -> align -> enforce), emit the exact DNS records, and stage a p=none -> quarantine -> reject rollout gated on aggregate-report evidence. Reach for this when the user says "set up SPF/DKIM/DMARC", "get to DMARC enforcement", or "pass Gmail's sender rules". Used by `email-deliverability-architect` (primary).
---

# Skill: email-authentication-setup

> **Invoked by:** `email-deliverability-architect` (primary).
>
> **When to invoke:** "set up email auth for <domain>"; "publish SPF/DKIM/DMARC"; "get us to p=reject"; "are we authenticated for Gmail/Yahoo?".
>
> **Output:** the exact DNS records to publish + an alignment check + a staged enforcement rollout + how to confirm each stage from aggregate reports.

## Procedure

1. **Authenticate (SPF + DKIM).**
   - **SPF** — publish one TXT record at the domain root listing the authorized senders, ending in `~all` (softfail) during setup, `-all` (hardfail) once verified. Keep it to **≤10 DNS lookups** (SPF's hard limit) — flatten or drop unused `include:`s if you're near it. SPF authenticates the **envelope/return-path** domain.
   - **DKIM** — have the ESP generate a key; publish the public key as a TXT (or CNAME, the ESP-managed pattern) at `<selector>._domainkey.<domain>`. DKIM signs the message so the **`d=` domain** is cryptographically verified. Prefer 2048-bit keys; plan rotation.
2. **Align (the step everyone skips).** DMARC passes only when an authenticated identifier **aligns** with the `From:` (header) domain:
   - SPF alignment: return-path domain matches `From:` domain.
   - DKIM alignment: `d=` domain matches `From:` domain.
   - DMARC passes if **either** aligns. Relaxed alignment (default) allows subdomains; strict requires an exact match. A "passing" SPF on a mismatched return-path domain still **fails DMARC** — check alignment, not just pass.
3. **Enforce (staged, evidence-gated).** Publish DMARC at `_dmarc.<domain>` and walk the policy up:
   - `p=none; rua=mailto:dmarc@<domain>` — **monitor only.** Collect aggregate (RUA) reports ~2 weeks; confirm every legitimate stream aligns.
   - `p=quarantine; pct=25` → ramp `pct` to 100 — borderline mail to spam, reversible.
   - `p=reject` — unauthenticated mail bounced. Only after the reports show legitimate streams clean.
   - Traverse [`../../knowledge/email-authentication-decision-tree.md`](../../knowledge/email-authentication-decision-tree.md) for the branch logic; never skip straight to `reject`.
4. **(Optional) BIMI** — once at `p=quarantine`/`reject`, publish a BIMI record pointing at an SVG logo; note that Gmail/Apple display generally requires a **VMC/CMC certificate** (paid, verify currency). Mark this volatile.
5. **Lint the records** before publishing with [`../../scripts/email_auth_lint.py`](../../scripts/email_auth_lint.py) — it flags SPF lookup-count and `+all`, a DMARC missing `rua` or jumping to `p=reject`, and a too-permissive policy.

## Worked example

> User: "Set up auth so we pass Gmail's bulk-sender rules, sending from `mail.example.com` via SendGrid."

```dns
; SPF (envelope domain authorizes SendGrid)
mail.example.com.            TXT  "v=spf1 include:sendgrid.net ~all"
; DKIM (SendGrid-managed CNAMEs — automated key rotation)
s1._domainkey.mail.example.com.  CNAME  s1.domainkey.uXXXX.wlYYY.sendgrid.net.
s2._domainkey.mail.example.com.  CNAME  s2.domainkey.uXXXX.wlYYY.sendgrid.net.
; DMARC — START at monitor, not reject
_dmarc.example.com.         TXT  "v=DMARC1; p=none; rua=mailto:dmarc@example.com; fo=1"
```

Then: collect RUA reports → confirm SendGrid traffic aligns on DKIM → `p=quarantine; pct=25` → ramp → `p=reject`. Gmail/Yahoo bulk-sender rules (5,000+/day) additionally require **one-click unsubscribe** and a **spam rate under the published threshold** — see [`../deliverability-audit/SKILL.md`](../deliverability-audit/SKILL.md). _(Thresholds are volatile — re-verify against the current Gmail/Yahoo postmaster guidance; map last reviewed 2026-06.)_

## Guardrails

- A passing SPF/DKIM with **no alignment** still fails DMARC — alignment is the deliverable, not pass/fail.
- Never publish `p=reject` without RUA evidence that legitimate mail aligns; it silently drops real email (forwarding and mailing lists break SPF especially — see the forwarding scenario).
- SPF over 10 lookups **permerrors** — count the lookups, flatten if needed.
- DMARC policy lives at the **organizational** domain (`_dmarc.example.com`) and covers subdomains unless overridden with `sp=`.

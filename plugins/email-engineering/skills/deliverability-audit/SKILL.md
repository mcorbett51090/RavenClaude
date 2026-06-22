---
name: deliverability-audit
description: Diagnose why mail is landing in spam (or pre-flight a domain before a big send) by traversing the deliverability triage tree — authentication, DMARC alignment, reputation/warm-up, list hygiene, content, and bulk-sender compliance — then return the specific failing layer, the fix, and how to confirm it from postmaster/RUA signals. Reach for this when the user says "why are we going to spam?", "audit our deliverability", or "are we Gmail/Yahoo compliant?". Used by `email-deliverability-architect` (primary).
---

# Skill: deliverability-audit

> **Invoked by:** `email-deliverability-architect` (primary).
>
> **When to invoke:** "we started landing in spam"; "audit our sending"; "are we compliant with the bulk-sender rules?"; before a large or first send.
>
> **Output:** the failing layer (or a clean bill), the fix, and the signal that confirms recovery.

## Procedure — traverse the triage tree top-to-bottom

Walk [`../../knowledge/email-authentication-decision-tree.md`](../../knowledge/email-authentication-decision-tree.md) (the diagnosis tree). The order matters — a lower layer is meaningless if a higher one fails:

1. **Authentication** — do SPF and DKIM **pass**? (Check a real message's `Authentication-Results` header or Google Postmaster Tools.) If not, fix auth first ([`../email-authentication-setup/SKILL.md`](../email-authentication-setup/SKILL.md)).
2. **Alignment** — does DMARC **pass** (an authenticated identifier aligns with `From:`)? A pass on auth but fail on alignment is the most common "but we have SPF!" trap.
3. **Reputation** — is the domain/IP **warmed**? Check Google Postmaster domain reputation **and Microsoft SNDS/JMRP** for the Outlook/Hotmail population — Microsoft reputation moves independently of Gmail's, so a Postmaster-only check is blind to it. A new domain or a volume spike reads as spam regardless of auth. Remedy: warm-up ramp, reduce volume, isolate the bad stream.
4. **List hygiene** — bounce rate and **spam-complaint rate**. Gmail's bulk-sender guidance targets a spam rate kept low (well under ~0.3%, verify current threshold). Remedy: suppress hard bounces + complainers, stop buying lists, confirm opt-in.
5. **Content / formatting** — broken HTML, a single giant image, spammy phrasing, link-domain mismatch, missing plain-text part, or >102KB (Gmail clips). Remedy: fix the message, add the text part.
6. **Bulk-sender compliance** (Gmail/Yahoo, 5,000+/day) — authenticated **and** one-click unsubscribe (RFC 8058 `List-Unsubscribe-Post` + `List-Unsubscribe`) **and** low spam rate. Each is a hard gate, not a nice-to-have.

## Pre-send compliance checklist (the verdict shape)

```
[ ] SPF passes and is within 10 lookups
[ ] DKIM passes (2048-bit, aligned d=)
[ ] DMARC passes (aligned) and policy is at least p=quarantine for bulk
[ ] One-click unsubscribe present (List-Unsubscribe + List-Unsubscribe-Post)  [bulk]
[ ] Spam-complaint rate under threshold (Postmaster Tools)                     [bulk]
[ ] Transactional and marketing on separate subdomains
[ ] Domain/IP warmed for the intended volume
[ ] Plain-text part present; HTML < 102KB; links match sending domain
```

## Worked example

> User: "We have SPF and DKIM but newsletters still go to spam."

Triage: auth passes (1) ✓ → **alignment (2)**: the newsletter ESP sends with a return-path on `esp-bounces.net` and an unaligned `d=`, so DMARC **fails** despite SPF/DKIM passing. Fix: configure the ESP to use a custom return-path/DKIM on a subdomain of `example.com` so an identifier aligns. Confirm: `Authentication-Results` shows `dmarc=pass`, and RUA reports show the newsletter source aligned. If alignment was already fine, drop to (3) reputation — check Postmaster, suspect a cold subdomain or a complaint spike.

## Guardrails

- Don't fix content (5) before auth/alignment (1-2) — you'll chase ghosts.
- "It works to my Gmail" is not evidence; read Postmaster Tools / RUA aggregate reports for the population.
- A sudden spam jump on a previously-good domain is usually **reputation** (complaints, a compromised form, or a list you didn't warm) — not a content change.

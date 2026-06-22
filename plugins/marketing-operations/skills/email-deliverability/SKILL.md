---
name: email-deliverability
description: "Get email to the inbox — authenticate (SPF/DKIM/DMARC alignment + policy), pick dedicated vs shared IP, warm up, and protect sender reputation. Reach for this on any deliverability or 'going to spam' question."
---

# Skill: Email deliverability

Inbox placement, not "sent" (knowledge/email-deliverability.md). Authenticate before you send, warm before you scale, read reputation as a leading signal.

## Step 1 — Authenticate
SPF + DKIM published AND **aligned** with the `From:` domain; DMARC staged `none → quarantine → reject`. Traverse the alignment/policy tree.

## Step 2 — Choose the sending IP
Dedicated vs shared on sustained volume + warmup commitment. Traverse the IP tree. Separate transactional from marketing streams.

## Step 3 — Warm up & keep clean
Gradual ramp on the most-engaged segment; permission-only list; suppress hard bounces, sunset inactives.

## Step 4 — Monitor reputation
Google Postmaster + Microsoft SNDS + DMARC RUA. Watch complaint rate first; handle bounces/complaints per the playbook.

## Output
A deliverability read: auth/alignment status, IP recommendation, warmup plan, and the reputation metrics to watch — each threshold marked `[unverified]` and verify-at-use against current provider rules (§3 #8). Consent/privacy routes to the qualified authority (§2).

## Reference
- [`../../knowledge/email-deliverability.md`](../../knowledge/email-deliverability.md) — full doc + both decision trees.

---
name: bounce-complaint-suppression
description: Close the email feedback loop — classify hard vs soft bounces and spam complaints, enforce a suppression check before every send, and reconcile the ESP's suppression list with your own so you never re-send to a bad address. Reach for this when the user says "we keep emailing bounced addresses", "handle complaints", or "build a suppression list". Used by `email-sending-engineer` (primary).
---

# Skill: bounce-complaint-suppression

> **Invoked by:** `email-sending-engineer` (primary). Pairs with `transactional-email-integration` (which delivers the events) and `deliverability-audit` (list hygiene as a deliverability layer).
>
> **When to invoke:** "we keep sending to addresses that bounce"; "handle the complaint feedback loop"; "build/maintain a suppression list".
>
> **Output:** a classification + suppression model and the pre-send enforcement that keeps the list clean.

## Procedure

1. **Classify the event correctly — the action depends on the type:**
   - **Hard bounce** (mailbox doesn't exist, domain invalid — 5xx permanent) → **suppress immediately and permanently.** Re-sending poisons reputation.
   - **Soft bounce** (mailbox full, server temporarily down — 4xx transient) → retry a bounded number of times over a window; suppress only after repeated failures.
   - **Spam complaint** (FBL — the recipient hit "report spam") → **suppress immediately**, and treat as a strong negative reputation signal. Never email a complainer again.
   - **Unsubscribe** (List-Unsubscribe / one-click) → suppress for the relevant stream, fast.
2. **Make suppression a hard pre-send gate.** Every send path checks the suppression list **before** dispatch — a suppressed address is dropped (and logged), never sent. This check is non-optional and lives at the lowest layer so no caller can bypass it.
3. **Reconcile two lists.** The ESP keeps its own suppression list (it may silently drop) **and** you keep yours. Sync them — pull the ESP's suppressions via API/webhook into your store so your "sent" analytics and the actual deliveries agree, and so a provider switch carries the list.
4. **Scope suppression by stream.** A marketing unsubscribe should not suppress a password-reset (transactional) email — model suppression per stream/subdomain, with a global hard-bounce/complaint suppression that overrides everything.
5. **Track the rates.** Bounce rate and complaint rate are the deliverability vitals ([`../deliverability-audit/SKILL.md`](../deliverability-audit/SKILL.md)). A spike means stop and investigate the source, not push harder.

## Worked example (the data model)

```
suppression(email, reason, stream, suppressed_at)
  reason ∈ { hard_bounce, complaint, unsubscribe, manual }
  stream ∈ { global, marketing, transactional, ... }   -- global overrides all

-- enforced before every send (lowest layer, no bypass):
is_suppressed(email, stream) =
  EXISTS row WHERE email matches AND (stream = 'global' OR stream = :stream)
```

A `hard_bounce` and `complaint` write `stream='global'` (suppress everywhere). An `unsubscribe` from the newsletter writes `stream='marketing'` — receipts still send.

## Guardrails

- **Never** re-send to a hard bounce or a complainer — it's the fastest way to tank a domain's reputation.
- A complaint is worse than a bounce: it's an active negative vote the mailbox provider records. Honor it instantly and globally.
- Don't let an unsubscribe from marketing silently kill transactional mail (or vice-versa) — scope it.
- Reconcile with the ESP's list; relying only on your own (or only on theirs) drifts and re-sends.

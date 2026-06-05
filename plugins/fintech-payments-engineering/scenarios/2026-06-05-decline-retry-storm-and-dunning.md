---
scenario_id: 2026-06-05-decline-retry-storm-and-dunning
contributed_at: 2026-06-05
plugin: fintech-payments-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [declines, hard-vs-soft, retries, backoff, dunning, network-flag]
confidence: high
reviewed: false
---

## Problem

A subscription product's renewal job retried *every* failed charge on a tight loop — fixed 1-hour intervals, up to 24 attempts a day, regardless of why the charge failed. Two things broke. First, charges that hard-declined (stolen/lost/closed/invalid card) were retried hundreds of times, and the card networks flagged the merchant's excessive-retry behavior; the acquirer warned about an elevated decline-to-attempt ratio that threatened the merchant account. Second, the blanket retry recovered *fewer* soft declines (insufficient funds) than a smart schedule would have, because hammering a card at 3am the same hour it failed rarely succeeds — the funds aren't there yet.

## Constraints context

- Every decline carries an issuer **reason code**, and the recoverable (soft) vs. non-recoverable (hard) distinction is in that code — but the team treated all declines as "try again later" `[verify-at-use — map your PSP's specific decline/reason codes to hard vs. soft; they are PSP- and network-specific]`.
- Card networks monitor retry behavior; retrying a hard decline is read as abuse and can flag or penalize the merchant account — the cost of a wrong retry is not just a wasted call.
- Soft declines (NSF, issuer timeout, velocity, do-not-honor) are often timing-related; recovery odds rise around paydays and the end of the month, not minutes after the failure.

## Attempts

- Tried: the fixed-interval blanket retry. Failed both ways — abused the network on hard declines and under-recovered soft ones.
- Tried: simply lowering the retry count for everything. Reduced the network-flag risk but also cut soft-decline recovery further — wrong lever; the count wasn't the problem, the **lack of branching on reason code** was.
- Tried (the move that worked): **classify every decline as hard or soft from the reason code up front**, then branch — **hard → stop immediately**, surface a clear "update your payment method" message; **soft → smart retry** on a schedule spaced to likely-recovery times (not within 24h, biased toward paydays / month boundaries) with a small cap, then escalate to dunning comms; and for SCA `authentication_required`, send a re-authentication link rather than a blind retry.

## Resolution

**Never blanket-retry. Branch on the decline category from the reason code, and retry only soft declines, on a schedule.**

1. **Build the reason-code → hard/soft map before you retry anything.** Guessing turns a recoverable failure into a network-flagged merchant account.
2. **Hard decline: stop.** Retrying abuses network signals. Ask for a new payment method with an actionable message — that recovers the conversion, the retry doesn't.
3. **Soft decline: smart retry.** Space retries to likely-recovery windows (paydays, end of month), small cap, exponential-ish backoff — not a tight fixed loop. Then hand to dunning comms.
4. **SCA `authentication_required` is its own branch** — the card is fine, the cardholder must re-authenticate; send a re-auth link, not a retry.
5. **Preserve access during the grace period** and reserve manual outreach for high-LTV (annual) customers before canceling. See the "Subscription renewal failure — which dunning path?" and "Retry or stop after a decline?" trees in `../knowledge/fintech-payments-engineering-decision-trees.md`.

**Action for the next engineer:** if an acquirer flags your retry behavior or dunning recovery is poor, the first check is whether the retry logic **branches on the reason code at all** — a single retry path for all declines is the tell. The fix is the hard/soft map plus a payday-aware soft-retry schedule, not just a smaller retry count.

Cross-reference: canonical guidance is `../best-practices/retry-soft-declines-not-hard.md`, `../best-practices/dunning-without-churning.md`, and `../best-practices/handle-3ds-sca-and-declines.md`; the decline + dunning trees in `../knowledge/fintech-payments-engineering-decision-trees.md`.

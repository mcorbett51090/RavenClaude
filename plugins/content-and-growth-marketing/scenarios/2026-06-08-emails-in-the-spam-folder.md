---
scenario_id: 2026-06-08-emails-in-the-spam-folder
contributed_at: 2026-06-08
plugin: content-and-growth-marketing
product: klaviyo
product_version: "unknown"
scope: likely-general
tags: [deliverability, segmentation, lifecycle, dmarc, vanity-metrics, list-hygiene]
confidence: high
reviewed: false
---

## Problem

An ecommerce brand's email program cratered: open rates fell off a cliff, revenue per send dropped, and customer-service tickets reported order confirmations landing in spam. The team had been sending a weekly promotional blast to the entire list of ~400k addresses — including years of unengaged subscribers — and treated list size as the headline KPI ("we have 400k subscribers!"). They had no welcome flow; new, high-intent subscribers waited up to a week for the next blast.

## Constraints context

- A major mailbox provider had recently tightened bulk-sender requirements (authentication + low spam-complaint thresholds).
- The domain had no DMARC policy and an incomplete DKIM setup — the blasts were partly unauthenticated.
- The brand feared that pruning the list would "lose subscribers" and shrink the vanity number leadership watched.

## Attempts

- Tried: rewriting subject lines and sending more often to lift opens. Failed — more mail to an unengaged list raised spam complaints and made placement worse; copy can't rescue an unauthenticated sender to a stale list.
- Tried: buying a deliverability "monitoring" tool without changing sending behavior. Failed — it diagnosed the problem (poor authentication, low engagement) but the team didn't act on it.
- Tried: fixing authentication (SPF/DKIM/DMARC), sunsetting unengaged subscribers behind a re-engagement flow then suppressing the non-responders, segmenting by engagement, and adding a triggered welcome flow for new subscribers. This worked.

## Resolution

Inbox placement recovered within weeks once the domain was authenticated and the list was pruned to engaged subscribers — the list shrank to ~180k but revenue per send and total email revenue *rose*, because mail actually reached inboxes and went to people who wanted it. The triggered welcome flow became the single highest-revenue automation. The team retired "list size" and "open rate" as headline KPIs in favor of inbox placement, engaged-list health, and revenue per recipient.

## Lesson

Deliverability is the foundation — an email in spam converts at zero, and no subject line fixes an unauthenticated sender blasting a stale list. Segment and trigger instead of batch-and-blast, sunset the unengaged before they tank your reputation, and measure engaged-list health and revenue per recipient, never list size or open rate.

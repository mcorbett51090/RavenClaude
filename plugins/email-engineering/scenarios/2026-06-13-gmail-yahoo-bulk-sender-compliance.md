---
scenario_id: 2026-06-13-gmail-yahoo-bulk-sender-compliance
contributed_at: 2026-06-13
plugin: email-engineering
product: deliverability
product_version: "n/a"
scope: likely-general
tags:
  [
    bulk-sender,
    gmail,
    yahoo,
    one-click-unsubscribe,
    spam-rate,
    list-unsubscribe,
  ]
confidence: medium
reviewed: false
---

## Problem

A newsletter sending `[ESTIMATE] ~30k`/day to a mostly-Gmail audience saw open rates collapse and a chunk of mail going to spam. The team was authenticated (SPF+DKIM+DMARC) and assumed that was sufficient.

## Context

- Bulk/marketing stream on `news.example.com`, separate from transactional. Good.
- DMARC at `p=quarantine`, aligned. Auth was **not** the problem.
- Unsubscribe was a link to a web page requiring login — no `List-Unsubscribe` header, no one-click.
- Google Postmaster Tools showed the **spam-complaint rate** drifting toward `[ESTIMATE] ~0.35%` — over Gmail's stated concern level.

## Attempts

1. Re-checked auth (already fine — wrong layer).
2. Read the bulk-sender requirements: for 5,000+/day to Gmail/Yahoo you need authentication **and** one-click unsubscribe (RFC 8058) **and** a spam rate kept well under ~0.3%. Two of three were failing.

## Resolution

- Added the `List-Unsubscribe` + `List-Unsubscribe-Post: List-Unsubscribe=One-Click` headers and a no-login unsubscribe endpoint honored within ~2 days.
- The easy one-click opt-out **replaced** "report spam" clicks, dropping the complaint rate back under threshold over the next few sends (a working unsubscribe prevents complaints, which are far more damaging than an unsubscribe).
- Re-confirmed recovery in Postmaster Tools; placement returned.

**Lesson:** authentication is necessary but **not sufficient** for bulk senders. One-click unsubscribe and a low complaint rate are independent hard gates. _(Thresholds/dates are volatile — re-verify against current Gmail/Yahoo postmaster guidance; this scenario reflects guidance as of 2026-06.)_

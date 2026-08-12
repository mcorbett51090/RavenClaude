# Know which tab your mail lands in — and send the right signals

**Rule:** Design each email class (transactional, marketing, notification) with the correct inbox category signals — and never send signals that place transactional mail in Promotions.

---

## Why this matters

Gmail, Outlook, and Apple Mail all categorize mail inside the inbox. Promotions/Other/Updates placement is not failure — it is the correct destination for bulk mail. The deliverability risk is misclassification: transactional mail (password resets, receipts, alerts) that lands in Promotions is often seen much later, hurting both the user experience and engagement metrics.

## The two-rule model

1. **Transactional mail → Primary signals.** Omit `Precedence: bulk`, `List-Unsubscribe`, and `List-Id` from genuine one-to-one functional messages. Use a personal-style `From:` where plausible. Keep HTML minimal.

2. **Marketing/newsletter mail → Promotions is fine.** Do not fight it. You are required to include `List-Unsubscribe` (Gmail/Yahoo 2024 rules — [verify current](../knowledge/email-authentication-decision-tree.md)), which is a strong Promotions signal. That is correct. The Promotions tab exists precisely for this mail class.

## What to check in an audit

- Run the transactional send path through a test inbox (e.g., a personal Gmail account) and check which tab it lands in.
- If it lands in Promotions or Updates: look for `Precedence: bulk`, `List-Unsubscribe`, ESP bulk headers, or promotional content patterns.
- If marketing mail is unexpectedly in Primary: confirm `List-Unsubscribe` is present (required) and that you are not sending bulk mail with personal-email headers.

## Source

[`knowledge/inbox-categorization.md`](../knowledge/inbox-categorization.md) — provider signals, Gmail tab breakdown, Outlook Focused Inbox, Apple Mail, and the decision tree.

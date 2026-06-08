# Nurture the not-yet-ready — don't spam them

**Status:** Pattern
**Domain:** Marketing automation / lifecycle email
**Applies to:** `marketing-operations-demand-gen`

---

## Why this exists

Most B2B contacts who opt in to marketing communication are not ready to buy now. Treating every
contact as an MQL-in-waiting — emailing daily, sending every product update, ignoring engagement
signals — is how organizations burn their database, land on spam lists, and destroy domain
reputation. The resulting deliverability damage affects even the contacts who were ready to buy.

Lifecycle email exists to deliver value to people who are not yet ready — to earn the right to
be heard when they become ready, not to generate activity metrics for a marketing dashboard.

## How to apply

- **Segment by lifecycle stage and intent signal, not by list size.** The right question is not
  "how many people can we email?" but "which contacts would benefit from this message today?"
- **Set a contact frequency cap.** Define the maximum number of marketing emails a contact
  receives per week (typically 1–2 [verify-at-use]) and enforce it in the MAP. Frequency caps
  are a system constraint, not a guideline.
- **Build suppression logic into every flow.** Active opportunities and current customers receive
  different communication — or none. Competitor domains, hard bounces, and unsubscribes are
  suppressed at the flow level, not as an afterthought.
- **Design for the non-buyer.** Early-stage nurture content is educational and useful, not a
  product pitch. A contact who reads three blog posts and attends a webinar is better prepared
  to evaluate your product than one who received five "demo request" emails and unsubscribed.
- **Respect unsubscribes immediately and honor them completely.** An unsubscribe from one flow
  is an unsubscribe from all marketing email unless the contact explicitly re-subscribes. MAP
  global unsubscribe flags must be enforced across all programs.

**Do:**

- Gate email cadence on engagement signals: a re-engagement flow for cold contacts is different
  from an active-nurture flow for engaged contacts.
- Write subject lines and content that a non-buyer would value, not just a buyer.
- Review bounce rates, unsubscribe rates, and spam complaint rates monthly. Rising rates are
  early warning signals, not acceptable noise.

**Don't:**

- Send the same email to the full opted-in database regardless of lifecycle stage or engagement.
- Treat a low unsubscribe rate as permission to increase frequency.
- Build nurture flows with no exit criteria — contacts enrolled forever.
- Send re-engagement campaigns to contacts who have not engaged in 12+ months without a
  permission-confirmation step.

## Edge cases / when the rule does NOT apply

Transactional and product-triggered emails (onboarding sequences, usage alerts, billing notices)
follow a different discipline — they are functional, not marketing, and frequency caps do not
apply. Segment them at the infrastructure level (transactional send domain vs marketing send
domain) to protect deliverability for both.

## See also

- [`./mql-is-a-handoff-contract-not-a-trophy.md`](./mql-is-a-handoff-contract-not-a-trophy.md)
- [`./lead-scores-decay-maintain-them.md`](./lead-scores-decay-maintain-them.md)
- [`../skills/lead-scoring-and-lifecycle/SKILL.md`](../skills/lead-scoring-and-lifecycle/SKILL.md)

## Provenance

Codifies the email marketing deliverability discipline from Return Path / Validity, Litmus, and
the Email Experience Council, combined with the B2B lifecycle nurture methodology from
SiriusDecisions / Forrester B2B Research: nurture programs are designed for the non-buyer, not
the immediate MQL.

---

_Last reviewed: 2026-06-08 by `claude`._

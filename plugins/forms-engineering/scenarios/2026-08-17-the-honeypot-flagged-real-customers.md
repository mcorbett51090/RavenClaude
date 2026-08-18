---
scenario_id: 2026-08-17-the-honeypot-flagged-real-customers
contributed_at: 2026-08-17
plugin: forms-engineering
product: form-hardening
product_version: "n/a"
scope: likely-general
tags: [honeypot, assistive-tech, autofill, silent-rejection, anti-abuse]
confidence: medium
reviewed: false
---

## Problem

A small services business added a honeypot field to its contact form after a spam wave. Spam stopped. Over the following weeks two customers phoned to say they had "submitted the form twice and never heard back", and a third complained on a public review site. Nobody could reproduce it: the form worked in every browser the team tried.

## Context

- One public contact form, a handful of genuine submissions a week. Volume too low for any pattern to be obvious in aggregate.
- The honeypot was hidden with an off-screen positioning class already used elsewhere in the stylesheet, and named `company` — an ordinary field name reused because it "looked plausible to a bot".
- Rejections returned the same success page as an accepted submission, by design: the point of a honeypot is not to tell the submitter.
- **No counter and no log line** on the rejection path. There was no number anywhere that would have moved.

## Attempts

- Tried: reproducing in three desktop browsers, with the developer's own profile. Outcome: nothing. The developer's browser had no autofill entry for `company` and the developer was not using a screen reader.
- Tried: reading the server logs for the reported timestamps. Outcome: the submissions were there, and had been rejected. That was the first evidence the filter was firing on real traffic — and it took a customer complaint to look.
- Tried: adding a counter to the rejection path and letting it run for a week `[ESTIMATE — illustrative]`. Outcome: rejections were a meaningful share of all submissions on a form receiving a handful a week. Some were bots. Some plainly were not.
- Tried (the move that worked): rebuilding the honeypot against the four properties — out of the accessibility tree via `display: none` plus `aria-hidden="true"`, out of the tab order via `tabindex="-1"`, `autocomplete="off"`, and a `name` with no autofill heuristic behind it. Kept the counter. Outcome: rejections fell to a small residue consistent with automated traffic, and the complaints stopped.

## Resolution

Two failures, one root cause. The off-screen positioning left the field **in the accessibility tree**, so a screen-reader user reached it, heard a plausible label, and filled it in. The name `company` was a **magnet for browser autofill**, so a returning customer's browser filled it silently. Both populations were human, both were rejected, and neither was told.

The property that made it expensive was not the markup — it was that the rejection path emitted **nothing**. A filter you cannot observe is a filter you cannot debug, and the first signal was a public review.

**Action for the next person hitting this pattern:** when submissions "disappear", check the anti-abuse rejection path before the delivery path, and check whether it is counted at all. Apply the four properties in [`../best-practices/a-honeypot-must-be-invisible-to-assistive-tech-and-to-autofill.md`](../best-practices/a-honeypot-must-be-invisible-to-assistive-tech-and-to-autofill.md), and add the counter in the same change — an unobservable filter will produce this scenario again.

**Sources for facts cited:** failure mechanism and the four properties are in [`../knowledge/form-anti-abuse.md`](../knowledge/form-anti-abuse.md) §2 (2026-08-17). Figures are illustrative `[ESTIMATE]`.

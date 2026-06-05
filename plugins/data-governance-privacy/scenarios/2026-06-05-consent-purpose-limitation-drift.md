---
scenario_id: 2026-06-05-consent-purpose-limitation-drift
contributed_at: 2026-06-05
plugin: data-governance-privacy
product: gdpr
product_version: "n/a"
scope: likely-general
tags: [consent, purpose-limitation, lawful-basis, ml-training, revocation]
confidence: medium
reviewed: false
---

## Problem

A product team wanted to train a recommendation model on customer behavioral data the company had collected over years. The data was real and plentiful — the question that stopped the project was: *under what lawful basis was this data collected, and does model training fall within it?* It didn't. Most of the behavioral data had been collected under **consent for "improving your experience"** or under a **contract-performance** basis for delivering the product — neither of which covers training a new ML model. Worse, some of the records belonged to users who had since **withdrawn consent** or **opted out of profiling**, and those withdrawals had never propagated to the analytics store the training set was drawn from. This is purpose-limitation drift: using data beyond the basis it was collected under is a violation, not a feature (CLAUDE.md §2 #3).

## Constraints context

- No single **consent/lawful-basis store of record**: consent state lived in the app database, opt-outs lived in the marketing tool, and the analytics warehouse (the training-set source) had a *stale snapshot* of neither. So "which users may we train on?" had no authoritative answer.
- GDPR purpose limitation (Art. 5(1)(b)): personal data collected for one purpose can't be repurposed for an *incompatible* one without a fresh basis. "We already have the data" is not a basis (verified 2026-06-05, `[verify-at-use]`).
- Consent must be **granular, recorded, and revocable**, and revocation has to actually take effect downstream — a withdrawal that never reaches the training set is a withdrawal in name only.
- The legal *interpretation* — whether training is a "compatible" purpose, whether legitimate interest could apply, whether re-consent is required — routes to legal / `regulatory-compliance` (§3). This team engineers the consent/basis plumbing.

## Attempts

- Tried: assume the broad "improving your experience" consent covers model training. Failed the compatibility test — a new ML training purpose is materially different from the original collection purpose, so the original consent doesn't stretch to cover it.
- Tried: filter the training set to "users who didn't opt out" using the marketing tool's opt-out list. Failed — the opt-out list was one of *three* disagreeing sources, and the analytics warehouse the training set came from didn't reflect any of them in real time. Filtering against a stale source re-includes people who withdrew.
- Tried (the move that worked): make the **consent/lawful-basis store the system of record** and **join the training-set eligibility to it at query time**. (1) Consolidate consent + purpose + opt-out state into one authoritative store with a recorded basis *per purpose* (not one global flag). (2) **Propagate revocation** to every downstream copy, including the analytics warehouse, so a withdrawal removes the person from eligible training data. (3) Gate the training-set build on a live eligibility check against the store — "may we use *this person's* data for *this purpose*?" — rather than a stale snapshot. The legal question of *which* basis training needs went to legal; the engineering made the answer enforceable.

## Resolution

The gap was **treating consent as a single global flag and the basis as fungible**, plus **revocation that didn't propagate**. The fix is a consent/basis store-of-record keyed per purpose, with revocation that reaches every downstream copy, and a live eligibility gate on any new use. Whether ML training is a compatible purpose or needs fresh consent/legitimate-interest is legal's interpretation — the team's job was to make whatever answer legal gives *enforceable at query time*.

**Action for the next engineer:** before any "let's use the data we already have for X," ask which **per-purpose** basis covers X and whether the eligibility check runs against a **live** consent store or a stale snapshot. Build one consent/basis store of record, propagate revocation downstream (the analytics/training copy is the one teams forget), and gate new uses on a live check. The compatibility/lawful-basis interpretation routes to legal / `regulatory-compliance` (§3); date every regulatory fact.

Cross-reference: complements the **lawful-basis selection** tree in [`../knowledge/dgp-lawful-basis-decision-tree.md`](../knowledge/dgp-lawful-basis-decision-tree.md), the **What's the lawful basis for this use?** tree in [`../knowledge/data-governance-privacy-decision-trees.md`](../knowledge/data-governance-privacy-decision-trees.md), and [`../best-practices/consent-store-is-a-system-of-record.md`](../best-practices/consent-store-is-a-system-of-record.md) + [`../best-practices/know-your-lawful-basis-honor-consent.md`](../best-practices/know-your-lawful-basis-honor-consent.md).

**Sources (retrieved 2026-06-05):**
- GDPR Art. 5(1)(b) purpose limitation and Art. 6 lawful basis — https://gdpr-info.eu/art-5-gdpr/ and https://gdpr-info.eu/art-6-gdpr/

Lawful-basis compatibility and consent requirements vary by jurisdiction and are legal interpretations — `[verify-at-use]` against current law and route the interpretation to legal before any deliverable.

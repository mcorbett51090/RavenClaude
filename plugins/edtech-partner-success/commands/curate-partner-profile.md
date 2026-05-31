---
description: "Curate a durable partner profile — capture the partner's stated outcomes in their own words, map the 6-role buying committee with champion-redundancy status, confirm the decision-maker is alive in the role, and carry provenance on every claim."
argument-hint: "[the partner, e.g. 'the durable profile for a mid-sized district']"
---

# Curate a partner profile

You are running `/edtech-partner-success:curate-partner-profile`. Build or refresh the durable partner record the user described (`$ARGUMENTS`) — the work the `partner-profile-curator` agent owns. The profile is the source of truth the QBR, the success plan, and the save play all read from, so it carries provenance and gets refreshed, not left to rot.

## When to use this

You are establishing or refreshing the standing record for a partner (at onboarding, on a handoff, before a QBR, or on the ~90-day cycle). NOT for a point-in-time analytics readout (that is `/edtech-partner-success:build-learning-analytics-readout`).

## Steps

1. **Capture the partner's stated outcomes verbatim** (`qbr-open-with-partner-outcomes-not-product-features.md`): record the business outcomes the partner said the product should move, in their own words — this is what the QBR opens with and what the renewal is read against, so don't paraphrase it into vendor KPIs.
2. **Map the full 6-role buying committee** (`sponsor-map-the-buying-committee-and-track-champion-redundancy.md`): economic buyer, champion, technical buyer, user-champion, blocker, executive sponsor — in K-12 the C&I / curriculum director often decides what wins before procurement opens, so a profile threaded only through the superintendent or a friendly user misses the deciding seat.
3. **Track champion-redundancy as a durable status** (`sponsor-map-the-buying-committee-and-track-champion-redundancy.md`): flag single-threading explicitly — a partner with one champion is one departure from churn, and the "ghost sponsor" pattern (a named buyer who left, profile never updated) recurs because nobody refreshed it.
4. **Confirm the decision-maker is alive in the role every quarter** (`risk-confirm-the-decision-maker-is-alive-in-the-role-every-quarter.md`): verify the economic buyer still holds the seat — a renewal that lands in a dead inbox is a self-inflicted surprise.
5. **Carry provenance on every durable claim** (`analytics-normalize-to-partner-size-and-state-the-comparison-baseline.md`): each fact in the profile carries its source and date so a stale number isn't quietly trusted later.
6. **Keep student-level data out of the profile** (`ferpa-classify-the-data-bucket-before-you-share-or-de-identify.md`): the durable record holds relationship and outcome facts, not protected education records — classify before storing, and route anything student-level through `ferpa-comms-translator`. Use generic placeholders (`<district>`) in every example.

## Guardrails

- A profile that's never refreshed becomes the ghost-sponsor trap — schedule the ~90-day refresh and update on every handoff.
- Don't store protected education records or PII in the durable profile; it holds committee/outcome/provenance facts, not student data.
- Capturing outcomes in the PSM's optimistic paraphrase instead of the partner's words is how the QBR opens on the wrong goals — keep it verbatim.

---
scenario_id: 2026-06-08-gated-ebook-that-poisoned-the-funnel
contributed_at: 2026-06-08
plugin: content-and-growth-marketing
product: hubspot
product_version: "unknown"
scope: likely-general
tags: [demand-gen, funnel, lead-quality, consent, distribution, measure-outcomes]
confidence: medium
reviewed: false
---

## Problem

A B2B team was judged on raw MRL volume — marketing-recognized leads per month — and hit the number by aggressively gating a generic ebook behind a form, buying a list to seed an email push, and pre-ticking the marketing-consent box. Lead *counts* looked great and the team was celebrated. But sales stopped working the leads: the MQL→SQL→win stages had quietly cratered, the demo show-rate fell, and the bought addresses were spiking spam complaints that started dragging down deliverability for the *real* nurture program.

## Constraints context

- The compensation/scorecard rewarded top-of-funnel lead count, with no stage-conversion or revenue tie-back — classic vanity-metric optimization.
- The consent posture was a dark pattern (pre-ticked opt-in, a purchased list with no consent at all), which was both a trust problem and, given the brand's markets, a compliance exposure.
- Nobody had run the funnel stage-by-stage; "performance" was a single blended lead number, so the dead MQL→SQL stage was invisible.

## Attempts

- Tried: gating harder and buying more list volume to push lead count even higher. Failed — it added more low-intent and non-consented contacts, worsened spam complaints, and further poisoned sender reputation; more bad leads is negative yield.
- Tried: a sales SLA forcing reps to call every lead within an hour. Failed — faster contact on garbage leads just burned rep time and annoyed people who never meaningfully opted in.
- Tried: instrumenting the funnel stage-by-stage (visitor→lead→MQL→SQL→win with the drop at each step), killing the purchased list and the pre-ticked consent, ungating the genuinely top-of-funnel asset to drive reach, and reserving the form for a higher-intent, genuinely valuable offer. This worked.

## Resolution

Once the funnel was read by *stage*, the leak was obviously MQL→SQL, not top-of-funnel volume. Removing the bought list and honest-consent-only capture shrank raw lead count but lifted MQL→SQL conversion and demo show-rate sharply; deliverability for the legitimate program recovered once complaints fell. Ungating the awareness asset increased its reach and assisted pipeline more than the gated version ever had. The scorecard was rebuilt around stage conversion and organic-to-pipeline, not lead count.

## Lesson

Measure outcomes by funnel *stage*, never a blended lead count — a healthy top-of-funnel can mask a dead MQL→SQL, and counting leads rewards volume that poisons the funnel. Permission and consent are non-negotiable: bought lists and pre-ticked boxes burn deliverability and trust for a number that doesn't convert. And distribution beats gating for top-of-funnel reach — gate only a genuinely high-value, high-intent offer.

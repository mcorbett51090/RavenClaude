---
scenario_id: 2026-06-08-crm-garbage-corrupts-routing
contributed_at: 2026-06-08
plugin: revops
product: generic
product_version: "unknown"
scope: likely-general
tags: [data-quality, routing, scoring, sla, dedupe, crm]
confidence: high
reviewed: false
---

## Problem

A mid-market sales org ran a quarterly "data cleanup" sprint and treated CRM hygiene as a periodic project rather than an entry-point discipline. Between sprints, duplicate accounts piled up (the same logo entered three ways), required fields went unfilled, and dead accounts lingered. The damage was downstream and silent: the lead-routing rules keyed on a region field that was blank 40% of the time, so those leads fell into an unowned queue and sat for days; the lead score double-counted activity across duplicate records, inflating junk leads to the top of the call list; and territory reports double-counted revenue across the dupes. Speed-to-lead averaged over a day on the leads that *did* route, and nobody had an SLA clock to even notice.

## Constraints context

- Hygiene was a quarterly scrub, not enforced at the point of entry — so every metric drifted back to garbage within weeks of each cleanup.
- No required-field validation and no dedupe-on-entry: reps and forms created records with whatever they typed, including the blank region field that broke routing.
- No speed-to-lead SLA existed — leads had no defined owner and no clock, so an unrouted lead was invisible until a rep happened to stumble on it.

## Attempts

- Tried: a bigger, more thorough quarterly cleanup. Failed — it fixed the snapshot and the data re-rotted within the quarter; cleanup is a treadmill when entry isn't enforced.
- Tried: rewriting the routing rules to be more clever around the missing data. Failed — you cannot route reliably on a field that's blank 40% of the time; the rule isn't the problem, the substrate is.
- Tried: enforcing required fields + dedupe at the point of entry (validation on create, a match-and-merge on the key identity fields), then putting a speed-to-lead SLA on routing with a defined owner and a clock, and rebuilding the lead score on deduped records. This worked.

## Resolution

Entry-point validation stopped new dupes and blank-region records at the source, so routing had a clean field to key on and leads got a defined owner within minutes instead of sitting unowned for days. Deduping the score base stopped junk leads inflating to the top of the call list. The speed-to-lead SLA (assign within minutes, with a clock that surfaced breaches) made unrouted leads visible instead of silently lost. Territory revenue stopped double-counting once the dupes were merged. The metrics held between quarters because the fix was at entry, not in a scrub.

## Lesson

Data quality is the substrate, not a cleanup project — duplicates, missing fields, and dead accounts silently corrupt every downstream metric (routing, scoring, territory, forecast). Enforce required fields and dedupe at the point of entry, never in a quarterly scrub that the data re-rots past within weeks. And routing/scoring are SLAs, not suggestions: a lead needs a defined owner, a speed-to-lead clock, and a score built on clean records — an unrouted lead is lost revenue.

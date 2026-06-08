---
scenario_id: 2026-06-08-parallel-control-sets-doubled-the-work
contributed_at: 2026-06-08
plugin: cybersecurity-grc
product: iso-27001
product_version: "unknown"
scope: likely-general
tags: [crosswalk, map-once-attest-many, soc2, iso-27001, evidence]
confidence: high
reviewed: false
---

## Problem

A mid-size company already had a SOC 2 Type II and decided to pursue ISO 27001 for European buyers. The compliance lead, treating them as separate programs, stood up a second, parallel control set and a separate evidence-collection process for ISO — duplicate access-review records, duplicate change-management evidence, duplicate vendor reviews. Within a quarter the team was collecting the same evidence twice, in two formats, for two audits, and control owners were fielding redundant requests. The duplication, not the controls themselves, became the bottleneck.

## Constraints context

- ~120 people; an existing SOC 2 Type II with a year of operating evidence.
- The ISO push was buyer-driven and time-boxed; no appetite to rebuild controls from scratch.
- Evidence was a mix of automated exports and a few manual cadences — workable once, painful twice.

## Attempts

- Tried: running ISO as a fully independent program with its own controls and evidence. Failed — it roughly doubled the operating load and control owners pushed back on duplicate requests.
- Tried: assuming the SOC 2 evidence would "just count" for ISO with no mapping. Failed — without an explicit crosswalk, the certification body couldn't trace which Annex A control each piece of evidence satisfied.
- Tried: picking one primary control set, crosswalking SOC 2 Trust Services Criteria to ISO 27001 Annex A (and noting the NIST references), and authoring a Statement of Applicability so a single evidenced control mapped to both audits. This worked — most controls satisfied both frameworks from one evidence stream.

## Resolution

The team consolidated to one control set with a crosswalk and a reasoned SoA. The handful of genuinely ISO-only requirements (the ISMS management-system clauses) were added on top rather than duplicated underneath. Evidence was collected once, mapped many, and control owners stopped seeing redundant requests. The ISO certification reused the existing operating evidence window instead of starting a new one.

## Lesson

Map once, attest many. Pick a primary framework and crosswalk the rest to it; a single well-evidenced control should satisfy SOC 2, ISO 27001, and NIST simultaneously. Parallel control sets for parallel audits are pure waste — the crosswalk plus a reasoned Statement of Applicability is what turns one evidence stream into multiple attestations.

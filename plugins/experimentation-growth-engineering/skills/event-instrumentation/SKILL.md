---
name: event-instrumentation
description: "Instrument trustworthy product analytics: a tracking plan first, a consistent typed event/property schema (object_action naming, versioned), identity stitching (anonymous -> known), CDP routing (instrument once), and event-quality validation as code."
---

# Event Instrumentation

## Tracking plan first
Define events + properties + naming + types **before** instrumenting. Ad-hoc events = the data mess.

## Consistent schema
`object_action` naming, one case convention, **typed + validated** properties, versioned. An event named 3 ways is 3 events.

## Identity stitching
Tie **anonymous -> known** on identify, so funnels/attribution survive login. Broken stitching breaks every cross-session analysis.

## CDP + quality
Instrument **once** (Segment-style), fan out (warehouse copy -> data-platform). Validate events against the plan; monitor volume; treat instrumentation **as code**.

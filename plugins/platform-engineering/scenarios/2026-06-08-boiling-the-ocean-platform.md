---
scenario_id: 2026-06-08-boiling-the-ocean-platform
contributed_at: 2026-06-08
plugin: platform-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [thinnest-viable-platform, cognitive-load, roadmap, scope, platform-as-product]
confidence: high
reviewed: false
---

## Problem

A newly-formed platform team published an ambitious 12-capability roadmap — portal, catalog, scaffolder, multi-cloud provisioning, secrets management, a CLI, a cost dashboard, a service mesh control plane, and more — and disappeared for two quarters to build the foundation. When they emerged, almost nothing was usable end-to-end: half-built capabilities with no single path a team could actually take from "I want a new service" to "it's in production." Stream-aligned teams had routed around them entirely, building their own scripts. The platform team had been busy and shipped nothing that removed real cognitive load.

## Constraints context

- A real, repeated pain existed: every team hand-rolled a slightly different new-service setup (CI, deploy, secrets, observability), re-deriving the same decisions.
- The team optimized for an impressive-looking platform surface rather than for one painful workflow solved completely.
- No capability was justified by a named, concrete load it removed — the roadmap was a feature list, not a cognitive-load map.

## Attempts

- Tried: parallelizing all 12 capabilities to "go faster." Failed — everything was 60% done and nothing was usable; partial capabilities remove no load because a developer still can't complete a workflow without falling off the half-paved road.
- Tried: a steering committee to prioritize the backlog by stakeholder votes. Failed — it produced a politically-balanced list, not a leverage-ordered one, and still didn't ship a complete path.
- Tried: collapsing to a thinnest viable platform — pick the single highest-leverage workflow (new-service creation through to a running deploy), pave that *one* golden path completely (scaffolder registers the service, wires CI, ships docs and secure defaults), ship it, and only then expand on observed pull. This worked.

## Resolution

One fully-paved path that a team could take end-to-end removed more cognitive load than twelve half-built capabilities combined. Adoption came from ergonomics — the path was genuinely the easiest way to start a service — and the next capabilities were chosen by what consumers pulled for, not by the original roadmap. The team measured the load removed (no more hand-rolled setup) instead of the surface shipped.

## Lesson

Thinnest viable platform first, and cognitive load is the metric — pave the single highest-leverage path completely before building anything broader, and justify every capability by the concrete load it removes. A broad, half-built platform surface removes no load and breeds shadow tooling; one complete golden path beats twelve partial ones.

---
scenario_id: 2026-06-09-rewrite-reflex-vs-sized-paydown
contributed_at: 2026-06-09
plugin: engineering-management
product: tech-health
product_version: "n/a"
scope: likely-general
tags: [tech-debt, rewrite, carrying-cost, hotspot, strangler-fig]
confidence: medium
reviewed: false
---

## Problem

A team wanted to halt the roadmap for a quarter to rewrite a "terrible" legacy service. The risk: tech-debt was being framed as an all-or-nothing moral failing rather than a sized carrying cost traded against the roadmap, and a rewrite is the highest-risk, longest-payback option (§3 #7).

## Context

- The complaint was *felt* ("the codebase is slowing us down"), not yet *measured* (§3 #4 #7).
- Constraint: frame debt as carrying cost vs roadmap value, sized per case, on a measured hotspot (§3 #7).
- Leadership was about to approve the rewrite on the strength of the feeling alone.

## Attempts

- Tried: **measured the pain** — lead-time drift, change-fail, rework, and hotspots — instead of trusting the feeling (§3 #4 #7). Outcome: only two files (a hotspot) drove most of the rework; the rest of the "terrible" service was stable.
- Tried: **sized carrying cost + payback** with the `tech-debt` calculator (§3 #7). Outcome: an incremental paydown on the hotspot had a short payback; the full rewrite did not, within the code's remaining life.
- Tried: **traded explicitly against the roadmap** — a reserved capacity slice for strangler-fig paydown on the hotspot, no roadmap halt (§3 #7). Outcome: velocity recovered without the rewrite risk.

## Resolution

The fix was a **sized, incremental paydown on a measured hotspot**, not a quarter-long rewrite. The output was a tech-debt decision memo with measured pain, carrying cost, payback, and a capacity slice.

**Action for the next manager hitting this pattern:** **measure the pain, size the carrying cost and payback, confirm it's a hotspot, and prefer incremental over rewrite.** "We must rewrite it" and "we never have time" are the same unsized, untraded mistake (§3 #7). The architecture itself routes to `ravenclaude-core/architect`. See Tree 3 and the `decide-tech-debt` skill.

Figures are context-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data (§3 #8).

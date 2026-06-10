---
scenario_id: 2026-06-08-scope-creep-blew-the-soc2-budget
contributed_at: 2026-06-08
plugin: cybersecurity-grc
product: soc2
product_version: "unknown"
scope: likely-general
tags: [scope, audit-boundary, soc2, type-ii, cost]
confidence: high
reviewed: false
---

## Problem

A Series-A SaaS company kicked off its first SOC 2 Type II by declaring "everything we run is in scope" — every AWS account, the corporate IT environment, three internal tools, and a legacy on-prem box nobody fully understood. By the time fieldwork approached, the team was drowning: evidence had to be produced for systems that didn't touch customer data, the legacy box had no collectible evidence at all, and the projected audit cost had nearly doubled. Worse, the broad scope created exceptions in areas that had nothing to do with the customer-facing product — findings that read badly in the report for no business reason.

## Constraints context

- ~45 people, one production SaaS product on AWS; the on-prem box was a vestigial internal app.
- A prospect had asked for the SOC 2, so the deadline was real and money was tight.
- The CTO had set scope by "what we own," not by "what carries customer data and what we can attest."

## Attempts

- Tried: keeping everything in scope and brute-forcing evidence collection across all of it. Failed — the legacy box couldn't produce a clean evidence window, and the effort/cost ballooned with no assurance benefit to the customer.
- Tried: quietly dropping the hardest systems with no documentation. Failed — an undocumented carve-out is a boundary the auditor can't trace, and it invited questions about what else was excluded.
- Tried: re-scoping deliberately — drawing the boundary around the production SaaS environment and the controls that support it, segmenting it from corporate IT and the legacy box with a defensible network/access boundary, and documenting each carve-out with a justification. This worked: a tight, attestable scope the team could fully evidence.

## Resolution

The audit boundary shrank to the production product and its supporting controls, segmented and documented. The legacy box was carved out with a written justification (no customer data, isolated) and slated for decommissioning. The audit came in near the original budget, the evidence was collectible at the source, and the report covered exactly what customers cared about — with no stray exceptions from out-of-scope systems.

## Lesson

Scope is the highest-leverage decision. What's in the boundary drives cost, effort, and risk more than any control choice. Scope down to what carries the data and what you can attest honestly, segment it with a defensible boundary, carve out the rest with a documented justification, then expand in later cycles — don't set scope by ambition or by "what we own."

---
scenario_id: 2026-06-05-usage-data-identity-gap-data-platform-seam
contributed_at: 2026-06-05
plugin: customer-success-analytics
product: identity-seam
product_version: "n/a"
scope: likely-general
tags: [identity-resolution, usage-data, data-platform-seam, bridge-xref, null-not-zero]
confidence: high
reviewed: false
---

## Problem

The usage-trend signal — the single strongest churn predictor in the model — was producing nonsense for a chunk of the book: accounts that were clearly active showed flat-zero usage, and the health tier was flagging them Red. The root cause wasn't the signal design; it was an **identity-resolution gap upstream** — the product-usage events couldn't be joined to the CRM account spine, so "no matched events" was being read as "no usage."

## Context

- Segment: B2B SaaS, multi-product, usage events keyed on a product-side tenant ID that did **not** match the CRM Account ID.
- Constraint: a portion of accounts had no deterministic key linking usage events to the account master key; the join fell back to a name match that silently dropped the unmatched events. The mart then computed usage-trend over an incomplete event set.
- **Two house-rule violations compounded it:** (1) the unmatched-usage case was being coded as `0` instead of `NULL` — so a missing join read as "terrible usage," not "unknown"; (2) someone had started patching the join with name-only matches **inside the CS mart**, re-implementing identity resolution that belongs upstream.

## Attempts

- Tried: traced the zero-usage Reds back through the mart and confirmed they were **join failures, not real declines** (the metric-discrepancy tree in `customer-success-decision-trees.md` — grain/identity branch). Outcome: established that the signal was fine and the spine was broken.
- Tried: **routed the fix to `data-platform`, not patched it here.** Identity resolution is a data-platform deliverable (the `bridge_account_xref` cross-reference + the deterministic→domain→name precedence ladder + a resolution audit). This plugin *consumes* the resolved spine and defines the grain; it does not build the matcher. Outcome: the unmatched usage events got a proper deterministic/domain key path, with name-only matches quarantined for stewardship review instead of silently landed.
- Tried: fixed the `NULL`-not-zero handling in the mart so an unresolved account reads as **missing usage (NULL)**, not zero usage — which kept it *off* the Red list until the data was real. Surfaced a `data-pending` flag instead of a false Red. Outcome: the spurious Reds disappeared and the team stopped chasing phantom risk.

## Resolution

A usage signal is only as trustworthy as the identity spine under it. "No matched events" is **not** "no usage" — it's unknown, and it must read as `NULL`, never `0`. And the fix lives **upstream in data-platform's identity resolution, not in a name-match patch inside the CS mart**: this plugin consumes the resolved `bridge_account_xref` spine and defines the grain; it never re-implements the matcher and never publishes a metric off a name-only match without human review.

**Action for the next consultant hitting this pattern:** when a usage (or any source) signal shows suspicious zeros, **check the identity join before trusting the metric.** Confirm it's a join failure, not a real decline (the metric-discrepancy tree). Then: code the unmatched case as `NULL` not `0`, surface a `data-pending` flag, and **hand the resolution fix to `data-platform`** (the `cross-system-identity-resolution` skill + `bridge_account_xref`) — do not patch identity inside the CS mart. This is the canonical domain-layer-hands-contract-to-data-platform seam.

**Sources (this-plugin grounding, no external claim):** the seam is defined in this plugin's CLAUDE.md §4 #5 + #7 and the `identity-resolution-is-upstream-never-reimplement-it` / `nulls-are-explicit-missing-signal-is-never-silently-zero` best practices; the upstream matcher contract is [`../../data-platform/skills/cross-system-identity-resolution/SKILL.md`](../../data-platform/skills/cross-system-identity-resolution/SKILL.md) and [`../../data-platform/knowledge/where-cs-metrics-live.md`](../../data-platform/knowledge/where-cs-metrics-live.md). No external statistic is asserted in this scenario.

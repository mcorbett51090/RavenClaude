# Cite GA/preview status with a retrieval date for every Fabric capability you recommend

**Status:** Absolute rule
**Domain:** Cross-cutting / accuracy
**Applies to:** `microsoft-fabric`

---

## Why this exists

Fabric ships monthly GA promotions and preview introductions. A capability that was preview in March 2026 may be GA in May 2026, and one that was GA may have changed its billing model. Recommending a feature without citing its status and the date you checked is a confident-reasoning error: the consumer takes it as authoritative, designs around it, and discovers at build time that the behavior changed, the feature is still preview, or it is now billed differently. This is especially sharp for Direct Lake modes, OneLake security RLS/CLS, materialized views, and AI functions — all of which have been in rolling preview/GA cycles in 2025–2026.

## How to apply

Every design recommendation that cites a Fabric capability must include:

```
Direct Lake on-SQL mode — GA as of [retrieve date: 2026-03-15, Microsoft Learn Fabric release notes]
OneLake security RLS — Generally Available [retrieve date: 2026-04-01]
Materialized views (Eventhouse) — GA [retrieve date: 2026-06-01]
Fabric Data Agent — GA [retrieve date: 2026-05-28, fabric-2026-capability-map.md]
```

If the date cannot be confirmed in-session:

```
OneLake security CLS — [unverified — training knowledge; verify against Fabric release notes before using in production]
```

When writing to a knowledge doc or best-practice, add a `Last verified:` date and the source URL to the claim.

**Do:**
- Read `knowledge/fabric-2026-capability-map.md` before any capability recommendation — it is the plugin's freshness anchor.
- Flag any capability claim older than 90 days as needing re-verification.
- Re-verify Direct Lake guardrail numbers (rows per table, Parquet file count, memory limits) per SKU before quoting — these have changed between SKU generations.

**Don't:**
- Assert "Direct Lake supports X" or "OneLake security is GA" from training-knowledge memory alone — Fabric's monthly cadence makes these facts volatile.
- Skip the `[verify-at-build]` marker on SKU-gated limits even when you believe they are current — the consumer may be on a different SKU than you assumed.
- Quote a preview feature as production-ready in a design document without an explicit "Preview — not for production SLA" marker.

## Edge cases / when the rule does NOT apply

Core OneLake concepts (Delta Parquet format, the medallion layer structure, workspace/item model) are stable across releases and do not need per-claim retrieval dates. The rule targets capability-availability and billing claims, not structural concepts.

## See also

- [`../agents/fabric-architect.md`](../agents/fabric-architect.md) — owns the capability-selection decision and is the primary enforcer of this rule
- [`./name-your-direct-lake-mode.md`](./name-your-direct-lake-mode.md) — an example of a volatile capability claim (two modes, different behaviors) that requires a date

## Provenance

Codifies CLAUDE.md house opinion #9 ("cite the capability's GA/preview status with a retrieval date; Fabric ships monthly") and the Claim Grounding & Source Honesty protocol from the plugin constitution.

---

_Last reviewed: 2026-06-05 by `claude`_

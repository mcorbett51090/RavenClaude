# State the Mirroring read-only and query-billing caveats before recommending it

**Status:** Absolute rule
**Domain:** Data movement / Mirroring
**Applies to:** `microsoft-fabric`

---

## Why this exists

Fabric Mirroring is a turn-key near-real-time Delta replica of an external operational database. "Free to replicate" means the replication cost itself is not billed — but every query against the mirrored Delta tables is billed at the normal Fabric query rate. The anti-pattern is recommending Mirroring as "free" without surfacing the query-billing caveat. This misleads consumers who run heavy BI workloads on top of the mirror and then receive an unexpected capacity bill. Additionally, Mirroring destinations are **read-only** — no INSERT/UPDATE/DELETE is possible on the mirrored tables. Engineers who omit this caveat create architectures where a downstream transformation step tries to write to the mirror and fails at runtime.

## How to apply

Every recommendation to use Mirroring must state:

```
Mirroring replicates data to OneLake at no replication cost.
Queries against the mirrored Delta tables are billed at normal Fabric capacity rates.
Mirrored tables are READ-ONLY — no DML is possible against the Delta destination.
If transformation is needed, read from the mirror (bronze) and write to a separate silver lakehouse.
```

Checklist for any Mirroring design:
- [ ] Source is in the supported connectors list (SQL Server, Azure SQL, Cosmos DB, Snowflake, etc.) and the version/tier is supported `[verify-at-build]`.
- [ ] Consumer understands query billing at their typical query volume.
- [ ] Downstream transforms write to a separate, writable lakehouse — not to the mirrored destination.
- [ ] RLS on the source database is noted: Mirroring replicates data as-is; source-side row filtering is **not** applied in the mirror.

**Do:**
- Present the mirroring choice using the data-movement decision tree to confirm it is the right tool (not a pipeline or copy job).
- Document the replication lag expectation (typically seconds to minutes, source-dependent `[verify-at-build]`) in the design.

**Don't:**
- Describe Mirroring as "free data sync" without the query-billing caveat — "free to replicate" is not "free to use."
- Recommend Mirroring for a source that requires DML writeback (e.g., a "staging + transform in place" pattern) — the destination is read-only.
- Conflate Mirroring with Auto-mirroring: Auto-mirroring applies to SQL DBs and Cosmos DBs **already inside Fabric** (zero config); external-DB Mirroring requires enabling the Mirroring feature in the Fabric admin center.

## Edge cases / when the rule does NOT apply

When the consumer explicitly asks "I want a read-only analytical copy with minimal setup," Mirroring is exactly right — state the read-only nature as a feature, not a caveat, and confirm the query-billing expectation is understood.

## See also

- [`../agents/data-factory-engineer.md`](../agents/data-factory-engineer.md) — owns the data-movement decision and is primary enforcer of this rule
- [`./one-copy-shortcut-before-copying.md`](./one-copy-shortcut-before-copying.md) — the broader "shortcut before copying" principle of which Mirroring is a specific form

## Provenance

Codifies CLAUDE.md anti-pattern "calling Mirroring 'free' without the 'replicate-free, query-billed' caveat" (§4) and the `check-fabric-anti-patterns.sh` hook check; Microsoft Learn Fabric Mirroring documentation.

---

_Last reviewed: 2026-06-05 by `claude`_

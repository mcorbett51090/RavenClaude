# Research routine — OneLake-security GA correction (2026-06-15)

A Tier-A (news-cadence) weekly sweep run. Scope was honest-by-construction per
[`docs/research-routine-two-cadence.md`](../research-routine-two-cadence.md): only the ~25 vendor-API-anchored
plugins are swept for "news," and within that, this run drained the highest-value **open correction** from the
2026-06-11 backlog ([`2026-06-11-broad-sweep-findings.md`](2026-06-11-broad-sweep-findings.md)) that actively
misleads: the dedicated `microsoft-fabric` OneLake-security doc still carried pre-GA "preview" framing that the
plugin's own capability map (PR #411, v0.8.1) had already corrected — an internal contradiction.

## Finding (verified 2026-06-15 via the Microsoft-Learn MCP, first-party)

`plugins/microsoft-fabric/knowledge/onelake-security-and-governance.md` (Last reviewed 2026-05-28) was behind reality:

1. **GA, not preview.** OneLake security (data-access roles + RLS/CLS/OLS) is **GA**, rolling out default-on across
   supported items (Microsoft targeted end of May 2026). Source: [data access control model](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model) + Fabric what's-new. Still **public preview**: Eventhouse RLS, authorized third-party-engine enforcement.
2. **Supported items + ReadWrite** were undocumented: Lakehouse (Read, **ReadWrite**), Azure Databricks Mirrored Catalog (Read), Mirrored Databases (Read). Source: [get-started](https://learn.microsoft.com/fabric/onelake/security/get-started-onelake-security#what-types-of-data-can-be-secured).
3. **DefaultReader gotcha**: adding a user to a tighter role does not revoke the auto-created `DefaultReader` access — must remove them or the role buys nothing.
4. **Authorized-engine model** (`principalAccess` API) replaced the vague "third-party / partial / preview" row, incl. the unrestricted-Read foot-gun.
5. **Schema-enabled nuance** (the trap — see panels below): schema-enabled is **required for the in-portal data-preview pane** of RLS/CLS-secured tables, but **Spark RLS/CLS *enforcement* works schemaless** via `spark.sql.fabric.catalog.enable-schemaless-lakehouses=true`. Source: [OneLake security limitations](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model#onelake-security-limitations) + [Spark support](https://learn.microsoft.com/fabric/data-engineering/spark-onelake-security).

## Panel 1 — usefulness assessment

**VERDICT: USEFUL · confidence high.** A Tier-A plugin whose #1 discipline is "cite GA/preview status with a date"
was internally self-contradicting on exactly that axis; every sub-claim is primary-source-cited; the fix is
proportionate (knowledge-file + one house-opinion line, no code). Caveats carried forward: don't over-correct the
schema-enabled point; keep Eventhouse/authorized-engine as preview; soften "all supported items"; restamp the date.

## Panel 2 — detailed review of the drafted edits

**VERDICT: APPROVE-WITH-FIXES · confidence high.** Most edits faithful to Learn, but it caught a real over-correction
(independently confirming a trap the editor had also flagged): the first draft collapsed the **data-preview pane**
(schema-enabled *required*, Learn limitation #4) and **Spark enforcement** (schemaless *works* via the flag) into one
claim, erasing a still-true limitation. P0s applied:

- Split data-preview-vs-enforcement in both the knowledge doc and CLAUDE.md #14.
- Resolved the cross-file contradiction the draft's own callout claimed was fixed: scoped "prerequisite for OneLake
  security" → "...data-preview pane" in `fabric-2026-capability-map.md`, `skills/direct-lake-gold-shaping/SKILL.md`,
  and `agents/fabric-admin.md`.
- Softened the "all supported items / default-on" absolute to "GA; rolling out default-on (targeted end of May 2026)"
  and noted the one stale Learn sub-page (`onelake-shortcut-security`) still labeled "(preview)".

P1s applied: repointed the DefaultReader citation anchor; added the authorized-engine unrestricted-Read foot-gun;
marked the third-party CLS cell "engine-enforced"; added the Runtime-1.3/env-3.5 + latency/permission caps.

## Tiebreak

**Not needed** — the panels agreed (useful → approve-with-fixes); no third panel convened.

## Shipped

- `microsoft-fabric` **v0.8.1 → v0.8.2** (plugin.json + marketplace.json lockstep; CHANGELOG entry).
- Files: `knowledge/onelake-security-and-governance.md`, `CLAUDE.md`, `knowledge/fabric-2026-capability-map.md`,
  `skills/direct-lake-gold-shaping/SKILL.md`, `agents/fabric-admin.md`.

## Still open in the backlog (not this run)

Fabric Graph GA, Copy-job CDC / Eventstream connectors GA, M365-Copilot Fabric Data Agents, microsoft-graph
agentUser/passkey, tableau 2026.2, data-streaming Flink-2.x/Kafka-4.0 + database-engineering PG18 version-anchor rot.
These remain queued for a future run; this run deliberately scoped to the one open CORRECTION that actively misleads.

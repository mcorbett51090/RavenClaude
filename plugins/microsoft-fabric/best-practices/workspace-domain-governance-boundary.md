# Workspaces and domains are the governance boundary — security at the right plane, not the wrong role

**Status:** Absolute rule (the two-plane model) / Pattern (workspace-per-layer-and-stage topology) — treating workspace roles as data access, or promising RLS/CLS on an engine where it's preview, is a bug (house opinion #6).

**Domain:** Governance / OneLake security / topology

**Applies to:** `microsoft-fabric`

---

## Why this exists

Security in Fabric is enforced on **two planes**, and conflating them is the documented governance failure (house opinion #6): the **control plane** (what you can *do* — workspace roles) vs the **data plane** (what data you can *see* — OneLake security RLS/CLS/OLS). Two traps follow. First, **Admin/Member/Contributor's Write overrides any OneLake-security Read restriction** — you *cannot* use OneLake security to restrict those roles, only to grant Viewers; promising "I'll lock that data down with RLS" for a Contributor is false. Second, **RLS/CLS is not uniformly available** — it's GA on Lakehouse/SQL-endpoint/Direct-Lake-on-OneLake but **Eventhouse is RLS-only public preview** and third-party engines are partial/preview; quoting a guarantee on the wrong engine is a bug (house opinion #9: cite GA/preview with a date). Layer/stage workspaces (medallion layer boundaries + dev/test/prod) make the topology itself the governance boundary.

## How to apply

Put the boundary on the workspace, enforce data access on the data plane, and verify the engine's RLS/CLS status before promising it.

```text
Control plane (what you can DO):  workspace roles (Admin/Member/Contributor/Viewer) + domains.
Data plane   (what you can SEE):  OneLake security data-access roles (RBAC + RLS/CLS/OLS).
Boundary     (topology):          one workspace per medallion layer AND per dev/test/prod stage.
```

| Role | Can do | OneLake data (default) |
|---|---|---|
| Admin / Member / Contributor | full use | **always read+write** (overrides OneLake-security Read) |
| Viewer | see items | **no data by default** — grant via OneLake security roles |

- **Grant Viewers data** with OneLake security data-access roles (folder/table scope), carrying RLS/CLS predicates / OLS as needed. A user in *no* role sees **no data**.
- **Verify the engine's RLS/CLS status** before committing: Lakehouse/SQL-endpoint/Direct-Lake-on-OneLake = GA; **Eventhouse RLS-only = preview**; third-party = preview. Cite the status + retrieval date.
- **Mind the prerequisites/caps:** **schema-enabled lakehouses required** for OneLake-security data preview (house opinion #14); **250 roles/item, 500 members/role**; RLS-only and CLS-only roles can't be combined in one role.
- **Domains** group workspaces (usually by business unit) for data-mesh governance and delegated tenant settings — domain assignment drives **discovery/consumption filtering, not access** (access still comes from roles).
- **Route every auth/secret/PII change** (SPNs, OneLake-security roles, tenant settings) through `ravenclaude-core/security-reviewer`.

**Do:**
- Keep the planes separate: workspace roles for control, OneLake security for data.
- Make medallion layers and dev/test/prod stages each their own workspace.
- Cite RLS/CLS GA/preview status (per engine) with a retrieval date before promising it.

**Don't:**
- Treat a workspace role (Viewer especially) as a data-access grant — Viewer sees no data by default.
- Claim OneLake security can *restrict* an Admin/Member/Contributor — Write overrides it.
- Promise RLS/CLS on Eventhouse/third-party engines as if GA — verify first (house opinion #9).

## Edge cases / when the rule does NOT apply

- **Warehouse SQL-native security** (RLS/CLS/dynamic data masking/OLS at the T-SQL layer) is its own surface — but a Direct Lake model over a SQL-defined RLS table **forces Direct-Lake-on-SQL fallback** (see [`name-your-direct-lake-mode.md`](./name-your-direct-lake-mode.md)).
- **A tiny single-team workspace** may not need layer/stage separation — say so; the boundary is for governed, multi-stakeholder estates.
- **Default roles** (e.g. Lakehouse `DefaultReader`) auto-grant a baseline via member virtualization — know what they expose before relying on them.

## See also

- [`../knowledge/onelake-security-and-governance.md`](../knowledge/onelake-security-and-governance.md) — two planes, the RLS/CLS GA/preview matrix, domains, Purview
- [`alm-deploy-via-pipelines-parameterize-sources.md`](./alm-deploy-via-pipelines-parameterize-sources.md) — the per-stage workspaces this topology feeds
- [`lakehouse-medallion-layer-boundaries.md`](./lakehouse-medallion-layer-boundaries.md) — the layer-per-workspace boundary
- [`../agents/fabric-admin.md`](../agents/fabric-admin.md)

## Provenance

Codifies house opinions #6, #9, and #14 from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in [Security overview](https://learn.microsoft.com/fabric/security/security-overview), [OneLake security access-control model](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model) (Contributor Write overrides OneLake Read; Viewer no data by default; 250 roles/item, 500 members/role; RLS-only + CLS-only can't combine), and [Domains](https://learn.microsoft.com/fabric/governance/domains) (discovery filtering, not access) — Microsoft Learn, retrieved 2026-05-30. RLS/CLS GA/preview matrix from [`../knowledge/onelake-security-and-governance.md`](../knowledge/onelake-security-and-governance.md).

---

_Last reviewed: 2026-05-30 by `claude`_

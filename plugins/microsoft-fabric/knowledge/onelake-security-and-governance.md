# OneLake security & governance

**Last reviewed:** 2026-06-15 · **Confidence:** high (first-party Microsoft Learn, GA/preview re-verified 2026-06-15 via the Microsoft-Learn MCP).
**Owner:** `fabric-admin`.
**Source:** [Security overview](https://learn.microsoft.com/fabric/security/security-overview), [OneLake security access-control model](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model), [Get started with OneLake security](https://learn.microsoft.com/fabric/onelake/security/get-started-onelake-security), [Spark support for OneLake security](https://learn.microsoft.com/fabric/data-engineering/spark-onelake-security), [OneLake security integrations overview](https://learn.microsoft.com/fabric/onelake/security/onelake-security-integrations-overview), [Domains](https://learn.microsoft.com/fabric/governance/domains), [OneLake catalog](https://learn.microsoft.com/fabric/governance/onelake-catalog-overview).

> **Status (re-verified 2026-06-15):** OneLake security — data-access roles with RLS/CLS/OLS — is **GA**, rolling out as **default-on across supported items** (Microsoft targeted end of May 2026). This aligns the doc with the sibling [`fabric-2026-capability-map.md`](fabric-2026-capability-map.md), which the 2026-06-11 sweep already corrected from "preview" to GA. What remains **public preview** is *specific enforcement surfaces*, not the feature: **Eventhouse RLS** and **authorized third-party-engine** enforcement (see the matrix below). `[verify-at-use]` — Fabric ships monthly; one Learn sub-page (`onelake-shortcut-security`) still carries a stale "(preview)" label, so re-confirm the release state at build.

## Two planes — keep them separate (house opinion #6)

Security in OneLake is enforced on **both** the control plane and the data plane:

- **Control plane** = what you can *do* (create/manage/share items). Governed by **workspace roles**.
- **Data plane** = what data you can *see*. Governed by **OneLake security** (RBAC, RLS/CLS/OLS).

### Workspace roles

| Role | Workspace items | OneLake data (default) |
|---|---|---|
| Admin / Member / Contributor | full use | **always** read+write (overrides OneLake-security Read) |
| Viewer | can see items | **no data by default** — grant via OneLake security |

So Admin/Member/Contributor's **Write** permission **overrides** any OneLake-security Read restriction — you cannot use OneLake security to *restrict* those roles, only to *grant* Viewers. ([RBAC model](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model))

### OneLake security (data plane)

Create **data-access roles** on a Fabric data item granting access to specific folders/tables, then assign users/groups. A user not in any role sees **no data** in that item. **Default roles** (e.g. Lakehouse `DefaultReader`) auto-grant a baseline using member virtualization. Roles can carry **RLS** (row) and **CLS** (column) predicates; **OLS** (object — table/folder level) hides tables/columns.

A role grants either **Read** or **ReadWrite**. ReadWrite lets a Viewer-level user edit data on specific tables/folders (via Spark notebooks, OneLake File Explorer, or OneLake APIs — **not** the Lakehouse UX) without granting item create/manage rights. Supported data items + permissions ([Get started with OneLake security](https://learn.microsoft.com/fabric/onelake/security/get-started-onelake-security#what-types-of-data-can-be-secured)):

| Data item | Supported permissions |
|---|---|
| Lakehouse | Read, **ReadWrite** |
| Azure Databricks Mirrored Catalog | Read |
| Mirrored Databases | Read |

> **DefaultReader gotcha (security-relevant):** when you add a user to a tighter data-access role, **also remove them from `DefaultReader`** (or remove the `ReadAll` permission that virtualizes them into it) — otherwise they keep full read access and your RLS/CLS role buys nothing. ([Default roles / member virtualization](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model#onelake-security-and-workspace-permissions))

## The GA/preview matrix — RLS/CLS is NOT uniformly available (must-cite)

| Engine / surface | RLS | CLS | Status |
|---|---|---|---|
| Lakehouse / Spark notebooks | Yes | Yes | GA |
| SQL analytics endpoint (**user's-identity** mode) | Yes | Yes | GA |
| Direct Lake **on OneLake** | Yes | Yes | GA (drives empty results, not errors, on misconfig) |
| Eventhouse / KQL | RLS only | — | **public preview** |
| Authorized third-party engines (authorized-engine model) | Yes (engine-enforced) | Yes (engine-enforced) | **public preview** |

**Authorized-engine model** (the third-party row): an external engine registers an Entra identity as a workspace **Member**, reads raw Delta files from OneLake, then calls the OneLake `principalAccess` API to fetch the user's *precomputed effective access* (table permissions + RLS predicates + CLS column lists) and enforces it in its own compute. OneLake stays the single source of truth; non-authorized external reads of an RLS/CLS table are **blocked**, not silently unfiltered. **Foot-gun:** the engine's registered identity must itself have **unrestricted Read** on the tables it serves — if RLS/CLS applies to that identity, the `principalAccess` calls return errors. ([Integrations overview](https://learn.microsoft.com/fabric/onelake/security/onelake-security-integrations-overview))

Prerequisites + caps:
- **Schema-enabled lakehouses for the in-portal *data-preview* pane (house opinion #14).** The **data preview of RLS/CLS-secured tables is not supported on non-schema lakehouses** — schema-enabled is required for *that experience* and is the recommended OneLake-security default. ([OneLake security limitations](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model#onelake-security-limitations)) **Distinct from Spark RLS/CLS *enforcement*,** which *does* work on a non-schema lakehouse: set the Spark property `spark.sql.fabric.catalog.enable-schemaless-lakehouses=true` on the environment. ([Spark support for OneLake security](https://learn.microsoft.com/fabric/data-engineering/spark-onelake-security))
- Spark notebooks need **environment 3.5+ on Fabric Runtime 1.3+** for OneLake-security enforcement.
- Caps: **250 roles per item** (request-increase to 1000), **500 members per role**, **500 permissions per role**. Role-definition changes take ~5 min to apply; user-group membership changes ~1 hr (engine caches may add another hour).
- **RLS-only and CLS-only roles cannot be combined** in one role.
- Warehouse also supports SQL-native **RLS / CLS / dynamic data masking / OLS** at the T-SQL layer; a Direct Lake model over a SQL-defined RLS table forces Direct-Lake-on-SQL fallback.

## Governance surfaces

- **OneLake catalog** — Explore (discover), **Govern** (posture + recommended actions for data you own), **Secure** (audit workspace + OneLake-security roles, create/edit/delete from one place). Embedded in Teams/Excel/Copilot Studio; programmatic via the Catalog Search REST API.
- **Domains / subdomains** — logically group workspaces (usually by business unit) for **data-mesh** governance; tenant settings can be **delegated** to domain admins. Domain assignment drives *consumption/discovery filtering*, not access (access still comes from roles).
- **Microsoft Purview** — catalog, lineage, sensitivity labels, DLP across the unified data estate.
- **Sensitivity labels** propagate with data through Fabric.

> Any auth/secret/PII change (service principals, OneLake-security roles, tenant settings) routes through **`ravenclaude-core/security-reviewer`** (mandatory per the marketplace convention).

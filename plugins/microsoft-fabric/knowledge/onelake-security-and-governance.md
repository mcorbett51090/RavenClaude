# OneLake security & governance

**Last reviewed:** 2026-05-28 · **Confidence:** high (first-party Microsoft Learn, retrieved 2026-05-28).
**Owner:** `fabric-admin`.
**Source:** [Security overview](https://learn.microsoft.com/fabric/security/security-overview), [OneLake security access-control model](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model), [Get started with OneLake security](https://learn.microsoft.com/fabric/onelake/security/get-started-onelake-security), [Domains](https://learn.microsoft.com/fabric/governance/domains), [OneLake catalog](https://learn.microsoft.com/fabric/governance/onelake-catalog-overview).

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

Create **data-access roles** on a Fabric data item granting access to specific folders/tables, then assign users/groups. A user not in any role sees **no data** in that item. **Default roles** (e.g. Lakehouse `DefaultReader`) auto-grant a baseline using member virtualization. Roles can carry **RLS** (row) and **CLS** (column) predicates; **OLS** (object) hides tables/columns.

## The GA/preview matrix — RLS/CLS is NOT uniformly available (must-cite)

| Engine / surface | RLS | CLS | Status |
|---|---|---|---|
| Lakehouse / Spark | Yes | Yes | GA |
| SQL analytics endpoint (user identity) | Yes | Yes | GA |
| Direct Lake **on OneLake** | Yes | Yes | GA (drives empty results, not errors, on misconfig) |
| Eventhouse / KQL | RLS only | — | **public preview** |
| Third-party / external engines | partial | partial | **preview** |

Prerequisites + caps:
- **Schema-enabled lakehouses are required** for OneLake-security data preview to work (house opinion #14).
- Caps: **250 roles per item, 500 members per role**.
- **RLS-only and CLS-only roles cannot be combined** in one role.
- Warehouse also supports SQL-native **RLS / CLS / dynamic data masking / OLS** at the T-SQL layer; a Direct Lake model over a SQL-defined RLS table forces Direct-Lake-on-SQL fallback.

## Governance surfaces

- **OneLake catalog** — Explore (discover), **Govern** (posture + recommended actions for data you own), **Secure** (audit workspace + OneLake-security roles, create/edit/delete from one place). Embedded in Teams/Excel/Copilot Studio; programmatic via the Catalog Search REST API.
- **Domains / subdomains** — logically group workspaces (usually by business unit) for **data-mesh** governance; tenant settings can be **delegated** to domain admins. Domain assignment drives *consumption/discovery filtering*, not access (access still comes from roles).
- **Microsoft Purview** — catalog, lineage, sensitivity labels, DLP across the unified data estate.
- **Sensitivity labels** propagate with data through Fabric.

> Any auth/secret/PII change (service principals, OneLake-security roles, tenant settings) routes through **`ravenclaude-core/security-reviewer`** (mandatory per the marketplace convention).

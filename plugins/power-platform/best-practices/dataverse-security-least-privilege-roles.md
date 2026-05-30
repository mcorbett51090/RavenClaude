# Build security roles by copying Basic User and granting least privilege — never System Administrator "so they can work"

**Status:** Absolute rule — a role model where everyone is an admin is the absence of a security model.

**Domain:** Dataverse / Security

**Applies to:** `power-platform`

---

## Why this exists

Dataverse security is **cumulative and additive**: a user's effective access is the union of every role assigned to them (directly or via team), at the *highest* scope any of those roles grants. Two failure modes follow. First, granting `System Administrator` "so the user can do their job" gives Organization-level access to everything and silently defeats every business-unit and ownership boundary you designed — and it is invisible until an auditor or a data-leak incident finds it. Second, **building a custom role from scratch** omits the base privileges every user needs (user settings, system views, the `process`/`workflow` read needed for business rules and BPFs), producing cryptic "you don't have permission" errors that look like data bugs. Both are avoided by the same discipline: copy `Basic User`, then grant the minimum each job function needs at the *narrowest* scope that works.

## How to apply

Start from `Basic User`, raise scope one notch at a time per table, and assign roles to **teams/security groups**, not individuals.

```text
Role design loop (per job function):
1. Copy the "Basic User" role  → keeps the base privileges that prevent cryptic errors.
2. For each table the function touches, set the LOWEST scope that works:
     own records only        → User          (single circle)
     their team/BU's records → Business Unit  (filled circle)
     their BU + sub-BUs      → Parent-Child BU (double circle)
     everything              → Organization   (full circle — justify in writing)
3. Grant only the privileges used: Create/Read/Write/Delete/Append/AppendTo/Assign/Share.
4. Assign the role to an OWNER TEAM or Entra-group team — not to named users one by one.
```

Verify effective access from the **outside** — log in as a non-admin test user, not as yourself:

```http
# What roles does this user actually have (directly + via teams)?
GET /api/data/v9.2/systemusers({user-id})?$select=fullname
   &$expand=systemuserroles_association($select=name),
            teammembership_association($select=name)
```

| Scope | Icon | Grants access to | Reach for it when |
|---|---|---|---|
| **User** | single circle | Only rows the user owns | Default for any operational/transactional table |
| **Business Unit** | filled circle | Rows owned by anyone in the user's BU | Team-shared work within one org-chart node |
| **Parent-Child BU** | double circle | User's BU **and all child BUs** | Managers/regional leads over a BU subtree |
| **Organization** | full circle | All rows, every BU | Reference/config tables, or a justified all-readers case |

**Do:**
- **Copy `Basic User`** as the base for every custom role — it carries the privileges that prevent the "missing base privilege" cryptic errors.
- Grant the **lowest scope that satisfies the requirement**, per table, per privilege. Most operational tables want **User**, not Organization.
- Assign roles to **owner teams / Entra-group teams**; membership changes then flow automatically and there's one place to audit.
- Cap `System Administrator` at **2–3 people** and review role assignments quarterly.
- **Test as a regular user** — security that only an admin has confirmed is untested.

**Don't:**
- Hand out `System Administrator` (or Org-scope-everything) "so they can do their job." That is *no* security model.
- Build a role from scratch — you will omit base privileges and ship cryptic permission errors.
- Share apps/flows/records directly with named users instead of a security group/team — it doesn't scale and can't be audited.
- Confuse **license** (can the user open *any* app) and **security role** (what can they do once in). Both are required; missing either blocks access.

## Edge cases / when the rule does NOT apply

- **Column-level security (FLS) overrides role scope downward** for a single column — a user with Org-level Read on the table still won't see a secured column unless a Column Security Profile grants it. Use FLS sparingly; see `dataverse-field-level-security-sparingly.md`.
- **Sharing** intentionally grants access *above* a user's role scope for specific rows — that's the supported escape hatch for "this one record, this one user," not a substitute for a role.
- **Organization-owned tables** only honor Organization scope (no owner column), so User/BU scopes are meaningless there — a reason to pick `UserOwned` at table creation for anything needing record-level security (ownership type is permanent).
- **Hierarchy / position security** is the right tool when access must follow the reporting line rather than the BU tree — it composes with roles, it doesn't replace them.

## See also

- [`../skills/dataverse-web-api/resources/security-model.md`](../skills/dataverse-web-api/resources/security-model.md) — the 7-layer model, the 4 scopes, the 8 privileges, copy-Basic-User rule
- [`./dataverse-field-level-security-sparingly.md`](./dataverse-field-level-security-sparingly.md) — when column-level security is and isn't warranted
- [`./dataverse-access-error-is-not-a-schema-error.md`](./dataverse-access-error-is-not-a-schema-error.md) — a 403 is an access fact, not a schema fact
- [`../knowledge/dataverse-decision-trees.md`](../knowledge/dataverse-decision-trees.md) — `## Decision Tree: Security — record access mechanism (role scope vs team vs sharing)`
- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owner; flags the all-admins anti-pattern

## Provenance

Grounded in the plugin's own `skills/dataverse-web-api/resources/security-model.md` (Layer 4 role design rules: "ALWAYS copy the Basic User role and modify"; the 4 access scopes; "Limit System Administrator to 2-3"; additive-roles semantics) and the `dataverse-architect` agent anti-pattern "every user has System Administrator … you've built no security model at all." The cumulative/highest-scope union semantics are the documented Dataverse security model.

---

_Last reviewed: 2026-05-30 by `claude`_

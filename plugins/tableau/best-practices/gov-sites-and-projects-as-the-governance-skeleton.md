# Use sites for hard tenancy boundaries and projects for content governance — don't conflate them

**Status:** Pattern — sites are the tenancy boundary, projects are the governance unit; reaching for a new site when a project would do (or vice versa) is the deviation to avoid.

**Domain:** Governance / topology

**Applies to:** `tableau`

---

## Why this exists

Teams reach for a new **site** when they actually need a new **project**, and then discover users, groups, and data sources don't cross the site boundary, so they re-create everything and the "isolation" becomes a maintenance tax. A **site** is a hard tenancy boundary — separate users, groups, content, and (on Server) separate admin — appropriate when two populations must be fully isolated (different companies, regulatory separation). A **project** is the governance unit *within* a site — the container you lock, grant groups on, and hang RLS'd data sources under. Most "keep these teams apart" requirements are a **locked project per team in one shared site**, not a site per team: the teams still share a user directory and can share certified data sources where appropriate, while the locked project enforces content separation. Picking the wrong level either over-isolates (sites everywhere, nothing shareable) or under-isolates (everything in one project, no real boundary).

## How to apply

Decide the level by the question "must these populations be *fully* isolated, including users and admin?"

```
Need to separate content/teams?
  ├─ Different companies / regulatory hard isolation / separate admin
  │     → SITE per tenant   (separate users, groups, content, admin)
  └─ Same org, teams that shouldn't see each other's content
        → ONE site, a LOCKED PROJECT per team
          Site: Analytics
            ├── Project: Finance   [LOCKED]  → group "Finance-*"
            ├── Project: Sales     [LOCKED]  → group "Sales-*"
            └── Project: Shared    [LOCKED]  → certified cross-team data sources
```

**Do:**
- Use a **site** only for a genuine tenancy/regulatory boundary that must isolate users and admin.
- Use a **locked project per team** within one site for ordinary "teams shouldn't see each other's content."
- Put genuinely shared, certified data sources in a shared project both teams can read.
- Map the org's tenancy + team structure to the site/project skeleton *before* publishing content into it.

**Don't:**
- Spin up a site per team and then fight the fact that users/groups/data sources don't cross sites.
- Put every team's content in one unlocked project and call group grants "isolation."
- Move content between sites casually — it's a re-publish, not a move; plan tenancy up front.

## Edge cases / when the rule does NOT apply

- **Tableau Cloud single-site** — a Cloud deployment may be one site by design; there projects carry the entire governance load `[verify-at-build]`.
- **External-facing / customer tenancy** — multi-tenant customer isolation may justify sites *and* per-tenant RLS; design both together with security review.
- **Server vs Cloud admin scope** — site-admin capabilities differ between Server and Cloud `[verify-at-build]`; confirm before promising a tenancy model.

## See also

- [`./gov-permissions-via-locked-projects-not-per-workbook.md`](./gov-permissions-via-locked-projects-not-per-workbook.md) — how to govern *within* a project
- [`./gov-certified-data-sources-and-governance.md`](./gov-certified-data-sources-and-governance.md) — the shared certified sources that justify a shared project
- [`../knowledge/governance-embedding-decision-trees.md`](../knowledge/governance-embedding-decision-trees.md) — `## Decision Tree: Permission model`
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns this rule
- Tableau Help, "Sites" + "Projects" governance topics `[verify-at-build]`

## Provenance

Extends the `tableau-admin` discipline #1 ("Govern at the project, not the content") to the site/project topology decision. Grounded in Tableau's site-as-tenancy / project-as-governance model — re-verify Cloud-vs-Server site-admin scope and Cloud single-site behavior against current Tableau Help.

---

_Last reviewed: 2026-05-30 by `claude`_

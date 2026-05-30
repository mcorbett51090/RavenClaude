# Grant permissions to groups on locked projects, not workbook-by-workbook

**Status:** Pattern — the locked-project + group-grant model is the strong default for any governed site; a per-content override is the deviation you justify and time-box.

**Domain:** Governance / access control

**Applies to:** `tableau`

---

## Why this exists

A Tableau permission you can't read off a single grant matrix is a permission you can't audit. When authors set permissions per workbook, the same user ends up with different effective access on two workbooks in the same project, "who can see this?" becomes a per-content investigation, and a leak hides in an override nobody remembers making. The locked-project model collapses this: permissions are granted to **groups** on a **locked project**, and that project rule becomes the single source of truth for every workbook and data source inside it. "Locked" stops authors from silently overriding at the content level — so the grant matrix on the project *is* the access model. Grant to groups (not named users) so membership, not permission edits, is what changes who sees what.

## How to apply

Lock the project, grant a group at the project level, and let every content item inherit. Build (or audit) against a written grant matrix.

```
Site: Analytics
└── Project: Finance  [Content permissions: LOCKED]
    ├── Group "Finance-Viewers"   → Viewer    (View, Download Summary)
    ├── Group "Finance-Explorers" → Explorer  (+ Web Edit, Save a Copy)
    └── Group "Finance-Leads"     → Project Leader (manage content + permissions)
    Default for all other groups: NO grant  →  deny by omission

# Same shape via the REST API (grant a CAPABILITY to a GROUP on the PROJECT):
PUT /api/3.x/sites/{site-id}/projects/{project-id}/permissions
{
  "permissions": {
    "granteeCapabilities": [{
      "group": { "id": "{finance-viewers-group-id}" },
      "capabilities": { "capability": [
        { "name": "Read",            "mode": "Allow" },
        { "name": "ViewUnderlyingData", "mode": "Deny" }
      ]}
    }]
  }
}
```

**Do:**
- Set the project's content permissions to **Locked** so the project rule governs every item.
- Grant **groups**, never named users — change membership, not permissions, to change access.
- Start from **deny by omission**: no grant = no access; never "everyone can see it, then subtract."
- Keep a written grant matrix (group × project × role) as the reviewable source of truth.

**Don't:**
- Set permissions per workbook in a governed project — that fragments the model and defeats audit.
- Grant `All Users` / a broad group at the site root and then carve exceptions downward.
- Use a customizable (unlocked) project for content that's a real boundary.

## Edge cases / when the rule does NOT apply

- **Personal sandboxes** — exploratory, owner-only content with no shared audience doesn't need a grant matrix; it graduates into a locked project when it gets an audience.
- **A genuine single-workbook divergence** — occasionally one item truly needs narrower/wider access than its project; allow it as a **documented, time-boxed exception** with a review date, not as the default.
- **Nested projects** — a child project can lock independently; decide deliberately whether it inherits or overrides the parent's rule.

## See also

- [`./gov-certified-data-sources-and-governance.md`](./gov-certified-data-sources-and-governance.md) — the data-source half of the governed-content story
- [`./gov-rls-as-a-data-policy-not-a-hidden-filter.md`](./gov-rls-as-a-data-policy-not-a-hidden-filter.md) — row-level access is a *different* control from content access
- [`../knowledge/governance-embedding-decision-trees.md`](../knowledge/governance-embedding-decision-trees.md) — `## Decision Tree: Permission model — locked project vs per-content grants`
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns this rule
- Tableau Help, "Set permissions" + "Lock content permissions to the project" `[verify-at-build]`

## Provenance

Codifies the `tableau-admin` discipline #1 ("Govern at the project, not the content") from [`../agents/tableau-admin.md`](../agents/tableau-admin.md) and the constitution's deny-by-omission posture. Grounded in the Tableau project/group permission model (locked vs customizable projects) — re-verify capability names and lock semantics against current Tableau Help before quoting to a client.

---

_Last reviewed: 2026-05-30 by `claude`_

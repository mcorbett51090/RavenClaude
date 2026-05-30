# Pin one publisher prefix you control, per repo

**Status:** Pattern — strong default. Mismatched or default (`cr_`, `new_`) prefixes across solutions in one repo are an ALM nightmare to merge and make customizations untraceable.

**Domain:** ALM

**Applies to:** `power-platform`

---

## Why this exists

Every solution component carries a **publisher prefix** — the few characters in front of every schema name (`mc_partner_id`). The prefix comes from the solution's publisher, and the default that the platform hands every new maker is `cr_` (or `new_`). Two problems follow from leaving it default. First, **traceability**: when every org's components are `cr_`-prefixed, you cannot tell at a glance whose customization a column belongs to, and two solutions that both used `cr_` will collide on schema names when they meet in one environment. Second, **merge pain**: if the solutions in a single repo were authored under different publishers, their components don't share a namespace, cross-solution references get awkward, and consolidating them later means renaming schema (which is effectively re-creating the components). Pick one prefix you control, register it as your publisher, and use it for every solution in the repo.

## How to apply

Create a publisher with a deliberate, org-specific prefix up front; create every solution under it. Set this before the first component exists — changing a prefix after the fact means re-creating schema.

```bash
# Create the publisher once (prefix you control — NOT cr_ / new_)
pac org list   # confirm you're pointed at the right dev org
# In the maker portal or via the Dataverse Web API, create a publisher:
#   Display name: "Raven Power"   Prefix: "rvn"   (→ schema names become rvn_...)

# Create every solution under that publisher
pac solution init --publisher-name "Raven Power" --publisher-prefix rvn
```

A registered publisher + consistent prefix means every component reads `rvn_partner_id`, `rvn_ApprovalFlow`, `rvn_PartnerSiteUrl` — instantly attributable and collision-free across the repo.

**Do:**
- Choose a short, org-specific prefix (`rvn`, `mc`, your org's initials) and document it in the repo README.
- Use the **same** publisher for every solution in the repo so they share a namespace.
- Set the prefix before authoring the first component — it's cheap now, expensive later.

**Don't:**
- Ship anything real under the default `cr_` / `new_` prefix.
- Mix publishers across solutions that live in (or will merge into) one repo.
- Try to "rename" a prefix on existing components — Dataverse won't rename schema; you'd re-create everything.

## Edge cases / when the rule does NOT apply

- **Multiple distinct products** legitimately built by the same team may each warrant their own publisher/prefix — but each *repo* (or product boundary) still pins exactly one. The rule is one prefix per namespace, not one prefix per org forever.
- **Consuming a third-party managed solution** brings its publisher's prefix along; you don't (and can't) re-prefix its components — your customizations layered on top still use *your* prefix.
- **Throwaway dev/spike orgs** can stay on the default prefix; the rule bites the moment a solution is on a promotion path.

## See also

- [`./alm-source-control-the-unpacked-solution-tree.md`](./alm-source-control-the-unpacked-solution-tree.md) — the tree where prefixed schema names show up in diffs
- [`../agents/solution-alm-engineer.md`](../agents/solution-alm-engineer.md) — "Pin the publisher prefix per repo"
- [`../CLAUDE.md`](../CLAUDE.md) §3 #5 — publisher prefix you control

## Provenance

Codifies house opinion §3 #5 ("Publisher prefix you control") and the `solution-alm-engineer` opinion "Pin the publisher prefix per repo." The `power-platform` hook `check-house-opinions.sh` mechanically flags default prefixes (`cr`, `crXXX`, `new`) in `solution.xml` / `customizations.xml`. `pac solution init --publisher-name/--publisher-prefix` verified against the Microsoft Learn `pac solution` reference, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_

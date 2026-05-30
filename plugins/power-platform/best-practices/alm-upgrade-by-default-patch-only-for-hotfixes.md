# Upgrade by default; patch only for hotfixes

**Status:** Pattern — strong default. Reaching for patches as the routine release vehicle stacks solution layers in PROD and leaves deleted components behind.

**Domain:** ALM

**Applies to:** `power-platform`

---

## Why this exists

When you import a new version of a managed solution, you choose how it lands. **Upgrade** (stage-and-upgrade, or upgrade) replaces the solution wholesale at a new version: components removed in the new version are actually *deleted* from the target, and the layer stack stays clean. **Patch** applies a small incremental change *on top of* an already-deployed solution without replacing it — fast, but it does **not** delete removed components, and patches accumulate as additional layers over time. A team that patches every release ends up with a PROD environment carrying a tall stack of patch layers, orphaned components that were "removed" in source but never deleted in target, and a layering picture nobody can reason about. The discipline: **upgrade is the default release path; patches are a deliberate tool for shipping a single hotfix between full releases.**

## How to apply

Use the upgrade path (`--import-as-holding` then apply, or the in-product *Upgrade* option) for regular releases. Reserve patches for an urgent one-component fix that can't wait for the next full release.

```bash
# DEFAULT: full upgrade — clean replacement, deleted components actually removed.
# Stage-and-upgrade imports to a holding solution, then promotes (deletes removed components):
pac solution import --path ./out/MySolution_managed_${BUILD_SHA}.zip \
    --import-as-holding         # stage as holding...
pac solution upgrade --solution-name MySolution   # ...then apply the upgrade

# HOTFIX ONLY: a patch carries just the changed component(s) on top of the deployed base.
# Author the patch against the deployed version, ship it, then roll it into the next
# full upgrade so the patch layer doesn't live forever.
```

**Do:**
- Default to **upgrade** for quarterly/regular releases — it cleans up deleted components and keeps the layer stack flat.
- Use a **patch** for a genuine hotfix to one column/flow that can't wait, and **roll the patch into the next full release** so the layer is reclaimed.
- Verify after an upgrade that components you removed in source are gone in target (the thing patches silently *don't* do).

**Don't:**
- Patch every release because it's faster — you're building an un-reasonable-about layer stack in PROD.
- Leave hotfix patches stranded as permanent layers; fold them into the next upgrade.
- Use a patch to *remove* a component — patches add/modify; deletions need an upgrade.

## Edge cases / when the rule does NOT apply

- **Segmented solutions** (only some columns of an entity) are a related-but-distinct tool for shipping a narrow slice; like patches they're situational, not the routine vehicle (see `solution-alm-engineer`).
- **Stage-for-upgrade vs upgrade**: staging (holding solution) lets you import now and apply the delete-bearing upgrade later in a maintenance window — still the upgrade path, just split in time.
- **First-ever install** of a solution into a clean env is neither patch nor upgrade — it's a plain import; the patch/upgrade distinction only applies to *subsequent* versions.

## See also

- [`./managed-vs-unmanaged-solution-discipline.md`](./managed-vs-unmanaged-solution-discipline.md) — managed state is the precondition for clean upgrades
- [`./alm-one-build-artifact-promoted-unchanged.md`](./alm-one-build-artifact-promoted-unchanged.md) — the artifact an upgrade promotes
- [`../agents/solution-alm-engineer.md`](../agents/solution-alm-engineer.md) — "Patches and segmented solutions are situational, not default"
- [`../skills/alm-pipeline-design/SKILL.md`](../skills/alm-pipeline-design/SKILL.md) §7 — patch vs upgrade

## Provenance

Codifies the `solution-alm-engineer` opinion ("Patches and segmented solutions are situational... don't reach for them as a routine release vehicle") and `alm-pipeline-design` skill §7 ("hotfixes patch; quarterly releases upgrade"). `pac solution import --import-as-holding` and `pac solution upgrade` verified against the Microsoft Learn `pac solution` reference, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_

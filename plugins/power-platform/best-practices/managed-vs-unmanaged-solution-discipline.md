# Managed in test and prod, unmanaged only in dev

**Status:** Absolute rule — violations build an invisible unmanaged layer that *will* cause "why didn't my fix flow through" later.

**Domain:** Solution mechanics / ALM

**Applies to:** `power-platform`

---

## Why this exists

A Dataverse solution carries a managed *or* unmanaged state, and that state decides whether your future edits flow through cleanly. The moment someone customizes a **managed** solution directly in a downstream environment, Dataverse creates an **active unmanaged layer** on top. That layer is invisible in the normal solution view, it silently wins over the managed component beneath it, and it means a corrected component shipped from dev later **does not take effect** — the unmanaged layer keeps shadowing it. Teams lose hours chasing "I fixed it in dev, why is prod still broken?" when the answer is an unmanaged layer nobody remembers creating.

## How to apply

Export **unmanaged** from dev (your authoring environment); import **managed** into test and prod. The unmanaged tree is what you source-control; the managed `.zip` is what you ship.

```bash
# In DEV (authoring): export unmanaged, unpack the tree, commit it
pac solution export --name MySolution --managed false --path ./out/MySolution_unmanaged.zip
pac solution unpack --zipfile ./out/MySolution_unmanaged.zip --folder ./src/MySolution --packagetype Both

# For the release: build the MANAGED zip in CI and import THAT to test/prod
pac solution export --name MySolution --managed true --path ./out/MySolution_managed.zip
pac solution import --path ./out/MySolution_managed.zip   # against the test/prod auth profile
```

**Do:**
- Keep one authoring environment (dev) as the only place unmanaged components exist.
- Build the managed artifact in CI from the committed unpacked tree, not by hand in the portal.
- If you must remove an unmanaged customization, remove the **layer** (delete the unmanaged customization in its source env and re-export) — re-importing the managed solution will *not* clear it.

**Don't:**
- Edit a managed component in test/prod "just this once."
- Hand-upload a portal `.zip` export straight to prod — no reproducibility, and you can't tell managed from unmanaged at a glance.

## Edge cases / when the rule does NOT apply

- **A single dedicated dev environment per solution** is the assumption. Multi-dev-environment shops may have more than one unmanaged authoring env, but each component still has exactly one unmanaged home.
- **Hotfix-to-one-column** scenarios are the legitimate use of **patches / segmented solutions** — a deliberate, documented tool, not the routine release vehicle (see `solution-alm-engineer`).
- **Trial / throwaway POC environments** that will never be promoted can stay unmanaged end-to-end; the rule is about anything on a promotion path.

## See also

- [`../agents/solution-alm-engineer.md`](../agents/solution-alm-engineer.md) — owns export/import, the active-layer trap, and the fresh-import smoke test
- [`../knowledge/managed-environments-and-governance-2026.md`](../knowledge/managed-environments-and-governance-2026.md) — environment-tier strategy that this discipline sits inside
- [`../skills/alm-pipeline-design/SKILL.md`](../skills/alm-pipeline-design/SKILL.md) — dev/test/prod pipeline that automates the managed-import path

## Provenance

Codifies house opinion #4 ("Managed in test and prod. Unmanaged only in dev.") from [`../CLAUDE.md`](../CLAUDE.md) §3 and the matching `solution-alm-engineer` opinion. The "invisible unmanaged layer" failure mode is one of the plugin's named anti-patterns (§4).

---

_Last reviewed: 2026-05-30 by `claude`_

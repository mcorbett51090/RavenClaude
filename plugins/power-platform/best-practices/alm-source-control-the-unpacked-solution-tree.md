# Source-control the unpacked solution tree, never the .zip

**Status:** Absolute rule — a `.zip` in git is opaque, un-reviewable, and merge-hostile. Violations defeat the entire point of putting a solution under source control.

**Domain:** ALM

**Applies to:** `power-platform`

---

## Why this exists

A solution `.zip` is a build artifact: a compressed binary blob. Commit it and your "source control" is a sequence of binary snapshots no one can diff, review, or merge. Two makers touching the same solution produce two incompatible `.zip`s and git can only say "binary files differ." The whole value of source control — reviewable diffs, blame, three-way merge, PR review of a *specific flow's* trigger condition — evaporates. The unpacked tree (`pac solution unpack`) is text-ish: `solution.xml`, `customizations.xml`, per-component folders for Entities, Workflows, CanvasApps, WebResources, AppModules. That is what a human and a reviewer read. The `.zip` is what CI builds *from* that tree on the way to an import.

## How to apply

Unpack on the way in; pack in CI on the way out. Commit the tree, `.gitignore` the build output.

```bash
# Bootstrap from an existing dev environment (first time only)
pac solution clone --name MySolution            # pulls + unpacks into ./MySolution
# OR unpack an existing export:
pac solution export --name MySolution --managed false --path ./out/MySolution.zip
pac solution unpack --zipfile ./out/MySolution.zip --folder ./src/MySolution --packagetype Both

git add ./src/MySolution            # commit the TREE
git commit -m "MySolution: add lookup column to mc_partner"

# CI builds the artifact FROM the tree — never committed:
pac solution pack --folder ./src/MySolution --zipfile ./out/MySolution_managed.zip --packagetype Managed
```

`.gitignore` essentials:

```gitignore
bin/
obj/
*.zip
*.user
node_modules/
*.msapp          # canvas binary — unpack to *.fx.yaml via pac canvas
```

**Do:**
- Use `pac solution unpack --packagetype Both` so the tree carries both managed and unmanaged metadata, and review the diff before every PR.
- Read flow `definition.json`, canvas `*.fx.yaml`, and entity ribbon XML diffs in review — that's where the bugs hide.
- Keep `pac solution sync` in your loop to re-pull dev changes into the existing tree rather than re-cloning.

**Don't:**
- `git add MySolution.zip`. Ever.
- Hand-edit the packed `.zip` and re-commit it — the tree is the source of truth, the zip is derived.

## Edge cases / when the rule does NOT apply

- **Throwaway / spike solutions** never destined for promotion don't need a tree — but the moment one is on a release path, unpack it.
- **Canvas `.msapp`** is binary inside the solution; `pac solution unpack` extracts canvas app source as `*.fx.yaml` when `--processCanvasApps` is honored by your CLI version — verify your `pac --version` produces the YAML, not a raw `.msapp`, before relying on canvas diffs. [unverified — confirm against your installed pac CLI]
- **Power BI artifacts** are not Dataverse-solution components and are not unpacked by `pac` — they use PBIP for git (see `power-bi-engineer`).

## See also

- [`./managed-vs-unmanaged-solution-discipline.md`](./managed-vs-unmanaged-solution-discipline.md) — what *state* you export/import along the tree
- [`./alm-one-build-artifact-promoted-unchanged.md`](./alm-one-build-artifact-promoted-unchanged.md) — the packed managed zip is built once and promoted byte-for-byte
- [`../agents/solution-alm-engineer.md`](../agents/solution-alm-engineer.md) — owns the pac CLI and the unpacked-tree layout
- [`../skills/alm-pipeline-design/SKILL.md`](../skills/alm-pipeline-design/SKILL.md) §1 — source-control discipline

## Provenance

Codifies house opinion §3 #12 ("Source control the unpacked solution") from [`../CLAUDE.md`](../CLAUDE.md), the `solution-alm-engineer` opinion ("Source control = unpacked solution tree, not the `.zip`"), and the `alm-pipeline-design` skill Core Principle #2. `pac solution clone/unpack/pack/sync` verbs verified against Microsoft Learn `pac solution` reference (retrieved 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_

# One managed artifact, built once, promoted unchanged to every stage

**Status:** Absolute rule — if TEST and PROD run different `.zip` bytes, TEST proved nothing about PROD. Re-packing per stage reintroduces exactly the variance the pipeline exists to remove.

**Domain:** ALM

**Applies to:** `power-platform`

---

## Why this exists

The whole point of a dev → test → prod pipeline is to validate *the thing you will ship* before you ship it. If the pipeline exports unmanaged from dev for the TEST import and exports *again* for the PROD import, the two managed solutions can differ — a dev change landed between exports, a GUID churned, a component was published in one export and not the other. TEST validated artifact A; PROD received artifact B. Every behavioral difference between them is an untested change reaching production. The discipline that closes this gap: build the managed artifact **once** (in a dedicated build step), version it by commit SHA, publish it as a pipeline artifact, and import *that exact file* into TEST, UAT, and PROD. Config differences between environments belong in environment variables and connection references — data that travels alongside the artifact — never in different bytes.

## How to apply

Export-to-managed happens once. Downstream stages import the published artifact; they never re-export.

```bash
# BUILD stage (runs once): pack unmanaged from the committed tree, import to a clean
# build env, export the MANAGED artifact, publish it keyed by commit SHA.
pac auth select --name build
pac solution pack   --folder ./src/MySolution --zipfile ./out/MySolution.zip --packagetype Unmanaged
pac solution import --path ./out/MySolution.zip
pac solution export --name MySolution --managed true --path ./out/MySolution_managed_${BUILD_SHA}.zip
# → publish ./out/MySolution_managed_${BUILD_SHA}.zip as the immutable build artifact

# TEST / UAT / PROD stages: import THE SAME published file. Only the settings file changes.
pac auth select --name test
pac solution import --path ./out/MySolution_managed_${BUILD_SHA}.zip --settings-file ./deploymentSettings-test.json
pac auth select --name prod
pac solution import --path ./out/MySolution_managed_${BUILD_SHA}.zip --settings-file ./deploymentSettings-prod.json
```

**Do:**
- Version the artifact by commit SHA (and/or build number) so you can prove which bytes are in each environment.
- Vary only the `--settings-file` per stage — env vars and connection refs carry the per-environment config.
- Treat the published artifact as immutable; a fix means a new build with a new SHA, promoted from the top.

**Don't:**
- Re-export or re-pack between TEST and PROD.
- Edit the `.zip` between stages "to fix one thing."
- Branch-per-environment so each branch builds its own artifact — that is the same anti-pattern wearing a git hat.

## Edge cases / when the rule does NOT apply

- **In-product Power Platform Pipelines** enforce this structurally — the solution is exported once at deploy-request time and the identical artifact passes each stage in order (verified, MS Learn pipelines FAQ, 2026-05-30). You get one-artifact promotion for free.
- **A genuine rebuild** (the source tree changed) is a *new* artifact with a new SHA, promoted from the top of the pipeline — not the same release re-packed.
- **Patches/hotfixes** are their own artifact built once and promoted; the rule applies within a patch's promotion just as within a full release's.

## See also

- [`./alm-pipeline-stages-dev-test-prod.md`](./alm-pipeline-stages-dev-test-prod.md) — the staged pipeline this artifact moves through
- [`./alm-source-control-the-unpacked-solution-tree.md`](./alm-source-control-the-unpacked-solution-tree.md) — the tree the artifact is built *from*
- [`./alm-fresh-import-smoke-test-before-release.md`](./alm-fresh-import-smoke-test-before-release.md) — proving the one artifact imports cleanly before release
- [`../skills/alm-pipeline-design/SKILL.md`](../skills/alm-pipeline-design/SKILL.md) Core Principle #8 — "one build artifact, promoted unchanged"

## Provenance

Codifies `alm-pipeline-design` skill Core Principle #8 ("One build artifact, promoted unchanged") and the skill's anti-pattern "per-stage rebuilds — TEST and PROD running different .zip bytes." Pipelines' structural single-artifact enforcement verified against Microsoft Learn (pipelines FAQ); `pac solution pack/import/export --managed` flags verified against the `pac solution` reference, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_

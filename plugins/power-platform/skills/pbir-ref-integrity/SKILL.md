---
name: pbir-ref-integrity
description: "Report-wide referential-integrity validator for a PBIR Enhanced report's `definition/` tree. Deterministic, stdlib-only `check_refs.py` that catches DANGLING cross-file references — bookmarks pointing at deleted pages/visuals, `visualInteractions` naming visuals that no longer exist, a `pageOrder` that omits/invents/duplicates a page, an `activePageName`/`activeSection` that names a missing page, and report-wide visual-name collisions. Mimics the referential-integrity half of pbir-utils `validate`/`sanitize` and pbir.tools `validate`. Complements (does NOT duplicate) ravenclaude-core's single-page `pbir-layout-engine`. Owned by `power-bi-engineer`."
---

# Skill: pbir-ref-integrity

## What this is

A **runnable, deterministic validator** — [`check_refs.py`](check_refs.py) — that answers the question single-page linting structurally **cannot**: *do the cross-file references across a whole PBIR Enhanced report resolve?* Bookmarks, visual interactions, page order, and the active page all reference pages and visuals **by name across files**; when a page or visual is deleted or renamed, those references go stale. PBIR reports with dangling references **deploy clean** (no schema error) and then misbehave at render time — a bookmark jumps nowhere, an interaction silently no-ops, the report opens on the wrong page. This is the same silent-failure class the plugin's PBIR knowledge bank keeps cataloguing (see [`knowledge/pbir-enhanced-report-loading.md`](../../knowledge/pbir-enhanced-report-loading.md)).

It is **not** a layout linter and **not** a schema linter — those are ravenclaude-core's [`pbir-layout-engine`](../../../ravenclaude-core/skills/pbir-layout-engine/SKILL.md) (geometry + per-visual `visualType`/`displayOption` enums, single page). This validator is the **report-wide referential** complement: run both for full coverage.

## Why it exists — mimicked from pbir-cli (researched 2026-06-08)

Two community PBIR CLIs ship a `validate` command whose most valuable job is referential integrity:

- **akhilannan/pbir-utils** — `validate` (checks reports against sanitizer checks) and `sanitize`, which *"removes invalid bookmarks (referencing deleted pages/visuals) and unreferenced bookmarks"*, plus `set-page-order` / `set-active-page`. (<https://akhilannan.github.io/pbir-utils/cli/>, retrieved 2026-06-08)
- **maxanatsko/pbir.tools** — `validate` (*"run `pbir validate` before you consider the edit finished"*) over the `Report/Page/Visual` path model. (<https://github.com/maxanatsko/pbir.tools/blob/main/cli/README.md>, retrieved 2026-06-08)

We **re-implement the idea** (deterministic referential validation over the PBIR folder model) in our own stdlib-only code, against the PBIR file facts in [`knowledge/pbir-enhanced-reference.md`](../../knowledge/pbir-enhanced-reference.md). We do **not** vendor, install, or shell out to either tool — and we deliberately stop at **detection** (report findings), not auto-`sanitize` mutation, because deleting a bookmark/interaction is a judgment call the `power-bi-engineer` should make, not a silent script (consistent with the marketplace's "tee up the human-only residue" discipline).

## The six checks

| Check | What it validates | Default severity |
|---|---|---|
| `ref-1` | Each bookmark's target page exists on disk | error |
| `ref-2` | Each visual a bookmark pins state for still exists on that page | warning |
| `ref-3` | `page.json` `visualInteractions` `source`/`target` are visuals on that same page | error |
| `ref-4` | `pages.json` `pageOrder` is a permutation of the on-disk page ids (no missing / invented / duplicate) | error |
| `ref-5` | `pages.json` `activePageName` **and** each bookmark's `activeSection` name an existing page | error |
| `ref-6` | A visual `name` is unique across the whole report (PBIR requires report-wide uniqueness) | error |

`ref-2` is a **warning** (a dangling pinned-visual leaves the rest of the bookmark usable); the others are **errors** (they break navigation, ordering, or identity). A torn/unparseable definition file yields a `parse` **error** finding for that file and degrades only that reference class — never a crash.

## PBIR folder model it reads

```
<Report>.Report/definition/
  report.json
  pages/
    pages.json                 { pageOrder: [...], activePageName }
    <pageId>/
      page.json                { name, displayName, visualInteractions[], ... }
      visuals/<visualId>/visual.json   { name, position, visual{...} }
  bookmarks/
    <bookmarkId>.bookmark.json { displayName, explorationState{ activeSection, sections } }
```

Point the validator at either the `*.Report` folder or its `definition/` directory. Every reader is **defensive**: a missing `pages.json` (older trees) skips `ref-4`/`ref-5`-page; a renamed `explorationState` key skips that bookmark's visual checks rather than failing the run. The validator reports what it can resolve; it never invents a finding.

## CLI contract

```text
python3 plugins/power-platform/skills/pbir-ref-integrity/check_refs.py [OPTIONS] <report-root>
```

`<report-root>` MUST NOT contain `..` and MUST resolve inside the repo root (else exit 2 — same purity contract as `lint.py`).

| Option | Effect |
|---|---|
| `--format text\|json` | output format (default `text`); JSON envelope is `{schema_version, validator_version, report_root, exit_code, summary, findings[]}` |
| `--strict` | exit nonzero on any finding ≥ `warning` (default: only `error` sets a nonzero exit) |
| `--list-checks` / `--version` | print the checks / pinned version and exit |

**Exit codes:** `0` clean (or info only) · `1` an error finding (or warning under `--strict`) · `2` I/O / parse / path-rejection.

## When `power-bi-engineer` runs it

- **Before declaring a PBIR edit done** — after any page/visual delete or rename, before commit/deploy. This is the report-wide counterpart to running `pbir-layout-engine` on the page you touched. Mirrors pbir.tools' *"run validate before you consider the edit finished."*
- **When triaging a "navigation/bookmark does nothing" or "report opens on the wrong page" report** — these are the classic dangling-reference symptoms.
- **In a PR pipeline for PBIP repos** — a deterministic, dependency-free gate (no Power BI Desktop, no network) that fails the build on a dangling reference, complementing the layout linter.

## Output Contract

The machine output is the `--format json` envelope above (snake_case keys, `exit_code` mirroring the process exit). When the `power-bi-engineer` reports a validation run as part of a handoff, it ends with the cross-plugin Structured Output JSON block per [`../../../ravenclaude-core/skills/structured-output/SKILL.md`](../../../ravenclaude-core/skills/structured-output/SKILL.md).

## Scope boundary

Detection only — this skill reports dangling references; it does **not** mutate the report (no auto-`sanitize`). Layout arithmetic + per-visual schema validity belong to ravenclaude-core's `pbir-layout-engine`; *authoring* a new `visual.json`/`page.json` belongs to [`knowledge/pbir-enhanced-reference.md`](../../knowledge/pbir-enhanced-reference.md); *debugging an infinite-spinner deploy* belongs to [`knowledge/pbir-enhanced-report-loading.md`](../../knowledge/pbir-enhanced-report-loading.md).

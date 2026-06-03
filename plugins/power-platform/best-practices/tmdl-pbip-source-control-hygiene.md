# Commit TMDL/PBIP as the text source, never the binary .pbix

**Status:** Absolute rule — a `.pbix` in git is opaque, un-diffable, and merge-hostile. Violations defeat the purpose of source control for Power BI the same way committing a solution `.zip` defeats it for Dataverse. The unpacked PBIP folder (TMDL model + PBIR report JSON) is the source of truth; the `.pbix` is a build artifact derived from it.

**Domain:** Power BI / Fabric ALM, source control

**Applies to:** `power-bi-engineer`, `solution-alm-engineer`, any agent or developer setting up a Power BI repository

---

## Why this exists

A `.pbix` file is a ZIP-compressed binary container. Put it under git and:

- Every save in Power BI Desktop produces a new binary that git stores as a full object — the diff is "Binary files differ."
- PR review is impossible: a reviewer cannot see which measure changed, which visual was added, or whether an RLS role was modified.
- Three-way merge is impossible: two developers touching the same report produce two incompatible `.pbix` files and git cannot resolve the conflict.
- A CI pipeline cannot validate model quality, run BPA, or lint the DAX — it can only store the blob.

The PBIP folder format (Power BI Project, released by Microsoft — source: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview, retrieved 2026-06-03) unpacks a Power BI report and semantic model into a text tree:

```
MyReport.Report/
  definition/
    report.json
    pages/
      Overview/
        page.json
        visuals/
          <visual-name>/
            visual.json
MyModel.SemanticModel/
  definition/
    model.bim            (or TMDL folder)
    tables/
      Sales.tmdl
      Date.tmdl
    relationships.tmdl
    roles.tmdl
```

That tree is what a human reads in PR review. The `.pbix` is what CI builds *from* that tree on the way to a publish step.

---

## How to apply

### Enable PBIP in Power BI Desktop

In Power BI Desktop → Options and settings → Options → Preview features → enable **Power BI Project (.pbip) format**. After enabling, use File → Save as → Power BI Project (`.pbip`) to save as the unpacked folder. `[unverified — training knowledge: confirm current menu location against your Desktop version]`

Alternatively, open an existing `.pbix` and save it as `.pbip` once; thereafter Desktop will save to the folder automatically.

### Commit the folder tree

```bash
# Add the PBIP folder to git — NOT the .pbix
git add MyReport.Report/
git add MyModel.SemanticModel/
git commit -m "MyReport: add YTD Revenue measure and Overview page"

# .gitignore — exclude binary artifacts
echo "*.pbix" >> .gitignore
echo "*.pbip"  # The .pbip entry-point file is a small JSON pointer — commit it
```

`.gitignore` essentials for a Power BI repo:

```gitignore
*.pbix
.pbix.bak
LocalSettings.json
```

Do NOT ignore `.pbip` (the project entry-point file) or any `.tmdl`, `.json`, or `.bim` files — those are the source.

### CI pipeline pattern

```bash
# 1. BPA: validate model quality (Tabular Editor CLI)
#    [unverified — confirm CLI flags against your TE version]
TabularEditor.exe "MyModel.SemanticModel/definition" -BPA rules.json -ErrorOnWarning

# 2. Lint: prettier check on JSON files
npx prettier --check "MyReport.Report/definition/**/*.json"

# 3. Publish: use `fab` CLI to deploy to a Fabric workspace
#    [unverified — confirm exact fab syntax against current release]
fab workspace publish --source "MyModel.SemanticModel" --workspace "Dev Workspace"
fab workspace publish --source "MyReport.Report" --workspace "Dev Workspace"
```

### Roundtrip: fetch from service back to local

```bash
# Pull workspace item back to local file system (fab CLI)
# [unverified — confirm syntax against current fab CLI release]
fab workspace get --item "MyModel" --workspace "Dev Workspace" --output "MyModel.SemanticModel"
```

---

## The Windows long-path (MAX_PATH 260) gotcha

**This is the most common silent failure for Power BI PBIP repos on Windows.** Windows has a legacy maximum path length of **260 characters** (`MAX_PATH`). PBIP and TMDL folder trees generate deeply nested paths — a report with many pages and many visuals produces paths like:

```
MyReport.Report\definition\pages\SalesOverviewByRegionAndProduct\visuals\clusteredBarChartRevenue2023\visual.json
```

On a PBIP repo cloned to a deep working-tree path (e.g., `C:\Users\username\Documents\Projects\CompanyName\FiscalYear2026\Reports\MyReport.Report\...`), the full path can exceed 260 characters. The result: **`git clone` fails silently on those files**, writing some files and skipping others with no error to the user, producing a corrupt checkout.

**Fix — one of three approaches:**

**Option 1 (recommended): enable Windows long-path support via git config**

```bash
git config --system core.longpaths true
```

Run this once, as Administrator, on the Windows machine where the repo will be cloned. This instructs git to use extended-length paths (up to 32,767 characters) via Windows' `\\?\` path prefix. Requires Windows 10 version 1607 or later. Source: 260-character MAX_PATH is a documented Windows legacy limit (`[unverified — training knowledge: the 260-char limit is a well-known Windows filesystem fact; verify registry approach below against current Windows version docs]`).

**Option 2: enable via Windows registry (applies system-wide to all applications)**

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem
LongPathsEnabled = 1  (DWORD)
```

Requires a reboot. Applies to all Win32 applications, not just git. Some corporate group policy objects reset this setting — check with IT before relying on it.

**Option 3: keep the working-tree root shallow**

Clone the repo to a short root path: `C:\src\` or `D:\repos\` rather than a deeply nested user home directory. This does not fix MAX_PATH — it only delays the problem as report/page/visual names grow.

**Recommended:** use Option 1 (git config) and Option 3 (shallow root) together. Option 1 is the authoritative fix; Option 3 is cheap defense.

**In CI (Linux/macOS):** this issue does not occur. Linux and macOS do not have a 260-character path limit. The problem is Windows-only. Document it in your repo's `README` so Windows contributors know to run the git config step on first clone.

---

## Do

- Enable PBIP format in Power BI Desktop and save all reports as `.pbip` from the first commit.
- Commit the entire `*.Report/` and `*.SemanticModel/` folder trees.
- Add `*.pbix` to `.gitignore`. The `.pbix` is a build artifact, not source.
- Run BPA in CI on every PR touching `.tmdl` files — this is the cross-tool backstop for model quality (including the measure-metadata triad in [`enforce-measure-metadata.md`](./enforce-measure-metadata.md)).
- On Windows dev machines: run `git config --system core.longpaths true` as Administrator before first clone, and clone to a short root path (`C:\src\`).
- Document the `core.longpaths` requirement in the repo's onboarding instructions so it is run before problems appear.
- Cross-link your repo's PBIP work to your ALM pipeline: `fab` CLI deploys the PBIP source; the `.pbix` artifact (if needed for downstream consumers) is built by CI.

## Don't

- `git add *.pbix`. Ever. See [`alm-source-control-the-unpacked-solution-tree.md`](./alm-source-control-the-unpacked-solution-tree.md) for the same principle applied to Dataverse solution `.zip` files — the rationale is identical.
- Commit `LocalSettings.json` — this is the Power BI Desktop user-local state file (selected page, expanded nodes). It is not source; it will conflict between developers.
- Assume the long-path issue won't affect your repo. PBIP paths are long by design (visual folder names mirror the visual's `name` property, which can be a 20-character hash). The only question is how soon the limit is hit.
- Mix PBIP and binary `.pbix` in the same repo (e.g., some reports as PBIP, some as `.pbix`). It creates an inconsistent review experience and CI cannot validate the binary files.

---

## Relationship to the Dataverse ALM rule

The principle is identical to [`alm-source-control-the-unpacked-solution-tree.md`](./alm-source-control-the-unpacked-solution-tree.md): the binary container (`.pbix` for Power BI, `.zip` for Dataverse solutions) is always a derived build artifact; the unpacked text tree is always the source of truth. The specific formats differ — PBIP/TMDL vs. `solution.xml`/`customizations.xml` — but the ALM contract is the same.

---

## See also

- [`alm-source-control-the-unpacked-solution-tree.md`](./alm-source-control-the-unpacked-solution-tree.md) — the Dataverse-solution parallel rule; the rationale in §"Why this exists" is directly analogous
- [`enforce-measure-metadata.md`](./enforce-measure-metadata.md) — the companion rule on measure metadata; CI enforces it on the TMDL source committed via this rule
- [`../knowledge/power-bi-fabric-agentic-toolchain-2026.md`](../knowledge/power-bi-fabric-agentic-toolchain-2026.md) — the toolchain map (TMDL, PBIP, PBIR, `fab`, Tabular Editor, semantic-link-labs)
- [`../knowledge/pbir-enhanced-reference.md`](../knowledge/pbir-enhanced-reference.md) — the PBIR Enhanced visual.json authoring reference (the report JSON files committed under this rule)
- Microsoft Learn PBIP overview: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview (retrieved 2026-06-03)
- [`../agents/power-bi-engineer.md`](../agents/power-bi-engineer.md) — the agent that owns Power BI source control and ALM decisions

---

## Provenance

Codifies house anti-pattern §4 ("Checking binary .pbix files into git/ADO repos — use PBIP instead") from [`../CLAUDE.md`](../CLAUDE.md), and the `power-bi-engineer` source-control discipline. The Windows long-path fix (`git config --system core.longpaths true`) is the standard remediation for the Windows 260-character MAX_PATH limit, a well-known Windows filesystem constraint. PBIP format reference: Microsoft Learn (retrieved 2026-06-03). Long-path specifics: `[unverified — training knowledge]` — verify registry approach against your Windows version.

---

_Last reviewed: 2026-06-03 by `claude`_

---
name: solution-layering-resolution
description: Diagnose and resolve Dataverse solution-layering problems — a managed import that "didn't take", an unmanaged Active layer shadowing managed components, wrong ribbon buttons, components that won't delete, stuck _Upgrade holding solutions, uninstall blockers. Read-only diagnosis first (msdyn_componentlayer / msdyn_solutionhistory / pac), then a ranked M0–M8 fallback chain with explicit HARD GATEs on every irreversible or prod step. Complements managed-solution-import and alm-pipeline-design.
allowed-tools: Bash, Read
---

# solution-layering-resolution — diagnose & resolve Dataverse solution layering

> **Why this exists.** A managed solution import can succeed (HTTP 200, `pac` exit 0) and still leave
> production **not matching source** — because the Dataverse **solution layer stack** decides runtime
> behaviour, not the last import. An **unmanaged "Active" layer** sitting on top of a managed
> component silently wins; a competing managed solution installed later outranks yours; a component
> you deleted in dev is still present because a plain update import does not delete; a `_Upgrade`
> holding solution gets stuck mid-cutover. None of these throw at import time. This skill makes the
> diagnosis **read-only and explicit**, then walks a **ranked fallback chain** so an agent can fall
> back automatically — while **gating every irreversible or prod-affecting step behind human approval**.

## The shape (what's the spine)

The **read-only diagnosis (M0) is the spine** — always run it first, write a snapshot to disk, and let
the symptom + the layer query select the method. Everything after M0 is a **ranked fallback chain**:
try the preferred method (★ — M0 and M1 only; M2 is an approval-gated fallback, never a default); on its named failure signal, fall to the next (`→ Mx`). No fix runs
against TEST/PROD without the matching **HARD GATE** being cleared by a human.

```
diagnose (M0, read-only) → pick method by symptom → [HARD GATE if prod/irreversible] → act → verify (re-run M0)
```

## The layer model (the 90 seconds that prevents the wrong fix)

- Runtime = the **topmost layer** for each component. Bottom→top: **System** < **managed solutions**
  (in install order; a patch layers directly above its parent) < **Unmanaged ("Active")**, which is
  **always on top**. [S4, S10]
- **Merge-behaviour components** — forms, sitemap, ribbon, app modules — **merge** across layers; all
  other component types are **top-wins**. [S3] This is why "remove the active layer" is not a universal
  fix: it does nothing useful for a merge component.
- **Dependencies** are created only between the **topmost** layers. [S8]
- `--force-overwrite` / `OverwriteUnmanagedCustomizations` does **not** affect merge components, and
  does **not** affect a component that has **another managed layer above** it. [S3]
- Every unmanaged component is *always* in the default/**Active** solution — you cannot "move it out of
  the Active layer" by deleting and recreating it. See the companion knowledge file
  [`../../knowledge/dataverse-solution-layering-active-dependency.md`](../../knowledge/dataverse-solution-layering-active-dependency.md)
  before any delete-to-relayer attempt.

## Decision tree — symptom → diagnosis → method

| Symptom | Diagnose (read-only, M0) | Method (ranked) | Verify |
|---|---|---|---|
| Managed import "didn't take" / prod differs from source | `msdyn_componentlayers` query (below); UI *See solution layers* [S4] | **Active** layer present → default **M1** (fix at source + stage-and-upgrade); **M2** RemoveActiveCustomization only as an approval-gated fallback (never default); else another managed layer on top → **M6** reorder/uninstall | Re-run layer query: no `Active` row; expected solution topmost |
| Ribbon / command-bar button wrong or missing | `&ribbondebug=true` Command checker [S7] | **M3** Command checker remove-layer; else **M4** RibbonDiffXml edit | Command checker shows expected layer wins |
| A component you deleted in dev is still in target | `pac solution list`; `msdyn_solutionhistories` | **M1** stage-and-upgrade (upgrade deletes absent components) [S3] | Component query returns 404/empty |
| Stuck `_Upgrade` holding solution | `GET solutions?$filter=endswith(uniquename,'_Upgrade')` | **M1b** `pac solution upgrade --solution-name <base>` / `DeleteAndPromote` | `pac solution list`: single base at new version, no `_Upgrade` |
| Uninstall blocked | `RetrieveDependenciesForUninstall(SolutionUniqueName='x')` | **M6** remove top-layer dependents first [S8] | Re-run → empty dependency list |
| Patch sprawl (many patch layers) | `solutions?$filter=parentsolutionid ne null` | **M1d→M1** clone to roll up → upgrade | One base version, no patch layers |
| Publisher / prefix conflict on import | import error log; compare `msdyn_publishername` across layers [S6] | Repackage under one publisher *(guidance — see Honest limits)* | Clean import |

## M0 ★ — read-only diagnosis (ALWAYS first)

**When:** any layering issue. **Prerequisites:** `pac` auth (or a Dataverse Web API bearer token — see
[`../../knowledge/dataverse-token-acquisition.md`](../../knowledge/dataverse-token-acquisition.md)) with
read on `msdyn_componentlayer`. **Never needs a gate — it changes nothing.**

Write every result to disk as a JSON snapshot so the post-fix verify can diff against it.

```bash
# 1. What solutions are installed, their versions, managed/unmanaged?
pac solution list --environment https://yourorg.crm.dynamics.com

# 2. The layer stack for ONE component (the authoritative read).
#    msdyn_componentlayer is a VIRTUAL table — in practice query it scoped to one component.
GET {org}/api/data/v9.2/msdyn_componentlayers?\
$filter=msdyn_componentid eq '<component-guid>' and msdyn_solutioncomponentname eq 'Entity'&\
$select=msdyn_name,msdyn_solutionname,msdyn_publishername,msdyn_order,msdyn_changes

#    Active-layer check: look for a row where msdyn_solutionname eq 'Active'.

# 3. Recent import/upgrade history + any exception.
GET {org}/api/data/v9.2/msdyn_solutionhistories?\
$orderby=msdyn_starttime desc&$top=20&\
$select=msdyn_name,msdyn_operation,msdyn_status,msdyn_result,msdyn_starttime,msdyn_exceptionmessage
```

**Failure signals:** `400` on `msdyn_componentlayers` → the required filter is missing (see the
`[unverified]` note on the dual-filter rule in *Honest limits*); add `msdyn_componentid` +
`msdyn_solutioncomponentname` and retry. `403` → read permission missing → **M7** (UI). Full query
cookbook incl. `$select` columns and the ribbon/dependency reads: [`resources/diagnosis-queries.md`](resources/diagnosis-queries.md).

**Next fallback:** API access denied → **M7**.

---

## M1 ★ — fix at source + managed stage-and-upgrade

**When:** the managed content itself is wrong/stale, components need deleting, or patches need rolling
up. This is the **correct default** for almost every "prod differs from source" case — fix it in dev,
re-ship, let the upgrade reconcile.

**Prerequisites:** change made in **dev** (unmanaged); solution **version bumped** (`pac solution version`
or `pac solution online-version --solution-name X --solution-version A.B.C.D`); a **backup export** of
the target taken first.

```bash
# backup the target first (forensic, not undo — see Risks)
pac solution export --name X --path ./bak_X_managed.zip --managed --environment https://prod...

# static-check the artifact you are about to ship
pac solution check --path ./X_managed.zip --geo UnitedStates --outputDirectory ./checkout

# ⚠️ HARD GATE — human approval required (import to TEST/PROD; upgrade deletes absent components + their DATA)
pac solution import --path ./X_managed.zip --stage-and-upgrade --async \
  --activate-plugins --settings-file ./deploymentSettings-prod.json \
  --environment https://prod...
```

Microsoft prefers a **single-stage** stage-and-upgrade over the two-stage holding dance. [S2]

**Failure signals:** version not higher → bump it; `MissingDependency` → import the dependency first
(and see the Active-dependency knowledge file); timeout → raise `--max-async-wait-time` or use `--async`
and poll `msdyn_solutionhistory`. **Next fallback:** need a validation window / scheduled cutover → **M1b**;
deletes are *undesired* → **M1c**; small hotfix only → **M1d**.

- **M1b — two-stage holding.** `pac solution import --import-as-holding` then, after validation,
  `pac solution upgrade --solution-name X --async`. Web API equivalent: `ImportSolution` with
  `HoldingSolution=true`, then **`DeleteAndPromote(UniqueName='X')`**. `StageSolution` is validate-only
  [S5]. **When:** you need a validation gap or a scheduled promote. **Failure:** `_Upgrade` stuck → retry
  `pac solution upgrade`. ⚠️ **HARD GATE** on the import and on `DeleteAndPromote` (prod + irreversible). **Next:** M1c.
- **M1c — plain update (no upgrade flag).** `pac solution import` with no `--stage-and-upgrade`. Does
  **NOT** delete components removed from the new version. [S2, S3] **Use when** deletes are undesired.
  ⚠️ **HARD GATE** on import to TEST/PROD.
- **M1d — patch.** `CloneAsPatch(ParentSolutionUniqueName, DisplayName, VersionNumber)` / UI *Clone a
  patch* [S3, S11]. Small hotfix layered above the parent; **must** later be rolled up via
  `CloneAsSolution` + upgrade, or patch sprawl accumulates. ⚠️ **HARD GATE** on applying it to prod.

---

## M2 — RemoveActiveCustomization (Web API), per component — approval-gated fallback, never a default

> **Not a default.** M2 is never chosen automatically. Use it only as a fallback when M0 confirms an Active layer, M1 is not viable, and a human has approved the HARD GATE below.

**When:** M0 confirmed an **`Active` (unmanaged) layer** sitting over a managed **non-merge** component in
TEST/PROD, and you want the managed layer to win again.

**Prerequisites:** confirmed via M0; the component is **not** unmanaged **base-layer** (removing the only
layer is not possible [S4]); an **unmanaged backup export** of the Active changes taken first.

> ⚠️ **HARD GATE — human approval required.** This is **irreversible and can lose data** [S4]. One call
> per component. Present the plan + the component list and wait for explicit approval; never run it
> automatically.

```http
POST {org}/api/data/v9.2/RemoveActiveCustomization
Content-Type: application/json

{ "LogicalName": "account", "Id": "<component-guid>" }
```

> **Corrected API surface (verified 2026-10-12 — this replaces the parameter names in the research
> brief).** The Dataverse Web API **action is singular `RemoveActiveCustomization`**, and its two
> parameters are **`LogicalName`** (`Edm.String`) and **`Id`** (`Edm.Guid`) — **not** the plural action
> name, and **not** `SolutionComponentName` / `ComponentId`. The **UI** feature is still labelled
> *"Remove active customizations"* (plural) [S4]; do not confuse the UI label with the API action name.

**Failure signals:** error that it is the "only layer" → the component is unmanaged **base** → it cannot
be de-layered; delete it instead (**M5**). Error on a **merge** component (form/ribbon/sitemap/app
module) → wrong tool → **M3/M4**. **Next fallback:** ribbon → **M3**; merge component → **M4**; no API
access → **M2-UI**.

- **M2-UI** — Solution → component → *See solution layers* → **Remove active customizations** [S4]. Same
  irreversibility, same **HARD GATE**. Notably, this operation is still permitted even when *Block
  unmanaged customizations* (M8) is enabled. [S9]

**Verify:** re-run the M0 layer query for that component — no `Active` row; the expected managed
solution is topmost.

---

## M3 — Command checker (ribbon / command bar)

**When:** a ribbon/command-bar button is wrong, missing, or shows an unexpected layer. Open the app with
`&ribbondebug=true` and use the **Command checker** to inspect and **remove the offending command layer**
[S7]. **Failure:** the layer isn't visible / isn't removable here → **M4**. ⚠️ **HARD GATE** if the
change is applied in TEST/PROD (it edits a shipped component + needs publish).

**Verify:** Command checker shows the expected command definition winning.

---

## M4 — export → edit XML → reimport (RibbonDiffXml / customizations.xml)

**When:** last resort for **merge components** (ribbons, sitemaps) where M2/M3 can't reach — because
`RemoveActiveCustomization` and force-overwrite don't apply to merge components [S3, S7]. High error
risk; hand-editing `RibbonDiffXml` / `customizations.xml` is easy to get wrong, and it requires a
**Publish All** afterward.

⚠️ **HARD GATE — human approval required** (manual XML edit of a shipped component + Publish All in
TEST/PROD). Prefer fixing at source (**M1**) over M4 whenever the component can be rebuilt in dev.

**Verify:** re-export and diff the component XML; Command checker / UI shows the intended result.

---

## M5 — import with --force-overwrite / OverwriteUnmanagedCustomizations

**When:** you need to **bulk-clear Active layers** across many **non-merge** components that ship inside
one solution. Microsoft **discourages** this — it is slow and destructive [S2]. `--force-overwrite`
(`-f`) / `OverwriteUnmanagedCustomizations=true` wipes unmanaged changes on non-merge components and has
**no effect** on merge components or components with another managed layer above [S3].

⚠️ **HARD GATE — human approval required** (force-overwrite import to TEST/PROD; wipes unmanaged work).

**Failure signals:** merge components unaffected → go per-component via **M2** (non-merge; approval-gated fallback, never a default) or **M3/M4**
(merge). **Verify:** re-run M0 across the affected components.

---

## M6 — reorder / uninstall a competing managed solution

**When:** M0 shows **another managed solution** outranking yours for the component (install order, or a
later install). **Prerequisite:** run `RetrieveDependenciesForUninstall(SolutionUniqueName='x')` and
remove top-layer dependents first [S8]. Uninstalling a managed solution **drops its tables and their
DATA**.

```bash
# read-only precondition (no gate)
GET {org}/api/data/v9.2/RetrieveDependenciesForUninstall(SolutionUniqueName='x')

# ⚠️ HARD GATE — human approval required (uninstall = data loss for that solution's tables)
pac solution delete --solution-name <name> --environment https://prod...
```

⚠️ **HARD GATE — human approval required** on the delete/uninstall. **Failure:** dependency list
non-empty → remove dependents first, then retry. **Verify:** `RetrieveDependenciesForUninstall` returns
empty; `pac solution list` shows the expected top solution.

---

## M7 — manual UI investigation

**When:** API/CLI access is denied (403, no app-user role). Use the maker portal: **Solution layers**
(*See solution layers*) [S4] and **Solution history** [S13] to read the stack and the last operations
by hand, then route the fix back through M1 (or M2 only as an approval-gated fallback, never a default) once access is restored. Read-only; no gate.

---

## M8 — prevention (NOT a fix for a live incident)

Stops the next layering incident; does **not** resolve the current one:

- **Managed-only downstream, unmanaged only in dev** (plugin house rule §3 #4).
- **Power Platform Pipelines** (default = stage-and-upgrade) / **Build Tools** for promotion [S2, S14].
- **Block unmanaged customizations** environment setting — a Power Platform **admin** enables it in the
  admin center; it blocks unmanaged-solution import, new-component creation, and unmanaged changes to
  managed components, while still allowing env-var changes, enable/disable, and *Remove an unmanaged
  layer* [S9]. ⚠️ **HARD GATE — human approval required** to toggle it (changes environment behaviour for
  all makers). See [`dlp-policy-design`](../dlp-policy-design/SKILL.md) + [`alm-pipeline-design`](../alm-pipeline-design/SKILL.md).
- **One publisher + prefix** per solution set; **managed properties** to lock customizability [S10].

---

## Preferred agent workflow (scripted, safe)

1. `pac auth list` / select env; **confirm the env URL is not prod unless the gate is cleared.**
2. **Diagnose (M0)** → write a JSON snapshot of layers + solution list + history to disk.
3. **Backup** — export unmanaged **and** managed of the affected solution(s) from the target.
4. **Dry-run** — `pac solution check`; `StageSolution` (validate-only) [S5]; diff the layer snapshot vs intended.
5. **Gate** — produce a plan and **await human approval** for every item in *Production HARD gates*.
6. **Act** — M1 (stage-and-upgrade, `--async`) preferred; M2 per-component only as an approval-gated fallback (never a default) when an Active layer is confirmed and M1 is not viable.
7. **Verify** — re-run M0; diff against the step-2 snapshot; confirm the version via `pac solution list`;
   monitor `msdyn_solutionhistory` status to completion.
8. **Log** every command + output to the run directory.

## Production HARD gates (every one needs explicit human approval — never automatic)

Label each of these `HARD GATE — human approval required` in any plan, and present it for sign-off
before running. They are irreversible, prod-affecting, or both:

1. **Any import (any mode) into TEST or PROD.**
2. **`--stage-and-upgrade` / Apply upgrade / `DeleteAndPromote`** — deletes components (and their column/table **data**) absent from the new version.
3. **`--force-overwrite` / `OverwriteUnmanagedCustomizations`** — wipes unmanaged changes on non-merge components.
4. **`RemoveActiveCustomization`** — once per component; irreversible, possible data loss.
5. **Solution delete / uninstall** — drops that solution's tables and data.
6. **Ribbon / customizations.xml edits + Publish All.**
7. **`--skip-dependency-check`.**
8. **Toggling *Block unmanaged customizations*** (or any environment setting).
9. **Environment backup / restore.**
10. **Publisher / prefix changes.**

## Risks & rollback

- **`RemoveActiveCustomization`:** irreversible; possible data loss [S4]. Partial rollback: re-import the
  unmanaged backup (re-creates the layer; **data is not restored**).
- **Stage-and-upgrade / Apply upgrade:** deletes components and their data when absent from the new
  version [S3]. Rollback means uninstall + reimport the previous managed version → data loss; real
  recovery is an **environment backup/restore** taken *before* the action.
- **Force-overwrite:** wipes unmanaged changes on non-merge components [S3].
- **Uninstall managed solution:** drops its tables/data.
- **Best prod rollback is a pre-action environment backup** (admin) — take it before any gated step.

## Honest limits & `[unverified]` markers

- **`msdyn_componentlayer` mandatory dual-filter rule** is **`[unverified]`**. The entity's columns
  (`msdyn_componentid`, `msdyn_solutioncomponentname`, `msdyn_solutionname`, `msdyn_publishername`,
  `msdyn_name`, `msdyn_order`, `msdyn_changes`) are **verified** against the entity reference [S6];
  the claim that a query *must* filter on both `msdyn_componentid` **and** `msdyn_solutioncomponentname`
  is a known virtual-table behaviour but is **not documented on that page** — if a broad query returns
  `400`, add both filters and retry.
- **Publisher-prefix remediation** ("repackage under one publisher; never rename the prefix of shipped
  components") is **`[unverified]`** — sound practice but not sourced this run. Treat as guidance, not a
  verified procedure.
- **Environment backup/restore as the canonical prod rollback** is **`[unverified]`** (process not
  fetched this run) — confirm the admin backup/restore steps against current docs before relying on it.
- The decision logic here (symptom routing, gate map, fallback order) is deterministic; the live
  Dataverse/`pac` calls need a real tenant and are best-effort.
- Verified against **Microsoft Learn + `pac solution` reference on 2026-10-12**. Re-verify on `pac`
  upgrades and when the Dataverse Web API version rotates.

## Cross-references

- Full verified API/CLI surface + copy-paste diagnosis queries: [`resources/diagnosis-queries.md`](resources/diagnosis-queries.md)
- Hardened import + flow reactivation (the import *mechanics* this skill gates): [`../managed-solution-import/SKILL.md`](../managed-solution-import/SKILL.md)
- End-to-end ALM pipeline design (prevention — M8): [`../alm-pipeline-design/SKILL.md`](../alm-pipeline-design/SKILL.md)
- The Active-layer dependency trap (don't delete to re-layer): [`../../knowledge/dataverse-solution-layering-active-dependency.md`](../../knowledge/dataverse-solution-layering-active-dependency.md)
- Token acquisition for the Web API calls: [`../../knowledge/dataverse-token-acquisition.md`](../../knowledge/dataverse-token-acquisition.md)
- **Any shipped use of an SPN secret, or any auth/consent decision, is reviewed by `ravenclaude-core/security-reviewer`.**

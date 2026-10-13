# Diagnosis queries + verified API/CLI surface

Companion reference for [`../SKILL.md`](../SKILL.md). Every table below was **verified against Microsoft
Learn on 2026-10-12** (sources keyed `S#` in the skill's source list; URLs at the bottom). Items that
could not be confirmed this run are marked `[unverified]` and must stay that way until checked.

> **Load-bearing correction (2026-10-12):** the Dataverse Web API action is **`RemoveActiveCustomization`**
> (singular), parameters **`LogicalName`** + **`Id`** — *not* the plural action name and *not*
> `SolutionComponentName` / `ComponentId`. The maker-portal feature keeps the plural label *"Remove
> active customizations"* [S4]. See the table under *Web API actions* below.

## 1. `msdyn_componentlayer` — the layer-stack read [S6]

Verified columns on the entity reference:

| Column | Use |
|---|---|
| `msdyn_componentid` | the component GUID you filter on |
| `msdyn_solutioncomponentname` | the component-type name (e.g. `Entity`, `SystemForm`, `Workflow`) |
| `msdyn_solutionname` | the solution that owns this layer — `Active` means the unmanaged top layer |
| `msdyn_publishername` | the publisher of the layer (compare across layers for prefix conflicts) |
| `msdyn_name` | friendly name of the component |
| `msdyn_order` | layer order |
| `msdyn_changes` | summary of what the layer changed |

```http
GET {org}/api/data/v9.2/msdyn_componentlayers?$filter=msdyn_componentid eq '<guid>' and msdyn_solutioncomponentname eq 'Entity'&$select=msdyn_name,msdyn_solutionname,msdyn_publishername,msdyn_order,msdyn_changes
```

`[unverified]` — the rule that this query **must** filter on both `msdyn_componentid` **and**
`msdyn_solutioncomponentname` is a known virtual-table behaviour but is **not documented** on the entity
reference page. If an unfiltered query returns `400`, add both filters and retry.

## 2. `msdyn_solutionhistory` — recent operations [S13]

Verified columns (subset of the entity reference, all confirmed present):
`msdyn_name`, `msdyn_operation`, `msdyn_suboperation`, `msdyn_status`, `msdyn_result`, `msdyn_starttime`,
`msdyn_endtime`, `msdyn_totaltime`, `msdyn_solutionversion`, `msdyn_ismanaged`, `msdyn_ispatch`,
`msdyn_isoverwritecustomizations`, `msdyn_errorcode`, `msdyn_exceptionmessage`, `msdyn_exceptionstack`,
`msdyn_publishername`, `msdyn_packagename`, `msdyn_packageversion`.

```http
GET {org}/api/data/v9.2/msdyn_solutionhistories?$orderby=msdyn_starttime desc&$top=20&$select=msdyn_name,msdyn_operation,msdyn_status,msdyn_result,msdyn_starttime,msdyn_exceptionmessage
```

## 3. Solutions + uninstall blockers

```http
# installed solutions
GET {org}/api/data/v9.2/solutions?$select=uniquename,version,ismanaged&$filter=isvisible eq true

# stuck holding solutions
GET {org}/api/data/v9.2/solutions?$filter=endswith(uniquename,'_Upgrade')

# patch layers (sprawl)
GET {org}/api/data/v9.2/solutions?$filter=parentsolutionid ne null
```

## 4. Web API actions / functions (verified parameter names) [S-webapi]

| Operation | Kind | Verified parameters |
|---|---|---|
| **`RemoveActiveCustomization`** | Action | `LogicalName` (Edm.String), `Id` (Edm.Guid) |
| **`ImportSolution`** | Action | `OverwriteUnmanagedCustomizations`, `PublishWorkflows`, `CustomizationFile`, `ImportJobId`, `HoldingSolution`, `StageAndUpgrade` (+ `ConvertToManaged` *obsolete*, `ComponentParameters`, `SolutionParameters`) |
| **`DeleteAndPromote`** | Action | `UniqueName` (Edm.String) |
| **`CloneAsPatch`** | Action | `ParentSolutionUniqueName`, `DisplayName`, `VersionNumber` |
| **`CloneAsSolution`** | Action | `ParentSolutionUniqueName`, `DisplayName`, `VersionNumber` |
| **`StageSolution`** | Action | validate-only staging [S5] |
| **`RetrieveDependenciesForUninstall`** | Function | `SolutionUniqueName` (Edm.String) → `Collection(dependency)` |
| **`RetrieveDependentComponents`** | Function | `ObjectId` (Edm.Guid), `ComponentType` (Edm.Int32) |

Note: a `StageAndUpgrade` boolean also exists as an `ImportSolution` parameter, and a `StageAndUpgrade`
action is listed in the Web API action reference — the single-stage path Microsoft prefers [S2].

## 5. `pac solution` flags (verified against the CLI reference) [S1]

| Subcommand | Required | Optional (selected) |
|---|---|---|
| `export` | `--name/-n` | `--path/-p`, `--managed/-m`, `--overwrite/-ow`, `--async/-a`, `--environment/-env`, `--include/-i`, `--targetversion/-v`, `--max-async-wait-time/-wt` |
| `import` | `--path/-p` | `--stage-and-upgrade/-up`, `--import-as-holding/-h`, `--force-overwrite/-f`, `--skip-dependency-check/-s`, `--skip-lower-version/-slv`, `--publish-changes/-pc`, `--activate-plugins/-ap`, `--settings-file`, `--async/-a`, `--max-async-wait-time/-wt`, `--environment/-env` |
| `upgrade` | `--solution-name/-sn` | `--async`, `--environment`, `--max-async-wait-time` |
| `online-version` | `--solution-name/-sn` | `--solution-version/-sv`, `--environment/-env` |
| `clone` | `--name/-n` | `--outputDirectory/-o`, `--packagetype/-p` (Unmanaged/Managed/Both), `--async/-a`, `--include/-i`, `--environment/-env`, `--localize/-loc`, `--map`, `--max-async-wait-time/-wt` |
| `check` | — | `--path/-p`, `--geo/-g`, `--outputDirectory/-o`, `--ruleSet/-rs`, `--ruleLevelOverride/-rl`, `--environment/-env` |
| `delete` | `--solution-name/-sn` | `--environment/-env` |
| `create-settings` | — | `--solution-zip/-z`, `--solution-folder/-f`, `--settings-file/-s` |

(The `export` example in the docs shows `--managed true`; the parameter is documented as a switch —
either form is accepted. `check` has no *required* parameter but needs `--path` in practice.)

## 6. Ribbon / command-bar diagnosis [S7]

Open the model-driven app with `&ribbondebug=true` appended to the URL, then use **Command checker** to
inspect which layer each command resolves to and to remove an offending unmanaged command layer. For
merge components that Command checker can't reach, the fallback is an XML export/edit/reimport of
`RibbonDiffXml` + **Publish All** (skill method **M4**).

## Sources (verified 2026-10-12 via `curl -sL` of learn.microsoft.com)

- **S1** `pac solution` reference — `/power-platform/developer/cli/reference/solution`
- **S2** ALM performance recommendations — `/power-platform/alm/performance-recommendations`
- **S3** Update solutions (upgrade/update/patch; overwrite semantics) — `/power-apps/maker/data-platform/update-solutions`
- **S4** Solution layers (UI; Remove active customizations; base-layer exception) — `/power-apps/maker/data-platform/solution-layers`
- **S5** Solution async (StageSolution / ImportSolutionAsync) — `/power-platform/alm/solution-async`
- **S6** `msdyn_componentlayer` entity reference — `/power-apps/developer/data-platform/reference/entities/msdyn_componentlayer`
- **S7** Remove an unmanaged layer for a ribbon (Command checker) — `/troubleshoot/power-platform/power-apps/create-and-use-apps/remove-an-unmanaged-layer-for-ribbon`
- **S8** Removing dependencies — `/power-platform/alm/removing-dependencies`
- **S9** Block unmanaged customizations — `/power-platform/alm/block-unmanaged-customizations`
- **S10** Solution layers / ALM — `/power-platform/alm/solution-layers-alm`
- **S11** Solution API (CloneAsPatch / CloneAsSolution / DeleteAndPromote) — `/power-platform/alm/solution-api`
- **S13** `msdyn_solutionhistory` entity reference — `/power-apps/developer/data-platform/reference/entities/msdyn_solutionhistory`
- **S14** Power Platform Pipelines — `/power-platform/alm/pipelines`
- **S-webapi** Web API Action/Function reference pages — `/power-apps/developer/data-platform/webapi/reference/{removeactivecustomization,importsolution,deleteandpromote,cloneaspatch,cloneassolution,retrievedependenciesforuninstall,retrievedependentcomponents}`

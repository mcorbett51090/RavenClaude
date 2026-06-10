# PBIP-in-Fabric deployment & environment variables

> **Last reviewed:** 2026-06-10. Sources: scout run
> `docs/research/2026-06-10-pbip-deployment-variables/report.md`; `microsoft/fabric-cicd` issue #839 (PR #840 in
> flight); `darkanita/PBIP_Fabric_Reference_Guide`; `iemejia/fabio` v0.20.0 (2026-06-10);
> `kerski/fabric-dataops-patterns`; `NatVanG/fab-inspector` v3.3.0 (2026-06-09); Marc Lelijveld /
> data-marc.com 2024; `alisonpezzott/pbi-ci-cd-isv-multi-tenant`; `powerofbi.org` Aug 2025.
> **Fabric moves fast — every claim about platform behavior or a tool's version is marked `[verify-at-use]`.**
> Refresh this file when: fabric-cicd PR #840 ships (`.platform` fix), the PBIR-deployment-pipeline constraint
> is lifted, Variable Library semantic-model-connection support GAs, or `fabio` publishes a stable API contract.

The most common "why isn't my CI/CD working on first run?" incident in PBIP deployments has one root cause:
mixing variables from two layers that are resolved at completely different points in the deploy cycle. This file
maps those two layers, documents the gotchas, and gives a decision table for picking the right mechanism.

---

## The load-bearing distinction: Layer A vs Layer B

**Layer A — Source-controlled variables** live inside the PBIP folder structure and are parameterized via
`parameter.yml` **before / during** `publish_all_items()`. `fabric-cicd` handles these.

| Variable | Location in PBIP | `parameter.yml` mechanism |
| --- | --- | --- |
| Power Query parameters (`Environment`, `SrvName`, `DbName`) | `definition/tables/<name>.tmdl` — `expression: "..."` | `find_replace` or `key_value_replace` |
| Lakehouse / warehouse GUIDs | Notebook metadata, `pipeline-content.json`, mashup PQ | `find_replace` with `$items.Lakehouse.Name.$id` |
| Workspace ID | All item-definition files | `$workspace.$id` (automatic dynamic variable) |
| SQL endpoint hostname | SemanticModel connection string | `$items.Lakehouse.Name.$sqlendpoint` |
| Connection GUIDs (pipelines, dataflows) | `pipeline-content.json`, `queryMetadata.json` | Manual `find_replace` per environment; not auto-deployed by fabric-cicd `[verify-at-use]` |
| Spark pool `instance_pool_id` | `Sparkcompute.yml` | `spark_pool` parameter type |
| Eventhouse query URI | Eventhouse definition | `$items.Eventhouse.Name.$queryserviceuri` |
| Semantic model `displayName` | `.platform` `$.metadata.displayName` | **BLOCKED** — see #839 gotcha below |

**Layer B — Post-deploy runtime variables** are applied **after** the artifact is live in the workspace.
Rules and libraries require a live target artifact; they cannot be configured before the first deploy.

| Mechanism | Applies to | When usable |
| --- | --- | --- |
| Fabric deployment-pipeline **parameter rules** | Semantic model PQ parameters | After first deploy only |
| Fabric deployment-pipeline **data source connection rules** | Semantic model connections | After first deploy only |
| **Variable Libraries** (GA April 2025) `[verify-at-use]` | Data pipelines, Notebooks, Copy jobs, Dataflows Gen2 | After workspace item is live; NOT yet: semantic model connections |
| **FabricPS-PBIP** `Set-SemanticModelParameters` | PQ parameters on import | At import time (applied before import, not strictly post-deploy, but requires a live workspace target) |
| **REST API** Update Parameter | PQ parameters | After the item is live in the workspace |

---

## Layer-A-vs-Layer-B decision aid

Use this table when choosing a parameterization mechanism. Mixing layers is the source of most first-deploy failures.

| What you are parameterizing | Layer | Mechanism |
| --- | --- | --- |
| Lakehouse GUID referenced in Power Query | A | `parameter.yml` `find_replace` with `$items.Lakehouse.Name.$id` |
| Workspace ID anywhere in definition files | A | `$workspace.$id` automatic token |
| SQL endpoint hostname in connection string | A | `$items.Lakehouse.Name.$sqlendpoint` token |
| Environment-specific PQ parameter (e.g. `Environment = "DEV"`) | A | `parameter.yml` `find_replace` or `key_value_replace` |
| Spark pool identity | A | `parameter.yml` `spark_pool` type |
| Semantic model connection to PROD lakehouse | B | Deployment-pipeline parameter rule — only after first deploy |
| Data Pipeline parameter that varies by stage | B | Variable Library `[verify-at-use]` or lakehouse-JSON pattern (see Toolchain below) |
| PQ parameter set via script post-deploy | B | FabricPS-PBIP `Set-SemanticModelParameters` or REST Update Parameter |
| Semantic model `displayName` per environment | BLOCKED | #839 gotcha — preprocess `.platform` before `publish_all_items()` (see below) |

**The canonical first-deploy mistake:** expecting Fabric deployment-pipeline parameter rules to apply on the
**first deploy** to a stage. Rules require a live artifact — they do not exist until after first deploy. The first
deploy always lands with the source (DEV) connection strings; configure rules on the first deploy's output so
subsequent deploys pick them up. Source: `darkanita/PBIP_Fabric_Reference_Guide`.

---

## The fabric-cicd #839 gotcha — `.platform` displayName parameterization silent failure

**Every PBIP deploy pipeline must warn on this.** Verify PR #840 status before hardcoding the workaround
into long-lived pipelines. `[verify-at-use]`

Neither `find_replace` nor `key_value_replace` in `parameter.yml` apply to `.platform` files during deployment,
despite the official docs claiming support. The most common use case is changing `$.metadata.displayName` per
environment — e.g. "Sales Dashboard [DEV]" vs "Sales Dashboard". All standard `parameter.yml` approaches fail
**silently**: no error, no warning, the replacement simply does not happen. Source: `microsoft/fabric-cicd`
issue #839.

**Workaround:** preprocess `.platform` files with Python (or any string-replace step) **before** calling
`publish_all_items()`:

```python
import pathlib

platform_path = pathlib.Path("MyReport/.platform")
content = platform_path.read_text()
patched = content.replace("Sales Dashboard [DEV]", f"Sales Dashboard [{env}]")
platform_path.write_text(patched)
# ... call publish_all_items() here
# optionally restore the original after deploy
```

---

## The PBIR-reports constraint

**PBIR-format reports cannot deploy through Fabric deployment pipelines.** `[verify-at-use]`

This shapes every PBIP architecture decision. If your artifact set includes PBIR reports, Fabric deployment
pipelines cannot be the sole promotion mechanism. Workaround paths:

- Continue using PBIX-format reports in the deployment pipeline (and maintain PBIR only for git/PBIP), or
- Use a code-first pipeline (fabric-cicd, FabricPS-PBIP, fabio) that deploys directly to the target
  workspace, bypassing the deployment-pipeline stage model entirely.

Source: Marc Lelijveld / data-marc.com 2024. `[verify-at-use]` — re-check Fabric roadmap before committing to an architecture that treats this as permanent.

---

## Toolchain reference

| Tool | What it does | When to use | Notes |
| --- | --- | --- | --- |
| **`microsoft/fabric-cicd`** `parameter.yml` | Layer-A parameterization; 4 substitution types (see below); official Python library | Primary CI/CD path for PBIP deploys via code | Watch #839 `.platform` exclusion; re-check docs at use `[verify-at-use]` |
| **`iemejia/fabio`** | Rust CLI with 74 command groups, 790+ subcommands; `deploy` command uses `parameters.json` (described as superset of fabric-cicd YAML, in JSON for agent-native tooling) | Agent-native, structured-JSON-output PBIP deploy; composable piping | 3 stars, v0.20.0 shipped 2026-06-10. **License not confirmed** — `[verify-before-use]`. PBIP TMDL/PBIR format support: `[verify-at-use]`. First-class agent tool (structured JSON + error codes + stdin/stdout piping). Author: Ismael Mejia. Prefer over the Python library for agent-driven workflows once license is verified. |
| **FabricPS-PBIP** (`microsoft/Analysis-Services`) | PowerShell `Set-SemanticModelParameters`; report binding via `itemProperties`; connection binding via REST | Layer-B PQ parameter override at import time; ADO-native PS pipelines | `kegottschalk/FabricDeployExtension` wraps this for GUI ADO users (0 stars, not published to Marketplace, self-deprecated) `[verify-at-use]` |
| **`NatVanG/fab-inspector`** | Declarative JSON-rules engine for PBIP/PBIR validation; v3.3.0 MIT; JSONLogic + `daxquery`/`sqlquery`/`apiget` operators; AI-friendly rule authoring | Pre-deploy validation gate | Use before `publish_all_items()`. Supersedes `NatVanG/PBI-Inspector` (old, semi-dormant). v3.3.0 shipped 2026-06-09. `[verify-at-use]` |
| **`kerski/fabric-dataops-patterns`** | `git diff`-scoped deploy (only changed models per push); synchronous refresh validation gate; `definition.pbir` interrogation for thin-vs-embedded routing | Production DataOps loop with change-scoped deploys | `git diff` scoped deploy is not in official fabric-cicd guidance. "Prime the pipeline" requirement: first deploy needs manual credential config before refresh succeeds. 62 stars, John Kerski. |
| **`powerofbi.org` lakehouse-JSON pattern** | Workaround for Fabric deployment pipelines having no parameter rules for Data Pipelines | Data Pipeline parameters across stages when Variable Libraries don't fit | JSON config in per-stage lakehouse; a "Read Parameters" notebook exits via `mssparkutils.notebook.exit(json.dumps(config))`; only one deployment rule needed (change the notebook's default lakehouse from DEV to TEST). Credit: Benoit / powerofbi.org, Aug 2025. `[verify-at-use]` |

---

## `parameter.yml` — four substitution types (fabric-cicd)

`[verify-at-use]` — re-check against fabric-cicd docs before authoring a new pipeline.

| Type | Mechanism | Use case | Key constraint |
| --- | --- | --- | --- |
| `find_replace` | String substitution across definition files; `is_regex: "true"` with capture-group 1; filter by `item_type`/`item_name`/`file_path` | Environment strings, workspace IDs, lakehouse GUIDs | Silently skips `.platform` files (#839) |
| `key_value_replace` | JSONPath-based substitution in JSON/YAML; auto-detects JSON without `.json` extension (`.schedules` files) | Structured JSON payloads, schedule config | Excludes `.platform` files by design (#839) |
| `spark_pool` | `instance_pool_id` → pool type + name; only `item_name` filter | Spark pool binding per environment | No `file_path` filter |
| `semantic_model_binding` | Post-deploy connection binding; one connection per semantic model; `_ALL_` key supported | Connection binding after artifact is live | Post-deploy, not pre-deploy |

Dynamic variable tokens: `$workspace.$id`, `$workspace.<name>`, `$items.<type>.<name>.$id`,
`$items.Lakehouse.<name>.$sqlendpoint`, `$ENV:<VAR_NAME>` (feature-flagged `[verify-at-use]`)

---

## Operational gotchas

1. **Parameter rules require live artifacts (first-deploy trap).** Rules must be configured AFTER first deployment to a stage. Source: `darkanita/PBIP_Fabric_Reference_Guide`.
2. **Manual "Update all" required after PR merge.** After a PR merges to main, users must manually trigger Git→Workspace sync; no automatic sync exists. Source: `darkanita/PBIP_Fabric_Reference_Guide`.
3. **`.platform` displayName replacement fails silently.** See #839 section above.
4. **`git diff`-scoped deploy prevents unnecessary refreshes.** Without it, every push rebuilds the whole workspace. `kerski/fabric-dataops-patterns` implements this; official fabric-cicd does not.
5. **Variable Libraries do NOT yet support semantic model connections** (as of GA April 2025). Use deployment-pipeline parameter/connection rules for semantic model connections after first deploy. `[verify-at-use]`
6. **ISV / multi-tenant parameterization shape is different from environment parameterization.** `alisonpezzott/pbi-ci-cd-isv-multi-tenant` uses `semanticModelsParameters` scoped per-tenant (not per-environment); the tenant-scoped config is a different shape from `parameter.yml` — do not conflate them.
7. **PBIR reports cannot use Fabric deployment pipelines** (see constraint section above). `[verify-at-use]`

---

## See also

- [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) — PBIR Enhanced infinite-spinner / schema errors after deploy (a different category of PBIR deploy failure)
- [`pbir-enhanced-reference.md`](pbir-enhanced-reference.md) — building PBIR Enhanced visuals correctly
- [`sempy-fabric-reference.md`](sempy-fabric-reference.md) — Python-from-a-Fabric-notebook refresh orchestration and workspace operations
- [`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md) — REST-first debugging for PBIR/Fabric problems
- [`power-bi-fabric-agentic-toolchain-2026.md`](power-bi-fabric-agentic-toolchain-2026.md) — the broader Power BI / Fabric toolchain landscape (TMDL, Tabular Editor, fab CLI, semantic-link-labs)
- [`../skills/power-bi/`](../skills/power-bi/) — PBIP git workflow + deployment skill playbook

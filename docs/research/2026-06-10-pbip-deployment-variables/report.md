# Scout Run: PBIP Project Deployment Variables & Parameterization in Microsoft Fabric

**Date:** 2026-06-10  
**Skill:** `ravenclaude-core:scout`  
**Seed:** "All the variables in a PBIP project" — PBIP/semantic-model parameters, `.platform`/`.pbip`/`definition.pbir` config, connection-string/data-source rebinding, deployment-pipeline deployment rules, `parameter.yml`/find-and-replace approaches, environment-specific config, fabric-cli/fabric REST/semantic-link-labs tooling.

Seeds traversed: `microsoft/fabric-cicd`, `RuiRomano/pbip-demo`, `RuiRomano/fabric-cli-powerbi-cicd-sample`, `m-kovalsky/semantic-link-labs`, `pbi-tools/pbi-tools`, `microsoft/Analysis-Services` (FabricPS-PBIP), `kerski/fabric-dataops-patterns`, `alisonpezzott/pbi-ci-cd-isv-multi-tenant`, `NatVanG/fab-inspector`, `iemejia/fabio`, `kegottschalk/FabricDeployExtension`, `donovanwhite/fabric-cicd-framework`, `darkanita/PBIP_Fabric_Reference_Guide`, `microsoft/unified-data-foundation-with-fabric-solution-accelerator`

---

## The parameterization surface map (what actually varies across DEV/TEST/PROD)

### Layer 1 — Inside the PBIP file structure (source-controlled variables)

| Variable | Location | Parameterization lever |
|---|---|---|
| Power Query parameters (Environment, SrvName, DbName) | `definition/tables/<name>.tmdl` | Deployment-pipeline parameter rules OR `parameter.yml` `find_replace` |
| Lakehouse / warehouse GUIDs | Notebook metadata, pipeline-content.json, mashup.pq | `find_replace` or `key_value_replace` with `$items.Lakehouse.Name.$id` |
| Workspace ID | All item definition files | `$workspace.$id` dynamic variable |
| SQL endpoint hostname | SemanticModel connection string | `$items.Lakehouse.Name.$sqlendpoint` |
| Connection GUIDs (pipelines, dataflows) | `pipeline-content.json`, `queryMetadata.json` | Manual `find_replace` per environment; not deployed by fabric-cicd |
| Semantic model `displayName` | `.platform` file `$.metadata.displayName` | **NOT replaceable via fabric-cicd** — documented bug issue #839; Python preprocess workaround |
| Spark pool `instance_pool_id` | `Sparkcompute.yml` | `spark_pool` parameter type |
| Report `byConnection` references | `definition.pbir` | Auto-converted from `byPath`; parameterize workspace-ID + model-ID components |
| Eventhouse query URI | Eventhouse definition | `$items.Eventhouse.Name.$queryserviceuri` |

### Layer 2 — fabric-cicd `parameter.yml` (four types, fetched from official docs)

1. **`find_replace`** — string substitution across all files; `is_regex: "true"` with capture group 1; filter by `item_type`/`item_name`/`file_path`
2. **`key_value_replace`** — JSONPath-based substitution in JSON/YAML; auto-detects JSON without `.json` extension (`.schedules` files); excludes `.platform` files by design
3. **`spark_pool`** — `instance_pool_id` → pool type + name; only `item_name` filter
4. **`semantic_model_binding`** — post-deploy connection binding; one connection per semantic model only; supports `_ALL_` key

Dynamic variables: `$workspace.$id`, `$workspace.<name>`, `$items.<type>.<name>.$id`, `$items.Lakehouse.<name>.$sqlendpoint`, `$ENV:<VAR>` (feature-flagged)

**Critical bug (issue #839):** `find_replace` and `key_value_replace` silently skip `.platform` files despite docs claiming support. PR #840 in flight. Workaround: preprocess `.platform` files with Python before calling `publish_all_items()`.

### Layer 3 — Fabric Deployment Pipeline rules (post-deploy, UI/API)

Configured AFTER first deployment only (rules require live artifacts — the most-common gotcha). Three types: parameter rules, data source connection rules. No rules for Data Pipelines — this gap is addressed by the `powerofbi.org` lakehouse-JSON pattern below.

### Layer 4 — Fabric Variable Libraries (GA April 2025)

Workspace item storing named key-value pairs with multiple "value sets" (environment rows). Supported: Data pipelines, Notebooks, Copy jobs, Dataflows Gen2. NOT yet: semantic model connections, pipeline default parameters. Connection parameterization requires explicit connection GUID from "Manage connections and gateways." Environments need identically-named libraries with different active value sets; the library reference itself cannot be parameterized.

### Layer 5 — FabricPS-PBIP PowerShell module (`microsoft/Analysis-Services`)

`Set-SemanticModelParameters -path "..." -parameters @{"Param1"="value"}` — overrides PQ parameters before/at import. Report binding via `itemProperties @{"semanticModelId"=$modelId}` at import time. Connection binding via PowerBI REST API with `gatewayObjectId: "00000000-..."` for shared cloud connections.

### Layer 6 — REST API direct manipulation

Used post-deploy: Update Parameter API, selective partition refresh, XMLA endpoint parameter override. Marc Lelijveld recommends this for stage-specific parameter changes in a hybrid Git+pipeline architecture.

---

## Ranked shortlist — 9 finds (depth × novelty × practitioner-grounding − popularity)

### 1. `iemejia/fabio` — Rust-native, agent-first Fabric CLI ⭐ HIGHEST VALUE

**URL:** https://github.com/iemejia/fabio  
**Stars:** 3 | **Forks:** 2 | **Language:** Rust (99.3%) | **Latest:** v0.20.0, June 10, 2026  
**Author:** Ismael Mejia

A Rust-built CLI for Microsoft Fabric with 74 command groups, 790+ subcommands. The `deploy` command uses `parameters.json` — described as "a superset of fabric-cicd's YAML `parameter.yml`, expressed in JSON for agent-native tooling consistency." Implements all four substitution types with:
- JSONPath-native `key_value_replace` (not just regex)
- Content-hash recomputation after each transformation layer
- Cascading `_ALL_` wildcard
- `$ENV:VAR_NAME` expansion
- `$workspace.id`, `$workspace.name`, `$items.Type.Name.id` dynamic variables
- Semantic model connection promotion with model-specific overrides
- Structured JSON output by default; consistent error codes; stdin/stdout piping

**Why great:** The first tool treating Fabric PBIP deployment as a composable, pipeable, agent-callable operation. Structured JSON output + error codes = first-class agent tool. The JSON parameter format is a drop-in replacement path from fabric-cicd YAML. Released v0.20.0 on the day of this scout run.

**Why invisible:** 3 stars. Zero blog promotion. Not in any "top fabric CI/CD tools" list. Author is an active community member but not a self-promoter.

**RC fit:** Extremely high — the agent-native PBIP deploy primitive the power-platform plugin is missing. Before recommending Python fabric-cicd for agent-driven workflows, `fabio` is the right call.

**License:** Not verified at fetch — verify before recommending.

---

### 2. `powerofbi.org` — lakehouse-JSON pattern for Data Pipeline parameterization

**URL:** https://www.powerofbi.org/2025/08/09/fabric-deployment-pipeline-rule-to-set-data-pipeline-parameters/  
**Author:** Benoit / powerofbi.org | **Date:** August 2025

Solves the gap that Fabric deployment pipelines have no parameter rules for Data Pipelines (only semantic models). Pattern: store environment config as JSON in a per-stage lakehouse (`Data Pipeline Parameters.json`); a "Read Parameters" notebook exits via `mssparkutils.notebook.exit(json.dumps(config))`; downstream activities parse it via `@activity('Read Deployment Parameters').output.result.ExitValue`. Only ONE deployment rule needed: change the notebook's default lakehouse from DEV to TEST.

**Why great:** Production-grade GA workaround for a documented gap. The "single rule + JSON config file" pattern is elegant — handles URIs, database names, vault references, all in one rule. Stage name stored in warehouse table enables conditional report formatting.

**Why invisible:** Single-author blog, no SEO, published Aug 2025. Not linked from any major Fabric resource list.

**RC fit:** High — knowledge-bank entry for "Data Pipeline parameters across deployment stages."

---

### 3. `microsoft/fabric-cicd` issue #839 — `.platform` displayName parameterization silent failure

**URL:** https://github.com/microsoft/fabric-cicd/issues/839  
**PR #840** in flight

Neither `find_replace` nor `key_value_replace` are applied to `.platform` files during deployment, despite documentation claiming support. Primary use case: changing `$.metadata.displayName` per environment ("Sales Dashboard [DEV]" vs "Sales Dashboard"). All approaches fail silently — no error, just no replacement. Workaround: Python preprocess `.platform` files before `publish_all_items()`, restore after.

**Why great:** A silent gotcha that burns every practitioner who reads the docs and tries to parameterize display names. Simple workaround once known; impossible to debug without this issue.

**Why invisible:** Buried in GitHub issues. Not in any "PBIP gotchas" blog post.

**RC fit:** High — `[BUG/GOTCHA]` knowledge-bank entry. Any PBIP deployment skill must warn on `.platform` exclusion.

---

### 4. `alisonpezzott/pbi-ci-cd-isv-multi-tenant` — ISV multi-tenant per-tenant parameterization pattern

**URL:** https://github.com/alisonpezzott/pbi-ci-cd-isv-multi-tenant  
**Stars:** 13 | **Forks:** 29 | **Author:** Alison Pezzott

CI/CD template for ISV distribution across multiple customer tenants. Two config files: `config.json` (workspace IDs + data sources per branch) and `config-isv.json` (per-tenant credentials + `semanticModelsParameters` with `SqlServerInstance`, `SqlServerDatabase`). Uses `ms-fabric-cli` not fabric-cicd. GitHub Actions deploys to all tenants in `config-isv.json` on merge to main.

**Why great:** Only fetched example of per-tenant PBIP parameterization (ISV scenario). The `semanticModelsParameters` pattern is tenant-scoped (not environment-scoped), a distinct shape from `parameter.yml`. The 29 forks vs 13 stars ratio signals active adaptation.

**Why invisible:** 13 stars, single commit shown, ms-fabric-cli is less-documented than fabric-cicd.

**RC fit:** Medium-high — ISV/multi-tenant deployment scenario schema candidate for power-platform plugin.

---

### 5. `kerski/fabric-dataops-patterns` — `git diff` scoped deploy + synchronous refresh validation gate

**URL:** https://github.com/kerski/fabric-dataops-patterns  
**Stars:** 62 | **Forks:** 16 | **Author:** John Kerski | https://www.kerski.tech

Three non-obvious production patterns:
1. **`git diff` scoped deploy** — only changed semantic models get deployed per push (not full-workspace rebuild)
2. **Synchronous refresh validation gate** — `Invoke-SemanticModelRefresh` wraps the async Power BI API with polling against "Get Refresh Execution Details" endpoint, then runs DAX Query View tests
3. **`definition.pbir` interrogation** — reads the report's PBIR definition to distinguish thin reports (external connection) from embedded semantic model reports and routes deployment accordingly
4. **"Prime the pipeline" documented requirement** — first deploy always requires manual credential configuration before refresh succeeds

**Why great:** The `git diff` scoped deploy is a production-grade pattern not in official fabric-cicd guidance. The synchronous refresh gate + DAX testing is a complete DataOps loop. `definition.pbir` interrogation is the most practical use of the PBIR format for deployment logic found in this scout.

**Why invisible:** 62 stars, niche practitioner blog, not linked from official PBIP resources.

**RC fit:** High — three knowledge-bank entries + strong PBIP deployment skill blueprint.

---

### 6. `NatVanG/fab-inspector` — declarative JSON rules validator for PBIP/PBIR

**URL:** https://github.com/NatVanG/fab-inspector  
**Stars:** 85 | **Forks:** 11 | **Author:** NatVanG | **Latest:** v3.3.0, June 9, 2026 | **License:** MIT

Deterministic, declarative JSON-rules engine for validating Fabric artifacts (PBIP/PBIR folders + published workspace items). JSONLogic operators + custom operators (`daxquery`, `sqlquery`, `apiget`, `dfsget`, `scannerapi`). Targets local CI folders, REST API queries, OneLake metadata. Output formats: Console, HTML (visual wireframes), JSON, PNG, GitHub/ADO. 11 base checks. Explicitly designed for AI-friendly (LLM-generatable) rule authoring.

**Why great:** A deployment pre-gate layer orthogonal to parameterization — validates that the PBIP structure/report governance meets standards before deploy fires. The `daxquery`/`sqlquery` operators enable live-model validation rules. The AI-friendly design is a double fit for RC. Supersedes the semi-dormant `NatVanG/PBI-Inspector` (found in prior scout, Nov 2023 dormant) — the name change makes it invisible to those who starred the old one.

**Why invisible:** 85 stars but the name-changed successor is unfindable from the prior repo. v3.3.0 shipped June 9, 2026 — very recent.

**RC fit:** High — PBIP deployment validation skill, complementary to the deploy skill.

---

### 7. `darkanita/PBIP_Fabric_Reference_Guide` — "parameter rules only after first deploy" gotcha

**URL:** https://github.com/darkanita/PBIP_Fabric_Reference_Guide  
**Stars:** 0 | **Forks:** 1 | **Author:** darkanita

Practitioner reference guide with two undocumented gotchas:
1. **Parameter rules require live artifacts** — rules can only be configured AFTER first deployment; so the first deploy ALWAYS uses DEV connection strings
2. **Manual "Update all" required** — after a PR merges to main, users must manually trigger Git→Workspace sync; no automatic sync exists

**Why great:** Both gotchas silently break "automated CI/CD" setups on first run. Not documented in official resources.

**Why invisible:** 0 stars, 1 fork. Zero SEO.

**RC fit:** Medium-high — gotcha knowledge-bank entries.

---

### 8. `kegottschalk/FabricDeployExtension` — Azure DevOps task extension for PBIP

**URL:** https://github.com/kegottschalk/FabricDeployExtension  
**Stars:** 0 | **Forks:** 0 | **Author:** Kevin Gottschalk | **Status:** "not ready for prime-time"

Azure DevOps extension wrapping FabricPS-PBIP with GUI tasks: Fabric Report Deploy and Fabric Semantic Model Deploy. The semantic model task accepts `ServerName` and `DatabaseName` as explicit pipeline parameters — making connection rebinding accessible to non-Python ADO users.

**Why relevant:** Only ADO extension for PBIP deployment found in this scout.

**Why not ranked higher:** 0 stars, self-deprecated, not published to ADO Marketplace. Watch only.

**RC fit:** Low-medium — reference for the "ADO GUI pipeline" path.

---

### 9. Marc Lelijveld hybrid CI/CD architecture (data-marc.com, 2024)

**URL:** https://data-marc.com/2024/07/09/fabric-ci-cd-with-git-deployment-and-release-strategies/  
**Author:** Marc Lelijveld (MVP)

Structural framework: Git integration on DEV only, deployment pipelines for TEST/PROD. Three parameterization paths: metadata-driven lakehouse config, DevOps variable substitution via find/replace during Git sync, Update Parameter REST API post-deploy. Key constraint: PBIR reports cannot deploy through Fabric deployment pipelines.

**Why relevant:** The Update Parameter REST API path is under-documented. The PBIR-deployment-pipeline constraint shapes every PBIP architecture decision.

**Popularity penalty:** Marc is a well-known MVP — moderate down-rank. But the PBIR constraint and REST API path are specific enough to earn a knowledge-bank slot.

---

## Dropped and why

| Find | Reason |
|---|---|
| `m-kovalsky/semantic-link-labs` | Covers Direct Lake migration, not multi-environment PBIP deploy parameterization |
| `RuiRomano/pbip-demo` | Standard fabric-cicd + Service Principal deployment; no novel parameterization pattern |
| `pbi-tools/pbi-tools` full CLI | Deployment manifest is interesting but targets PBIX/BIM, not PBIP/TMDL; docs marked "To come" |
| `donovanwhite/fabric-cicd-framework` | Adds warehouse SQL schema deploy on top of fabric-cicd; 1★, SQL-specific, not PBIP-parameterization |
| `saikiran10496/PowerBI-PBIP-Import` | Thin wrapper around FabricPS-PBIP; no novel parameterization; 0★ |
| `TemplateMechanics/pbi-pilot` | AI-harness for development-time PBIP editing, not deployment parameterization; 0★ |
| Official Microsoft docs | Explicitly down-ranked per scout brief |
| `microsoft/fabric-cicd` main repo | Official/famous; the reference baseline, not a fringe find |
| Fabric Variable Library Medium posts | Shallow, vendor-adjacent; covered by the more authoritative Jon Lunn find |
| `NatVanG/PBI-Inspector` (old) | Semi-dormant Nov 2023; superseded by `fab-inspector` |
| `JosiahSiegel/claude-plugin-marketplace` powerbi-master skills | Competitor/reference but not a PBIP env-var find; out of scope |

---

## The load-bearing structural finding

Two distinct "variable layers" in a PBIP project are routinely conflated by practitioners:

**Layer A — Source-controlled variables** (in PBIP files — PQ parameters, lakehouse GUIDs, connection strings) — parameterized via `parameter.yml` before/during deploy. fabric-cicd handles these.

**Layer B — Post-deploy runtime variables** (deployment pipeline rules, Variable Libraries, REST API Update Parameter, FabricPS-PBIP `Set-SemanticModelParameters`) — applied AFTER the artifact is in the workspace. Rules require live artifacts.

The canonical mistake: trying to use deployment-pipeline parameter rules at first-deploy time (they don't exist yet — `darkanita` documents this). The two-layer mental model is the missing conceptual frame most PBIP deployment writeups don't articulate, and it's where most "CI/CD broken on first run" incidents originate.

**The single highest-value find:** `iemejia/fabio` — Rust-native, agent-first, 3 stars, v0.20.0 shipped June 10 2026. The JSON-output + composable piping design makes it the right primitive for agent-driven PBIP deployment — before recommending the Python library for agentic workflows.

---

## Structured Output

```json
{
  "status": "complete",
  "summary": "Scout run on PBIP deployment variables and parameterization. 9 ranked shortlist items; 10 dropped with reasons. Top find: iemejia/fabio (Rust-native agent-first Fabric CLI, 3 stars, v0.20.0 June 10 2026). Key structural finding: two-layer mental model (source-controlled vs post-deploy runtime) is the missing conceptual frame behind most first-deploy failures.",
  "deliverables": [
    "docs/research/2026-06-10-pbip-deployment-variables/report.md",
    "docs/idea-board.md (PBIP scout section appended)"
  ],
  "handoff_recommendation": {
    "to_specialist": "rc-deep-research",
    "on": "iemejia/fabio",
    "verify": [
      "License (not confirmed at fetch)",
      "PBIP TMDL/PBIR format support confirmed vs PBIX-only",
      "Production use evidence beyond the repo itself",
      "parameters.json superset-of-parameter.yml claim verified against actual schema",
      "Agent-calling patterns: structured JSON on param-sub operations confirmed"
    ]
  },
  "confidence": 0.82,
  "next_actions": [
    "Append shortlist to docs/idea-board.md",
    "Hand iemejia/fabio to rc-deep-research for verification brief",
    "Add .platform displayName parameterization gotcha as knowledge-bank entry to power-platform plugin",
    "Add two-layer mental model as PBIP deployment skill primer"
  ]
}
```

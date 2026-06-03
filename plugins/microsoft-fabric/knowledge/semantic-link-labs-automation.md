# semantic-link-labs: Python automation for Fabric semantic models

**Last reviewed:** 2026-06-03 · **Confidence:** high (primary Microsoft sources, retrieved 2026-06-03).
**Owner:** `fabric-semantic-model-engineer` (primary); `fabric-admin` (BPA/audit workflows).
**Sources:** [microsoft/semantic-link-labs (GitHub)](https://github.com/microsoft/semantic-link-labs), [Semantic Link overview — Microsoft Learn](https://learn.microsoft.com/en-us/fabric/data-science/semantic-link-overview).
**Discovery credit:** [Data Goblins — power-bi-agentic-development](https://github.com/data-goblin/power-bi-agentic-development) — surfaced this library as high-leverage for agentic semantic-model work.

---

## What it is

`semantic-link-labs` (`microsoft/semantic-link-labs`) is a **Microsoft-maintained Python library** that runs **inside Fabric notebooks** and exposes programmatic operations on semantic models, reports, lakehouses, and admin surfaces. The import alias is `sempy_labs`:

```python
import sempy_labs as labs
```

It originated as tooling for the **Direct Lake migration path** (import → Direct Lake) and has since expanded into a broad automation toolkit. It runs inside the Fabric notebook kernel — it is **not a local or CI-side library**; execution requires a Fabric capacity-attached notebook session.

---

## Subpackages

| Subpackage | Surface it wraps |
|---|---|
| `sempy_labs.lakehouse` | Lakehouse operations (tables, partitions, maintenance) |
| `sempy_labs.report` | Report-level operations (pages, visuals, themes) |
| `sempy_labs.admin` | Tenant/workspace admin surfaces |
| `sempy_labs.deployment_pipeline` | Fabric deployment pipeline automation |
| `sempy_labs.directlake` | Direct Lake framing, guardrail checks, migration |
| `sempy_labs.environment` | Fabric environment management |
| `sempy_labs.graph` | Microsoft Graph integration |
| `sempy_labs.semantic_model` | TOM access, model-level operations |

---

## Highest-leverage capabilities for an agent

### 1. Programmatic Best Practice Analyzer (BPA) audits

Run the **Best Practice Analyzer** against any workspace's semantic model from a notebook — no need to open Power BI Desktop:

```python
labs.run_model_bpa(dataset="My Semantic Model", workspace="MyWorkspace")
```

Returns a structured DataFrame of rule violations with severity, rule name, and affected object. Agents can parse the output and emit a prioritized fix list. This is the fastest way to surface design issues across multiple models without manual Desktop sessions.

### 2. Vertipaq Analyzer

Run **Vertipaq Analyzer** (column-store memory + cardinality audit) programmatically:

```python
labs.vertipaq_analyzer(dataset="My Semantic Model", workspace="MyWorkspace")
```

Returns per-table, per-column, per-relationship memory stats. Use it to identify hot columns, oversized tables, and cardinality that will blow SKU guardrails in Direct Lake on-SQL mode. Pairs naturally with the Direct Lake fallback investigation workflow in [`direct-lake-and-semantic-models.md`](direct-lake-and-semantic-models.md).

### 3. Direct Lake migration + guardrail checks

Migrate an **import-mode** model to **Direct Lake** in a single orchestrated call — the library handles schema mapping, lakehouse binding, and framing:

```python
labs.migrate_model_to_direct_lake(
    dataset="My Semantic Model",
    workspace="MyWorkspace",
    lakehouse="MyLakehouse",
)
```

Check whether a model is within the Direct Lake **guardrails** for its SKU (row limits, column limits, table counts) before committing:

```python
labs.check_direct_lake_guardrails(dataset="My Semantic Model", workspace="MyWorkspace")
```

[unverified — exact method signatures may vary by library version; verify against the GitHub repo before using in production.]

### 4. Tabular Object Model (TOM) access

`sempy_labs.semantic_model` exposes the **Tabular Object Model** — the full model graph (tables, columns, measures, relationships, hierarchies, translations, perspectives) — as Python objects. Use this to:

- Enumerate all measures and their DAX expressions for bulk review or migration
- Modify model metadata (descriptions, formatting strings, display folders) programmatically
- Script cross-model consistency checks (naming conventions, hidden-column hygiene)

### 5. Cross-workspace deployment

Deploy semantic models and reports across workspaces programmatically — useful in CI/CD pipelines that Fabric deployment pipelines can't cover (e.g. dynamic workspace-per-tenant patterns):

```python
labs.deploy_semantic_model(
    source_workspace="Dev Workspace",
    target_workspace="Prod Workspace",
    dataset="My Semantic Model",
)
```

[unverified — method name and exact signature; verify against repo. As of 2026-06-03 this capability exists in some form but API surface changes frequently.]

---

## Which lane — semantic-link-labs vs TMDL vs `fab` CLI

| Question | Reach for | Why |
|---|---|---|
| Programmatic audit, analysis, or migration **inside a running Fabric notebook** | **semantic-link-labs** (`sempy_labs`) | Python-native; returns DataFrames; works against live workspace models without file export |
| **Source-of-truth authoring**, git-diffable model definition, DAX in text | **TMDL / PBIP** | Human-readable, version-controlled, the standard for model review and PR-based ALM |
| **Terminal / CI ops** — workspace item listing, upload/download, promotion scripting | **`fab` CLI** (`ms-fabric-cli`) or `fabric-cicd` | File-system-like workspace operations; fits shell scripts and CI pipelines; no notebook kernel needed |

The lanes are **complementary, not competing**. A mature ALM workflow uses all three: TMDL as source of truth in git → `fab`/`fabric-cicd` to promote across environments → semantic-link-labs for post-deploy validation audits (BPA + Vertipaq) and migration helpers.

---

## How it fits this plugin's agents

**`fabric-semantic-model-engineer`** — primary consumer. Reach for semantic-link-labs when:

- A client asks "how healthy is this model?" → BPA + Vertipaq Analyzer notebook gives an auditable answer in minutes.
- The task is migrating an import-mode model to Direct Lake → `migrate_model_to_direct_lake` + `check_direct_lake_guardrails` is the sanctioned path before manually reshaping gold tables.
- Cross-workspace model deployment falls outside what deployment pipelines handle.
- TOM inspection is needed to audit or bulk-update model metadata.

Cross-link: [`direct-lake-and-semantic-models.md`](direct-lake-and-semantic-models.md) covers the Direct Lake modes and guardrail design constraints that semantic-link-labs's migration helpers enforce at runtime.

**`fabric-admin`** — secondary consumer. BPA audits run at workspace or tenant scale surface policy violations (missing descriptions, non-compliant naming, unoptimized measures) that an admin needs for governance reporting. `sempy_labs.admin` wraps tenant-level surfaces that complement Fabric REST APIs.

---

## Gotchas and caveats

1. **Runs in Fabric notebooks only.** There is no pip-installable local-execution path that works against a live Fabric tenant without a capacity-attached kernel. Do not route this into local CI steps or recommend it for non-Fabric environments.

2. **Early-access / rapid churn.** Semantic Link (the underlying Microsoft feature) carries an "early access" label in some Fabric capability maps. The library version increments frequently; method signatures, return schemas, and available subpackages have changed across minor versions. **Always verify against the current GitHub repo** (`microsoft/semantic-link-labs`) before citing a specific API. Mark any specific method invocation `[unverified — check current version]` when you cannot confirm against the live repo.

3. **Auth is implicit inside a Fabric notebook.** The library uses the notebook session's Fabric identity — no separate credential setup is needed, but it means the caller's workspace permissions gate what the library can operate on. Admin-surface calls (`sempy_labs.admin`) require Fabric admin or capacity admin roles.

4. **Not a replacement for deployment pipelines or git integration.** For standard dev/test/prod promotion, Fabric's built-in deployment pipelines + Git integration remain the ALM backbone (see [`fabric-alm-cicd.md`](fabric-alm-cicd.md)). semantic-link-labs fills the gaps (programmatic validation, migration, dynamic multi-workspace patterns) — it does not replace the structured ALM toolchain.

5. **BPA rules are configurable but defaults cover the Microsoft community ruleset.** [unverified — custom ruleset injection mechanism; verify against repo documentation.]

---

## Sources

- [microsoft/semantic-link-labs — GitHub](https://github.com/microsoft/semantic-link-labs) — library source, README, subpackage docs. Retrieved 2026-06-03.
- [Semantic Link overview — Microsoft Learn](https://learn.microsoft.com/en-us/fabric/data-science/semantic-link-overview) — Microsoft's official overview of Semantic Link and its Fabric notebook integration. Retrieved 2026-06-03.
- **Discovery credit:** [Data Goblins — power-bi-agentic-development](https://github.com/data-goblin/power-bi-agentic-development) — Kurt Buhler's marketplace surfaced semantic-link-labs as a high-leverage tool for agentic semantic-model workflows. Content in this doc is written independently from primary Microsoft sources.

**Related knowledge:** [`direct-lake-and-semantic-models.md`](direct-lake-and-semantic-models.md) · [`fabric-alm-cicd.md`](fabric-alm-cicd.md) · [`fabric-2026-capability-map.md`](fabric-2026-capability-map.md)

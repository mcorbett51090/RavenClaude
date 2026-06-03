# Power BI / Fabric agentic development toolchain — 2026 landscape

> **Last reviewed:** 2026-06-03. Primary sources: Microsoft Fabric CLI (`fab`) documentation at https://learn.microsoft.com/en-us/fabric/cicd/fabi (retrieved 2026-06-03); Tabular Editor docs at https://docs.tabulareditor.com/ (retrieved 2026-06-03); semantic-link-labs GitHub repo at https://github.com/microsoft/semantic-link-labs (retrieved 2026-06-03); Deneb at https://deneb-viz.github.io/ and https://github.com/deneb-viz/deneb (retrieved 2026-06-03); PBIP/TMDL format docs at https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview (retrieved 2026-06-03). Items marked `[unverified — training knowledge]` have not been confirmed against live documentation in this session.
>
> **Discovery credit:** the framing of Power BI/Fabric as an *agentic development* landscape — pairing model-quality tooling, CLI ops, notebook automation, and doc tools into a coherent agent workflow — was mapped in the [`data-goblin/power-bi-agentic-development`](https://github.com/data-goblin/power-bi-agentic-development) marketplace (Kurt Buhler). The content here is written from underlying Microsoft and tooling primary sources; it does not reproduce Data Goblins material.
>
> **Cross-link:** for deep Python notebook automation against semantic models and workspaces, see [`../../microsoft-fabric/knowledge/semantic-link-labs-automation.md`](../../microsoft-fabric/knowledge/semantic-link-labs-automation.md).

---

## Why this doc exists

An agent working on Power BI and Fabric semantic models, reports, and CI/CD pipelines operates across a set of distinct tooling surfaces that are individually documented but rarely mapped against each other. This file describes the full landscape as of 2026 and tells an agent or developer which lane to use for which task. The goal is to reduce the "what tool do I reach for?" question to a single reference lookup.

---

## The source format layer — TMDL, PBIP, PBIR

Before any tooling makes sense, the source format must be right. Power BI's native `.pbix` is a binary container — not diff-able, not merge-able, not generatable by an agent. The Power BI team ships three text-based formats as the source layer:

### TMDL — Tabular Model Definition Language

TMDL is the text representation of a Power BI semantic model (data model, measures, relationships, roles, perspectives). A TMDL folder tree replaces the binary model in a PBIP project or a Tabular Editor–managed model. Every table, measure, column, and relationship is a readable `.tmdl` file. This is the format that:

- Can be committed to git and reviewed as a diff.
- Can be generated or edited by an agent (structured text with a defined grammar).
- Is consumed by Tabular Editor and by the `fab` CLI.
- Is validated by the Tabular Editor Best Practice Analyzer (BPA).

Source: Microsoft Learn TMDL overview `[unverified — training knowledge: confirm against current Fabric docs]`.

### PBIP — Power BI Project folder format

A PBIP is the unpacked project container: a folder that holds a `.pbip` entry file, a `definition/` subtree for the report (PBIR JSON), and a separate `*.SemanticModel/` subtree for the model (TMDL or the legacy model format). Committing the PBIP folder to git gives the team a text-diffable, CI/CD-friendly source. This is the correct unit to place under source control — not the binary `.pbix`. Source: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview (retrieved 2026-06-03).

### PBIR — Power BI Enhanced Report Definition

Within a PBIP, the report definition lives in a `definition/` folder as JSON files (`report.json`, `page.json` per page, `visual.json` per visual container). This is the PBIR Enhanced format. It is the source of truth for report structure and is the format an agent writes directly when generating report visuals programmatically. Full authoring reference: [`pbir-enhanced-reference.md`](pbir-enhanced-reference.md). Debug runbook: [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md).

---

## The model-quality lane — Tabular Editor, BPA, and C# scripting

### Tabular Editor

Tabular Editor (community edition TE2; commercial TE3) is the primary developer tool for authoring, reviewing, and validating Power BI and Analysis Services semantic models outside Power BI Desktop. It reads TMDL directly, provides a full TOM (Tabular Object Model) editor, and is the standard tool for:

- Bulk measure authoring and editing.
- Adding or validating `Description`, `DisplayFolder`, and `FormatString` on measures (the metadata triad — see [`../best-practices/enforce-measure-metadata.md`](../best-practices/enforce-measure-metadata.md)).
- Running the Best Practice Analyzer.
- Scripting bulk model changes in C#.

Source: https://docs.tabulareditor.com/ (retrieved 2026-06-03). Tabular Editor is also available as a Fabric external tool integration [unverified — training knowledge].

### Best Practice Analyzer (BPA)

BPA is a built-in Tabular Editor capability that scans the semantic model against a configurable rule set and reports violations. The standard Microsoft community rule set covers: unused measures, measures missing descriptions, measures missing format strings, calculated columns that should be measures, direct-typed relationships with wrong data types, and more.

In CI/CD, BPA can be run non-interactively via `TabularEditor.exe BPA <model-path> -r <rules.json>` to gate a PR on model quality. `[unverified — training knowledge: confirm CLI invocation syntax against your TE version]`.

### C# scripting in Tabular Editor

Tabular Editor exposes the full TOM object graph to a C# scripting surface. This allows bulk operations: iterate all measures and set a `FormatString` based on a naming pattern, rename a table and cascade its references, generate a scaffold of measures from a list, or validate `DisplayFolder` hierarchy consistency. Scripts run locally in Tabular Editor or non-interactively in CI.

Agent authoring note: C# scripts for Tabular Editor are short, structured, and templatable — an agent can generate them from a specification. The scripts are not compiled binaries; they execute in TE's embedded scripting host.

---

## The CI/CD terminal lane — `fab` CLI (microsoft/fabric-cli)

The `fab` CLI is Microsoft's command-line tool for Fabric workspace and item operations. It provides a file-system-like interface to Fabric: `fab cd`, `fab ls`, `fab cp`, `fab rm`. It is used for:

- Deploying PBIP/TMDL artifacts from a repository to a Fabric workspace.
- Fetching workspace items to the local file system (roundtrip to source control).
- CI/CD pipeline steps: publish a semantic model after BPA passes, deploy a report definition, promote across workspaces.

Source: https://learn.microsoft.com/en-us/fabric/cicd/fabi (retrieved 2026-06-03). The `fab` CLI is generally available (GA) as of the retrieval date; verify the current GA status of specific sub-commands before using them in a production pipeline `[unverified specifics — confirm against current release notes]`.

**Which lane:** use `fab` when the task is workspace/item CRUD, deployment, or CI/CD pipeline steps. Do not use it for semantic model inspection or DAX evaluation — those belong to Tabular Editor or semantic-link-labs.

---

## The notebook automation lane — semantic-link-labs

`semantic-link-labs` (GitHub: https://github.com/microsoft/semantic-link-labs, retrieved 2026-06-03) is a Microsoft-published Python library designed for Fabric notebooks. It wraps the `sempy.fabric` surface with higher-level, use-case-oriented functions for:

- Semantic model documentation generation (auto-document all measures, tables, and columns).
- BPA-equivalent model scanning from a notebook.
- Workspace and model management (list items, refresh, metadata queries).
- Lakehouse and Direct Lake integration.
- Generating TMDL from a notebook workflow.

This is the correct surface when the automation task is Python-native, runs inside a Fabric notebook (or a notebook-equivalent environment), and operates on the semantic model or workspace metadata rather than on individual files. For the full API surface, see [`../../microsoft-fabric/knowledge/semantic-link-labs-automation.md`](../../microsoft-fabric/knowledge/semantic-link-labs-automation.md).

**Which lane:** use semantic-link-labs for notebook-based Python automation of Fabric/Power BI models — documentation generation, model scanning, metadata queries. Use Tabular Editor for GUI-adjacent or CI-BPA work; use `fab` CLI for workspace deployment.

---

## The visualization lane — Deneb (Vega / Vega-Lite)

Deneb is a certified Power BI custom visual (Daniel Marsh-Patrick) that renders Vega and Vega-Lite declarative JSON specifications inside the Power BI client, with no gateway dependency and full support for Power BI cross-filtering interactivity. It is the agentic authoring target for bespoke chart types: a Vega-Lite spec is a JSON document that an agent can generate, validate, and embed without a graphical designer.

Full custom-visual decision guide (Deneb vs SVG-via-DAX vs R/Python vs core visuals): [`power-bi-custom-visuals-toolkit.md`](power-bi-custom-visuals-toolkit.md).

Primary sources: https://deneb-viz.github.io/ and https://github.com/deneb-viz/deneb (retrieved 2026-06-03).

---

## The doc and workspace discovery lane — pbi-search and fabric-workspace-reader MCP

Two tools support the "read-before-you-write" step in agentic workflows:

**pbi-search** `[unverified — training knowledge: verify current availability and invocation]` is a tool from the Data Goblins ecosystem for searching across Power BI content (measures, tables, report pages) in a workspace. It surfaces the vocabulary the model already uses, which an agent needs before generating new DAX measures or report visuals that must match existing naming. Discovery source: [`data-goblin/power-bi-agentic-development`](https://github.com/data-goblin/power-bi-agentic-development).

**fabric-workspace-reader MCP** `[unverified — training knowledge: verify current availability]` is a Model Context Protocol server from the Data Goblins ecosystem that exposes Fabric workspace contents to an MCP client (such as Claude Code). It allows an agent to enumerate workspace items, read semantic model metadata, and ground its outputs against the live workspace state before authoring. Discovery source: [`data-goblin/power-bi-agentic-development`](https://github.com/data-goblin/power-bi-agentic-development).

**When to use these:** at the start of any agentic session that will author new measures, visuals, or workspace items — before generating any output, use these tools to read what already exists.

---

## Which lane for which task

| Task | Primary tool | Notes |
|---|---|---|
| Commit semantic model to git | TMDL in a PBIP folder | Text-diffable, CI-friendly |
| Commit report definition to git | PBIR in a PBIP folder | JSON visual.json / page.json |
| Author or edit measures in bulk | Tabular Editor + C# scripting | Full TOM access |
| Validate measure metadata (description, format, folder) | Tabular Editor BPA | Standard rule set + custom rules |
| Run BPA in CI/CD | `TabularEditor.exe` BPA CLI | `[unverified — confirm CLI flags]` |
| Deploy model/report to Fabric workspace | `fab` CLI | `fab cp` or `fab deploy` |
| Fetch workspace items to local FS | `fab` CLI | Roundtrip to source control |
| Python notebook: document a model | semantic-link-labs | Generates measure/table docs |
| Python notebook: scan model quality | semantic-link-labs BPA wrapper | Notebook-native BPA |
| Python notebook: workspace metadata | `sempy.fabric` + semantic-link-labs | List items, refresh, query |
| Bespoke chart type (cross-filtering needed) | Deneb (Vega-Lite JSON spec) | Agent-generatable spec |
| Simple static badge or icon | SVG via DAX measure | No custom visual required |
| Statistical chart (ggplot2, seaborn) | R or Python visual | Requires gateway `[unverified]` |
| Discover existing model vocabulary | pbi-search, fabric-workspace-reader MCP | Read before writing `[unverified]` |
| Inspect `.pbix` without Power BI Desktop | powerbi-editor MCP (pbix-mcp) | Bundled in this plugin (§9 of CLAUDE.md) |

---

## The agentic workflow in sequence

A well-ordered agentic session on a Power BI/Fabric engagement proceeds in this sequence:

```
1. DISCOVER  — read the existing workspace, model vocabulary, and PBIP tree
               (fabric-workspace-reader MCP, pbi-search, PBIP folder read)

2. VALIDATE  — run BPA against the current TMDL; note model-quality gaps
               (Tabular Editor BPA or semantic-link-labs BPA wrapper)

3. AUTHOR    — generate/edit TMDL measures (Tabular Editor / C# script / direct TMDL edit)
               generate/edit PBIR report visuals (Deneb spec or PBIR visual.json)
               enforce metadata triad on every new measure (see enforce-measure-metadata.md)

4. TEST      — run BPA again; confirm no new violations; spot-check DAX correctness
               (power-bi-engineer + power-platform-tester agents)

5. DEPLOY    — push PBIP to git; CI runs BPA + prettier; fab CLI deploys to workspace
               (fab CLI, CI/CD pipeline)

6. DOCUMENT  — generate model documentation notebook
               (semantic-link-labs in a Fabric notebook)
```

---

## See also

- [`pbir-enhanced-reference.md`](pbir-enhanced-reference.md) — canonical PBIR Enhanced visual.json authoring reference
- [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) — PBIR Enhanced deploy/load debug runbook
- [`power-bi-custom-visuals-toolkit.md`](power-bi-custom-visuals-toolkit.md) — custom visual decision guide (Deneb, SVG, R/Python)
- [`../../microsoft-fabric/knowledge/semantic-link-labs-automation.md`](../../microsoft-fabric/knowledge/semantic-link-labs-automation.md) — deep semantic-link-labs API reference
- [`../best-practices/enforce-measure-metadata.md`](../best-practices/enforce-measure-metadata.md) — every measure ships with DisplayFolder + Description + FormatString
- [`../best-practices/tmdl-pbip-source-control-hygiene.md`](../best-practices/tmdl-pbip-source-control-hygiene.md) — TMDL/PBIP committed as text source, not binary .pbix, and Windows long-path fix
- [`../agents/power-bi-engineer.md`](../agents/power-bi-engineer.md) — the agent that owns this toolchain

---

_Last reviewed: 2026-06-03 by `claude`_

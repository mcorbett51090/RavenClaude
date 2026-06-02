---
name: power-bi
description: Veteran-level reference for Power BI — PBIP project structure + git, semantic model design, DAX patterns + performance, deployment pipelines, refresh / gateway troubleshooting, integration with Power Platform solutions / ALM. Used by `power-bi-engineer` (primary).
---

# Power BI Skill

**Purpose:** Provide veteran-level reference and patterns for the new `power-bi-engineer` agent — semantic model design, DAX, PBIP git workflows with Azure DevOps, deployment, refresh troubleshooting, and integration with Power Platform solutions/ALM.

## When to Use

- Designing or reviewing semantic models and DAX.
- Setting up or troubleshooting PBIP projects in git / Azure DevOps.
- Deployment pipeline or refresh/gateway issues.
- Coordinating Power BI artifacts with solution ALM or flows.

## How to Use This Skill

1. Start with this `SKILL.md` for architecture and decision guidance.
2. Dive into `resources/*.md` for specifics (PBIP structure, git patterns, DAX, etc.).
3. Combine with `solution-alm-engineer` for end-to-end pipelines that include Power BI.

## Core Principles

- **PBIP is mandatory** for anything going into source control or ADO. Binary .pbix files are not reviewable or mergeable.
- Treat the semantic model as code (model definition + measures).
- Parameters + Deployment Rules > hard-coded values or multiple branches.
- Test refresh and deployment in clean workspaces/environments.
- Keep models focused — prefer composite models over monolithic ones for large scenarios.

## Key Areas

- PBIP folder structure and what to commit / .gitignore
- Git workflows and common ADO/PBIP issues (large JSON diffs, merge conflicts, parameter handling)
- DAX performance patterns and tools (DAX Studio, VertiPaq Analyzer, Tabular Editor)
- Deployment strategies (Power BI Deployment Pipelines vs custom ADO pipelines with service principals / REST / Tabular Editor CLI)
- Refresh, gateways, incremental refresh, and XMLA
- Integration with Dataverse sources and solution packaging

## Recommended Resources
- `resources/pbip-structure-and-git.md`
- `resources/dax-patterns-and-performance.md`
- `resources/deployment-and-pipelines.md`
- `resources/refresh-gateway-troubleshooting.md`

## Knowledge bank pointers

For production-incident lessons (real customer engagements, with a decision tree + the workaround that resolved it), consult the plugin's [`knowledge/`](../../knowledge/) directory in addition to the resources above. The full §8a table is in [`../../CLAUDE.md`](../../CLAUDE.md); the Power BI–specific entry to know about:

- **[`knowledge/pbir-enhanced-report-loading.md`](../../knowledge/pbir-enhanced-report-loading.md)** — read before editing or building any **PBIR Enhanced** report's `definition/` JSON. Covers the `resourcePackages` + `version.json` "infinite spinner" trap, the ~June 2026 Fabric breaking change rejecting `prototypeQuery` on visuals, and the correct `nativeQueryRef` + `active` projection shape. Verified against 7 real Enhanced repos 2026-06-02.

This skill directly supports the new `power-bi-engineer` and ties into the enhanced ALM coverage for git/ADO scenarios.
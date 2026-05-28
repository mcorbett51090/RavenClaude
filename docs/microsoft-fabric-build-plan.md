# Microsoft Fabric plugin — execution-ready build plan

**Date:** 2026-05-28
**Status:** EXECUTION-SEQUENCED. Operationalizes [`microsoft-fabric-plugin-analysis.md`](microsoft-fabric-plugin-analysis.md) §8 (the plan as revised by the §7 expert review). When this plan and the analysis disagree, the analysis wins for *scope*; this plan wins for *sequencing + acceptance criteria*.
**Builder:** autonomous (Claude Opus 4.7), targeting a clean Linux checkout with the repo's CI gates green.

---

## 0. Definition of done (v0.1.0)

A consumer can `/plugin install microsoft-fabric@ravenclaude`, see **7 agents**, and dispatch any of them to get citation-grounded, decision-tree-driven Fabric guidance. All repo CI gates pass: `validate-marketplace` (no version drift), `validate-layout` (every file on the allow-list), prettier (whole-tree clean), frontmatter check (strict-YAML on all 7 agents), and `audit-gates.sh`. The `repo-guide.html` regenerates with the new plugin + its 7 agent cards.

---

## 1. The 7 agents (v0.1.0)

| Agent | One-line | Key skills/knowledge it drives |
|---|---|---|
| `fabric-architect` | workspace/domain/capacity topology + the **store-selection** + **shortcut/mirror/auto-mirror** decisions + medallion design | store-decision-tree, data-movement-tree, medallion-on-onelake, capacity-finops |
| `lakehouse-engineer` | Lakehouse, Spark/Python notebooks, Delta/V-Order/NEE/Liquid-Clustering, **medallion**, **materialized lake views**, environments/pools | medallion-on-onelake, store-decision-tree, capability-map |
| `warehouse-engineer` | Fabric Warehouse T-SQL, dimensional modeling, ACID, SQL endpoint, burstable perf, CLS/OLS | store-decision-tree, onelake-security, capacity-finops |
| `data-factory-engineer` | the **data-movement decision**: pipelines, Dataflow Gen2 (Fast Copy), Copy job (CDC), Mirroring, connectors, orchestration | data-movement-tree, medallion-on-onelake |
| `realtime-intelligence-engineer` | Eventstream → Eventhouse → KQL → Real-Time dashboard → Activator; anomaly detection | data-movement-tree, capability-map |
| `fabric-semantic-model-engineer` | **Direct Lake** semantic models (on-OneLake vs on-SQL), framing, fallback avoidance, TMDL/PBIP, the power-bi-engineer seam | direct-lake-and-semantic-models, medallion-on-onelake |
| `fabric-admin` | capacity admin + **FinOps**, **OneLake security** (RLS/CLS/OLS + GA/preview matrix), domains, Purview, sensitivity labels, **ALM** (Git + deployment pipelines + fabric-cli/fabric-cicd), tenant settings | capacity-finops, onelake-security, fabric-alm-cicd |

`works_with` cross-refs (per scenario schema): every agent lists 2-5 collaborators including, where relevant, `power-platform/power-bi-engineer`, `data-platform/*`, `applied-statistics/applied-statistician`, `ravenclaude-core/security-reviewer`, `ravenclaude-core/architect`.

---

## 2. Files to create

```
plugins/microsoft-fabric/
├── .claude-plugin/plugin.json          # name, version 0.1.0, requires core >=0.7.0, keywords
├── CLAUDE.md                           # team constitution (roster, routing, 14 house opinions, anti-patterns, seams)
├── README.md                           # consumer-facing: what it is, install, prereqs (fab CLI), roster
├── CHANGELOG.md                        # ## [0.1.0] — 2026-05-28
├── agents/
│   ├── fabric-architect.md
│   ├── lakehouse-engineer.md
│   ├── warehouse-engineer.md
│   ├── data-factory-engineer.md
│   ├── realtime-intelligence-engineer.md
│   ├── fabric-semantic-model-engineer.md
│   └── fabric-admin.md
├── hooks/
│   ├── check-fabric-anti-patterns.sh   # advisory PreToolUse; chmod +x
│   └── hooks.json                       # PreToolUse Write|Edit|MultiEdit registration
├── knowledge/
│   ├── fabric-store-decision-tree.md
│   ├── fabric-data-movement-decision-tree.md
│   ├── medallion-on-onelake.md
│   ├── direct-lake-and-semantic-models.md
│   ├── capacity-finops-and-throttling.md
│   ├── onelake-security-and-governance.md
│   ├── fabric-alm-cicd.md
│   └── fabric-2026-capability-map.md
└── templates/
    ├── fabric-workspace-and-capacity-plan.md
    ├── medallion-lakehouse-spec.md
    ├── fabric-ingestion-design.md
    ├── direct-lake-semantic-model-spec.md
    ├── fabric-capacity-cost-review.md
    └── fabric-alm-runbook.md
```

Plus edits to existing files:
- `.claude-plugin/marketplace.json` — append the `microsoft-fabric` entry (version `0.1.0`); bump the catalog `metadata.version`.
- `plugins/data-platform/CLAUDE.md` — reciprocal Fabric handoff (§10 + house opinion #12), bump `data-platform` patch version + its `marketplace.json` + plugin.json in sync.
- `docs/architecture.md` — Status table row.
- `README.md` (root) — "what's in each plugin" sub-section.
- `repo-guide.html` — regenerated via `scripts/generate-repo-guide.py`.

No `.repo-layout.json` change (all paths match existing `plugins/*/…` globs). No `NOTICE.md` (nothing imported). No bundled MCP.

---

## 3. Build sequence (each step independently committable)

**P1 — Skeleton + catalog.** `plugin.json`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`; append to `marketplace.json`. Gate: `python3 -m json.tool` on both manifests; version parity.

**P2 — Knowledge bank (8 docs).** Write the citation-grounded reference spine *first* — agents reference these, so they must exist to avoid dead links. Each doc: `Last reviewed: 2026-05-28`, confidence notation, MS Learn URLs, the §7 accuracy corrections baked in. Gate: links resolve; prettier clean.

**P3 — Agents (7).** Full scenario frontmatter (strict-YAML; no unquoted colon-space in `description`). Each: mission, the decision-discipline (traverse the relevant tree first), house opinions it enforces, skills/knowledge it drives, Capability Grounding Protocol inheritance, Output Contract + SOP block, escalation/seams. Gate: `check-frontmatter.py` passes.

**P4 — Templates (6) + hook.** Hook advisory (`exit 0`), `FABRIC_STRICT=1` to block, narrow file-type filter; `chmod +x`; `hooks.json`. Gate: `bash -n`; executable bit; `shellcheck`-clean if available.

**P5 — Seams + meta.** Edit `data-platform/CLAUDE.md` (reciprocal handoff) + sync its version. Update `architecture.md` + root `README.md`.

**P6 — Regenerate + gate.** `scripts/generate-repo-guide.py`; `npx prettier --write .`; `python3 scripts/check-frontmatter.py`; `scripts/audit-gates.sh` (or document any locally-unrunnable gate). Commit, push, draft PR.

---

## 4. Acceptance criteria per workload

- **Store decision** — `fabric-architect` traverses `fabric-store-decision-tree.md` (lakehouse/warehouse/eventhouse/SQL DB/Cosmos/shortcut) before naming a store; never keyword-matches.
- **Data movement** — `data-factory-engineer` traverses `fabric-data-movement-decision-tree.md` (mirroring/copy-job/copy-activity/eventstream/dataflow-gen2 + in-Fabric auto-mirror); states "free to replicate, not free to query" for mirroring.
- **Medallion** — `lakehouse-engineer` applies per-layer V-Order/file-size/maintenance from `medallion-on-onelake.md`; offers MLV vs notebook vs Dataflow Gen2; never serves bronze to Direct Lake.
- **Direct Lake** — `fabric-semantic-model-engineer` distinguishes Direct Lake on OneLake (no fallback) vs on SQL (fallback); shapes gold for framing; routes DAX to `power-bi-engineer`.
- **Security** — `fabric-admin` separates workspace roles (control plane) from OneLake security (data plane); cites the engine GA/preview matrix + schema-enabled prerequisite.
- **FinOps** — `fabric-admin` sizes to average+smoothing, recommends capacity isolation + reservations, reads the Capacity Metrics app.
- **ALM** — `fabric-admin` prescribes Git integration + deployment pipelines dev/test/prod, fabric-cli/fabric-cicd; no hand-edited prod.

---

## 5. v0.2.0+ backlog (deferred, recorded so it isn't lost)
- `fabric-data-ai-engineer` — notebooks/MLflow/AutoML, **Fabric Data Agents**, Operations Agents, AI functions, Copilot, Foundry/ontology.
- Skills directory (the analysis kept the v0.1.0 surface as agents + knowledge + templates; promote recurring procedures to `skills/` once `/wrap` surfaces them — matching the applied-statistics pattern).
- Wire the plugin into the Researcher staleness sweep so `fabric-2026-capability-map.md` gets re-dated (Fabric ships monthly).
- Evaluate bundling/declaring a Fabric MCP (REST/`fab`) once a stable community server exists.
- A `scenarios/` bank when the first real engagement scenario surfaces.

---

## 6. Risk register (post-review)
| Risk | Mitigation |
|---|---|
| Currency rot (Fabric ships monthly) | retrieval-dated citations + `fabric-2026-capability-map.md` + Researcher sweep |
| power-bi-engineer misroute | the litmus-test seam wording (§8.4 of the analysis) in both plugins' CLAUDE.md |
| data-platform keeps absorbing Fabric | reciprocal edit to `data-platform/CLAUDE.md` (P5) |
| Hook false positives | advisory-only at v0.1.0; promote to blocking only after consumer feedback |
| Roster build time | knowledge-first sequencing; each step independently committable so partial progress always ships |

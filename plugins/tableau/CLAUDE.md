# Tableau Plugin — Team Constitution

> Team constitution for the `tableau` Claude Code plugin — specialist agents for the full Tableau surface: the **developer** craft (VizQL, calculations, dashboard design), the **data** craft (modeling, extracts, performance, Prep), and the **platform** craft (Server/Cloud governance, content ALM, embedding, and the next-gen Pulse/Tableau-Next/CRM-Analytics surface).
>
> **Orientation:** domain-specific to Tableau analytics work. For the domain-neutral team inherited by every plugin (architect, coders, reviewers, project-manager), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`tableau-viz-engineer`](agents/tableau-viz-engineer.md) | Chart-type/VizQL selection, calculations (LOD `FIXED`/`INCLUDE`/`EXCLUDE`, table calcs, level-of-detail vs granularity), dashboard layout/interactivity, formatting, accessibility. | "which chart?"; "this LOD/table-calc is wrong"; "build/refactor this dashboard"; "why is this number double-counting?" |
| [`tableau-data-architect`](agents/tableau-data-architect.md) | Data modeling (relationships vs joins vs blends), extracts vs live + Hyper, incremental refresh, Tableau Prep flows, workbook/query performance tuning. | "relationship or join?"; "extract or live?"; "this workbook is slow"; "design the Prep flow" |
| [`tableau-admin`](agents/tableau-admin.md) | Server/Cloud governance, projects/permissions, row-level security, content promotion/ALM (Tableau Content Migration / `tabcmd`/REST), embedding (Embedding API v3, Connected Apps/JWT), and the Pulse/Tableau-Next/CRM-Analytics surface. | "permissions/RLS design"; "promote content dev→prod"; "embed a viz securely"; "should this be Pulse vs a dashboard?" |

Three coherent personas (developer / data / platform). Per the marketplace house rule, this plugin ships specialist *doing*-agents and forks **no** core *review* role — viz/data/security review escalates to `ravenclaude-core/security-reviewer` (RLS, Connected Apps/JWT, embedding auth) and `ravenclaude-core/code-reviewer` (calc/Prep correctness). **Sub-agents do not spawn other sub-agents** — only the Team Lead delegates.

---

## 2. Routing rules (Team Lead)

- **"Which chart / why is my calc/LOD wrong / build this dashboard"** → `tableau-viz-engineer`.
- **"Relationship vs join vs blend / extract vs live / slow workbook / Prep flow"** → `tableau-data-architect`.
- **"Permissions / RLS / promote content / embed securely / Pulse vs dashboard"** → `tableau-admin`.
- **RLS or embedding *auth* (Connected Apps, JWT, user filters as a security control)** → design in `tableau-admin`, **escalate the security verdict to `ravenclaude-core/security-reviewer`**.
- **Warehouse/semantic modeling upstream of Tableau** → escalate to `data-platform` / `microsoft-fabric`. **Salesforce source data / CRM Analytics-on-platform** → seam with `salesforce`. **Power BI comparison** → `power-platform/power-bi-engineer`.

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **Model granularity before you calculate.** Know each table's grain and the viz's level of detail before writing a single LOD; most "wrong number" bugs are grain bugs, not calc bugs.
2. **Relationships by default; joins/blends with a reason.** Use the logical layer (relationships) unless a documented need forces a physical join or a data blend.
3. **The deliverable is the question answered, not the dashboard.** Chart type follows the question (comparison/trend/distribution/correlation/part-to-whole), never aesthetics.
4. **Extract by default for performance; live only when freshness demands it.** Name the freshness requirement that justifies a live connection.
5. **Performance is designed, not tuned later.** Filter at the source, minimize marks, avoid high-cardinality quick filters and string calcs in the hot path.
6. **RLS is a security control, not a convenience filter.** User filters / data-policy RLS get the same scrutiny as any access control and escalate to security review.
7. **Promote, don't rebuild.** Content moves dev→test→prod through a repeatable migration path (Content Migration Tool / REST API), never hand-republished.
8. **Embed with Connected Apps + JWT, never a trust ticket hack or embedded credentials.**
9. **Volatile claims carry a retrieval date** (version-specific limits, feature availability, Pulse/Tableau-Next positioning) and are re-verified before quoting to a client.

---

## 4. Anti-patterns the agents flag

- A calculated field where an LOD or a fixed grain was needed (double-counting / wrong totals).
- A table calc whose addressing/partitioning is left to default and silently wrong.
- A data blend used where a relationship would have been correct (and faster).
- A live connection with no stated freshness requirement (paying latency for nothing).
- High-cardinality quick filters / "show all values" on a large extract.
- RLS implemented as a hidden filter rather than an enforced data policy / user filter, with no security review.
- Content hand-republished across environments instead of promoted.
- Embedding via legacy trusted tickets or embedded service-account creds instead of Connected Apps/JWT.
- A two-point "trend," a truncated/aspect-distorted axis, or a dual-axis not synchronized.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before an agent says "I can't" or asserts a platform fact, it must: (1) check the knowledge bank + decision trees; (2) **traverse the relevant `## Decision Tree:` section** before selecting a method (chart type, relationship-vs-join, extract-vs-live, RLS mechanism) — don't keyword-match; (3) try the next-easiest defensible path before declaring blocked; (4) escalate with the mandatory phrasing. Volatile Tableau facts (version limits, Hyper internals, Pulse/Tableau-Next features) carry inline `[verify-at-build]` / `[unverified — training knowledge]` markers per the Claim-Grounding discipline. See [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 6. Output Contract

```
Question: <the business question, in observable terms>
Grain & model: <table grains; relationship/join/blend choice + why>
Method: <chart type / calc / LOD / table-calc choice + WHY (from the decision tree)>
Build: <fields, calcs (with the LOD/table-calc spelled out), viz spec>
Performance: <extract/live + the freshness reason; the perf levers applied>
Governance: <permissions/RLS/promotion/embedding notes; security escalation if any>
Verdict: <plain-language answer tied to the decision>
```

Plus the cross-plugin **Structured Output Protocol** JSON block ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)).

---

## 7. Knowledge bank & best practices

- [`knowledge/`](knowledge/) — reference docs with `Last verified:` dates + Mermaid **decision trees** (chart selection, relationship vs join vs blend, extract vs live, LOD vs table calc, RLS mechanism, embedding auth, content promotion, **data-freshness pipeline** — Bridge vs Cloud-native, full vs incremental, stale-dashboard diagnosis). The agents traverse these before choosing a method.
- [`best-practices/`](best-practices/) — named, citable rules (one per file), grounded in the knowledge bank and surfaced in the marketplace repo-guide + dashboard Guidance tab.
- **Cross-plugin (render loop)** [`../ravenclaude-core/knowledge/visual-feedback-loop.md`](../ravenclaude-core/knowledge/visual-feedback-loop.md) — read when iterating a workbook toward pixel-perfect: **structural-first** — read the `.twb`/`.twbx` zone geometry directly (the reliable path), with a Tableau image-export (`tabcmd`/REST) screenshot as the *secondary* check; structural-only is a complete pass. Backs the `tableau-viz-engineer` **Visual feedback loop** section.
- [`skills/`](skills/) — step-by-step procedures: [`workbook-performance-audit`](skills/workbook-performance-audit/SKILL.md) (evidence-first Performance Recorder ladder) and [`embedding-connected-apps-jwt`](skills/embedding-connected-apps-jwt/SKILL.md) (Connected App / Direct Trust JWT + Embedding API v3; security-gated).
- [`scenarios/`](scenarios/) — unverified, dated field-note bank consulted as a **secondary** source (mandatory unverified preamble); see the [scenario-retrieval skill](../ravenclaude-core/skills/scenario-retrieval/SKILL.md).
- [`hooks/`](hooks/) — `flag-tableau-anti-patterns.sh`, an **advisory** (never-blocking) `PreToolUse(Write|Edit)` hook flagging the §4 anti-patterns it can grep in `.twb`/`.tds` XML.
- [`templates/`](templates/) — fill-in templates for performance audits, governance/RLS plans, embedding design specs, and dashboard design specs.

---

## Value-add completeness (pilot build-out 2026-06-05)

This plugin was completed against the marketplace value-add menu. Every item was considered;
each is either **built** or carries a one-line disposition for an auditable "every item examined."

| # | Item | Disposition | Notes |
|---|---|---|---|
| 1 | `scenarios/` bank | **BUILT** | 4 dated scenarios (LOD order-of-ops, embedding JWT+RLS, Server→Cloud refresh, perf-recorder) + README, mirroring the power-platform schema. |
| 2 | Decision-tree knowledge | **BUILT** | [`knowledge/data-freshness-pipeline-decision-trees.md`](knowledge/data-freshness-pipeline-decision-trees.md) — 3 trees (Bridge vs Cloud-native, full vs incremental, stale-dashboard diagnosis), grounded + cited + dated. |
| 3 | `skills/` | **BUILT** | [`skills/workbook-performance-audit/`](skills/workbook-performance-audit/SKILL.md) + [`skills/embedding-connected-apps-jwt/`](skills/embedding-connected-apps-jwt/SKILL.md). |
| 4 | `hooks/` advisory | **BUILT** | [`hooks/flag-tableau-anti-patterns.sh`](hooks/flag-tableau-anti-patterns.sh) — 6 anti-patterns on `.twb`/`.tds`, advisory (exit 0), `PreToolUse(Write\|Edit)`, registered in `hooks/hooks.json`. |
| 5 | `templates/` | **BUILT** | workbook-performance-audit, governance-rls-plan, embedding-design-spec, dashboard-design-spec. |
| 6 | Bundled MCP server | **RECOMMEND, not bundle** | The **official `tableau/tableau-mcp`** (Apache-2.0, `npx @tableau/mcp-server` `[verify-at-use]`) exists and is read-oriented — but it is **per-tenant + authenticated** (`SERVER`/`SITE_NAME`/`PAT_NAME`/`PAT_VALUE` — a PAT secret), so per [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) it is the **RECOMMEND** row (can't hardcode a consumer-specific URL/secret), like power-platform's Dataverse MCP. See the recommend block below. No third-party content vendored → **no `NOTICE.md`** needed. |
| 7 | LSP server | **N/A** | Tableau has no general code LSP surface (workbooks are XML/UI artifacts, calcs are an embedded DSL, not a language served by an LSP). Nothing real to ship. |
| 8 | Monitors / `bin/` / output-styles / settings.json defaults / themes | **N/A** | No long-running monitor target (refresh monitoring lives in Tableau itself); no CLI binary to wrap (`tabcmd`/REST are documented in agents/knowledge, not re-implemented); an output-style for "viz review" is already served by the team **Output Contract** (§6) — a separate output-style would duplicate it; no settings/theme defaults are domain-meaningful here. |
| 9 | `CHANGELOG.md` / `NOTICE.md` | **CHANGELOG BUILT; NOTICE N/A** | [`CHANGELOG.md`](CHANGELOG.md) added (top entry = this build-out). No third-party content bundled → no `NOTICE.md`. |
| 10 | Quickstart / cross-plugin seams / output contracts | **PRESENT (no gap)** | All 3 agents carry `quickstart` + `scenarios` frontmatter + `works_with` seams; the team **Output Contract** (§6) + Structured Output Protocol are in place; seams to `data-platform`/`salesforce`/`power-platform`/`security-reviewer` are documented (§2, §8). |

### Recommended (not bundled) MCP — the official Tableau MCP server

> **Verified 2026-06-05** against the official repo [`github.com/tableau/tableau-mcp`](https://github.com/tableau/tableau-mcp) (Apache-2.0). The package name, auth env vars, and tool surface are version-current — **`[verify-at-use]`** the exact published npm name and read/write verbs before relying on them (the claim-grounding discipline applies).

Tableau's **first-party** MCP server connects an agent to Tableau Cloud/Server to query published
data sources, explore content/workbook metadata, and retrieve view images. It is **NOT bundled** —
it is per-tenant + authenticated (a site URL + a Personal Access Token), so a hardcoded
`mcpServers` entry can't carry a consumer-specific URL/secret. It is **recommended + consumer-configured**:

```jsonc
// consumer's MCP config — PAT is a per-tenant secret; store a reference, never a literal
{
  "mcpServers": {
    "tableau": {
      "command": "npx",
      "args": ["-y", "@tableau/mcp-server@latest"],   // pin the tested version [verify-at-use]
      "env": {
        "SERVER": "https://<your-tableau-cloud-or-server>",
        "SITE_NAME": "<your_site>",
        "PAT_NAME": "<pat-name>",
        "PAT_VALUE": "<reference-to-secret>"
      }
    }
  }
}
```

**Owned by** `tableau-admin` (tenant connection) + `tableau-data-architect` (data queries).
**Trigger:** when the user asks an agent to *query live Tableau data / inspect a published data
source or workbook on the site*, point them at this server rather than describing the REST API.
**Boundary:** it is for **live site queries + metadata**, NOT for `.twb`/`.tds` file authoring and
NOT a replacement for the REST API / `tabcmd` in a promotion pipeline. **Any PAT/secret-handling
or write-capable use escalates the auth decision to `ravenclaude-core/security-reviewer`.**

---

## 8. Escalating out of the Tableau team

- **`ravenclaude-core/security-reviewer`** — RLS, Connected Apps/JWT, embedding auth, data-policy access.
- **`data-platform` / `microsoft-fabric`** — warehouse + semantic modeling upstream of Tableau.
- **`salesforce`** — Salesforce source objects, CRM Analytics-on-platform.
- **`power-platform/power-bi-engineer`** — Power BI comparison / migration.
- **`ravenclaude-core/documentarian`** / **`project-manager`** — stakeholder deliverables / engagement RAID.

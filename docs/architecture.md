# RavenClaude — Architecture

This repo is a **private Claude Code plugin marketplace**. Each plugin inside it bundles a set of agents, skills, hooks, rules, and templates that a consumer project can install through Claude Code's native `/plugin marketplace add` mechanism. The repo itself isn't loaded into consumer projects — only individual plugins are.

> **Audience for this doc:** anyone working *on* the marketplace (adding a plugin, changing a plugin, reviewing a PR). For instructions on *installing* the plugins as a consumer, see the root [`README.md`](../README.md). For team rules that ship inside `ravenclaude-core`, see [`plugins/ravenclaude-core/CLAUDE.md`](../plugins/ravenclaude-core/CLAUDE.md).

---

## The marketplace model

```mermaid
flowchart TB
    subgraph marketplace["RavenClaude — private plugin marketplace (this repo)"]
        direction TB
        catalog["<code>.claude-plugin/marketplace.json</code><br/>catalog: lists every plugin"]
        subgraph plugindir["<code>plugins/</code>"]
            direction LR
            core["<b>ravenclaude-core</b><br/>domain-neutral<br/>14 specialist agents<br/>dispatch, gates, hooks, templates"]
            pp["<b>power-platform</b><br/>Microsoft Power Platform<br/>10 specialist agents<br/>13 skills (9 imported MIT + 4 in-house)<br/>bundles pbix-mcp server"]
            future["<i>future plugins</i><br/>finance, EdTech,<br/>Salesforce, …"]
        end
        catalog -.->|references| plugindir
    end

    consumer["<b>Consumer project</b> — any Claude Code project on a collaborator's machine<br/>plugin extracted to <code>~/.claude/plugins/cache/</code><br/>plugin's <code>CLAUDE.md</code> auto-loads; agents become available to Team Lead"]

    marketplace ==>|"<code>/plugin install &lt;name&gt;@ravenclaude</code><br/>read-only, one-way distribution"| consumer

    classDef hub fill:#1f2937,stroke:#9ca3af,color:#f9fafb
    classDef plugin fill:#0f766e,stroke:#5eead4,color:#ecfeff
    classDef future fill:#374151,stroke:#9ca3af,color:#e5e7eb,stroke-dasharray: 4 3
    classDef consumer fill:#7c2d12,stroke:#fed7aa,color:#fff7ed
    class catalog hub
    class core,pp plugin
    class future future
    class consumer consumer
```

**One-way distribution.** A consumer's `marketplace update` pulls the latest version from this repo into their local cache. The consumer cannot push back — their changes stay on their machine. The feedback path (lessons, fixes, new patterns) is the PR flow documented in [`CONTRIBUTING.md`](../CONTRIBUTING.md).

---

## Why plugins, not Expert repos

An earlier iteration of this project planned a "central hub + sibling Expert repos" pattern (RavenClaude as the hub, with separate `PowerPlatformExpert`, `SalesforceExpert` repos cloned alongside consumer projects). That model has been replaced by Claude Code's native plugin marketplace, which gives us the same separation with three concrete advantages:

| | Old "sibling Expert repos" model | Plugin marketplace model (current) |
|---|---|---|
| **Distribution** | Each consumer project's devcontainer clones each repo to a known sibling path | `/plugin install <name>@ravenclaude` — one command per plugin |
| **Updates** | Manual `git pull` in each cloned sibling | `/plugin marketplace update ravenclaude` updates all plugins at once |
| **Discovery** | Consumer has to know which Experts to clone | Claude Code surfaces all available plugins in `/plugin` |
| **Activation** | Consumer's `CLAUDE.md` has to opt in by referencing paths | Plugin's own `CLAUDE.md` auto-loads when active |
| **Versioning** | Implicit via git SHA | Explicit `version` field in each `plugin.json`; consumers can pin |

Domain separation is still a first-class concern — it just lives in *separate plugins inside this repo* rather than separate repos. The rule from the old architecture ("Power Platform specifics don't pollute domain-neutral patterns") still holds; it's now enforced by `plugins/ravenclaude-core/` vs. `plugins/power-platform/` rather than by `RavenClaude/` vs. `PowerPlatformExpert/`.

---

## What goes where

The marketplace contains a domain-neutral core plus one plugin per significant domain. Anything domain-specific lives in its own plugin, never in `ravenclaude-core`.

| Lives in `plugins/ravenclaude-core/` | Lives in a domain plugin (e.g. `plugins/power-platform/`) |
|---|---|
| Generic agent role definitions (architect, coder, tester, reviewer, designer, documentarian, project-manager, prompt-engineer, deep-researcher, partner-success-manager, etc.) | Domain-specific agent definitions (`power-fx-engineer`, `flow-engineer`, `dataverse-architect`, future Salesforce / finance / EdTech specialists) |
| Cross-domain skills (dispatch playbook, worktree helpers, generic code-review patterns) | Domain-specific skills (Power Platform's `dataverse-web-api`, `pcf-controls`, `power-apps-code-apps`, etc.) |
| Cross-domain hooks (format-on-write, guard-destructive, remind-tests) | Domain-specific hooks (only if a hook is meaningless outside that domain) |
| Generic rules (coding standards, security baseline, git workflow, agent collaboration) | Domain-specific rules (Power Platform's "solutions, always" and "managed in test+prod" opinions) |
| Generic templates (memos, runbooks, design specs, RAID logs, partner-success artifacts) | Domain-specific templates (a Dataverse data model spec, a flow run-history triage template, etc.) |

**Rule of thumb:** if it would be relevant to a Salesforce engagement AND a Power Platform engagement AND an iOS app project, it belongs in `ravenclaude-core`. If it only matters for one of them, it belongs in that one's plugin.

---

## Folder layout

```
RavenClaude/
├── .claude-plugin/
│   └── marketplace.json           ← catalog: lists every plugin in this marketplace
│
├── plugins/
│   ├── ravenclaude-core/
│   │   ├── .claude-plugin/plugin.json   ← manifest (name, version, author)
│   │   ├── CLAUDE.md                    ← team constitution that auto-loads
│   │   ├── agents/                      ← 13 specialist agent files
│   │   ├── skills/                      ← dispatch playbook, worktree helpers, etc.
│   │   ├── hooks/                       ← format-on-write, guard-destructive, remind-tests
│   │   ├── rules/                       ← coding-standards, security, git-workflow, agent-collab
│   │   └── templates/                   ← memos, runbooks, RAID logs, partner-success artifacts
│   │
│   └── power-platform/
│       ├── .claude-plugin/plugin.json   ← also declares bundled pbix-mcp MCP server
│       ├── CLAUDE.md
│       ├── NOTICE.md                    ← MIT attribution for imported skills + pbix-mcp
│       ├── agents/                      ← 10 specialist agent files
│       ├── hooks/                       ← check-house-opinions (advisory)
│       └── skills/                      ← 13 skills (9 imported Daniel Kerridge MIT + 4 in-house)
│
├── .claude/                       ← config for working ON this repo itself (NOT shipped)
│   └── settings.json              ← permissions + hooks for marketplace dev
│
├── .github/
│   └── pull_request_template.md   ← auto-loaded PR form for all contributions
│
├── docs/                          ← meta-repo docs (not shipped to consumers)
│   ├── architecture.md            ← this file
│   ├── access.md                  ← collaborator record
│   ├── best-practices/            ← cross-domain rules (with _TEMPLATE.md)
│   └── memory-bank/
│       ├── lessons-learned.md     ← reverse-chronological trial-and-error log
│       └── decision-log.md        ← reverse-chronological architectural decisions
│
├── CLAUDE.md                      ← working-on-the-marketplace constitution
├── CONTRIBUTING.md                ← how collaborators propose changes
└── README.md                      ← install instructions for consumers
```

Key boundary: **the `docs/` tree, `.claude/`, `.github/`, `CLAUDE.md`, `CONTRIBUTING.md`, and `README.md` at the repo root are NOT shipped to consumers.** They're meta-repo content — only the contents of `plugins/<plugin-name>/` are extracted when a consumer installs a plugin.

---

## How a consumer uses the marketplace

```bash
# In any Claude Code project on a collaborator's machine:
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude
/plugin install power-platform@ravenclaude     # if they need it
/reload-plugins
```

After install, each plugin's `CLAUDE.md` auto-loads into the consumer's Claude Code session. Agents defined under `plugins/<name>/agents/` become available to the Team Lead for dispatch. Skills under `plugins/<name>/skills/` are consulted on demand. Hooks, rules, and templates apply per the plugin's own configuration.

To pick up new versions:

```bash
/plugin marketplace update ravenclaude
/reload-plugins
```

The repo is private — see [`docs/access.md`](access.md) for the current collaborator list and the access-model rationale.

---

## How knowledge is captured

The marketplace has three layers of "memory," each with a different purpose and a different write path:

| Layer | Where it lives | Who writes to it | What goes here |
|---|---|---|---|
| **Consumer's auto-memory** | `~/.claude/projects/<project>/memory/` on the consumer's machine | The consumer's Claude session | Session-local context: user preferences, current task state, project facts. Private to that consumer. |
| **Plugin lessons** (cross-domain) | `docs/memory-bank/lessons-learned.md` (this repo) | Collaborators via PR | Cross-domain trial-and-error findings — *applies to any Claude work*. Reverse-chronological, newest first. |
| **Plugin best-practices** (cross-domain) | `docs/best-practices/<slug>.md` (this repo) | Collaborators via PR | Cross-domain rules with rationale + how-to-apply + provenance. One file per rule. Use [`_TEMPLATE.md`](best-practices/_TEMPLATE.md). |

**Domain-specific lessons** (e.g. a Power Platform-specific Dataverse rule) belong inside the relevant plugin's folder — for example, `plugins/power-platform/skills/<domain-skill>/resources/<rule>.md` — not in this repo's domain-neutral `docs/`.

**Flow when Claude (in any consumer project) discovers something non-obvious:**

1. Save in that project's auto-memory immediately so the current session benefits.
2. Decide where it generalizes:
   - **Specific to one domain** → goes inside that domain's plugin via a PR to this repo (`plugins/<plugin>/...`), and the relevant plugin's version is bumped.
   - **Applies across domains** → goes here, in `docs/memory-bank/lessons-learned.md` or `docs/best-practices/`, via a PR.
   - **Both** → write the cross-domain rule here, write the domain-specific deep-dive in the plugin, cross-link them.
3. Cite the propagation explicitly in the response so the user can verify the trail.

The PR flow itself is in [`CONTRIBUTING.md`](../CONTRIBUTING.md).

---

## Adding a new plugin

When a new domain matures past the point where it deserves its own plugin (Salesforce, finance, EdTech, etc.):

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json` with `name`, `description`, `version`, `author`, optional `license` and `keywords`.
2. Add `agents/`, `skills/`, `hooks/`, `rules/`, `templates/` subdirectories — only the ones the plugin actually needs.
3. Add `plugins/<plugin-name>/CLAUDE.md` as the team constitution that ships with the plugin.
4. Append the new plugin to the `plugins[]` array in `.claude-plugin/marketplace.json`.
5. If the plugin imports third-party content, add `plugins/<plugin-name>/NOTICE.md` with the license + attribution (see `plugins/power-platform/NOTICE.md` for the canonical form).
6. Open a PR following the **Marketplace / meta change** section of the PR template.
7. After merge, test the install from a separate Claude Code project: `/plugin marketplace update ravenclaude` then `/plugin install <plugin-name>@ravenclaude`.

The existing plugins are the reference implementations — `ravenclaude-core` for a "team patterns" plugin, `power-platform` for a "domain specialist team plus imported skills" plugin.

---

## Status

**Active plugins:**

| Plugin | Version | Description |
|---|---|---|
| [`ravenclaude-core`](../plugins/ravenclaude-core/) | 0.7.0 | Domain-neutral: 14 specialist agents (includes `data-engineer`; all with active Structured Output Protocol blocks), dispatch playbook with Cross-plugin dispatch section, gates, **5 hooks** (includes the advisory `guard-recursive-spawn`), contribution-staging workflow, templates, Cited-Adjudicator Escalation rule, audit-ci-gates skill + scaffold. **Capability Grounding Protocol now requires agents to enumerate alternative implementation paths from easiest to most difficult and try them in order before declaring blocked — no more "did you try X?" round-trips.** |
| [`power-platform`](../plugins/power-platform/) | 0.9.0 | Microsoft Power Platform: 11 specialist agents (includes `power-platform-tester`; all with active cross-plugin Structured Output Protocol blocks + licensing_impact field), 13 skills + advisory house-opinion hook covering **8 checks** + bundled pbix-mcp MCP server + knowledge bank capturing production lessons (programmatic cloud-flow creation via Dataverse Web API when the PA Management API is blocked). §5 reinforced with alternate-methods rule (REST → SDK → CLI → portal-with-automation-around-it laddering). |
| [`finance`](../plugins/finance/) | 0.2.0 | Corporate finance & FP&A: 7 specialist agents, 4 skills, 8 templates, advisory anti-pattern hook. §5 reinforced with alternate-methods rule (revenue-recognition framing, peer-comp vs DCF triangulation). Inherits `ravenclaude-core` protocols; requires `ravenclaude-core@>=0.5.0`. |
| [`regulatory-compliance`](../plugins/regulatory-compliance/) | 0.2.0 | Financial-regulatory: 6 specialist agents, 4 skills, 8 templates, 1 defensive PreToolUse PII-scrub hook. Field-experience positioning (BMA). §5 reinforced with alternate-methods rule (alternative frameworks, control-narrative gap documentation, primary vs derivative citation laddering). Inherits `ravenclaude-core` protocols. |
| [`web-design`](../plugins/web-design/) | 0.3.0 | Web design & build: 7 specialist agents, 4 skills, 8 templates, 1 advisory hook, and a knowledge bank with the 2026 "cutting edge yet simple" reference set (Linear, Vercel, Raycast, Resend, Cursor, v0, Tldraw, Cal.com). §5 reinforced with alternate-methods rule (grid → flex → subgrid, lighter library, build-time vs runtime laddering). Inherits `ravenclaude-core` protocols. |
| [`edtech-partner-success`](../plugins/edtech-partner-success/) | 0.1.0 | EdTech Partner Success Manager team: 6 specialist agents (partner-success-manager, success-playbook-designer, qbr-composer, learning-analytics-analyst, ferpa-comms-translator, partner-profile-curator), 4 skills (partner-health-scoring, success-plan-authoring, qbr-composition, rostering-data-quality), 8 templates, 1 advisory hook flagging PSM anti-patterns (action items without dates, generic boilerplate, unverified numeric claims, multi-partner names visible in `To:` lines, health-score status without named signals). Vertical-explicit but segment-agnostic (K-12 / higher-ed / corp L&D). Inherits `ravenclaude-core` protocols; requires `ravenclaude-core@>=0.7.0`. |
| [`data-platform`](../plugins/data-platform/) | 0.3.5 | Data-platform team: 4 specialist agents (database-setup-guide, etl-pipeline-engineer, dashboard-builder, connector-developer) for the **non-Microsoft / SMB** embedded-analytics lane (Supabase/Neon/RDS, Airbyte/Fivetran, Evidence/Superset/Metabase/Cube). 11 skills, 12 templates, advisory hook, 13-doc knowledge bank. Opinionated against per-viewer-priced BI. Reciprocal seam with `microsoft-fabric` (enterprise Microsoft hands off there). Requires `ravenclaude-core@>=0.7.0`. |
| [`applied-statistics`](../plugins/applied-statistics/) | 0.1.0 | "Is this difference/trend REAL?" — 1 specialist (applied-statistician), 5 skills, 5-doc knowledge bank, 4 templates, 1 advisory hook. Seams with data-platform ("is it correct?" vs "is it real?"). Requires `ravenclaude-core@>=0.7.0`. |
| [`microsoft-fabric`](../plugins/microsoft-fabric/) | 0.1.0 | Microsoft Fabric specialist team: 7 agents (fabric-architect, lakehouse-engineer, warehouse-engineer, data-factory-engineer, realtime-intelligence-engineer, fabric-semantic-model-engineer, fabric-admin) covering OneLake, Lakehouse/Delta/medallion, Warehouse, Data Factory, Real-Time Intelligence, Direct Lake, and platform admin (capacity FinOps, OneLake security, ALM). 8-doc citation-grounded knowledge bank (two Mermaid decision trees + a dated 2026 capability map), 6 templates, 1 advisory hook (14 house opinions). Built from a researched, expert-reviewed plan ([`microsoft-fabric-plugin-analysis.md`](microsoft-fabric-plugin-analysis.md)). Reciprocal seams with `data-platform` and `power-platform/power-bi-engineer`. Requires `ravenclaude-core@>=0.7.0`. |
| [`claude-app-engineering`](../plugins/claude-app-engineering/) | 0.1.0 | Claude app-engineering specialist team: 6 agents (claude-solution-architect, prompt-and-context-engineer, mcp-and-server-tools-engineer, agent-sdk-engineer, eval-engineer, claude-app-ops-engineer) for building production apps on the Claude API + Claude Agent SDK + MCP — build-surface decision, prompt caching, tool use, MCP servers + hosted server tools, Agent SDK/Managed Agents, evals, LLM FinOps. 9-doc dated-and-cited knowledge bank, 6 templates, 1 advisory hook (14 house opinions). Built from a researched, expert-reviewed plan ([`claude-app-engineering-plugin-analysis.md`](claude-app-engineering-plugin-analysis.md)). Ships no security/architect clone — escalates to core; reciprocal prior on `core/prompt-engineer`. The marketplace itself is the worked example. Requires `ravenclaude-core@>=0.7.0`. |

**Memory bank:** 4 lessons recorded (see [`memory-bank/lessons-learned.md`](memory-bank/lessons-learned.md)) — PMP discipline (project-manager), PSM discipline (partner-success-manager), mermaid for conceptual diagrams, and rebase-orphan branch cleanup.

**Decision log:** No entries yet — first decision will be recorded the next time an architectural choice deserves a written rationale.

**Planned plugins** (on the roadmap): Salesforce. EdTech is now shipping as `edtech-partner-success` (anchored on the PSM lane). See [`./plugin-roadmap-analysis.md`](./plugin-roadmap-analysis.md) for the original prioritization analysis behind the finance / regulatory-compliance / web-design selection.

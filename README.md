# 🐦‍⬛ RavenClaude

**A private Claude Code plugin marketplace** — bundled team rules, specialist agents, dispatch playbooks, and templates that travel with you across projects.

> 🎛 **[▶ Open the RavenClaude dashboard](https://mcorbett51090.github.io/RavenClaude/plugins/ravenclaude-core/dashboard.html)** — point-and-click editor for your `.ravenclaude/comfort-posture.yaml`: set per-tool file, network, shell, and package autonomy across three levels (deny → ask → allow) — per layer (user / local / project) and per individual permission — without editing YAML by hand. _(That link is the published, read-only preview.)_

> 🖥 **Working on this repo?** Launch the **functional local dashboard** (where **Save & apply** actually writes this repo's config) with one command: `bash scripts/open-dashboard.sh`. It kills any running dashboard server, starts a fresh one, and opens it in your browser automatically. _(VS Code users: a `.vscode/tasks.json` wired as the default build task — Ctrl/Cmd+Shift+B — runs the same script; `.vscode/` is gitignored, so add it locally if you want the keybinding.)_

> 📖 **[▶ View `repo-guide.html` rendered in your browser](https://mcorbett51090.github.io/RavenClaude/repo-guide.html)** — a self-contained single-page guide to every plugin, agent, skill, hook, rule, and template, with a searchable cross-plugin index. Regenerated from the manifests on every release.
>
> _(Or [view the raw HTML source](repo-guide.html), or download and open locally — no server, no build step.)_

Today this marketplace ships **11 plugins**:

- **[`ravenclaude-core`](plugins/ravenclaude-core/)** — domain-neutral Team Lead + 14 specialists (architect, coders, reviewers, designer, documentarian, deep-researcher, project-manager, partner-success-manager, prompt-engineer, data-engineer, etc.), plus dispatch playbooks (with a Cross-plugin dispatch section), gates, 22 skills, 11 hooks, templates, and the **cross-project contribution-staging loop**.
- **[`power-platform`](plugins/power-platform/)** — 11 Microsoft Power Platform specialists (Power Fx, flows, Power BI, Dataverse, model-driven, PCF, Copilot Studio, Power Pages, admin, ALM, tester), 18 skills, an advisory house-opinions hook covering 8 checks, and the bundled `pbix-mcp` MCP server.
- **[`finance`](plugins/finance/)** — 7 corporate-finance & FP&A specialists (FP&A analyst, financial modeler, controller, treasury, valuation, audit-prep, board-pack composer), 9 skills, templates, advisory anti-pattern hook.
- **[`regulatory-compliance`](plugins/regulatory-compliance/)** — 6 financial-regulatory specialists (AML/KYC, regulatory reporting, risk-and-controls, policy & procedure writer, examination prep, Bermuda-insurance), 9 skills, templates, defensive PII-scrub hook.
- **[`web-design`](plugins/web-design/)** — 7 web specialists (web architect, UX, visual, frontend implementer, content strategist, accessibility auditor, performance engineer) with WCAG 2.2 AA/AAA, Core Web Vitals, SEO/AEO, and Fluent + React discipline. 10 skills, templates, advisory web anti-pattern hook.
- **[`edtech-partner-success`](plugins/edtech-partner-success/)** — 6 K-12 EdTech partner-success specialists (partner-success manager, success-playbook designer, learning-analytics analyst, QBR composer, partner-profile curator, FERPA comms translator) with 12 skills and a knowledge bank of operating cadences.
- **[`data-platform`](plugins/data-platform/)** — 4 non-Microsoft/SMB data specialists (ETL pipeline, connector, database-setup, dashboard) with 11 skills and a deep knowledge bank (dbt, warehouse selection, ingestion, semantic modeling).
- **[`applied-statistics`](plugins/applied-statistics/)** — a statistical-analysis specialist with 5 skills (experiment design, regression, causal inference, time series, statistical review) and a citation-grounded knowledge bank.
- **[`microsoft-fabric`](plugins/microsoft-fabric/)** — 7 enterprise-Fabric specialists (architect, lakehouse, warehouse, Data Factory, Real-Time Intelligence, semantic model, admin) with a citation-grounded knowledge bank and advisory anti-pattern hook.
- **[`claude-app-engineering`](plugins/claude-app-engineering/)** — 6 specialists for building on the Claude API + Agent SDK + MCP (solution architect, prompt/context, MCP/server-tools, Agent SDK, eval, app-ops) with a citation-grounded knowledge bank.
- **[`azure-cloud`](plugins/azure-cloud/)** — 7 Azure infrastructure specialists (architect, Bicep IaC, Entra identity, network, app-platform, integration, ops) with a citation-grounded knowledge bank and advisory anti-pattern hook.

Salesforce remains on the roadmap.

---

## Install (recommended)

In any Claude Code project where you want the agents:

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude
# Optional — add only if you're working on Power Platform:
/plugin install power-platform@ravenclaude
/reload-plugins
```

That's it. The `ravenclaude-core` specialist agents become available to the Team Lead via the `spawn-team` skill, the dispatch skills (`spawn-team`, `new-worktree`, `cleanup-worktrees`, `create-pr`, `run-full-test-suite`) are loaded, and the format/lint/test hooks fire automatically. Installing `power-platform` adds its 11 specialists alongside.

To pin a specific version (recommended for client engagements where you don't want surprise updates):

```shell
/plugin marketplace add mcorbett51090/RavenClaude#<git-sha>
```

To update later:

```shell
/plugin marketplace update ravenclaude
/reload-plugins
```

---

## Local development install

If you want to iterate on this marketplace itself (or test a change before pushing):

```shell
# From any test project, point at your local checkout:
/plugin marketplace add /path/to/RavenClaude
/plugin install ravenclaude-core@ravenclaude
/reload-plugins
```

After editing files in `plugins/ravenclaude-core/` (or `plugins/power-platform/`), run `/plugin marketplace update ravenclaude` and `/reload-plugins` again to pick up the changes.

---

## Fallback — clone instead of install

If you're on a Claude Code plan or in an enterprise environment that restricts marketplace installs, you can clone this repo and copy the plugin folder manually:

```bash
git clone https://github.com/mcorbett51090/RavenClaude.git
# User scope (available across all your projects on this machine):
cp -r RavenClaude/plugins/ravenclaude-core/* ~/.claude/

# Or project scope (just one project):
cp -r RavenClaude/plugins/ravenclaude-core/* /path/to/your/project/.claude/
```

You lose auto-update and version pinning. To update, `git pull` and re-copy. Otherwise the agents, skills, hooks, rules, and templates work identically.

---

## What's in each plugin

### `ravenclaude-core`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 14 | `plugins/ravenclaude-core/agents/` |
| Skills | 22 (dispatch via `spawn-team`, `new-worktree` / `cleanup-worktrees`, `create-pr`, `run-full-test-suite`, `draft-agent-brief`, `structured-output`; the cross-domain staging loop `contribute-finding` / `review-staged-contributions`; the tribunal `thing` / `decision-review`; posture + capability skills `set-posture`, `permission-hygiene`, `environment-discovery`; quality skills `agent-quality-rubric`, `audit-ci-gates`, `cross-platform-determinism`, `knowledge-file-staleness-sweep`, `plugin-release-checklist`, `prompt-pattern-library`, `scenario-retrieval`; plus the `researcher/` meta-skill) | `plugins/ravenclaude-core/skills/` |
| Hooks | 11 (format-on-write, guard-destructive, remind-tests, enforce-layout, guard-recursive-spawn, capability-orientation, ensure-default-mode, reapply-posture, route-decision-review, thing-orchestrator, copilot-hook-adapter) | `plugins/ravenclaude-core/hooks/` |
| Rules | 4 (coding-standards, security, git-workflow, agent-collaboration) | `plugins/ravenclaude-core/rules/` |
| Commands | 4 (`/init-agent-ready`, `/dashboard`, `/set-posture`, `/wrap`) | `plugins/ravenclaude-core/commands/` |
| Templates | memos, runbooks, design specs, RAID logs, partner-success artifacts, agent-ready-repo scaffold | `plugins/ravenclaude-core/templates/` |

The team rules ship inside the plugin as [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md). Copy or adapt that into your consumer project's root `CLAUDE.md` and fill in your project's stack-specific gates (formatter, linter, type-checker, test runner).

For a full list of agents and when to spawn each, see the team-roster table in [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md) §5.

### `power-platform`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 11 (`power-fx-engineer`, `flow-engineer`, `power-bi-engineer`, `dataverse-architect`, `model-driven-engineer`, `solution-alm-engineer`, `power-platform-admin`, `pcf-developer`, `copilot-studio-engineer`, `power-pages-engineer`, `power-platform-tester`) | `plugins/power-platform/agents/` |
| Skills | 18 (a mix of imported MIT skills from Daniel Kerridge + in-house additions including `grounding-protocol`, `maintainability-review`, `power-automate`, `power-bi`, `plan-with-team`) | `plugins/power-platform/skills/` |
| Hooks | 1 advisory house-opinions hook covering 8 mechanically-detectable §3/§4 checks (GUIDs, default prefix, hard-coded URLs, binary .pbix, missing flow Try/Catch, premium-connector licensing note, Power Fx var/col prefix, plaintext secret in env-var default) | `plugins/power-platform/hooks/` |
| Bundled MCP | `powerbi-editor` (community `pbix-mcp`, MIT) — requires `pip install pbix-mcp` | declared in `plugins/power-platform/.claude-plugin/plugin.json` |

Domain-specific team constitution: [`plugins/power-platform/CLAUDE.md`](plugins/power-platform/CLAUDE.md). Inherits the neutral team from `ravenclaude-core` and extends with PP-specific routing, house opinions, and anti-patterns. See attribution in [`plugins/power-platform/NOTICE.md`](plugins/power-platform/NOTICE.md).

### `microsoft-fabric`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 7 (`fabric-architect`, `lakehouse-engineer`, `warehouse-engineer`, `data-factory-engineer`, `realtime-intelligence-engineer`, `fabric-semantic-model-engineer`, `fabric-admin`) | `plugins/microsoft-fabric/agents/` |
| Knowledge bank | 8 citation-grounded, retrieval-dated docs (store-selection + data-movement Mermaid decision trees, medallion-on-OneLake, Direct Lake two-mode, capacity FinOps, OneLake security GA/preview matrix, ALM/CI-CD, a dated 2026 capability map) | `plugins/microsoft-fabric/knowledge/` |
| Templates | 6 (workspace-and-capacity plan, medallion spec, ingestion design, Direct Lake model spec, capacity-cost review, ALM runbook) | `plugins/microsoft-fabric/templates/` |
| Hooks | 1 advisory anti-pattern hook (autotune-not-NEE, mirroring-free-unqualified, V-Order-off-on-gold, Direct-Lake-no-mode); `FABRIC_STRICT=1` to block | `plugins/microsoft-fabric/hooks/` |

Domain-specific team constitution: [`plugins/microsoft-fabric/CLAUDE.md`](plugins/microsoft-fabric/CLAUDE.md). Covers the **enterprise Microsoft / Fabric** lane (OneLake, Lakehouse, Warehouse, Data Factory, Real-Time Intelligence, Direct Lake, capacity FinOps, OneLake security, ALM). Seams reciprocally with `data-platform` (non-Microsoft/SMB embedded) and `power-platform/power-bi-engineer` (standalone Power BI / `.pbix`). No bundled MCP — documents the `fab` CLI / REST prerequisite. Built from a researched, expert-reviewed plan ([`docs/microsoft-fabric-plugin-analysis.md`](docs/microsoft-fabric-plugin-analysis.md)).

### `claude-app-engineering`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 6 (`claude-solution-architect`, `prompt-and-context-engineer`, `mcp-and-server-tools-engineer`, `agent-sdk-engineer`, `eval-engineer`, `claude-app-ops-engineer`) | `plugins/claude-app-engineering/agents/` |
| Knowledge bank | 9 citation-grounded, retrieval-dated docs (build-surface decision tree, dated 2026 capability map, prompt-caching playbook, tool-use + structured output, MCP server authoring, server-side tools + Files API, Agent SDK + Managed Agents, evals + quality, FinOps + reliability + security) | `plugins/claude-app-engineering/knowledge/` |
| Templates | 6 (architecture spec, prompt-and-caching design, MCP server spec, eval plan, cost model, Agent SDK runbook) | `plugins/claude-app-engineering/templates/` |
| Hooks | 1 advisory anti-pattern hook (hardcoded `sk-ant-` key, Messages API call with no `max_tokens`, retired model id, full-message logging); `CLAUDE_APP_STRICT=1` to block | `plugins/claude-app-engineering/hooks/` |

Domain-specific team constitution: [`plugins/claude-app-engineering/CLAUDE.md`](plugins/claude-app-engineering/CLAUDE.md). Covers building production apps on the **Claude API + Claude Agent SDK + MCP** (build-surface decision, prompt caching, tool use, MCP servers + hosted server tools, Agent SDK / Managed Agents, evals, LLM FinOps). Ships **no** security-reviewer/architect clone — AI-app security and cross-domain architecture escalate to `ravenclaude-core` (a reciprocal prompt-engineer prior was added to core). The marketplace itself is the worked example. No bundled MCP — documents the Anthropic SDK / Claude Agent SDK prerequisite. Built from a researched, expert-reviewed plan ([`docs/claude-app-engineering-plugin-analysis.md`](docs/claude-app-engineering-plugin-analysis.md)).

### `azure-cloud`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 7 (`azure-architect`, `bicep-iac-engineer`, `entra-identity-engineer`, `network-engineer`, `app-platform-engineer`, `integration-engineer`, `azure-ops-engineer`) | `plugins/azure-cloud/agents/` |
| Knowledge bank | 9 citation-grounded, retrieval-dated docs (landing zones & governance, IaC decision + Bicep, compute + integration decision trees, Entra identity, networking & connectivity, observability & FinOps, deployment & CI/CD, dated 2026 capability map) | `plugins/azure-cloud/knowledge/` |
| Templates | 6 (landing-zone plan, IaC deployment spec, architecture spec, Entra identity design, cost & observability review, CI/CD runbook) | `plugins/azure-cloud/templates/` |
| Hooks | 1 advisory anti-pattern hook (hardcoded secret, public exposure, broad RBAC, TLS/HTTPS-off, hardcoded GUID, Terraform local backend); `AZURE_STRICT=1` to block | `plugins/azure-cloud/hooks/` |

Domain-specific team constitution: [`plugins/azure-cloud/CLAUDE.md`](plugins/azure-cloud/CLAUDE.md). Covers the **Azure infrastructure & platform layer** under the Microsoft stack (landing zones / CAF, Bicep/Terraform/AVM/Deployment-Stacks, Entra identity, networking, compute selection, integration, observability + FinOps + governance). Ships **no** security-reviewer/architect clone — escalates to `ravenclaude-core`. Seams reciprocally with `power-platform` (Logic Apps vs Power Automate), `claude-app-engineering` (Azure host), `microsoft-fabric` (raw Azure data services), and `web-design` (Static Web Apps). No bundled MCP — documents the `az` CLI / Bicep / Terraform prerequisite. Built from a researched, expert-reviewed plan ([`docs/azure-cloud-plugin-analysis.md`](docs/azure-cloud-plugin-analysis.md)).

### `finance`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 7 (`fpa-analyst`, `financial-modeler`, `controller`, `treasury-analyst`, `valuation-analyst`, `audit-prep-specialist`, `board-pack-composer`) | `plugins/finance/agents/` |
| Skills | 9 | `plugins/finance/skills/` |
| Hooks | 1 advisory anti-pattern hook | `plugins/finance/hooks/` |
| Templates | board pack, variance memo, model spec, treasury & FP&A artifacts | `plugins/finance/templates/` |

Domain-specific team constitution: [`plugins/finance/CLAUDE.md`](plugins/finance/CLAUDE.md). Covers corporate finance & FP&A (planning, modeling, controllership, treasury, valuation, audit prep, board reporting).

### `regulatory-compliance`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 6 (`aml-kyc-analyst`, `regulatory-reporting-analyst`, `risk-and-controls-specialist`, `policy-and-procedure-writer`, `examination-prep-specialist`, `bermuda-insurance-specialist`) | `plugins/regulatory-compliance/agents/` |
| Skills | 9 | `plugins/regulatory-compliance/skills/` |
| Hooks | 1 defensive PII-scrub hook | `plugins/regulatory-compliance/hooks/` |
| Templates | policy, SAR/regulatory-report, risk-and-controls matrix, examination-prep artifacts | `plugins/regulatory-compliance/templates/` |

Domain-specific team constitution: [`plugins/regulatory-compliance/CLAUDE.md`](plugins/regulatory-compliance/CLAUDE.md). Covers financial-regulatory work (AML/KYC, regulatory reporting, risk & controls, policy authoring, exam prep, Bermuda insurance).

### `web-design`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 7 (`web-architect`, `ux-designer`, `visual-designer`, `frontend-implementer`, `content-strategist`, `accessibility-auditor`, `performance-engineer`) | `plugins/web-design/agents/` |
| Skills | 10 (incl. `fluent-react-implementation`, `design-tokens-scaffolding`, `design-system-audit`, `seo-technical-audit`, `core-web-vitals-tuning`, `conversion-design`) | `plugins/web-design/skills/` |
| Knowledge bank | 7 citation-grounded, retrieval-dated docs (modern web stacks, modern CSS, web-platform capabilities, AEO, design systems & component architecture, Fluent + React for web) | `plugins/web-design/knowledge/` |
| Hooks | 1 advisory web anti-pattern hook | `plugins/web-design/hooks/` |

Domain-specific team constitution: [`plugins/web-design/CLAUDE.md`](plugins/web-design/CLAUDE.md). Covers web architecture, UX, visual design, frontend implementation, content/SEO/AEO, accessibility (WCAG 2.2 AA/AAA), and performance (Core Web Vitals), with a deepening Fluent UI + React track.

### `edtech-partner-success`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 6 (`partner-success-manager`, `success-playbook-designer`, `learning-analytics-analyst`, `qbr-composer`, `partner-profile-curator`, `ferpa-comms-translator`) | `plugins/edtech-partner-success/agents/` |
| Skills | 12 | `plugins/edtech-partner-success/skills/` |
| Knowledge bank | 16 docs (K-12 PSM operating cadences, impact measurement, renewal motions) | `plugins/edtech-partner-success/knowledge/` |
| Hooks | 1 advisory anti-pattern hook | `plugins/edtech-partner-success/hooks/` |

Domain-specific team constitution: [`plugins/edtech-partner-success/CLAUDE.md`](plugins/edtech-partner-success/CLAUDE.md). Covers K-12 EdTech partner success (implementation, adoption, impact measurement, renewals, training, support).

### `data-platform`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 4 (`etl-pipeline-engineer`, `connector-developer`, `database-setup-guide`, `dashboard-builder`) | `plugins/data-platform/agents/` |
| Skills | 11 | `plugins/data-platform/skills/` |
| Knowledge bank | 13 docs (dbt patterns, warehouse selection, ingestion, semantic modeling, the non-Microsoft/SMB lane) | `plugins/data-platform/knowledge/` |
| Hooks | 1 advisory anti-pattern hook | `plugins/data-platform/hooks/` |

Domain-specific team constitution: [`plugins/data-platform/CLAUDE.md`](plugins/data-platform/CLAUDE.md). Covers the non-Microsoft / SMB analytics-engineering lane; seams reciprocally with `microsoft-fabric` (enterprise-Microsoft) and `power-platform/power-bi-engineer`.

### `applied-statistics`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 1 (`applied-statistician`) | `plugins/applied-statistics/agents/` |
| Skills | 5 (experiment design, regression, causal inference, time series, statistical review) | `plugins/applied-statistics/skills/` |
| Knowledge bank | 5 citation-grounded, retrieval-dated docs | `plugins/applied-statistics/knowledge/` |
| Hooks | 1 advisory anti-pattern hook | `plugins/applied-statistics/hooks/` |

Domain-specific team constitution: [`plugins/applied-statistics/CLAUDE.md`](plugins/applied-statistics/CLAUDE.md). Covers rigorous statistical analysis (experiment design, regression, causal inference, time series) with a statistical-review gate.

---

## Contributing back from a consumer project (no repo access needed)

You don't need write access to this marketplace to propose a lesson back. If you're working in any consumer project that has `ravenclaude-core` installed and Claude discovers a pattern, fix, or rule worth keeping, use the **contribution-staging loop**:

1. In your consumer session, ask Claude to use the **`contribute-finding`** skill on the finding. It formats a canonical `RAVENCLAUDE-STAGING-SUBMISSION` block (lesson or best-practice shape).
2. Send the block to Matt (Slack, email, paste in a shared doc).
3. On the marketplace side, Matt drops the block into `docs/staging/incoming/` and runs **`/review-staged-contributions`** — security sweep + topic-expert routing, then keep / update / deny.

Full flow: [`docs/staging/README.md`](docs/staging/README.md). This is the design-intent contribution path for collaborators who don't (or shouldn't) need direct push access.

---

## How agents actually get invoked

A common point of confusion: **these plugin agents do not appear as `subagent_type` options on the `Agent` tool**. Claude Code's built-in agent list (general-purpose, Explore, Plan, etc.) is separate from plugin-supplied agents, and a fresh `Agent` call with `subagent_type: "code-reviewer"` will fail with an InputValidationError.

Plugin agents fire through the **Team Lead orchestration pattern**:

1. The top-level Claude session acts as **Team Lead** — it reads `plugins/ravenclaude-core/CLAUDE.md`, sees the team roster, and decides which specialist(s) the user's request needs.
2. To dispatch one or more specialists, the Team Lead invokes the [`spawn-team`](plugins/ravenclaude-core/skills/spawn-team/SKILL.md) skill — that's the playbook for picking the right specialist, briefing it like a new colleague, and integrating the structured handoff payload that comes back.
3. The specialist runs, returns a Markdown report ending in a `---RESULT_START--- … ---RESULT_END---` JSON block, and the Team Lead re-routes from there.
4. **Sub-agents never spawn other sub-agents.** They return a slice; the Team Lead re-dispatches. This keeps the dependency graph a flat tree.

If you want to talk to a specific agent directly (e.g. "have the architect look at this"), say so in plain English to the Team Lead and it will use `spawn-team` to dispatch the architect. Don't try to address the agent by name through the `Agent` tool's `subagent_type` parameter — that's reserved for the built-in agents.

For the dispatch playbook itself, see [`plugins/ravenclaude-core/skills/spawn-team/SKILL.md`](plugins/ravenclaude-core/skills/spawn-team/SKILL.md).

---

## Browsing the marketplace at a glance

[`repo-guide.html`](repo-guide.html) at the repo root is an interactive single-page guide to every plugin, agent, skill, hook, rule, and template that ships from this marketplace. Open it in any browser (no server required) for a tabbed, searchable view of the current state — or click **[▶ View rendered on GitHub Pages](https://mcorbett51090.github.io/RavenClaude/repo-guide.html)** to render it inline from `main` without cloning. The page is regenerated from the manifests on every release via `python3 scripts/generate-repo-guide.py`; CI's `Verify repo-guide.html is fresh` step fails if it drifts.

---

## Working on the marketplace itself

If you're **developing** RavenClaude (adding plugins, updating agents), see [`CLAUDE.md`](CLAUDE.md) at this repo's root — it's the meta-repo dev guide.

Repo layout:

```
RavenClaude/
├── .claude-plugin/marketplace.json    ← marketplace catalog
├── plugins/
│   ├── ravenclaude-core/              ← the domain-neutral plugin
│   └── power-platform/                ← Microsoft Power Platform specialists
├── .claude/                           ← settings for working ON the marketplace
├── docs/                              ← meta-repo docs
├── checklists/                        ← release / new-plugin / incident checklists
└── CLAUDE.md                          ← meta-repo dev guide
```

The container at `.devcontainer/` auto-installs the Claude Code CLI on rebuild, so a fresh Codespace is ready to work on plugins without setup.

---

## Roadmap

**Shipped since the original roadmap:** `finance`, `regulatory-compliance`, `web-design`, `edtech-partner-success`, `data-platform`, `applied-statistics`, `microsoft-fabric` (the enterprise-Microsoft data-platform lane — OneLake / Lakehouse / Warehouse / Data Factory / Real-Time Intelligence / Direct Lake / capacity FinOps, from [`docs/microsoft-fabric-plugin-analysis.md`](docs/microsoft-fabric-plugin-analysis.md)), `claude-app-engineering` (building on the Claude API + Agent SDK + MCP, from [`docs/claude-app-engineering-plugin-analysis.md`](docs/claude-app-engineering-plugin-analysis.md)), and `azure-cloud` (Azure infrastructure & platform, from [`docs/azure-cloud-plugin-analysis.md`](docs/azure-cloud-plugin-analysis.md)).

Still planned:

- **`salesforce`** — Salesforce metadata, Apex, Flow specialists (deferred — see [`docs/plugin-roadmap-analysis.md`](docs/plugin-roadmap-analysis.md) for why it ranks below the Microsoft-stack work).

Each builds on top of `ravenclaude-core` (which provides the neutral team) and adds domain-specific agents that the consumer can choose to install or skip. `power-platform` is the reference implementation of this pattern.

---

## License

MIT — see [`LICENSE`](LICENSE) for the full text. Bundled third-party content carries its own attribution; see [`plugins/power-platform/NOTICE.md`](plugins/power-platform/NOTICE.md) for the Daniel Kerridge skills import and the pbix-mcp server attribution.

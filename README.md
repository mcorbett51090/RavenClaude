# 🐦‍⬛ RavenClaude

**A private Claude Code plugin marketplace** — bundled team rules, specialist agents, dispatch playbooks, and templates that travel with you across projects.

> 🎛 **[▶ Open the RavenClaude dashboard](https://mcorbett51090.github.io/RavenClaude/plugins/ravenclaude-core/dashboard.html)** — point-and-click editor for your `.ravenclaude/comfort-posture.yaml`: set per-tool file, network, shell, and package autonomy across five levels (deny → always-ask → mostly-ask → mostly-allow → autopilot) without editing YAML by hand.

> 📖 **[▶ View `repo-guide.html` rendered in your browser](https://mcorbett51090.github.io/RavenClaude/repo-guide.html)** — a self-contained single-page guide to every plugin, agent, skill, hook, rule, and template, with a searchable cross-plugin index. Regenerated from the manifests on every release.
>
> _(Or [view the raw HTML source](repo-guide.html), or download and open locally — no server, no build step.)_

Today this marketplace ships **five plugins**:

- **[`ravenclaude-core`](plugins/ravenclaude-core/)** — domain-neutral Team Lead + 14 specialists (architect, coders, reviewers, designer, documentarian, deep-researcher, project-manager, partner-success-manager, prompt-engineer, data-engineer, etc.), plus dispatch playbooks (with a Cross-plugin dispatch section), gates, 5 hooks, templates, and the **cross-project contribution-staging loop**.
- **[`power-platform`](plugins/power-platform/)** — 11 Microsoft Power Platform specialists (Power Fx, flows, Power BI, Dataverse, model-driven, PCF, Copilot Studio, Power Pages, admin, ALM, tester), 13 skills, an advisory house-opinions hook covering 8 checks, and the bundled `pbix-mcp` MCP server.
- **[`finance`](plugins/finance/)** — 7 corporate-finance & FP&A specialists (FP&A analyst, financial modeler, controller, treasury, valuation, audit-prep, board-pack composer), 4 skills, 8 templates, advisory anti-pattern hook.
- **[`regulatory-compliance`](plugins/regulatory-compliance/)** — 6 financial-regulatory specialists (AML/KYC, regulatory reporting, risk-and-controls, policy & procedure writer, examination prep, Bermuda-insurance), 4 skills, 8 templates, defensive PII-scrub hook.
- **[`web-design`](plugins/web-design/)** — 7 web specialists (web architect, UX, visual, frontend implementer, content strategist, accessibility auditor, performance engineer) with WCAG 2.2 AA/AAA, Core Web Vitals, and SEO discipline. 4 skills, 8 templates, advisory web anti-pattern hook.

EdTech and Salesforce plugins remain on the roadmap.

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
| Skills | 10 (dispatch via `spawn-team`, `new-worktree` / `cleanup-worktrees`, `create-pr`, `run-full-test-suite`, `draft-agent-brief`, `structured-output`, plus `contribute-finding` / `review-staged-contributions` for the cross-domain staging loop; the `researcher/` meta-skill sits alongside as a folder) | `plugins/ravenclaude-core/skills/` |
| Hooks | 5 (format-on-write, guard-destructive, remind-tests, enforce-layout, guard-recursive-spawn) | `plugins/ravenclaude-core/hooks/` |
| Rules | 4 (coding-standards, security, git-workflow, agent-collaboration) | `plugins/ravenclaude-core/rules/` |
| Templates | 21 (memos, runbooks, design specs, RAID logs, partner-success artifacts) | `plugins/ravenclaude-core/templates/` |

The team rules ship inside the plugin as [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md). Copy or adapt that into your consumer project's root `CLAUDE.md` and fill in your project's stack-specific gates (formatter, linter, type-checker, test runner).

For a full list of agents and when to spawn each, see the team-roster table in [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md) §5.

### `power-platform`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 11 (`power-fx-engineer`, `flow-engineer`, `power-bi-engineer`, `dataverse-architect`, `model-driven-engineer`, `solution-alm-engineer`, `power-platform-admin`, `pcf-developer`, `copilot-studio-engineer`, `power-pages-engineer`, `power-platform-tester`) | `plugins/power-platform/agents/` |
| Skills | 13 (9 imported MIT from Daniel Kerridge + 4 in-house: `grounding-protocol`, `maintainability-review`, `power-automate`, `power-bi`) | `plugins/power-platform/skills/` |
| Hooks | 1 advisory house-opinions hook covering 8 mechanically-detectable §3/§4 checks (GUIDs, default prefix, hard-coded URLs, binary .pbix, missing flow Try/Catch, premium-connector licensing note, Power Fx var/col prefix, plaintext secret in env-var default) | `plugins/power-platform/hooks/` |
| Bundled MCP | `powerbi-editor` (community `pbix-mcp`, MIT) — requires `pip install pbix-mcp` | declared in `plugins/power-platform/.claude-plugin/plugin.json` |

Domain-specific team constitution: [`plugins/power-platform/CLAUDE.md`](plugins/power-platform/CLAUDE.md). Inherits the neutral team from `ravenclaude-core` and extends with PP-specific routing, house opinions, and anti-patterns. See attribution in [`plugins/power-platform/NOTICE.md`](plugins/power-platform/NOTICE.md).

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
2. To dispatch one or more specialists, the Team Lead invokes the [`spawn-team`](plugins/ravenclaude-core/skills/spawn-team.md) skill — that's the playbook for picking the right specialist, briefing it like a new colleague, and integrating the structured handoff payload that comes back.
3. The specialist runs, returns a Markdown report ending in a `---RESULT_START--- … ---RESULT_END---` JSON block, and the Team Lead re-routes from there.
4. **Sub-agents never spawn other sub-agents.** They return a slice; the Team Lead re-dispatches. This keeps the dependency graph a flat tree.

If you want to talk to a specific agent directly (e.g. "have the architect look at this"), say so in plain English to the Team Lead and it will use `spawn-team` to dispatch the architect. Don't try to address the agent by name through the `Agent` tool's `subagent_type` parameter — that's reserved for the built-in agents.

For the dispatch playbook itself, see [`plugins/ravenclaude-core/skills/spawn-team.md`](plugins/ravenclaude-core/skills/spawn-team.md).

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

Planned future plugins (each in its own subfolder under `plugins/`, all in this same repo):

- **`finance`** — FP&A, variance analysis, financial-modeling specialists.
- **`edtech`** — partner-success, rostering, FERPA-aware translation specialists.
- **`salesforce`** — Salesforce metadata, Apex, Flow specialists.

Each builds on top of `ravenclaude-core` (which provides the neutral team) and adds domain-specific agents that the consumer can choose to install or skip. `power-platform` is the reference implementation of this pattern.

---

## License

MIT — see [`LICENSE`](LICENSE) for the full text. Bundled third-party content carries its own attribution; see [`plugins/power-platform/NOTICE.md`](plugins/power-platform/NOTICE.md) for the Daniel Kerridge skills import and the pbix-mcp server attribution.

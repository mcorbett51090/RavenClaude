# 🐦‍⬛ RavenClaude

**A private Claude Code plugin marketplace** — governed multi-agent teams, specialist plugins, and a comfort-posture dashboard that travel with you across projects.

> 🚀 **[▶ See what RavenClaude is (`pitch.html`)](https://mcorbett51090.github.io/RavenClaude/pitch.html)** — value prop, proof, and catalog at a glance. **Start here.**
>
> 📖 **[▶ Open the RavenClaude portal](https://mcorbett51090.github.io/RavenClaude/)** — browse every plugin, agent, skill, hook, rule, and template (with an “I want to…” lookup). Regenerated from the manifests on every release.
>
> 🎛 **[▶ Open the RavenClaude dashboard](https://mcorbett51090.github.io/RavenClaude/plugins/ravenclaude-core/dashboard.html)** — comfort-posture editor (preview). For a live **Save & apply** against your repo, run **`rc dashboard`** (or `bash scripts/open-dashboard.sh` in this checkout).
>
> 📖 **[▶ First Workflow in 10 Minutes](GETTING_STARTED.md)** — install → dashboard → one governed multi-agent dispatch → `/wrap`.
>
> 🌐 **[▶ Raven Power ↗](https://ravenpower.net)** — the consulting front door behind RavenClaude.

Today this marketplace ships **184 plugins** (live inventory: **[portal Marketplace](https://mcorbett51090.github.io/RavenClaude/)** — prefer that over any hand-maintained essay list below).

**[`ravenclaude-core`](plugins/ravenclaude-core/)** is the foundation: Team Lead + specialist agents, dispatch playbooks, gates, hooks, templates, comfort-posture, and the Learn / teaching surfaces on the dashboard. Domain plugins (Power Platform, cloud, finance, security, and many more) install beside it.

### What's new in core (through **0.323.7**)

- **Thing tribunal** — opt-in command-review for risky tools; **hardening EDIT** behind `command_review.hardening_edit` (**default ON**; set false to opt out).
- **Runes ready-queue** — Oath-hook + `rc runes`; dashboard **Runes at session start** opt-in (`runes:` absent ⇒ off); may auto-claim ungated ready work when On; never auto Longship merge.
- **Prompt Builder** — `#/prompt-builder` with Gate 144 / Host Context floors; catalog model SSOT; blank modes + canned Task/Few-shot.
- **Plugin lifecycle** — per-project last-used ledger; opt-in deprecate/uninstall sweep (**auto_uninstall default OFF**; uninstall plan-only until a reviewed API); ask-first install from the **ravenclaude** marketplace only.
- **Comfort-posture + dashboard** — deny/ask/allow autonomy; Settings + Pipeline; host-scope badges; Learn tab for teaching the system.

> **Count-drift note:** specialist/skill/hook tallies change every release. Treat the portal and `claude plugin details ravenclaude-core` as SSOT — do not trust stale “15 specialists / 58 skills” prose if it reappears elsewhere.

---

## Install

There are **two install paths**, depending on which agent host you use. Pick one and follow that column — the surfaces don't overlap (the `/plugin` slash commands exist only in Claude Code; the `ravenclaude` script exists only on the Copilot side).

|  | **Path A — Claude Code** (recommended if you have it) | **Path B — GitHub Copilot CLI / Codespace** |
|---|---|---|
| **Audience** | You run `claude` and want the marketplace's agents/skills/hooks inside it. | You run `copilot` (or want the dashboard + governance in a Codespace without Claude Code). |
| **Install** | `/plugin marketplace add mcorbett51090/RavenClaude` <br> `/plugin install ravenclaude-core@ravenclaude` <br> `/reload-plugins` | `git clone https://github.com/mcorbett51090/RavenClaude.git ~/RavenClaude` <br> `bash ~/RavenClaude/scripts/ravenclaude setup --project .` <br> `source ~/.bashrc` |
| **Add a plugin** | `/plugin install power-platform@ravenclaude` <br> `/reload-plugins` | `bash ~/RavenClaude/scripts/ravenclaude setup --project . --with-plugin power-platform` |
| **Update later** | `/plugin marketplace update ravenclaude` <br> `/reload-plugins` | `rc` (the alias = `ravenclaude update && copilot --plugin-dir …`) |
| **Pin a SHA** | `/plugin marketplace add mcorbett51090/RavenClaude#<sha>` | `git -C ~/RavenClaude checkout <sha>` |
| **Launch** | (nothing — Claude Code loads the plugin automatically) | `rc` in a NEW terminal (or `bash -i -c rc` from a non-interactive shell) |

That's it. The `ravenclaude-core` specialist agents become available to the Team Lead via the `spawn-team` skill, the dispatch skills are loaded, and the format/lint/test hooks fire automatically. Installing a domain plugin (e.g. `power-platform`) adds its specialists alongside.

### Path B — zero-touch Codespace auto-setup

For a **brand-new repo** you can skip even those commands. Stamp the Codespace template into the repo once:

```shell
bash ~/RavenClaude/scripts/ravenclaude init-codespace --project /path/to/repo
```

It drops `.devcontainer/devcontainer.json` + `.devcontainer/ravenclaude-post-create.sh` into the repo (or, if a `devcontainer.json` already exists, names the keys to merge — `postCreateCommand`, `postStartCommand`, `forwardPorts`, `portsAttributes`). Commit those, rebuild the Codespace, and on every start the post-create script installs prerequisites (Node 22+, git-lfs, Copilot CLI), wires the repo, applies the balanced posture, and adds the `rc` alias. The dashboard auto-launches on the forwarded port — no command to remember.

### Path B prerequisites (most images already have them)

The post-create script auto-installs these on Debian-family images, but if you're on an image without `apt-get` you need them present yourself:

- **Node 22+** (Copilot CLI requires it). The template image `mcr.microsoft.com/devcontainers/universal:2-linux` already has Node; the `python:3.12` family does not.
- **git-lfs** (for any repo with LFS-tracked assets).
- **GitHub CLI** (`gh`) — used to clone a private marketplace fork via your Codespace's auth.

---

## The three dashboards (don't confuse them)

RavenClaude ships three dashboard surfaces with similar URLs but different scopes. Most install confusion comes from clicking the wrong one.

| Surface | URL / launch | What it edits | When to use |
|---|---|---|---|
| **Published preview** (read-only) | <https://mcorbett51090.github.io/RavenClaude/plugins/ravenclaude-core/dashboard.html> | Nothing — Save & apply is a no-op (no server) | Browse the UI before installing. **Do not** try to set a real posture here. |
| **Marketplace local dashboard** | `bash scripts/open-dashboard.sh` (from a marketplace clone) | This marketplace repo's own `.ravenclaude/comfort-posture.yaml` | Only when **developing the marketplace itself** (you're inside `RavenClaude/`). |
| **Per-repo consumer dashboard** | `bash .ravenclaude/dashboard.sh` or `ravenclaude dashboard` (auto-launches on Codespace start if `init-codespace` ran) | **Your repo's** `.ravenclaude/comfort-posture.yaml` + `.claude/settings.json` | Every other case. This is the one consumers should use. |

If Save & apply seems to do nothing, you're almost certainly on the first row. Switch to the second or third.

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

## Updating and version pinning

The marketplace ships **semver-versioned** plugins (`plugin.json` `version` + matching `marketplace.json` entry, CI-gated for drift). 183 of the 184 plugins declare `requires.ravenclaude-core` — a minimum `ravenclaude-core` version they expect, surfaced in the per-plugin card of the portal’s **Marketplace** section ([`index.html`](index.html)).

**To update everything to the marketplace's latest:**

```shell
/plugin marketplace update ravenclaude
/reload-plugins
```

That pulls the catalog head + reloads every installed plugin. Safe for day-to-day use; CI's version-drift gate catches manifest mismatches before they ship.

**To pin to a specific commit SHA** (recommended for client engagements where surprise updates are unwelcome):

```shell
/plugin marketplace add mcorbett51090/RavenClaude#<git-sha>
/plugin install ravenclaude-core@ravenclaude
/reload-plugins
```

The pin survives `/plugin marketplace update` — the pinned SHA is the catalog's source of truth for that engagement until you re-add at a newer SHA.

**To check compatibility** between a domain plugin and your installed `ravenclaude-core`: open the portal ([`index.html`](index.html)) → **Marketplace**, find the plugin, read the **Requires** row. If your installed core version is older, update core first (`/plugin install ravenclaude-core@ravenclaude` to latest, or pin to a SHA ≥ the requirement).

**When an upgrade prompts an `ask`** in the comfort-posture dashboard: that's expected — `shell_package_install` defaults to `ask` in the balanced seed (added v0.101.0). Click **Allow once** the first time; flip the category to `allow` from the dashboard's Set up tab if you'd rather not see the prompt.

**The non-removable security floor** (force-push, `rm -rf`, `curl | sh`, host credential reads — `~/.ssh`, `~/.aws`, etc.) cannot be wiped by editing `comfort-posture.yaml` — `apply-comfort-posture.py` always unions the baseline with whatever the user supplies. Verified by `tests/fixtures/test_security_deny_floor.py`. See [`SECURITY.md`](SECURITY.md) §"Defaults and floors" for the full list.

---

## What's in the marketplace

**184 plugins** (verified). Full inventory with agents, skills, hooks, and “I want to…” lookup: **[portal Marketplace](https://mcorbett51090.github.io/RavenClaude/)**. Per-plugin detail lives in each [`plugins/<name>/README.md`](plugins/).

### Featured (starter set)

| Plugin | Focus |
|--------|-------|
| [`ravenclaude-core`](plugins/ravenclaude-core/) | Domain-neutral Claude Code foundation: specialist agents, skills, gates, hooks, rules,… |
| [`power-platform`](plugins/power-platform/) | Power Platform specialist team — agents (incl. power-platform-tester, power-bi-engineer) and… |
| [`claude-app-engineering`](plugins/claude-app-engineering/) | Claude app-engineering specialist team — agents (claude-solution-architect,… |
| [`security-engineering`](plugins/security-engineering/) | Security-engineering (AppSec) team — agents (appsec-engineer, threat-modeler,… |
| [`incident-response-dfir`](plugins/incident-response-dfir/) | Blue-team DFIR / SOC team — agents (dfir-response-lead, detection-and-forensics-engineer) for… |
| [`aws-cloud`](plugins/aws-cloud/) | AWS cloud infrastructure & platform team — agents (aws-architect, aws-iam-identity-engineer,… |
| [`azure-cloud`](plugins/azure-cloud/) | Azure cloud infrastructure & platform specialist team — agents (azure-architect,… |
| [`finance`](plugins/finance/) | Corporate finance & FP&A specialist team — FP&A analyst (budgets, forecasts, variance… |
| [`web-design`](plugins/web-design/) | Web design & build specialist team — web architect (IA, stack, hosting), UX designer… |
| [`data-platform`](plugins/data-platform/) | Data-platform team — agents (database-setup-guide, etl-pipeline-engineer, dashboard-builder,… |
| [`project-management`](plugins/project-management/) | Project & delivery management team — four specialists across the predictive (PMBOK/PMP) and… |
| [`ai-coding-model-guidance`](plugins/ai-coding-model-guidance/) | Cross-tool AI-coding model guidance — three strategist agents that help you reason about model… |

Install any plugin with `/plugin install <name>@ravenclaude` then `/reload-plugins` (Path A), or `ravenclaude setup --project . --with-plugin <name>` (Path B).

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

[`index.html`](index.html) at the repo root is the **portal** — an interactive single page covering every plugin, agent, skill, hook, rule, and template that ships from this marketplace (in the **Marketplace** section), plus the comfort-posture **Dashboard**. Open it in any browser (no server required) for a searchable view of the current state — or click **[▶ Open on GitHub Pages](https://mcorbett51090.github.io/RavenClaude/)** to render it from `main` without cloning. It is regenerated from the manifests on every release via `python3 scripts/generate-index-dashboard.py`; CI's freshness gate (Gate 97) fails if it drifts.

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

`salesforce` (Apex, Flow, Agentforce, platform-architecture specialists) has since **shipped** as well — it is now one of the 184 plugins above, no longer planned-only.

Each builds on top of `ravenclaude-core` (which provides the neutral team) and adds domain-specific agents that the consumer can choose to install or skip. `power-platform` is the reference implementation of this pattern.

---

## License

MIT — see [`LICENSE`](LICENSE) for the full text. Bundled third-party content carries its own attribution; see [`plugins/power-platform/NOTICE.md`](plugins/power-platform/NOTICE.md) for the Daniel Kerridge skills import and the pbix-mcp server attribution.

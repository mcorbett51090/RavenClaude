# ravenclaude-core — Claude Code plugin

> The domain-neutral Team Lead + specialist-agent foundation for the RavenClaude marketplace.

> 🎛 **Comfort-posture dashboard** — a point-and-click editor for your permission rules (deny → ask → allow, per layer + per permission) and command-review toggles, no YAML by hand. After install, run **`/dashboard`** for the fully-functioning version (one-click **Save & apply**), or take a **[quick look on the hosted copy](https://mcorbett51090.github.io/RavenClaude/plugins/ravenclaude-core/dashboard.html)** (Copy/Download only). Details in [Comfort-posture dashboard](#the-protocols-it-provides-to-the-whole-marketplace) below.

> 📚 **New here?** The dashboard's **Learn** tab explains the moving parts — permission layers, the command-review tribunal, hooks — with diagrams and interactive widgets. The same reference, readable on GitHub, is generated at **[docs/concepts.md](../../docs/concepts.md)**.

Ships the orchestrator-worker dispatch model, 15 generalist specialist agents (architect, backend/frontend/fullstack coders, code-reviewer, security-reviewer, tester-qa, data-engineer, deep-researcher, designer, documentarian, project-manager, partner-success-manager, prompt-engineer, viz-spec-reviewer), 44 skills, 19 hooks, 5 rule-sets, working templates, slash commands (`/init-agent-ready`, `/wrap`, `/set-posture`, `/dashboard`, `/forge`, `/reset-plugin-cache` (alias `/ragnarok`)), and a knowledge bank the Researcher cross-checks. Every other plugin in the marketplace extends this one.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude
/reload-plugins
```

This is the prerequisite plugin — domain plugins (`power-platform`, `finance`, …) require it for the shared protocols below.

## What's inside

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 15 | [`agents/`](agents/) |
| Skills | 44 | [`skills/`](skills/) |
| Hooks | 19 | [`hooks/`](hooks/) |
| Rule-sets | 5 | [`rules/`](rules/) |
| Slash commands | 7 (`/init-agent-ready`, `/wrap`, `/set-posture`, `/dashboard`, `/forge`, `/reset-plugin-cache` (alias `/ragnarok`)) | [`commands/`](commands/) |
| Knowledge files | see [`knowledge/`](knowledge/) | [`knowledge/`](knowledge/) |

## The protocols it provides to the whole marketplace

- **Orchestrator-worker dispatch** — only the Team Lead spawns specialists; sub-agents hand back, they don't fan out.
- **Capability Grounding Protocol** — pre-action environment + decision-tree checks, alternate-methods enumeration, and honest blocked-phrasing before any "I can't."
- **Structured Output Protocol** — every handoff ends with a `---RESULT_START--- … ---RESULT_END---` JSON block alongside human-readable Markdown.
- **Comfort-posture** — `/set-posture` translates a per-category YAML into `.claude/settings.json` permission rules, with an always-on `security_deny` baseline.
- **Comfort-posture dashboard** — a point-and-click editor for your permission rules + command-review toggles. The `dashboard.html` ships **inside the installed plugin** (at `~/.claude/plugins/cache/ravenclaude/ravenclaude-core/<version>/dashboard.html`). Two ways to use it:
  - **Fully-functioning (recommended) — `/dashboard`.** Launches a small **local** server (bundled in the plugin) and gives you a URL; open it in a real browser tab and the **Save & apply** button writes `.ravenclaude/comfort-posture.yaml` and applies it in one click. Binds `127.0.0.1`, local/single-user, CSRF-guarded; writes via `/__save`/`/__read`/`/__classify`, the only action endpoint is an allow-listed `/__run` (install/update/status — **no arbitrary shell**), and the rest are read-only observability feeds. In a Codespace, keep the forwarded port **Private**.
  - **Quick look (no server).** Open the [hosted dashboard](https://mcorbett51090.github.io/RavenClaude/plugins/ravenclaude-core/dashboard.html) or the cached file directly, pick rules, **Copy/Download** the YAML into `.ravenclaude/comfort-posture.yaml`, then run `/set-posture`. (The hosted copy reflects the marketplace's latest and can differ from your installed version; the cached file is version-matched.)

  Claude-Code-specific — other tools (Copilot/Cursor/Codex) don't execute it.

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution (dispatch rules, agent-routing decision tree, knowledge-freshness discipline, run-artifacts standard).

## When to dispatch

```text
"Design the approach before we build X"        → architect
"Implement this API handler / this UI"          → backend-coder / frontend-coder
"Review this diff before I merge"               → code-reviewer (+ security-reviewer if auth/crypto)
"Is this library claim actually true?"          → deep-researcher
"Set up this repo so agents behave"             → /init-agent-ready
"Capture what we just learned"                  → /wrap
"Tune how autonomous Claude is here"            → /set-posture
"Open the dashboard (Save & apply works)"       → /dashboard
```

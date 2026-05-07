# 🐦‍⬛ RavenClaude

**The central Claude knowledge hub** for cross-domain consulting work. Lessons, agent roles, and reusable assets that apply to *any* Claude work accumulate here. Domain-specific knowledge — Power Platform, Salesforce, websites, Apple apps, etc. — lives in separate **Expert repos** that this hub references when needed.

## The model in one picture

```
RavenClaude (this repo, central, domain-neutral)
   + PowerPlatformExpert  (separate repo, when doing Power Platform work)
   + SalesforceExpert     (separate repo, when doing Salesforce work)
   + WebsiteExpert        (etc.)
   ──────────────────────────────────────────────
   = the full Claude context for a client project
```

The central hub stays clean. Each Expert repo stays focused. Client projects mix and match.

## What's inside

| Path | What lives there |
|------|------------------|
| `docs/memory-bank/lessons-learned.md` | **Read this first.** Running log of cross-domain "we tried X, Y failed because Z, here's what works." Newest at top. |
| `docs/memory-bank/decision-log.md` | Major architectural decisions and the reasoning behind them. |
| `docs/best-practices/` | Cross-domain best-practice guides. |
| `docs/architecture.md` | How the hub works and how Expert repos plug in. |
| `skills/` | Cross-domain skills (one folder per skill). |
| `scripts/` | Cross-domain reusable utility scripts. |
| `templates/` | Cross-domain file/config/prompt templates. |
| `examples/` | Cross-domain sanitized real-world examples. |
| `checklists/` | Cross-domain pre-flight / post-flight checklists. |
| `.claude/` | This repo's own Claude config (agent definitions, hooks, permissions). Governs how Claude operates *inside* this repo. |
| `.devcontainer/` | Codespaces setup. Auto-installs the Claude CLI on every container build. |
| `CLAUDE.md` | Operational constitution — house rules for work inside this repo. |

## Quick start (in this repo)

Open in GitHub Codespaces or any devcontainer-aware IDE. The container builds with:

- **Claude Code CLI** (`claude`) — Anthropic's terminal Claude.
- **GitHub CLI** (`gh`) — preinstalled.
- Standard universal devcontainer image (Node, .NET, Python, etc.).

If the container is already running and you want the tool installed without rebuilding:

```bash
bash .devcontainer/post-create.sh
```

> Domain-specific tools (the Power Platform `pac` CLI, Salesforce's `sfdx`, etc.) are intentionally *not* installed here. Those live in the matching Expert repo's devcontainer.

## How to consume this hub from another project

Add to your consumer project's devcontainer (or setup script):

```bash
# Read-only clone of this central hub
git clone --depth=1 https://github.com/<owner>/RavenClaude.git /workspaces/RavenClaude

# Plus any Expert repos relevant to the work
git clone --depth=1 https://github.com/<owner>/PowerPlatformExpert.git /workspaces/PowerPlatformExpert
```

In the consumer's `CLAUDE.md` or session prompts, reference hub assets by the `@ravenclaude/...` convention — e.g. `@ravenclaude/skills/<skill-name>` resolves to `/workspaces/RavenClaude/skills/<skill-name>`. Expert repos get their own short-name conventions (`@ppe/...`, `@sfe/...`).

See [`docs/architecture.md`](docs/architecture.md) for the full consumption protocol and the knowledge-accumulation flow.

## Contributing knowledge

When something non-obvious surfaces while working in a consumer project:

1. Save it to that project's auto-memory immediately.
2. Decide where it generalizes:
   - Specific to one domain → that Expert repo's `lessons-learned.md`.
   - Cross-domain → [`docs/memory-bank/lessons-learned.md`](docs/memory-bank/lessons-learned.md) here.
3. Cite the propagation in your response so the trail is verifiable.

## License

TBD — pick a license before public use.

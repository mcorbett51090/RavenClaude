# CLAUDE.md — RavenClaude (Claude Code addendum)

@AGENTS.md

This file is Claude Code's entry point. The `@AGENTS.md` import above pulls in the cross-tool conventions (setup, layout, style, testing, PR rules). Anything below is **Claude-Code-specific** and is not meaningful to other agentic tools.

---

## Plan-mode default

For non-trivial changes touching more than two files (or any manifest), enter plan mode first and present a Keep / Update / Deny structure before writing. This matches Matt's documented preference; Cursor/Codex users won't see this guidance and don't need to.

## Memory references

User-scoped memory lives under your Claude Code home (e.g. `~/.claude/projects/<encoded-project-path>/memory/` on Linux/macOS or the equivalent on Windows). `MEMORY.md` is the index inside that directory. Update it when something durable about the user, project, or working style changes.

## Marketplace-dev hooks

Two registration paths are wired in this repo, intentionally:

1. **Plugin canonical** — `plugins/ravenclaude-core/hooks/hooks.json` registers all four hooks with `${CLAUDE_PLUGIN_ROOT}` paths. This is the path consumers get when they `/plugin install ravenclaude-core@ravenclaude`.
2. **Marketplace dev** — `.claude/settings.json` registers the same four hooks with `${CLAUDE_PROJECT_DIR}` paths against the working tree. This is what fires when you're editing the marketplace itself and the dev session may not have the latest plugin version installed.

Both wirings call idempotent scripts, but the two paths *do* fire on the same events when both are active. Long-term the marketplace dev session should rely on the installed plugin only — to migrate, run `/plugin marketplace update ravenclaude` + `/reload-plugins` in your dev session, confirm the installed version is current, then delete the `hooks` block in `.claude/settings.json`. Until then, keeping both is the safer default.

If you need a marketplace-only hook (i.e., one that should NOT ship to consumers), add it to `.claude/settings.json` under `hooks` separately from the dev-mirror block above.

## Layout enforcement (Claude Code path)

The plugin's `hooks/enforce-layout.sh` runs `PreToolUse` on `Write|Edit|MultiEdit`. It reads `.repo-layout.json` at the project root, matches the target path against `allowed_globs`, and denies off-pattern writes with a suggested correct location. The hook silently allows everything if `.repo-layout.json` is absent — so consumers who install the plugin without setting up a layout manifest are not surprised.

The matching CI workflow `.github/workflows/validate-layout.yml` is the cross-tool backstop (catches direct human commits, Cursor/Codex/Aider edits, and any case where the hook didn't fire).

Why both: Claude Code issue [#23478](https://github.com/anthropics/claude-code/issues/23478) confirms that path-scoped rule files (`paths:` frontmatter) load only on Read, not on Write. They cannot prevent off-pattern file *creation*. The hook (in-loop, Claude-only) plus the CI (universal backstop) is the supported enforcement pattern in 2026.

## Slash commands shipped by the plugin

After installing the plugin in any project, consumers get:

- `/init-agent-ready` — guided setup: creates `AGENTS.md`, `CLAUDE.md`, `.repo-layout.json`, and optionally a CI workflow tailored to the consumer's repo type (application / library / monorepo / docs / data / IaC).

The command is defined in `plugins/ravenclaude-core/commands/init-agent-ready.md` and writes from templates in `plugins/ravenclaude-core/templates/agent-ready-repo/`.

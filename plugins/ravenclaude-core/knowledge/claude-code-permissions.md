# Claude Code permissions — the load-bearing model

> **Last reviewed:** 2026-05-22 against the Anthropic Claude Code documentation site at code.claude.com (permissions, permission-modes, settings, tools-reference pages). **Refresh when:** Anthropic ships a new permission mode, adds documented prompt-verbosity controls, or changes the cross-layer merge rule. Companion to [`../skills/permission-hygiene.md`](../skills/permission-hygiene.md).

This document is the long-form "why these patterns" reference behind the [`permission-hygiene`](../skills/permission-hygiene.md) skill. The skill tells you what to do; this file tells you what the model is and where the surprises live.

---

## The schema

Permission rules live under `permissions.allow`, `permissions.ask`, and `permissions.deny` in any of the four settings files. Each rule is a string in one of two shapes:

- `Tool` — the bare tool name (e.g. `Bash`, `WebSearch`)
- `Tool(specifier)` — the tool name plus a tool-specific specifier (e.g. `Bash(git status:*)`, `WebFetch(domain:github.com)`, `Read(/etc/**)`)

A **bare-tool deny** like `deny: ["Bash"]` removes the tool from Claude's context entirely — Claude never sees it. A **scoped deny** like `Bash(rm *)` leaves the tool available and blocks matching calls. This is the most-surprising bit of the model: people add `deny: ["Bash"]` expecting "block destructive shell" and end up with "no shell at all."

## Precedence — the cross-layer merge rule

**Within a single settings file:** rules evaluate in order `deny → ask → allow`. The first matching rule wins. Deny always beats ask, ask always beats allow.

**Across settings files:** permissions **merge** across layers rather than override. A deny in *any* layer blocks the action regardless of allow rules in other layers. The layer precedence top→bottom for non-permission settings:

1. Managed (enterprise) settings
2. Command-line args
3. Project local: `.claude/settings.local.json`
4. Project team-shared: `.claude/settings.json`
5. User: `~/.claude/settings.json`

**Implication for the permission model specifically:** you can't "override down." If `~/.claude/settings.json` denies `Bash(rm *)`, no project-level allow will let `rm` through. This is the safe behavior, but it surprises users who expect later layers to override earlier ones.

## Bash patterns — the documented fragility

The Anthropic permissions doc has an explicit warning section: **Bash argument-constraint patterns are fragile.** The published example: `Bash(curl http://github.com/ *)` is bypassed by all of these:

- Options before URL: `curl -X GET http://github.com/...`
- Protocol swap: `curl https://github.com/...`
- Redirects: `curl http://bit.ly/...` (which redirects to github.com)
- Variable substitution: `URL=http://github.com/...; curl $URL`
- Extra whitespace: `curl  http://github.com/...` (two spaces)

**The doc's own recommendation:** for URL-shape constraints, deny `curl`/`wget` in Bash and use `WebFetch(domain:...)` rules instead. For general "constrain Bash arguments" needs, use a **PreToolUse hook** that inspects the full command and rejects.

## Wildcards — the space matters

- `Bash(ls *)` matches `ls -la`, `ls /tmp`, etc. — but NOT `lsof` (the space enforces a word boundary).
- `Bash(ls*)` matches both `ls -la` AND `lsof`. Almost always too broad.
- `Bash(ls:*)` is shorthand for `Bash(ls *)` — equivalent, just a different style.

The colon-suffix form (`tool:*`) is conventional in Anthropic's own example settings repo and reads cleaner; this marketplace uses it throughout `.claude/settings.json`.

## What's already auto-allowed (no rule needed)

Claude Code ships a built-in `READONLY_COMMANDS` allow-list. Don't add rules for these — they never prompt:

- **Always:** `cal`, `uptime`, `cat`, `head`, `tail`, `wc`, `stat`, `strings`, `hexdump`, `od`, `nl`, `id`, `uname`, `free`, `df`, `du`, `locale`, `groups`, `nproc`, `basename`, `dirname`, `realpath`, `cut`, `paste`, `tr`, `column`, `tac`, `rev`, `fold`, `expand`, `unexpand`, `fmt`, `comm`, `cmp`, `numfmt`, `readlink`, `diff`, `true`, `false`, `sleep`, `which`, `type`, `expr`, `test`, `getconf`, `seq`, `tsort`, `pr`, `echo`, `printf`, `ls`, `cd`, `find`.
- **All git read-only subcommands:** `git status`, `git log`, `git diff`, `git show`, `git blame`, `git branch`, `git tag`, `git remote`, `git ls-files`, `git ls-remote`, `git rev-parse`, `git describe`, `git stash list`, `git reflog`, `git shortlog`, `git cat-file`, `git for-each-ref`, `git worktree list`.
- **All gh read-only subcommands:** `gh pr view/list/diff/checks/status`, `gh issue view/list/status`, `gh run view/list`, `gh workflow list/view`, `gh repo view`, `gh release view/list`, `gh api` (GET only), `gh auth status`.
- **Docker read-only:** `docker ps`, `docker images`, `docker logs`, `docker inspect`.
- **Safe-flag-only:** `xargs`, `file`, `sed` (read-only expressions), `sort`, `man`, `help`, `netstat`, `ps`, `base64`, `grep`, `egrep`, `fgrep`, `sha256sum`, `sha1sum`, `md5sum`, `tree`, `date`, `hostname`, `info`, `lsof`, `pgrep`, `tput`, `ss`, `fd`, `fdfind`, `rg`, `jq`, `uniq`, `history`, `arch`, `ifconfig`, `pyright`.

Source: `src/tools/BashTool/readOnlyValidation.ts` (per the Claude Code core `/fewer-permission-prompts` skill body, which inspects the source list at runtime).

## Permission modes (the six modes)

| Mode                | What it does                                                                                          | Where it's set                          |
| ------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `default`           | Standard prompt-on-uncertain behavior                                                                 | Per-session                             |
| `acceptEdits`       | Auto-approves common filesystem Bash inside cwd (`mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed`)  | Per-session                             |
| `plan`              | Planning mode — read/think only, no writes                                                            | Per-session                             |
| `auto`              | Research-preview; classifier-driven autonomy. **Silently drops broad allow rules** (`Bash(*)` etc.)   | `~/.claude/settings.json` only          |
| `dontAsk`           | Auto-deny everything not explicitly allowed (useful for CI)                                           | Per-session / per-invocation            |
| `bypassPermissions` | Skips most checks. **`rm -rf /` and `rm -rf ~` still prompt** as a circuit breaker                    | Launch flag only                        |

**`auto` mode gotchas:**
- Requires Claude Code v2.1.83+, Sonnet 4.6 / Opus 4.6+, Anthropic API only (not Bedrock/Vertex/Foundry).
- Drops `Bash(*)`, `PowerShell(*)`, wildcarded interpreters like `Bash(python*)`, package-manager run wildcards (`npm run *`), all `Agent` allow rules. They restore when you leave auto mode.
- `defaultMode: "auto"` is **ignored** in project-level settings — must be set in user-level `~/.claude/settings.json`.

## Read/Edit path anchors (gitignore-style)

Rules for `Read(...)` and `Edit(...)` follow gitignore semantics with four anchor types:

| Pattern       | Anchored to        | Example                                |
| ------------- | ------------------ | -------------------------------------- |
| `//abs/path`  | Filesystem root    | `Read(//etc/**)`                       |
| `~/path`      | Home directory     | `Read(~/.ssh/**)`                      |
| `/path`       | **Project root**   | `Read(/secrets/**)` ← NOT filesystem!  |
| `path`, `./path`, `**/.env` | Current working dir / any depth | `Read(.env)` ≡ `Read(**/.env)` |

**`Edit(...)` implicitly grants `Read(...)` on the same path.** Don't write paired rules.

**Critical gap:** `Read`/`Edit` rules **do not protect against subprocess access.** A `Read(**/.env)` deny does not stop a Python script Claude writes (`python -c "open('.env').read()"`) from reading the file. OS-level enforcement requires the Claude Code sandbox feature.

## The "more prompt detail" question

**As of 2026-05-22, no documented Claude Code setting increases prompt verbosity.** The settings doc has no `skipAutoPermissionPrompt`-equivalent, no Bash `description`-renders-in-prompt switch. Confirmed by exhaustive read of the permissions, permission-modes, settings, and tools-reference docs.

The Bash tool accepts a `description` parameter, but the public docs frame it as transcript annotation, not prompt-UI surface. Whether it shows in the permission prompt is **not documented** — don't rely on it without verification.

Practical levers that actually work:

1. **Narrate before the call.** Agents say in one sentence what the command does and why, immediately before invoking the tool. The narration appears above the prompt in the transcript.
2. **PreToolUse hooks that print to stderr.** Hook stderr lands in the transcript near the prompt.
3. **Group rules by section** in `.claude/settings.json` so a reviewer scanning the file can map "what's allowed here" to "what concern this serves."

## settings.local.json bloat — the typical evolution

The bloat pattern, observed in real projects (including this marketplace, pre-2026-05-22 sweep):

1. Claude asks for permission to run a specific command.
2. User clicks "Yes, don't ask again."
3. Claude Code writes the EXACT command (including all literal arguments) to `.claude/settings.local.json`.
4. The user runs a variant the next time; Claude asks again; user clicks "Yes, don't ask again" again; new rule added.
5. After a few weeks, the local file has dozens of nearly-identical rules — most for commands that will never recur verbatim (PR comments with literal text, `chmod +x <exact-script>.sh`, `mkdir -p <exact-path>`).

The skill's periodic-cleanup ritual is the antidote. **Most local rules are noise, not policy.** Abstract the durable ones up to `.claude/settings.json`; delete the rest.

## Hooks beat broad rules

When a rule shape can't reliably express your intent, switch to a PreToolUse hook. Pattern:

```jsonc
// .claude/settings.json
{
  "permissions": {
    "allow": ["Bash"], // broad
    "deny": []
  },
  "hooks": {
    "PreToolUse": [{ "matcher": "Bash", "command": "scripts/guard-destructive.sh" }]
  }
}
```

The hook reads the full command from stdin/env, decides, prints to stderr, and exits 0 (allow) or non-zero (deny with the stderr text shown to the user). This composes — multiple hooks chain. RavenClaude's [`hooks/guard-destructive.sh`](../hooks/guard-destructive.sh) is the in-repo example.

## Citations

- [Configure permissions — code.claude.com/docs/en/permissions](https://code.claude.com/docs/en/permissions) — primary source for rule syntax, precedence, Bash argument-fragility warning, hook integration.
- [Choose a permission mode — code.claude.com/docs/en/permission-modes](https://code.claude.com/docs/en/permission-modes) — primary source for the six modes, auto-mode drop-broad-rules behavior, protected paths.
- [Claude Code settings — code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings) — primary source for settings file layer precedence; confirmed absence of prompt-verbosity controls.
- [Tools reference — code.claude.com/docs/en/tools-reference](https://code.claude.com/docs/en/tools-reference) — primary source for tool list, Edit-implies-Read, Bash tool behavior.
- [GitHub issue #26796 — Bash tool prompts for permission on auto-approved commands](https://github.com/anthropics/claude-code/issues/26796) — confirms a known reliability bug: pre-approved commands sometimes still prompt.
- [Korny's "Better Claude Code permissions"](https://blog.korny.info/2025/10/10/better-claude-code-permissions) — community guidance; argues hooks > broad rules.
- Claude Code core `/fewer-permission-prompts` skill body — primary source for the `READONLY_COMMANDS` auto-allow list shape; references `src/tools/BashTool/readOnlyValidation.ts` and `src/utils/shell/readOnlyCommandValidation.ts`.

# Claude Code permissions — the load-bearing model

> **Last reviewed:** 2026-05-22 against the Anthropic Claude Code documentation site at code.claude.com (permissions, permission-modes, settings, tools-reference pages) AND the canonical GitHub Security Advisories at `github.com/anthropics/claude-code/security/advisories`. **Refresh when:** Anthropic ships a new permission mode, adds documented prompt-verbosity controls, changes the cross-layer merge rule, or publishes a new security advisory affecting the permission model. Companion to [`../skills/permission-hygiene/SKILL.md`](../skills/permission-hygiene/SKILL.md).

This document is the long-form "why these patterns" reference behind the [`permission-hygiene`](../skills/permission-hygiene/SKILL.md) skill. The skill tells you what to do; this file tells you what the model is and where the surprises live.

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

## Past CVEs that shaped the permission model

Settings files (`.claude/settings.json`, `.claude/settings.local.json`, managed-settings) are treated by Claude Code as **security boundaries**. Multiple advisories in the past year have shown how attacker-controlled settings or trust-bypass mechanisms led to arbitrary code execution. Each row below is verified against the canonical [GitHub Security Advisories for `anthropics/claude-code`](https://github.com/anthropics/claude-code/security/advisories); CVE numbers were cross-checked against NIST NVD.

| Date | Title | Severity | Patched in | CVE | GHSA |
|---|---|---|---|---|---|
| Feb 6, 2026 | Sandbox Escape via Persistent Configuration Injection in settings.json | High (7.7) | v2.1.2 | [CVE-2026-25725](https://nvd.nist.gov/vuln/detail/CVE-2026-25725) | [GHSA-ff64-7w26-62rf](https://github.com/anthropics/claude-code/security/advisories/GHSA-ff64-7w26-62rf) |
| Mar 18, 2026 | Workspace Trust Dialog Bypass via Repo-Controlled Settings File | High (7.7) | v2.1.53 | [CVE-2026-33068](https://nvd.nist.gov/vuln/detail/CVE-2026-33068) | [GHSA-mmgp-wc2j-qcv7](https://github.com/anthropics/claude-code/security/advisories/GHSA-mmgp-wc2j-qcv7) |
| Apr 17, 2026 | Insecure System-Wide Configuration Loading Enables Local Privilege Escalation on Windows | Moderate (5.4) | v2.1.75 | [CVE-2026-35603](https://nvd.nist.gov/vuln/detail/CVE-2026-35603) | [GHSA-5cwg-9f6j-9jvx](https://github.com/anthropics/claude-code/security/advisories/GHSA-5cwg-9f6j-9jvx) |
| Apr 20, 2026 | Sandbox Escape via Symlink Following Allows Arbitrary File Write Outside Workspace | High (7.7) | v2.1.64 | [CVE-2026-39861](https://nvd.nist.gov/vuln/detail/CVE-2026-39861) | [GHSA-vp62-r36r-9xqp](https://github.com/anthropics/claude-code/security/advisories/GHSA-vp62-r36r-9xqp) |
| Apr 24, 2026 | Trust Dialog Bypass via Git Worktree Spoofing Allows Arbitrary Code Execution | High (7.7) | v2.1.84 | [CVE-2026-40068](https://nvd.nist.gov/vuln/detail/CVE-2026-40068) | [GHSA-q5hj-mxqh-vv77](https://github.com/anthropics/claude-code/security/advisories/GHSA-q5hj-mxqh-vv77) |

### What the pattern tells you about the permission model

1. **`settings.json` is attacker-relevant.** Three of the five CVEs above hinge on the file: a malicious repo committing a settings file with `defaultMode: bypassPermissions`; an attacker creating a missing `settings.json` from inside a sandbox to inject persistent hooks; an attacker creating `C:\ProgramData\ClaudeCode\managed-settings.json` on a Windows machine where the parent dir is world-writable. Treat any `settings.json` from outside your team — including ones inside a repo you just cloned — as untrusted input.
2. **Trust-dialog bypasses recur.** Two of the five CVEs are workspace-trust bypasses (repo-controlled settings; git-worktree `commondir` spoofing). When you click "trust this workspace," you are extending trust to anything the workspace can later inject — including any hook script its `.claude/settings.json` references. Don't trust workspaces you wouldn't run `git clone && rm -rf /` against blindfolded.
3. **Sandboxed exec + permission-deny don't fully isolate.** The Apr 20 symlink-escape (`CVE-2026-39861`) exploited the seam between two independently-restricted capabilities — a sandboxed command could create a symlink, the unsandboxed parent followed it. The lesson for *your* hooks: any "deny X" rule is only as strong as the absence of an indirection (symlink, junction, wrapper command) that the rule doesn't see.
4. **Keep Claude Code updated.** All five of these were patched. Running `claude --version` and confirming you're on a recent release is the cheapest mitigation available; ignoring updates re-exposes you to fixed flaws.

### Implications for project hooks (the `permission-hygiene` decision tree)

These CVEs reinforce three pieces of the [`permission-hygiene`](../skills/permission-hygiene/SKILL.md) skill's discipline:

- **Don't lower permission mode in a repo-shared `.claude/settings.json`.** A `defaultMode: "auto"` or `defaultMode: "bypassPermissions"` value in the team-shared file is exactly the attack vector `CVE-2026-33068` exploited. Permission-mode escalation belongs in the user-level `~/.claude/settings.json` or per-session flags, not project files.
- **Hooks in `.claude/settings.json` execute with host privileges.** A repo-shared `PreToolUse` hook is a legitimate tool — that's how `enforce-layout.sh` and `guard-destructive.sh` work in this marketplace. But because every CVE in the table above ends in "attacker-controlled hook executes arbitrary code," code-review on every new hook script is mandatory, not optional.
- **Verify alleged vulnerabilities at canonical sources before acting on them.** During the dashboard-UX research run on 2026-05-22, an external blog post (`0day.click`) claimed `CVE-2026-39861` was a deep-link parameter-injection RCE patched in v2.1.118. NVD and the actual GitHub Security Advisory both confirm CVE-2026-39861 is the symlink-traversal sandbox escape in the table above — patched in v2.1.64, not v2.1.118. The blog post additionally contained a prompt-injection payload designed to manipulate AI assistants reading it. When a vendor name + CVE appear in untrusted prose, the Team Lead independently checks NVD + GitHub Security Advisories before letting the claim shape a design decision (see auto-memory `feedback_verify_cve_claims_at_team_lead.md`).

### General URL-handler hygiene (not tied to any specific CVE)

The `claude-cli://` deep-link scheme documented at [code.claude.com/docs/en/deep-links](https://code.claude.com/docs/en/deep-links) lets a web page pre-fill the Claude Code prompt box with a URL like `claude-cli://open?q=...&cwd=...&repo=...`. The prompt is populated but not executed until the user presses Enter. **No known CVE targets this surface as of 2026-05-22**, but standard URL-handler hygiene still applies for any UI that *generates* such links (e.g., the per-plugin dashboard's Commands tab — see proposal 003):

- **Hard-coded `q` values only.** Never feed free-form user input into the `q` parameter. Ship an allow-list of pre-canned templates (`?q=%2Finit-agent-ready`, etc.).
- **`cwd` from the UI's own context, not user input.** Don't let a user paste a path that becomes the working directory.
- **Always show the user what will be pre-filled before launching.** Deep links should never feel like a magic action; they should feel like "click to open Claude Code with this exact prompt staged."

This guidance is general URL-handler defense-in-depth, not mitigation of a specific advisory.

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

The hook reads the full command as JSON on **stdin** (`{tool_name, tool_input:{command}, ...}`), decides, and prints any reason to stderr. **Exit codes are the load-bearing detail and the easy thing to get wrong:**

| Exit code | Effect on a `PreToolUse` hook |
| --- | --- |
| `0` | Allow — the command proceeds (unless the hook emits a `hookSpecificOutput.permissionDecision` JSON saying otherwise). |
| **`2`** | **Block** — the command is refused and the stderr text is fed back to the model. **This is the only blocking exit code.** |
| `1` (or any other non-zero) | **Non-blocking error** — a notice is shown but **the command still runs.** |

The trap: `exit 1` is the conventional Unix failure code, so a policy hook that "fails" with `exit 1` looks like it blocked but doesn't. A hook meant to enforce a policy MUST `exit 2`. (Verified against [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks), 2026-05-25: *"only exit code 2 blocks the action. Claude Code treats exit code 1 as a non-blocking error and proceeds."*) This composes — multiple hooks chain. RavenClaude's [`hooks/guard-destructive.sh`](../hooks/guard-destructive.sh) reads stdin JSON and exits 2 to block; it is the in-repo example.

## Citations

- [Configure permissions — code.claude.com/docs/en/permissions](https://code.claude.com/docs/en/permissions) — primary source for rule syntax, precedence, Bash argument-fragility warning, hook integration.
- [Choose a permission mode — code.claude.com/docs/en/permission-modes](https://code.claude.com/docs/en/permission-modes) — primary source for the six modes, auto-mode drop-broad-rules behavior, protected paths.
- [Claude Code settings — code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings) — primary source for settings file layer precedence; confirmed absence of prompt-verbosity controls.
- [Tools reference — code.claude.com/docs/en/tools-reference](https://code.claude.com/docs/en/tools-reference) — primary source for tool list, Edit-implies-Read, Bash tool behavior.
- [GitHub issue #26796 — Bash tool prompts for permission on auto-approved commands](https://github.com/anthropics/claude-code/issues/26796) — confirms a known reliability bug: pre-approved commands sometimes still prompt.
- [Korny's "Better Claude Code permissions"](https://blog.korny.info/2025/10/10/better-claude-code-permissions) — community guidance; argues hooks > broad rules.
- Claude Code core `/fewer-permission-prompts` skill body — primary source for the `READONLY_COMMANDS` auto-allow list shape; references `src/tools/BashTool/readOnlyValidation.ts` and `src/utils/shell/readOnlyCommandValidation.ts`.

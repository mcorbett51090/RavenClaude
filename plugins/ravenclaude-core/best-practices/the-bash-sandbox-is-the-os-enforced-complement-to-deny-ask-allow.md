# The Bash sandbox is the OS-enforced complement to deny / ask / allow

**Status:** Pattern
**Domain:** Agent design / Security / Permissions

**Applies to:** `ravenclaude-core`

---

## Why this exists

Permission rules (`deny` / `ask` / `allow`) and the Bash **sandbox** answer two
different questions, and a repo that runs unattended needs both. Permission rules
are evaluated **before** a command runs, from the command _string_ (and, in auto
mode, a classifier's read of it). The sandbox is enforced **while** the command
runs, by the operating system, on the process and every child it spawns.

That difference is the whole point. A permission rule reasons about what a command
_says_ it will do; the sandbox constrains what it _can_ do "regardless of what the
model chose to run and even if an allowed command does more than its name
suggests" ([Anthropic — sandboxing](https://code.claude.com/docs/en/sandboxing)).
The two are complementary layers, not alternatives.

**This closes a hole the permissions layer cannot.** This repo's own
[`../knowledge/claude-code-permissions.md`](../knowledge/claude-code-permissions.md)
names it: a `Read(**/.env)` **deny** does not stop a Python subprocess Claude
writes — `python -c "open('.env').read()"` — from reading the file, because
`Read`/`Edit` rules gate Claude's _built-in_ tools, not the subprocesses a `Bash`
command spawns. The knowledge file's stated fix is exactly this rule: "OS-level
enforcement requires the Claude Code sandbox feature." The sandbox's
`credentials` / `denyRead` settings are what actually stop the subprocess read;
the permission `deny` alone does not.

The second reason is throughput, not just safety. The sandbox lets Claude run most
shell commands **without a per-command prompt**, because the OS boundary — not a
human clicking "allow" — is what contains the blast radius (Anthropic reports an
internal **84% reduction** in permission prompts). For an unattended or
fast-iterating session that is the difference between real autonomy and a run that
stalls on approvals — and it is a _safer_ way to get there than
`--dangerously-skip-permissions`, which removes the checks instead of enforcing a
boundary.

## How to apply

**Turn it on, and prefer it over bypass mode for autonomy.** Enable
`sandbox.enabled` in `~/.claude/settings.json` (all projects) or per-project via
`/sandbox` → Mode → **auto-allow** (writes `.claude/settings.local.json`). In
auto-allow mode, sandboxed Bash commands run without prompting while the OS holds
the boundary — the autonomy you'd otherwise reach for
`--dangerously-skip-permissions` to get, without giving up the `deny` backstop.

**Both halves or neither — filesystem _and_ network.** "Effective sandboxing
requires both filesystem and network isolation. Without network isolation, a
compromised agent could exfiltrate sensitive files like SSH keys; without
filesystem isolation, a compromised agent could backdoor system resources." By
default writes are confined to the working dir + session temp, and **no network
domains are pre-allowed** (the first new domain prompts). Widen deliberately:

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": { "allowWrite": ["~/.kube", "/tmp/build"] },
    "credentials": {
      "files": [
        { "path": "~/.aws/credentials", "mode": "deny" },
        { "path": "~/.ssh", "mode": "deny" }
      ],
      "envVars": [{ "name": "GITHUB_TOKEN", "mode": "deny" }]
    }
  }
}
```

**Close the credential-read default explicitly.** The default read policy allows
reading the _entire computer_ except a few denied dirs — which **still includes**
`~/.aws/credentials` and `~/.ssh/`. Add a `sandbox.credentials` block (Claude Code
v2.1.187+) to deny those files and unset secret env vars for sandboxed commands;
this is the subprocess-read gap from the Why section, closed.

**The two layers stack — keep the `deny` list too.** Explicit permission `deny`
rules are still honored inside the sandbox, and content-scoped `ask` rules (e.g.
`Bash(git push *)`) still prompt even for sandboxed commands. So the three-tier
posture ([`./permissions-are-deny-ask-allow-not-an-on-off-switch.md`](./permissions-are-deny-ask-allow-not-an-on-off-switch.md))
and the sandbox reinforce each other; the sandbox is not a reason to loosen `deny`.

## Edge cases / when the rule does NOT apply

- **Platform.** The built-in sandbox runs on macOS (Seatbelt), Linux and WSL2
  (`bubblewrap` + `socat`). **Native Windows is not supported** — run Claude Code
  inside WSL2 there. On a host where the sandbox can't start it warns and falls
  back to _unsandboxed_ by default; set `sandbox.failIfUnavailable: true` to make
  that a hard stop where the sandbox is a required gate.
- **It's a risk reducer, not a hard boundary.** The network proxy filters by
  hostname and does **not** inspect TLS, so a broad `allowedDomains` (e.g. all of
  `github.com`) can leave a domain-fronting exfil path; broad `allowWrite` into a
  `$PATH` dir or `.bashrc` re-opens code-execution. Widen one side and re-check the
  other. For a stronger boundary use a dev container / VM
  ([Sandbox environments](https://code.claude.com/docs/en/sandbox-environments)).
- **Scope.** The sandbox isolates **Bash subprocesses only.** Read/Edit/Write use
  the permission system directly; MCP tools and computer-use run under their own
  boundaries. Subagents inherit the parent session's sandbox config.
- **Non-Claude-Code hosts** (Copilot / Cursor / Codex) have no equivalent — the
  _principle_ (an OS boundary beats a string-matched rule) ports; this specific
  feature does not. This is the same Claude-only caveat as the OS-sandbox note in
  [`../knowledge/concepts/containment-posture.md`](../knowledge/concepts/containment-posture.md).

## See also

- [`./permissions-are-deny-ask-allow-not-an-on-off-switch.md`](./permissions-are-deny-ask-allow-not-an-on-off-switch.md) — the model-evaluated layer this OS-enforced layer complements; the sandbox is where the "`deny` doesn't reach subprocesses" gap in that rule is actually closed.
- [`../knowledge/claude-code-permissions.md`](../knowledge/claude-code-permissions.md) — the "`Read`/`Edit` deny doesn't stop subprocess access; OS-level enforcement requires the sandbox" gap this rule operationalizes, plus the sandbox-escape CVE history (a reminder it's a risk reducer, not a hard wall).
- [`./web-access-allow-deny-list-before-first-fetch.md`](./web-access-allow-deny-list-before-first-fetch.md) — the WebFetch egress control; the sandbox's `allowedDomains` is the Bash-subprocess analogue for network egress.

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-07-02 subreddit scan](../../../docs/research/2026-07-02-claude-subreddit-scan/README.md)),
grounded against the Anthropic primary docs
[Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing)
(Seatbelt/bubblewrap OS enforcement, auto-allow mode, the `sandbox.*` settings and
`credentials` block, the both-halves warning, the TLS/host-not-inspected
limitation) and cross-checked against this repo's own
[`../knowledge/claude-code-permissions.md`](../knowledge/claude-code-permissions.md)
subprocess-access gap (the hole this feature fills). The 84%-prompt-reduction and
autonomy framing is Anthropic's; the specific version/platform facts are
verify-at-use (the feature is evolving — `credentials` landed v2.1.187,
per-session domain-allow v2.1.191).

---

_Last reviewed: 2026-07-02 by `claude`_

# The permission list is policy; the OS-enforced sandbox is containment — run both

**Status:** Pattern
**Domain:** Agent design / Security / Permissions
**Applies to:** `ravenclaude-core`

---

## Why this exists

[`permissions-are-deny-ask-allow-not-an-on-off-switch.md`](./permissions-are-deny-ask-allow-not-an-on-off-switch.md)
establishes that the `deny`/`ask`/`allow` lists are a **policy** layer: the
`allow` list is a convenience layer and the `deny` list is the backstop. But
there is a subtler limit that rule names only in passing — **every permission
decision is made _before_ the command runs, from the command _string_** (plus a
classifier's judgement in auto mode). So the whole permission model answers one
question: _should we launch this command?_ It cannot answer _what will the
command actually touch once it is running?_ A command whose string looks benign
can do more than its name suggests, spawn a child process that does something
else, or be mis-classified — and the permission layer has already made its call
by then.

Claude Code's **sandboxed Bash tool** closes exactly that gap. It is a second,
**OS-enforced containment** layer that the operating system applies to the
running process and all of its children, "so it holds regardless of what the
model chose to run and even if an allowed command does more than its name
suggests" (Anthropic docs). The two are explicitly **complementary layers**, not
alternatives: the permission list decides _whether to launch_; the sandbox
bounds _what a launched command can reach_. For an unsupervised or scheduled run
— this marketplace's own posture — you want both.

## The two layers, side by side

| | Permission rules (policy) | Sandbox (containment) |
| --- | --- | --- |
| **Question it answers** | Should this command be *launched*? | What can a launched command *reach*? |
| **When it decides** | Before the process runs, from the command string (+ classifier in auto mode) | Continuously, on the running process and every child |
| **Enforced by** | Claude Code, in-process | The OS — Seatbelt (macOS), bubblewrap (Linux / WSL2) |
| **Fails if** | The string is deceptive or a child does more than the parent | (Defense-in-depth caveats below — it is not a complete boundary) |
| **Configured in** | `permissions.deny`/`ask`/`allow` | `sandbox.*` in `settings.json`; `/sandbox` panel |

## How to apply

1. **Turn the sandbox on for autonomous / scheduled runs.** Set
   `sandbox.enabled: true` in `~/.claude/settings.json` (all projects) or a
   project's `.claude/settings.json`, or open `/sandbox` and pick a mode.
   Auto-allow mode runs sandboxed Bash without a prompt because the boundary
   contains it — Anthropic measured an **~84% reduction in permission prompts**
   internally — so the safety dividend and the autonomy dividend arrive together.
2. **Keep both filesystem _and_ network isolation.** The docs are explicit:
   _"Effective sandboxing requires both."_ Filesystem default = read/write the
   working directory + session temp, blocked from writing anywhere else
   (including `~/.bashrc` and `/bin/`). Network default = a proxy with **no**
   domains pre-allowed, prompting on the first new host. Drop network isolation
   and a compromised command can exfiltrate `~/.ssh`; drop filesystem isolation
   and it can backdoor a binary on `$PATH`.
3. **Let the layers compose — do not treat the sandbox as a reason to loosen the
   deny list.** Even in auto-allow mode the policy layer still bites: explicit
   `deny` rules are **always** respected, `rm`/`rmdir` against `/` or your home
   directory still prompt, and content-scoped `ask` rules (e.g.
   `Bash(git push *)`) still force a prompt. The deny list this repo ships
   (`rm -rf`, `git push --force`, `npm publish`, …) keeps doing its job _under_
   the sandbox; the sandbox just stops a name-deceptive or mis-classified
   command from escaping the working directory in the first place.
4. **Block credential reads explicitly — the default read policy doesn't.** The
   sandbox's default *read* scope is the whole machine, so `~/.aws/credentials`
   and `~/.ssh/` are still readable unless you add them to `sandbox.credentials`
   (deny file reads + unset secret env vars) or `sandbox.filesystem.denyRead`.
   For unattended runs holding cloud creds, do this.

## Edge cases & honest caveats (verify-at-use)

- **It is defense-in-depth, not a jail.** Anthropic states plainly: _"Sandboxing
  reduces risk but is not a complete isolation boundary."_ The built-in network
  proxy allow-lists by hostname and **does not inspect TLS**, so a broad
  `allowedDomains` entry (e.g. `github.com`) can be a data-exfiltration path via
  domain fronting. Keep the domain allow-list narrow; use a TLS-terminating
  custom proxy if your threat model needs it.
- **Broad widenings re-open the hole.** A wide `allowWrite` into a `$PATH` or
  shell-config directory, an over-broad `allowedDomains`, an `allowUnixSockets`
  entry exposing `/var/run/docker.sock`, or Linux `enableWeakerNestedSandbox`
  each weakens containment. When you widen one side, check you haven't undone the
  other.
- **Scope is Bash subprocesses only.** Read/Edit/Write file tools use the
  permission system directly (not the sandbox), computer-use runs on your real
  desktop, and subagents inherit the parent session's sandbox config. The
  sandbox does **not** run on native Windows (use WSL2) and needs `bubblewrap` +
  `socat` on Linux/WSL2.
- **This is not a substitute for the tribunal or the destructive-action guard.**
  Those govern _intent_ and _irreversibility_; the sandbox governs _blast
  radius_. Different layers, all kept.

## See also

- [`./permissions-are-deny-ask-allow-not-an-on-off-switch.md`](./permissions-are-deny-ask-allow-not-an-on-off-switch.md)
  — the policy-layer sibling. That rule sorts operations into `deny`/`ask`/`allow`; this one adds the OS-enforced containment beneath them. Read them together.
- [`./web-access-allow-deny-list-before-first-fetch.md`](./web-access-allow-deny-list-before-first-fetch.md)
  — the egress-policy companion for `WebFetch`; the sandbox's network proxy is the Bash-subprocess analogue of the same allow/deny discipline.
- [`./runaway-brake-prevents-the-thrash-loop.md`](./runaway-brake-prevents-the-thrash-loop.md)
  — another guardrail sized for unsupervised / auto-mode sessions; the sandbox is the containment member of that same family.
- [`../CLAUDE.md`](../CLAUDE.md) § "Containment posture — the boundary the tribunal structurally can't provide" + the `containment-posture` Learn concept — the constitution already establishes that **only the OS holds the subprocess line** (a `deny` on the agent's `Read` tool doesn't stop a script the agent writes and runs) and that the container/worktree is the model-agnostic boundary. This rule is the consumer-facing, `/sandbox`-specific operationalization of that principle: where the constitution's caveat is "the OS sandbox is Claude-only, so under Copilot the container/worktree is the containment," this rule is "under Claude Code, turn the built-in Bash sandbox on."

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-06-30 subreddit scan](../../../docs/research/2026-06-30-claude-subreddit-scan/README.md)),
grounded against Anthropic's primary docs —
[Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing)
(the layer model, the filesystem/network boundaries, the OS primitives, the
"complementary layers" and "not a complete isolation boundary" framing) — and
against this repo's own posture: it runs **unattended scheduled routines** on
Claude Code on the web behind a `settings.json` `deny` list, which is precisely
the policy-layer-plus-containment-layer threat model this rule describes. The
~84% prompt-reduction figure is an Anthropic-reported internal measurement
(verify-at-use — the number moves); the **mechanic** (policy decides launch,
the OS enforces the boundary on the running process) is the durable part.

---

_Last reviewed: 2026-06-30 by `claude`_

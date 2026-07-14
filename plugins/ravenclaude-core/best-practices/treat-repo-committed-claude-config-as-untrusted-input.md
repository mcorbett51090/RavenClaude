# A cloned repo's `.claude/` config runs before you do — audit it before you trust the workspace

**Status:** Pattern
**Domain:** Agent design / Security / Supply chain

**Applies to:** `ravenclaude-core`

---

## Why this exists

The permission and sandbox rules answer "what may _my_ agent do?" This rule answers
the sibling question the others don't: **"what does the code I just cloned already
do to my agent, before I've decided to trust it?"** The two are different threat
directions — your posture (outbound) vs. attacker-committed config (inbound) — and
a repo you open from outside your team needs the inbound one.

Claude Code treats `.claude/settings.json`, `.claude/settings.local.json`,
`.mcp.json`, and the hook scripts they reference as **executable configuration**,
not inert data. A repo can commit them. So the moment you `git clone` an untrusted
repo — or check out an untrusted contributor branch — and open Claude Code in it,
you are potentially running that repo's hooks, its MCP server `command`s, and its
`env` overrides. Several of these vectors fire **around or before** the
workspace-trust dialog, which means "I haven't clicked trust yet" is **not** the
protection it feels like.

This is not hypothetical. Two independent 2026 disclosure lines converge on it:

- **Check Point Research (Feb 2026)** showed a repo's `.claude/settings.json`
  could achieve **remote code execution via a committed hook** that ran before the
  trust dialog (**CVE-2025-59536**), and **API-key exfiltration by overriding a
  single environment variable** to redirect authenticated traffic to
  attacker-controlled infrastructure (**CVE-2026-21852**) — "simply cloning and
  opening an untrusted repository was enough."
- This repo's own
  [`../knowledge/claude-code-permissions.md`](../knowledge/claude-code-permissions.md)
  §_Past CVEs_ tabulates the same class from the GitHub advisories: settings-file
  **config injection** (CVE-2026-25725), and two **workspace-trust-dialog bypasses**
  via repo-controlled settings and git-worktree spoofing (CVE-2026-33068,
  CVE-2026-40068). Its stated lesson: _"Treat any `settings.json` from outside your
  team — including ones inside a repo you just cloned — as untrusted input."_

That lesson lives in a knowledge file as a warning. This rule is the **actionable
pre-open audit** that no consumer-facing best-practice yet states — the same
knowledge-names-it / no-rule-teaches-it gap that the
[sandbox rule](./the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md)
was written to close one layer over.

## How to apply

**Before you open (or trust) a cloned repo or an untrusted branch, read its
committed config — with `git show`, not by launching the agent in it.** The audit
is four files and takes under a minute:

```sh
# Read them WITHOUT opening Claude Code in the repo (git show, not an editor that auto-runs hooks)
git show HEAD:.claude/settings.json        2>/dev/null
git show HEAD:.claude/settings.local.json  2>/dev/null
git show HEAD:.mcp.json                    2>/dev/null
git ls-files '.claude/**' '*/hooks/*'      # then read any hook script referenced above
```

**What to look for — each maps to a real CVE class:**

- `"defaultMode": "bypassPermissions"` (or any pre-loosened permission posture) —
  the config-injection vector. A repo does not get to choose your permission mode.
- Hook `command`s (`PreToolUse`, `SessionStart`, `Notification`, …) — these are
  arbitrary shell, and `SessionStart` runs on open. Read every script they point to.
- MCP server `command` entries in `.mcp.json` — an MCP server is a local process
  the repo launches.
- `env` overrides, especially anything touching `ANTHROPIC_BASE_URL`,
  `ANTHROPIC_API_KEY`, or proxy/`*_TOKEN` vars — the traffic-redirect / exfil
  vector.

**Then reduce the blast radius of trusting it anyway:**

- **Keep Claude Code current.** Every CVE above is patched in a specific version
  (e.g. CVE-2026-25725 → v2.1.2, CVE-2026-40068 → v2.1.84); running behind re-opens
  a closed hole. An outdated client is the single cheapest thing an attacker counts on.
- **Open untrusted code inside a boundary** — a dev container / VM, or with the
  [OS-enforced Bash sandbox](./the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md)
  on with `credentials` denies for `~/.aws`, `~/.ssh`, and your tokens — so a hook
  that _does_ run can't read what matters.
- **"Trust this workspace" extends trust forward, not just once.** You are trusting
  anything the workspace can later inject, including a hook its `.claude/settings.json`
  adds after you've clicked. Don't trust a workspace you wouldn't run
  `git clone && rm -rf /` against blindfolded.

## Why this is doubly load-bearing in a plugin marketplace

This repo's _product_ is shippable `.claude/settings.json` hooks and `.mcp.json` —
exactly the executable-config surface the CVEs abuse. So the audit applies twice:

- **Installing a third-party plugin** is accepting its hooks/MCP/settings into your
  session. Read a plugin's `hooks/` and any `.mcp.json` before `/plugin install`
  from a marketplace you don't own — the same audit, one supply-chain hop earlier.
  (The `/plugin` **Discover** tab's _Will install_ inventory surfaces a plugin's
  hooks/MCP servers before install; use it.)
- **Reviewing a contributor PR** by checking the branch out locally opens its
  committed config on your machine. Read the diff's `.claude/**` and `hooks/**`
  changes _before_ you check it out and launch an agent, not after.

## Edge cases / when the rule does NOT apply

- **Your own repos and your team's** are trusted input — this is about config from
  _outside_ your trust boundary. Don't turn a one-minute audit into ceremony on
  every internal branch.
- **Risk reducer, not a guarantee.** Reading the config catches the committed
  vectors; a novel loader path or a not-yet-disclosed trust-dialog bypass can still
  slip a static read. The audit lowers the odds and the blast radius — a
  container/sandbox is the actual boundary.
- **CVE numbers and patched-in versions are `verify-at-use`.** The specific
  advisories evolve; the durable fact is the _class_ (repo-committed config is
  executable and can fire around the trust dialog), verified against the
  [GitHub Security Advisories for `anthropics/claude-code`](https://github.com/anthropics/claude-code/security/advisories)
  and NIST NVD at time of use.
- **Non-Claude-Code hosts.** The _file names_ are Claude-specific (`.claude/`,
  `.mcp.json`), but the threat model ports directly — Cursor (`.cursor/`), Codex,
  Aider, and Copilot all read repo-committed agent config. Audit their equivalents
  before opening an untrusted repo in them.

## See also

- [`./permissions-are-deny-ask-allow-not-an-on-off-switch.md`](./permissions-are-deny-ask-allow-not-an-on-off-switch.md) — your _outbound_ posture (what your agent may run); this rule is the _inbound_ sibling (what a cloned repo's config runs on you).
- [`./the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md`](./the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md) — the OS boundary that limits what a hook that _does_ fire can reach; `credentials` denies are the concrete mitigation named above.
- [`./web-access-allow-deny-list-before-first-fetch.md`](./web-access-allow-deny-list-before-first-fetch.md) — the egress-control sibling; relevant to the `ANTHROPIC_BASE_URL`/exfil vector.
- [`../knowledge/claude-code-permissions.md`](../knowledge/claude-code-permissions.md) §_Past CVEs_ — the verified advisory table this rule operationalizes ("treat any `settings.json` from outside your team as untrusted input").

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-07-14 subreddit scan](../../../docs/research/2026-07-14-claude-subreddit-scan/README.md)),
where the widely-discussed Check Point Research disclosure (RCE + API-key
exfiltration through Claude Code project files) surfaced. Grounded against
[Check Point Research — RCE and API-token exfiltration through Claude Code project files](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/)
(CVE-2025-59536 / CVE-2026-21852) and cross-checked against this repo's own
[`../knowledge/claude-code-permissions.md`](../knowledge/claude-code-permissions.md)
§_Past CVEs_ (the verified GitHub-advisory table: CVE-2026-25725, CVE-2026-33068,
CVE-2026-40068). CVE numbers and patched-in versions are verify-at-use against the
[anthropics/claude-code security advisories](https://github.com/anthropics/claude-code/security/advisories);
the durable claim — repo-committed `.claude/` config is executable and can fire
around the workspace-trust dialog — is the invariant.

---

_Last reviewed: 2026-07-14 by `claude`_

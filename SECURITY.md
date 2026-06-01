# Security policy

RavenClaude is a private Claude Code plugin marketplace operated by **Raven Power LLC**. The maintainer is **Matt Corbett** (`@mcorbett51090`). Repo access is limited to a named collaborator list — see [`docs/access.md`](docs/access.md).

This document covers responsible disclosure for vulnerabilities in **plugin content shipped from this marketplace** (agents, skills, hooks, bundled MCP servers, CI workflows). Vulnerabilities in Claude Code itself should go to [Anthropic](https://www.anthropic.com/) directly — they're out of scope here.

---

## What counts as a security issue

In a marketplace whose payload is agent definitions, skills, hooks, and a bundled MCP server, the realistic threat surface is:

- **Hooks that execute attacker-controlled input** — e.g., a hook that pipes a filename into `eval`, runs unquoted variables through `bash -c`, or trusts a path from a tool result without sanitization.
- **Skill or agent files with prompt-injection payloads** — content designed to coerce an agent in a consumer project into exfiltrating data, running destructive commands, or bypassing the user's intent.
- **Workflow files (`.github/workflows/*`) that run untrusted inputs in privileged contexts** — `pull_request_target` patterns, secret leakage in logs, dependency confusion.
- **Bundled or referenced MCP servers** that handle file content, network requests, or shell commands and have a known unpatched issue (e.g., the `pbix-mcp` server bundled in `power-platform`).
- **Credentials or secrets accidentally committed** — `.env` files, API tokens, real tenant identifiers in git history.
- **Supply-chain risk in imported third-party skills** — the 9 Daniel Kerridge skills in `power-platform`, the `pbix-mcp` server, or any future imports.

Functional bugs (a flow that doesn't trigger correctly, a wrong DAX recommendation, a typo in a template) are bugs — file them via the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md), not under security.

---

## How to report

**Do not open a public GitHub issue for a security vulnerability.** This repo is private, but issues are visible to all collaborators.

Instead, contact the maintainer directly:

- **Email:** `matt@ravenpower.net` — subject line starting with `[RavenClaude security]`.
- **GitHub:** open a private security advisory at https://github.com/mcorbett51090/RavenClaude/security/advisories/new (requires GitHub login).

Please include:

1. A description of the vulnerability and which plugin / file / workflow it affects.
2. The version (plugin `version` from `plugin.json` or commit SHA).
3. Reproduction steps — what an attacker would do, what the impact is.
4. Whether you've already discussed this with anyone else, and if so, who.
5. Any suggested fix, if you have one.

Encryption: if the report is sensitive enough that email-in-the-clear is the wrong channel, request a Signal handoff in your first message and I'll respond with a channel.

---

## What happens next

| Timeline | What we do |
|---|---|
| Within 3 business days | Acknowledge receipt and confirm whether it's in scope for this repo. |
| Within 14 days | Triage: severity assessment, affected plugin(s), affected versions, scope of impact on consumers who have already installed. |
| Coordinated | If a fix is needed, we develop it on a private branch, prepare a release with notes, and coordinate disclosure timing with the reporter. |
| At release | Publish a patched release with a clear note in the affected plugin's `CHANGELOG.md` and a GitHub Security Advisory describing the issue and the fix. |

For high-severity issues (active exploitation, credential exposure, RCE in a hook) we'll move faster — same-day acknowledgement, fix within 72 hours if feasible.

---

## What we ask of reporters

- Give us a reasonable window to fix before public disclosure. Default: 90 days from acknowledgement, shorter if the issue is already public, longer if a coordinated fix is complex.
- Don't run probing tests against other RavenClaude consumers — we don't have the visibility or authority to consent on their behalf.
- Don't test against the maintainer's own production environments without explicit pre-arrangement.

We'll credit reporters by name (or pseudonym, if you prefer) in the relevant `CHANGELOG.md` and GitHub Security Advisory, unless you'd rather stay anonymous.

---

## Out of scope

- **Claude Code itself** — report to Anthropic.
- **Microsoft Power Platform** vulnerabilities — report to Microsoft Security Response Center (MSRC).
- **Vulnerabilities in upstream third-party content** that we bundle (`pbix-mcp`, the Kerridge skills) — please report those to the upstream maintainers first. If you've reported upstream and the upstream is unresponsive or the issue affects RavenClaude consumers specifically, then yes, contact us.
- **Theoretical risks with no realistic exploit path** — e.g., "a hook *could* be modified by a malicious collaborator." That's a process/access-control concern, not a vulnerability.
- **DoS via large input** to a local hook or agent — these are local tools running on the user's machine; resource exhaustion is a usability bug, not a security issue.

---

## Defaults and floors (added 2026-06-01, v0.101.0)

These are the security-relevant default behaviors the marketplace ships. Consumers can tune some of them through the dashboard; **the floor cannot be tuned away**.

### The non-removable `security_deny` floor

`comfort-posture.yaml`'s `security_deny:` list is **always unioned with `DEFAULT_SECURITY_DENY`** when emitted to `.claude/settings.json`. A user (or the dashboard, or an attacker via a typo) **cannot wipe the baseline** by setting `security_deny: []` or omitting the field — the baseline always appears first in the emitted `permissions.deny` bucket.

Baseline entries cover: `rm -rf`, `git push --force`, `git reset --hard`, `git clean -fd`, `npm publish`, `curl | sh`, `wget | sh`, reads of `.env*` / `~/.ssh` / `~/.aws` / `~/.config/gcloud` / `~/.azure` / `~/.kube/config` / `~/.docker/config.json`, and the in-repo secret files listed in `apply-comfort-posture.py:DEFAULT_SECURITY_DENY`. Authoritative source: that constant.

Regression contract: `tests/fixtures/test_security_deny_floor.py`. If you find a way to bypass the floor, treat it as a high-severity report and email per the disclosure policy above.

### Codespace forwarded ports must stay Private

`scripts/serve-dashboards.py` binds to `0.0.0.0` so it works through Codespace port forwarding. **The port must remain Private** (the default). If you flip it to Public, the `/__save` + `/__run` POST surface becomes reachable from the public internet on a path that doesn't expect to be public. The startup banner check refusing `0.0.0.0` on `GITHUB_CODESPACES_PORT_VISIBILITY=public` is a tracked follow-up (`docs/security/2026-06-dashboard-and-posture-apply-review.md` finding #3).

### CSRF posture

The dashboard server validates `Origin` / `Host` / `Sec-Fetch-Site` on state-changing endpoints. This blocks a malicious webpage in the same browser session from POSTing to `127.0.0.1`. A scripted HTTP client that omits `Origin` and sets `Host: 127.0.0.1:8000` would bypass the check — currently mitigated by loopback / private-port-forwarding only. A per-process random CSRF token (embedded in `dashboard.html`, checked on every state-changing endpoint) is a tracked follow-up (`docs/security/2026-06-dashboard-and-posture-apply-review.md` finding #4).

### `shell_package_install: ask` is the consumer-facing default

As of v0.101.0, the balanced posture seed defaults `shell_package_install` to `ask` at the project layer. A malicious dependency in `package.json` (registry confusion, post-install script, tarball-from-`/tmp`) would otherwise execute silently when an agent runs `npm install` / `pip install`. The friction is one prompt per install. Consumers who have vetted their supply chain can flip this back to `allow` from the dashboard's Set up tab.

**`shell_code_exec` stays `allow`** — flipping to `ask` would prompt on every script the agent executes, which would surface dozens of times per session and likely push consumers off the marketplace. If you're working on partner-confidential code, consider flipping this in your own posture via the dashboard.

## Hardening notes (for collaborators editing this repo)

These aren't disclosure rules — they're house rules for contributors to reduce the chance of introducing the kind of issue this policy is about:

- **Hooks**: always `set -euo pipefail`. Quote every `"$variable"`. Never `eval` a tool-provided string. Validate inputs before passing them to shell builtins.
- **Workflows**: never use `pull_request_target` with checkout of the PR head unless you know exactly why. Pin third-party actions to a commit SHA, not a tag.
- **MCP declarations**: pin the command, document the install prerequisite, document the failure mode if the prerequisite is missing.
- **Imported content**: include a `NOTICE.md`, link the upstream, record the upstream commit SHA you imported from.
- **Secrets**: never commit. The repo is private but git history is forever — if a secret lands, rotate it and follow up with a force-push history rewrite via a coordinated maintainer action.

When in doubt, route the concern through Matt before merging.

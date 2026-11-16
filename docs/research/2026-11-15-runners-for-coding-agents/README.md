# Runners for AI coding agents (research, 2026-11-16)

How coding-agent sessions use compute, and what that means for this factory's fleet. This sits on top of [the 2026-11-15 self-hosted runner research](../2026-11-15-self-hosted-runners/README.md) and the Website guide `docs/RUNNER-FLEET-GUIDE.md` (PR #1481). It does not repeat label matching, ephemeral loops, or Mac sleep. Those still hold.

Facts were checked against vendor docs on 2026-11-16. Anything that ships monthly is marked `[verify-at-use]`. Four research passes were run. The fourth added no new primary fact ([pass log](passes.md)).

The account `mcorbett51090` is a **user**, not an organization (GitHub API, 2026-11-16). RavenClaude is **public**. RavenPower-Website is **private**. Larger hosted runners, runner groups, and organization-level Copilot runner locks are organization or enterprise features, so they are not available on this account.

## Files

| File | What it covers |
|---|---|
| [01-where-each-agent-runs.md](01-where-each-agent-runs.md) | Which product runs on whose machines, and which of those machines are our runners |
| [02-copilot-actions-path.md](02-copilot-actions-path.md) | Copilot cloud agent on Actions: setup file, 59-minute cap, firewall, architecture, hosts |
| [03-claude-code-action.md](03-claude-code-action.md) | Claude Code's GitHub Action: permissions, timeouts, what the live Website workflow already does |
| [04-cursor-and-codex.md](04-cursor-and-codex.md) | Cursor cloud agents, CLI-in-Actions, and self-hosted workers; Codex cloud and `openai/codex-action` |
| [05-workload-isolation-storms.md](05-workload-isolation-storms.md) | Long jobs, idle waiting, injection, storms, cost, observability |
| [06-recommendations.md](06-recommendations.md) | Recommendations for this fleet, and the live Website changes that need a GO |
| [sources.md](sources.md) | URLs, grouped |
| [passes.md](passes.md) | Pass log |

## Top findings

1. **An agent job holds a runner for the whole model wait.** Tests use CPU. An agent session is mostly network idle and still occupies one slot. On Website, the Claude workflow's long job is `timeout-minutes: 90` with a 120-turn cap (default-branch `.github/workflows/claude.yml`, read 2026-11-16). GitHub's Copilot docs say an Actions session stops at 59 minutes and that the cap cannot be raised.

2. **Copilot on Actions is a poor default for this fleet.** The 2026-10-28 changelog says the cloud sandbox is the default, has no one-hour cap, and runs on GitHub-managed infrastructure. The Actions environment doc says the agent is compatible with Ubuntu x64 and Windows 64-bit only, and that self-hosted use requires the integrated firewall to be disabled or the agent is blocked. Larger hosted runners are an organization or enterprise feature. This account is a user.

3. **The live Claude workflow's fallback label is `["self-hosted"]`.** `runs-on` is `vars.CLAUDE_RUNS_ON` with that fallback (same file). The 2026-11-15 fleet table lists the secrets runner as `self-hosted` plus `raven-secrets`. The Claude job does not contain the name-guard regex. Pin the variable to `lane-medium` plus `host-box`, and change the fallback so an empty variable is not the only label.

4. **The name guard stays as written, and it does not separate the Yoga from the box.** The live regex `^box-((fast|large|web)[0-9]+|raven-(web|light)-[0-9]+)$` matches `box-web11` and `box-fast11`, which the 2026-11-15 guide lists as the Yoga registrations. Routing is the label set. Do not widen the regex so that new agent names match.

5. **Products do not start CI the same way.** Copilot's risks page says workflows do not run until a person with write access approves them (default). The Claude GitHub App's pushes do start workflows. Website's workflow is written so that they do, because a default-token push leaves required checks unstarted. Cursor cloud agents open pull requests from Cursor's VMs; the CI those pull requests start is what reaches our runners. `commerce-ci.yml` has no `concurrency` key (code search, default branch, 2026-11-16).

6. **Cursor's self-hosted worker is a different program from an Actions runner.** The self-hosted machines page says the worker opens a long-lived outbound HTTPS connection and that Cursor does not connect into the network. Do not start that process as the same OS user as the Actions runners. Codex cloud, on the legacy environments page, also runs in OpenAI's container. `openai/codex-action` runs inside a workflow. Website has no such workflow (code search, 2026-11-16).

7. **Public RavenClaude stays off self-hosted runners.** GitHub's secure-use page says self-hosted runners can be persistently compromised by untrusted workflow code and tells you not to attach them to public repositories. Website is the private repo where the fleet lives.

`ravenclaude-core` was not edited. `knowledge/github-actions-hardening.md` and `knowledge/claude-in-ci.md` already cover token scope and the default-token push that does not start workflows (those files say checked 2026-08). A concurrent branch is hardening that plugin. The new rows are in `devops-cicd` and `ai-coding-model-guidance`.

# 01: Where each coding agent actually runs

Checked 2026-11-16. "Our runners" means the Website fleet: the 8-core Linux box, the Yoga sandbox (1.5 CPU), and the planned Mac mini and MacBook. Lanes in force, per the owner: `lane-fast`, `lane-medium`, `lane-slow`, `host-box`, `host-yoga`.

| Product | Where the agent loop runs | Does it occupy a GitHub Actions runner? | What then hits our CI |
|---|---|---|---|
| Copilot cloud agent, Cloud sandbox (default since 2026-10-28) | GitHub-managed sandbox | No | A pull request, and workflows stay off until a person approves them (default) |
| Copilot cloud agent, Actions | A GitHub Actions job | Yes, for up to 59 minutes | Same approval gate |
| Copilot CLI `--environment-host` | A machine you register | No. It is not an Actions runner | Whatever that machine's shell can push |
| Claude Code GitHub Action | Whatever `runs-on` the workflow sets | Yes, for the whole job | Pushes from the Claude GitHub App start workflows |
| Claude Code on the web / cloud | Anthropic cloud | No | A pull request, then your CI |
| Cursor cloud agent | A Cursor VM | No | The PR's workflows, on our runners |
| Cursor self-hosted worker or pool | Your machine, outbound HTTPS only | No | Same, if the worker pushes |
| Cursor CLI inside a workflow | The job's runner | Yes | The job itself is the CI |
| Codex cloud | An OpenAI container | No | A pull request you open |
| `openai/codex-action` | The job's runner | Yes | Only if a later step pushes |

Sources for each row are in [sources.md](sources.md). The split that matters: **three of these products never sit on our runners, and their pull requests still do.**

## What this account can and cannot buy

- **User account.** Larger GitHub-hosted runners exist only for organizations and enterprises on Team or Enterprise Cloud ([larger runners](https://docs.github.com/en/actions/concepts/runners/larger-runners), [custom images](https://docs.github.com/en/actions/how-tos/manage-runners/larger-runners/use-custom-images)). Runner groups are organization-only (already in the 2026-11-15 research). Organization Copilot settings that force every repository onto one runner type do not apply ([org runner controls](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/configure-runner-for-coding-agent)).
- **Public RavenClaude.** Standard GitHub-hosted minutes are free on a public repository. Self-hosted runners must not be attached to it ([secure use](https://docs.github.com/en/actions/reference/security/secure-use)). Agent workflows in this marketplace stay on `ubuntu-latest`.
- **Private Website.** Hosted runners are not the fleet (the no-hosted-runners rule in `commerce/test/no-hosted-runners.test.ts`, cited by the live Claude workflow). Agent jobs that must run here run on the box.

## Architecture

| Runner | Copilot on Actions | Claude workflow as written today | Codex action |
|---|---|---|---|
| Box, Linux x64 | Allowed | Allowed. The `gh` install step downloads `linux_amd64` | Allowed (Linux) |
| Yoga sandbox, Linux x64, 1.5 CPU | Allowed by the product, wrong for a 59-minute hold | Allowed by the binary, wrong for a 90-minute hold | Same |
| Mac mini macOS, or Linux arm64 VM | Not supported (Ubuntu x64 or Windows 64-bit only) | The pinned `gh` tarball is amd64, so the current step fails on arm64 | macOS is allowed; arm64 was not stated on the action page |

Copilot's architecture line is in [the environment doc](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment): "only compatible with Ubuntu x64 Linux and Windows 64-bit runners."

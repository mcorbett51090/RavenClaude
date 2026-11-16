# Coding-agent compute placement

**Plugin:** `ai-coding-model-guidance`
**Last retrieved:** 2026-11-16
**Scope:** where the agent process runs. Model choice stays in [`cross-tool-model-lineup-2026.md`](cross-tool-model-lineup-2026.md). This file is not part of that closed-world list.

Volatile rows are `[verify-at-use]`. One factory's lane labels and a live workflow are written up in [`docs/research/2026-11-15-runners-for-coding-agents/`](../../../docs/research/2026-11-15-runners-for-coding-agents/README.md). Do not copy those labels into a consumer repo that does not have them.

## Which machine the session occupies

| Surface | Where the loop runs | Occupies a GitHub Actions runner? | Retrieved |
|---|---|---|---|
| Copilot cloud agent, Cloud sandbox (default since the 2026-10-28 changelog) | GitHub-managed sandbox. No one-hour cap on that changelog. Billing "begins in November 2026" with no day stated | No | 2026-11-16 |
| Copilot cloud agent, Actions | A GitHub Actions job. Docs: 59-minute maximum, Ubuntu x64 or Windows 64-bit. Self-hosted requires the integrated firewall off | Yes | 2026-11-16 |
| Copilot CLI `--environment-host` | A machine the user registers. Not an Actions runner | No | 2026-11-16 |
| Codex cloud (legacy environments page) | OpenAI container. Internet off by default in the agent phase. Secrets removed before that phase. Cache up to 12 hours. Page is marked legacy | No | 2026-11-16 |
| `openai/codex-action` | The workflow's runner. Default `safety-strategy` is `drop-sudo`. Windows only with `unsafe`. Split the API key and the write token across two jobs | Yes | 2026-11-16 |
| Cursor cloud agent | Cursor VM | No. The pull request it opens then runs the repo's CI | 2026-11-16 |
| Cursor self-hosted worker | User machine, outbound HTTPS. The docs say Cursor does not connect inbound | No | 2026-11-16 |
| Cursor CLI in a workflow | The job's runner, `CURSOR_API_KEY` | Yes | 2026-11-16 |

Claude Code's GitHub Action is a job step on whatever `runs-on` the workflow sets. Runner placement for that action is `devops-cicd`'s map, not a model row. Escalate Claude model questions to `claude-app-engineering`.

## What to tell someone who asks "put the agent on our runners"

1. If the product's cloud mode already runs the session, the runner cost shows up later, as CI on the pull request. Cap that CI with `concurrency` and `cancel-in-progress` on test workflows. Leave a job that pushes uncanceled.
2. Copilot on Actions is the path that needs `copilot-setup-steps.yml`. The job must be named `copilot-setup-steps`. Other job keys are ignored. `timeout-minutes` max is 59. A failed setup step does not fail the session; the agent starts in the partial environment.
3. A self-hosted runner that also runs ordinary CI is a poor place for a model API key. Prefer the vendor sandbox. If the key has to be on a runner, pin `runs-on` to the trusted label set, set `timeout-minutes`, and do not use a fallback of `self-hosted` alone.
4. Public repositories: GitHub's secure-use page says not to attach self-hosted runners. Do not recommend one.
5. `queue: max` (up to 100 pending runs) is not a capacity plan. It piles work onto a small fleet until the 24-hour queue limit.

## Sources

- [Copilot environment](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment)
- [Copilot on GitHub.com](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github)
- [Changelog 2026-10-28](https://github.blog/changelog/2026-10-28-work-from-anywhere-with-a-new-connected-copilot-cloud-experience/)
- [Codex cloud (legacy)](https://learn.chatgpt.com/docs/environments/cloud-environment)
- [Codex GitHub Action](https://learn.chatgpt.com/docs/github-action)
- [Cursor cloud agents](https://cursor.com/docs/cloud-agent)
- [Cursor self-hosted machines](https://cursor.com/docs/cloud-agent/self-hosted)
- [Cursor CLI in Actions](https://cursor.com/docs/cli/github-actions)

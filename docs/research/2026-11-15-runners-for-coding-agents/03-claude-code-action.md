# 03: Claude Code GitHub Action

Primary pages, retrieved 2026-11-16:

- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [claude-code-action `docs/security.md`](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md) (raw file the same day)

The action is a job step. `runs-on` is the workflow's. Anthropic's cost section describes the default `ubuntu-latest` example, which spends GitHub-hosted minutes and API tokens (or a subscription, if the OAuth token is used). Nothing on that page forbids a self-hosted runner. A cancelled or timed-out session does not restore git config, and on a self-hosted runner that keeps its home directory a `safe.bareRepository` setting can be left behind. That matches a persistent box runner.

## Caps that matter on a small fleet

| Knob | What the docs say | What Website does today |
|---|---|---|
| Job timeout | "Set workflow-level timeouts to avoid runaway jobs." Hosted jobs die at 6 hours. Self-hosted jobs die at 5 days. The default token on a self-hosted job only refreshes for 24 hours ([limits](https://docs.github.com/en/actions/reference/limits), [GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token)) | `timeout-minutes: 90` on the long job, `2` on the authorize job |
| `--max-turns` | Pass it in `claude_args` | `120` |
| Concurrency | "Use GitHub's concurrency controls to limit parallel runs." | Job-level group per issue or pull request, `cancel-in-progress: false` |
| Who may start a run | Write access. Bots are rejected unless listed. `allowed_bots: '*'` on a public repo lets any GitHub App supply the prompt, and that bot is not checked for write access | A job `if` plus a collaborator-permission call, before the long job starts |

`cancel-in-progress: false` is the right setting for a job that pushes. Killing it mid-push leaves a partial branch. The workflow comment records an earlier bug: a workflow-level group cancelled a waiting hand-off because a later comment joined the group before the `if` ran. Keep the group on the job.

One group per issue does not cap the fleet. Ten issues at once are ten jobs, each allowed to hold a runner for 90 minutes. GitHub gives a job a single concurrency group, and the default queue keeps only one pending run. A single global group would drop waiting hand-offs for other issues. The cap that does not drop them is a label that only two box runners carry. See [06](06-recommendations.md).

## Permissions and the token that starts CI

The official app's permission set is wide (Actions read/write, Administration read, workflows read/write, and others). GitHub does not let an install accept a subset. A custom app can be limited to Contents, Issues, and Pull requests, and then it does not cover Claude's other GitHub features.

The action's own security doc says the token is short-lived and repo-scoped. Passing the workflow's default `GITHUB_TOKEN` as `github_token` makes pushes that do not start other workflows. Website's workflow removes checkout's credential include and lets the action push as the Claude app, on purpose, so Commerce CI starts. That behavior is already documented in `ravenclaude-core` `knowledge/github-actions-hardening.md`. This note only records that the live file still depends on it.

`show_full_output` is off by default. Actions debug mode turns it on. On a public repository those logs are public. Leave it off on RavenClaude. Website is private; debug mode still copies command output into the log.

## Untrusted text and `pull_request_target`

The security doc's rules that apply even on a private repo where only the owner comments:

- The model still reads an issue body when a maintainer triggers a run. Review that body first. HTML comments and a set of invisible characters are stripped. New bypasses are expected.
- `restrict_untrusted_prs` defaults to true. It denies common package-manager and shell commands on pull requests whose author lacks write access. It is a command list, not a sandbox. `Bash(git:*)` is called out as a way past that list (`git rebase --exec`). Website's allow list includes `Bash(git:*)` and `Bash(node:*)`. Node can reach the network. The workflow header already says pull-request text stays untrusted.
- Do not check out an untrusted ref into the workspace root on `pull_request_target` or `workflow_run`. Check out the base branch at the root, and put the head in a subdirectory if the model must read it.
- A cancelled run skips the restore of `GITHUB_ENV` and git config. Later `always()` steps still run.
- `claude-code-base-action` does not do the actor checks or the untrusted-PR command list. Website pins `claude-code-action` (commit `61a9c274fa7110a66dfafc1bbbced03833eb25fe`, tag v1.0.269 in the comment). Keep the full action.

## The live Website workflow (default branch, 2026-11-16)

Read via the GitHub contents API. Observations, not a proposal to edit it from this repo:

- Both jobs use `vars.CLAUDE_RUNS_ON`, fallback `["self-hosted"]`.
- The long job refuses a GitHub-hosted runner (`runner.environment != 'self-hosted'`). It does not check the runner name against the guard regex.
- Claude Code and `gh` are installed under a file lock into the runner user's home, because two concurrent installs corrupted a checksum (2026-11-08). That home is shared by every job on that OS user. An ephemeral runner would redo the install every job; the lock exists because the runners are persistent.
- The OAuth secret is on the long job only. The authorize job does not receive it.
- The `gh` binary is the amd64 tarball. An arm64 runner fails that step.

The fallback label set is the defect. `self-hosted` is on every runner, including `raven-secrets-pc` (`self-hosted`, `raven-secrets` in the 2026-11-15 fleet table). If `CLAUDE_RUNS_ON` is unset, the long job is eligible for that runner, and the name guard is not in this workflow to stop it.

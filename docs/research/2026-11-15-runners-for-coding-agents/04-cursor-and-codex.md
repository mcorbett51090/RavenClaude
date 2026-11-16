# 04: Cursor and Codex

Retrieved 2026-11-16. The cloud modes described below run on the vendor's machines. Pointing either product at the box is a separate mechanism, and that process should not share the Actions OS user.

## Cursor cloud agents

[Cloud agents](https://cursor.com/docs/cloud-agent) run in isolated VMs Cursor operates. The environment is a clone plus dependencies, from a snapshot or from `.cursor/environment.json`. The page does not describe them as GitHub Actions runners. A pull request they open is an ordinary pull request: Website CI runs on our runners, under our labels and the name guard.

[Automations](https://cursor.com/docs/cloud-agent/automations) start those agents from GitHub events. Two of them replace a job that polls:

| Trigger | What the page says it matches | What the page says it does not match |
|---|---|---|
| CI completed | A GitHub check on a pull request or branch | — |
| Workflow run completed | An Actions run started by `push` | Runs started by `pull_request`, `workflow_dispatch`, or `schedule`. The page says to use CI completed for pull-request checks |

That automation does not occupy one of our runners while it waits. A workflow job that loops on `gh pr checks` does. Do not add a polling job.

## Cursor CLI inside Actions

[GitHub Actions for the CLI](https://cursor.com/docs/cli/github-actions) installs the CLI and runs `agent` with `CURSOR_API_KEY`. That job holds a runner for the whole session and needs outbound HTTPS to Cursor. The page shows a full-autonomy example that commits and comments, and a restricted example that leaves pushes to a later step. Use the restricted shape. The key is a secret: same placement as the Claude OAuth token, on the long job, `host-box` only.

The Website code search on 2026-11-16 found no Codex action file and no Copilot setup file. The Claude workflow is the file that names a Cursor automation. The failover automation posts as `cursor[bot]`. That login is an automation identity, not a runner.

## Cursor self-hosted workers

[Self-hosted machines](https://cursor.com/docs/cloud-agent/self-hosted) and [self-hosted pools](https://cursor.com/docs/cloud-agent/self-hosted-pool), as those pages describe them: Cursor runs the loop, inference, and planning. The worker runs terminal commands, file edits, and browser actions. `agent worker start` opens a long-lived outbound HTTPS connection. The machines page says Cursor does not connect into your network, and that the outbound connection is all that is required. No public port.

A pool worker is claimed by one session at a time. The pool page says requests carry a `repo=` label and, for a named pool, `pool=`. `--idle-release-timeout` exits the process after it has been idle.

The pages do not describe this worker as an Actions scale set. It does not pick up `runs-on` jobs, and the name guard does not see it. Starting it as the `ghrunner` user on the box would put agent shell, the shared `~/.claude` install, and CI jobs in one home directory. If a worker is ever used, give it a separate OS user or VM, the same split as the deploy runner in the 2026-11-15 recommendations.

## Codex cloud

[Codex cloud (legacy environments)](https://learn.chatgpt.com/docs/environments/cloud-environment), retrieved 2026-11-16. The page says this legacy path still serves code review and the Linear and GitHub integrations, and points current web, mobile, and desktop use at a newer cloud-environments guide.

What that page states about the container:

- Setup scripts run with internet. During the agent phase, internet is off by default. Limited or unrestricted access is a setting. Traffic that is allowed goes through an HTTP proxy.
- Secrets are available to setup scripts and are removed before the agent phase. Environment variables last for the whole chat.
- Container state is cached for up to 12 hours. Changing the setup script, maintenance script, variables, or secrets invalidates it.
- The page describes an OpenAI container. It does not mention GitHub Actions runners. A pull request opened afterwards is what reaches our CI.

`[verify-at-use]` for the non-legacy cloud guide if a task is started from the current web UI rather than the legacy environment.

## `openai/codex-action`

[Codex GitHub Action](https://learn.chatgpt.com/docs/github-action), retrieved 2026-11-16. Not present in Website (code search, 2026-11-16).

| Input | Default on that page | Why it matters on a shared runner |
|---|---|---|
| `safety-strategy` | `drop-sudo` | Removes `sudo` before Codex runs. Irreversible for the job. The page says to run the action last. Windows cannot use this value; the only Windows value is `unsafe` |
| `sandbox` | unset; the page says `workspace-write` when neither this nor a permission profile is set | Narrowest mode that still completes the task. The page says `read-only` does not protect secrets, because hosted runners have passwordless sudo and a privileged reader can see process memory |
| `allow-users` / `allow-bots` | empty | Empty means only users with write access |
| `openai-api-key` | empty | The proxy holds the key. The job that has the key should have `contents: read` only |

The documented shape is two jobs. The Codex job checks out with `persist-credentials: false`, holds the key, and emits `final-message`. A second job, with no key, has `issues: write` and `pull-requests: write` and posts the comment. Do not put the key and a write token in the same job.

The security checklist on that page: sanitize prompt text from pull requests and issue bodies, do not use `unsafe` on a multi-tenant runner, rotate the key if proxy logs leak it.

If Codex is instead assigned as a third-party agent inside GitHub's Copilot cloud-agent UI, it follows that product's runner and firewall rules, including the extra npm hosts in [02](02-copilot-actions-path.md). That path is not `openai/codex-action`.

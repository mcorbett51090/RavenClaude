# 03 — Agent or runner

Checked 2026-11-16. A runner executes a command and returns its exit code. A coding agent reads the tree, decides what to run, and writes prose. The exit code and the prose are different evidence. The merge gate should follow the exit code.

## The decision

| Question | Use a runner | Use a coding agent |
|---|---|---|
| The result is a merge gate | Yes. The job exit code is the check. | The model’s summary is a report for a person. A program posts the status from exit codes. |
| The command is already written and deterministic | Yes. | The agent adds a chance of a skipped step and a slower start. |
| The job needs a browser, a secret, or a production token | Yes, on the lane allowed to hold that secret. | Keep that secret out of the agent VM. |
| You need a machine of a known size, on a queue you control | Yes. | The agent VM is sized by the vendor. The account can be busy or out of usage. |
| A red log needs a sentence and a proposed patch | The runner already produced the log. | Yes. The patch lands on a branch. The runner checks the new SHA. |
| You are classifying a flake from a log you already have | The runner’s job is finished. | Yes, as a reader of the log. The classification does not override the exit code. |
| The wait budget is about a minute | A warm runner. | An agent start is minutes, plus a poll, plus a hold when the account is out of usage. |
| The input includes the pull request diff or a repository file | The script treats it as data. | Those files can contain instructions. See [04](04-agent-checks-that-count.md). |

Give the agent the red log. Keep the green paint on a program that reads exit codes.

## What each product posts

**GitHub Actions** posts a check run as the `github-actions` app. This session read `GET /apps/github-actions` and got id **15368**, slug `github-actions`. The conclusion follows the job’s exit. That is the object a ruleset should require for anything a script can decide.

**Copilot coding agent** runs in a GitHub Actions appliance and opens a pull request. The firewall how-to, retrieved 2026-11-16 from [Customizing or disabling the firewall for GitHub Copilot cloud agent](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-firewall), says the firewall applies to processes the agent starts through its shell tool, and then lists the limits in its own words: MCP servers and Copilot setup steps are outside it, it operates inside the Actions appliance, and sophisticated attacks may bypass it. The setup-steps page says self-hosted runners require the firewall to be disabled in the repository settings, and that use of the agent is blocked until then. This session did not run an agent against that firewall. The page is the source. Workflows on the agent’s pull request can sit at "Approve and run" until a person with write access approves them. A `workflow_dispatch` started from the agent does not satisfy a required check on the pull request (troubleshooting page, same date). The agent’s pull request still needs the same required checks as a person’s. The firewall is a network limit on the appliance, documented with the limits above. It is not the merge rule.

**Claude Code’s GitHub Action** runs as a job in Actions, so the job’s conclusion is an Actions check and can be pinned to app 15368. That is safe when the conclusion is the script’s exit code. It is unsafe when the job exits 0 because the model said the tests passed: the ruleset then trusts the app name and the model together. The cloud-provider how-to (Bedrock, Vertex, Foundry), retrieved 2026-11-16, changes where inference runs and how the workflow gets a cloud credential from OIDC. It does not change which app is allowed to report the check. A workflow that wakes because a comment contains an at-mention is taking the comment as an instruction. Keep that job’s token at contents: read, and keep it off the required-status writer.

**Cursor cloud agents** run in a VM with the repository, a startup environment, and the secrets and network policy the account set ([Cloud Agents](https://cursor.com/docs/cloud-agent), retrieved 2026-11-16). The API can start one on a given SHA. The factory bridge’s own note says the API it calls has no completion webhook, so a cron polls. The VM is a reasonable place to run a suite when runners are busy, if a program other than the model posts the status, and if the VM’s credential cannot write commit statuses. Restrict outbound domains. Keep the status-writing key in the worker, not in the VM.

## A split that stays honest

1. A runner, or a fixed script inside the agent VM, runs the named commands.
2. A program reads the exit codes and the SHA, and posts the status with an App credential the agent does not hold.
3. The agent writes the explanation and, when asked, a fix on a branch.
4. The fix is a new SHA. The runner checks it. The earlier pass does not carry over.

Triage, flake classification, and "why did this job fail" are agent work. "Is this SHA allowed to merge" is a program reading an exit code.

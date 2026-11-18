# 06: Recommendations for this factory

The 2026-11-15 list (L1–L7 in the Website guide) still stands. This page adds the agent-specific rules and the live changes that follow from them. Nothing here has been applied to Website.

Constraints that are not up for revision:

- The name-guard regex stays `^box-((fast|large|web)[0-9]+|raven-(web|light)-[0-9]+)$`. It is not widened.
- Lanes in use: `lane-fast`, `lane-medium`, `lane-slow`, `host-box`, `host-yoga`.
- RavenClaude (public) does not get self-hosted agent jobs.
- The box stays persistent until the ephemeral loop has been proven on a new host (2026-11-15 R5). Agent jobs live with that constraint, they do not overturn it.

## Rules

1. **Copilot sessions stay on the Cloud sandbox** unless the task needs the private network. Do not add `copilot-setup-steps.yml` just to put Copilot on the box. If a task truly needs Actions: Ubuntu x64 only, ephemeral registration, integrated firewall off, host firewall on, and a label set no other workflow uses. Do not register the box with `--environment-host`. That shell would bypass Actions entirely.
2. **Claude jobs require `host-box` and `lane-medium`.** Not `lane-fast`, not `lane-slow`, not a label the Yoga carries. The 90-minute timeout and the shared home directory are box facts.
3. **Cap concurrent Claude jobs with a label, not with a second concurrency group.** Add `lane-agent` to exactly two box runners that already have `lane-medium` and `host-box`. Point the long job at `["self-hosted","lane-medium","host-box","lane-agent"]`. CI that targets `lane-medium` can still use those two runners when no agent job is queued. A third agent job waits. Names stay `box-raven-web-N`. The regex does not change.
4. **The authorize job does not take a `lane-agent` slot.** It has no model secret. It can use `lane-fast`. It must not fall back to bare `self-hosted`.
5. **Do not cancel an in-progress Claude job.** Keep `cancel-in-progress: false` on that job. Do cancel superseded test matrices.
6. **Leave Copilot's workflow-approval switch on.** Claude app pushes should keep starting CI. Those are different switches.
7. **No Cursor worker and no Codex action on the `ghrunner` user.** Cursor cloud agents and Codex cloud are fine: they do not sit on the box. A worker or `openai/codex-action` needs its own OS user, and the Codex job that holds the API key must not also hold a write token.
8. **Model credentials never land on the Yoga or the secrets runner.** The fallback `["self-hosted"]` is how they would.

## Live changes for Website (each needs a GO)

| # | Change | Exact action | Rollback |
|---|---|---|---|
| G1 | Pin Claude to the box | Set `CLAUDE_RUNS_ON` to `["self-hosted","lane-medium","host-box"]`. Confirm the Yoga runners do not have both `lane-medium` and `host-box`. Save the old value first | Restore the saved value |
| G2 | Remove the bare fallback | In `.github/workflows/claude.yml`, change the `runs-on` fallback from `["self-hosted"]` to the same pinned array, on both jobs. An unset variable then still cannot match the secrets runner | Revert that commit |
| G3 | Two agent slots | Add the label `lane-agent` to exactly two box runners that already have `lane-medium` and `host-box` (`POST /repos/mcorbett51090/RavenPower-Website/actions/runners/{id}/labels`). After G1 has been checked, set `CLAUDE_RUNS_ON` to `["self-hosted","lane-medium","host-box","lane-agent"]` for the long job only. Leave the authorize job on `["self-hosted","lane-fast"]` so a 2-minute permission check does not consume an agent slot | `DELETE` the label; point the variable back at G1 |
| G4 | Stop stacked test matrices | Add a concurrency block to `commerce-ci.yml` (the file has no `concurrency` key on the default branch). Group by workflow plus ref. `cancel-in-progress` true only for `pull_request`. Do not cancel `push` to the default branch | Revert that commit |
| G5 | Do not auto-run Copilot workflows | Confirm the repository setting "Require approval for workflow runs" for Copilot is still on. Do not disable it | Turn it back on |
| G6 | No Copilot-on-Actions until G1–G3 are in | Do not merge a `copilot-setup-steps.yml` that targets `lane-medium` or `raven-web`. If one is proposed later, its `runs-on` is a dedicated ephemeral x64 label, the firewall exception is documented, and the runner name is one the existing regex refuses, so a misrouted CI job fails closed | Delete the file |

G1 is the one to do first. G3 without G1 leaves the old variable matching the Yoga whenever the Yoga still carries `box` and `raven-web`. G2 is a one-line safety net and can ship with G1. G4 is independent and is the storm control for Claude app pushes. G5 is a check, not an edit, unless the setting has been turned off.

## What not to do

- Do not add `agent` to the name-guard alternation. `lane-agent` is a label. Runner names stay on the current regex.
- Do not give the Yoga `lane-medium`, `lane-slow`, or `lane-agent`.
- Do not put the Mac mini's arm64 VM on `CLAUDE_RUNS_ON` until the `gh` install step is not hardcoded to `linux_amd64`. Copilot on Actions still could not use it.
- Do not set `queue: max` on the Claude workflow.
- Do not install ARC or gVisor on the box as part of this change.

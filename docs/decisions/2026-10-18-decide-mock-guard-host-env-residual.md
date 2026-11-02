# Decision record: the decide mock guard's host-environment residual

**Date:** 2026-10-18 · **Owner:** Matt (asked the agent to pick a recommendation and act on it) ·
**Decision:** accept the residual and record it here. No code change.

**Source:** the security review of [#1377](https://github.com/mcorbett51090/RavenClaude/pull/1377)
(CLEAR-WITH-NITS), whose one medium finding was left unfixed by design.

## The finding

`thing-decide.py` honours its test hooks (`THING_DECIDE_MOCK_VERDICT`, `THING_DECIDE_MOCK_EVAL`) only
when three things hold (`_mock_gate`, `plugins/ravenclaude-core/scripts/thing-decide.py:288`):

1. the harness marker `THING_DECIDE_ALLOW_MOCK=1` is set;
2. no project-scope Claude settings file (`settings.json` / `settings.local.json`, in the project,
   `--root` and every parent up to the git top level) plants a `THING_DECIDE_*` key;
3. in a live session, the mock produces only a defer.

A live session is detected from `CLAUDECODE` or `THING_DECIDE_LIVE_SESSION=1`
(`thing-decide.py:296`). On a host other than Claude Code, a caller that runs `thing-decide.py`
directly sets neither. If something outside the project's Claude settings files has put the marker and
a `yes` mock into that environment, the mock can still produce a binding `yes`.

## Who can reach it

| Route to the engine | Host | Reaches the residual? |
|---|---|---|
| `route-decision-review.sh` (the `AskUserQuestion` hook) | Claude Code only | No. Claude Code sets `CLAUDECODE`, and the hook sets `THING_DECIDE_LIVE_SESSION=1` when its payload has `transcript_path`. The Codex, Copilot, Cursor and Gemini projectors all skip this hook (`scripts/generate-*-hooks.py`). |
| The `decision-review` skill, run by an agent from a shell | Codex, Copilot, Cursor, Gemini | Only if the host's own environment already carries the marker and the mock. |

Putting those two variables into a non-Claude host's environment needs the host's own environment
injection for a trusted project, such as a Codex `shell_environment_policy`. That access can also set
`PYTHONPATH` or `PATH`, which runs arbitrary code inside the engine or replaces `python3`. An attacker
with it does not need the mock.

## Why no code change

- **No fix raises the bar.** A `--allow-mock` flag, a second marker, or a check that the parent
  process is a test harness can all be set or faked by whoever controls the environment. So can
  `PYTHONPATH`.
- **The cost is not small.** A heuristic such as "treat every non-harness caller as live" would break
  the harness callers that exercise binding verdicts (Gates 17 and 31) unless they opt out, and that
  opt-out would itself be an environment variable.
- **The realistic plant is already closed.** A cloned repo's `.claude/settings.json` `env` block, which
  needs no code execution, is screened by condition 2.

## Reopen this if any of these happens

- A host gains a repo-controlled way to set environment variables that does **not** also allow
  `PYTHONPATH` or `PATH`, for example a named allow-list of variables loaded from an untrusted
  project. The residual would then be reachable without code execution.
- `route-decision-review.sh` is wired on a non-Claude host. That host's adapter or shim must then
  export `THING_DECIDE_LIVE_SESSION=1`, as Claude Code's path already does.
- A new caller of `thing-decide.py` runs in an unattended context (a Routine or CI) where a binding
  `yes` acts without a human. That caller must set the live-session signal itself.

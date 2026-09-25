---
name: routine-reserve
description: "Set up, inspect, override, or remove the routine token reserve — an hourly meter Routine records what your claude.ai Routines cost, and a projected reserve of the weekly usage cap is held back for them so non-stop interactive work never starves them. Use for '/routine-reserve setup|status|override|clear-override|uninstall', 'keep enough tokens for my routines', or 'how much of my weekly cap do my routines need'."
---

# Routine token reserve

Lets a user run Claude non-stop without starving their scheduled claude.ai Routines. An hourly
**meter Routine** records each Routine run's cost; the engine projects how much of the weekly cap
the Routines still need before the weekly reset (remaining firings × recent-weighted cost ×
safety margin); that **reserve** shrinks as the week runs down. The user sees it, can override it
for the current week, and is warned when their own usage crosses into it.

Engine: `${CLAUDE_PLUGIN_ROOT}/scripts/routine-reserve.py` (run it with `python3`). Mechanism,
verified data sources and honest limits: [`../../knowledge/routine-token-reserve.md`](../../knowledge/routine-token-reserve.md).

## Verbs

| Verb | What it does |
|---|---|
| `setup` | One-time wiring, below. Every outward step is confirmed with the user first. |
| `status` | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/routine-reserve.py refresh`, then `… status`. Show the output as-is. |
| `override <pct>` | `… set-override <pct>` — holds exactly `<pct>`% until the current weekly reset, then reverts to the projection. |
| `clear-override` | `… clear-override`. |
| `uninstall` | Delete the meter Routine, restore the previous statusline, set the knob to `off`. Leave the data branch in place and name it. |

## Requirements (say which are missing; never guess past one)

- Claude Code with the claude.ai Remote tools (`list_triggers`, `create_trigger`, …). Load them with
  ToolSearch before concluding they are absent. Without them, print the manual steps in § Manual fallback.
- A **private** GitHub repo to hold the data (the "home repo"), with the Claude GitHub App installed on it.
- Pro/Max for the automatic weekly percentage. Other plans can set `routine_reserve_weekly_budget_usd`.

## Setup

1. **Home repo.** Ask for `owner/repo`; suggest `<owner>/ravenclaude-usage`. Check it is private
   (`gh api repos/<owner/repo> --jq .private`, or the GitHub MCP tools). **Refuse a public repo**
   unless the user explicitly says to allow it: the samples are account telemetry. If it does not
   exist:
   - local session with `gh` authed → offer `gh repo create <owner/repo> --private`;
   - cloud session → repo creation is not available there (the session proxy only allows
     repository-scoped API calls). Ask the user to create it at github.com/new as **private** and to
     add it to the Claude GitHub App at claude.ai/connect-github; then attach it with `add_repo` (push).
2. **Data branch.** In a scratch clone of the home repo, create the orphan branch
   `ravenclaude/usage-meter` (orphan on purpose: it shares no history with any other branch, so it can
   never be merged or opened as a PR). Put in it: `routine-reserve.py` (copied from the plugin),
   `README.md` from `${CLAUDE_PLUGIN_ROOT}/templates/routine-reserve/data-branch-README.md`, and an
   empty `samples/.keep`. Commit `chore(usage-meter): initialize data branch [skip ci]` and push. If the
   branch exists, replace `routine-reserve.py` only when it differs, commit
   `chore(usage-meter): update engine [skip ci]`.
3. **Pin the engine.** `sha256sum routine-reserve.py` as committed. The meter refuses to run anything else.
4. **Render the prompt.** Take `${CLAUDE_PLUGIN_ROOT}/templates/routine-reserve/meter-prompt.md`, keep
   only the text after `--- PROMPT ---`, replace `{{HOME_REPO}}` and `{{ENGINE_SHA256}}`.
5. **Create or update the meter Routine** (idempotent by name `RavenClaude usage meter`):
   `list_triggers` → if found, `update_trigger` with the new prompt; else `create_trigger` with
   `cron_expression: "0 * * * *"`, `create_new_session_on_fire: true`, `notifications: {}`,
   `initiation: human_request`, and an `environment_id` from `list_environments` whose sessions can
   reach the home repo (ask the user if more than one could).
6. **Model — its own explicit question.** `create_trigger` has no model setting, so the meter runs on
   the caller's model until changed. Ask: "Run the meter on Haiku to keep it cheap?" Only on a yes,
   `update_trigger model: <haiku model id>`, then `get_trigger` to confirm it applied. If it did not,
   say so and offer to delete the meter rather than leave a frontier-model Routine firing hourly.
7. **Prove it once.** `fire_trigger`, wait a few minutes, `… pull`, and check that
   `~/.ravenclaude/usage/mirror/samples/` holds a new file whose meter record shows an `attended`
   value. Report that value — it is how the guard tells unattended sessions apart.
8. **Statusline (asks first).** A plugin cannot set the main `statusLine`, so copy the engine to
   `~/.ravenclaude/bin/routine-reserve.py` and set `statusLine.command` in `~/.claude/settings.json` to
   `python3 ~/.ravenclaude/bin/routine-reserve.py ingest-statusline --wrap '<their existing command>'`
   (omit `--wrap` when there is none). Save the previous `statusLine` to
   `~/.ravenclaude/usage/statusline-previous.json` so `uninstall` can restore it.
9. **Config.** Write `~/.ravenclaude/usage/config.json` `{"home": "<owner/repo>"}` and set
   `routine_reserve: advise` in this repo's `.ravenclaude/comfort-posture.yaml`.
10. Finish with `status`.

## Manual fallback

When the Remote tools are unavailable where setup runs, print: the rendered prompt, the schedule
(`0 * * * *`, a new session per firing, notifications off), and ask the user to create the Routine at
claude.ai with Haiku selected. Steps 1–3 and 8–9 still run locally.

## Honest limits

- Only claude.ai **cloud** Routines are counted. Event-triggered Routines, Cowork local tasks and
  `CronCreate` jobs are listed as "not counted".
- The weekly percentage is live only while a Claude Code statusline is rendering (Pro/Max). Elsewhere
  the reserve is marked *estimated*.
- The %-per-dollar calibration uses metered spend, deliberately biased low (the safe direction: a
  larger reserve). Local sessions on other machines are not metered.

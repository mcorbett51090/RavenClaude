# Routine token reserve — keep enough weekly cap for your Routines

**Last verified:** 2026-09-24 (Claude Code 2.1.281, a claude.ai cloud session). **Refresh when:** a
Claude Code release changes the statusline `rate_limits` shape, the Remote tools' `list_triggers` /
`get_session` output, or how `PreToolUse` `ask` behaves in headless sessions.

**What it is for.** You want to run Claude non-stop — loops, workflows, background agents — up to a
point, while your scheduled claude.ai Routines still have enough of the weekly usage cap to run. The
routine token reserve projects how much of the cap the Routines still need before the weekly reset,
shows it, lets you override it for the current week, and warns when your own use crosses into it.

Wire it with `/routine-reserve setup`. Engine: [`../scripts/routine-reserve.py`](../scripts/routine-reserve.py).
Skill: [`../skills/routine-reserve/SKILL.md`](../skills/routine-reserve/SKILL.md). Gate: 291.

## The mechanism

```
 cloud, hourly                                        your machine / session
 meter Routine ──[chore(usage-meter): sample [skip ci]]──▶ private home repo
   list_triggers, get_session (≤25/firing),                branch ravenclaude/usage-meter
   list_sessions → raw JSON → checksum-pinned engine          │ fetched in the background at SessionStart
                                                               ▼
 statusline shim ──▶ ~/.ravenclaude/usage/rate-limits.json  +  mirror/samples/
                     routine-reserve.py compute ──▶ ~/.ravenclaude/usage/reserve.json ──▶ warnings, status
```

- **Reserve** = Σ over active Routines of *remaining firings before the reset* × *recent-weighted
  cost per run* × (1 + margin). It shrinks as the week runs down and reaches zero at the reset.
- **Cost per run** — a 28-day average weighted by recency (half-life 7 days). A run counts once it
  has settled (its session idle for an hour). Runs are keyed by (Routine, fire time); a Routine that
  reuses one persistent session is costed by the growth between runs, not the session total.
- **Cold start** — under 3 measured runs, a Routine's cost blends its own runs with the median run
  across all Routines (never the most expensive one), and is flagged *estimated*.
- **Override** — `/routine-reserve override <pct>` holds exactly that share until the current reset.
- **States** — `ok`, `warn` (within `routine_reserve_warn_points` of the line), `over`, `infeasible`
  (the Routines alone need more than what is left; warn only), `unknown` (no reading or no calibration).

State is **account-scoped** (Routines belong to the account, not to a repo), so it lives in
`~/.ravenclaude/usage/`, readable from every repo — not in `.ravenclaude/runs/`.

## Where each number comes from (observed 2026-09-24)

| Number | Source | Observation |
|---|---|---|
| Routine schedules, last run | Remote MCP `list_triggers` | cron / `run_once_at`, `next_run_at`, `last_run.{session_id, fired_at, finished_at}`. **Last run only; no cost.** |
| Cost of a run | Remote MCP `get_session` on the run's session | `external_metadata.usage.{input,output,cache_read,cache_write}_tokens` and `cost_usd`. Cost kept growing 31 min after `finished_at` on one run. |
| Run history | the meter, accumulated | `list_sessions` excludes trigger-fired runs, so history exists only because the meter records it. |
| Weekly-cap position | statusline stdin | `rate_limits.seven_day.{used_percentage, resets_at}` — Pro/Max only, absent until the first API response ([statusline docs](https://code.claude.com/docs/en/statusline)). **No hook input carries it.** |
| %-of-cap per dollar | calibrated | weekly `%` ÷ metered spend in the window; or `routine_reserve_weekly_budget_usd`. |

Only an agent can call the Remote tools, which is why the collector is itself a Routine. A plugin
cannot set the main `statusLine` and `${CLAUDE_PLUGIN_ROOT}` does not expand there
([plugins reference](https://code.claude.com/docs/en/plugins-reference)), so setup installs a
self-contained copy of the engine at `~/.ravenclaude/bin/` and wraps any statusline you already have.

## On the dashboard

The **Reserve** tab (`#/reserve`, under Activity) shows the same numbers as `/routine-reserve status`:
the weekly percentage with its source and age, the effective reserve and the line, the per-Routine table
(runs left, average cost, estimated flag) and anything *not counted*. It needs the served dashboard
(`bin/rc dashboard`); a static copy shows an explanation instead.

- `GET /__reserve` computes the projection **in memory** from the files above and never writes
  `reserve.json` or `calibration.json` — viewing the tab cannot move the numbers the hooks read.
- `POST /__reserve-override` takes `{"action": "set", "pct": 0-100}` or `{"action": "clear"}`, and
  requires the dashboard's CSRF token and a same-origin request like every other write. A value that
  is not a real number in range is rejected (400); setting an override without a live weekly reading
  is refused (409), because an override expires at the reset and there is no reset to expire at.
- Both endpoints call the engine's own `set_override` / `clear_override`, so the command and the tab
  cannot drift apart.

## Safety properties

- **The error runs in the safe direction.** Spend is only counted where it is known (a session first
  seen mid-week contributes only its growth after that); under-counting raises the %-per-dollar rate
  and so *enlarges* the reserve. Local sessions on other machines are not metered at all — same direction.
- **Private data, allow-listed fields.** A sample holds Routine ids, names, schedules, run times,
  tokens, `cost_usd`, model and the meter's attended flag. Never prompts, session titles, repo URLs or
  branches, connectors or environment ids. Setup refuses a public home repo.
- **The meter runs only the pinned engine.** Setup commits the engine to the data branch and pins its
  sha256 in the meter's prompt; the meter refuses to run on a mismatch, so a collaborator editing the
  branch cannot run code over your account's raw session data.
- **No PR storms.** The data branch is an orphan (no shared history), commits carry `[skip ci]`, and
  the meter's prompt forbids opening a PR — a cloud session's default is to open one after a push.
- **Never stalls a Routine.** In a headless session a `PreToolUse` `ask` is a denial (observed below),
  so nothing here asks in an unattended session.

## Observed behaviour this design rests on

- `claude -p` with a `PreToolUse` hook matching `*`: the hook fired for `Bash`, `ToolSearch` and the
  deferred `CronList`; returning `permissionDecision: "ask"` **denied** the call, and the model
  received the hook's reason as the denial text.
- In that nested `claude -p`, `CLAUDE_CODE_SESSION_ATTENDED` was `0` while the parent shell saw `1` —
  the flag is set per Claude process, not inherited. `CLAUDE_CODE_ENTRYPOINT` *was* inherited.
- The meter records its own `attended` value on every firing, so the value inside a real Routine run
  is measured rather than assumed.
- Creating a GitHub repository is not available from a claude.ai cloud session: the GitHub App token
  lacks it (403) and the session proxy allows only repository-scoped API paths. Setup asks the user to
  create the private home repo there.

## Honest limits

| Limit | Effect |
|---|---|
| Only claude.ai **cloud** Routines are counted | Event-triggered Routines, Cowork local tasks and `CronCreate` jobs appear as "not counted". |
| The weekly % is live only where a Claude Code statusline renders | Cloud and headless sessions see the last reading; the reserve is marked *estimated* there. |
| The meter costs tokens too | It is one of your Routines, so it reserves its own share. Setup offers to run it on Haiku. |
| Whether the weekly window is fixed or rolling | Recorded in `rate-limits-history.jsonl` as `resets_at` changes; not yet characterised. |
| Hosts other than Claude Code | The hooks are explicitly skipped for Copilot, Codex and Gemini — no Routines or statusline data there. |

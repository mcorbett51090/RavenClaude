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
  is refused (409), because an override expires at the reset and there is no reset to expire at. A
  failed write of `override.json` (disk full, permissions) is also 409 — never reported as saved.
- Both endpoints call the engine's own `set_override` / `clear_override`, so the command and the tab
  cannot drift apart.

## Guard mode

`routine_reserve: guard` keeps everything `advise` does and adds a `PreToolUse` check on autonomous
work: `Workflow`, `ScheduleWakeup`, `CronCreate`, a background `Agent` (the default; an explicit
`run_in_background: false` is not guarded), and a Remote MCP call that starts or feeds a session or
Routine (`create_session`, `send_message`, `fire_trigger`, `create_trigger`).

| Situation | What it does |
|---|---|
| State `over`, a live statusline reading, an attended interactive session, not a subagent | **Asks** before the call. Approving allows autonomous work for the rest of that session this week. |
| The same, while that ask is pending or was just declined (90 s) | **Denies** with the reason, so parallel calls raise one ask, not several. |
| State `warn` or `infeasible`; or headless (`CLAUDE_CODE_SESSION_ATTENDED` ≠ 1), an SDK/Actions entrypoint, a subagent's own call, or an estimated reading | **Warns** once per band, never asks. |
| State `ok` or `unknown`, or any other tool | Silent. |

**Consent is recorded only after the asked call actually ran.** A `PreToolUse` hook cannot see the
answer to its own ask, so the `PostToolUse` half records consent when the guarded tool runs; a
declined ask never reaches `PostToolUse`. When the ask recorded a `tool_use_id`, only a
`PostToolUse` with that same id grants consent — a missing or empty id does not match a concrete
pending id. Consent is per session and per week: a new weekly reset asks again.

**Escape.** Move the line with `/routine-reserve override <pct>` (or the dashboard Reserve tab), or set
`routine_reserve: advise`. The guard state lives in `~/.ravenclaude/usage/guard/<session>.json`.

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

## Diagnosing a silent meter (added 2026-10-12)

A Routine run reports **SUCCEEDED whenever its session ends normally** — the meter's old
"stop and report the failing step in one line" produced exactly that, so a clone/commit/push
failure was invisible: the run went green and no sample landed. Observed on probes 4 and 5
(trigger `trig_01PD9CQj6ix9uiEac49mx2AF`): both fired, reported SUCCEEDED, and left the data
branch at `72a7d14` with no sample. **Which step failed is UNVERIFIED** — probe 5's session
(`session_012den9amp13KVyHyqsQKV2q`) last line was never captured; an unsent draft said only
"the clone failed." The fixes below do not depend on knowing the exact step.

- **The meter now fails loudly.** Every Bash step in [`../templates/routine-reserve/meter-prompt.md`](../templates/routine-reserve/meter-prompt.md)
  prints a single final line `METER FAILED: <step> — <reason>` and exits non-zero on failure;
  success prints `METER OK: recorded <file>`. Step 7 forwards that line verbatim, so a reader
  can tell a landed sample from a silent clone/commit/push failure even though the Routine
  status is SUCCEEDED either way.
- **The clone cause (CONFIRMED from repo evidence).** A fresh meter session starts with no
  repos attached (`sources: []`, observed), so there is no `127.0.0.1` git-proxy `origin`;
  the URL derivation then falls back to a direct `https://github.com/<repo>.git`, which a
  cloud session's proxy cannot reach. The prompt's `add_repo(push)` + one retry is the fix,
  and a `METER FAILED: clone` whose URL is a bare github.com URL is the tell that the home
  repo was never attached.
- **Staleness check.** `python3 routine-reserve.py check-staleness [--dir D] [--max-age-hours N]`
  (default 3 h — one skipped hourly firing) exits non-zero and prints `STALE:` when the newest
  sample is older than the window, or when no sample exists at all — so a scheduled or manual
  check catches a dead meter the Routine status hides.
- **Allow-list verifier.** `python3 routine-reserve.py check-sample [PATH|--dir D]` exits
  non-zero and names any field outside `SAMPLE_ALLOWED_KEYS[kind]` — the read-side complement
  to `meter_records` dropping unlisted fields at write time.

## Honest limits

| Limit | Effect |
|---|---|
| Only claude.ai **cloud** Routines are counted | Event-triggered Routines, Cowork local tasks and `CronCreate` jobs appear as "not counted". |
| The weekly % is live only where a Claude Code statusline renders | Cloud and headless sessions see the last reading; the reserve is marked *estimated* there. |
| The meter costs tokens too | It is one of your Routines, so it reserves its own share. Setup offers to run it on Haiku. |
| Whether the weekly window is fixed or rolling | Recorded in `rate-limits-history.jsonl` as `resets_at` changes; not yet characterised. |
| Hosts other than Claude Code | The hooks are explicitly skipped for Copilot, Codex and Gemini — no Routines or statusline data there. |

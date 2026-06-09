# Run-state monitor — reactive guardrail/run-state notifications

> Component: `monitors/` (a NEW plugin component type for `ravenclaude-core`, added v0.132.0, FORGE roadmap #7).
> Files: [`monitors/monitors.json`](../monitors/monitors.json) + [`monitors/watch-run-state.sh`](../monitors/watch-run-state.sh).

## What it is

The **push** complement to the read-only Heimdall / Víðarr / Norns dashboard tabs. Those tabs are **pull** surfaces — the agent (or user) opens one and reads what already happened. The run-state monitor **streams** the same guardrail/run-state signals to Claude Code as **native notifications**, so the agent reacts to a deny/warn *as it lands* during a multi-agent run, without anyone asking it to go look.

It reads the same substrate the readers read: the per-session hook-event log [`hooks/_emit-event.sh`](../hooks/_emit-event.sh) writes to
`${CLAUDE_PROJECT_DIR}/.ravenclaude/runs/${CLAUDE_SESSION_ID}/hook-events.jsonl`.

## How a Claude Code monitor works (verified against the docs)

Verified against [code.claude.com/docs/en/plugins-reference](https://code.claude.com/docs/en/plugins-reference) § Monitors (retrieved 2026-06-08):

- A plugin monitor is declared as a **JSON array** in `monitors/monitors.json` (or inline / by-path via `experimental.monitors` in `plugin.json`). We use `experimental.monitors: "./monitors/monitors.json"` — the forward-compatible declaration the docs recommend (the bare top-level `monitors` key still works but `claude plugin validate` warns and a future release will require `experimental.*`).
- Each entry has **`name`** (unique within the plugin — prevents duplicate processes on reload/re-invoke), **`command`** (run as a persistent background process in the session working directory), **`description`** (required — shown in the task panel and in notification summaries), and an optional **`when`**.
- `when` is `"always"` (default — start at session start / reload) or `"on-skill-invoke:<skill-name>"` (start the first time that skill in this plugin is dispatched). **We scope to `on-skill-invoke:spawn-team`** — NOT `always` — so the watcher only runs during multi-agent runs, where guardrails matter most. This is the **cost bound**: ordinary single-agent sessions never start it.
- **Every stdout line of the command becomes a Claude notification.** That is why the emit surface is also an **injection surface** (see Safety below).
- Monitors are **Claude-Code-only** (v2.1.105+), run only in interactive CLI sessions, run unsandboxed at the same trust level as hooks, and are skipped on hosts where the Monitor tool is unavailable.

> Note vs. plan.md #7: the plan assumed `name` / `command` / `when`. The docs add a **required `description`** field, and the forward-compatible declaration is `experimental.monitors`. We followed the docs.

## The three invariants (from the red-team monitor notes)

1. **`when: on-skill-invoke:spawn-team`, never `when: always`.** Bounds cost — the watcher is a no-op except during a spawned multi-agent run.
2. **Read-only.** The watcher only `tail`s and summarizes. It writes nothing to the substrate, mutates no run state, runs no tool. A pure reader, like Heimdall.
3. **Derived labels only — never raw event content.** For each new JSONL line the watcher emits ONE line built from the **whitelisted** fields `verdict` / `hook` / `tool` / `rule` only. It NEVER echoes the `path` field (a file path or the raw command string), the timestamp, the session id, or any free-form content. This mirrors the capability-banner injection-safety rule: a hostile path/command captured in a deny event must not flow back into the session as text a downstream model could read as instructions. Each field is also stripped of CR/LF so one event is always exactly one notification line.

Example emitted line:

```
⚠ guard-destructive.sh denied Bash (rule: destructive-pattern)
```

## Fail-safe behavior (the `tail -F` empty-glob fragility, handled)

- **No `.ravenclaude/runs/` dir yet** → sleep and re-poll; never crash.
- **`runs/` exists but no `hook-events.jsonl`** → sleep and re-poll for one.
- **The active log rotates** (a newer run dir appears) → re-resolve the newest log and follow that.

The watcher deliberately does **NOT** `tail -F <glob>`: a bare glob matching nothing makes `tail -F` exit immediately, and the monitor host would crash-loop restarting it (a notification-spam / cost problem). Instead it resolves the single newest `hook-events.jsonl` itself, tails that one concrete file (so `tail -F` re-opens on truncate/rotate without exiting on an empty match), and re-resolves when the file disappears or a newer run dir supersedes it. Bounded poll, no busy-spin, no restart storm.

## Claude-Code-only — degrade note for Copilot

Plugin monitors are a Claude Code component; **GitHub Copilot CLI has no monitor equivalent**, so under Copilot this component simply does not load. There is no degraded watcher there — the read-only Heimdall / Víðarr tabs remain the pull surface (the agent consults them at session start via the capability banner's RECENT GUARDRAIL ACTIVITY line). This is the same Claude-only boundary as the OS sandbox: we do not fake a portable push channel where the host can't provide one.

## Supersedes the prior "Monitors — N-A" disposition

The `## Value-add completeness (build-out 2026-06-05)` table in this plugin's CLAUDE.md marked "Monitors / background jobs — N-A" on the grounds that the hook substrate + readers already cover observability. That disposition was about **pull** observability. This component is the **push** complement the pull surfaces structurally can't provide (a dashboard tab can't notify you mid-run). FORGE roadmap #7 is the deliberate, scoped reversal — bounded by `on-skill-invoke` scoping and the read-only / derived-labels-only invariants so it adds the reactive channel without the cost or injection risk the original N-A call was guarding against.

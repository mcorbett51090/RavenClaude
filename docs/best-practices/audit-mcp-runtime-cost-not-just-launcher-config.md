# Audit MCP **runtime** cost, not just launcher config — and check `wchan` before calling a session hung

**Status:** Primary diagnostic

**Domain:** Cross-domain (MCP / agent-host operations)

**Applies to:** Any project where agent sessions spawn MCP servers over stdio (the common case for locally-launched plugin servers — an HTTP/SSE-transport MCP server is out of scope, see Edge cases).

---

## Why this exists

A static launcher audit (grep every `mcpServers` block for a missing `-y` or a floating version tag) answers "which servers *could* block at startup." It cannot answer "what is running right now, and is it too much" — that requires looking at live process state. This matters because MCP's stdio transport wires a server's stdin/stdout directly to one client, so a stdio server cannot be shared between sessions: every concurrent session pays the full cost of its own copy. Sessions also don't reliably tear down their MCP children on exit, so orphaned processes ratchet upward across restarts until the host is oversubscribed — a state whose symptom (a stalled session) looks exactly like the unrelated launcher-blocking failure mode this doc's sibling diagnostic covers.

## How to apply

Check `wchan` first, before assuming a stalled session is an MCP problem at all:

```
ps -eo pid,ppid,stat,wchan:20,rss,args | grep -iE 'mcp|npm exec' | grep -v grep
```

- Idle-healthy states: `ep_poll`, `do_wait`, `futex_wait_queue` — the process is fine; look at machine-wide load and memory next.
- Genuinely blocked states: `pipe_read`, `tty_read`, or process state `D` — this is the sibling launcher-blocking failure mode, not a runtime-cost problem; go audit launcher config instead.

This is a Linux/procfs-specific check (`wchan` via `/proc/<pid>/wchan`); it has no direct equivalent on macOS or Windows hosts.

**Do:**
- Track concurrent-session count, MCP-process count, and total MCP RSS together against the host's core count and free memory — a single number in isolation (just process count, just RSS) hides which resource is actually binding.
- Identify an orphan by process lineage, not by name: its parent is neither a live agent-session process nor another MCP process, meaning its original owner is gone and it has been reparented. In a container, reparenting can land an orphan on PID 1 rather than a recognizable agent-host process — confirm the claimed owner is actually alive (a positive liveness check), don't rely only on "no owner found."
- Run any reaping step as a dry run first, and require an explicit confirmation step before sending a real signal — never fire-and-forget straight from the same command that identified candidates.
- Escalate signals: `SIGTERM` first, and only escalate to `SIGKILL` after confirming the process didn't exit.
- Kill leaves before parents in an orphaned process tree, to avoid an intermediate wrapper re-spawning a child you already reaped.
- Audit what a plugin's server actually spawns at runtime (inspect the live process tree), not what its description claims — a plugin can bundle a heavy dependency (a browser, a runtime) with no hint of that in its name.
- Prefer a pinned, direct launcher invocation over an `npx pkg@latest` chain — the wrapper chain itself (`sh -c npx …` → `npm exec` → the real process) costs resident memory beyond the server's own footprint, on top of the network/hang risk the sibling diagnostic covers.

**Don't:**
- Don't use `pkill`/`killall` to reap orphans. Matching by process name cannot distinguish an orphan from a live session's child with the same name — a name match is not a lineage match. Many hardened environments prohibit these commands outright for exactly this reason.
- Don't pipe the `ps | grep` matcher above directly into a kill command. It is a discovery query; treat its output as a list of candidates for a human or a policy-gated script to confirm, not as a ready target list.
- Don't kill a zombie (state `Z`, 0 RSS). It holds no resources; only its parent can reap it, and signaling it does nothing.
- Don't assume closing a chat tab frees its MCP servers' memory. Verify with a process check — reparenting-without-reaping is the default failure mode, not the exception.
- Don't expect reaping to revive an already-wedged session. A session stuck mid-turn on a starved host will not recover once resources free up; the fix is to close and reopen it, not to wait.

## Edge cases / when the rule does NOT apply

- A **single** blocked launcher (one session, one server stuck at handshake) is the *other* MCP failure mode — a config/pinning problem, not a runtime-cost problem. Don't reach for this doc's process-population audit when the actual symptom is one server never leaving `pipe_read`; that calls for a static launcher audit instead.
- A long-lived, intentionally-persistent MCP server (one meant to run continuously, independent of any single chat session) is not an orphan even if its parent looks unusual — confirm intent before reaping.
- A host with ample spare RAM and cores may simply never hit this symptom regardless of orphan count; the audit is about identifying and bounding the cost, not a claim that any orphan is automatically urgent.
- Reparenting to PID 1 is normal and expected inside a container/cgroup; don't treat PID-1 parentage alone as proof of "orphan" — pair it with the liveness check above. Memory/CPU accounting under a cgroup can also differ from raw host-level `ps` output; cross-check against the container's own accounting (e.g. `docker stats`) before concluding a host is oversubscribed from `ps` alone.
- Immediately after an agent-host restart or extension reload, a brief burst of processes whose apparent "owner" session hasn't fully re-registered yet can look like orphans for a few seconds — confirm the host has settled (a session actually failed to reap, not just hasn't finished starting) before reaping anything in that window.
- Before reaping anything, prefer to quiesce first: confirm the target sessions are actually idle (not mid-turn) rather than reaping opportunistically under load.

## See also

- Lesson: ["An MCP launcher that blocks at session start or plugin reload hangs the host UI: `npx` without `-y` prompts on stdin, which is the MCP transport, so nobody can ever answer"](../memory-bank/lessons-learned.md#2026-09-09--an-mcp-launcher-that-blocks-at-session-start-or-plugin-reload-hangs-the-host-ui-npx-without--y-prompts-on-stdin-which-is-the-mcp-transport-so-nobody-can-ever-answer) (dated 2026-09-09) — the complementary failure: one server blocking at startup, versus this doc's too-many-healthy-servers case.
- Lesson: ["MCP cost is per live session, not per machine, and dead sessions leave orphaned servers behind: the box starves and the symptom looks like a hang"](../memory-bank/lessons-learned.md#2026-09-10--mcp-cost-is-per-live-session-not-per-machine-and-dead-sessions-leave-orphaned-servers-behind-the-box-starves-and-the-symptom-looks-like-a-hang) (dated 2026-09-10) — the diagnosis, story, and measurements behind this rule; this doc keeps the reusable procedure, that entry keeps the numbers.
- [`bundled-mcp-servers.md`](./bundled-mcp-servers.md) — the launcher-config side (pinning, auto-start reality) that this doc's runtime audit complements.

## Provenance

Measured on a consumer-project host: 51 MCP processes, 2.7 GB resident, load average 16.4 on 8 cores. 22 of those processes belonged to sessions that had already ended. One plugin bundling Playwright and a Chromium browser accounted for 78% of total MCP memory despite its name suggesting nothing browser-related. Reaping the confirmed orphans (parent-lineage rule, dry-run first) brought the host to 30 processes / 1.5 GB / load 4.0, verified against a synthetic orphan with zero impact on any live session.

---

_Last reviewed: 2026-09-10 by consumer-project session_

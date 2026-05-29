# Plan — the orchestrator HYBRID (Team Lead as a dispatchable tool, floor stays in-host)

> **Status:** PLAN / SCOPE ONLY (2026-05-29). Awaiting Matt's approval before any build.
> Origin: Matt's question "would a Claude orchestrator that Copilot calls be better?" → an 8-agent
> expert-panel workflow (run 2026-05-29, `wf_3802f995-301`). Verdict: **don't replace; hybrid.**
> This doc turns the panel's recommendation #2 into a concrete, staged plan.

## TL;DR

The panel said **keep the current "port RavenClaude into Copilot" approach** (confidence 0.83) because an
orchestrator that Copilot merely _calls_ cannot gate Copilot's _own_ direct tool calls — moving the
apparatus behind Copilot would silently bypass the deterministic safety floor, which is the whole reason
the Copilot port exists. **But** the panel unanimously endorsed capturing the orchestrator's one real win
— a single, no-porting-glue dispatch engine — as an **optional tool**, not a replacement front-door.

**The hybrid in one sentence:** keep the in-host `.github/hooks` floor exactly as-is (it gates everything
Copilot does), AND expose the RavenClaude Team Lead as **one MCP tool** Copilot may call for heavy
multi-agent fan-out — so delegated work runs the full native apparatus with zero porting glue, while
residual Copilot-native calls are still caught by the floor.

## Why this shape (the decisive constraint)

A `PreToolUse` hook only gates the loop of the agent that executes the tool. Therefore:

| Architecture | Gates Copilot's own Bash/file/net? | Porting glue | Verdict |
| --- | --- | --- | --- |
| CURRENT (port into Copilot) | ✅ yes — hooks are in Copilot's loop | lots (adapter, dual-wire, #2540) | keep |
| ORCHESTRATOR (Copilot calls a Claude back-end, delegates everything) | ❌ no — orchestrator is a callee; can't see Copilot's own calls | little | **rejected** — silently defeats the floor |
| **HYBRID (this plan)** | ✅ yes — floor stays in-host; orchestrator is an _additional_ optional tool | floor unchanged; +1 thin MCP wrapper | **build** |

The hybrid never moves the floor. The orchestrator tool is **additive**: when Copilot delegates into it,
that subtree runs native Claude Code (full hooks/skills/subagents); when Copilot acts on its own, the
in-host hooks gate it. You get clean dispatch where invoked AND the catch-all floor on everything else.

## What the research corrected (don't repeat these in the build)

These were verified against docs during the workflow — fold them in so the build is grounded, not hopeful:

1. **"Free subscription auto-mode comes back" is FALSE.** The Claude Agent SDK requires an API key and
   forbids claude.ai login for third-party agents; from 2026-06-15 SDK usage draws separate metered
   credit. The orchestrator tool's seats/dispatch cost real tokens. `[verify before build — policy may shift]`
2. **The ~24-29s `claude -p` cold-start exists in BOTH worlds** (seats shell to `claude -p` either way),
   so the orchestrator removes no latency and _adds_ a hop + a second context window. `[unverified — benchmark on target host]`
3. **The SDK's "expose tools" server is in-process only** — making the Team Lead callable by Copilot needs
   a bespoke **stdio MCP wrapper**, which is glue comparable to the adapter it would "replace." Budget for it.
4. **MCP long-tool timeout/streaming behavior is undocumented** for a multi-minute tool. A team-lead
   fan-out can run minutes; Copilot's MCP client may silently time out or be unable to stream progress.
   **This is the #1 feasibility risk and must be spiked first (Phase 0).**

## Open questions that GATE the build (resolve in Phase 0 before writing the wrapper)

1. **[decisive] Does Copilot CLI honor a long-running (60–180s) MCP tool call?** Test an artificial slow
   MCP tool against current Copilot CLI. If it hard-times-out under ~60s, the team-lead-as-one-tool shape
   is infeasible and we fall back to "Copilot custom-agent shells to `claude -p`" (a different wrapper).
2. **[policy] Is a personal, non-distributed Copilot→Claude orchestrator in-scope for the Feb-2026 OAuth
   restriction**, or does it require a metered API key? Fetch `support.claude.com/en/articles/15036540`
   + ToS before relying on subscription auth. (Matches the "verify policy at Team Lead" discipline.)
3. **[bug lifetime] Is Copilot #2540 still open?** (Confirmed OPEN 2026-05-28.) If it closes, CURRENT's
   maintainability _improves_ independently — re-weigh whether the hybrid tool is even worth it then.

## Proposed phases (each independently shippable; STOP after Phase 0 if the spike fails)

### Phase 0 — feasibility spike (no product code) — **gate**
- Author a throwaway MCP server exposing one `sleep_then_return(seconds)` tool. Register it with Copilot
  CLI. Measure: does a 30s / 90s / 180s call succeed? Is there progress streaming? What's the hard ceiling?
- Benchmark `time claude -p "say hi"` cold + warm on the target host (kills/keeps the latency argument).
- Resolve the OAuth-policy question from primary sources.
- **Deliverable:** a 1-page findings note appended here. **Decision gate:** proceed only if a multi-minute
  MCP tool is viable; else pivot to the custom-agent-shells-to-`claude -p` variant and re-plan.

### Phase 1 — the orchestrator MCP wrapper (thin, stdio)
- A stdio MCP server exposing ONE tool, e.g. `ravenclaude_team_lead(task, context)`, that shells to plain
  `claude -p` (NOT `--bare`; subscription-auth constraint) running the Team Lead dispatch prompt.
- Returns the Structured Output Protocol JSON block as the tool result.
- Ships generated (single source of truth), wired via the existing `ravenclaude` installer into
  `~/.copilot/mcp-config.json` — reusing the MCP-merge path already in `cmd_install`.
- **Explicitly NOT:** a replacement for any hook. The `.github/hooks` floor is untouched.

### Phase 2 — guardrails on the tool itself
- The orchestrator tool's own nested Claude Code run carries the full in-host apparatus (hooks fire in
  _its_ loop). Verify the runaway-brake + DoD-gate + tribunal apply inside the delegated subtree.
- Confirm the egress-secret backstop covers the tool's payload (it's a new ingress path).

### Phase 3 — docs + the honest caveat
- Document in `plugins/ravenclaude-core/CLAUDE.md`: the floor is in-host and non-negotiable; the
  orchestrator tool is optional and additive; "if Copilot delegates everything, prefer just running
  Claude Code directly" — the tool is for _selective_ heavy fan-out, not wholesale delegation.

## What this plan deliberately does NOT do

- Does **not** make Copilot delegate 100% (unenforceable, and collapses into "just run Claude Code").
- Does **not** move, weaken, or relocate the deterministic floor.
- Does **not** assume the SDK gives back free subscription auto-mode.

## Success criteria

- The in-host floor still gates a Copilot-native `git push --force` / `curl|sh` with the orchestrator tool
  installed (prove the floor didn't move).
- A delegated `ravenclaude_team_lead(...)` call runs a real multi-agent fan-out and returns SOP JSON.
- `ravenclaude update` keeps the wrapper current with zero re-install (the design pillar).

## Decision for Matt

Approve the **phased hybrid** (build starts at Phase 0, a no-product-code spike), or adjust scope. The
spike is cheap and is the honest gate — if Copilot can't host a multi-minute MCP tool, we learn that
before writing the wrapper.

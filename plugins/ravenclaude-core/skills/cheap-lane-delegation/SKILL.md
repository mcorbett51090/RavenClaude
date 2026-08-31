---
name: cheap-lane-delegation
description: "Route ONE well-defined job (single-file, tests, summary, mechanical refactor) off Claude via cheap-lane-delegate.sh (bounded, returns). Opt-in cheap_lane: advise|agent. NOT for quota-escape, host-switch, fresh window, or 'pass remaining work to Grok' → session-handoff."
allowed-tools: Bash, Read
---

# Skill: cheap-lane-delegation

The Team Lead already dispatches to Claude sub-agents for team-of-agents work
(`skills/spawn-team`). This skill is the same dispatch discipline applied to a
**second, cheaper backbone** for the narrow slice of work that doesn't need Claude's
judgment at all — and it composes with, never replaces, spawn-team.

**Why this exists.** Measured on the owner's account (2026-08-26, 14 days of
transcripts): main-loop output was 41.2M tokens, 83.2% top-tier model, 16.6%
second-tier — essentially none of it on a cheap model. That spend is in the
conversation itself, not in sub-agent dispatch, so no amount of tuning *sub-agent*
model tiers touches it. The fix is upstream of tier selection: **decide whether a
task needs to be in the main session's own reasoning loop at all**, before deciding
which model handles it.

---

## Off by default — read this before doing anything else

`cheap_lane:` in `.ravenclaude/comfort-posture.yaml` gates this skill, matching
`design_checkins` / `decision_review` / `parallelism` / `orchestrator`: an **opt-in
behavioral commitment**, not a machine-enforced control, and **absent or `off` means
this skill is a no-op** — check the knob before doing anything else.

```yaml
cheap_lane:
  mode: off          # off (default) | advise | agent
  tier: fast          # fast (default) | balanced | top — the delegated-work tier
  agent: grok          # grok (default) | copilot — the coding agent CLI to delegate to
```

| Mode | What happens |
|---|---|
| `off` (default) | This skill does nothing. Every task stays in the main session, exactly as before. |
| `advise` | A cheap-lane-routed task runs in an isolated scratch dir; its output is returned as a **suggestion** for you to apply, never applied automatically. |
| `agent` | A cheap-lane-routed task runs in a disposable git worktree with write access; **you review the diff before it merges.** |

**Nothing here executes without the knob set**, and nothing in `agent` mode merges
without a human (or the Team Lead, explicitly, per the Agentic-Default Principle)
reviewing the diff first.

---

## Step 1 — route the task

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-plugins/ravenclaude-core}/scripts/route-task.py" --task "<the task description>"
```

Returns JSON: `{"lane": "cheap"|"claude", "tier": "fast"|"balanced"|"top", "rule": "...", "reason": "..."}`.

⛔ **The default is `claude`, deliberately asymmetric.** A task wrongly sent to the cheap lane
can produce a confidently wrong multi-file change that costs more to unwind than it
saved; one wrongly kept on Claude costs only money. So an unmatched task, an
ambiguous task, and a task matching **both** an escalation and a cheap-lane rule all
resolve to `claude` — escalation rules dominate cheap rules, never the reverse. This
is a **text classifier over a task description**; it cannot read the repo, so it
does not know that "fix the typo in auth.py" touches a security boundary — the
escalation rules are deliberately broad for exactly that reason.

If `lane == "claude"`: do the work yourself (or dispatch a Claude sub-agent per
`spawn-team`), as normal. This skill has nothing further to do.

If `lane == "cheap"`: continue to Step 2.

---

## Step 2 — delegate

```bash
bash "${CLAUDE_PLUGIN_ROOT:-plugins/ravenclaude-core}/scripts/cheap-lane-delegate.sh" \
  --agent <cheap_lane.agent, default grok> \
  --tier <tier from Step 1> --mode <advise|agent, from cheap_lane.mode> \
  --task "<the same task description>" [--repo <path>, agent mode only]
```

`cheap-lane-delegate.sh` is an **agent-agnostic dispatcher** — it owns only
*which coding agent CLI* to shell out to; every other flag passes through
verbatim to that agent's own delegate script (`grok-delegate.sh` /
`copilot-delegate.sh`), because the two CLIs' real flag shapes genuinely differ
(Grok has `--sandbox`/`--max-turns`; Copilot has `--deny-tool`, no turn cap).
Calling a per-agent script directly (skipping the dispatcher) also works — the
dispatcher exists for the common case of a posture-driven agent choice, not as a
mandatory indirection layer.

### The matrix — coding agent x model x effort x turn/timeout budget

This is **not a single-vendor tool.** `--tier` resolves the same three-row shape
-- `fast` / `balanced` / `top` -- differently per agent, because each CLI's real,
**live-verified** (2026-08-26) capability shape differs:

| Tier | **Grok** -- model / effort / perspective | **Grok** budget | **Copilot** -- effort | **Copilot** budget |
|---|---|---|---|---|
| `fast` (default) | grok-4.5 / low / scanner | 15 turns / 300s | low `[see honest limit below]` | 300s (no turn-count flag exists) |
| `balanced` | grok-4.5 / high / architect | 30 turns / 600s | medium `[see honest limit below]` | 600s |
| `top` (never auto-assigned) | grok-4.6 / high / critic | 60 turns / 1200s | high `[see honest limit below]` | 1200s |

Grok's model+effort+perspective come from the shared
[`knowledge/substrate-tier-map.json`](../../knowledge/substrate-tier-map.json)
(the **same map** FORGE's G2/G3 panels resolve from -- reused, not duplicated).
**Copilot's row is deliberately NOT sourced from that same map**, even though it
also carries a `hosts.copilot` entry: that entry's model strings
(`"Claude Sonnet 5"`, display-name shaped) are for FORGE panel resolution, a
different consumer with different invocation mechanics, and none of six
distinct guesses derived from it validated as a real `--model` value against
the installed Copilot CLI this session -- see `copilot-delegate.sh`'s own header
for the full, live-probed record. Reusing that map here would have been the
exact "looks like one source of truth, isn't verified for this use" trap.

⛔ **Honest limit, stated because it was measured, not assumed:** Copilot's
`--model auto` (the default -- no valid PINNED slug was discoverable
non-interactively) **rejects `--effort` outright at the API level**
(`"Model \"auto\" does not support reasoning effort configuration"`, a real
runtime error, not a guess). So out of the box, **the Copilot lane's tier
ladder differentiates by timeout budget only** -- the effort column above is
what `--effort` WOULD carry if a caller pins a real, effort-capable model via
`copilot-delegate.sh --model <slug>` (confirmed via the interactive `/model`
picker on your own account), at which point `--effort` is sent for real.

Plus the levers that are orthogonal to tier and always available:

| Lever | Values | Set by |
|---|---|---|
| `--agent` | `grok` (default) \| `copilot` | `cheap_lane.agent` in `comfort-posture.yaml`, or the dispatcher flag directly -- the coding-agent-selection lever |
| `mode` | `advise` (suggestion only) \| `agent` (disposable worktree, human reviews the diff) | `cheap_lane.mode` in `comfort-posture.yaml` -- the containment lever |
| `--effort` | Grok: `low`\|`medium`\|`high` (CLI rejects `xhigh`). Copilot: `none`\|`minimal`\|`low`\|`medium`\|`high`\|`xhigh`\|`max`, sent ONLY with a pinned `--model` (see above) | An explicit CLI override -- wins over the tier-resolved effort |
| `--model <slug>` | Copilot only; Grok's model comes from the tier map, unoverridable here | An explicit CLI override for a caller who has confirmed their own valid slug |
| `--timeout <secs>` / `--max-turns <n>` (Grok only -- no verified Copilot turn-count flag) | any positive int | An explicit CLI override -- wins over the tier's budget row above |

**Why turn/timeout scale with tier at all.** Before this, every delegated task got the
same flat 30-turn/600s budget regardless of how trivial or how deep the task was -- a
one-liner regex paid for the same ceiling as a multi-file mechanical refactor, and
`top` (reserved for the hardest cheap-lane-adjacent work a human explicitly picked)
had no extra runway to actually use its stronger model. Scaling the budget with the
tier means `fast` fails fast (300s) instead of hanging for 10 minutes on a task that
should have taken 20 seconds, and `top` gets the room its model/effort choice implies
it might need.

**codex is not a supported `--agent` value.** The Codex CLI was not installed on
the host this matrix was built and verified against, so its non-interactive
invocation syntax could not be live-tested the way Grok's and Copilot's were --
see `cheap-lane-delegate.sh`'s header for the full reasoning and what a future
session needs to add it for real, rather than on a guess.


Exit code is the whole contract — **treat any non-zero as "do it locally"**, silently, no drama:

| Exit | Meaning |
|---|---|
| `0` | The delegated agent's output is on stdout (advise mode) or the diff is staged in a worktree (agent mode) — use it. |
| `2` | The target CLI is absent, a bad argument was given, or `--agent` named an unsupported agent. Fall back to doing the task yourself. |
| `4` | The delegated agent itself failed or exceeded its timeout. Fall back. |
| `7` | A recursion guard fired (nested delegation, or called from inside a tribunal seat). Never override this — fall back. |
| `8` | The task text contained a secret-shaped literal and was refused **before** anything left this machine. Remove the secret; do not retry with the same text. |
| `9` | `agent` mode couldn't provision an isolated worktree. It refused rather than letting the delegated agent touch the live checkout — do the task yourself. |

⛔ **Containment is per-agent, and the two shipped agents are NOT equally strong.**
`grok-delegate.sh`'s header has the measured, positive-controlled proof that
`--sandbox` is a real KERNEL boundary (Seatbelt on macOS / Landlock on Linux) —
the strongest containment this tool offers, plus the one real footgun in Grok's
own flags (`--tools ""` means "no restriction," not "no tools" — the script does
not pass it). `copilot-delegate.sh`'s header documents the honest opposite: its
containment is CLI-documented default-path restriction (verified working,
including a real refused-write positive control), **not** a measured kernel
sandbox — read that header before choosing `agent` mode with `--agent copilot`
on anything you would not also hand write access via a worktree alone.

---

## Composition with existing dispatch (read this — it is not a separate system)

| Question | Answered by |
|---|---|
| Does this multi-agent orchestration need a Claude sub-agent, a skill, or a dynamic workflow? | `spawn-team` Step 2 |
| Is this ONE well-defined task cheap enough to route off Claude entirely? | **This skill** |
| Must a **new session** on another host own the rest (quota, leftover list, plugin-cache reload)? | `session-handoff` — not this skill |
| Should a sub-agent dispatch downgrade/upgrade tier? | `agent-dispatch-evaluator` (governs sub-agent calls only — see its own `dispatch-config.json`) |

This skill and `agent-dispatch-evaluator` are **not the same mechanism** and do not
conflict: the evaluator tunes which *model tier* a Claude sub-agent dispatch uses;
this skill decides whether a task enters the Claude reasoning loop **at all**. A
task can be evaluator-tuned AND still never reach the cheap lane (most won't — the
escalation rules are broad on purpose).

**The orchestrator-worker rule is unchanged.** Only the Team Lead dispatches — to a
Claude sub-agent, or, when this skill is on, to the configured cheap-lane agent. A dispatched Claude sub-agent
does not itself invoke this skill; that would be the sub-agent spawning further
work outside the Team Lead's view, which `rules/agent-collaboration.md` already
governs against.

---

## Honest limits

- **This is text-shape routing, not code understanding.** It cannot see that a
  "simple" edit touches a security boundary two files away. The escalation rules
  are broad by design to compensate, but they are not infallible — review
  `agent`-mode diffs regardless of how routine the task looked.
- **No hook enforces which lane a task takes.** Like `design_checkins` and every
  other behavioral posture knob, this is the Team Lead honoring a stated
  preference, not a machine-checked gate. `route-task.py --self-test` proves the
  *router* is sound; nothing proves the Team Lead actually consulted it on every
  eligible task.
- **The delegated agent's own permission flags are not equally trustworthy as a
  safety boundary across agents.** For Grok, the isolated scratch dir / worktree
  PLUS a measured, positive-controlled kernel sandbox (Seatbelt/Landlock) both
  hold — see `grok-delegate.sh`'s header. For Copilot, only the scratch
  dir/worktree PLUS the CLI's documented (verified, not kernel-enforced)
  default-path restriction hold — see `copilot-delegate.sh`'s header. Do not
  relax either design without re-running that agent's own probes.

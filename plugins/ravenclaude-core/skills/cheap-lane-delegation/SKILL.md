---
name: cheap-lane-delegation
description: Route everyday, well-defined work (single-file edits, test-writing, summarization, mechanical refactors, boilerplate) to Grok instead of doing it in the main Claude session, escalating multi-file/architecture/debugging/security work to Claude. Opt-in via the `cheap_lane:` comfort-posture knob.
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
  tier: fast          # fast (default) | balanced — the Grok tier for delegated work
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

Returns JSON: `{"lane": "grok"|"claude", "tier": "fast"|"balanced"|"top", "rule": "...", "reason": "..."}`.

⛔ **The default is `claude`, deliberately asymmetric.** A task wrongly sent to Grok
can produce a confidently wrong multi-file change that costs more to unwind than it
saved; one wrongly kept on Claude costs only money. So an unmatched task, an
ambiguous task, and a task matching **both** an escalation and a cheap-lane rule all
resolve to `claude` — escalation rules dominate cheap rules, never the reverse. This
is a **text classifier over a task description**; it cannot read the repo, so it
does not know that "fix the typo in auth.py" touches a security boundary — the
escalation rules are deliberately broad for exactly that reason.

If `lane == "claude"`: do the work yourself (or dispatch a Claude sub-agent per
`spawn-team`), as normal. This skill has nothing further to do.

If `lane == "grok"`: continue to Step 2.

---

## Step 2 — delegate

```bash
bash "${CLAUDE_PLUGIN_ROOT:-plugins/ravenclaude-core}/scripts/grok-delegate.sh" \
  --tier <tier from Step 1> --mode <advise|agent, from cheap_lane.mode> \
  --task "<the same task description>" [--repo <path>, agent mode only]
```

Exit code is the whole contract — **treat any non-zero as "do it locally"**, silently, no drama:

| Exit | Meaning |
|---|---|
| `0` | Grok's output is on stdout (advise mode) or the diff is staged in a worktree (agent mode) — use it. |
| `2` | `grok` CLI absent, or a bad argument. Fall back to doing the task yourself. |
| `4` | Grok itself failed or exceeded its timeout. Fall back. |
| `7` | A recursion guard fired (nested delegation, or called from inside a tribunal seat). Never override this — fall back. |
| `8` | The task text contained a secret-shaped literal and was refused **before** anything left this machine. Remove the secret; do not retry with the same text. |
| `9` | `agent` mode couldn't provision an isolated worktree. It refused rather than letting Grok touch the live checkout — do the task yourself. |

⛔ **Containment is the worktree AND the kernel sandbox, deliberately both** — see
`grok-delegate.sh`'s own header for the measured, positive-controlled proof that
`--sandbox` really is enforced (Seatbelt on macOS / Landlock on Linux) and for the
one real footgun in Grok's own flags (`--tools ""` means "no restriction," not "no
tools" — the script does not pass it).

---

## Composition with existing dispatch (read this — it is not a separate system)

| Question | Answered by |
|---|---|
| Does this multi-agent orchestration need a Claude sub-agent, a skill, or a dynamic workflow? | `spawn-team` Step 2 |
| Is this ONE well-defined task cheap enough to route off Claude entirely? | **This skill** |
| Should a sub-agent dispatch downgrade/upgrade tier? | `agent-dispatch-evaluator` (governs sub-agent calls only — see its own `dispatch-config.json`) |

This skill and `agent-dispatch-evaluator` are **not the same mechanism** and do not
conflict: the evaluator tunes which *model tier* a Claude sub-agent dispatch uses;
this skill decides whether a task enters the Claude reasoning loop **at all**. A
task can be evaluator-tuned AND still never reach the cheap lane (most won't — the
escalation rules are broad on purpose).

**The orchestrator-worker rule is unchanged.** Only the Team Lead dispatches — to a
Claude sub-agent, or, when this skill is on, to Grok. A dispatched Claude sub-agent
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
- **Grok's own permission flags are not the safety boundary here** — the isolated
  scratch dir / worktree is, verified with a positive control in
  `grok-delegate.sh`'s header. Do not relax that design without re-running those
  probes.

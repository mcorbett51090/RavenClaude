# Token-budget playbook — turning Max 20x headroom into throughput

> **Purpose.** A phased, ROI-ordered guide for converting an under-used Max 20x
> token budget into more concurrent work and more quality passes — tuned to
> _this_ repo's existing tooling. Written 2026-06-04.
>
> **Provenance.** Feature mechanics verified this session against the official
> Claude Code docs (`code.claude.com/docs`, via the `claude-code-guide` agent,
> 2026-06-03). Plan-limit numbers are from Anthropic help pages + third-party
> trackers (see Sources) and **shift over time** — treat them as orders of
> magnitude, not contract. Repo tooling claims are grounded in the files cited
> inline (checked this session).

## The reframe

On Max 20x the binding constraint is almost never tokens — it's _your attention_
and how much work you orchestrate in parallel. "Maximize token usage" therefore
means: **run more concurrent work, and layer more quality passes on each change.**
Burning tokens is not the goal; converting idle budget into finished, verified
work is.

What you're sitting on (approximate, [Sources](#sources)):

- **~900 prompts / rolling 5-hour window** on Max 20x (counter starts on your
  first prompt, not a wall clock).
- **Two weekly caps** (one all-model, one Sonnet-only), reset 7 days after a
  session starts.
- **Opus and Sonnet run on _independent_ 5-hour and weekly buckets** — burning
  Opus doesn't touch Sonnet.
- 5-hour limits were **permanently doubled** for Claude Code (May 2026).
- Usage is **shared** across Claude Code, claude.ai chat, and Cowork.

Driving one serial session uses maybe 5–10% of that. The phases below close the gap.

---

## Phase 0 — Set high-throughput personal defaults (one-time)

Put _personal_ defaults in `.claude/settings.local.json` (gitignored — verified
this session via `git check-ignore`), so the shared team `settings.json` stays
untouched. This repo now ships one:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "claude-opus-4-8[1m]",
  "env": { "CLAUDE_CODE_EFFORT_LEVEL": "xhigh" }
}
```

- `model: claude-opus-4-8[1m]` — Opus 4.8 with the **1M context window**, included
  on Max (no premium for tokens 200K→1M).
- `CLAUDE_CODE_EFFORT_LEVEL: xhigh` — default to deeper reasoning per turn.
  Per-docs mechanism; if a build doesn't honor the env var, the reliable
  per-session fallback is `/effort xhigh` (or `ultrathink` in a single prompt).

> The shared `settings.json` pins `claude-opus-4-7` for the team. Bumping the
> team default to 4.8 is a separate, team-wide call — left as a suggestion, not
> changed here.

---

## Phase 1 — Parallelism (the biggest multiplier)

### 1a. Background-agent swarm

Dispatch independent sessions that run concurrently against your quota:

```bash
claude agents                      # dashboard: type a prompt + Enter to dispatch
                                   #   Space = peek, Enter = attach, Ctrl+T = pin
claude --bg "investigate the flaky CI on PR #268"   # fire-and-forget from shell
claude --bg --name fix-auth "fix the token refresh bug"
```

Each session burns quota independently — running 5–10 in parallel is _the point_.
Idle non-pinned sessions auto-stop after ~1h.

### 1b. Worktrees — you already have the tooling (you just weren't using it)

This repo ships a complete worktree system; nothing to install:

| Tool                                            | What it does                                            |
| ----------------------------------------------- | ------------------------------------------------------- |
| `scripts/worktree-new.sh <slug>`                | One isolated tree at `.claude/worktrees/<slug>` on `agent/<slug>` |
| `scripts/worktree-clean.sh <slug>` / `--status` / `--all` | Safe removal (refuses dirty trees), status, bulk-clean  |
| `scripts/worktree-swarm.sh <slug>...`           | **New:** fan out N trees + emit `claude --bg` dispatch lines |
| skills `new-worktree` / `cleanup-worktrees`     | Team-Lead managed-worktree workflow (a.k.a. "Sleipnir") |

The reason worktrees matter: **two agents editing the same working tree silently
corrupt each other's diffs.** A worktree gives each parallel agent its own
checkout of the same repo, so a swarm is collision-free.

The fast path — spin up a swarm and get pasteable launch commands:

```bash
scripts/worktree-swarm.sh --task "port module X to the new API" mod-a mod-b mod-c
# creates 3 trees, prints one `claude --bg` line per tree
scripts/worktree-swarm.sh --status        # who has uncommitted changes
scripts/worktree-swarm.sh --clean-all      # remove every clean tree when done
```

For ad-hoc, fire-and-forget exploration the Agent tool's built-in
`isolation: "worktree"` is simpler (auto-cleaned if the sub-agent makes no
changes). Use the managed scripts above when the tree must persist across
several agent runs and be visible to later steps — that's the distinction the
`new-worktree` skill draws.

### 1c. Subagent fan-out within one session

Delegate verbose work (log sweeps, multi-file search) to subagents — they run in
isolated context and return only a summary, keeping your main thread clean. Spawn
several in one message to run them concurrently. Route cheap work to cheaper
models (`model: haiku` in a subagent's frontmatter): counterintuitively the right
move even on Max, because it frees your Opus 5-hour bucket for work that needs Opus.

---

## Phase 2 — Depth per task

- **`/effort high|xhigh|max`** (or `ultrathink` for a one-off) — the cleanest
  "spend tokens → better answer" knob. `max` for thorny architecture calls,
  `xhigh` as a daily default (set in Phase 0).
- **1M context (`opus-4-8[1m]`)** — hold an entire subsystem + full history and
  do 50-file refactors / whole-codebase reviews without compaction churn.

---

## Phase 3 — Automated quality multi-pass

- **`/code-review`** and **`/security-review`** on every diff (`--fix` applies
  findings). These fork multiple reviewer agents against the diff + full
  codebase, then filter false positives. (`/code-review ultra` runs a deeper
  cloud pass that bills separately to usage credits — not free quota.)
- **CI autofix loop** — ask Claude to `subscribe_pr_activity` on a PR; it
  auto-diagnoses/re-kicks CI until green and answers review comments.
- **`/loop 5m <prompt>`** — keep a session working on an interval (polling a
  deploy, babysitting a PR) without manual checking.

---

## Phase 4 — Spend the budget on _this repo's_ heavy machinery

You've already built token-hungry, quality-multiplying workflows. Use them more
aggressively instead of one-shotting:

- **`deep-research`** — fan-out web search + adversarial verification + cited
  synthesis.
- **`two-panel-plan-review`** — two independent expert panels stress-test a plan,
  then cold-review the build plan. Run before committing engineering effort to
  anything non-trivial.
- **The decision tribunal** (`thing-decide.py`) — routes yes/no calls through a
  multi-seat panel; every seat is token spend that buys an auditable verdict
  instead of a silent guess.

---

## Quick reference

| Lever                       | Command / mechanism                          | Parallelism      |
| --------------------------- | -------------------------------------------- | ---------------- |
| Background swarm            | `claude agents` / `claude --bg`              | Unlimited\*      |
| Worktree swarm              | `scripts/worktree-swarm.sh <slug>...`        | N trees          |
| Subagent fan-out            | spawn several in one message                 | 2–5 / session    |
| Deeper reasoning            | `/effort xhigh`\|`max`, `ultrathink`         | single thread    |
| Big context                 | `opus-4-8[1m]`                               | single thread    |
| Review passes               | `/code-review`, `/security-review` (`--fix`) | several / PR     |
| Recurring autonomy          | `/loop 5m <prompt>`                          | runs unattended  |
| Heavy skills                | `deep-research`, `two-panel-plan-review`     | multi-agent      |

\* bounded only by your rate limits.

## Anti-patterns (these do _not_ increase useful throughput)

- **Output styles / verbosity** change what you _see_, not tokens spent.
- **Prompt caching** _saves_ tokens (reuses the system-prompt/CLAUDE.md prefix) —
  good, but not a way to "use more."
- **Maxing effort on trivial tasks** — overthinking. Match effort to difficulty.

## Troubleshooting

The three failure modes you'll actually hit when running a swarm:

- **`claude --bg` isn't available** (some remote/web sessions, or the CLI flag
  isn't present) — the parallelism still works, it's just driven from _inside_
  the session instead of as detached OS processes. Use the Agent tool's built-in
  `isolation: "worktree"` for fire-and-forget parallel sub-agents, or dispatch
  sub-agents in-session via the Agent/Task tool. `scripts/worktree-swarm.sh`
  still usefully pre-creates the isolated trees regardless.
- **A worktree won't delete (`worktree-clean.sh` refuses)** — the tree has
  uncommitted changes. Run `worktree-swarm.sh --status` (or
  `worktree-clean.sh --status`) to see which trees are dirty first, then either
  commit/stash the work in that tree, or pass `--force` to discard it.
- **An `agent/<slug>` branch lingers after cleanup** — `worktree-clean.sh` only
  auto-deletes the branch when it's fully merged; an unmerged branch is left
  intentionally so work isn't lost. Merge or archive it, then remove the branch.
  This repo blocks `git branch -D` — the sanctioned escape hatch is
  `scripts/archive-branch.sh`.

## Sources

- [What is the Max plan? — Claude Help Center](https://support.claude.com/en/articles/11049741-what-is-the-max-plan)
- [Claude Code Rate Limits & Usage Quotas Explained (2026) — TrueFoundry](https://www.truefoundry.com/blog/claude-code-limits-explained)
- [Complete Claude Limits Guide 2026 — TokenMix](https://tokenmix.ai/blog/complete-claude-limits-guide-2026-tokens-uploads-5-hour)
- [Manage usage credits for paid Claude plans — Claude Help Center](https://support.claude.com/en/articles/12429409-manage-extra-usage-for-paid-claude-plans)
- Claude Code feature mechanics: [official docs](https://code.claude.com/docs/en/) (2026-06-03).

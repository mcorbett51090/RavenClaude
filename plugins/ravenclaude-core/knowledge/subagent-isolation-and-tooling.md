# Sub-agent isolation & tooling — what delegated agents can and can't do

> **Last reviewed:** 2026-06-08 (frontmatter-field + plugin-agent-restriction section added against [sub-agents](https://code.claude.com/docs/en/sub-agents) + [plugins-reference](https://code.claude.com/docs/en/plugins-reference), retrieved 2026-06-08). The original git-write/`isolation` observations below were captured 2026-05-23 against observed Claude Code (Opus 4.7) behavior during a parallel multi-agent PR-review engagement. **Refresh when:** Anthropic changes sub-agent permission inheritance, the `isolation: "worktree"` behavior, the subagent frontmatter field set, the plugin-agent restriction, or background-task tooling. Companion to [`claude-code-permissions.md`](claude-code-permissions.md).

This file records a non-obvious, load-bearing constraint on how the Team Lead delegates work to sub-agents. It cost two blocked waves of agents to pin down — capture it so the next orchestration doesn't repeat the mistake.

## The lesson in one line

**Delegated sub-agents in this environment cannot run git-_write_ commands (`fetch` / `checkout` / `commit` / `push`) — both worktree-isolated _and_ plain non-isolated background agents were denied. Read-only review agents using `git show` worked fine. Conclusion: branch-mutating git work must be done by the main (interactive) agent — only it can obtain the approval that mutating commands require. Worktree isolation is a _further_ restriction that also strips `Read`.**

> **⚠️ Scope correction (2026-06-13) — the one-line lesson above is NOT universal.** Re-verification against current primary docs ([sub-agents.md](https://code.claude.com/docs/en/sub-agents)) + a direct this-session probe **contradicted it as a general rule**: a **non-isolated, foreground** general-purpose sub-agent ran `git checkout -b` and `git commit --allow-empty` — both exit 0, **no permission gate**. The reconciliation is the mechanism already named in this file (see §"What was observed", `ask`-tier bullet): the 2026-05-23 denials were specific to **`run_in_background: true` agents under a posture where git-writes sit in the `ask` tier** — a background (non-interactive) sub-agent can't surface the approval prompt, so the call is refused. A **foreground** sub-agent, or a posture where those commands are `allow`-tier, writes fine. Two further corrections: `isolation: "worktree"` isolates the **working directory, not the `Read` tool** (current docs; the "strips `Read`" observation may reflect old behavior or that wave's specific tool grant — re-verify before relying on it), and the durable reason to keep sub-agent writes serialized/isolated is the **shared-working-tree race** (a non-isolated sub-agent shares the main session's tree + index), not a blanket deny. **Not re-tested this session:** `git push` specifically, and the web/remote restricted-git-proxy. Treat the empirical record below as _conditionally_ true (background × ask-tier), scoped accordingly. Full record: [`docs/research/2026-06-13-claude-subreddit-scan/README.md`](../../../docs/research/2026-06-13-claude-subreddit-scan/README.md) §"Post-scan accuracy re-verification".

## What was observed (2026-05-23)

A 7-PR review ran three waves of delegated agents against the same repo:

| Wave | Agents | Isolation | Tools needed | Result |
|---|---|---|---|---|
| 1. Review (read-only) | 18 background agents | none | `git show <ref>:<path>`, `Read`, `Grep` | ✅ all worked, fully in parallel |
| 2. Edit-application (writes) | 7 background agents | `worktree` | `git checkout` / `commit` / `push` | ❌ all denied **`Bash` + `Read`** |
| 3. Edit-application retry (writes) | 1 background agent | **none** | `git fetch` / `checkout` / `commit` / `push` | ❌ denied **`Bash`** (git-write) — even non-isolated |

Wave 1 parallelized perfectly because `git show <ref>:<path>` reads any branch **without touching the working tree** — no checkout, no collision, no isolation needed. Waves 2 and 3 both failed: the writes never ran. Wave 3 is the decisive data point — dropping isolation did **not** restore the ability to write.

## Why it happens

- `git show origin/<branch>:<file>` prints a blob from any ref without changing `HEAD` or the working tree, and is read-only — so it sits in the pre-allowed tier and runs unattended. N agents can read N different branches concurrently in one clone with zero contention.
- `git fetch` / `checkout` / `commit` / `push` **mutate** state. In this session's permission posture those land in the "ask" tier, and **a background sub-agent cannot surface an interactive approval prompt** — so the call is auto-denied. The main (interactive) agent hits the same tier but _can_ get approval, which is why the Team Lead's own `git commit`/`push` succeed while a sub-agent's identical command is refused.
- `isolation: "worktree"` is a **separate, additional** restriction: it also strips `Read` (wave 2 lost both `Bash` and `Read`). So worktree isolation is strictly worse for this kind of work, not a workaround.

The earlier draft of this file guessed the cause was worktree isolation alone and suggested "serialize non-isolated agents" as a fix. Wave 3 disproved that — recording the correction here so the wrong workaround isn't attempted again.

## How to actually delegate the work

**Read-only fan-out (analysis, review, search):** spawn non-isolated background agents freely and in parallel. Have them read via `git show <ref>:<path>`. Fast, safe, and the right default for multi-branch review.

**Branch-mutating work (edit / commit / push across branches):** **the main (interactive) agent does it** — sequentially, branch by branch (checkout → edit → commit → push → next). This is the only path confirmed to work in this environment, because mutating git needs approval a background sub-agent can't get. Two things that look like workarounds but do **not** help here:

- _Non-isolated agents, serialized one per branch_ — still denied (wave 3); the blocker is the approval tier, not working-tree contention.
- _Agents building their own `git worktree` by hand_ — still needs git-write Bash (denied), and edits land on `/tmp/...` paths that the `enforce-layout` hook rejects as off-pattern.

If the write volume is large, the lever is **the main agent's context budget**, not delegation: read targeted sections of large files (`git show`/`grep` to locate, `Read` with offset/limit) rather than whole files, and commit each branch before moving to the next so progress survives a context summarization.

## Rule of thumb

> Reading a branch needs no isolation and no approval (`git show` — parallelize across sub-agents freely). Writing a branch needs approval that only the main agent can obtain — so do all checkout/commit/push work in the main session, sequentially. `isolation: "worktree"` only makes it worse (it also removes `Read`). Don't delegate git-writes to sub-agents in this environment.

## Subagent frontmatter — the field set, and what a plugin-shipped agent may use

> Reviewed 2026-06-08 against [sub-agents](https://code.claude.com/docs/en/sub-agents) + [plugins-reference](https://code.claude.com/docs/en/plugins-reference) (retrieved 2026-06-08). The git-write observations above are about *runtime* behavior; this section is about the *declarative* surface — what you can put in an agent's YAML frontmatter, and the binding constraint on plugin-shipped agents.

A subagent definition's frontmatter accepts the following fields. The ones load-bearing for cost, safety, and institutional memory:

| Field | Type / values | Effect |
| --- | --- | --- |
| `name`, `description` | string | Identity + dispatch hint. |
| `tools`, `disallowedTools` | list | Allow-list / block-list the agent's tool surface. |
| `model` | model id | Pin the backbone (right-size cost; e.g. Haiku for cheap read-only agents). |
| `effort` | reasoning-effort dial | Tune depth vs. cost per agent. |
| `maxTurns` | integer | Hard ceiling on the agent's turn budget (runaway brake). |
| `skills` | list | **Preload** named skills into the agent at dispatch. |
| `memory` | `user` \| `project` \| `local` | Give the agent a **persistent `MEMORY.md` directory** at the named scope — institutional memory that survives across runs. |
| `background` | `true` \| `false` | Run detached (the background-agent path; note the git-write constraint above still applies). |
| `isolation` | `worktree` | Run in a git worktree — and, per the lesson above, this **also strips `Read`**, so it is a *further* restriction, not a convenience. |
| `color`, `initialPrompt` | string | Display + seed-prompt niceties. |

### Binding constraint: a plugin-shipped agent may NOT use `hooks`, `mcpServers`, or `permissionMode`

> **Load-bearing accuracy note. Verified 2026-06-08** against [plugins-reference](https://code.claude.com/docs/en/plugins-reference).

When an agent ships **inside a plugin** (as every `plugins/ravenclaude-core/agents/*.md` does), three frontmatter fields are **silently ignored** for security reasons:

- `hooks`
- `mcpServers`
- `permissionMode`

"Silently ignored" is the trap: declaring them does **not** error — it just has no effect, so an agent that *appears* to (say) lower its own `permissionMode` or wire its own `hooks` is running with none of that in force. A plugin agent's writable declarative surface is therefore exactly: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation` (plus `color` / `initialPrompt`). Anything requiring `hooks` / `mcpServers` / `permissionMode` must be wired at the plugin level (`hooks/hooks.json`, the plugin's MCP declaration) or in the consumer's `settings.json` — never on the agent.

**Implication for core's roster:** the fields above are the whole declarative surface, and (since 2026-09-14) every roster agent carries `model:` and `tools:` under CI gates (`check-frontmatter.py`; Gates 287/288 for the tier; Gate 289 for dispatch). **Subagents *can* spawn subagents on this platform** — three layers deep by default, `[docs-verified 2026-09-14, sub-agents § "Let subagents spawn their own subagents"]`; see § "Native subagent runaway guards" below. The "Team-Lead-only dispatch" rule is a **house policy**, and the field that actually enforces it is `tools`: a subagent whose allow-list omits `Agent` cannot dispatch, and `Agent(type)` scoping is *ignored* in a subagent definition, so `Agent` in any form is an unscoped grant. `scripts/check-nested-dispatch.py` (Gate 289) fails any shipped `agents/*.md` that grants it without a reasoned exemption; the determination is [`docs/decisions/2026-09-14-nested-dispatch-determination.md`](../../../docs/decisions/2026-09-14-nested-dispatch-determination.md). An earlier revision of this paragraph called the rule "subagents cannot spawn subagents"; that was a platform claim, and it was false.

### `CLAUDE_CODE_SUBAGENT_MODEL` is a fleet DEFAULT, not an override — unless you set `_FORCE`

> **Load-bearing accuracy note — order corrected 2026-09-14** against [sub-agents § "Choose a model"](https://code.claude.com/docs/en/sub-agents) and the `anthropics/claude-code` changelog (both retrieved this session). The 2026-06-22 revision of this section quoted the env var as step **1**; that was true when written and has been **stale since v2.1.251**, which moved it to step 3 (*"set the default subagent model rather than override everything: an agent definition's `model:` and an explicit per-spawn model now take precedence over it"*). v2.1.257 then added `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` to restore the old override behaviour on request. Surfaced originally by the 2026-06-22 Claude-subreddit scan — see [`docs/research/2026-06-22-claude-subreddit-scan/README.md`](../../../docs/research/2026-06-22-claude-subreddit-scan/README.md).

Claude Code resolves a subagent's model in this order (quoted from the official doc this session):

1. The per-invocation `model` parameter (what the orchestrator passes for one dispatch)
2. The subagent definition's `model` frontmatter (`inherit` selects the main conversation's model)
3. **The `CLAUDE_CODE_SUBAGENT_MODEL` environment variable**, when set to a model alias or id
4. The main conversation's model

Before v2.1.251 the env var came **first** and overrode both the per-invocation parameter and the frontmatter, including `model: inherit`. Setting it to `inherit` is the same as leaving it unset. By itself it does **not** change the model the built-in `Explore` / `Plan` run on — for that, or to make it override everything as it used to, set **`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`** (v2.1.257+), which applies the variable (or the main model) to *every* subagent, ignoring per-spawn and agent-definition overrides.

**The two practitioner levers, restated for the current order:**

- **Main-on-Opus, un-pinned subagents on Sonnet/Haiku in one knob.** `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` (or `haiku`) makes every delegated subagent that pins *nothing* run on the cheaper backbone. Because every RavenClaude roster agent now pins `model:`, this knob reaches only the built-in `general-purpose` / `claude` types and a consumer's own un-pinned agents — the roster's own tiering is done in frontmatter, where Gates 287/288 can see it.
- **Default is `inherit`.** With none of the three levers set, a subagent uses the main conversation's model (step 4): an Opus main session fans Opus subagents. The cheap-subagent saving is opt-in.

**What changed for RavenClaude's guarantee:** under the current order a consumer's plain `CLAUDE_CODE_SUBAGENT_MODEL` **no longer overrides** the `opus` pin on `security-reviewer` / `code-reviewer` / `architect` — the frontmatter pin holds. Only `_FORCE` flattens it, and the tier doctrine says so in one line: *do not set FORCE in a project that runs the review gates through subagents* ([`model-tier-delegation.md`](model-tier-delegation.md) § "The three ways a dispatch picks its model"). The `[unverified — community aggregation]` nuance the June revision carried — that the env var may not reach built-ins with a hard-coded model — is now stated by the doc itself for `Explore` / `Plan` and needs no hedge.

Neither variable is set anywhere in this plugin — they are *consumer-environment* levers, documented here as an interaction, not a config the plugin ships.

## Native subagent runaway guards — the platform now caps concurrency + nesting depth

> **Verified 2026-08-19 against the [Claude Code changelog](https://code.claude.com/docs/en/changelog); changelog through 2.1.250 (2026-08-28) does not reverse these.** These are *native, platform-enforced* caps — the complement to RavenClaude's own **behavioral** parallelism cap ([`skills/spawn-team`](../skills/spawn-team/SKILL.md) Step 5, which no hook tracks) and the deterministic [`runaway-brake.sh`](../hooks/runaway-brake.sh) (`max_total`). Refresh when Anthropic changes the subagent cap set.

Since mid-2026 Claude Code enforces two native ceilings on a subagent fan-out, regardless of any RavenClaude posture:

| Guard | Default | Override | Landed |
| --- | --- | --- | --- |
| **Concurrent subagents** — "one message can't fan out unbounded background agents" | **20** | `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | v2.1.217 (2026-07-21) |
| **Nesting depth** — how deep a subagent may spawn subagents | **3** (was 1) | `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` (`=1` disables nesting) | disabled-by-default v2.1.217 (2026-07-21) → depth 3 v2.1.219 (2026-07-24) |

**The load-bearing interaction with v0.274.0 "parallelism defaults to MAXIMUM":** the constitution's parallelism posture now defaults to maximum fan-out, and its banner states "no hook tracks a live concurrency count." True at the RavenClaude layer — but the **platform still bounds it**: an "unlimited parallelism" posture is silently capped at **20 concurrent subagents** by the native guard above. So "maximum" means "up to the native ceiling," not literally unbounded; document that ceiling here so an orchestrator planning a wide fan-out isn't surprised by silent throttling.

**Retired guard — do not cite the 200 per-session cap as current.** v2.1.212 (2026-07-17) added a per-session spawn budget (default 200, `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`, reset by `/clear`); it was **removed in v2.1.224 (2026-08-07)** — *"long-running sessions no longer refuse new agents (concurrency and depth limits still apply)."* As of 2026-08-28 only the **concurrency (20)** and **nesting-depth (3)** guards remain native; the per-session budget is gone. RavenClaude's own `runaway-brake.sh` `max_total` (default 1200) is the surviving portable equivalent of a total-spawn ceiling for the model-agnostic Copilot/Codex surfaces where the native guard is absent.

---
name: Claude Code parallel and modes
description: >-
  Use when choosing Claude Code CLI parallelism or modes — remapping informal
  "max parallel", picking plan mode / subagents / worktrees /batch / ultracode
  workflows / ultrathink /effort /compact, surviving parent context limits during
  fan-out (disk-first handoff), or writing operator prompt templates.
  Not for non-Claude coding tools (escalate ai-coding-model-guidance) and not
  for inventing a /max-parallel command.
---

# Claude Code parallel and modes

**Plugin home (LOCKED):** `ravenclaude-core` (CLI operator — not `claude-app-engineering`).  
**Evidence:** `/workspace/rc-deep-research-claude-commands/DIGEST.md` + `VERIFY.md` (2026-09-05). Survive-parent: DIGEST-rc-deep-research-session-agent-token-loss (2026-09-05).  
**Verify on install version:** `/help` + https://code.claude.com/docs/en/model-config (version drift).

## Hard rules

1. **There is no official `/max-parallel` or mode named "max parallel".** Org slang only. Remap every ask to documented knobs below.
2. **`ultrathink` ≠ API effort.** Keyword adds an in-context deeper-reasoning instruction for that turn; `/effort` and the API effort level stay unchanged.
3. **`"think"` / `"think hard"` / `"think more"` are not keywords** (model-config). Prefer `ultrathink` or `/effort …`.
4. **`ultracode` ≠ `ultrathink`.** Ultracode is a Claude Code setting: sends API **`xhigh`** **plus** auto dynamic workflows. Ultrathink is one-turn in-context depth only.
5. **Do not invent token deltas, Max quotas, or Grok Bot weekly numbers.**
6. Parallel **writes** need isolation (worktrees / `/batch` / `isolation: worktree`). Never parallel-edit one dirty shared checkout.
7. Raise `CLAUDE_CODE_MAX_*` **only when hitting defaults**, not "for fun."

## Documented knobs (remap table)

| Intent | Use |
| --- | --- |
| Review before edits | **Plan mode** — `Shift+Tab`, `/plan`, `--permission-mode plan` |
| Side research / noisy context | **Subagents** ("use subagents"); short summaries back |
| Parallel **writes** | **Worktrees** `claude --worktree …`, `/batch`, frontmatter `isolation: worktree` |
| Large multi-phase fan-out | **Dynamic workflows** / keyword `ultracode` / `/effort ultracode` / `/deep-research` |
| One hard reasoning turn | Keyword **`ultrathink`** in that prompt |
| Session deeper adaptive reasoning | `/effort xhigh` or `/effort max` (sparingly; `max` often session-only) |
| Context pressure, keep theme | `/compact [focus]`; topic change → `/clear`; inspect → `/context` |
| Post-change cleanup | `/simplify` (parallel review agents) |

### Caps (defaults — confirm on version)

| Knob | Default |
| --- | --- |
| Concurrent Agent-tool subagents | **20** — `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (ultracode sessions **exempt**) |
| Parallel read-only tools + subagents | **10** — `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` |
| Subagent nest depth | **3** — `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` |
| Workflow concurrent agents / run | **≤16** (CPU-limited); up to **1000** agents/run |

## Decision tree

1. Non-trivial / high-blast / unfamiliar → **plan mode** first.  
2. Independent research lanes / noisy logs → **subagents** (or `/deep-research` for breadth web).  
3. Parallel **file writes** → **worktrees / `/batch`**; partition paths; shared contracts sequential.  
4. Huge multi-phase orchestration + verify → **workflow / ultracode** (not for tiny edits).  
5. One hard design/debug turn → **`ultrathink`** (do not raise session effort for everything).  
6. Persistently harder reasoning → `/effort xhigh` or test `/effort max`; drop back to `high` after.  
7. Context full, same theme → `/compact` with focus; new theme → `/clear`.  
8. Human said "max parallel" → map to rows above; **never** hunt `/max-parallel`.
9. Fan-out with heavy returns → **Survive parent context** (disk-first; batch; persist before compact; escalate long work to agent-view).

### Plan mode precision (VERIFY must-fix)

Plan mode: research/propose **without source edits** until approve. Reads + **built-in read-only** shell exploration; **other** shell may prompt or go through classifier when auto-during-plan is available. Bypass-permissions sessions **do not** enforce plan edit/command blocks. Status: `⏸ plan mode on`.

## Operator block (paste into GO / implement briefs)

```text
## Parallelism (map "max parallel" → official Claude Code controls)
- Fan out *independent* WebFetch/WebSearch/reads and subagent units in parallel.
- Serialize only on true dependencies or shared-file ownership.
- Prefer: subagents for side research; `/batch` or worktrees for edit fan-out;
  `ultracode` / "use a workflow" for large multi-phase orchestration;
  `/deep-research` for breadth web research.
- Isolation: worktree for any parallel *writes*.
- Do NOT invent extra scope just to parallelize.
- Caps: default concurrent subagents ~20; workflow ~16 concurrent —
  raise env only if blocked on the default.
- No `/max-parallel` command. ultrathink ≠ /effort. ultracode ≠ ultrathink.
- "think" / "think hard" / "think more" are ordinary text, not keywords.
- Survive parent context: workers write mid-run to a run dir; return path + ≤~1.5–2k only.
- Do not /compact while waiting on unpersisted large returns — persist first, then compact.
- Batch verbose fan-out (often ≤2–3 concurrent returns) so parent is not flooded.
- Budget (--max-budget-usd) halts background subagents — different from compact.
- Long independent work: escalate to agent-view / claude --bg / separate sessions.
```

## Survive parent context

**Evidence:** DIGEST-rc-deep-research-session-agent-token-loss (2026-09-05; fleet cli-out). Prefer **extension** of this skill — not a new plugin.

### Ideal (fleet default) — disk-first handoff + thin parent + batched returns

1. Every worker **writes mid-run** to a run dir (`angles/`, digests, `run-log.jsonl`) **before** returning.
2. **Return only** path + ≤~1.5–2k digest (never raw dumps or full scrapes).
3. Parent is a **path index + decision engine**; re-read files after `/compact`, `/clear`, or a new session.
4. **Batch fan-out** so parent is not flooded in one burst (effort ladder: fact 0–1 / compare 2–4 / breadth ≤8–10; for verbose returns often ≤2–3 concurrent).
5. **Do not `/compact` while waiting** on large unpersisted returns — persist first, then compact.
6. Raise `CLAUDE_CODE_MAX_*` only when hitting defaults — never invent `/max-parallel`.

### Official facts (High — code.claude.com)

- Full context does **not** end the session; Claude Code **auto-compacts** as the window fills (context-window docs).
- Subagent transcripts persist **independently** of the main conversation under `~/.claude/projects/.../subagents/`; parent compact does **not** wipe them (sub-agents docs).
- Resume via `claude --continue` / `--resume` / `/resume`, then continue a subagent via `agentId` / SendMessage where supported; Explore/Plan are one-shot.
- `/clear` saves prior conversation (recover via `/resume`); `/compact` replaces history with a summary (sessions docs).
- **Budget** (`--max-budget-usd`) **halts running background subagents** — different failure mode from context compact (cli-reference).
- Agent-view background sessions are separate supervised processes; attach/resume recover; process restart can hand off workers (agent-view docs).
- Dynamic workflows keep intermediate results in script variables and are resumable in-session; still-running/failed agents may rerun (cascade risk) (workflows docs).

### Community risk (Medium — hedged anecdotes)

Large parallel **return payloads** into the parent can jump past autocompact and hit API max ("Prompt is too long" / `/compact` death spiral). See anthropics/claude-code issues #26041, #23463, #16209 (2026). Treat as practice risk, not a product guarantee. Disk side-effects workers already wrote survive; only **unpersisted** parent-only state is lost.

### Escalation ladder

| Rank | Mitigation | When |
| --- | --- | --- |
| 1 | Disk-first + thin returns + batch (this section) | Default specialist Max fan-out |
| 2 | Agent-view / `claude --bg` separate sessions | Multi-hour / high-quota independent work |
| 3 | Dynamic workflows / ultracode | Dozens of agents, scripted verify |
| 4 | Worktrees / `/batch` | Parallel **writes** (does not alone fix return flood) |
| 5 | Earlier autocompact (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`) between batches | High-baseline sessions |
| 6 | JSONL salvage after freeze | Last resort |

### T9 — Survive-parent fan-out

```text
Use subagents (or a workflow). Disk-first handoff is mandatory:
- Each worker writes its full artifact under <RUN_DIR>/<unit>/ before returning.
- Each return is path + ≤~2k digest only. No raw dumps into the parent.
- Parent merges by re-reading files from disk after all units finish.
- Batch concurrent returns (start ≤2–3 if payloads are verbose).
- Do not /compact until artifacts are on disk.
- No /max-parallel. Raise CLAUDE_CODE_MAX_* only if blocked on defaults.
Goal: <GOAL>
```

### Anti-patterns (add)

| Anti-pattern | Do instead |
| --- | --- |
| Inline full scrapes / tool dumps into parent after fan-out | File-back; return path + digest |
| /compact while waiting on unpersisted large returns | Persist first, then compact |
| Assume parent compact kills subagent disk transcripts | Transcripts persist; still file-back for usable knowledge |
| Assume budget halt = same as compact | Budget halts background subagents — separate mode |

## Templates (T1–T9)

### T1 — Breadth research

```text
/deep-research <QUESTION>

Requirements:
- Fan out independent angles in parallel (docs, changelog, issues, competing approaches).
- Cross-check claims; drop or mark unverified anything that fails verification.
- Return: claim | source URL | date | confidence | notes.
- Do not invent quotas or product facts without a primary source.
```

Natural variant: `use a workflow to research <TOPIC>: … parallel angles … adversarially verify … Prefer small/medium workflow size unless I say otherwise.`  
Optional: one `ultrathink` on the hard synthesis turn only.

### T2 — Independent file edits

```text
/batch <GOAL>

Rules for the plan you present before spawning:
- Decompose into 5–30 independent units with non-overlapping path ownership.
- Shared contracts / lockfiles / migrations / root config: sequential pre-step.
- Each unit: worktree isolation, implement, test, own PR.
- Max concurrent implementation agents: <N>. Stop if two units need the same file.
```

CLI: `claude --worktree unit-a` / `claude --worktree unit-b` in separate terminals.

### T3 — Plan-then-build

```text
/plan <FEATURE OR BUG>

Constraints:
- Research first; no source edits until I approve the plan.
- Produce: goals, non-goals, file list, risks, test/verify, rollback.
- Call out shared files that must stay sequential.
- After approve: small commits; verify; then /simplify.
```

### T4 — Compact mid-session

```text
/compact Focus the summary on: decisions made, open questions, file paths touched,
commands that worked, and the current plan. Drop exploratory dead-ends and raw
tool dumps. Preserve the acceptance criteria for <TASK>.
```

Pre-flight: `/context` then compact if pressure before the next phase.

### T5 — One hard reasoning turn

```text
ultrathink

Problem: <HARD QUESTION>
Context: <minimal facts / paths>
Decide among <OPTIONS> with tradeoffs, failure modes, and a recommended path.
Do not edit files yet. Do not spawn a large agent fan-out unless I ask.
```

Session depth: `/effort max` then `/effort high` to drop back. **Do not** rely on "think hard".

### T6 — Operator block

Use the operator block in **Operator block** above.

### T7 — Independent research lanes

```text
Use subagents. Spawn three parallel read-only explorers:
1) auth / session — paths under <A>
2) data layer — paths under <B>
3) API surface — paths under <C>
Each returns a short summary (findings, key files, risks). Main agent merges
and proposes a single plan. No file edits from explorers.
```

### T8 — Post-change parallel cleanup

```text
Implement <CHANGE>, verify with <TEST>, then /simplify
```

## Anti-patterns (mandatory)

| Anti-pattern | Do instead |
| --- | --- |
| Always-max-parallel in CLAUDE.md / every prompt | Parallelize only independent units; default effort `high` |
| Parallel agents on shared files / one checkout | Worktrees / `/batch` / path partition |
| Parallel on lockfiles, migrations, root config | One sequential owner |
| "think hard" as effort control | `ultrathink` or `/effort xhigh\|max` |
| `/effort ultracode` for tiny edits | `/effort high`; workflow only when orchestration needed |
| Compact mid-debug when raw tool traces still matter | Finish thread or write keepers first; else `/clear` for new topic |
| Raise `CLAUDE_CODE_MAX_*` without hitting caps | Raise only when blocked |
| Confuse ultrathink / max / ultracode | See remap table |

## Cost / CPCT (high-signal, no invented quotas)

- N parallel agents ≈ **N×** tokens/quota (Cursor docs; Claude agent-view similar signal).  
- Thinking / higher effort billed roughly as **output**-priced tokens.  
- Prefer fleet ladder: fact 0–1 · compare 2–4 · breadth ≤8–10; condensed returns to leads.  
- Spend order when choosing surfaces: Claude Max → Codex → Grok provider → Cursor cloud / Bot session.  
- Do **not** invent Grok Bot weekly balances.

## Out of scope / seams

- **Not** for Copilot/Codex/Grok model routing → `ai-coding-model-guidance`.  
- **Not** a Grok Bot fleet delegation skill (no `grok-bot-delegation` plugin).  
- Agent teams: experimental; confirm enablement on https://code.claude.com/docs/en/agent-teams.md before encoding env strings.  
- Ultrathink-in-skills tip: **demoted** (VERIFY UNVERIFIABLE on primary `code.claude.com` bar).

## Primary citations

- https://code.claude.com/docs/en/model-config  
- https://code.claude.com/docs/en/permission-modes  
- https://code.claude.com/docs/en/sub-agents  
- https://code.claude.com/docs/en/env-vars  
- https://code.claude.com/docs/en/workflows  
- https://code.claude.com/docs/en/context-window  
- https://code.claude.com/docs/en/common-workflows  
- https://code.claude.com/docs/en/agents  
- https://code.claude.com/docs/en/commands  
- https://support.claude.com/en/articles/14554000-claude-code-power-user-tips  
- https://code.claude.com/docs/en/agent-view
- https://code.claude.com/docs/en/sessions
- https://code.claude.com/docs/en/cli-reference
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

Full research pack: `/workspace/rc-deep-research-claude-commands/`

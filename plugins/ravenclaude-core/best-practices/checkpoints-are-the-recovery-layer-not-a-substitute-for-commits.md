# Checkpoints / `/rewind` are the recovery layer — they undo Claude's edits, not the world's side-effects

**Status:** Pattern
**Domain:** Project setup / session safety / Guardrails
**Applies to:** `ravenclaude-core` (consumer-repo setup; any unsupervised or fast-iterating session)

---

## Why this exists

This repo ships a deep **prevention** stack — the runaway brake bounds depth, the definition-of-done gate bounds correctness, the task-scope gate bounds breadth, `guard-destructive` blocks the unarguable catastrophes, the containment posture holds the OS boundary, and the tribunal pre-screens commands. All of it answers "stop the bad thing before it happens." None of it answers the **other** half: _"Claude already made the change, it's wrong, and I want the last twenty minutes back."_ That is the **recovery layer**, and Claude Code ships it natively as **checkpoints**.

Claude Code (v2.0+) snapshots state on **every prompt you send**. `/rewind` — or pressing **Esc twice** on an empty prompt — opens a menu of those checkpoints and lets you **restore code**, **restore the conversation**, or **restore both** to any earlier prompt. It is the single most effective "fearless experimentation" affordance the tool has: a bad multi-file edit is two keystrokes from undone, so an agent (or a user driving one) can try the risky refactor instead of tip-toeing around it.

The reason this needs to be a _named rule_ and not just "a nice feature" is its **boundary**, which is non-obvious and bites hard: a checkpoint reverts the **files Claude edited and the conversation** — it does **not** revert anything that escaped the editor. A `Bash` command that dropped a table, pushed a branch, sent a webhook, deleted a file with `rm`, installed a package, or mutated a remote service is **not** undone by `/rewind`. Treating checkpoints as a universal undo is exactly how a session "rewinds" and then acts as if the destructive side-effect never happened — when it very much did.

## How to apply

Use checkpoints as the **fast inner-loop** recovery for in-session edits, and keep the **durable** recovery anchors (git, the destructive-action guards) for everything that leaves the editor.

| Want to undo… | Use… | Why |
| --- | --- | --- |
| A wrong multi-file **edit** Claude just made this session | **`/rewind` → restore code** (or Esc-Esc) | Fast, no commit needed; the checkpoint is already there. |
| A conversation that **went down a bad path** (keep the good code) | **`/rewind` → restore conversation** | Rewinds context-rot / a derailed plan without losing file work. |
| A change you want gone **across sessions / after the container is reclaimed** | **`git` commit + branch** | Checkpoints are session-scoped and ephemeral — a remote-environment container reclaim takes them with it. |
| A **destructive Bash side-effect** (dropped table, pushed branch, deleted file, sent request) | **The thing that prevents it** — `guard-destructive`, the tribunal, a human gate | `/rewind` cannot reach outside the editor; recovery here is "didn't happen," not "undo." |

**Do:**

- Reach for `/rewind` (Esc-Esc) the moment an edit goes wrong — it is faster and cleaner than asking Claude to "revert that," which re-burns context and can compound the mistake.
- Commit at the **same natural boundaries** you'd checkpoint at (after a working phase). The commit is the cross-session anchor; the checkpoint is the within-session one. They compose — they are not redundant.
- Lean on checkpoints to make **prevention affordable**: because a bad edit is cheaply reversible, you can keep the destructive-action guards strict without the session grinding to a halt on every speculative change.

**Don't:**

- Don't treat `/rewind` as a substitute for committing. Checkpoints are **session-local and ephemeral** — they don't survive a fresh session, and in a remote/web environment they don't survive the container being reclaimed. The commit is what persists.
- Don't assume a rewind un-did a `Bash` side-effect. After restoring code, **re-check external state** (the branch, the database, the file the shell touched) — the editor is back, the world may not be.
- Don't disable the destructive-action guards because "I can always rewind." The guards exist precisely for the class of action `/rewind` **cannot** reach.

## Edge cases / when the rule does NOT apply

- **Already pushed / already merged work** belongs to git history, not a checkpoint — use the normal git recovery path (and for an _unmerged_ abandoned branch, [`scripts/archive-branch.sh`](../../../scripts/archive-branch.sh) / the `branch-archive` skill is the sanctioned tag-then-delete).
- **Copilot CLI / non-Claude-Code hosts** don't have Claude Code's checkpoint feature — there the recovery layer is git commits plus the portable guardrails (`runaway-brake`, `dod-gate`, `guard-destructive` via the adapter). This rule's `/rewind` half is Claude-Code-specific; the "commit is the durable anchor" half is universal.
- **Background / unattended runs** can't press Esc-Esc — for those the durable anchor (frequent commits) and the prevention guards carry the whole load; checkpoints are an interactive-session convenience.

## See also

- [`./runaway-brake-prevents-the-thrash-loop.md`](./runaway-brake-prevents-the-thrash-loop.md) · [`./definition-of-done-gate-makes-done-mean-done.md`](./definition-of-done-gate-makes-done-mean-done.md) — the prevention guards this recovery layer complements (depth + correctness bounds).
- [`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md) — `guard-destructive` is the deterministic gate for the side-effects `/rewind` can't reach.
- The marketplace constitution's containment-posture and `guard-destructive` notes in [`../CLAUDE.md`](../CLAUDE.md) — the OS / destructive-Bash boundary that defines what checkpoints structurally cannot undo.

## Provenance

Distilled from a 2026-06-10 scan of Claude Code community discussion (r/ClaudeAI and aggregations of it) cross-checked against [Anthropic's Claude Code checkpointing docs](https://code.claude.com/docs/en/checkpointing). The community's repeated lesson — "Double-Esc / `/rewind` turns Claude Code into a fearless experimentation playground" — is paired here with its repeatedly-missed corollary (checkpoints revert _Claude's edits and the conversation_, **not** `Bash` side-effects or external state), so the recovery layer is documented alongside its real boundary rather than as a universal undo. The repo shipped a thorough _prevention_ stack but no consumer-facing _recovery-layer_ rule — this closes that gap. Research + panel record: [`docs/research/2026-06-10-claude-subreddit-scan/README.md`](../../../docs/research/2026-06-10-claude-subreddit-scan/README.md).

---

_Last reviewed: 2026-06-10 by `claude`_

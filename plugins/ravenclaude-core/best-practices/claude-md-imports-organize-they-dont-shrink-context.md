# CLAUDE.md `@imports` organize — they don't shrink context; path-scoped rules and skills do

**Status:** Pattern
**Domain:** Agent design / Context budget / Memory files

---

## Why this exists

The reflex when a `CLAUDE.md` grows past the "keep it under ~200 lines"
guidance is to split it: move chunks into separate files and pull them back
with `@path` imports. The file *looks* smaller, so it feels like the context
got smaller too. It didn't. **Imported files are expanded and loaded into the
context window at launch alongside the `CLAUDE.md` that references them** — so a
1,000-line `CLAUDE.md` and a 50-line `CLAUDE.md` that `@imports` 950 lines cost
the model the **same** number of tokens every session, and carry the **same**
adherence penalty (Anthropic's own guidance: longer always-loaded instructions
"consume more context and reduce adherence").

`@import` is a *de-duplication and organization* tool — its real job is letting
two tools (or two files) share one source without copy-paste drift (the
canonical case is `@AGENTS.md`, so Claude Code and Cursor/Codex read the same
conventions). It is **not** a context-budget tool. Reaching for it to "save
tokens" is a category error that leaves the file feeling tidy while the model
still carries every byte.

The lever that *actually* shrinks baseline context is **conditional loading** —
move instructions that only matter for part of the codebase out of the
always-loaded memory and into a surface that loads **on demand**:

- **`.claude/rules/` with `paths:` frontmatter** — a path-scoped rule loads only
  when Claude touches a matching file (`src/api/**` rules appear only during API
  work). Out of context the rest of the time → real token savings.
- **Skills** — a skill's body loads only when invoked (or when Claude judges it
  relevant), not every session. A multi-step procedure that lives in `CLAUDE.md`
  "just in case" is paying rent in every conversation; as a skill it pays only
  when used.

So the decision isn't "inline vs. import" — both load at launch. It's
**"always-loaded vs. conditionally-loaded."** Import for dedup; path-scope or
skill-ify for budget.

## How to apply

When a memory file gets large, sort each block by **how often it's actually
needed**, not by how to physically split the file:

| The instruction is… | Put it in… | Loads… |
|---|---|---|
| Needed every session (build/test commands, layout, "always do X") | `CLAUDE.md` (root) — keep it tight | At launch, always |
| Shared with another tool / another file (no duplication wanted) | a file pulled in by `@import` | At launch, always — **organization only, no budget win** |
| Relevant only to specific paths (`src/api/**`, `frontend/**`) | `.claude/rules/<topic>.md` with `paths:` frontmatter | On demand, when a matching file is touched |
| A multi-step procedure used occasionally | a **skill** | On invocation only |

**The worked example is this repo's own memory layout.** The root
[`CLAUDE.md`](../../../CLAUDE.md) is a lean 81 lines and opens with `@AGENTS.md`
— which pulls **188 more lines** into context at launch. The import keeps the
root file *scannable* (Claude-specific notes below, cross-tool conventions
imported above, no copy-paste drift with the Cursor/Codex-readable `AGENTS.md`)
— but it bought **zero** context reduction: the effective always-loaded memory
is ~269 lines, exactly as if both files were one. That's the right call *for
that content* (it genuinely is needed every session and genuinely is shared
cross-tool) — and it's also the precise illustration of the rule: the import
solved a *duplication* problem, not a *budget* one. If a future block were
path-specific, the budget-correct home would be `.claude/rules/`, not another
`@import`.

**Do:**

- **Use `@import` to kill duplication** — `@AGENTS.md`, a shared `@~/.claude/…`
  preferences file across worktrees, a `@package.json` reference. The win is one
  source of truth, not a smaller context.
- **Move path-specific guidance to `.claude/rules/` with `paths:`** — this is the
  one move that genuinely trims the per-session baseline.
- **Skill-ify occasional procedures** — anything that reads "when doing X, follow
  these steps" and isn't needed every turn.
- **Measure, don't eyeball** — a short root file with deep imports is not a small
  context. Check what's actually loaded (`/context`, `/memory`) rather than
  trusting the line count of the top file.

**Don't:**

- **Don't split `CLAUDE.md` into imports expecting a token saving** — you'll get
  a tidier file and the identical context cost.
- **Don't push always-needed facts into a skill** to "save context" — if the
  model needs it every session, conditional loading just means it isn't there
  when it's needed. Conditional loading is for conditional content.

## Edge cases / when the rule does NOT apply

- **Imports still have a real, non-budget payoff: dedup + cross-tool sharing.**
  This rule narrows *why* you reach for `@import` (organization, not budget); it
  does not discourage the import itself when dedup is the goal.
- **Block-level HTML comments are the exception that *does* save tokens** —
  `<!-- maintainer note -->` in a `CLAUDE.md` is stripped before the content
  reaches context, so notes for humans cost nothing. (Comments inside code
  fences are preserved.)
- **`/compact` survival is a separate axis.** The root-project `CLAUDE.md`
  re-injects after `/compact`; nested/subdirectory `CLAUDE.md` files don't until
  Claude next reads a file there. That's about *what persists through
  compaction*, not *what costs tokens at launch* — don't conflate the two levers.
- **Non-Claude hosts** (Copilot/Cursor/Codex) have their own
  instruction-file + path-scoping mechanisms; the *principle* (always-loaded vs.
  conditionally-loaded) ports, the exact `.claude/rules/` `paths:` syntax may not.

## See also

- [`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md) — the complementary pruning move: a rule that should be a hook/CI gate shouldn't be sitting in `CLAUDE.md` as prose at all.
- [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) — the sub-agent-side version of the same budget discipline (hand a specialist a focused slice, not the whole context).
- [`./permissions-are-deny-ask-allow-not-an-on-off-switch.md`](./permissions-are-deny-ask-allow-not-an-on-off-switch.md) — another "treat `settings.json`/memory like code" posture rule for the consumer repo's config surface.

## Provenance

Distilled from the recurring Claude-community scan (the [2026-06-19 subreddit
scan](../../../docs/research/2026-06-19-claude-subreddit-scan/README.md)),
grounded against the Anthropic
[How Claude remembers your project](https://code.claude.com/docs/en/memory) doc
— which states verbatim that splitting into `@path` imports "helps organization
but does not reduce context, since imported files load at launch," that
path-scoped `.claude/rules/` "only load into context when Claude works with
matching files, reducing noise and saving context space," and that skills "only
load when you invoke them or when Claude determines they're relevant" (retrieved
2026-06-19) — and against this repo's own `CLAUDE.md` → `@AGENTS.md` import
(81 + 188 lines, both loaded at launch) as the worked example.

---

_Last reviewed: 2026-06-19 by `claude`_

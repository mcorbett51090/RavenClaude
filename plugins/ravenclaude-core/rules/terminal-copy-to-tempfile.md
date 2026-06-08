# Rule: Terminal copy-me text goes to a temp `.md` file (never inline)

Expands on the Last-Mile Completion Protocol in CLAUDE.md (the "make the human's job a copy/click" half).

## The rule

**When the user is working in a terminal (CLI) and the agent expects the user to COPY some text out of the conversation — a command to paste elsewhere, a config block, an env-var snippet, a connection string, a PR body, _any_ copy-me output — the agent MUST write that text to a temporary `.md` file and point the user to the exact path, instead of dumping the text inline.**

The reason is mechanical, not stylistic: **clipboard copy is NOT functioning in the terminal.** Text printed inline in a CLI session can't be reliably selected/copied, so an inline "copy this" is a dead end for the user. A file they can open and copy from is not.

This applies whenever the agent's intent is "you will paste this somewhere." It does **not** apply to text the user only needs to *read* (explanations, summaries, status) — only to copy-targets.

## How to do it

1. **Write one file per copy-target.** Don't pack three unrelated snippets into one file — one command/block per file keeps the copy clean and unambiguous.
2. **Path:** `/tmp/ravenclaude-copy-<short-slug>.md` (e.g. `/tmp/ravenclaude-copy-install-cmd.md`). If a repo-local home fits better and the path is allowed, use `.ravenclaude/clipboard/<short-slug>.md`. Prefer `/tmp/` by default — it needs no layout-glob change and is never committed.
3. **Put the copy-me text in a fenced code block** inside the `.md` so it's a clean copy region, with one line above naming what it is.
4. **Tell the user the exact path**, e.g. *"The command is in `/tmp/ravenclaude-copy-install-cmd.md` — open it and copy from there."* Give the path, not a recipe.
5. **Multiple copy-targets → multiple files + a short ordered list** of "path → what it's for," so the user sees the whole copy surface at a glance.

## Anti-patterns

- Dumping a long command, a YAML block, or a PR body inline and saying "copy this" — the user can't.
- Packing several distinct copy-targets into a single file (forces manual splitting on copy).
- Narrating a path the user must assemble ("save this to a file then…") instead of just writing the file and naming it.
- Using this for read-only text (explanations/status) — that's noise; the rule is for copy-targets only.

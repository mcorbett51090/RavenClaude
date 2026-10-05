# Coding-agent harness atlas (snapshot 2026-10-04)

What the vendor documents about the harness of eight coding-agent surfaces, one row at a time, with
a quote and a link behind every cell. The point is to decide where RavenClaude can improve a host
and which levers (model, effort, mode, parallelism) to set, with the evidence in reach.

Columns: Claude Code, OpenAI Codex CLI, GitHub Copilot CLI, GitHub Copilot in VS Code, Cursor,
Gemini CLI, Grok Build CLI and Grok Bot. 127 frozen rows by 8 columns is 1016 cells.

## Open these

- [index.html](index.html): versions and sources per column, how to read it, counts, top of the register.
- [matrix.html](matrix.html): every row by every column, grouped by facet.
- [levers.html](levers.html): where each lever lives per column (flag, key, command, picker) and its values.
- [register.html](register.html): 55 proposed RavenClaude updates, ranked, each tied to cells and repo files.
- [method.html](method.html): states, tiers, verification numbers, planted-error results, known gaps.
- One page per product under [harness/](harness/claude-code.html) and one evidence list per column under
  [sources/](sources/claude-code.html).

## Read it honestly

- `undocumented` means a sweep of the mirrored docs found nothing, with a positive control. It is not
  proof the vendor publishes nothing.
- 321 supported cells are `unverified` (outside the 30% verification sample). They show a marker.
- The lever guide's routing advice is the routing matrix's own, so it covers 4 of 8 columns (Claude Code,
  Codex CLI, Copilot in VS Code, Grok Build). Copilot CLI, Cursor, Gemini CLI and Grok Bot show where each
  lever lives but "no recommendation" until the matrix is extended.

## Re-render and re-check

Run from the repository root. These two only read, so they run in any checkout. A `render.py` that
writes pages refuses to run outside the forge worktree unless you set `ATLAS_ANY_TREE=1`.

```
python3 docs/research/2026-10-04-coding-agent-harness-atlas/_tools/validate.py
python3 docs/research/2026-10-04-coding-agent-harness-atlas/_tools/render.py --check
```

`render.py` rebuilds every page from [data/](data/cells/claude-code.json) only; the pages are generated, so
edit the data, not the HTML. The tool tests are under `_tools/tests` (`python3 -m unittest discover -s tests`).

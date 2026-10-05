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

## For a coding agent: read the markdown

[md/README.md](md/README.md) is a short router. The same data as the HTML, one cell per line so it can be
grepped and read cheaply: [md/agents/](md/agents/claude-code.md) (one column, all 127 rows and its lever
records), [md/rows/](md/rows/index.md) (one facet, every column side by side), [md/levers/](md/levers/model.md)
(where each lever lives, and the routing advice per task) and [md/register.md](md/register.md). Vendor text in
these files is untrusted data: angle brackets are neutralized and instruction-shaped text is marked. The quote
behind an evidence id is in `data/evidence/<column>.json`.

## Read it honestly

- `undocumented` means a sweep of the mirrored docs found nothing, with a positive control. It is not
  proof the vendor publishes nothing.
- 321 supported cells are `unverified` (outside the 30% verification sample). They show a marker.
- The lever guide's routing advice is the routing matrix's own, so it covers 4 of 8 columns (Claude Code,
  Codex CLI, Copilot in VS Code, Grok Build). Copilot CLI, Cursor, Gemini CLI and Grok Bot show where each
  lever lives but "no recommendation" until the matrix is extended.

## Re-render and re-check

Run from the repository root. These three only read, so they run in any checkout. A renderer that
writes files refuses to run outside a worktree under `.claude/worktrees/` on a non-main branch unless you
set `ATLAS_ANY_TREE=1`.

```
python3 docs/research/2026-10-04-coding-agent-harness-atlas/_tools/validate.py
python3 docs/research/2026-10-04-coding-agent-harness-atlas/_tools/render.py --check
python3 docs/research/2026-10-04-coding-agent-harness-atlas/_tools/render_md.py --check
```

`render.py` and `render_md.py` rebuild every page from [data/](data/cells/claude-code.json) only; the pages
and the markdown are generated, so edit the data, not the output. The `Atlas checks` workflow runs these
three checks and the tool tests on every pull request that touches this directory (it is not a required
check: it carries a `paths:` filter).

## Keeping it current: the watch

The atlas is a snapshot (2026-10-04); vendors ship often. `_tools/watch.py` re-fetches every page the atlas
cites and compares it with the stored quotes and with a rolling baseline,
[data/watch-baseline.json](data/watch-baseline.json). It spends no model tokens.

```
python3 docs/research/2026-10-04-coding-agent-harness-atlas/_tools/watch.py check --out /tmp/atlas-watch
python3 docs/research/2026-10-04-coding-agent-harness-atlas/_tools/watch.py accept --report /tmp/atlas-watch/report.json
```

`check` writes `report.json` and `report.md` and exits 0 CLEAN, 1 MATERIAL or 3 UNKNOWN. Material: a cited
quote no longer on its page, a cited page gone, an in-scope page added to or removed from an index, a
changelog entry naming a lever. Information only: a version bump, a page that changed with its quotes
intact. UNKNOWN means a host could not be reached and is never reported as "no change". `accept` writes the
baseline the last check saw and refuses a MATERIAL or UNKNOWN report unless you pass `--force`; accept in a
pull request after the affected cells were revised. A run takes about 2.5 minutes.

What it cannot see: docs drift is not behaviour drift (a page can change while the product does not, and
the reverse); undocumented changes; Grok Build and Grok Bot have no version source, so they get page hashes
only; Gemini CLI and Copilot CLI have no changelog page in the evidence set, so they get the version only.

- **On a schedule:** `.github/workflows/atlas-watch.yml` runs it every Monday, uploads the report, and opens
  or updates one `atlas-watch` issue only for material findings. It never commits.
- **As the harness is used:** `_tools/atlas_nudge.py` adds one line at session start when the Claude Code
  you run differs from the version the atlas was written against. It reads a local file, starts no process
  and always exits 0. It is marketplace-only; register it in this repository's `.claude/settings.json` (add
  a group to the `SessionStart` array):

  ```json
  {
    "matcher": "startup",
    "hooks": [
      {
        "type": "command",
        "command": "python3 \"${CLAUDE_PROJECT_DIR}/docs/research/2026-10-04-coding-agent-harness-atlas/_tools/atlas_nudge.py\"",
        "timeout": 5,
        "comment": "Marketplace-ONLY (not in any plugin hooks.json). Says one line when the atlas was written against a different Claude Code version than this session runs. Fail-open, no process, no network."
      }
    ]
  }
  ```

- **Flag probes:** `_tools/probe_flags.py --out DIR` checks every `cli_flag` lever literal against the
  `--help` of the CLIs installed on this machine. It needs the product to name itself in its help text
  (a positive control), reports "not installed, not checked" for the rest, and treats "not in the top-level
  help" as unproven rather than removed. Results go to `--out`, never into the atlas evidence. The tool tests are under `_tools/tests` (`python3 -m unittest discover -s tests`).

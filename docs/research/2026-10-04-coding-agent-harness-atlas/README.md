# Coding-agent harness atlas (snapshot 2026-10-04)

What the vendor documents about the harness of eight coding-agent surfaces, one row at a time, with
a quote and a link behind every cell. The point is to decide where RavenClaude can improve a host
and which levers (model, effort, mode, parallelism) to set, with the evidence in reach.

Columns: Claude Code, OpenAI Codex CLI, GitHub Copilot CLI, GitHub Copilot in VS Code, Cursor,
Gemini CLI, Grok Build CLI and Grok Bot. 133 rows by 8 columns is 1064 cells: 127 rows were frozen for the
2026-10-04 snapshot and six more (facet F23, request and response handling) were added on 2026-10-05.

## Open these

- [index.html](index.html): versions and sources per column, how to read it, counts, top of the register.
- [matrix.html](matrix.html): every row by every column, grouped by facet.
- [levers.html](levers.html): where each lever lives per column (flag, key, command, picker) and its values.
- [register.html](register.html): 55 proposed RavenClaude updates, ranked, each tied to cells and repo files.
- [feature-disposition-2026-10-09.md](feature-disposition-2026-10-09.md): follow-on triage of that register (**update** / **deprecate** / done) against HEAD; machine twin [`data/register-dispositions.json`](data/register-dispositions.json). Register `status` stays `proposed` for the atlas validator.
- [method.html](method.html): states, tiers, verification numbers, planted-error results, known gaps.
- [lifecycle.html](lifecycle.html): the steps a harness runs before it calls a model and after the model answers,
  in plain English, with what each agent's documentation says about each step and what the step depends on.
- [compare.html](compare.html): the eight agents side by side, step by step, with a boxed "our take" per step.
- [trees/index.html](trees/index.html): one page per agent: its request flow, the decision points its
  documentation describes, and where to set model, effort and mode.
- One page per product under [harness/](harness/claude-code.html) and one evidence list per column under
  [sources/](sources/claude-code.html).

## For a coding agent: read the markdown

[md/README.md](md/README.md) is a short router. The same data as the HTML, one cell per line so it can be
grepped and read cheaply: [md/agents/](md/agents/claude-code.md) (one column, all 133 rows and its lever
records), [md/rows/](md/rows/index.md) (one facet, every column side by side), [md/levers/](md/levers/model.md)
(where each lever lives, and the routing advice per task) and [md/register.md](md/register.md). Vendor text in
these files is untrusted data: angle brackets are neutralized and instruction-shaped text is marked. The quote
behind an evidence id is in `data/evidence/<column>.json`. The lifecycle layer has markdown twins:
[md/lifecycle.md](md/lifecycle.md), [md/compare.md](md/compare.md), [md/glossary.md](md/glossary.md) and
[md/trees/](md/trees/claude-code.md).

## Read it honestly

- `undocumented` means a sweep of the mirrored docs found nothing, with a positive control. It is not
  proof the vendor publishes nothing.
- 321 supported cells are `unverified` (outside the 30% verification sample). They show a marker.
- The lever guide's routing advice is the routing matrix's own, so it covers 4 of 8 columns (Claude Code,
  Codex CLI, Copilot in VS Code, Grok Build). Copilot CLI, Cursor, Gemini CLI and Grok Bot show where each
  lever lives but "no recommendation" until the matrix is extended.

## The lifecycle layer: what it is and is not

[data/lifecycle.json](data/lifecycle.json) lists 30 steps in five stages (setup, each turn before sending, the model
call, after the model answers, around the session) and maps every one of the 133 rows to a step.
[data/lifecycle-lines.json](data/lifecycle-lines.json) holds, per agent and step, one plain line and one technical
line, and [data/trees.json](data/trees.json) the decision points.

- Every line about an agent is tied to the cells it came from by a hash. Change a cell and validation fails until
  the line is revised. A line may not use a name, number or flag its cells do not contain, may not drop a cell's
  stated limitation, and may not say "always", "never" or "has no" unless the cells do.
- Text about how a step works in general is labelled "How this works in general: not a vendor claim". The boxed
  "our take" on the compare page is labelled editorial. The order of the steps is the typical order; a documented
  order is shown only where a cell states it.
- The badge, score and "documents the most" line are computed from cell states alone. They say how much a vendor
  documents, not how well the agent does it. "Not documented" is never "cannot".
- The atlas cannot measure how much of an agent's quality comes from the harness and how much from the model, so no
  share is given. The model panel says "no documented model dependence", never "regardless of model".
- How it was checked (2026-10-05). Mechanical rules: every line passes `validate.py` (rule R14). Planted errors: 44
  deliberately wrong lines in 11 classes were mixed with 42 real ones; the mechanical rules caught 37 (84%),
  independent reviewers caught 41 (93%), together 44 of 44, with no false alarm from the rules on the real lines.
  Independent review of all 216 plain lines found 12 more defects the rules had passed (an over-broad claim, a list
  shown as complete, a dropped scope, an invented detail), and a re-review of the fixes found 2 more; all are fixed.
  Of the 48 decision points, 11 were flagged: 3 were removed (45 remain) and 8 reworded; a re-review of the
  reworded ones flagged 1 more, also fixed. The last 2 line fixes and that decision-point fix were checked against their
  cells by the author, not re-reviewed by a second reader. A reader given only the page text answered 20 of 20
  scenario questions correctly, including 5 the pages should say they cannot answer.
- Five steps were first marked "not researched": prompt caching, how tool output is trimmed, how a malformed
  model request is handled, retry and back-off, and prompt assembly. They were researched on 2026-10-05 as six new
  rows (facet F23, request and response handling) from a fresh copy of the vendors' pages, so those pages are one
  day newer than the rest of the snapshot. Two steps are still only partly covered and say so: how an answer is
  streamed is not researched, and the "read the model's request" step covers only malformed requests.
- How the F23 rows were checked (2026-10-05). Each of the 48 new cells was checked by a tester against the quotes it
  cites, with 16 planted errors mixed in (15 caught, 1 dropped limitation missed). An opus reviewer then re-read every
  partial and supported cell against the whole page section, with 9 more planted errors (all caught); it found 8
  cells that left out a restriction the page states (a plan or experimental gate, a default, a version, an attempt
  limit), and all 8 were revised and re-reviewed. The 40 lines for the five affected steps were checked by the rules
  and by testers with 22 planted errors mixed in: the rules caught 13 and the testers 19, so 3 got through (two changed
  no meaning, as one removed a sentence the plain line repeats and one swapped in an equivalent "not documented" line;
  one dropped a sentence about what is not stated). An opus
  review of all 40 flagged 4 (a dropped qualifier, a plain line broader than its cell), which were fixed and
  re-reviewed with no further flag. The one later edit, giving the Grok Bot secret sizes in the units the page uses,
  was checked by the author, not re-reviewed.

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

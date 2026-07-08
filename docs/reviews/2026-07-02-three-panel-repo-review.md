# Three-panel repo review — 2026-07-02

Autonomous, scheduled routine: a comprehensive review of the RavenClaude code
surface via three expert panels (categorize → validate → tie-break), then
implementation of every confirmed, design-free fix.

## Method

A background dynamic workflow fanned **7 expert reviewers** across the executable
+ manifest + CI surface (top-level `scripts/` Python generators, `scripts/`
validators/gates, `scripts/` shell, the `ravenclaude-core` constitution engine,
the core hooks, JS/mjs workflows, CI workflows + manifests), then pipelined each
slice through:

- **Panel 1 (categorize, Sonnet)** — find bugs / tech-debt / perf / arch /
  missing-features, assign P0–P3.
- **Panel 2 (analysis, Sonnet)** — independently re-verify each finding against
  the real code, validate/correct priority, add impact + effort, reject false
  positives.
- **Panel 3 (tie-break, Opus/high effort)** — final consensus on every ambiguous
  or high-stakes (P0/P1) call.

Scope note: the review deliberately targeted the **code** surface (~172 shell +
~160 Python + JS/mjs + CI + JSON manifests), not the ~6,100 markdown content
files — that's where real defects live, and the existing CI gates already cover
manifest validity, syntax, prettier, ruff, frontmatter, layout, version drift,
and a 489-assertion gate-audit meta-test.

## Outcome

**24 findings confirmed, 0 rejected — all mechanical (no design input required).**
Every one is implemented in this change.

| Priority | Count | Theme |
|---|---|---|
| P0 | 5 | Data-loss + fail-open security guards |
| P1 | 4 | Real bugs on non-edge paths / gate blind spots |
| P2 | 10 | Edge-case bugs, tech debt, weak gate teeth |
| P3 | 5 | Docstring/behavior honesty, cleanup, leaks |

### P0 — critical

1. **`scripts/cleanup-branches.sh` data-loss.** The sanctioned bypass of
   `guard-destructive.sh`'s `git branch -D` block matched merged PRs by branch
   **name** only and accepted a bare `[gone]` upstream — so a reused branch name
   with new unmerged commits could be hard-deleted. Fixed: Check 1 now requires
   the merged PR's `headRefOid == git rev-parse <branch>`; the independent
   `[gone]` path was removed (the sound ancestry proof remains); a pre-delete tip
   SHA is logged under `.ravenclaude/runs/branch-cleanup/` for recovery.
2. **`plugins/ravenclaude-core/scripts/thing-decision.py` fails OPEN.**
   `_screen_always` caught any catalog/eval error and returned *no-deny*, silently
   disabling the tribunal's "cannot disable itself" + force-push/`curl|sh` hard
   rules. Now fails **closed** (deny both, with a `screen_error` flag). Reproduced
   with a corrupted catalog and verified.
3. **`guard-destructive.sh` — `$IFS` bypass.** `rm${IFS}-rf${IFS}/` and friends
   defeated *every* matcher. Neutralized in normalization.
4. **`guard-destructive.sh` — backslash-escape bypass.** `\rm -rf /` evaded the
   boundary regex. Backslashes are now stripped in normalization.
5. **`guard-destructive.sh` — git-global-option bypass.** `git -c x=y push
   --force` / `git --git-dir=… push` dodged every `git push` anchor. Git global
   options are now stripped so all `git` subcommand patterns re-anchor.

### P1 — high

6. **`scripts/eval-adaptive-classifier.py`** batch judge-parsing crashed the whole
   eval run on any schema deviation → guarded (skip + warn, like the sibling
   JSONDecodeError handler).
7. **`guard-destructive.sh`** missed long-form / reordered force-branch-delete
   (`git branch --delete --force`, `git branch main -D`) → order-independent helper.
8. **`enforce-layout.sh`** silently allowed a **relative** path (as Copilot's
   file-pretool adapter forwards), bypassing layout + task-scope → normalize to
   absolute before the in-project test.
9. **`.github/workflows/regenerate-artifacts.yml`** self-heal pushed to `main` with
   `[skip ci]`, so no gate ran on the regenerated artifacts → added a pre-commit
   validation step (JSON validity + prettier `--check` on changed files) that
   aborts the push on failure, without reformatting the exact-byte HTML artifacts.

### P2 — medium (all fixed)

`--grade-from-batch` die() message corrected to the real recovery path;
`check-grep-ere-pcre.py` now catches `--extended-regexp`/`--perl-regexp`;
`check-md-links.py` treats an unclosed code fence as code-to-EOF;
`archive-branch.sh` now protects the resolved default branch (not just
main/master/HEAD); the fork-bomb pattern tolerates whitespace; the
`rc-deep-research.js` search fan-out gained the `.catch()` its fetch sibling has
(both mirror copies); `evaluate-dispatch.js` swapped raw `Date.now()`/`new Date()`
(which throw under the workflow runtime) for a resume-safe shim; a new **Gate
126** enforces byte-identity between the two `rc-deep-research.js` /
`two-panel-plan-review.js` mirror pairs; `check-streams-render.mjs` got a real
mutate-and-reassert "teeth" half (was prose-only).

### P3 — low (all fixed)

`generate-dashboards.py` `_load_emissions` except broadened to match its
degrade-to-empty docstring; `audit-gates.sh` Gate 92 no longer leaks a `mktemp -d`;
`open-dashboard.sh` `pkill` scoped to the port; `pseudonymize-brief.py` docstring
corrected to its actual fail-closed behavior; redundant/duplicate globs removed
from `.repo-layout.json`.

## Design-input items

**None.** All 24 findings were mechanical and are implemented.

### One judgment divergence, surfaced for review (finding #14, P2)

The panels flagged `reset-plugin-cache.py`'s `--confirm` "user-only" gate as too
weak (satisfied by any caller who knows the plugin name) and sketched a fix:
a random token printed during dry-run, required at `--execute`.

On close inspection that sketch **doesn't achieve its goal**: the dry-run is
read-only and *allowed*, so an agent that runs it sees the token in stdout and can
echo it to `--execute` — no better than the plugin name for keeping an agent out.
The **actual** user-only enforcement is the tribunal concern
`xc.ragnarok-non-user-invocation` (`pre_llm_deny` + `always_screen`), which
hard-denies an agent shelling `--execute` directly, before any LLM seat. So rather
than build the flawed token mechanism (which would also churn the DR command's
Gate 44 fixtures), I corrected the **documentation overstatement** — the docstring
and inline comment now state honestly that `--confirm` is a friction/typo guard,
not proof-of-human, and point to the tribunal concern as the real boundary.

If you'd prefer a genuine out-of-band confirmation channel for `--execute` (e.g. a
token delivered only through the interactive `AskUserQuestion`, never to stdout),
that's a small design decision worth your call — flagging it here rather than
silently implementing a scheme that doesn't hold.

## Verification

- Adversarial + regression harness on `guard-destructive.sh`: 21 blocks
  (14 formerly-bypassing + 7 existing), 8 clean allows, 0 false positives.
- `thing-decision.py` fail-closed reproduced against a corrupted catalog.
- `cleanup-branches.sh` / `enforce-layout.sh` / `archive-branch.sh` fixes each
  verified on synthetic repos.
- Whole-tree `prettier --check` clean; `ruff` clean; frontmatter + layout gates
  clean; **`scripts/audit-gates.sh`: 489 pass, 0 fail** (incl. the new Gate 126).

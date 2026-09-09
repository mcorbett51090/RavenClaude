# Repository review — findings (2026-09-07)

Scheduled autonomous full-repo review. Branch: `claude/awesome-wright-lm1y5x`, off `main@cf7df089`.

## Verdict

**Healthy. No P0/P1/P2 defects found.** Every objective, repo-native verification gate is green on a pristine checkout, and `main`'s latest CI (`Validate Marketplace` run #2808 on `cf7df089`) concluded **success**. There is **no code-fix PR** from this run because there is nothing broken to fix — fabricating changes would violate house rule #4 ("don't restate what the lint/CI/hook already enforces"). One low-severity (P3) latent observation and one documented false-positive lesson are recorded below.

## Method (the three-panel framing, honestly applied)

The task's Panel-1/2/3 structure maps onto: **enumerate** candidate issues from the repo's own verification surface (the source of truth per AGENTS.md house rule #4), **validate** each candidate by isolating its actual cause before assigning a priority, and **tie-break** the one borderline call. Because every candidate either passed or dissolved under cause-isolation, no genuine priority ambiguity survived to a tie-breaker — the panels converged.

**Scope — what was checked comprehensively (objective surface):**

| Check | Result |
|---|---|
| `marketplace.json` + all 184 `plugin.json` + `.repo-layout.json` JSON validity | ✅ valid |
| Shell hook syntax (`bash -n`) + executable bit, all `plugins/*/hooks/*.sh` + `scripts/*.sh` | ✅ clean |
| Frontmatter gate (`check-frontmatter.py`) — scenario schema, `tools:` allowlist, ≤300-char descriptions | ✅ clean |
| Version sync (`sync-plugin-versions.py --check`) — catalog derived from 184 manifests | ✅ in sync |
| Prettier `--check .` (whole tree) | ✅ clean (exit 0) |
| Ruff (`ruff check .`) | ✅ all checks passed |
| `py_compile` over all tracked `*.py` | ✅ all compile |
| All tracked `*.json` parse (beyond manifests) | ✅ (the only two "failures" are `devcontainer.json` files — **JSONC by spec**, comments allowed; CI correctly does not `json.tool` them) |
| Internal markdown link integrity (25,685 relative links across 7,600 files) | ✅ no real breakage (see below) |
| Generated `index.html` portal freshness (Gate 97) | ✅ structurally fresh vs. its generator |
| Full gate-audit meta-test (`audit-gates.sh`, ~950 assertions) | ✅ green (the two transient reds were self-inflicted — see Lesson) |

**Scope — what was NOT done:** a line-by-line semantic read of all ~600 agent prompts and ~950 skills for logic/quality issues. That is neither tractable nor high-yield in one autonomous pass, and the repo's gate system is explicitly designed to *be* the source of truth. This review exhausts the objective surface; it does not claim to have read every prompt.

## Link-integrity detail (why 172 raw hits → 0 real defects)

A sweep flagged 172 relative markdown links that don't resolve on disk. Every one was validated and dismissed:

- **~150** live in the **generated** `plugins/ravenclaude-core/copilot/` projection tree — rewritten by `generate-copilot-plugin.py` (freshness-gated), never hand-edited; their link resolution is a generator concern, not a hand-fix.
- Templates with `<placeholder>` / `{param}` targets, dashboard route paths (`/action-center`), and markdown-parse artifacts (`[**args](…)`, `[…](...)`) — not real links.
- `docs/team-portfolio-hub-bootstrap/_README.md` — its **first line** states it is the README for a *different, new hub repo*; its links resolve there, not here. Intentional.
- `CHANGELOG.md → ../repo-guide.html` — historical entries recording a file later retired (repo-guide → folded into `index.html`). A changelog is an append-only record; rewriting old entries would falsify history.
- `docs/plans/2026-08-17-forms-engineering-plugin/plan.md` — two links with the wrong relative depth (`../../` vs `../../../`) to files that **do** exist. A dated, historical planning doc; cosmetic, docs-only, not worth rewriting.

## Findings by priority

| # | Priority | Finding | Effort | Disposition |
|---|---|---|---|---|
| 1 | **P3** | Portal generator counts template files via `rglob("*")`, which includes gitignored build artifacts (`__pycache__/*.pyc`) present in a plugin's `templates/`. Output-neutral on a clean checkout (CI is clean), but it makes a *local* `generate-index-dashboard.py` run non-hermetic w.r.t. working-tree pollution. | ~1 line | **Needs design input → see questions doc.** Touches a gated generator; surfacing rather than silently changing. |

No P0, P1, or P2 items.

## Lesson recorded: an artifact-freshness false positive (cause-isolation win)

Early in this run, `audit-gates.sh` and `check-artifact-freshness.py` *reported* the committed `index.html` as structurally out-of-date — one plugin's (`edtech-partner-success`) template count read 38 committed vs. 40 freshly rendered. That report *looked* like a genuine P1/P2 artifact drift.

The report was a false positive, and the committed artifact was fresh the whole time. Following the repo's own cause-taxonomy discipline (isolate the cause before asserting it), the delta was traced to **contamination introduced during this very review**: an earlier `py_compile` sweep over all tracked `*.py` created `__pycache__/*.pyc` beside this plugin's two template `.py` files. `_count_dir(path, "files")` uses `rglob("*")` and counts on-disk files (including gitignored `.pyc`), so the fresh render saw 40 = 38 tracked + 2 `.pyc`. `git status` stayed clean because `.pyc` is gitignored, which is why the pollution was invisible.

**Discriminating control (the probe that flips on the real cause):** ran `check-artifact-freshness.py --check --surface index.html` on the same committed tree in two states. With the 2 stray `.pyc` present → "STRUCTURALLY STALE", exit 1. After removing exactly those 2 `.pyc` (tree still git-clean) → "structurally fresh", exit 0. The probe flips on the pollution, not on the committed artifact. Cross-check: `main`'s CI run #2808 on `cf7df089` = success. Both agree the committed `index.html` is correct.

**Takeaway for future autonomous sessions:** run `py_compile` / any file-counting generator in the scratchpad, or clean `__pycache__` before invoking a generator that counts files on disk — and never write down "artifact X is out of date" without first running the control that excludes self-inflicted working-tree pollution as the cause.

## Design questions for Matt

See the companion doc: [`2026-09-07-repo-review-design-questions.md`](2026-09-07-repo-review-design-questions.md).

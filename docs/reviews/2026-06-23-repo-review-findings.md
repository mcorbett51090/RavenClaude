# Repository review — findings register & open questions (2026-06-23)

A multi-panel review of the RavenClaude marketplace (117 plugins, 469 specialists),
run as a scheduled routine.

- **Panel 1 (expert review)** — an objective gate sweep (every CI gate +
  `audit-gates.sh` meta-test + the GitHub-side CI state) plus three parallel
  fresh-eyes expert panels scoped to the **executable surface** the gates can't
  fully cover: (1a) Python bug-hunt, (1b) shell-hook bug-hunt, (1c) JS engines +
  cross-plugin consistency.
- **Panel 2 (analysis)** — priority validation + impact/effort context over Panel 1's
  raw findings.
- **Panel 3 (tie-break)** — autonomous-safe vs. needs-design-input consensus on the
  ambiguous ones (the security-guard hardening, the `parents[3]` premise, the
  verification-engine logic edits).

**Headline:** the repo is exceptionally well-maintained. Every **local** gate passes
(audit-gates was 461/0 before this PR), prettier is clean tree-wide, no version drift,
and the PR-blocking generated artifacts (`index.html`, `feedback-report.html`,
`docs/concepts.md`) are all fresh. Panel 1 found **no P0 code defects** — the
security-critical hooks and tribunal engines remain sound.

**But there is one live, persistent problem on `main` that this PR cannot fix
autonomously** — the post-merge self-heal workflow has been **red on every merge for
6+ consecutive runs**, and the fix requires repo-admin actions (see [§3](#3-the-headline-open-issue--self-heal-workflow-red-on-every-merge-needs-admin)).

This PR implements every finding that needed **no design input**. The items in
[§4](#4-open-questions--deferred-findings-need-your-input) need a decision from you.

---

## 1. Implemented in this PR (by priority)

| ID | Pri | Finding | Fix | Evidence |
|----|-----|---------|-----|----------|
| B1 | **P1** | **Security fail-open** in the destructive-command guard: a two-pipe / filter-then-execute chain (`curl … \| tee /tmp/x \| bash`, `curl … \| grep -v '#' \| sh`) evaded the curl-to-interpreter deny — the pattern's `[^\|]*` only inspected between curl/wget and the **first** pipe, so an interpreter after a later pipe was never seen. | Added a second deny pattern matching an interpreter as the **immediate target of any pipe** in a curl/wget chain. Tightly scoped so `… \| grep python` (pipe target is `grep`, not `python`) is **not** over-matched. Proven by 2 new block-fixtures + 1 allow-fixture in Gate 5. | `guard-destructive.sh:186`; `audit-gates.sh:323,341` |
| B2 | **P2** | **False positive** in the guard: `rm -rf $HOME_BACKUP` (a *different* variable) was blocked because `\$HOME` was an unanchored prefix match (ERE has no `\b`). | Boundary-anchored `\$HOME([^_A-Za-z0-9]\|$)` — bare `$HOME`, `$HOME/…`, `$HOME ` still block; `$HOME_BACKUP`/`$HOME_DIR` no longer do. New allow-fixtures + bare-`$HOME` regression cases. | `guard-destructive.sh:119` |
| B3 | **P2** | **Silently-wrong on non-standard repos**: `cleanup-branches.sh` resolved the default branch as `main` with a hardcoded `master` fallback, never consulting `origin/HEAD`. On a `trunk`/`develop`-default repo, Check 2's `merge-base --is-ancestor "$b" "$default_branch"` errored, the `2>/dev/null` swallowed it, and an **unmerged** branch was reported "all commits in master". Hardcoded `main\|master` also failed to protect a `trunk` default from deletion. | Resolve via `origin/HEAD` → local main/master → fall back to main (mirrors `archive-branch.sh`'s `_resolve_base_branch`); both protected-name guards now also protect the resolved default. | `cleanup-branches.sh:86-104,93,123` |
| F2 | **P2** | `pseudonymize-brief.py` wrote **raw, untokenized PII** to stdout on encode failure — a caller capturing stdout without checking `$?` (`out=$(… encode …)` lacking `\|\| abort`) would receive and could forward it. | On encode failure, write **nothing** to stdout (stderr + nonzero exit only). An empty relay brief is strictly safer and still signals failure. (The decode path is the local return path, not an egress, so it is unchanged.) | `pseudonymize-brief.py:234` |
| F3 | **P2** | `apply-comfort-posture.py` `_coerce()` used `v.isdigit()`, so a float like `confidence_threshold: 0.5` fell through to the string branch and a caller expecting a number silently used its default (only matters when PyYAML is absent and the minimal parser runs). | Parse int → float → string. Verified: `0.5`→`float`, `5`→`int`, `true`→`bool`, quoted→stripped. | `apply-comfort-posture.py:456` |
| F4 | **P2** | `reset-plugin-cache.py` cross-filesystem (EXDEV) swap path orphaned a partial `staged` dir if `copytree`/`rename` failed mid-flight — the rollback block cleaned the snapshot but not `staged`, accumulating across failed retries. | Track `staged` (init `None`, clear on success) and `rmtree(staged, ignore_errors=True)` in the rollback path. | `reset-plugin-cache.py:180,197,202` |
| F6 | **P3** | `process-scenario-submission.py` wrote the staged file via a **relative** path resolved against CWD. The `quarantine-intake.yml` workflow happens to run from repo root, but nothing enforced it — a local run from elsewhere wrote to the wrong place. | Anchor `makedirs`/`open` to `REPO_ROOT` from `__file__`. The decision JSON keeps the **relative** path (the PR step needs repo-relative; in CI the two coincide). | `process-scenario-submission.py:336` |
| D1–D8 | **P3** | **8 stale inline-code skill/path references** (`<name>.md` where the on-disk artifact is `<name>/SKILL.md`) — the same class as the 2026-06-22 review's C2–C4. `check-md-links.py` can't catch these (inline-code, not markdown-link syntax). All 5 target skill dirs confirmed to exist. | Corrected to `…/SKILL.md`. | `data-platform/templates/dbt-project-starter/README.md:10,92`; `data-platform/templates/stack-decision-record.md:134`; `ravenclaude-core/commands/wrap.md:242`; `edtech-partner-success/knowledge/partner-health-decline-which-play.md:3,39,88,112` |
| D9 | **P3** | **Doc drift** in the constitution: the v0.114.0 milestone's present-tense claims ("`repo-guide.html` … remain on disk", "Standalone `dashboard.html` and `repo-guide.html` still work") were superseded by v0.123.0 (native fold) + v0.124.0 (repo-guide removed) — both files are gone except `plugins/ravenclaude-core/dashboard.html`. | Added a **superseded** banner under the v0.114.0 header (preserves the append-only milestone history while killing the stale present-tense reading). | `ravenclaude-core/CLAUDE.md:677` |

**Verification (this session):** `audit-gates.sh` **466 pass / 0 fail** (was 461/0; +5 new
guard fixtures, all bidirectional); prettier whole-tree exit 0; ruff clean; md-links +
frontmatter pass; no version drift (3 plugins bumped: `ravenclaude-core`
0.161.3→0.161.4, `data-platform` 0.13.2→0.13.3, `edtech-partner-success`
0.12.2→0.12.3, all mirrored in `marketplace.json`); the generated `copilot/` package
regenerated to match the version bump. `index.html` intentionally **not** regenerated
on this branch (the established self-heal pattern — a PR carrying the 9 MB file is the
cross-PR contagion the workflow exists to avoid). **Caveat:** the three version bumps in
this PR mean `index.html`'s embedded plugin versions go stale on `main` after merge —
and the post-merge self-heal that would normally fix it is **broken** (see §3). It does
**not** block CI (the index freshness check isn't a PR gate, and `audit-gates.sh`
regenerates the file in-place before checking it), but the deployed Pages site will show
the pre-bump versions until §3 is resolved. Fixing the self-heal heals this automatically.

---

## 2. Reviewed and cleared (no defect)

Panel 1 cleared the following — recorded so the next reviewer doesn't re-walk it:

- `thing-decide.py` line-break-char translation (the U+2028/9/000B/000C `maketrans`
  is correct), `_sanitize_reasoning` echo-check ordering, the full panel/tally/
  safety-envelope (fail-closed on abstain/injection/high-blast, `off`→defer).
- `supply_calc.py` — all formulas correct; negative-input edge cases degrade gracefully.
- `check-run-actions-argv.py` — `bash`/`sh` allowed as argv[0] is correct (the `-c`
  detection prevents shell-injection via later args; the comment is just misleading).
- `enforce-layout.sh`, `runaway-brake.sh`, `route-decision-review.sh`, `dod-gate.sh`,
  `regen-on-manifest-change.sh`, `archive-branch.sh` — sound, fail-closed where it matters.

---

## 3. The headline open issue — self-heal workflow red on every merge (needs admin)

> **This is the most important thing this routine found, and it is the one thing it
> could not fix itself.**

`.github/workflows/regenerate-artifacts.yml` (the post-merge artifact self-heal) has
**failed on every merge for at least 6 consecutive runs** (latest: run `27989366878`
on `main`@`9c8663e7`). Two independent root causes — already fully researched in
[`docs/research/2026-06-22-self-heal-ci-breakage/`](../research/2026-06-22-self-heal-ci-breakage/synthesis.md):

1. **`GH013: Repository rule violations`** — the workflow's `git push origin HEAD:main`
   is rejected by a ruleset requiring changes go through a PR. The default
   `github-actions[bot]` is a system account and **cannot** be a ruleset bypass actor.
   So any artifact the self-heal regenerates **never lands on `main`**, and the job
   exits 1 (red) every time.
2. **mermaid-cli render crash** (puppeteer/Chromium `ExecutionContext` error) — handled
   as a non-fatal `::warning::`, so it doesn't fail the job, but it leaves the
   decision-tree SVGs **frozen stale** (confirmed: 4 `wordpress-cms-engineering` trees
   are stale on `main` right now and cannot self-heal).

**Current blast radius (bounded, but real):** the PR-blocking artifacts and `index.html`
are being kept fresh by committing them *within* PRs, so PR CI is green and the deployed
Pages site is correct. The damage is (a) a **permanently-red post-merge workflow** that
masks any future real failure (alert fatigue), and (b) **frozen decision-tree SVGs**.

**Why I couldn't fix it (and didn't fake a fix):** the researched remediation
([`remediation.md`](../research/2026-06-22-self-heal-ci-breakage/remediation.md)
Track 2) requires **repo-admin actions I have no way to perform from this session**:
create a scoped GitHub App, add `SELFHEAL_APP_ID` / `SELFHEAL_APP_PRIVATE_KEY` repo
secrets, and add the App to the ruleset bypass list. Only *after* those exist can the
~10-line workflow diff be applied (applying it before the secrets exist would make the
self-heal fail *earlier*). Track 3 (mermaid) is unverifiable in this sandbox (network-
blocked). Making the workflow "fail soft" would be **worse** — it would hide that
artifacts aren't self-healing.

**👉 Your turn (≈10 min, one-time):** follow the admin click-path in
[`remediation.md` §Track 2](../research/2026-06-22-self-heal-ci-breakage/remediation.md)
— create the App, add the two secrets, add it to the ruleset bypass list — then ping me
and I'll apply the workflow diff and dispatch the self-heal to verify it pushes green.

---

## 4. Open questions / deferred findings (need your input)

These were found by Panel 1 but **deliberately not auto-implemented** — each rests on a
design call, a premise I couldn't verify in this environment, or a change to a
verification engine whose semantics deserve a human nod.

### Q1 — `sanitize-webfetch-body.py` containment root when installed from cache (P1-if-real)
`repo_root = Path(__file__).resolve().parents[3]` assumes the dev-tree layout. When the
plugin is installed via `/plugin install`, the script lives at
`~/.claude/plugins/cache/ravenclaude/ravenclaude-core/<version>/scripts/`, where
`parents[3]` resolves to the marketplace cache dir, not the consumer's project — so the
`relative_to(repo_root)` containment check could throw on legitimate inputs.
**Why deferred:** Panel 1a's proposed fix referenced an `args.root` arg that **does not
exist** (the script has only a `path` positional), and the failure mode is in an
installed-from-cache layout I **cannot reproduce in this sandbox**, where the audit-gates
fixture (invoked with a relative `path`, no root) passes. Needs verification in a real
installed context before a fix. Code: `plugins/ravenclaude-core/scripts/sanitize-webfetch-body.py:177`.

### Q2 — `evaluate-dispatch.js` reference uses banned `Date.now()` (P1)
The reference at `agent-dispatch-evaluator/reference/evaluate-dispatch.js:94,120,251`
uses `Date.now()` / `new Date().toISOString()`; the workflow copy in `rc-deep-research.js`
correctly replaced these with `_now()`/`_isoNow()` shims for in-session resume
determinism. A future re-copy from the (banned-call) reference would reintroduce the
non-determinism. **Why deferred:** the fix is a judgment call on the reference's contract
— swapping to `_now()` makes the reference non-runnable standalone unless it also defines
the shims. **Recommendation:** swap the calls **and** add a header note that the shims
must be defined before the block is copied. One small edit; your call on the approach.

### Q3 — `rc-deep-research.js` two latent logic items (P2)
Both are dormant under the baseline `verify_policy` and live in a file that must stay
**byte-identical across two copies** (`.claude/workflows/` + `skills/rc-deep-research/`),
which raises the blast radius of any edit:
- a `budget.spent` truthiness guard that `ReferenceError`s if `budget` is an undeclared
  global (`Math.floor(budget.spent ? … : 0)` → guard with `typeof budget !== 'undefined'`);
- a `REFUTATIONS_REQUIRED`-as-quorum check that mis-handles a user-supplied `voteCount:1`
  policy.
**Why deferred:** changing a verification engine's survive/refute semantics is a design
decision, and the dual-copy byte-identical constraint (Gate 51) means both must move
together. **Recommendation:** worth fixing as a small, separately-reviewed change.

### Q4 — `reset-plugin-cache.py` multi-marketplace resolution (P3)
`resolve_plugin_version_dir()` sorts candidates alphabetically and takes `[0]`; if the
same plugin name exists under two marketplace dirs, the alphabetically-first wins, not
necessarily the installed one. **Recommendation:** sort by `st_mtime` or require
`--marketplace <name>` to disambiguate. Low impact (needs a two-marketplace setup to
trigger); flagging, not fixing. Code: `reset-plugin-cache.py:112`.

### Q5 — 16 open draft PRs, several stale/superseded (process)
There are **16 open draft PRs**, several of which are overlapping repo-review branches
that this and prior reviews have superseded — e.g. **#461** ("regenerate stale
feedback-report.html") is moot now that `main`'s report is fresh; **#465 / #457 / #453**
are older repo-review batches. **Recommendation:** a sweep to close the superseded ones
(merged-equivalent work already on `main`) would cut the noise. This is your call — I
didn't close anyone else's PR autonomously.

### Q6–Q9 — still-open items from the 2026-06-22 review
The four open questions from yesterday's register
([`2026-06-22-repo-review-findings.md` §4](./2026-06-22-repo-review-findings.md#4-open-questions-need-your-input))
appear **unresolved** (no PR applies them): Q1 document `cleanup-branches.sh` in
`scripts/README.md` (note: this routine just *fixed a bug* in it — B3 — so documenting it
is now more warranted), Q2 louder signal on persistent SVG-render failure, Q3 a
preventive guard for the self-heal-gap class, Q4 a cadence for the 90-day concepts
re-verification. They still need your yes/no.

---

## 5. Panel routing note

Per the repo's decision-review convention, everything in §1 was **rule-derivable** (a
security fail-open with an unarguable malicious idiom, a false-positive narrowing, a
wrong-on-disk path, a latent crash/leak, a hardcode) and was implemented directly with
bidirectional gate fixtures proving teeth. Everything in §3–§4 rests on a genuine
preference, an admin-only action, an unverifiable-here premise, or verification-engine
semantics, so it is surfaced to you rather than auto-resolved.

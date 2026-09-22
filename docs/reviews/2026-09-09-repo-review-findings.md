# Repository review — 2026-09-09

Autonomous, multi-panel review of the RavenClaude marketplace. Scope: the full
working tree (184 plugins, the `scripts/` gate suite, CI workflows, boundary docs),
with the repo's own gate suite as the primary detector. Every conclusion below is
grounded in a this-session check, cited inline.

## Headline

**Main's required CI check was RED, and this PR turns it green.** The required
"Validate manifests and hooks" check (`validate-marketplace.yml`) failed on main's
current tip `e9e58f2` (run 2865, conclusion **failure**) — and had been failing since
today's two docs-straight-to-main archive commits. Root cause, one event, three
distinct gate failures:

> Commit `e3d7176` + `e9e58f2` ("archive shipped/stale plans…", 2026-09-09) moved
> ~25 plan directories under `docs/plans/archive/` **without updating a single
> relative reference**, and the docs-straight-to-main flow bypasses the pre-merge
> gates, so the breakage landed unvalidated. The last green main commit was
> `5002263` (#1132).

| Gate (all in the required check) | On main `e9e58f2` | After this PR |
|---|---|---|
| `prettier --check .` (whole-tree) | ✗ `build-plan.html` | ✅ exit 0 |
| `check-md-links.py` (relative-link resolution) | ✗ 37 broken links* | ✅ passes |
| `audit-gates` Gate 242 (ratchet freshness) | ✗ stale `measured_against` | ✅ re-stamped |
| `audit-gates` Gate 238 (inventory sweep) | ✗ (CI) | ✅ green on fixed tree |

\* md-links did not even appear in the CI failure list because the `core` job died at
the audit-gates step (Gate 238/242) before reaching the standalone md-links step;
verified separately that `check-md-links.py` exits 1 on main's tree and 0 after the fix.

All three fixes restore the exact pre-archive green state (verified: the parent commit
`5002263` had `check-md-links` exit 0, zero broken links).

## Panel 1 — expert scan & categorization

Signal source: the repo's own gate suite (the highest-value detector in a repo this
self-validating), run this session, cross-checked against main's actual CI run logs.

- **P0-1 — whole-tree prettier gate red.** `docs/plans/archive/2026-06-04-partner-success-command-center/build-plan.html`
  fails `prettier --check`. It is *meant* to be prettier-ignored (the ignore comment
  says it "was already failing the whole-tree gate… blocking every PR" and must stay
  ignored, not reformatted — prettier's HTML printer drifts between versions), but
  `.prettierignore` lines 27 & 33 still named the **pre-archive** path. The archive
  move stranded the ignore rule.
- **P0-2 — required `check-md-links.py` gate red.** 37 broken relative links across 20
  files: inbound references to moved plans (live docs, dated records, 6 ravenclaude-core
  skills, 4 edtech-partner-success files) **and** the moved plan files' own outbound
  links (whose relative depth changed when they descended one directory).
- **P0-3 — ratchet-freshness gate red (Gate 242).** `scripts/artifact-budgets.seed.json`
  and `tests/fixtures/inventory-coverage-ratchet.json` were stamped `measured_against`
  `6a40641`; main's base advanced past it via the two docs-to-main commits (which, unlike
  feature PRs, never re-stamp). This is the designed PR #991-shape detection firing
  correctly.
- **Gate 238 (inventory sweep)** failed in main's CI run but passes deterministically
  standalone and in-suite on the fixed tree (census 384==384, probes 7/8 executed, canary
  RED). See Panel 3.

No other P0/P1 surfaced: all other surface gates (JSON validity, shell syntax + exec
bits, ruff, frontmatter over 600+ agents/skills, version-catalog sync) were green this
session.

## Panel 2 — analysis (priority, impact, effort)

- **All three confirmed P0, not lower.** The bar for P0 here is "a consumer or CI
  actually breaks." CI is the thing that broke: the *required* merge gate is red on main,
  so **every open PR is blocked from merging** until this lands. Impact is repo-wide;
  effort is low and mechanical. Impact-to-effort overwhelmingly favors fixing now.
- **The link fixes are faithful, not rewrites.** Each change corrects only the link
  *target* to the file's new location (`…/plans/X/…` → `…/plans/archive/X/…` for inbound;
  one added `../` for outbound). Display labels and prose are untouched — a deliberately
  minimal edit. (Consequence: a few skill code-span labels still *read* the pre-archive
  path while linking correctly to `archive/`; a cosmetic staleness accepted in exchange
  for not editing prose. Noted as a P3 follow-up below.)
- **Two plugins were touched → patch-bumped** (`ravenclaude-core` 0.320.0→0.320.1,
  `edtech-partner-success` 0.12.7→0.12.8), catalog derived via `sync-plugin-versions.py`,
  Copilot package regenerated, CHANGELOG top entries added — per house rules #6 / modify-
  existing-plugin steps. Link-target only; **no behavioral change**, migration: none.

## Panel 3 — tie-breaking

- **Fix-forward vs. revert the archive commits.** The one genuine judgment call.
  Resolved to **fix-forward**: reverting a maintainer's deliberate same-day cleanup is
  high-blast and discards intent, whereas completing the move (updating the references it
  left behind) preserves intent and is unambiguous and verifiable (`check-md-links` exit
  0). Fix-forward wins decisively.
- **Gate 238 — real defect vs. in-suite flake.** The discriminating evidence: it failed
  in main's full-suite CI run and in this session's *first* full-suite run, yet
  `inventory-sweep.py --check` passes **deterministically** standalone (twice) and the
  census is git-derived (deterministic) — 384==384 on a tree whose file set my changes
  never altered. The failure correlates with full-suite execution context, not with any
  artifact state. Verdict: **order-dependent/transient in-suite execution of the
  effect/"executed" probes, not an artifact defect.** It is green on the fixed tree; if it
  flakes again on this PR's CI, the remedy is a single re-run, not a code change (per the
  repo's own "flake is not a root cause, confirm with one re-run" rule).

## Implementation (this PR)

Sorted P0 → P3. Post-edit validation this session: `prettier --check .` exit 0;
`check-md-links.py` passes; `check-ratchet-freshness.py --check` exit 0;
`sync-plugin-versions.py --check` in sync; `inventory-sweep.py --check` exit 0;
`concepts.py --check` OK; Copilot package fresh.

- **P0-1 — `.prettierignore`:** repointed lines 27 & 33 to the `docs/plans/archive/…`
  location so the intentionally-ignored `build-plan.html` is matched again.
- **P0-2 — 20 files:** repointed every broken relative plan link to its moved target
  (inbound + outbound), via a resolver that recomputes each path from the real file's new
  location (0 unresolved).
- **P0-3 — ratchet files:** re-stamped `measured_against` to the current merge base
  (values unchanged — SHA only), per the repo's standing per-PR re-measure convention.
- **Plugin hygiene (two plugins whose shipped files were touched):** patch bumps
  (`ravenclaude-core` 0.320.0→0.320.1, `edtech-partner-success` 0.12.7→0.12.8) + CHANGELOG
  entries + derived catalog (`sync-plugin-versions.py`) + regenerated Copilot package.
- **Regen cascade (required by the above).** Editing plugin files covered by inventory
  concepts, plus the version bump, drifted three concepts' `covers_digest`
  (`plugin-cache-is-version-keyed`, `tprose-screens-edits-too`,
  `analog-closeness-quality-bar-is-independent-of-score`). Each entry was re-read and its
  **claim confirmed unchanged** (link-target/version edits don't touch what they assert),
  so each was `--restamp-cosmetic`'d (digest moved, `last_verified` NOT — no false
  freshness). Then regenerated the derived artifacts: `concepts.json`, `dashboard.html`,
  `index.html` (docs/concepts.md was byte-identical). All freshness gates green after.

## Items needing design input / a decision

1. **The docs-straight-to-main flow keeps breaking the required check (recurring,
   structural).** Docs commits bypass the pre-merge gates, but main's *push* CI then runs
   the full required suite and goes red whenever a docs commit (a) leaves a whole-tree
   prettier/md-links violation or (b) advances the ratchet base without re-stamping. Today
   it did all three at once. **Question for Matt:** should docs-to-main commits run a
   lightweight pre-commit subset (prettier + md-links + ratchet re-stamp), or should plan
   *archival* specifically go through a PR? Recommendation: a pre-push hook (or a thin
   required-on-docs workflow) running exactly those three is the cheapest durable fix;
   relevant code: `.github/workflows/validate-marketplace.yml`, `scripts/check-md-links.py`,
   `scripts/check-ratchet-freshness.py`, `AGENTS.md` §"When a PR is required vs. not".
2. **Stale code-span labels after the link fixes (P3, cosmetic).** A handful of skill/doc
   links now display the pre-archive path text while linking correctly to `archive/`.
   Repointing the *labels* too would be correct but means editing prose/code-spans across
   ~10 files (and more plugin bumps). **Question:** worth a follow-up sweep, or leave as
   acceptable drift? Recommendation: leave unless a future reader trips on it — the links
   resolve, and the label churn isn't worth the plugin-version noise.

3. **Latent tooling bug — skill-count writers emit wrong counts transiently (P2/P3).**
   During the regen cascade, a generator transiently wrote **incorrect** skill counts into
   two source files — `plugins/ravenclaude-core/README.md` ("Skills 64 → 20") and
   `plugins/data-platform/.claude-plugin/plugin.json` (a `"99 skills"` literal appended to
   the description, which **Gate 206 forbids**). Both were reverted and did **not**
   reproduce on a clean re-run of any generator, so they are not in this PR — but they are
   a live symptom of the "**4 independent skill-counting implementations with no shared
   source of truth**" already named as a follow-up in #1132's own commit log. **Question
   for Matt:** fund the shared `discover_skills()` utility (all counters call one source)?
   Recommendation: yes, but as its own scoped PR — the bug is order/first-run-sensitive and
   needs a reproduction harness, not a drive-by fix. Relevant code:
   `scripts/generate-skill-index.py`, `scripts/generate-dashboards.py`,
   `scripts/generate-index-dashboard.py`, and the README/description writers.

No other item requires a decision before it can be resolved.

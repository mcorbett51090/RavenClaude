# Repository review — 2026-09-02

Autonomous, multi-panel review of the RavenClaude marketplace. Scope: the full
working tree (182 plugins, ~10,160 files, the `scripts/` gate suite, CI workflows,
and boundary docs). Method mirrors the three-panel structure below; conclusions are
grounded in this-session checks, cited inline.

## Headline

**The repository is in excellent health.** Every surface gate and the whole-repo
meta-test pass:

| Check | Result (this session) |
|---|---|
| `python3 -m json.tool` on all manifests + `.repo-layout.json` | ✅ valid |
| `bash -n plugins/*/hooks/*.sh scripts/*.sh` | ✅ clean |
| hook executability loop | ✅ all executable |
| `ruff check .` | ✅ All checks passed |
| `npx prettier@3.9.4 --check .` (whole tree) | ✅ exit 0 |
| `scripts/check-frontmatter.py` (600+ agents/skills) | ✅ OK |
| `scripts/check-marketplace-claims.py` | ✅ passed |
| `scripts/audit-gates.sh` (per-gate teeth meta-test, Gates through 234) | ✅ **0 failures** |

No P0 or P1 issues were found. The one genuine issue cluster is P2/P3 documentation
drift, described below and **fixed in this PR**.

## Panel 1 — expert scan & categorization

A full-tree sweep for bugs, tech debt, performance, architecture, and missing
features. Signal sources: the repo's own gate suite (the highest-value detector in a
repo this self-validating), a TODO/FIXME/BUG marker sweep, and a repo-internal
broken-link scan across all markdown.

- **Markers (`TODO`/`FIXME`/`XXX`/`HACK`/`BUG`):** 89 hits in code, **all intentional**
  — bug-fix commentary, test fixtures, the anti-pattern-detection hooks (which
  *search* user files for `TODO`), and vendored `mermaid.min.js`. No actionable debt.
- **Broken repo-internal markdown links:** 168 raw hits, but after excluding
  placeholders (`<topic>.md`, `**args`, `...`), generated `copilot/` projections, and
  vendored assets, **11 real ones remain** — and 10 of those 11 point at one retired
  artifact.

**Finding F-1 (the only substantive cluster): dangling references to the retired
`repo-guide.html`.** The artifact `repo-guide.html`, its generator
`scripts/generate-repo-guide.py`, and its freshness detector
`scripts/check-guide-fresh.sh` are **all absent from the tree** (verified: `ls` →
No such file; not in `git ls-files`). Its role — the browsable marketplace
catalog / repo guide — was **folded into `index.html`**, which `README.md` now
presents as "the portal / front door" and which CI gates for freshness (Gate 97).
Several *live* files still describe `repo-guide.html` as an active, gated, generated
artifact.

| # | Location | What's stale | Priority |
|---|---|---|---|
| F-1a | `checklists/release-checklist.md:26` | A release step instructing the releaser to run `python3 scripts/generate-repo-guide.py` (does not exist) and warning that a `Verify repo-guide.html is fresh` CI step (does not exist) will fail. A human following the checklist hits "No such file." | **P2** |
| F-1b | `.github/workflows/validate-marketplace.yml` (repo-guide NOTE block) | Comment claims `check-guide-fresh.sh` is "still audited … Gate 11" and that `regenerate-artifacts.yml` regenerates `repo-guide.html` post-merge. Both false — the script is gone and `regenerate-artifacts.yml` never references it. | **P3** |
| F-1c | `docs/best-practices/decision-trees-in-knowledge-files.md:64` | Broken link + dead GitHub Pages URL to `repo-guide.html`. Decision-tree Mermaid now renders in `dashboard.html`. | **P3** |
| F-1d | `AGENTS.md:163` | "The repo-guide generator picks them up…" — mechanism is still true, only the artifact name is stale (now the `index.html` portal generator). | **P3** |

## Panel 2 — analysis (priority validation, impact & effort)

Panel 1's assignments reviewed and confirmed:

- **No P0/P1.** Nothing breaks a consumer's `/plugin marketplace update`, no gate is
  red, no hook is broken, no manifest is invalid. The bar for P0/P1 in this repo is
  "a consumer or CI actually breaks," and that bar is not met.
- **F-1a is correctly P2, not P3:** it is the one item with a *human* in the failure
  path — a releaser is actively instructed to run a command that errors. Impact:
  confusion / a broken release step. Effort: trivial (one line). Impact-to-effort
  strongly favors fixing now.
- **F-1b/c/d are correctly P3:** stale comments/wording and a dead doc link. Impact:
  a maintainer or reader is momentarily misled; nothing breaks. Effort: trivial.
- **Deliberately NOT changed** (out of scope for an autonomous fix — they are
  point-in-time records or illustrative content, and rewriting them would corrupt
  history or add no value):
  - Historical references to `repo-guide.html` in `CHANGELOG.md` and dated
    `docs/plans/**`, `docs/research/**`, `docs/reviews/**` write-ups — these are
    records of what was true when written.
  - `docs/plans/2026-08-17-forms-engineering-plugin/plan.md` broken
    `../../ravenclaude-core/…` links — a dated historical plan.
  - `plugins/data-governance-privacy/best-practices/access-request-workflow-not-ad-hoc.md`
    `[@jane-smith-steward](steward)` — an *illustrative example* of an access-request
    record, not a real link.
  - `docs/team-portfolio-hub-bootstrap/_README.md` links to `reports/`,
    `portfolio.html`, etc. — a bootstrap template describing files the **consumer**
    generates, not files expected to exist here.

## Panel 3 — tie-breaking

No genuine ambiguity required a tie-breaker. The one judgment call — *which* live
artifact replaces `repo-guide.html` in each reference — was resolved against
convergent live evidence rather than a coin-flip:

- **Catalog / portal role → `index.html`.** `README.md:366` names `index.html` "the
  portal … covering every plugin, agent, skill, hook, rule, and template," gated by
  Gate 97. Used for F-1a and F-1d.
- **Rendered decision-tree / concept diagrams → `dashboard.html`.** The
  `validate-marketplace.yml` dashboard NOTE states the "concept/decision-tree SVGs
  [are] inlined into" `dashboard.html`; the file exists (10.5 MB, 362
  decision-tree/concept matches). Used for F-1c.

## Implementation (this PR)

Sorted P2 → P3. Every change replaces a **demonstrably dead** reference (the files
genuinely do not exist) with a **demonstrably live** one (verified present this
session), and is comment/prose/checklist text only — no executable gate logic
changed.

- **P2 — `checklists/release-checklist.md`:** repointed the "regenerate the guide"
  step to `scripts/generate-index-dashboard.py` / `index.html` / Gate 97, with a note
  that `repo-guide.html` was retired.
- **P3 — `.github/workflows/validate-marketplace.yml`:** rewrote the obsolete
  repo-guide NOTE block to state accurately that the artifact was retired and its role
  folded into the Gate-97-gated `index.html` (comment only — no gate behavior
  changes).
- **P3 — `docs/best-practices/decision-trees-in-knowledge-files.md`:** repointed the
  Mermaid-renders link (and its GitHub Pages URL) to `dashboard.html`.
- **P3 — `AGENTS.md`:** "repo-guide generator" → "portal generator (`index.html`)".

Post-edit validation (this session): `prettier --check` on all four files → exit 0;
`check-marketplace-claims.py` → passed; both new link targets resolve on disk.

## Items needing design input / a decision

**None.** This review surfaced no issue that requires an architectural decision or a
maintainer's preference before it can be resolved. The health checks are green and the
only real cluster was unambiguous documentation drift with a single correct fix each.

If a follow-up is wanted, the lowest-value-but-tidy option is sweeping the *historical*
`repo-guide.html` mentions (CHANGELOG, dated plans/research) — but that is explicitly
**not recommended**: those are records, and editing them trades a harmless stale name
for corrupted history.

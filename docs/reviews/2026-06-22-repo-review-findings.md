# Repository review — findings register & open questions (2026-06-22)

A comprehensive review of the RavenClaude marketplace (101 plugins, 400+ agents)
run as a multi-panel exercise:

- **Panel 1 (expert review)** — an objective gate sweep (all CI gates + the
  `audit-gates.sh` meta-test) plus three parallel expert panels: (1a)
  generated-artifact / CI-self-heal consistency, (1b) executable-code bug hunt
  (scripts, hooks), (1c) cross-plugin consistency & tech debt.
- **Panel 2 (analysis)** — priority validation + impact/effort context
  (performed by the synthesizing reviewer over Panel 1's raw findings).
- **Panel 3 (tie-break)** — consensus on the ambiguous severities (dormant gate,
  the doc-path fixes' version-bump cost, the archive-branch latent bug).

**Headline:** the repo is exceptionally well-maintained. Every objective gate
passes **except one**, which was a live CI-red P0 (now fixed). Panel 1b found
**no high-severity code defects** — the security-critical hooks
(`guard-destructive`, `enforce-layout`, `route-decision-review`, the tribunal
engines, the untrusted-intake processor) are sound and fail-closed where it
matters. The remaining findings are tech debt and small correctness items.

This PR implements every finding that needed **no design input**. The items in
[§4 Open questions](#4-open-questions-need-your-input) need a yes/no from you.

---

## 1. Implemented in this PR (by priority)

| ID | Pri | Finding | Fix | Evidence |
|----|-----|---------|-----|----------|
| A1 | **P0** | `audit-gates.sh` Gate 99 (feedback-report freshness) failing on a clean tree — **CI red on main**; the stale `feedback-report.html` (366→369 scenarios) fails every open PR. `generate-feedback-report.py` was never added to the post-merge self-heal. | Regenerated `feedback-report.html`; added the generator to `regenerate-artifacts.yml` (step + `paths:`). | `scripts/audit-gates.sh:3211`; `.github/workflows/validate-marketplace.yml:323` |
| A2 | **P1** | Latent twin of A1: `generate-concepts-doc.py` (`docs/concepts.md`) has a PR-time `--check` gate **and** an audit-gates clean-tree gate but was also missing from the self-heal — a sibling concept merge would stale it and fail every open PR. | Added to `regenerate-artifacts.yml`. | `.github/workflows/validate-marketplace.yml:368`; `scripts/audit-gates.sh:1671` |
| C1 | **P1→P2** | Dormant CI gate: `scripts/check-concern-stats-render.mjs` (Pipeline-tab "Concern reliability" render gate, incl. an XSS-hygiene no-`innerHTML` assertion) had **no caller** while its 8 sibling render gates are all wired. The card could silently regress. | Registered as **Gate 104** (per-gate dispatcher + main sequence + Supported list). | `scripts/check-concern-stats-render.mjs` (unreferenced before); siblings at `scripts/audit-gates.sh:2455,2503,2556,…` |
| C2 | **P2** | `ravenclaude-core/CLAUDE.md` (the constitution) references `data-platform` skills as `<name>.md` — but skills are `<name>/SKILL.md` directories. A reader/agent following the path 404s. (Not a markdown link → `check-md-links.py` can't catch it.) | Corrected 4 paths to `…/SKILL.md`. | `plugins/ravenclaude-core/CLAUDE.md:15-16` |
| C3 | **P2** | `finance/README.md` dispatch pointer `…/spawn-team.md` → should be `…/spawn-team/SKILL.md`. | Corrected. | `plugins/finance/README.md:42` |
| C4 | **P3** | `microsoft-365-copilot/CLAUDE.md` cites `veterinary-practice/vet_calc.py` — actual path is `…/scripts/vet_calc.py`. | Corrected. | `plugins/microsoft-365-copilot/CLAUDE.md:235` |
| B1 | **P3** | Dead code: `regen-on-manifest-change.sh` has a `generate-repo-guide.py` regen block, but that script + `repo-guide.html` were deleted in v0.124.0. The `[ -f ]` guard means it never runs, but the block + header comment mislead. | Removed the block; corrected the header. | `plugins/ravenclaude-core/hooks/regen-on-manifest-change.sh:96-106` |
| B2 | **P3** | `archive-branch.sh:123` hardcodes `main` in `git log "$BRANCH" --not main`. On a `master`-default repo this errors → `\|\| true` → `UNMERGED_COUNT=0` → the plan prints a **false "fully merged"** for an unmerged branch (no data loss — the tag is still made — but a misleading "safe to delete" signal). | Resolve the default branch (`origin/HEAD` → main/master → fail-safe to "all commits unmerged"). | `scripts/archive-branch.sh:121-124` |

**Verification (this session):** `audit-gates.sh` **445 pass / 0 fail** (was
443/1 → 444/0 after A1/A2 → 445/0 after Gate 104); prettier whole-tree clean;
every generator `--check` fresh; no version drift; md-links + marketplace-claims
pass. `index.html` is intentionally **not** regenerated on this PR branch — it
self-heals post-merge via `regenerate-artifacts.yml`, the established pattern for
plugin-version bumps (a PR branch carrying the 8.9 MB file is the cross-PR
contagion the workflow exists to avoid).

---

## 2. Reviewed and cleared (no defect)

Panel 1b spot-checked the security-critical surface and **cleared** it — recorded
here so the next reviewer doesn't re-walk it:

- `guard-destructive.sh`, `enforce-layout.sh`, `route-decision-review.sh`,
  `runaway-brake.sh`, `dod-gate.sh` — correct `set` flags, exit-2-to-block,
  fail-closed where it matters; the fail-open paths are deliberate + documented.
- `process-scenario-submission.py` (untrusted GitHub-issue intake) — path built
  from `.isdigit()`-validated number + `[a-z0-9-]` slug (no traversal); secret/PII
  scan before injection-strip (correct order); reads untrusted content via env,
  not argv.
- `pseudonymize-brief.py`, `thing-decide.py`, `claude-orchestrate.sh` — span/decode
  logic, line-break-char handling, and recursion/scrub guards all correct.
- All 101 plugins have the required `plugin.json` + `README.md` + `CLAUDE.md`.
- The 121 `TODO`/`FIXME` grep hits in `plugins/` are almost entirely **content**
  (anti-pattern hooks that *detect* those words, CHANGELOG entries) — not debt.

---

## 3. Architectural observation (the root-cause pattern behind A1/A2)

A1 and A2 are two instances of one latent class:

> **A generated artifact with a PR-time freshness gate, but no step in the
> post-merge `regenerate-artifacts.yml` self-heal.** When a *sibling* PR stales
> it, every open PR fails the gate and nothing on `main` heals it.

This is the exact contagion the self-heal workflow was built to kill (it already
covers counts, SVGs, dashboard, index, bi-report, copilot). Two generators had
slipped the net; both are now wired. See [Q3](#q3-preventive-guard-for-the-self-heal-gap)
for a proposed guard so a *third* can't slip in unnoticed.

---

## 4. Open questions (need your input)

### Q1 — Document `cleanup-branches.sh`, or confirm intentional omission?

`scripts/cleanup-branches.sh` is an operator utility (a hand-invoked wrapper
around the `guard-destructive.sh` escape hatch) but is **absent from
`scripts/README.md`**, while its cousins `archive-branch.sh` / `worktree-clean.sh`
are documented there. It's not dead code — it's undiscoverable.

- **Recommendation:** add a one-line entry to `scripts/README.md`.
- **Why it's a question, not a fix:** it may be intentionally undocumented (e.g.
  deprecated in favour of `archive-branch.sh`). One line either way; your call.
- Code: `scripts/cleanup-branches.sh`, `scripts/README.md`.

### Q2 — Louder signal when the post-merge SVG render keeps failing?

`render-trees.py --check` is **stale right now** on a clean tree. This is *not* a
CI failure (its clean-tree gate was deliberately removed; it self-heals
post-merge). But the self-heal renders SVGs with mermaid-cli + Chromium and, by
design, a render failure is **non-fatal** — it emits a `::warning::` and
continues. So a *persistently* failing render leaves the SVGs silently stale with
only a buried warning.

- **Recommendation:** add a cheap alert (e.g. the Níðhöggr "Debt watch" card, or a
  scheduled check) that fires when the decision-tree SVGs have been stale for >N
  merges — turning a silent warning into a visible signal.
- **Why it's a question:** it's a new monitoring surface, not a bug fix, and the
  current behavior is intentional. Worth it, or leave as-is?
- Code: `.github/workflows/regenerate-artifacts.yml:142-148`; `scripts/render-trees.py`.

### Q3 — Preventive guard for the self-heal gap?

A1/A2 were each "a generator with a PR-time freshness gate but no self-heal step."
I fixed the two instances; nothing stops a **third** from being introduced.

- **Recommendation:** a small meta-check (a new audit-gate, or a line in an
  existing one) that asserts: *every generator referenced by a clean-tree
  `--check` gate in `audit-gates.sh` / `validate-marketplace.yml` is also present
  in `regenerate-artifacts.yml`.* This makes the contagion class structurally
  impossible to reintroduce.
- **Why it's a question:** it adds a gate (the repo is disciplined about gate
  count + the gate-audit doctrine), and encoding "which generators must self-heal"
  is a small policy decision. Want it built? (I'd estimate ~30 lines + a
  bidirectional fixture.)
- Code: `scripts/audit-gates.sh`, `.github/workflows/regenerate-artifacts.yml`.

### Q4 — `concepts.py` 90-day staleness time-bomb (informational)

`concepts.py --check` carries a **90-day platform-fact content gate**. When a
`last_verified` date ages past 90 days, the gate fails on PRs and the post-merge
self-heal **cannot** fix it (it needs a human re-verification of the fact, not a
regeneration). This is working as designed, but it's a latent PR-blocker with a
human in the critical path.

- **Recommendation:** none mechanical — flagging so a scheduled "re-verify the
  aging concepts" sweep can be planned before a date crosses the threshold. The
  `knowledge-file-staleness-sweep` skill already exists for this; the question is
  whether to put it on a cadence.
- Code: `scripts/audit-gates.sh:1597-1598`; `scripts/concepts.py`.

---

## 5. Panel routing note

Per the repo's decision-review convention, the yes/no items in §4 are genuine
**preference / design** calls (Q1: intent; Q2/Q3: new surface vs. cost; Q4:
cadence), so they are surfaced to you rather than auto-resolved. Everything in §1
was rule-derivable (a failing gate, a wrong on-disk path, dead code, a latent
hardcode) and was implemented directly.

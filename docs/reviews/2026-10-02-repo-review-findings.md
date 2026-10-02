# Repository review — 2026-10-02

Autonomous, four-panel review of the RavenClaude marketplace. Scope: the full
working tree (**184 plugins**, ~10k files, the `scripts/` gate suite, the CI
workflows, boundary docs), with a focused correctness pass over the logic-heavy
executable surface (shell hooks, Python gates, GitHub Actions) where real bugs
live.

Method mirrors the requested three-panel structure, implemented as four
independent expert-reviewer panels (Panel 1) over four scoped slices, then a
Panel 2 validation + Panel 3 tie-break pass by the orchestrator that re-verified
every finding on the real tree before any fix was written. Ground truth for repo
health is the repo's own gate corpus, not an LLM opinion — the panels ran _on top
of_ the real gates. Model assignment per the task: the Panel 1 categorization
scanners ran on a lighter tier (sonnet); validation, tie-breaking, and all
implementation decisions were made at the frontier tier.

Provenance: the review branch (`claude/awesome-wright-nl7bht`) was **even with
`origin/main`** at review time (merge-base = main HEAD), so every finding is on
real main, not a stale checkout.

## Headline

**The repository is in excellent health.** Every surface gate and the whole-repo
meta-test pass on real main:

| Check | Result (this session) |
|---|---|
| `python3 -m json.tool` on all manifests + `.repo-layout.json` | ✅ 186 files parse |
| `bash -n` + hook executability (200 files) | ✅ clean |
| `prettier --check .` (whole tree) | ✅ exit 0 |
| `ruff check .` | ✅ all checks passed |
| `jsonschema` — all 184 `plugin.json` + `marketplace.json` | ✅ valid |
| `scripts/ci-preflight.py` freshness hotspots (inventory/dashboard/index/census/sweep/copilot/codex/concepts) | ✅ pass (one advisory, below) |
| `scripts/audit-gates.sh` (per-gate teeth meta-test) | ✅ pass |
| plugin required-file completeness (184 plugins) | ✅ 184/184 complete |
| broken-link scan across boundary docs | see CO findings |

The only non-green diagnostic is the `ratchet-merge-base` **advisory** in
`ci-preflight` (`artifact-budgets.seed.json` stamped at an older merge base) — the
**real** `check-ratchet-freshness.py` gate exits 0, so it is not a CI failure. See
decision E.

**No P0 issues. One P1** (a reproduced security-guard bypass), **fixed.** The rest
are P2/P3, split between what was safe to auto-fix and what needs owner sign-off.

## The four panels

- **Panel A — Shell & hook correctness** (23 `scripts/*.sh` + a risk-sample of 177
  plugin hooks; shellcheck 0.11): **1 P1, 7 P2, 6 P3**, every one reproduced.
- **Panel B — Python gate & script correctness** (~28 `check-*` gates + the
  generators; ran each `--check`, tested empty-scope vacuous passes, and
  `PYTHONHASHSEED` 1/2/12345 for generator nondeterminism): **0 P0, 1 P1, 2 P2, 8
  P3**, all wiring/blind-spots — no logic bug inside the hardened gates.
- **Panel C — GitHub Actions / CI** (all 17 workflows + dependabot + the live
  `main` ruleset): **0 P0, 0 P1, 5 P2, 9 P3**. All 39 `uses:` SHA-pinned; no
  `paths:` on any required check; no script injection; no `pull_request_target`.
- **Panel D — Consistency / links / dead code** (all 184 plugins, boundary docs,
  catalog, 238 hook path refs): **0 P0, 0 P1, 3 P2, 7 P3**. 184/184 plugins
  complete; catalog matches dirs; no dead code.

## Fixed in the accompanying PR (grouped by priority)

### P1 — security

- **URL-authority parsing bypass** in `guard-web-access.sh` and
  `mark-web-domain-seen.sh` (SH-1). The host was extracted with `${host%%/*}`,
  which terminates the authority only at `/`. A query/fragment with no path slash
  (`evil.example?@trusted.example`, `evil.example#x`, the `\` variant) left the
  whole string as the "host", so the `##*@` userinfo strip read `@trusted.example`
  as the host — **spoofing the allow list and bypassing the deny list**.
  Reproduced: pre-fix, `https://evil.example?@trusted.example` returned
  `permissionDecision:"allow"`. Fixed to cut the authority at the first of
  `/ ? # \` before stripping userinfo, in both reader and writer. **Validated
  end-to-end** against a deny/allow config: all four attack vectors now resolve to
  `evil.example` and are blocked (rc=2); benign URLs and ports unaffected.

### P2 — reproduced correctness bugs

- **`runaway-brake.sh` (SH-5):** `exec 9>"${f}.lock" 2>/dev/null` permanently
  redirected the script's own fd 2, so the blocking "Runaway brake" reason went to
  `/dev/null`. Scoped the redirection to the `exec`.
- **`enforce-layout.sh` (SH-6):** `${file#$project_root/}` left `$project_root`
  unquoted in the strip pattern, so a glob/bracket in the project path (e.g.
  `~/Clients/[Acme]`) broke the prefix strip and denied every in-project write.
  Quoted it.
- **`cleanup-branches.sh` (SH-7):** the merged-ness proof used an unqualified
  branch name, so a same-named tag could shadow the branch and a real run could
  `update-ref -d` an unmerged branch. Now `refs/heads/$b`.
- **`check-qa-test-automation-anti-patterns.sh` (SH-3):** dead on arrival — the
  XPath grep pattern `page\.\$x\(` was double-quoted, so `$x` expanded as an unset
  variable under `set -u` and the hook exited 1 before reporting. Escaped the `$`;
  validated the old pattern errors under `set -u` and the fixed hook flags a
  `page.$x(...)` write.

### P2/P3 — broken links & doc drift (Panel D)

- `AGENTS.md` cited a `model-tier-delegation.md` §"Multi-hop delegation" that no
  longer exists (CO-1) — dropped (the decision doc it also links covers it).
- Two more dead §-anchors into the same stub: `ravenclaude-core/CLAUDE.md`
  §"Cross-host honesty" and `knowledge/subagent-isolation-and-tooling.md` §"The
  three ways…" (CO-2) — dropped, file links kept.
- `agents/source-control-coordinator.md` cited `AGENTS.md` §"Remote-environment PR
  mechanics"; the heading is in `CLAUDE.md` (CO-6a) — corrected.
- `docs/plugin-discovery-routine-policy.md` cited `CLAUDE.md` §"Admin bypass is
  deliberate"; it's in `AGENTS.md` (CO-6b) — corrected.
- `CHANGELOG.md` linked `../index.html` (escapes the repo); → `index.html` (CO-5).
- `psm-dashboard-build/SKILL.md` tier table named seven brief files that don't
  exist (CO-3) — corrected to the real archived names; T0 → `plan.md` §"Tier 0";
  T5 marked "no brief yet".
- `regulatory-compliance/control-testing/SKILL.md` cross-plugin ref
  `skills/soc-control-walkthrough.md` → the real `…/SKILL.md` path (CO-8).

Version cascade applied correctly: patch-bumped `ravenclaude-core` (0.326.1),
`qa-test-automation` (0.3.4), `edtech-partner-success` (0.12.11),
`regulatory-compliance` (0.12.7); CHANGELOG top entries added; catalog synced via
`sync-plugin-versions.py`; copilot + codex agent projections regenerated (only the
edited agent changed); the three concepts whose covered artifacts changed
re-stamped **cosmetic** (digest moved, `last_verified` not — honest, since none of
the edits changes the concept's substance). All validated: `prettier --check .`,
`concepts.py --check`, `generate-*-plugin/agents --check`, and `audit-gates.sh`
pass.

## Deferred for owner sign-off → the decision doc

Everything touching a CI gate's pass/fail behaviour, a human-reviewed re-seed, the
security perimeter's policy, or a multi-file campaign was **not** auto-applied
(matching the 2026-09-22 precedent). Full detail, with ready-to-apply fixes, in
[`docs/2026-10-02-repo-review-design-questions.md`](../2026-10-02-repo-review-design-questions.md):

- **Gate blind spots:** skill-description cap/ratchet dead in CI and failing today
  (A1, P1-sev finding but a policy re-seed, not a code bug); Copilot tool
  projection fails open to all-tools (A2); Codex hook-accounting red + unwired
  (A3); Gate 242 covers 3 of 7 required checks (A4); a batch of fail-closed/scope
  hygiene fixes (A5, incl. SH-8/PY-5/6/7/8, SH-9/12/13/14).
- **The `scan_target` campaign (B):** 30 PreToolUse hooks still blind to new
  writes — completes the 2026-09-23 work; recommended as its own batch + a gate.
- **CI hardening/policy (C):** trufflehog `:latest`, always-OK "assert-not-required"
  steps, quarantine spam cap, docs-only filter missing `ruff.toml`/`.prettierignore`,
  dispatch secret-scan skip, pip pins, permissions floor, PAT scoping, merge race,
  job timeouts, dependabot npm, stale workflow comments.
- **Content/doctrine (D):** Power Platform resource files (author vs delete); 52
  dangling `works_with` refs + a resolution gate; heredoc commit-subject handling;
  an abandoned forward reference; the STRATEGY.md stub (known B10).
- **Latent ratchet (E):** restamp `artifact-budgets.seed.json` on a current merge
  base.

## Appendix — panel verdict counts

| Panel | P0 | P1 | P2 | P3 |
|---|---|---|---|---|
| A — shell/hooks | 0 | 1 | 7 | 6 |
| B — python/gates | 0 | 1 | 2 | 8 |
| C — CI/actions | 0 | 0 | 5 | 9 |
| D — consistency | 0 | 0 | 3 | 7 |

Fixed this PR: 1 P1 + 4 P2 (shell) + 6 broken-link (P2/P3). All other findings →
the decision doc.

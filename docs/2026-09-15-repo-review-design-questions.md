# Repo review — 2026-09-15 — findings, fixes, and design questions

Scheduled whole-repo review run. This document records the multi-panel process, the
P0–P3 findings, what was fixed autonomously in the accompanying PR, and the handful of
items that warrant a human design decision rather than a mechanical fix.

## Method

The repo's mechanical layer was confirmed clean first (`scripts/ci-preflight.py` → 19
PASS / 0 FAIL: lint, freshness, ratchets, inventory), so the sweep targeted the surface
where real correctness/security bugs live in a markdown+JSON marketplace: **executable
code** — 127 Python scripts, 23 shell scripts, 254 plugin hooks, 17 GitHub Actions
workflows.

- **Panel 1 (scan, lighter model):** four parallel reviewers over disjoint high-risk
  slices — (A) recently-changed executable files, (B) CI-gating scripts + generators,
  (C) plugin shell hooks, (D) GitHub Actions workflows. Each returned structured
  findings (file:line, dimension, P0–P3, failure scenario, confidence).
- **Panel 2 (validation):** every reported finding was re-verified directly against the
  code (regex behaviour, live reproduction, sibling-convention cross-check) before being
  accepted. No finding was actioned on a panel's say-so alone.
- **Panel 3 (tie-break):** convened only for ambiguous priorities. **None arose** — the
  four confirmed findings had unambiguous severities, so no tie-break was needed.

## Findings

| ID  | Priority | File | Defect | Status |
|-----|----------|------|--------|--------|
| A1  | P1 | `plugins/finance/hooks/scan-finance-secrets.sh` | Placeholder filter inspected only the **first** regex match per line (`head -n1`), so a documented placeholder sharing a line with a genuine secret masked it — a false-negative in the `--ci` merge gate. | **Fixed** |
| B1  | P1 | `scripts/check-gate-registration.py` | `_full_suite_blocks()`'s "ambiguity, not a skip" guard was **dead** (always-true inner condition), so a malformed full-suite gate header would escape the meta-gate silently — the exact class this checker exists to catch. Latent (no malformed header today). | **Fixed** |
| C1  | P2 | `plugins/finance/hooks/flag-finance-anti-patterns.sh` | Comment + runtime banner told maintainers to use `exit 1` to BLOCK, but Claude Code's PreToolUse contract only blocks on `exit 2` — false enforcement, framed as a compliance control for "sensitive engagements". | **Fixed** |
| C2  | P3 | `plugins/web-design/hooks/check-web-anti-patterns.sh` | Same `exit 1`-to-block defect. | **Fixed** |
| C3  | P3 | `plugins/power-platform/hooks/check-house-opinions.sh` | Same defect. | **Fixed** |
| C4  | P3 | `plugins/power-platform/hooks/validate-tmdl-measure-metadata.sh` | Same defect. | **Fixed** |
| C5  | P3 | `plugins/power-platform/hooks/validate-flow-action-names.sh` | Same defect — **not** reported by the panel; found by a follow-up grep for the full defect class. | **Fixed** |
| C6  | P2 | Documentation of the above hooks (each plugin's `CLAUDE.md` §7, `README.md`, and `power-platform/best-practices/name-flow-actions-descriptively.md`) | The **same wrong `exit 1`-to-block instruction** in the prose that documents the fixed hooks — found by grepping the defect class across all docs. | **Fixed** (for the 3 plugins touched) |

Panel D (GitHub Actions, 17 workflows) returned **no findings**: SHA-pinning and
untrusted-input-through-`env` are already mechanically enforced (workflow-hygiene gate,
Gate 242), and the three required checks correctly omit `paths:` filters.

**No P0 findings.** The repo is in good shape; this was a productive-but-shallow yield,
consistent with a tree swept the prior day.

### Follow-up finding surfaced during the fix (not a panel finding)

Grepping the `exit 1`-to-block defect class across the whole tree showed it is
**systemic** — the same wrong instruction appears in the docs (and possibly the hooks)
of plugins outside this PR's scope: **`regulatory-compliance`** (its `README.md` and
`skills/sar-narrative-drafting/SKILL.md` — notably framed as a *SAR/STR compliance
control*, "always flip to `exit 1`", so the highest-stakes instance), **`data-platform`**
(`CLAUDE.md`), and **`edtech-partner-success`** (`CLAUDE.md`). These were **not** fixed
here to avoid ballooning a focused bug-fix PR into a 6+-plugin change; see Q4.

## What the PR changes

All seven confirmed findings were mechanical (no design decision required) and are fixed
in the PR, grouped by priority:

- **P1** — A1 (all-spans placeholder check + 2 regression tests, `test_secrets_gate.py`
  now 15/15); B1 (real fail-closed logic + a new "malformed header fails closed" teeth
  case, self-test now 12 checks).
- **P2 / P3** — C1–C5: each hook now documents and implements the established sibling
  convention (`<PLUGIN>_STRICT=1` → `exit 2` to block; `exit 1` correctly described as
  non-blocking). Verified live: advisory → exit 0, `STRICT=1` → exit 2.

Plugin semver bumped for the three affected plugins (finance 0.18.8, web-design 0.18.3,
power-platform 0.44.12); catalog re-derived via `scripts/sync-plugin-versions.py`.

## Design questions (for your review)

These are **not** bugs — they are judgment calls surfaced by the sweep. Recommendations
are given but not acted on.

### Q1 — Standardise the anti-pattern-hook STRICT contract into one shared helper?

The `exit 2`-behind-`<PLUGIN>_STRICT` pattern is now duplicated across ~15 anti-pattern
hooks (`plugins/*/hooks/flag-*-*.sh`, `check-*-anti-patterns.sh`). The C1–C5 defect was
precisely a *copy that drifted* from the convention. A shared sourced helper (e.g.
`plugins/ravenclaude-core/hooks/lib/strict-block.sh` exposing `strict_block_if_set VARNAME`)
would make the whole class un-driftable and gate-checkable.

- **Recommendation:** worth doing, but it is a cross-plugin refactor touching many files
  and a new shared-lib convention — deferred to a human decision rather than bundled into
  a bug-fix PR. Relevant code: `plugins/*/hooks/*anti-pattern*.sh`,
  `plugins/*/hooks/flag-*.sh`.

### Q2 — Sweep for other "comment promises X, code does Y" latent guards?

B1 was a dead guard whose comment asserted a fail-closed behaviour the code did not
implement. This is a distinct, high-value defect class (a broken guard is invisible from
a green dashboard). Panel B found one; a targeted sweep for `# ... ambiguity/fail-closed/
must ...` comments sitting above no-op control flow across `scripts/check-*.py` could find
siblings.

- **Recommendation:** schedule a focused follow-up sweep (dimension: "guard/​comment
  divergence") over the `scripts/check-*.py` gate family. Low effort, defensible yield.

### Q4 — Sweep the systemic `exit 1`-to-block doc defect across the remaining plugins?

The follow-up finding above (`regulatory-compliance`, `data-platform`,
`edtech-partner-success`, and likely others) is the C1–C6 defect class in plugins this PR
did not touch. Fixing it properly means, per plugin: verifying the hook's actual exit
path, correcting the docs, bumping the version, and updating the changelog.

- **Recommendation:** run one dedicated sweep PR that greps
  `flip.*exit 0.*exit 1 | exit 0. to .exit 1` across `plugins/**` (excluding CHANGELOGs
  and `docs/**/archive`), fixes each hook + its docs to the `<PLUGIN>_STRICT=1 → exit 2`
  convention, and bumps each touched plugin. The `regulatory-compliance` SAR/STR instance
  should be treated as **P2, not P3** — it is a documented compliance control that
  currently promises enforcement it does not deliver.

### Q5 — Codex hooks projection: wire or skip `prompt-optimizer-gate.sh`?

`scripts/generate-codex-hooks.py --check` fails on the current tree (and on a clean
`main` — this is **pre-existing, not introduced by this PR**): the canonical hook
`prompt-optimizer-gate.sh` is "neither wired nor explicitly skipped" in the Codex
projection. It is not caught by `audit-gates.sh` or the required CI, so it does not block
merges today.

- **Recommendation:** decide whether `prompt-optimizer-gate.sh` should run on Codex (wire
  it) or not (add it to the explicit skip list), then regenerate. A small, self-contained
  fix — but it needs the wire-vs-skip judgment, so it is surfaced here rather than guessed.
  Code: `scripts/generate-codex-hooks.py`.

### Q3 — Should placeholder detection in the secrets scanner be structural, not regex-on-line?

A1 is the **third** iteration of the same masking bug (whole-line → first-span →
all-spans). Each fix narrowed the blind spot without changing the approach. The all-spans
fix closes the known gap, but the underlying technique (regex the raw line) remains
fragile against future shapes.

- **Recommendation:** the current fix is correct and sufficient for now. A structural
  rewrite (tokenise the line, classify each candidate) is a larger investment — flag it
  only if a fourth variant of this bug appears. Code:
  `plugins/finance/hooks/scan-finance-secrets.sh` §per-rule loop.

## Verification

`prettier --check` clean, `ruff check` clean, `check-gate-registration.py` live + full
self-test pass, `test_secrets_gate.py` 15/15, `check-diff-budget.py` within budget,
catalog in sync (Gate 226). Full `scripts/audit-gates.sh` run recorded in the PR.

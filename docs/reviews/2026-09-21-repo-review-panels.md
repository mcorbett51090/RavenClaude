# Comprehensive repo review — three-panel sweep (2026-09-21)

**Scope:** whole-repository review as a scheduled autonomous routine. Categorize issues P0–P3,
resolve priority conflicts by expert consensus, implement design-free fixes, and surface the
rest for maintainer decision.

**Headline:** the tree is exceptionally hardened and was **fully green at start** (every CI gate,
`ruff`, `prettier`, all freshness/ratchet/inventory gates, markdown-link check, and the read-only
`ci-preflight.py` — 19/19 pass). The panels found **2 concrete, verifiable minor (P2) defects**,
both now fixed in this PR, and **1 out-of-scope observation** deferred below. No P0/P1 defects.

This is an honest outcome, not a thin one: a naive whole-repo reviewer on this codebase produces
noise, because most apparent "issues" are documented-intentional designs (fail-open-by-design guards,
"no host probe on purpose", "WARN is the only verdict"). The panels were run under a strict contract —
**only defects with a concrete reproduction; documented-intentional design is not a bug; every fix
validated against the repo's own gates.**

## Method — the panels

| Panel | Role | Scope | Model tier |
|---|---|---|---|
| **1A** | Expert review | Python `scripts/*.py` (~130) — correctness, error-handling, resource-leaks, perf | heavier (general-purpose) |
| **1B** | Expert review | Shell `plugins/*/hooks/*.sh` + `scripts/*.sh` (~200) — fail-open/closed, injection, exit codes | heavier |
| **1C** | Expert review | GitHub Actions `.github/workflows/*.yml` (17) + handler scripts — CI/CD security & gate integrity | heavier |
| **2** | Analysis / validation | Orchestrator re-read every finding against source; confirmed reproduction, priority, effort | heavier |
| **3** | Tie-break | — | n/a — no priority was ambiguous, so no adjudication was needed |

Lighter-model categorization was unnecessary: the confirmed finding set was small enough (3) that the
orchestrator validated each directly rather than fanning out a categorization pass.

## Confirmed findings

### P2 — F1 · `scripts/inventory-sweep.py:404` · error-handling · **FIXED**

The must-fail-convention probe guarded only on marker *presence*
(`"must-fail-teeth-exit:" not in decl.stdout`), then did
`decl.stdout.split("must-fail-teeth-exit:")[1].strip().split()[0]`. When a probed self-test emits the
marker as the last non-whitespace content with **no value** (line `must-fail-teeth-exit:` — a plausible
authoring typo where the intended exit-code variable was empty), `"".split()` → `[]` → `IndexError`.
The probe runs at the call site (`spec["run"](...)`) **with no try/except around it**, so the uncaught
error aborts the **entire sweep** and loses every other probe's result — a self-blinding failure mode
in the very tool that certifies gate integrity.

- **Fix:** classify an empty value as `SKIP("no-selftest-declared")` (matching the existing
  undeclared-convention semantics) instead of indexing `[]`.
- **Verified:** regression test over `marker-at-EOF`, `marker-trailing-spaces`, and `valid-value`;
  the two empty cases now classify SKIP with no crash, the valid value is unaffected; the script's own
  `--must-fail` self-test still exits 3 (teeth intact).
- **needs_design_input:** no. Latent (no current self-test triggers it) → minor, not major.

### P2 — F2 · `plugins/microsoft-365-copilot/hooks/flag-copilot-anti-patterns.sh:145` · correctness · **FIXED**

Strict mode (`M365_COPILOT_STRICT=1`) exited **1** on a violation. In Claude Code, exit 1 from a hook
is a non-blocking error that is silently swallowed — so strict mode was a **silent no-op**, the exact
opposite of its documented "make it BLOCK" intent. Six sibling advisory hooks in this marketplace
(finance, edtech, staffing, web-design, power-platform, database-engineering) all use **exit 2** for
the identical strict feature and state verbatim that "exit 1 is non-blocking and silently swallowed."
This hook was the lone outlier and committed the mistake its siblings warn against.

- **Fix:** `exit 1` → `exit 2`; header comment corrected. Advisory default (exit 0) unchanged; only the
  opt-in strict path is affected, and only to start working as documented.
- **Version:** `microsoft-365-copilot` `0.5.8` → `0.5.9`; catalog re-derived via
  `sync-plugin-versions.py`; CHANGELOG entry added.
- **Verified:** `bash -n` clean; no gate/test pins the old exit code; grep confirms exit 2 at :150.
- **needs_design_input:** no.

## Deferred — needs a maintainer decision

### D1 — `scripts/generate-concepts-doc.py` `_rebase_body_links` (~line 67) · cross-platform determinism

The link rebaser uses `os.path.normpath(os.path.join(...))`, which emits backslashes on Windows. For a
committed, CI-diffed artifact, a Windows generator run would desync the freshness gate. **No realized
failure exists in the current flow** — this repo's CI is Linux + macOS only — so it was not counted as
a finding. But it matches the failure class the `cross-platform-determinism` skill exists to prevent.

- **Question for the maintainer:** is Windows-host regeneration in scope? If a contributor could ever
  regenerate artifacts on Windows, this (and any sibling generator using `os.path` for committed link
  paths) should switch to forward-slash-normalized joins. If Linux/macOS-only is a firm constraint,
  close as won't-fix and optionally add a one-line note to the generator asserting the constraint.
- **Recommendation:** low-cost hardening — normalize to `/` explicitly regardless of host. Deferred
  rather than auto-fixed because it's a scope judgment, not a bug in the current pipeline.

## What the panels confirmed clean (so it isn't re-chased)

- **CI/CD (1C):** 0 findings across all 17 workflows. Required checks (`validate-marketplace`,
  `validate-layout`, `validate-schemas`) are free of `paths:` filters on their `pull_request` triggers
  (the repo's own forbidden-hang footgun). Every `uses:` is full-SHA-pinned; no `pull_request_target`
  checkout-and-run of untrusted head; untrusted `github.event.*` reaches shells only via `env:`;
  the required aggregator rolls up each needed job's result rather than reporting a hollow success.
- **Python (1A):** zero bare excepts, zero mutable-default args, zero `shell=True`/`eval`/`exec`, no
  path-traversal in the local write/run server (`serve-dashboards.py` allow-list + CSRF + Origin/Host
  guards verified), no ordering bypass in the scenario-submission PII/secret gate.
- **Shell (1B):** the core catastrophe/injection/web/worktree/tribunal guards show no verifiable
  fail-open; every dependency floor (missing `jq`/`python3`/`git`/`timeout`/`grep -P`) is handled in
  the correct fail-closed or documented-fail-open direction, each backed by an audit gate with a
  must-fail teeth half. The builtin-`printf | grep -q` SIGPIPE concern was empirically tested and
  cleared (bash builtin printf does not propagate SIGPIPE-141).

## Validation performed before this PR

`ci-preflight.py` (19/19), `ruff` (clean), `prettier --check` on changed JSON (clean),
`check-artifact-freshness.py --check` (dashboard + index fresh), `sync-plugin-versions.py --check`
(catalog in sync), `check-md-links.py` (clean), F1 regression test, F2 `bash -n` + exit-code grep,
inventory-sweep `--must-fail` teeth (exit 3).

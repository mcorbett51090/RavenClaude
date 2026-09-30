# Repo-review routine — 2026-09-30 (autonomous)

Scheduled autonomous whole-repo review. Branch `claude/awesome-wright-b7ax8r` (cut from `origin/main`
4b35028). Method: whole-tree deterministic gate/lint sweep (complete coverage of the "broken now" axis)
+ a 4-panel risk-sampled semantic review (sonnet panelists on scripts/*.py, hooks/*.sh, .github, engine
python) → opus consolidation, first-hand verification, tiered P0–P3.

**Headline:** no P0; nothing is broken on `main` right now (whole-tree json/shell/prettier/ruff + all
freshness/inventory gates pass). The highest-severity findings are **P1 security-guard bypasses** that
this routine deliberately did **not** auto-fix (see "Why not auto-fixed"). Six safe, verified,
non-design fixes are in the accompanying PR.

---

## 1. Fixed in the accompanying PR (verified)

| id | priority | file | fix | validation |
|----|----------|------|-----|------------|
| F4 | **P1 security** | `scripts/process-scenario-submission.py` | The untrusted-intake secret/PII gate scanned `_normalize_intake` output, but the staged file is built from `_strip_injection` (normalize **+ injection-tag removal**). A secret split by an injection tag (`ghp_AA<system-reminder>…</…>BB`) passed the gate, then the strip removed the tag and **reconstructed the secret into the committed quarantine file**. Added a strictly-additive post-strip gate on the exact staged text. | functional smoke test: old gate returns None, new gate catches the reconstructed token |
| F3 | P2 | `scripts/generate-codex-hooks.py` | `generate-codex-hooks.py --check` exited 1 — `prompt-optimizer-gate.sh` (a UserPromptSubmit hook, wired in hooks.json) was neither projected nor in codex's `_SKIP` (gemini's generator already had it). Added the matching `_SKIP` entry. | `--check` now exits 0 ("54 canonical hooks all accounted for") |
| F5 | P2 | `scripts/review-ledger.py` | `rev-parse --abbrev-ref HEAD` prints the literal `"HEAD"` on a detached checkout (truthy), so the `or "detached"` fallback never fired and every detached worktree collided on ledger key `HEAD`. | py compile + ruff; logic verified |
| C5 | P2 | `validate-schemas.yml`, `validate-marketplace.yml`, `validate-macos.yml` | `pip install jsonschema` was **unpinned** in two **required** checks (inconsistent with the repo's ruff/prettier/action SHA pinning), and the `python -m jsonschema` CLI is deprecated ("will be removed") — a future release would break both required checks at once. Pinned `jsonschema==4.26.0` (current version; still ships the CLI). | version+CLI confirmed live; actionlint v1.7.7 + prettier clean |
| C14 | P3 | `validate-marketplace.yml` | The private-email leak guard used `if grep -rin … 2>/dev/null`, which treats grep exit 2 (a real scan error) the same as exit 1 (clean) → a scan error silently reported "OK no private emails" (a leak guard failing **open**). Split the exit codes: 0=leak→fail, 1=clean→ok, ≥2=error→fail loud. | 3-path isolated test + actionlint clean |
| C12 | P3 | `.prettierignore` | `researcher-reminder.yml` was excluded "until the template literal is refactored" — the refactor shipped (v0.194.0) and the file passes prettier@3.9.4. Removed the stale exclusion so the whole-tree format gate covers it. | whole-tree prettier --check clean |

All six are in non-substrate, non-security-control locations (top-level `scripts/`, `.github/`, root),
so they were safe to apply and validate autonomously.

---

## 2. Needs your decision / security review (NOT auto-fixed)

### Why not auto-fixed
Two independent reasons gate these:
1. **Substrate protection.** `command_review.enabled: false` in this repo, **but** four `shell_*`
   categories carry `thing: on`, so the tribunal's substrate self-disable floor still fires and **denies
   agent Write/Edit to `plugins/ravenclaude-core/hooks/**` and `plugins/ravenclaude-core/scripts/**`**
   (the documented reason `coordinator-lock.sh` shipped in `bin/`, and guard-destructive patches needed
   the special #1241 route). Every guard/tribunal fix below lives there.
2. **They are security controls.** Changing a guard's matching regex is exactly where a well-meant fix
   introduces a new bypass or false-positive. These want human + `security-reviewer` eyes, not an
   autonomous routine — which is also what the task's "issues that need design input → summary doc" asks.

> **Recurrence signal worth acting on:** `docs/reviews/2026-08-07-repo-review-maintainer-actions.md`
> already documented the `git reset --hard` fail-open (P1, with a ready patch) — never applied. These
> guard findings keep being *re-discovered* every review because the autonomous path is structurally
> blocked from fixing them. They need a deliberate human pass (edit from a session where the substrate
> exemption resolves, or via the API/CI route #1241 used).

### P1 — security-guard bypasses (defense-in-depth guards; Claude's native auto-mode classifier is the real backstop)
- **`guard-destructive.sh` heredoc bypass** (~L162): a heredoc body is only blanked when a *bare*
  interpreter precedes `<<`. `sudo bash <<'EOF'`, `nohup sh`, `timeout 5 bash`, `exec bash`, `ssh host
  bash`, `cat <<'EOF' | bash`, `cat <<'EOF' | sudo sh` all pass with a recursive delete in the body.
  → Match the interpreter through common wrappers/pipes.
- **`guard-destructive.sh` `git reset --hard`** (~L1857; = the 2026-08-07 P1): deny requires `--hard`
  immediately after `reset`; `git reset HEAD~3 --hard` / `-q --hard` / `--quiet --hard` slip through. A
  ready patch exists in the 2026-08-07 doc. → Apply it (make the flag match order-independent, like the
  already-fixed `git clean` sibling).
- **`guard-web-access.sh` host parse** (~L67, mirrored in `mark-web-domain-seen.sh:74`): host extraction
  doesn't stop at `?`/`#` and reads `@` in a query as userinfo → deny-list bypass (`https://evil.com?x=1`)
  and whitelist spoof (`https://evil.com?@good.com` parses as `good.com`). → Parse the authority
  correctly (stop at `/?#`, treat `@` as userinfo only before the first `/`).
- **`thing-concerns.py` self-disable carve-out** (~L387): strips double-quoted spans as inert *before* the
  metachar check, but `$(…)`/backticks inside double quotes still execute → `cat "$(rm -rf …/hooks)"` is
  judged read-only. → Don't treat `$()`/backticks inside double quotes as inert.
- **`thing-decision.py` leading-segment classification** (~L213, **needs design**): `classify()` routes
  on the first segment only and a clean low-tier command gets an explicit `allow`, so `ls && git push
  origin main`, `ls; npm install -g evil`, `echo hi | bash`, `find . -delete`, `cd /tmp && git push …`
  all clear with no panel. **This becomes P0 on Copilot, where the Thing is the only gate.** → Classify
  each segment of a compound command at the highest tier any segment reaches. (Design: this changes the
  review surface materially.)
- **`_scrub.sh` secret coverage** (~L51; also `thing-seat.sh:96`, `concerns-catalog.md:99`): scrub covers
  only `ghp_` and misses `gho_/ghu_/ghs_/ghr_` (**this env's `GITHUB_TOKEN` is a `ghu_` token**),
  `--api-key`, `--secret=`, `PGPASSWORD=`, non-JWT Bearer, AWS secret keys → they leak into
  `hook-events.jsonl`, deny stderr, and seat egress. `precompact-digest.py:95` already widened to
  `gh[pousr]_` — the canonical scrubber was left behind. → Port the widened pattern set to `_scrub.sh`.
- **`premise-gate.py` substring "settled"** (~L163): `any(s in settle for s in _SETTLED)` — "unsettled" /
  "not settled" contain "settled", so an unsettled inference exits 0 CLEAN. → Match the settle-state as a
  whole token, not a substring.
- **`premise-gate.py` phase detection** (~L60/277): only recognizes `## Phase N` / `P2` / bare-number
  headings; `## Phase A`, `### Step 1`, `## Stage 1`, `#### Task 3` → phases:0 → the unwired guard never
  fires and reports CLEAN ("cannot see means cannot report clean" violated). → Broaden phase recognition
  or fail-closed when a plan has over-floor content but zero recognized phases.

### P1/P2 — tribunal fail-open / config parse (substrate; human review)
- `thing-orchestrator.sh` reads the posture from the payload `.cwd` with no walk-up / `CLAUDE_PROJECT_DIR`
  fallback → a subdir cwd silently disables the whole tribunal incl. the hard-rule floor (`runaway-brake`,
  `dod-gate`, `worktree-guard` share the lookup). [the agent's cwd-tracking premise was unverified]
- `thing-orchestrator.sh:143` shell short-circuit accepts only lowercase `on|true|yes`; the engine's
  `_TRUTHY` also accepts `True/On/"on"/1` → `thing: True` silently disables the floors.
- `THING_SEAT_MOCK_VERDICT` (a test hook) is honored in production from the hook env / a repo
  `.claude/settings.json` `env` block, and is not covered by the self-disable guard.
- `thing-decision.py` file-shape self-disable only matches project-relative substrate — the **installed
  plugin cache** copy (the real runtime substrate) is not covered (the Bash-shape guard is). **needs design.**
- `dod-gate.sh` `except Exception: d={}` on PyYAML import → no PyYAML (stock macOS) ⇒ cmd empty ⇒ the
  blocking Stop gate silently exits 0 (header promises a "tolerant fallback" that isn't one).
- `route-decision-review.sh:69` aborts rc=1 under `set -euo pipefail` when the posture has no
  `decision_review:` key (this repo sets `binding`, so not triggered here, but a consumer would see it).
- `thing-seat.sh:243` `printf … | head -c 65536` under `set -euo pipefail` aborts 141 (SIGPIPE) on
  payloads >~64KB → the truncate path never runs, the seat abstains, large writes fail-closed.
- `guard-memory-compaction.sh` snapshots are second-stamped and the shrink limit is per-write → 5 rapid
  ~10% edits shrank memory 41% with 0 denies AND overwrote the one snapshot (the exact incident it exists
  to prevent).
- `runaway-brake.sh:169` `exec 9>"$f.lock" 2>/dev/null` permanently redirects the script's stderr to
  /dev/null → the brake trips but the reason message is lost.

### P1/P2 — repo-review cost/cardinality (why I did NOT run the full Workflow `/repo-review`)
- `repo-sweep.workflow.js` **logs the cost estimate but never clamps dispatch on it** — cold-cache review
  = `batches × dims × models × 2`, which exceeds the 1000-`agent()` Workflow cap past ~26 batches (this
  repo's plan is 363 batches). This is the **same failure class that burned ~98M tokens on 2026-09-09**,
  still unfixed. `estimate_cost.py` also has no converge-iteration term and its tier caps drift from the
  workflow's (ultra verify 160 vs 320). **needs design.** → This is why I used bounded direct `Agent`
  dispatch for the review instead of the Workflow-orchestrated `/repo-review`.
- `routine-reserve.py`: reserve projection/statusline/warn are frozen at SessionStart (a long session can
  exhaust the reserve silently); and an uncountable cron (day-names/`@daily`/6-field) → reserve 0,
  `estimated: False`, `state: ok` (under-states, wrong direction).

### P2 — other engine correctness (substrate)
- `thing-decision.py` shell_readonly prefixes are flag-blind: `find -delete/-exec`, `echo/cat` redirects,
  `git remote set-url`, `git branch -m`, `git log --output` classify as clean reads and are allowed.
- `apply-comfort-posture.py` emits `Bash(find:*)/echo/git branch/git remote` into the **allow** bucket →
  `find -exec/-delete` and `git branch -D` run without a prompt even at `shell_code_exec: deny`. **needs design.**
- `fix_summary.py` row-count invariant is tautological on the prod path; `applied` is an unverified agent
  self-report that drives `--converge`'s CONVERGED verdict; the captured patch ignores git failures and
  includes pre-existing dirty changes.
- `findings_merge.py` `_line_bucket` maps non-int lines (ranges like `10-12`, which the prompt allows) to
  bucket 0 → distinct same-title findings merge and the real location is lost; mixed int/str `id` → a
  `TypeError` that kills the Merge phase and the hand-recovery.
- `routine-reserve.py` `set_override` prints success even when `_write_json_atomic` swallowed an OSError;
  `conserve-tokens.py` prints a spurious "released" on the first prompt of a fresh session;
  `stall_watch.py` `proc_identity_ok` never compares `procStart` (PID-reuse undetected) and writes
  `ok:true` before dispatch; `context-usage-meter.py` block-regex matches the commented template header.
- `thing-denial-kb.py` stores `resolution/doc/category` unscrubbed and `recall` injects them into
  SessionStart context labeled "TRUSTED" → a persistent-injection surface. **needs design.**

### P2/P3 — CI / generators (editable but need careful gate re-validation)
- **`AGENTS.md:344` says "three" required checks; a live ruleset probe (by the review panel) found
  SEVEN** (the 3 `validate-*` + the 4 `github-protocol-*`). I could **not** first-hand re-verify (no `gh`
  / ruleset API in this environment), so I did not edit the doc. → Confirm the ruleset and update the doc.
- **Gate 242 (`check-inception-coverage.py`) protects only 3 of those 7** from a `paths:` filter — the 4
  `github-protocol-*` are unprotected (a `paths:` filter on one would hang docs-only PRs forever). None
  has a filter today (latent). → After confirming the ruleset, add the 4 to `REQUIRED_WORKFLOWS` and
  re-run Gate 242.
- **`check-skill-descriptions.py --check` (the cap+ratchet enforcement described in CLAUDE.md v0.320.0)
  is NOT wired into CI** — only `--self-test`/`--must-fail` are — and `--check` currently exits 1 (pinned
  `skill_count=956` vs current `961`). So the cap enforcement is not actually running. → Decide whether to
  wire `--check` and re-seed the pin.
- `check-workflow-hygiene.py`: Rule 1 accepts `permissions: write-all`; Rule 2 misses a multiline `uses:`;
  a missing dir → OK exit 0. Backstopped by zizmor here, but this is the sole enforcement in
  `init-agent-ci`-scaffolded consumer repos.
- `generate-copilot-plugin.py`: `project_tools` returns `[]` for both `*` and all-unmapped → an
  all-unmapped agent projects with **all tools** on Copilot (fail-open; latent, all 17 core agents map).
- `emit-codex-config.py`: `_TABLE` regex misses `[[array.of.tables]]` → the never-silently-weaken tighten
  logic skips those keys.

### P2/P3 — CI workflow hardening (mostly `quarantine-intake.yml`, public-repo intake)
- Spam cap counts open **issues** but every path closes them; real artifacts (PRs/branches) uncounted →
  cap never triggers (public repo). **needs design.**
- Intake PR is opened with `GITHUB_TOKEN` (no required checks run) and its title violates the
  Conventional-Commits check; body says "3 checks" (stale). **needs design** (PAT/App + conforming title).
- Reject path only comments+closes → a secret/PII body + edit history stay world-readable on the public
  repo. **needs design** (overwrite body / lock / rotate advice).
- Oversized issue body (~128KiB+) → E2BIG before the 64KiB reject path; issue stuck open, no comment.
- Required `github-protocol-secret-scan` / `pr-title` checks report green on `workflow_dispatch` without
  scanning/validating — and the quarantine PR body tells maintainers to re-run via dispatch. **needs design.**
- `inventory-sweep.yml` / `golden-set-inject-light.yml` "assert NOT required" self-checks grep the
  rulesets *list* endpoint (no `rules`) for the *workflow* name (contexts are *job* names) → can never
  fire (latent).
- `validate-macos.yml` concurrency (shared by schedule/dispatch/push + cancel-in-progress) → a push
  cancels the in-flight scheduled whole-tree macOS audit and the push run skips it → no audit that day.

---

## 3. Top questions for you
1. **Guard fixes** — approve a dedicated human/security pass to fix the P1 guard bypasses (heredoc,
   git-reset --hard, web-access host parse, tribunal segment classification, `_scrub` coverage,
   premise-gate substring/phase)? They can't be applied autonomously (substrate) and keep recurring. The
   git-reset one has a ready patch from 2026-08-07.
2. **`repo-sweep.workflow.js` cost clamp** — approve wiring `batches_affordable` to actually clamp/block
   dispatch (or block-mode split)? Until then, the full Workflow `/repo-review` remains a budget hazard.
3. **`AGENTS.md` 3-vs-7 required checks + Gate 242 coverage** — confirm the live ruleset so I can correct
   the doc and expand Gate 242 safely.
4. **`check-skill-descriptions.py --check`** — should its cap/ratchet enforcement be wired into CI (as
   v0.320.0 describes), and the `956→961` pin re-seeded?

---

## 4. Coverage & method (honest limits)
- **Complete** on the "broken now" axis: whole-tree json (186), shell syntax/exec (200), prettier,
  ruff, and every dashboard/index/concepts/copilot/codex/inventory freshness gate — all pass.
  (`ci-preflight.py` reports 2 FAILs, both non-defects: a transient toctou from my concurrent agents, and
  a `ratchet-merge-base` false positive — it mis-derives the base on a zero-commit branch where
  HEAD==origin/main; the seed file is byte-identical to main.)
- **Risk-sampled** on the semantic axis: 4 panels over the highest-churn / highest-blast-radius code
  (scripts/*.py, ravenclaude-core hooks/*.sh, .github/workflows, tribunal + repo-review engines). ~108
  code files reviewed. The ~7700 markdown/knowledge files and the 184 plugins' per-plugin `*_calc.py` +
  anti-pattern hooks were **not** individually reviewed — a true exhaustive semantic sweep of the whole
  tree is not feasible in one routine within budget.
- **Did not run `scripts/audit-gates.sh`** in full (700+ gates; inventory-sweep alone is 159s) — out of
  routine budget. Ran the specific gates my changes touch (actionlint v1.7.7 on the workflows; prettier;
  ruff; py_compile; the codex `--check`; a functional smoke test of F4).
- The findings' file/line numbers came from sonnet panelists; the ones I acted on I re-verified
  first-hand. Panelist line numbers on substrate files I could not edit may have drifted — treat them as
  locators, not exact anchors.

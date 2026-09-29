# Autonomous repo review — 2026-09-29

A scheduled multi-panel repository review ran on branch `claude/awesome-wright-s6c1en`.

**Structure.** Panel 1 = a deterministic baseline (the repo's own gates/lint, so findings are
reproducible, not speculative) **plus** four independent expert-review agents (Sonnet tier — the
"lighter model for categorization" per the routine's model-assignment directive) across
non-overlapping, risk-sampled slices: **(1A)** CI/CD workflow security · **(1B)** shell hook safety ·
**(1C)** the core Python engine (`scripts/`) · **(1D)** the shipped Python engine
(`plugins/ravenclaude-core/scripts/` + hooks). The orchestrator (Opus) served as Panel 2 (priority
validation, impact/effort) and Panel 3 (tie-breaking / de-escalation), and re-verified every finding
it acted on against a **pristine `git archive HEAD` tree** to separate real defects from
local-checkout artifacts.

**This routine has run before — its prior PRs are open and unmerged, so their fixes are *claimed*
(must not be duplicated):** **#1265** (2026-09-28) and **#1258** (2026-09-24) whole-repo reviews, plus
**#1263** (a `routine-reserve` write-failure fix). Their conclusion held again: the repo is healthy
and heavily gated, and the auto-fixable low-hanging fruit was largely picked in prior runs. This run
therefore targeted *genuinely new* findings and cross-references the rest.

**No P0 surfaced.** The deterministic floor is fully green: `py_compile` over all 434 tracked `.py`,
`bash -n` over all 332 `.sh`, JSON validity (the only two "failures" are `devcontainer.json` files,
which are legitimately JSONC — CI does not validate them as plain JSON), `ruff check .`, and
`prettier --check .` all pass. No `eval`, no `shell=True`, no bare `except:`; the 17 workflows are
39/39 SHA-pinned with a permissions floor and no injection (zizmor 0 findings); the guard/tribunal
layer held up under manual trace and fuzzing (11 hook scripts fuzzed with 19 malformed payloads → no
tracebacks). The two `ci-preflight` FAILs this run are checkout artifacts, not defects (see below).

---

## Implemented in the accompanying PR (confirmed + validated — no decision needed)

Both fixes are in root `scripts/` (not inside any plugin, not the tribunal substrate, not touched by
open PRs #1258/#1265), so there is **no plugin version bump and no generated-file churn**. Each was
reproduced and validated before/after; `ruff` clean.

### P2
- **`scripts/check-inception-coverage.py:77` — a `git mv` into a gated root bypassed the coverage
  forcing function.** `added_artifacts()` diffed with `--diff-filter=A`, so a file *moved or copied*
  into `plugins/ravenclaude-core/{hooks,skills,agents,scripts,commands}/` showed up as a Rename/Copy,
  not an Add, and was never required to be named in an inventory `covers[]`. Changed to
  `--diff-filter=ACR`, matching the sibling precedent at `check-layout.py:93`.
  *Validation:* proven in a scratch repo (`git mv loose.sh gated/moved.sh` → `A` prints nothing, `ACR`
  prints `gated/moved.sh`); `--must-fail` still exits 3 (all three teeth intact); `--check` exits 0 on
  HEAD (empty diff on this branch, so no gate-result change now).

### P3
- **`scripts/content-scan.py:245` — fail-safe fetch didn't catch the errors it promised.** The
  docstring says "'' on any error," but the `except` caught only `(URLError, HTTPError, ValueError)`,
  so a mid-body `ConnectionResetError` / socket read-timeout (both `OSError`, not `URLError`) aborted
  the whole scan and lost the not-yet-written digest. Broadened to
  `(OSError, http.client.HTTPException, ValueError)`.
  *Validation (observation, not inference):* `URLError`/`HTTPError` **are** `OSError` subclasses (nothing
  dropped); `ConnectionResetError`/`socket.timeout` **are** `OSError` (gap closed); `IncompleteRead` **is**
  `HTTPException`. Opt-in research CLI only.

---

## `ci-preflight` FAILs — both resolved as NON-actionable (verified on a clean tree)

1. **`hotspot:3b-index-freshness`** — `index.html` reported stale locally, but on a pristine
   `git archive HEAD` tree `generate-index-dashboard.py --check` reports **"up to date" (exit 0)**. The
   local "stale" was caused by gitignored `__pycache__/*.pyc` inflating a template count (this is
   finding **B-10** below). `index.html` regeneration is owned by the `regenerate-artifacts.yml`
   post-merge self-heal (which ran green on the current tip), so regenerating/committing it here would
   only churn a timestamp and could race the workflow. **Left untouched, deliberately.**
2. **`hotspot:1-ratchet-merge-base`** — `artifact-budgets.seed.json`'s stamp is behind the merge-base;
   the preflight itself frames this as "re-measure on rebased HEAD before merge," a deliberate maintainer
   operation (already tracked as #1265 design-input #11). Not applicable to a PR that touches no ratchet
   files.

---

## Design-input — needs your decision (NOT auto-applied)

Confirmed by a panel but deliberately not force-applied by an unattended session.
`[SUBSTRATE]` = editing `plugins/ravenclaude-core/hooks/` or `.../scripts/` is tribunal-blocked for
autonomous edits. `[CASCADE]` = a fix inside `ravenclaude-core` triggers the plugin version-bump +
`generate-copilot-plugin.py` regen. Line refs are on the current `main` (4b35028).

### A. Highest-value — guard/tribunal security & integrity (all `[SUBSTRATE]`/`[CASCADE]`)

1. **(P1) Tribunal pre-LLM screen fails OPEN on large padded input — a bypass (1D-1).** The screen is
   *quadratic* (not catastrophic backtracking — this refines #1265's "ReDoS-clean at 20K" to "blows up
   at scale"): `thing-concerns.py:153` `_flatten` `\s*\n\s*` plus the `git\s+push\b[^|&;\n]*` catalog
   regexes, with **no Bash-command size cap** and **no timeout on the python call**
   (`thing-orchestrator.sh:161,164`). Measured by Panel 1D: a 130K-space Bash command took **113 s** and
   a 300K Write payload **195 s**, against the **90 s** hook timeout — and the repo's own doc says a
   timeout fails open, so a padded command slips the tribunal screen. **`guard-destructive.sh` is
   unaffected** (it blocked the same padded force-push in 0.6 s), so the deterministic destructive-command
   backstop still holds. **Recommendation:** add a size cap (reject/deny oversize payloads pre-regex) and
   a hard deadline that fails *closed* on the tribunal screen. Needs a design decision on the cap and
   the fail-closed semantics.
2. **(P1) Self-disable floor bypass (1D-2).** `_self_disable_read_only` treats `"$(rm …)"` inside double
   quotes and `rg --pre …` as inert, so with `shell_readonly` toggled off, `ls "$(rm -f <hook>)"` is
   allowed. **Recommendation:** parse command substitutions inside quotes; treat `rg --pre`/`--search-zip`
   as executing.
3. **(P1) `install_launch_guard.py --uninstall` silently discards later rc-file edits (1D-3).** Uninstall
   overwrites the user's shell rc with the pre-install snapshot and takes no backup, so any edits made
   after install are lost. **Recommendation:** back up the current rc before restoring, or surgically
   remove only the guard block.
4. **(P1) WebFetch/MCP body sanitizer DoS (1D-4).** `sanitize-webfetch-body.py:113` `^\s*` takes **245 s**
   on 100 KB of blank lines, and the two sanitizer hooks (`hooks.json:51,89`) have no `timeout`. Same
   class as #1 (unbounded input × superlinear regex). **Recommendation:** bound input size and add a hook
   timeout.
5. **(P2, security) `_write_settings_json_atomic` widens `settings.json` perms 0600 → 0644 (1D-8).** The
   atomic writer creates the temp file with default mode, exposing a previously owner-only settings file.
   **Recommendation:** preserve the source mode (or `chmod 0600`) on the replacement.
6. **(P2, fail-open) A malformed posture with `thing: on` silently disables the tribunal (1D-6).**
   `posture_error` is computed but never consumed, so a parse error opens the gate instead of failing
   closed. **Recommendation:** treat a posture parse error as fail-closed for `thing`.
7. **(P1, security, fail-OPEN) `guard-web-access.sh` host-extraction bypass — `[KNOWN = #1258 F1]`
   (1B-1).** The parser never terminates the host at `#`/`?`, so `https://evil.test?u=@allowed.example`
   reads as the allowed host and a denied host slips the blacklist; `mark-web-domain-seen.sh` shares the
   parser. #1258 carries the exact RFC-3986 patch for the sanctioned route — **worth landing.**
8. **(P2) `route-decision-review.sh` exits 1 on every `AskUserQuestion` when the posture has no
   `decision_review` key — confirmed by TWO independent panels (1B-4 = 1D-5).** Should no-op-allow
   (grep, exit 0) when the key is absent.
9. **(P1, verified live) `dod-gate.sh` `trusted: true` is defeated by a two-commit change (1B-2);
   `web_access.trusted` has no defence (1B-3).** The git-blame commit-separation proof that authorizes a
   `trusted` Stop-hook command can be bypassed by splitting the change across two commits → arbitrary
   command at Stop. **Recommendation:** bind the trust proof to the command content (hash), not commit
   separation.

### B. Gate-integrity / gate-wiring (root scripts — fixable in a focused follow-up)

10. **(P1/P2) `generate-index-dashboard.py` counts working-tree files, incl. gitignored ones (1C-1).**
    `_count_dir()`/`_scan_templates()` walk the working tree, so a stray `__pycache__/*.pyc`/`.DS_Store`
    changes the committed, CI-diffed `index.html` (this is why the local `ci-preflight` reported stale).
    **Reproduced with a control** (clean `git archive HEAD` tree is fresh; adding one `.pyc` flips it
    stale). *Held:* the file is touched by open PR #1265 (a different hunk) and it is an output-affecting
    generator change — land after #1265. **Fix:** count from `git ls-files` (fallback: walk skipping
    `__pycache__`/`*.pyc`/dotfiles), matching the `census-must-be-independent` concept. Output-preserving
    on a clean tree.
11. **(P1/P2) `check-skill-descriptions.py --check` is documented as blocking but never wired into CI,
    and red on HEAD (1C-2).** Verified this session: `audit-gates.sh` invokes it only as `--self-test`
    (line 10985) and `--must-fail` (10987) — the posture-drift enforcer `--check` appears in no workflow
    or gate; it exits 1 on a clean tree (pinned `skill_count=956`, current `961`), and the token half
    silently no-ops where `tiktoken` is absent (CI never installs it). **Decision needed:**
    enforce-vs-advisory. If enforce → re-seed the pin 956→961 (a deliberate maintainer op) + wire into
    Gate 281 + make the tiktoken skip explicit. If advisory → correct the CLAUDE.md "blocks" claim.
12. **(P2) `check-nuance-floor.py --check` never run on the real corpus, red on HEAD (1C-3).** Verified:
    Gate 241 invokes only `--golden` (frozen fixtures, lines 1169/9784) + `--must-fail` (1170/9787); the
    real-corpus `--check` is in no workflow or gate and exits 1 (25 entries fail the shape/falsifiability
    floor). Consistent with `main` CI being green — the meta-gates *are* wired; only the real-corpus
    `--check` is advisory-by-current-design ("P3 armed"). **Decision:** enforce (with a grandfather list)
    or document as advisory.
13. **(P2) Gate scripts fail-open on a flag mistake (1C-12).** 11 gate scripts use
    `return rc if args.check else 0`; `inventory-sweep.py --check --json` already exits 0 regardless of
    the verdict, and dropping `--check` from any workflow silently turns a gate into a no-op. **Fix
    (concrete, isolated):** compute the verdict before the `--json` branch in `inventory-sweep.py`;
    longer-term make gate the default and require explicit `--report` for exit-0.
14. **(P2/P3) Budget/append-only ceilings can be loosened in place (1C-11).** `check-artifact-budgets.py`
    only compares adjacent rows in the same file, so editing the last row upward passes every gate.
    **Fix:** compare against the merge-base copy and require append-only history (root script — good
    follow-up-PR candidate).
15. **(P2) 50 unquoted `${CLAUDE_PLUGIN_ROOT}` hook commands in `hooks.json` fail open on paths with
    spaces (1B-6) `[CASCADE]`.** A consumer whose cache path contains a space silently loses every hook.
    **Fix:** quote the interpolated path in each command string.
16. **(P2) `ledger.py` `read_ledger` is quadratic (1D-9)** — re-splits the whole shard per line; and
    learned denial-KB resolutions are re-injected at SessionStart unbounded and unscrubbed (1D-10).
    `[SUBSTRATE]`

### C. Lower-priority / latent (P3) — safe fixes deferred to keep this PR tight

- **1C-6** `ci-preflight.py` `check_unstaged_sensitive_paths()` returns PASS (not UNAVAILABLE) when
  `git status` errors/times out (fail-open on a local advisory tool).
- **1C-7** `check-md-links.py` inline-code regex `` `[^`]*` `` spans blank lines, hiding 25 links (4
  relative, all currently resolvable); the `copilot` exclusion is broader than its docstring.
- **1C-8** `check-shipped-references-resolve.py` skips any `#`-led line, but the corpus is markdown where
  `#` is a heading — a heading referencing a non-shipping script is never checked.
- **1C-5** `_html_merge.scope_css` latent mis-scoping (`html[attr]`, `}` in strings, `@scope`/
  `@starting-style`) — none in today's CSS.
- **1C-10** `concepts.py compute_covers_digest()` doesn't normalise CRLF → permanent false drift on a
  Windows (autocrlf) checkout. Inferred (not run on Windows).
- **1C-13** `check-changed-concept-renders.py` runs a whole-corpus check despite a "scoped to changed
  concepts" docstring.
- **1A** workflow hardening: **1A-1** the "assert NOT a required check" steps in `inventory-sweep.yml` /
  `golden-set-inject-light.yml` grep the rulesets *list* (names, not check *contexts*) so they can never
  fire — a dead self-protective control (Panel 1A verified against a positive control: the same grep also
  misses "Validate manifests and hooks", which the ruleset detail confirms IS required); **1A-2**
  `SELF_HEAL_PAT` shares a job with unpinned `pip`/`npx` installs (split generate/publish);
  **1A-3/4/5** minor (no `--match-head-commit` on the self-heal merge; secrets not Environment-scoped;
  the paths-guard covers 3 of 7 currently-required checks).
- **1D-11..1D-17** `[SUBSTRATE]` ledger crashes on malformed records; `audit_dir` traversal; ledger
  timestamp double-clock; `reset-plugin-cache.py` TTL never enforced; `shlex` corruption hardening;
  mock-verdict env hooks in the production path; `install_stall_watch.py` hard-coded label + no platform
  check.
- **1B-5..** `[SUBSTRATE]` `runaway-brake.sh` loses its block message on Linux (`exec 2>/dev/null`);
  `enforce-git-protocol.sh` denies heredoc commit messages in block mode; `log-probe.sh` doesn't
  sanitise the session id (path-traversal write); `dod-gate.sh`/`remind-tests.sh` miss new untracked dirs
  and no-op without PyYAML; **1D-7** without PyYAML every tool call is denied with a misleading "tamper"
  message.

### D. Carried from prior runs — still open (not re-derived)

**#1265 design-input #1–#13** (guard-destructive segment-scoping, log-probe status-code,
context-usage-meter Grok precedence, repo-review engine cost caps, check-workflow-hygiene Rule 1,
guard-memory-compaction integer-division, routine-reserve type-guard, fix_summary returncode,
coordinator-lock atomicity, inventory-sweep quadratic, ratchet stale, `_emit-event` C0 escaping,
`repo_map` tie-break) — re-confirmed still open where checked; see #1265's
`docs/reviews/2026-09-28-repo-review.md`.

---

## Repository visibility vs "private" documentation (P3, doc-only — owner call)

The GitHub API reports this repo **public** (`"private": false`, topic `public`, Pages enabled, 7
stars / 1 fork — evidently intentional), while `AGENTS.md`, `CLAUDE.md`, and the README tagline call
the marketplace "private." **This is a documentation inconsistency, not a data leak:** `marketplace.json`
and the plugin manifests use name-only `author`/`owner` blocks (no email), so the House Rule's
"strip email before public" requirement is already satisfied (the `"email"` tokens are just the
*keyword* in the email-engineering plugin). `matt@ravenpower.net` appears only in docs / `SECURITY.md`
/ a workflow — expected in a knowingly-public repo. **Recommendation:** align the "private" language
with reality, or confirm public-by-design and update the docs.

---

## Panel artifacts

Per-agent raw findings, the clean-tree verification, and the orchestrator decision log are in the
session run directory `.ravenclaude/runs/repo-review-2026-09-29/` (`panel1{a,b,c,d}-*.json`,
`clean-tree-verification.md`, `decisions.md`) — local-tier, gitignored, not committed.

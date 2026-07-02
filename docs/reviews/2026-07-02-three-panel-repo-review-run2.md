# Repository review — 2026-07-02 (run 2, multi-panel, autonomous fixes)

Second autonomous three-panel review of the day (an earlier pass landed as **#545** + **#546**).
Structure: **Panel 1** (expert fan-out, categorize P0–P3) → **Panel 2** (validation + impact/effort) →
**Panel 3** (opus tie-break on ambiguous items). The review ran across the actionable code surface
(core hooks, core/repo scripts, CI workflows, ~155 plugin advisory hooks, ~108 plugin calculators,
manifests, doc-accuracy).

**Every finding below was re-verified against fresh `origin/main`** (`9ea9e1c`), because this session's
checkout started ~a week stale — so the reviewer's own numbers had drifted and several candidate findings
were already fixed by #545/#546. Only genuinely-present, net-new issues were acted on. Guard-destructive
findings were reproduced with a live exploit harness before and after the fix.

Baseline going in was green (JSON validity, `bash -n`, `py_compile`, ruff, prettier whole-tree,
frontmatter, layout, marketplace-claims structural, version-drift, and the full `audit-gates.sh`
meta-test — **489 pass / 0 fail**). The panels surfaced defects the gates can't see: regex *semantics*
inside hooks, exit-code *meaning* under Claude Code, and a doc that contradicts its own hook.

---

## A. Fixed autonomously in this PR (reproduced before, verified after)

### P0 — security: the primary consumer catastrophe-guard had a path-qualified bypass

- **`plugins/ravenclaude-core/hooks/guard-destructive.sh`** — the four structural danger checks
  (`_is_dangerous_rm` / `_chmod` / `_find` / `_truncate`) anchored the command name only after
  start-of-string / `;` / `&` / `|` / whitespace. That class excludes `/`, so a **path-qualified**
  invocation — `/bin/rm -rf /`, `./rm -rf ~`, `/usr/bin/chmod -R 777 /` — was never matched, and no
  `deny_patterns[]` entry backstops rm/chmod/find/truncate. The hook's own header calls it the consumer's
  "PRIMARY deterministic guard on the `/plugin install` path", so this was a full, silent bypass via a
  textbook absolute-path evasion. **Reproduced live** (all three ALLOWED pre-fix), then fixed by adding
  `/` to the left-boundary class of all four checks. Verified: all three now BLOCK (exit 2), with 6
  no-false-positive controls still ALLOWED and the whole Gate-5 corpus (24 fixtures) still green.

### P2 folded into the same guard fix (two more missed forms)

- `_is_dangerous_find` missed **`-execdir`** (the per-match twin of `-exec`) — `find / -execdir unlink {} +`
  and `find /etc -execdir shred {} +` bypassed. Fixed: `-exec(dir)?`.
- `_is_dangerous_truncate` missed the long-option **`--size=0`** spelling of `-s 0` —
  `truncate --size=0 /etc/passwd` bypassed. Fixed to accept `-s 0` **and** `--size=0` / `--size 0`.

### P1 — advisory hooks whose documented STRICT/blocking mode silently did nothing

In Claude Code a PreToolUse hook blocks with **exit 2**; exit 1 is a non-blocking error that is silently
swallowed. Three PreToolUse anti-pattern hooks implemented their opt-in blocking mode with `exit 1`, so the
enforcement mode was inert:

- **`plugins/azure-cloud/hooks/check-azure-anti-patterns.sh`** (`AZURE_STRICT=1`) — `exit 1` → `exit 2`.
- **`plugins/claude-app-engineering/hooks/check-claude-app-anti-patterns.sh`** (`CLAUDE_APP_STRICT=1`) — `exit 1` → `exit 2`.
- **`plugins/microsoft-fabric/hooks/check-fabric-anti-patterns.sh`** (`FABRIC_STRICT=1`) — `exit 1` → `exit 2`
  (its header comment even documented "blocking (exit 1)"; corrected too).

  *(The other ~10 PreToolUse anti-pattern hooks were checked and already use `exit 2` correctly.)*

### P1 — a doc that told consumers to make a PII guard that doesn't block

- **`plugins/regulatory-compliance/CLAUDE.md`** — instructed "for **SAR / STR drafting** … flip the bottom
  `exit 0` to `exit 1` so the hook blocks the write." A consumer following it verbatim got a hook that
  still allowed PII writes on the plugin's highest-stakes control. The hook's own header + runtime comments
  already said `exit 2`; the doc now matches. (Doc-only; the hook was already correct.)

### P2 — earned-value forecast computed from a display-rounded CPI

- **`plugins/construction-general-contractor/scripts/construction_calc.py`** — `EAC = BAC / CPI` was computed
  from the 4-decimal-rounded `cpi`, introducing avoidable dollar-scale rounding drift (e.g. ~$1.43 at
  BAC $1M with a non-clean CPI, scaling with BAC). Now computed from the exact ratio `BAC * ACWP / BCWP`.

### P3 — CI script-injection hardening + a stale catalog count

- **`.github/workflows/validate-layout.yml`** — `github.base_ref` was interpolated directly into a `run:`
  script; moved to `env:` (`$BASE_REF`), the GitHub-documented hardening for untrusted `github.*` context.
- **`.claude-plugin/marketplace.json`** — `metadata.description` said "**99** domain plugins"; the actual
  non-core count on fresh main is **130**. Corrected. (This phrase is not covered by
  `check-marketplace-claims.py`, so it does not self-heal — see §C.)

**Version bookkeeping:** `ravenclaude-core` 0.184.0→0.184.1 (+ copilot mirror), `azure-cloud` 0.5.1→0.5.2,
`claude-app-engineering` 0.9.6→0.9.7, `microsoft-fabric` 0.8.4→0.8.5, `regulatory-compliance` 0.12.1→0.12.2,
`construction-general-contractor` 0.1.0→0.1.1 — each synced to `marketplace.json` (no drift), CHANGELOG top
entries added where the plugin ships one.

---

## B. Needs your design input (NOT auto-fixed — a judgment call, and the surface is security-sensitive)

Each item is a real, verified finding whose *fix shape* is a decision, so it's teed up here rather than
committed. The quarantine items in particular touch untrusted-external-content intake + GitHub Actions.

### B1 — Quarantine intake: "handled" signal can fire with no PR (P1)

`​.github/workflows/quarantine-intake.yml:167-178` posts "queued for review as a pull request: <url>",
labels `staged`, and **closes the issue** gated only on `steps.process.outputs.action == 'stage'` — with
**no check that the PR was actually created**. `peter-evans/create-pull-request` exits silently with empty
outputs when there is no diff (e.g. a re-labeled issue whose deterministic staged content is byte-identical
to an existing branch). Result: the tracking issue reads "reviewed and queued", the issue is closed, and no
reviewable PR exists — a false "handled" on the first human gate for untrusted content (not a code-injection
path; the damage is a lost audit trail + false assurance).

- **Recommended fix:** add `steps.pr.outputs.pull-request-number != ''` to the close/success step's `if:`,
  plus a companion step (inverted condition) that comments "no new PR was created — check the existing
  quarantine branch/PR", applies a `needs-maintainer-attention` label, and **does not** close the issue.
- **Why deferred:** it's a security-sensitive intake workflow and the exact remediation (new label name,
  message, whether to reopen) is a maintainer call.

### B2 — Quarantine PRs never trigger the PR-gated validation workflows (P2)

`​.github/workflows/quarantine-intake.yml:139` — PRs opened by `peter-evans/create-pull-request` with the
default `GITHUB_TOKEN` do **not** trigger `pull_request`-triggered workflows (GitHub's loop-prevention), so
a quarantine PR lands with **no CI checks run**. Options are architectural (a PAT/app token vs. an explicit
`workflow_dispatch` re-trigger vs. accepting manual review as the gate) — your call on the trust/automation
tradeoff.

### B3 — "PostToolUse hook can be made blocking" is structurally impossible (P2)

Several plugin `CLAUDE.md` files (e.g. `plugins/power-platform/CLAUDE.md:173`) tell consumers a **PostToolUse**
hook can be made "blocking" by flipping its exit code. PostToolUse fires *after* the edit has already
completed, so exit 2 surfaces stderr to the agent but **cannot block the write**. This is the mirror of the
A-section PreToolUse fix, but the correct rewording is a decision (drop the claim? reframe as "advisory
signal only"? move the check to PreToolUse?) spanning multiple plugin docs — worth one consistent pass.

### B4 — `docs/architecture.md` is materially stale (P2)

- The top Mermaid diagram shows only ~15 domain plugins and lists **Salesforce as a not-yet-shipped "future
  plugin"** (it shipped); the per-plugin summary table has undercounted skill/agent/hook counts for ~35+ rows.
- **Deferred because** rendering 130 plugins in one hand-maintained diagram is a layout/design decision, and
  the table arguably wants a generator (it is not in the `regenerate-artifacts.yml` self-heal set today).
  Options: prune the diagram to categories, or generate the table — your preference.

---

## C. Verified and deliberately NOT changed (recorded for honesty)

These surfaced in Panel 1 but were dropped after verification against fresh main — acting on them would be
noise or a regression:

- **Already fixed by today's #545/#546:** `apply-comfort-posture.py` unguarded `json.loads` on
  `settings.json` (now guarded); the `$IFS`/backslash/git-global-option guard-destructive bypasses; the
  `check-grep-ere-pcre.py` `--extended-regexp` long-option hole (added in #545).
- **Count drift self-heals — left alone on purpose:** `marketplace.json` per-plugin skill counts (says
  "46 skills" for ~110 plugins), the README "119 plugins" / core "44 skills / 19 hooks" claims, etc. These
  are rewritten post-merge by `regenerate-artifacts.yml` → `check-marketplace-claims.py --fix`, and PR CI
  runs `--structural-only`, so they neither block this PR nor need hand-editing (PR #530 documents this as
  the accepted, self-healing state). The one count that is **not** in that set — `metadata.description`'s
  "99 domain plugins" free prose — was hand-fixed in §A; consider adding it to the claims checker so it
  stops recurring.
- **No reachable exposure:** `check-grep-ere-pcre.py` still misses the deprecated `egrep` spelling, but no
  hook uses `egrep`; the `validate-marketplace.yml` "Verify hooks are executable" step treats a zero-glob
  match as a pass, but `plugins/*/hooks/*.sh` always matches many hooks here.
- **`audit-gates.sh` Gate 4** unit-tests the exec-bit primitive on one hardcoded hook rather than looping
  the corpus. Broadening it is defensible but low-value: the *functional* exec-bit enforcement is the CI
  "Verify hooks are executable" step (which does loop all hooks), and the real reason a non-exec hook
  shipped recently was CI not auto-running on a remote-session push (`c47bfe9` fixed that hook) — a
  gate-coverage change would not have caught it. Noted for a future pass, not fixed here.

---

## Verification this session

- Guard-destructive: live exploit harness — 3 path-qualified + 2 `-execdir` + 2 `--size=0` bypasses ALLOWED
  pre-fix → all BLOCK (exit 2) post-fix; 6 benign controls still ALLOWED; the exact `audit-gates.sh` Gate-5
  corpus (24 fixtures) still green.
- Exit-code fixes: enumerated all ~22 anti-pattern hooks; confirmed exactly 3 PreToolUse hooks used `exit 1`
  in STRICT mode; the rest already `exit 2`.
- Full suite: `python3 -m json.tool` (all manifests), `ruff` (clean), `prettier --check .` (exit 0),
  `check-frontmatter.py`, `check-layout.py --all`, `check-grep-ere-pcre.py`, `check-marketplace-claims.py
  --structural-only`, version-drift (none), and **`scripts/audit-gates.sh` — 489 pass / 0 fail**.

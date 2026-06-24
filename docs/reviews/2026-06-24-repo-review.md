# Repository review — 2026-06-24 (scheduled routine)

A scheduled, unattended routine ran a comprehensive repo review and resolved everything that did not need a human decision. This document is the residue: the **design-input questions** for Matt, each with a recommendation and a link to the exact code.

## How this was produced

- **Grounding pass** — ran the repo's own gates (`audit-gates.sh`, `check-*.py`, prettier, ruff, actionlint, layout) to surface confirmed, reproducible issues rather than speculation.
- **Three-panel review** (`Workflow`, model-by-complexity): Panel 1 expert finders (Sonnet) scanned the executable surface — gate scripts, dashboard generators, core hooks, core Python, shell tooling, CI workflows — and categorized P0–P3; Panel 2 (Sonnet) validated priorities and added impact/effort; Panel 3 (Opus, high effort) tie-broke ambiguous priorities. 22 findings survived validation (P1×4, P2×13, P3×5).

## Headline: `main` CI was red for 24h+ (now fixed)

Two CI workflows had been failing on every `main` commit since 2026-06-23 (10+ consecutive runs, merged over):

| Workflow | Root cause | Fix (committed) |
|---|---|---|
| **Validate Layout** | `.claude/agent-memory/**` (committed in #486) matched no `allowed_globs`, so the `check-layout.py --all` full-tree backstop failed. | Added `.claude/agent-memory/**` to `.repo-layout.json`. |
| **Validate Marketplace** | `audit-gates.sh` Gate 12 `must_fail` audit hard-coded the literal `'43 skills'`; #498 reworded the catalog prose so that string no longer exists → the planted-bad-value substitution became a no-op → the gate could not be made to fail → the meta-test reported a false failure (486 pass / 1 fail). | Replaced the hard-coded literal with a drift-proof **injected** wrong claim (`actual+100 skills`). |

After both fixes: `audit-gates.sh` = **487 pass / 0 fail**; `check-layout.py --all` green.

## Implemented in this PR (no design input required)

| Pri | Area | Fix |
|---|---|---|
| P0 | CI | layout allow-list + audit-gates fixture (above) |
| P1 | bug | `mark-web-domain-seen.sh` resolves session via `_ee_resolve_session` (payload `.session_id`) like `guard-web-access.sh` — the web first-use trust gate no longer re-prompts every fetch on native Claude Code |
| P1 | security | `thing-decide.py` passes `[question, context]` to `_sanitize_reasoning` (context was exempt from the JudgeDeceiver echo-block) |
| P1 | bug | `cleanup-branches.sh` exits 4 on a failed `git branch -D` / remote delete instead of silently exiting 0 |
| P1 | ci | `researcher-reminder.yml` cron fixed (`0 10 1-7 * 1` fired ~10×/month via POSIX DOM-OR-DOW) → `0 10 * * 1` + first-Monday guard |
| P2 | bug | `serve-dashboards.py` `/__runs` guards `stat().st_mtime` against a mid-request dir delete (both server copies, parity preserved) |
| P2 | bug | `archive-branch.sh` `--reason`/`--evidence` with no value → clear error, not silent `shift 2` exit 1 |
| P2 | bug | `ravenclaude update` forwards args (`--project` was dropped) |
| P2 | security | least-privilege `permissions: contents: read` on the 3 validate-\* workflows |
| P3 | bug | `notify.sh` no-jq fallback escapes backslash/control chars (was quote-only) |
| P3 | ci | `validate-marketplace.yml` reads name/version with `jq` (was `python3 -c` interpolating `$manifest`) |

## Needs design input — questions for Matt

Each is a real, validated finding deliberately **not** auto-implemented because the fix is a judgment call, a breaking change, or carries CI-regression risk under "merge on green."

### 1. `set -e` in the fail-open hooks — standardize or keep intentional? (P2/P3)

Three hooks use `set -uo pipefail` (no `-e`): [`dod-gate.sh:23`](../../plugins/ravenclaude-core/hooks/dod-gate.sh), [`runaway-brake.sh:23`](../../plugins/ravenclaude-core/hooks/runaway-brake.sh), [`copilot-hook-adapter.sh:36`](../../plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh). Panel 3 found that adding `-e` changes **zero** behavior today (every error path is already `|| true` / `|| exit 0` guarded) and that omitting `-e` is a **coherent, intentional fail-open pattern** for these guardrail hooks (e.g. `copilot-hook-adapter.sh:24-26` documents "always exits 0 so a translation hiccup never wedges the tool").

- **Recommendation:** leave as-is; the omission is intentional, not an oversight. If you want belt-and-suspenders, add `set -euo pipefail` to all three *and* keep the explicit guards (cosmetic uniformity, no behavior change).
- **Question:** Standardize on `set -euo pipefail` across all hooks for consistency, or keep the documented fail-open `-uo` in these three?

### 2. `stream-ops.py` — enforce the declared allowlist, or fix the comment? (P2, bug)

[`stream-ops.py:268,326`](../../plugins/ravenclaude-core/scripts/stream-ops.py): `_validate_event_fields` enforces only the 6-entry **denylist** (`_FORBIDDEN_EVENT_KEYS`); the comment at line 326 claims "every persisted key must be an allowed derived field," and `_ALLOWED_EVENT_FIELDS` (line 67) is defined but never used. So a non-forbidden key (e.g. `filename`, `raw_path`) can be written via `extra`.

- **Recommendation:** switch to allowlist enforcement (reject any key not in `_ALLOWED_EVENT_FIELDS`) — it matches the no-egress invariant's intent. **But it is a breaking change** for any current `extra` caller using a key outside the allowlist, so it needs your call.
- **Question:** Enforce the allowlist (stricter, breaking) or downgrade the comment to describe the denylist (status quo)?

### 3. `_sanitize_reasoning` 40-char echo-block window (P2, security)

[`thing-decide.py:402`](../../plugins/ravenclaude-core/scripts/thing-decide.py): `if len(u) >= 10 and u[:40] in sanitized` only checks the **first 40 chars** of each user-controlled field, so a seat echoing a user substring starting at char 41+ evades the verbatim-echo block. Downstream the 256-char cap + untrusted-data prefix bound the damage.

- **Recommendation:** widen the window (e.g. sliding-window or check the full field) — note this also requires mirroring in the shell layer (`route-decision-review.sh §4a`) to keep Gate 20's drift check green, and has a small perf cost on long fields.
- **Question:** Widen the echo-block beyond 40 chars (accepting the dual-layer change + perf cost), or accept the current bound given the 256-cap mitigation?

### 4. `check-marketplace-claims.py` regex coverage (P2, tech-debt — two items)

- **`AGENTS_RE` under-matches** ([line 78](../../scripts/check-marketplace-claims.py)): only `specialist`/`strategist` prefixes are recognized, so a future plugin describing itself as "5 AI agents" / "5 domain agents" yields no claim → the agent-count drift gate silently no-ops for it. **Risk:** broadening the regex could surface a *currently-drifted* plugin and fail CI on this PR — which is why it's deferred under merge-on-green.
- **`README_PLUGINS_RE` comment overstates anchoring** ([lines 83/87](../../scripts/check-marketplace-claims.py)): `(\d+)\s+plugins\b` could match a subset-count sentence ("comparing 5 plugins and 12 plugins"); the "cannot false-positive" comment is misleading. README prose doesn't currently trigger it.
- **Recommendation:** broaden `AGENTS_RE` to `(?:\w+\s+){0,2}?agents?` in a **dedicated** PR so any drift it surfaces is fixed in the same change (not mixed into this one); fix the `README_PLUGINS_RE` comment to match reality (or tighten the regex to the canonical "ships **N plugins**" form).
- **Question:** Want me to do the `AGENTS_RE` broadening as a follow-up PR (and fix any drift it finds)?

### 5. Pin `peter-evans/create-pull-request` to a SHA (P2, security)

[`quarantine-intake.yml:137`](../../.github/workflows/quarantine-intake.yml) uses `@v6` (mutable tag) in a workflow that processes **untrusted external issue bodies** and holds `contents: write` + `pull-requests: write` + `issues: write`. A moved upstream tag could run arbitrary code in this pipeline. (Contrast: `validate-marketplace.yml` SHA-pins its actionlint download.)

- **Recommendation:** pin to the commit SHA of the current `v6.x` release. Deferred because choosing/verifying the exact SHA is a supply-chain decision worth an explicit confirm rather than an autonomous pick.
- **Question:** Pin to the latest `v6` SHA? (I can look it up and open a one-line PR on your go-ahead.)

### 6. Two low-value nits (P2/P3) — fix or leave?

- **`must_fail_egress()` is a partly-vacuous teeth test** ([`check-streams-classify.py:128-146`](../../scripts/check-streams-classify.py)): it hand-writes the phrase into `history.jsonl` and reads it back, so it validates *detection*, not the `append_event` *tripwire* (which is separately covered by `check_no_egress`). Recommendation: monkeypatch `append_event` to genuinely exercise the tripwire, or rename + fix the docstring so it doesn't over-claim.
- **`_FM` frontmatter regex not end-anchored** ([`check-frontmatter.py:39`](../../scripts/check-frontmatter.py)): the closing `---` lacks a `$` anchor, so a malformed `---bar` delimiter that happens to leave valid YAML between fences passes. Practical impact ~nil. Recommendation: add `$` with `re.MULTILINE` if you want it tight.
- **Question:** Worth fixing these two, or close as won't-fix?

---

_Generated by the scheduled review routine. The implemented fixes are in the accompanying PR; this document is the design-decision queue._

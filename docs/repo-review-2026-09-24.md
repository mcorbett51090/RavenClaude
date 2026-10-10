# Whole-repo review — 2026-09-24

**Scope:** systematic bug/tech-debt/security sweep of the RavenClaude marketplace repo.
**Method:** a three-panel review (expert fan-out → validation → tie-break), then autonomous
implementation of the fixes that do not need design input, and this document for the rest.
**Run type:** scheduled, non-interactive (no live owner input).

> **Headline:** the repository is in excellent health. `scripts/ci-preflight.py` reports **19/19
> PASS** (prettier, ruff, shell-syntax, JSON validity, every freshness/ratchet/inventory gate), there
> are **no P0/P1 defects**, and the executable surface (129 root Python scripts, 23 shell + 22 mjs,
> 56 core hooks, 60 core plugin scripts, 17 CI workflows) is unusually well-hardened — nearly every
> gate ships its own must-fail teeth. The findings below are concentrated and mostly low-severity.

---

## How the review was run

| Panel | Role | Model tier |
|---|---|---|
| **Panel 1 (expert review)** | Five parallel reviewers, one per executable-code surface (root Python gate scripts; shell + mjs; core guardrail hooks; core plugin Python; GitHub Actions workflows). Each returned genuine, verifiable defects only — no style, no formatting (ruff/prettier own that), no markdown-content staleness (the weekly sweep owns that). | Fast/mid (Sonnet + a security reviewer) |
| **Panel 2 (validation)** | Priority assignment validated; impact/effort/context added; severities adjusted (see F2 below). | Frontier (this session) |
| **Panel 3 (tie-break)** | The one ambiguous severity (F2, P2↔P3) adjudicated. | Frontier (this session) |

Coverage caveat carried honestly from the reviewers: a handful of very large files were sampled by
structure/grep rather than read line-by-line (`serve-dashboards.py` ~2980 lines; seven large
shell/mjs files incl. `check-worktree-state.sh`, `check-committed-routes.mjs`,
`check-dashboard-roundtrip.mjs`). No anomaly surfaced in the targeted greps over them, but they are
not claimed as exhaustively read.

---

## Findings by priority

| ID | Pri | Category | Location | Status |
|---|---|---|---|---|
| **F1** | **P2** | security (fail-open) | `plugins/ravenclaude-core/hooks/guard-web-access.sh:66-74` | ⛔ owner-action (tribunal-locked) — patch below |
| **1A-1** | **P2** | resource-leak / CI-availability | `scripts/check-hard-rule-floor.py:88-112` | ✅ **fixed in this PR** |
| **F2** | **P3** | over-block (fail-safe) | `plugins/ravenclaude-core/hooks/guard-destructive.sh:298`, `~1853-1855` | ⛔ owner-action / design |
| **1A-2** | **P3** | resource-leak (convention) | six root `scripts/check-*.py` + ~dozens repo-wide | 📋 recommendation (see below) |
| **1A-3** | **P3** | error-handling | `scripts/install-codex-mcp.py:160`, `scripts/install-copilot-mcp.py:129` | ✅ **fixed in this PR** |
| **1D-1/2** | **P3** | resource-leak | `plugins/ravenclaude-core/scripts/ledger.py` `_git()`, `ignored()` | 📋 part of 1A-2's convention question (tribunal-locked) |

**Clean:** the shell + mjs slice (`gate()`/`_skip_or_fail()`/`rc_mustfail()` machinery, every
`process.exit`/`JSON.parse`/`eval` site verified), and the GitHub Actions slice (all 39 `uses:`
SHA-pinned, zero `pull_request_target`, untrusted issue title/body isolated through `env:` with no
shell-injection sink, scoped `permissions:`, the three required checks correctly free of `paths:`
filters). No `shell=True`/`eval`/`exec` on untrusted input anywhere in the Python surface; no bare
`except:`; no bare `open()` outside a `with`.

---

## ✅ Fixed in this PR

### 1A-1 (P2) — unbounded subprocess in a required-CI gate could hang CI for hours

`scripts/check-hard-rule-floor.py` is **Gate 209**, which drives the live `guard-destructive.sh`
~23 times per run to lock the PreToolUse hard-rule floor. Both driver helpers (`_drive`,
`_drive_write`) spawned the hook with **no `timeout=`**. `guard-destructive.sh` reads its payload
from **stdin** — a genuine hang path — and Gate 209 runs unconditionally inside
`.github/workflows/validate-marketplace.yml`, one of the three **required** status checks, whose job
sets no `timeout-minutes` (so GitHub's 360-minute default applies). A hung hook would stall the
required check for hours, blocking every PR, instead of failing fast.

**Fix:** each drive is now bounded (`timeout=30`); a `TimeoutExpired` prints a clear diagnostic and
returns a sentinel (`124`) that matches neither the expected deny (`2`) nor allow (`0`), so every
assertion fails and the gate reddens rather than hangs. The timeout is a ceiling, not an added delay,
so it is not expected to affect the normal path.

**Control:** `audit-gates.sh --check 209` was run with the `timeout=30` change in effect — all ~23
live drives passed (exit 0, self-test PASS), so on this repo none exceeded the bound; `ruff` clean.

### 1A-3 (P3) — uncaught `KeyError` on a malformed MCP catalog entry

`scripts/install-codex-mcp.py:160` and `scripts/install-copilot-mcp.py:129` accessed
`catalog[name]["config"]` with no guard. A plugin-authored `mcp-catalog.json` entry missing its
`"config"` key would crash with a raw Python traceback, instead of the clean, actionable error these
files use everywhere else. (`catalog[name]` itself is safe — both files validate `wanted ⊆ catalog`
upstream.)

**Fix:** an explicit up-front `if "config" not in catalog[name]` check prints a clean message and
returns 1. Verified: driving both scripts with a config-less catalog entry printed
`catalog entry '<name>' is missing its 'config' key` and returned 1 (no traceback); `ruff` clean.

---

## ⛔ Requires owner action / design input

### F1 (P2) — `guard-web-access.sh` host extraction is bypassable via `#`/`?` before `@`

**Why it can't be auto-fixed here:** the file lives under `plugins/ravenclaude-core/hooks/`, the
command-review tribunal's own **substrate**. An agent edit is denied category-independently by
`xc.tribunal-self-disable` (Sága log `.ravenclaude/runs/thing/thing-2026-09-24T07-19-17Z-4853.json`)
— **this is correct**: agent-authored changes to the guard layer are exactly what that floor gates.
Apply via the dashboard / sanctioned maintainer route.

**The defect.** Host extraction strips scheme → path → userinfo → port:

```sh
host="${url#*://}"    # strip scheme
host="${host%%/*}"    # strip path
host="${host##*@}"    # strip userinfo (to LAST @)
host="${host%%:*}"    # strip port
```

Per RFC 3986 the authority ends at the first of `/ ? #`, but only `/` is stripped. So a `@` inside a
**fragment** or **query** reaches the `##*@` strip and forges the host. Traced by hand through the
`${}` string operations:

- `https://evil.com#@good.com` → computed host **`good.com`** (real fetch still targets `evil.com`).
- `https://evil.com?@x` → computed host **`x`**.

**Impact (fail-OPEN — the dangerous direction):**
1. **Deny-list bypass:** with `evil.com` on the `deny:` list, `WebFetch https://evil.com#@unlisted`
   computes an unlisted host, so the `exit 2` block never fires and the fetch falls through to the
   normal prompt — the deterministic backstop is evaded.
2. **Silent auto-allow (worse):** with `good.com` on `allow:` and `web_access.trusted: true`,
   `WebFetch https://evil.com#@good.com` computes `good.com` → `permissionDecision: allow` with **no
   prompt** — a fetch that actually targets `evil.com` is silently auto-allowed. This crafted URL is
   exactly the shape a prompt-injection would emit to exfiltrate past the deny list.

**Severity rationale (Panel 2):** P2, not P1 — it weakens a *defense-in-depth* backstop (Claude
Code's own per-domain permission dialog still exists for the unlisted case), and exploitation
presumes the model is already emitting an attacker-crafted URL. But it is the highest-severity
finding and the one worth fixing promptly.

**Proposed patch (minimal RFC-3986 parsing — apply between the path strip and the `@` strip; traced
by hand, not executed here since the file is substrate-locked):**

```diff
 # Host from the URL: strip scheme, userinfo, path, port; lowercase.
 host="${url#*://}"
 host="${host%%/*}"
+host="${host%%\?*}"   # strip a ?query    — RFC 3986: the authority ends at the FIRST of / ? # ,
+host="${host%%#*}"    # strip a #fragment — so a '@' inside a query/fragment must not reach the
+                      # userinfo strip below and forge the host. `%%/*` above already handles an
+                      # '@' in a path; these two close the fragment/query case.
 host="${host##*@}"
 host="${host%%:*}"
```

Hand-trace against legitimate inputs: `user@example.com/path?x=@y` → `example.com`,
`evil.com?@good.com` → `evil.com`, `evil.com#@good.com` → `evil.com`. **Recommended follow-up when
applied:** add two must-fail fixtures to the guard's test — `evil.com#@good.com` must NOT auto-allow,
and `evil.com#@unlisted` must still be blockable when `evil.com` is denied. (This is a proposal; it
should get the same security review any guard-layer change gets before it lands.)

### F2 (P3) — `guard-destructive.sh` force-push patterns over-block on a folded newline

**Why it can't be auto-fixed here:** same tribunal substrate as F1, *and* the fix touches the core
deny logic of the most safety-critical guard, where a careless change could open a real bypass — this
genuinely needs design review, not an autonomous patch. (Aptly, this very document was first refused
by the `srm.force-push` hard rule because its prose described the pattern — the same prose-vs-command
confusion documented in CLAUDE.md milestones v0.242.0/v0.244.0.)

**The defect (mechanism confirmed).** The normalizer folds all whitespace, including newlines, to
single spaces (`guard-destructive.sh:298`, `tr -s '[:space:]' ' '`), while the force-push deny
patterns (`~1853-1855`) bound their match with a `[^;&|]` character class that excludes `; & |` but
**not** newline. So a benign two-line command — an ordinary branch push on the first line, and on a
later line a comment that merely *names* a force flag — collapses to one line and false-matches the
force-push rule → `exit 2` (a false deny). Reproduced live by the review agent (the tribunal's
sibling `srm.force-push` catalog rule denied its innocuous diagnostic command for the same reason,
and denied the first draft of this very file).

**Severity (Panel 3 tie-break, P2 → P3):** this is an *over-block* (false positive). It is
**fail-safe** — it never weakens a security boundary, only annoys — and this repo has explicitly
navigated the same `[^;&|]`-excludes-newline class before (CLAUDE.md milestones v0.242.0/v0.244.0
fixed sibling instances in the concerns catalog). Downgraded from the reviewer's P2 to **P3**.

**Direction of a fix (for the owner to design):** add newline to the separator-exclusion class in the
force-push patterns, **or** segment-split `cmd` on `;`/`&&`/`||`/newline and match per-segment (as
`guard-foreground-suite.sh` already does) rather than folding newlines into one line before matching.
The same class also lives in `thing-orchestrator.sh`'s `srm.force-push` catalog rule, which a
dedicated pass should cover together. ⚠️ Whichever direction is chosen, it must be verified NOT to
create a false *negative* (a genuine force-push on its own line must still deny).

### 1A-2 + 1D (P3) — adopt (or explicitly decline) a subprocess-`timeout` convention

The missing-`timeout` pattern in 1A-1 is **not** an isolated bug — it is a repo-wide inconsistency.
A grep of `subprocess.run/Popen` across `scripts/*.py` and `plugins/ravenclaude-core/scripts/*.py`
shows dozens of call sites, some bounded (`timeout=30/60/120`) and some not, with no systematic
convention. Point-patching only the handful the review happened to name would leave the tree *more*
inconsistent, not less — so this is deliberately routed here as a **convention decision**, not
autonomous churn.

Representative unbounded sites (all P3, all low-likelihood — local git rarely hangs):

- `scripts/check-layout.py:83,92` · `scripts/check-diff-budget.py:128` (`_git()`) ·
  `scripts/check-generated-headers.py:82` · `scripts/check-form-metrics.py:104` ·
  `scripts/check-gate-suite-coverage.py:64` · `scripts/check-model-ids.py:123`
  (all invoked from `audit-gates.sh` → the required Validate-Marketplace check).
- `plugins/ravenclaude-core/scripts/ledger.py` `_git()` (~408-421, the hot path for
  `rc ledger append`) and `ignored()` (~1421-1425). *(Tribunal-locked substrate — owner-applied.)*

**Recommended decision:** either (a) adopt "every `subprocess.run` in a gate/hot-path script carries
a `timeout=` and treats `TimeoutExpired` as a finding" and add a small lint for it, applied in one
reviewed pass across all sites; or (b) explicitly decide the convention is "bound only where a hang
has real blast radius" (which 1A-1 already satisfies) and document that so the inconsistency reads as
intentional. Either is fine; the current silent middle is the only wrong state.

---

## Nothing else surfaced

No P0/P1 issues, no correctness bugs in the tribunal/adjudication engines (fail-closed defaults all
matched their documented specs), no injection/`shell=True`/unsafe-deserialization on untrusted input,
no inverted or always-pass gates, no un-SHA-pinned Actions, no `paths:` filter on a required check.
The two security findings (F1, F2) both live in the guard layer that the repo deliberately protects
from autonomous edits — which is why they are teed up here for owner application rather than patched.

*Generated by an automated scheduled review routine.*

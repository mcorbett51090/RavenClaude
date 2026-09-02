# Repository review — 2026-08-31 (three-panel, autonomous)

Scheduled full-repo review. Six skeptical expert finders (Panel 1) across review
dimensions; each finding validated against the code (Panel 2) and priority
tie-broken (Panel 3) by the Team Lead. **Implemented fixes shipped in PR #1059**;
the items below need a maintainer decision or the version-bump cascade, so they are
written up here rather than bundled into that PR.

## Headline

The repo is **healthy**. Every hard gate is green on `main` — prettier, ruff, JSON
validity, shell syntax, the 238-gate `audit-gates.sh` meta-test, `sync-plugin-versions`
(catalog derived from all 182 manifests), `check-frontmatter`, `check-md-links`,
marketplace↔filesystem plugin parity, required-check `paths:` hygiene, hook exec bits
— **with one exception that was already red and is now fixed**:

- **[P1, FIXED in #1059]** `check-marketplace-claims.py` (inside the **required**
  `validate-marketplace` check) was failing: `ravenclaude-core/README.md` said
  Skills = 54, actual = 55. A 55th skill landed via the admin-bypass path without
  updating the gated count, so every PR was blocked from merging on this check.
  Corrected 54 → 55; the gate is green again (verified this session).

The three finders scanning executable code (107 Python scripts, 48 core hooks +
20 shell scripts, 13 CI workflows) found **no P0/P1 bugs** — the code is
exceptionally hardened (fail-closed exits, `--self-test`/`--must-fail` teeth,
BSD/bash-3.2 portability, least-privilege workflow permissions, no `run:` injection).

## Shipped in PR #1059 (no design input needed, no version bump)

| # | Pri | Fix |
|---|-----|-----|
| 1 | P1 | `ravenclaude-core/README.md` Skills 54 → 55 (unblocks required gate) |
| 2 | P3 | root `README.md` core table: Skills 52 → 55, Hooks 34 → 39 |
| 3 | P3 | root `README.md` power-platform: 21 → 23 skills (bullet + table) |
| 4 | P3 | root `README.md` Commands row: added missing `/stream`, `/handoff` |
| 5 | P3 | `ravenclaude-core/README.md` Slash-commands row: added missing `/stream` |
| 6 | P3 | `quarantine-intake.yml`: stale `@v6`/v6.1.0 comment → v8.1.1 (SHA unchanged) |

---

## Needs a decision or a version-bump follow-up

Each item: the finding, a recommendation, effort, and the code to look at. The two
**hook** items are real, mechanical fixes with no design ambiguity — they are here
**only** because touching a `ravenclaude-core` hook forces a version bump, and a bump
was **measured this session** to make `index.html` (9.2MB) + the copilot tree go stale
(`check-artifact-freshness.py --check` → FAIL; `generate-copilot-plugin.py --check` →
STALE), the churn this repo keeps off the PR path. Bundle them into the next feature
bump, or greenlight a focused PR that pays the regeneration cost.

### A. Real bugs — implementable, but need the version-bump cascade

**A1 — [P2] `guard-memory-compaction.sh`: the shrink-deny is dead code for MultiEdit.**
`plugins/ravenclaude-core/hooks/guard-memory-compaction.sh:158-171`.
**Observation (reproduced this session):** fed the real hook a 2,815-byte
`/tmp/…/memory/MEMORY.md` and a >15% shrink expressed three ways — `Write`→tiny content
→ **exit 2 (deny)**; `Edit` removing ~1,900 bytes via top-level `old_string` → **exit 2
(deny)**; `MultiEdit` removing the *same* ~1,900 bytes via `edits[]` → **exit 0 (allow)**.
Same shrink, Edit denies, MultiEdit allows. **Mechanism:** the `else` branch reads
`.tool_input.old_string` (line 161) / `.tool_input.new_string` (line 162); MultiEdit
carries neither (it uses `.tool_input.edits[]`), so `new_bytes` stays empty and line 171
`case '' ) exit 0` allows unconditionally. The hook is registered for `Write|Edit|MultiEdit`
but `hooks/tests/test-memory-compaction-guard.sh` only exercises `Write`, so the gap is
ungated. **Impact:** an agent that trims a memory index by >15% via MultiEdit is never
denied — the sole mechanism for Memory-Engineering Rule 4 no-ops on 1 of its 3 registered
tool shapes (bounded: the tool-agnostic snapshot at line 137 still runs, so the edit stays
recoverable). **Recommendation:** in the `else` branch sum the `edits[]` deltas
(`jq '[.tool_input.edits[] | (.new_string|length)-(.old_string|length)] | add'`); add
Edit + MultiEdit fixtures to Gate 184. **Effort:** small (code) + small (test).
**Design input:** none — restores the behavior the header already claims.

**A2 — [P3] `remind-tests.sh` uses the porcelain parse `dod-gate.sh` documents as buggy.**
`plugins/ravenclaude-core/hooks/remind-tests.sh:28-31` computes changed files via
`git status --porcelain | awk '$2 ~ /…/'`. `dod-gate.sh:79-88` documents that exact
`$2` parse as silently missing paths with spaces and mishandling renames, and switched to
`--porcelain=v1 -z | tr '\0' '\n' | grep -cE …`. The advisory sibling was not updated.
**Impact:** low — advisory nudge only; after a rename-into-source-extension or a
spaced path, the "run the full suite" reminder is suppressed. **Recommendation:** reuse
the `dod-gate.sh` idiom. **Effort:** trivial. **Design input:** none.

### B. Design decisions

**B1 — [P2] The 40 `flag-*-antipatterns.sh` advisory hooks over-state their detection.**
e.g. `plugins/accounting-bookkeeping/hooks/flag-accounting-bookkeeping-antipatterns.sh:35`.
40 of the 69 `flag-*` hooks carry a header claiming they flag "a metric with no baseline |
an unsourced benchmark/market figure | client/user PII", but the entire body is a single
`grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b'` — **none** of the three named anti-patterns is
detected. On professionally-authored output (no literal TODO/FIXME) the guardrail is silent.
**Question:** is the intended contract **detect** or merely **remind on placeholder tokens**?
- *Remind* → soften the header + `hooks.json` comment to match (accurate, ~zero risk). Effort: small (templated across 40).
- *Detect* → add the cheap mechanical checks it advertises (bare `$N`/`%` figure with no adjacent `(source`/`20\d\d)`; SSN/email regex for PII). Effort: medium; risk: false-positive noise on advisory hooks.
**Recommendation:** soften now (fix (a)); open a separate scoped effort if real detection is wanted.

**B2 — [P3] The whole antipattern-hook fleet silently no-ops when `jq` is absent.**
All ~169 `plugins/*/hooks/*.sh` resolve the target file from stdin JSON via `jq`, guarded by
`command -v jq`; with `$CLAUDE_TOOL_FILE_PATH` not a real Claude Code variable, a consumer
without `jq` gets `FILE` empty → `exit 0` for every hook, including the security-oriented
`check-*` ones, with no diagnostic. **Question:** is silent degradation the intended posture
for a security-adjacent fleet? **Recommendation:** emit a one-line stderr notice when `jq` is
missing but stdin JSON is present (observability without behavior change), or document `jq`
as a marketplace prerequisite. **Effort:** small (templated) — but touches 169 files, so it
wants a decision before the churn.

**B3 — [P2] `audit-gates.sh` is an 8,932-line single-file harness for every gate.**
`scripts/audit-gates.sh`. Its own header records a past macOS run that "DIED AT GATE 7 …
while reporting no failures, because a dead run prints no ✗." Partially self-defended by
`check-gate-registration.py`, but the 552KB single file is edited on every gate change and
can't be reviewed in a normal diff. **Recommendation:** a "gates-reached == gates-registered"
tripwire so a truncated run fails loud (cheap, high-value); longer term, decompose into
sourced per-gate fragments. **Design input:** approve the tripwire / decomposition appetite.

**B4 — [P2] `generate-dashboards.py` (~15k lines) is a SPOF for the public portal**, loaded by
`generate-index-dashboard.py:964` via a dynamic `_load_sibling`. **Recommendation:** carve
sub-app renderers into a `dashboards/` package. **Design input:** refactor appetite (large).

**B5 — [P2] 9.2MB generated `index.html` is committed and re-committed each merge** with no
`linguist-generated`/`-diff` attribute; `.git` is already 45MB. **Question:** keep committing
the artifact, or serve it from a Pages build and mark it `-diff linguist-generated`? This is a
policy call and interacts with the self-heal design (B6).

**B6 — [P2] The self-heal architecture is a SPOF on `SELF_HEAL_PAT`.**
`.github/workflows/regenerate-artifacts.yml:381-493`. Big artifacts were moved off the PR path;
`main` regenerates + self-commits post-merge via a PAT. If the PAT expires, `main` (and the
portal) silently drift stale while the bot PR sits with no checks. **Recommendation:** a
scheduled freshness `--check` on `main` that fires `scripts/notify.sh` so PAT expiry surfaces
loudly. **Effort:** small. **Design input:** confirm the alarm channel.

**B7 — [P2] The documented branch-check gate is still unbuilt, and its incident already happened.**
`CLAUDE.md:58-59` admits porting `RavenPower-Website`'s `check:branch` (fail on modified tracked
files on `main`, `RP_ALLOW_MAIN=1` escape) is "a live follow-up"; `CLAUDE.md:35-53` documents work
that landed silently on `main` here. No `check-branch*` / `RP_ALLOW_MAIN` exists. **Recommendation:**
port it as a `PreToolUse` guard + CI backstop (the layout-hook pattern). **Design input:** greenlight.

**B8 — [P3] Dual hook-registration (dev-mirror vs canonical) is hand-synced with no drift gate.**
A hook added only to `.claude/settings.json` works in dev but never ships. **Recommendation:** a
small gate asserting canonical `hooks.json` ⊇ the dev-mirror block (minus the deliberately
marketplace-only `Notification` entry). **Effort:** small. **Design input:** approve the new gate.

**B9 — [P3] Twelve near-parallel `check-*-render.mjs` harnesses** (~2,877 lines) duplicate
render-and-assert scaffolding. **Recommendation:** extract a shared `render-harness.mjs`; reduce
each to a per-app spec. **Effort:** medium.

**B10 — [P3] `STRATEGY.md` is a stub** — the public/private marketplace boundary lives only in the
maintainer's memory. **Recommendation:** promote the non-confidential half of the boundary rule into
`STRATEGY.md` so contributors can apply it. **Design input:** what's shareable.

**B11 — [P3] Two workflows pin an older `actions/checkout`.** `inventory-sweep.yml:50` and
`spike-claude-availability.yml:49` pin v4.2.2; 11 others pin v7.0.1 (SHA
`3d3c42e5aac5ba805825da76410c181273ba90b1`), with no rationale comment for the divergence.
**Question:** intentional? If not, bump both to the v7.0.1 SHA (low-regret). If yes, add a
one-line rationale to match this repo's documented-divergence convention.

**B12 — [P3] `inventory-sweep.yml:95-107` `continue-on-error: true` defangs a guard.** The step
meant to fail red if the scheduled sweep ever appears in a branch ruleset only produces a
`::error::` annotation; the run stays green. The `|| echo '[]'` already tolerates the 403 case,
so `continue-on-error` only affects the real-detection path. **Question:** intended severity of a
ruleset-membership violation? If it should block, drop `continue-on-error`.

**B13 — [P3, trivial] Five `scripts/*.sh` lack the executable bit** (`check-hook-failclosed.sh`,
`dod-fast.sh`, `regen-inventory.sh`, `spike-selfheal-contract.sh`, `spike-tprose-canary.sh`).
**Non-defect for behavior** — all are invoked via `bash scripts/x.sh`, and the exec-bit gate only
covers `plugins/*/hooks/*.sh` — but they diverge from the ~15 sibling scripts that do carry `+x`,
and one `author-wave1-entries.py` print suggests running `scripts/regen-inventory.sh` directly.
**Recommendation:** `chmod +x` the five (trivial consistency) or leave as-is; either is defensible.

---

## Non-findings deliberately NOT flagged (recorded so they aren't re-raised)

- Required-check `paths:` hygiene: the three required checks correctly have **no** `paths:` on
  `pull_request:` while **keeping** `paths:` on `push:` — deliberate and documented.
- Admin ruleset bypass; the docs-straight-to-main flow; optional per-plugin `CHANGELOG.md`;
  the `perl -pi`/LF portability pins — all documented, reasoned trade-offs.
- No wrong-plugin-name copy-paste, no phantom agents, no `plugin.json`/README fabrication found
  in the plugin-consistency sample.

_Provenance: `.ravenclaude/runs/repo-review-2026-08-26/` (panel outputs, ground-truth checks, the
A1 reproduction control)._

# CI gate harness audit — 2026-06-23

Analysis of `scripts/audit-gates.sh` (~68 numbered gates, 468 bidirectional assertions) +
the 6 GitHub Actions workflows, to find gates that can be **consolidated, removed, or updated**.
Run via `/forge`; deep read by a subagent that verified every load-bearing artifact, hardcoded
count, and must-fail fixture against the live tree.

## Headline
**The harness is in very good shape.** No gate guards a deleted artifact (→ **no REMOVE**), and no
two gates duplicate coverage closely enough to merge without losing a distinct property
(→ **no coverage-reducing CONSOLIDATE**). Every spot-checked must-fail half still has teeth
(notably all Gate 12 count fixtures — the "stale literal → silent no-op" trap was specifically
hunted and found clean). The findings are a small set of **UPDATE** (naming/wiring) fixes.

## Actioned in this PR (safe — additive / relabel only, zero coverage removed)
| # | Finding | Fix |
|---|---|---|
| A | **Gate-number collision:** two full-suite gates both printed "Gate 104" (the grep-PCRE check + the Pipeline concern-stats render). `--check 104` could only ever reach concern-stats. | Renumbered the PCRE gate to **106** (105 was just taken by the Heimdall carve-out gate); concern-stats stays 104 (it owns the `--check` slot). |
| B | **Stale dispatcher comment** (`audit-gates.sh:29-31`): "full **48-gate** matrix" + a supported-list missing 97/100/101/103/104/105. | Corrected to "~68-gate" and synced the list to the real `--check` case + Supported error line. |
| C | **Two dormant gates:** Gate 60 (Copilot seat cap) and Gate 80 (`ravenclaude status` launcher) existed **only** in the `--check` dispatcher — no full-suite block, no workflow invoked `--check 60/80`, so a normal CI run **never exercised them**. | Wired both into the full suite (each test passes standalone and in the full run). |

## Deferred (NEEDS HUMAN JUDGMENT — not actioned)
- **Gate 70 decorative assertion** (`[ 1 -ne 2 ]`) — an intentional always-pass "exit-codes-are-distinguishable" marker; the real teeth live in its test script (G70.6). Not a silent-no-op bug; left as-is.
- **`hasattr` "both server copies" sub-checks** in render Gates 37/38/40/41/43/49 vs Gate 32's endpoint parity — *thematic* overlap only; each checks a distinct property (the specific reader symbol exists in both copies). Cheap; left as KEEP. A reviewer could fold them into Gate 32 to reduce assertion count — a preference call, not a defect.
- **Gate 54 mirror** — a full block plus a `--check 54` inline reimplementation (duplicated mutant logic rather than a shared helper). Not a coverage problem; an optional dedup like the dashboard-server-drift mirror.

## Numbering / retirement note (doc consistency)
Unused/retired numbers: 11 (repo-guide.html removed → covered by 97+51), 39, 55–59, 61–69, 71–79,
81–89, 94–96 (reserved for an in-flight data-viz run). After this PR, 105 = Heimdall carve-out and
106 = grep-PCRE; 104 = concern-stats only.

## Verification
Full `bash scripts/audit-gates.sh` after these changes: **468 pass, 0 fail** (now including the
newly-wired Gates 60 + 80); `bash -n` clean; collision resolved (verified no remaining
double-"Gate 104").

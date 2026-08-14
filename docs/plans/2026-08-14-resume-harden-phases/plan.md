# Plan: resume-harden-phases

**Depth:** quick · **Date:** 2026-08-14 · **Owner:** Matt Corbett
**Status:** implementation already ran in five parallel worktrees. This plan is the land + hold record.

## Intent

Finish the five in-flight recurring-defect-hardening phases, verify each (self-test, must-fail, registration), then land. Do not start PR 11 / 3b / 16 / 17.

## What actually shipped (this session, not pushed)

| Phase | Branch | Commit | Gate | Orchestrator-verified |
|---|---|---|---|---|
| livefix | `harden/livefix-gate51-pitch` | `fc7efcc2` | **205** | `--check 205` 0; self-test 7/7 including must-fail exit 2; registration clean |
| PR 14 | `harden/pr14-self-certifying` | `daa0c971` | **204** | `--check 204` 0; `--self-test` 0; `--must-fail` 2; registration clean |
| PR 12 | `harden/pr12-count-ssot` | `13a7b2ff` | **206** | `--check 206` 0; self-test 16 shapes / 11 narrow-blind; live tree 361 surfaces clean; plant uses `1 advisory hook` |
| PR 10 | `harden/pr10-canary` | `ecc16ef3` | **207** | `--check 207` 0; `--check 154` 0; `activation_gate` on every host; D4 advisory |
| PR 9 | `harden/pr9-provenance` | `f5e485cb` | **extends 34** | `--check 34` 11/11; version `0.258.0 → 0.259.0` |

Reserved numbers were honored. No branch stole another phase's gate.

## Dependency DAG

```
livefix (205) ─────────────────────────────┐
pr14 (204) ────────────────────────────────┤
pr9 (extends 34) ──┐                       ├── land sequentially (audit-gates.sh rebase)
                   ├── PR 11 (NEXT, not now)
pr10 (207) ────────┘
pr12 (206) ────────────────────────────────┘
```

Critical path to PR 11: land **pr9** + **pr10**, then start PR 11.

All five were **implemented in parallel** (isolated worktrees). **Land serially** because every branch edits `scripts/audit-gates.sh`.

### Recommended land order
1. `livefix` — smallest, independent, #903-run defects
2. `pr14` — Gate 204
3. `pr9` — Gate 34 extension + version bump
4. `pr12` — largest (174 plugin bumps); Gate 206
5. `pr10` — Gate 207 + `activation_gate` schema

Rebase each onto `origin/main` after the previous merges.

## Alternatives (kept from panels)

1. **Parallel impl / serial land** (chosen) — max wall-clock, expected `audit-gates.sh` rebase cost.
2. **Serial impl in land order** — fewer rebases, ~5× wall-clock. Rejected: user said max parallel.
3. **Extend Gate 51 for livefix instead of 205** (panel A) — rejected: the user's reserved table assigned 205.

## depends_on_claims

- Phase livefix `depends_on_claims: [1, 2, 5, 12]`
- Phase pr14 `depends_on_claims: [1, 2, 4, 12]`
- Phase pr12 `depends_on_claims: [1, 2, 6, 9, 11, 12]`
- Phase pr10 `depends_on_claims: [1, 2, 7, 9, 12]`
- Phase pr9 `depends_on_claims: [1, 8, 9, 12]`
- Phase PR11-next `depends_on_claims: [10]`
- Held PR3b/16/17 `depends_on_claims: [9, 10]`

## Verification this session caught

- **CL-11 (narrow regex would lie):** settled. Pre-DROP `pr9` tree: adjective-tolerant checker exit 2, 1951 finding-lines including `1 advisory hook`. Post-DROP `pr12`: exit 0. Gate 206's plant is the narrow-blind shape.
- **PR12 `--must-fail` flag:** the script has no `--must-fail` CLI; teeth live in `audit-gates.sh` as a planted `1 advisory hook`. That is the correct place.
- **PR10 `--must-fail`:** wrapper exits 0 when teeth work (mutants themselves exit 2). Honest, not a fail-open.
- **Panel A "sibling scan never called":** implementer finished it. `--check 205` now exercises rotten pitch.html `#/` hrefs.
- **Local `main` 4 behind `origin/main`:** unused; worktrees were already on `91cff60e`.

## Out of scope (still held)

- **PR 11** — start after pr9 + pr10 merge.
- **PR 3b** — tribunal-denied `plugins/ravenclaude-core/scripts/`; needs a bang-command session.
- **PR 17** — D2 security red-team.
- **PR 16** — D6 defer.

## DoD for landing each PR

- Rebase onto current `origin/main`
- Re-run that PR's `--check N` after rebase
- `check-gate-registration.py` clean
- Open PR; do not merge until CI green
- After all five: PR 11 is the next start

## Engineering pre-commitments

Reserved gates 204–207, version bumps on pr9/pr10/pr12, `docs/gate-oracle-manifest.json`, `activation_gate` field.

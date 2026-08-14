# Plan: harden-pr3b (packaging move)

**Depth:** quick · **Date:** 2026-08-14 · **Owner:** Matt Corbett
**Base:** `a71b47b9`

## Intent

Move `premise-gate.py`, `classify_claim.py`, `check-design-schema.py` into `plugins/ravenclaude-core/scripts/` so consumers can resolve them. Keep marketplace-root shims. Empty `_DEFERRED_PACKAGING`. Gate 187 green.

## Reconciled (A ∩ B)

- **Shim, not rewrite.** Canonical files in the plugin; `scripts/<name>.py` are thin wrappers. Implementer used `os.execv` **and** re-applies `-O` via `sys.flags.optimize` (Gate 178).
- **classify_claim locator:** walk up to marketplace-root `tests/fixtures/classify-claim/` (not `parent.parent`).
- **Operational cites** in forge-pipeline / design-clone / brand-extraction tests point at the plugin path.
- **`audit-gates.sh`** keeps `python3 scripts/…` (shim).
- Empty `_DEFERRED_PACKAGING` only after operational cites are retargeted.
- Version **0.262.0 → 0.263.0**. No new gate.

`depends_on_claims:` move `[3,4,5]`; shims `[5,9]`; Gate 187 `[6]`; bump `[7]`; held `[8]`.

## Alternatives

1. Shim + retarget plugin-internal tests (chosen).
2. Rewrite every call site, no shim — breaks FORGE muscle memory.
3. Move-only without emptying `_DEFERRED_PACKAGING` — hollow.

## Status this session

Implemented on `harden/pr3b-packaging` `75993d1c`. Verified: shim + `-O` self-tests, Gate 187, Gates 193 and 194.

## Out of scope

PR 16 (D6), PR 17 (D2). PR 15 already banked.

## Engineering pre-commitments

Version **0.263.0**. `_DEFERRED_PACKAGING` emptied. No new gate number.

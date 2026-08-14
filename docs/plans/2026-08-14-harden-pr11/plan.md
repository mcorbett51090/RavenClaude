# Plan: harden-pr11 (P17 / Gate 208)

**Depth:** quick · **Date:** 2026-08-14 · **Owner:** Matt Corbett
**Base:** `origin/main` `6deb8f6e`

## Intent

Build PR 11 now that PR 9 (#906) and PR 10 (#908) have landed. Deliver P17: host-capability sentences asserted against `host-support.json`, plus adapter deny-reason round-trip. Gate number is **208** (build-plan's 205 is taken by livefix).

## Reconciled approach (A ∩ B)

1. **Extend Gate 154** (`check-host-support.py`) — generator output must not invent host+capability literals off-SSOT (MH-27).
2. **New Gate 208** — `check-host-capability-citations.py` + adapter round-trip.
   - exit 2 only where a `host-support.json` cross-ref exists
   - `docs/` uncited = advisory
   - honor `[docs-verified]` / `[unverified]`
3. **MH-28** — the two leftover call sites are `templates/agent-ready-repo/AGENTS.md.template` and `CLAUDE.md.template` (still claim Aider reads AGENTS.md natively). Fix them. Bump `0.261.0 → 0.262.0`.
4. **Cursor adapter** — reason may live on stderr; do not assert a generic JSON field. Prefer stderr sentinel + fixed-literal JSON.
5. **B-only note:** Copilot file-pretool swallowing stderr is a P8 sibling — fix or named-waive, do not silently skip.

## DAG

```
MH-28 template fix ──┐
154 generator scan ──┼── Gate 208 registration ── verify ── land
citation lint ───────┤
adapter round-trip ──┘
```

All three lint/RT slices parallelize; registration is the join.

`depends_on_claims:`
- Phase MH-28 `depends_on_claims: [5, 9]`
- Phase 154 extend `depends_on_claims: [2, 4, 6, 8]`
- Phase citations `depends_on_claims: [3, 7, 8]`
- Phase adapter RT `depends_on_claims: [4, 7]`
- Phase register/verify `depends_on_claims: [1, 2, 5]`
- Held `depends_on_claims: [10]`

## Alternatives

1. **One Gate 208 covering citations+RT; 154 stays the generator SSOT scan** (chosen — matches both panels).
2. **Three new gate numbers** — rejected; next-free is one slot and 154 already owns the map.
3. **Hard-fail all docs/ prose** — rejected by build-plan SNR correction.

## Out of scope

PR 3b, 16, 17.

## DoD

- `--check 208` 0 and `--check 154` 0
- must-fail: MH-27 generated slash-commands on a host with none; uncited knowledge claim with SSOT; adapter that drops deny reason
- both regions + Supported + `check-gate-registration.py`
- version bump iff `plugins/` touched (expected: yes)
- prettier/ruff as required

## Engineering pre-commitments

Reserved Gate **208**. Version target **0.262.0** if templates/plugins change.

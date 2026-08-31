# Decision record — recurring-defect hardening initiative closed

**Date:** 2026-08-14 · **Owner:** Matt · **Method:** `/forge` leftover-decision
**Tree:** `origin/main` `332a368a` (#919)

## Initiative DoD #4 (run after every other PR shipped)

Both required checks were run this session against that tip:

| Check | Result |
|---|---|
| `python3 scripts/check-gate-registration.py` | exit 0 — `audit-gates.sh` clean |
| `python3 scripts/check-constitution-claim-staleness.py` | exit 0 — no contradicted claim in 182 every-session files |

Highest numbered gate: **210**. ravenclaude-core: **0.264.0**.

## Coverage

P1–P21 each have a shipped mechanism or a recorded ruling. D6 (agent-recommended defer of PR 16) was overridden by keep-going and shipped as #919 / Gate 210. D2 shipped as #918 / Gate 209 **CLEAR d** (lock, not a widened Bash door).

## Leftovers — this session's ruling

Tribunal seats abstained (timeout); verdicts below are fact-derived, not preferences.

| Leftover | Ruling |
|---|---|
| Draft [#886](https://github.com/mcorbett51090/RavenClaude/pull/886) (2026-08-13 news sweep) | **Do not merge as-is** (341 commits behind; marketplace.json + #907 README collision). Leave open for a rebase, do not close. |
| Self-heal after #919 | **No action** — #919 already regenerated `dashboard.html` and `index.html`. |
| ~194-gate UNWIRED retrofit | **Do not start** — named-not-built residual of PR 1. |
| Twin-server shared-import | **Do not start** — named-not-built residual of PR 5. |
| Tribunal inert-body preprocessor → `thing-concerns.py` | **Do not start** — PR 17 red-team: own review. |

The 17-PR hardening band is closed. Those three residuals need a new plan if they are ever funded.

# Review — harden `rc-deep-research` plan before implement

**Date:** 2026-09-10  
**Plan:** `docs/plans/2026-09-03-harden-rc-deep-research/plan.md` (G6, 2026-09-03)  
**Owner decision:** review for issues, then keep going.

## Verdict

The plan is still the right spine. **Do not implement P1–P6 in one PR.** Several
same-PR landing constraints (SP-1–SP-6) are load-bearing; violating one produces
a silently-green broken main. Start at **P0a** (disabled-config floor gate +
prompt-text golden) after re-reading the live gate number.

## Issues found (do not ignore)

| # | Issue | Why it matters |
|---|---|---|
| R1 | **Next-free-gate is stale.** Plan says Supported max is 262 ⇒ Gate 263. `audit-gates.sh` now has 264+ (caveman, prompt-optimizer, …). Re-read the `Supported:` max before claiming a number. | Landing "Gate 263" would collide and fail CI or silently skip. |
| R2 | **Line citations have already drifted.** Plan V5/V6 pin `:1160`, `:1170`, `:1429`. `rc-deep-research.js` has been edited since 2026-09-03 (eval wiring, dispatch wrapper, recovery batch). Re-read the live file before any region edit. | SP-1/SP-3 assume those regions. A stale line map drops a half. |
| R3 | **SP-1 and SP-2 forbid the DAG's "four authors in parallel" as written.** P1∩P3 and P1∩P4a must land together. Treat those as **one PR each**, not four. | Hand-resolved conflict that drops either half compiles and passes Gate 126. |
| R4 | **CE-4 cannot be structurally closed** (C11). PCE4 only narrows persist-crossing. Any PR that claims "untrusted bytes no longer reach Writer" is false. | Honesty + House Rule 3. |
| R5 | **Disabled floor is still ungated** (C7). `adapterOpts` returns `{}` when disabled; asserted in SKILL.md, enforced by nothing. That is P0a. It is also the prerequisite of P0c derivation (F4.3): once derivation lands, Gate 126 can no longer detect a mis-merged canonical. | Build the net first. |
| R6 | **Adaptive-classifier / dispatch-evaluator share this file.** June parked work's remaining Phase 6 flip and P5 sampler both touch `rc-deep-research.js`. Sequence; do not parallelize. | Same-file conflict + Gate 52 floor. |
| R7 | **`_isoNow` is still the constant `1970-01-01`.** Audit lines are non-evidentiary. In scope for P0b/P4, not a reason to skip P0a. | |

## What "keep going" means this session

Command-review hard-denied edits to several plugin scripts in the same turn
(`srm.force-push` false positive). P0a is a new gate in `audit-gates.sh` plus a
golden over `rc-deep-research.js` — the same deny family. **Do not workaround.**
Next implement session should land P0a only: allocate the next free gate, add
the disabled-config byte-identity assertion, add the prompt-text golden. Then
stop and open the P1+P3+P4a combined PR.

## What not to do

- Do not flip `run-config.json` `enabled: true` as part of hardening.
- Do not start P7 packaging until O82 live-install settle.
- Do not extend Gate 126 to a third copy in a different commit than the sync script (SP-5).

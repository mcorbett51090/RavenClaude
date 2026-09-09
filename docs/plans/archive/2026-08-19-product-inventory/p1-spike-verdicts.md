# P1 — Empirical spike verdicts

**Phase 1 of** [`plan.md`](plan.md). `depends_on_claims: [13, 15, 16]`

Four spikes, each with the command run and the literal output class. ⛔ Per the
phase acceptance: **a spike with no recorded verdict is not done**, and an empty
result needs a positive control — every row below names one.

---

## The four-row table

| Spike | Command run | Literal verdict | Consequence |
|---|---|---|---|
| **S1** — T-PROSE canary | `bash scripts/spike-tprose-canary.sh` | **8 verdicts, 8/8 asserted, positive control DENIED as required.** Q1 DENY · Q2 ALLOW · Q3 DENY · Q4a DENY · Q4b ALLOW · Q5 DENY · Q6 ALLOW | Authoring rule is **one `control:` per CLAIM**, placed **above** it. Two ledger corrections (§below). Rule written to [`inventory-authoring.md`](../../best-practices/inventory-authoring.md). |
| **S2** — `claude -p` in scheduled CI | `.github/workflows/spike-claude-availability.yml` (`workflow_dispatch` + weekly `cron`) | **PENDING a dispatch run.** Local host probe: `command -v claude` → `/Users/…/.local/bin/claude` — evidence about **this host**, explicitly **not** a CI verdict. | No phase is cancelled either way. The workflow reports `yes` / `no` / **`UNKNOWN`**, and UNKNOWN is not `no`. A `no` activates the §7.4 substitute ladder. |
| **S3** — self-heal contract | `bash scripts/spike-selfheal-contract.sh` | **`covers-digest-drift` → FATAL — self-heal aborts.** 1 of 3 content-freshness classes detonates. Extractor found 1 survivability pattern (`staleness gate FAILED`); teeth run confirms a class outside it is reported FATAL. | R4 / X1 converted from a read-derived inference to a **measured fact**. P2 fixes it and this script is its standing regression. |
| **S4** — prose rendering path | `python3 scripts/audit-prose-rendering-path.py` | **CLEAN.** 18 prose consumers traced, **0** shell-interpolation findings; 199 shell files parsed, **0** syntax or embedded-block failures. `--must-fail` → both detectors bit. | Red-team #8 closed by measurement. The audit becomes a standing gate. |

---

## ⛔ Two corrections to the plan's §1 ground-truth ledger

Recorded here rather than silently patched, because mitigations were built on both.

### GT6 is FALSE — T-PROSE is not CREATE-only

control: the identical stamped-diagnosis body was sent as a `Write` to a
non-existent path and as an `Edit` to an existing one; **both denied**, while a
benign body on the same existing path allowed.

`S1-Q5` = **DENY**. The `if os.path.exists(path): sys.exit(0)` early-exit at
`guard-premise.sh:462` gates **T-SHAPE only**; the hook header says so explicitly.

**Impact on the plan.** X15's mitigation reasoned that re-stamps on existing files
are *"structurally exempt."* They are exempt **by content**, not by structure
(`S1-Q6` = ALLOW for a bare date bump, because an `Edit` payload carries only
`new_string`). Same outcome, different mechanism — and a re-stamp that also
rewrites the nuance **is** screened, which the structural reading would have missed.

### W8 has materialised — one control per CLAIM

control: a body with a control above claim 1 and a second stamped claim twelve
lines below denied; the same body with a control above each claim allowed.

`S1-Q3` = **DENY**. The plan named this as variance W8 (*"not yet accepted — it is
measured in P1"*). It is now measured and it landed the expensive way. Per-entry
authoring cost rises; §19.2's P9 figure should be read with that applied.

---

## What each spike does NOT settle

An admitted gap beats a false claim of coverage.

1. **S2 is not settled until the workflow is dispatched.** The local `command -v`
   result is about this laptop. A binary on `PATH` is also not a working model call
   — the workflow separates those two explicitly, and reports `no` for a present
   binary with no key.
2. **S3 measures the GREP CONTRACT, not a live workflow run.** It replays the
   conditional extracted from `regenerate-artifacts.yml` against representative
   output lines. It would not catch a failure that changes the workflow's control
   flow *elsewhere* in the step.
3. **S4's shell-interpolation check is a SHAPE check.** It proves no prose consumer
   calls `shell=True` / `os.system` / `os.popen`. It does not prove that some other
   process downstream of a generated artifact never does.
4. **S1 measures the guard as it is today.** It is re-runnable precisely because that
   is the only thing that keeps the authoring rule bound to the guard.

---

## Acceptance — P1

- [x] Four spikes, each with the command run and a literal output class.
- [x] S1 includes a file that **should** deny **and does** (`S1-C0`), so "it did not
      deny" is falsifiable rather than vacuous.
- [x] The line-offset rule and template shape recorded in
      [`docs/best-practices/inventory-authoring.md`](../../best-practices/inventory-authoring.md).
- [x] S4's apostrophe rule is enforced mechanically, not stated.
- [ ] S2 dispatched in CI — the one row that stays **PENDING**, honestly, rather
      than being marked done from a local probe.

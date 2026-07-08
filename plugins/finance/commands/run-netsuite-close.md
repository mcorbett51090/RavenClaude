---
description: "Pull a NetSuite trial balance the gold-standard way and run it through the governed close: OAuth2 M2M (or time-boxed TBA) auth, a BS-cumulative/IS-period SuiteQL query, a hard tie-out, then the same submit-only controller cycle every source uses. Setup is one-time/admin-assisted; the close itself is the fast part once wired."
argument-hint: "[entity + period, e.g. 'June close for Meridian Robotics from NetSuite']"
---

# Run the NetSuite close

You are running `/finance:run-netsuite-close`. Pull the trial balance the user described (`$ARGUMENTS`) from NetSuite via the reference SuiteQL connector, then hand it straight into the same governed close cycle every other source uses — leaving the user to review and approve, not to reconcile connector plumbing.

Full runbook (read this first if the user hasn't wired NetSuite before): [`../skills/netsuite-close/SKILL.md`](../skills/netsuite-close/SKILL.md).

> **HONEST BOUNDARY.** This chains a **reference implementation + offline harness**, not a certified NetSuite connector — see the honest-boundary block at the top of the skill. If the user hasn't completed the one-time, admin-assisted NetSuite setup (OAuth2 M2M integration record, certificate, role provisioning), stop and point them at the skill's BEFORE-CLOSE-DAY section before attempting a live pull.

## The chain

```
config (connector-config.template.json, NetSuite M2M block)
  → signer (netsuite_signer.py — cert-signed JWT assertion, key from a 0600 file)
  → netsuite_connect.py (mint token → SuiteQL BS-cumulative/IS-period pull → tie-out → stage)
  → run-controller-cycle (COA lint → statements → reconcile/flux → HTML package → SUBMIT)
```

```shell
# 1. Confirm the per-entity config exists and points at the right NetSuite account/subsidiary
#    (../templates/connector-config.template.json — NetSuite M2M variant block)

# 2. Pull the trial balance (add --replay for an offline dry run against synthetic fixtures,
#    zero live credentials — do this first if the user is unsure the wiring is correct)
python3 scripts/connectors/netsuite_connect.py \
  --config   <entity>-netsuite-config.json \
  --period   <period_id> \
  --out      staging/trial-balance-<entity>-<period>.csv

# 3. If the pull doesn't tie, diagnose before escalating to the user
python3 scripts/connectors/netsuite_doctor.py diagnose --config <entity>-netsuite-config.json

# 4. Hand the staged NetSuite TB into the standard close cycle
python3 scripts/controller_cycle.py \
  --entity   <entity-profile>.json \
  --coa      <coa-mapping>.csv \
  --tb       staging/trial-balance-<entity>-<period>.csv \
  --prior-tb <prior-trial-balance>.csv \
  --subledger <subledger>.csv \
  --gl-detail <journal-lines>.csv \
  --run-dir  .ravenclaude/runs/close/<entity>/<period> \
  --out-html close-package.html --out-json close-package.json
```

**Provenance.** All scripts this chain drives — [`scripts/connectors/netsuite_connect.py`](../scripts/connectors/netsuite_connect.py), [`scripts/connectors/netsuite_doctor.py`](../scripts/connectors/netsuite_doctor.py), [`scripts/connectors/oauth_client.py`](../scripts/connectors/oauth_client.py) (`netsuite_m2m` provider), [`scripts/connectors/suiteql.py`](../scripts/connectors/suiteql.py), [`scripts/connectors/netsuite_signer.py`](../scripts/connectors/netsuite_signer.py), and [`scripts/controller_cycle.py`](../scripts/controller_cycle.py) — are present and green (`python3 scripts/test_connectors.py` → 91/91, 2026-07-07). Run `--replay` for an offline dry run before your first live pull. Reference impl, not a certified connector (§3).

## The submit-only boundary (do not violate)

Same rule as [`run-controller-cycle`](run-controller-cycle.md): this command performs **`submit` only**. It never approves, auto-certifies, or locks. If the connector pull recorded a TB hash, pin it at submit so a later NetSuite re-pull can be checked for drift:

```shell
python3 scripts/close_state.py --run-dir <dir> submit  --actor autopilot --amount <total> \
  --source-tb-sha256 <sha256 of the staged NetSuite pull>
python3 scripts/close_state.py --run-dir <dir> review  --actor <reviewer>
python3 scripts/close_state.py --run-dir <dir> approve --actor <approver> --threshold <sod_threshold>
python3 scripts/close_state.py --run-dir <dir> lock    --actor <approver> --approval-token <out-of-band>
python3 scripts/close_state.py --run-dir <dir> verify-source --current-hash <hash of a fresh NetSuite pull>
```

`verify-source` is the **changed-after-sign-off** check — it flags a NetSuite balance that moved after the preparer signed off, which is the cross-system control this NetSuite chain adds on top of NetSuite's own audit trail.

## What to hand back

1. The close package HTML (the review surface), with its traceability + self-certified banners intact.
2. Whether the NetSuite pull tied on the first try, or what `netsuite_doctor.py diagnose` found if it didn't.
3. The reconciliation flags and material flux lines the reviewer must clear.
4. The next-step approval + `verify-source` commands above.
5. The finance Output Contract block (CLAUDE.md §6) — Sources cited, Materiality threshold applied, Confidentiality.

## Honesty

State the day-budget honestly: **one-time NetSuite setup (certificate, integration record, role provisioning) needs a NetSuite admin and change control — budget days, not hours, the first time.** The **recurring** close, once wired, can approach a day for a layperson. Do not sell "close in a day" for a first-time build. State the traceability badge as-is — a TB-only run is not audit-traceable, and the cash flow is an unaudited draft (see [`close-approval-workflow`](../skills/close-approval-workflow/SKILL.md)'s tier caveat). This is a reference implementation and offline harness, not a certified NetSuite connector; live wiring is the consumer's step (see [`netsuite-close`](../skills/netsuite-close/SKILL.md)'s honest-boundary block).

---
name: close-approval-workflow
description: "The governed review→approve→lock state machine with enforced segregation of duties and an append-only hash-chained audit log. Refuses same-actor approval above threshold and illegal transitions. Runs scripts/close_state.py. Honest tier caveats. Used by `controller` + `audit-prep-specialist`."
---

# Skill: close-approval-workflow

**Purpose:** Make the close's controls *enforced by construction*, not documented. Every deliverable is submitted into a state machine that refuses illegal transitions and refuses a same-actor approval above the entity's SoD threshold, writing every event to an append-only, hash-chained audit log.

Engine: [`../../scripts/close_state.py`](../../scripts/close_state.py) (stdlib only).

## Why it exists

The failure mode behind the public "AP agent released ~$92K past a documented control" incident (2025) is a control that was *written down but not enforced*. Here the enforcement is code: the state machine is the only path a package can advance, and the SoD check is a hard refusal, not a policy note.

## State model

```
draft → submitted → in_review → approved → locked
                  ↘ (reject) → draft        ↘ (authorized reopen) → draft
```

- `submit` records the preparer + package amount.
- `approve` **refuses** when `actor == preparer` and `amount ≥ sod_threshold` (logged denial).
- `lock` needs a **non-agent approval token**; without it the package is badged **self-certified, single-actor** (a stderr warning + a `state.json` flag).
- `verify` recomputes the hash chain end-to-end; any retroactive edit breaks it (exit non-zero).

## Invocation

```shell
D=.ravenclaude/runs/close/<entity>/<period>
python3 scripts/close_state.py --run-dir $D submit  --actor autopilot --amount 1852500
python3 scripts/close_state.py --run-dir $D review  --actor controller
python3 scripts/close_state.py --run-dir $D approve --actor controller --threshold 100000
python3 scripts/close_state.py --run-dir $D lock    --actor controller --approval-token <out-of-band>
python3 scripts/close_state.py --run-dir $D verify
```

## HONEST TIER CAVEAT (do not overclaim)

Identity here is **config-asserted, not authenticated** — `--actor NAME` is a caller-supplied string with no identity-provider binding. The hash chain is therefore tamper-**evident** (a third party detects an edit), **not** tamper-**preventing** against the operator who holds the file. At this local tier the SoD check stops the *same declared actor* self-approving above threshold and stops the accidental single-process auto-approve — it does **not**, by itself, make the close auditor-grade, and it does **not** "design out" the Ramp incident. Real auditor-reliable segregation needs an identity provider + an immutable store, which lands at the warehouse/ELT tier. LOCK's non-agent approval-token requirement is the bridge: absent it, the package is explicitly self-certified. State this caveat wherever the workflow's controls are described.

## Orchestrator boundary

The close orchestrator ([`run-controller-cycle`](../../commands/run-controller-cycle.md)) calls **`submit` only** — reaching `approved`/`locked` always requires a separate, later, human-invoked call. This is regression-tested ([`test_controller_autopilot.py`](../../scripts/test_controller_autopilot.py)) so an unattended run can never collapse the review gate.

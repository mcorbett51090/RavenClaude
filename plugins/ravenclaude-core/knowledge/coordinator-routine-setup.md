# Coordinator Routine setup — the exact `create_trigger` call shapes

**Status:** runtime-action reference (Task 7.1/7.2). Binding the coordinator's Routines is a **runtime
action**, not a file the plugin ships — this document exists so the action is reproducible without
re-deriving the call shape each time.

**Owner: Matt.** Two Routines are bound, both self-bind mode (no `persistent_session_id`, no
`create_new_session_on_fire`), `initiation: "human_request"` for the first bind of each.

## Routine 1 — the coordinator's own wake cadence (Task 7.1)

```
create_trigger(
  name: "source-control-coordinator wake",
  prompt: "<the coordinator's own wake instructions — resume as source-control-coordinator, "
          "read the ledger queue per coordinator-ledger-convention.md, act on the fixed verb "
          "allowlist, escalate anything else>",
  cron_expression: "0 * * * *",   # hourly, per Gate G3's documented floor — accept the tool's
                                    # own stated "normally hourly" floor rather than guessing a
                                    # smaller number and having it fail silently at runtime
  initiation: "human_request"
)
```

Acceptance test: `list_triggers` shows the new trigger; after its first scheduled fire,
`last_run.status == "SUCCEEDED"`. Record the resulting `trigger_id` in the coordinator's status
snapshot (`.ravenclaude/runs/coordinator/status.json`) so any session can discover whether a Routine
is actually bound without asking Matt.

## Routine 2 — weekly self-restart (Task 7.2)

Closes the "no context-management story for a multi-week role" gap. On fire, the coordinator ends its
current session and re-binds fresh, re-subscribing to exactly the open coordinator-tagged PR set it
reads back from the ledger/status snapshot. Because all durable state lives in the ledger and the
status record — never session memory — this restart is cheap and safe: a maintenance non-event, not a
manual recovery.

```
create_trigger(
  name: "source-control-coordinator weekly self-restart",
  prompt: "<end this session; on the next wake, re-bind fresh and re-subscribe to the open "
          "coordinator-tagged PR set from the ledger/status snapshot>",
  cron_expression: "0 6 * * 1",   # weekly, Monday 06:00 UTC — an arbitrary low-traffic slot;
                                    # adjust to the repo's own quiet window
  initiation: "human_request"
)
```

Acceptance test: force a restart tick and confirm the freshly-bound session re-subscribes to the same
PR set the outgoing session had, with no gap in coverage beyond the restart's own brief window.

## Disable — the authoritative stop (see strategic-plan.md "Rollout & rollback" for the full ordering)

`list_triggers` → `delete_trigger` on **both** `trigger_id` (Routine 1) and `restart_trigger_id`
(Routine 2) is the authoritative stop — it removes the wake source itself, so a malfunctioning,
confused, or prompt-injected coordinator cannot un-delete a trigger it is not currently running. Do
this before flipping the `source_control_coordinator` comfort-posture knob, which is a cooperative
signal only (read by the coordinator's own runtime), not a containment control over an
already-running, misbehaving coordinator.

## Cron-floor gate (G3)

This tool's own description states: "Minimum interval is normally hourly (some projects allow
shorter); a too-frequent schedule is rejected and the error names the minimum." This plan accepts the
documented floor and defaults to hourly (`0 * * * *`) rather than empirically probing for a shorter
interval — the gate's own explicit alternative ("accept the documented floor and skip straight to
hourly") was taken this round.

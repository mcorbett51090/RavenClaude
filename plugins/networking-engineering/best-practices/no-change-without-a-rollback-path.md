# No network change without a rollback path

**Status:** Absolute rule
**Domain:** Change management / operations
**Applies to:** `networking-engineering`

---

## Why this exists

A network change is uniquely self-endangering: the same control plane you're editing is
the one carrying your management session. A single wrong ACL, route filter, or interface
shutdown can lock you out of the very device you need to fix — turning a two-minute change
into a truck roll or a data-center visit. The rollback path is what makes the change
*reversible from a distance*, which is the only kind of change that's safe to make remotely.

## How to apply

**Do:**
- Use **commit-confirm / rollback-timer** mechanisms where the platform supports them: apply the change with an automatic revert that fires unless you confirm from a *second, verified path* within N minutes.
- Where there's no commit-confirm, stage a **saved rollback config** and a scheduled reload-to-rollback as a dead-man's switch.
- Capture **pre-change state** (routes, adjacencies, the affected flows) so you can prove whether to roll back.
- Validate post-change **from a different path than the one you changed** before confirming.

**Don't:**
- Apply a change that can partition your management plane with no auto-revert.
- Confirm a change by checking only from the device you just changed (it can lie).
- Skip the rollback "because it's a small change" — the small changes cause the lockouts.

## Edge cases / when the rule does NOT apply

- **Purely additive, non-disruptive reads/telemetry config** carries near-zero lockout risk — a rollback plan is still cheap insurance but not existential.
- **Greenfield lab/virtual topologies** with no production traffic — iterate freely; the rule is about production blast radius.

## See also
- [`../skills/configure-switching-routing-and-services/SKILL.md`](../skills/configure-switching-routing-and-services/SKILL.md)
- [`./config-as-code-is-the-source-of-truth.md`](config-as-code-is-the-source-of-truth.md)

## Provenance
Codifies the `network-implementation-engineer` house opinion "commit-confirm or it didn't happen safely" and standard change-management discipline. Last reviewed 2026-07-01.

---

_Last reviewed: 2026-07-01 by `claude`_

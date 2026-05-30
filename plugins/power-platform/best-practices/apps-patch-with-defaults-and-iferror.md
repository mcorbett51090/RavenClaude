# Write Dataverse records with `Patch(Defaults(table), ...)` wrapped in `IfError` — never a hand-rolled record literal

**Status:** Absolute rule — a canvas write with no error handling and no `Defaults()` is a bug.

**Domain:** Canvas apps / Power Fx

**Applies to:** `power-platform`

---

## Why this exists

`Patch` with a hand-rolled record literal skips required fields, ignores column default values, and bypasses column behavior — the record saves with nulls the server expected the platform to fill, or fails on a constraint the maker never sees. `Defaults(table)` returns a record pre-populated with the table's declared defaults and required-field placeholders, so `Patch(Defaults(table), {...})` respects the schema. Separately, a `Patch` with no error path fails silently: the user clicks Save, nothing visible happens, and the record never wrote. Constitution §3 #10 makes error handling part of the build — canvas writes go through `IfError(Patch(...), Notify(...))`, not a follow-up.

## How to apply

New record = `Patch(table, Defaults(table), {fields})`. Existing record = `Patch(table, record, {fields})`. Wrap both in `IfError` with a user-visible `Notify`.

```powerfx
// DON'T — hand-rolled literal skips required fields + no error path.
Patch(Contacts, { firstname: txtFirst.Text, lastname: txtLast.Text })

// DO — Defaults() respects schema; IfError surfaces failure to the user.
IfError(
    Patch(
        Contacts,
        Defaults(Contacts),
        { firstname: txtFirst.Text, lastname: txtLast.Text }
    ),
    Notify("Couldn't save contact: " & FirstError.Message, NotificationType.Error),
    Notify("Contact saved.", NotificationType.Success)
)
```

**Do:**

- Use `Defaults(table)` for every new record; pass the existing record (not its GUID) for updates.
- Wrap every write in `IfError` and `Notify` the user on both failure and success.
- Use `NotificationType.Error` for failures so the message styling matches severity.
- Look records up by name or alternate key, never by a hard-coded GUID (constitution §3 #11).

**Don't:**

- Block the user with a modal screen for routine feedback — `Notify` is non-blocking and accessible.
- Swallow `Patch` errors silently or rely on the gray "something went wrong" banner.
- Construct a record literal for a new row when `Defaults()` exists.

## Edge cases / when the rule does NOT apply

- **Bulk `Patch` with a table argument** (`Patch(table, colChanges)`) — still wrap in `IfError`; check `Errors(table)` for per-row failures rather than a single `FirstError`.
- **Forms control writes** — `SubmitForm`/`EditForm` have their own `OnFailure`/`OnSuccess` events; use those rather than wrapping `SubmitForm` in `IfError`.
- **Optimistic-UI scenarios** where you intentionally write-then-reconcile — still `IfError`, but the recovery path differs (roll back the local collection).

## See also

- [`../agents/power-fx-engineer.md`](../agents/power-fx-engineer.md) — "`Patch` with `Defaults(table)` … never a hand-rolled record literal" is this agent's stated rule
- [`./apps-delegation-first-data-access.md`](./apps-delegation-first-data-access.md)
- [`../skills/canvas-app-performance/SKILL.md`](../skills/canvas-app-performance/SKILL.md) — Patch performance (split large patches, push to a flow)
- Constitution §3 #10 (error handling is part of the build) and #11 (no GUIDs in formulas)

## Provenance

From `power-fx-engineer.md` opinions (`Patch`+`Defaults`, `Notify` with the right type) and plugin constitution §3 #10/#11. The silent-write failure mode is the agent's flagged anti-pattern.

---

_Last reviewed: 2026-05-30 by `claude`_

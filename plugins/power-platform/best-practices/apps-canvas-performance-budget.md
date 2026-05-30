# Treat every canvas property as a function the runtime re-evaluates — budget network calls and control count

**Status:** Pattern — strong default; deviate only with a Monitor trace that justifies it.

**Domain:** Canvas apps / Power Fx

**Applies to:** `power-platform`

---

## Why this exists

Most slow canvas apps got slow at design time, not from "extra features." A control's `Items`, `Text`, and `Visible` properties are not set once — they are expressions the runtime re-evaluates whenever a referenced dependency changes. A `LookUp()` inside a gallery's `ThisItem` context runs once per visible row on every refresh; with 200 Dataverse-backed rows that is 200 connector calls per gallery refresh. Network calls dominate cost; local Power Fx is cheap. If you do not budget connector calls and control count up front, no amount of after-the-fact tuning recovers the lost design.

## How to apply

Pre-load once, then operate locally. Parallelize independent loads. Denormalize lookups out of gallery item templates.

```powerfx
// DON'T — a per-row connector round-trip inside the gallery template.
// gal.Items = Accounts ; lblOwner.Text = LookUp(Users, id = ThisItem.OwnerId).fullname

// DO — pre-collect parents once on screen show, LookUp against the local collection.
// Screen.OnVisible:
Concurrent(
    ClearCollect(colAccounts, Accounts),
    ClearCollect(colUsers, Users)
);
// gal.Items = colAccounts ; lblOwner.Text = LookUp(colUsers, id = ThisItem.OwnerId).fullname
```

**Do:**

- Wrap 2+ independent loads in `Concurrent()` — same work, ~1/Nth the wall-clock on a network-bound load.
- Load per-screen data in `Screen.OnVisible`, not `App.OnStart` (which blocks the splash screen).
- Keep one screen under ~500 controls; move heavy data entry to a model-driven form or Custom Page.
- Run **Monitor** first (Tools → Monitor, sort by Duration desc) and fix the top entries — do not optimize what is not slow.

**Don't:**

- `LookUp`/`Filter` against a connector inside a gallery item template.
- Stack four hidden containers as a "tab" pattern — all four stay in the control tree and get evaluated.
- `ClearCollect` on every `OnSelect` of a button users mash — that is a network round-trip per click.

## Edge cases / when the rule does NOT apply

- **Live data that must reflect server changes mid-session** — a cached collection goes stale; refresh deliberately (`Refresh(source)` + re-collect) or bind directly and accept the call cost.
- **Truly tiny screens** (a single form, a handful of controls) — the control-count budget is irrelevant; do not add collection machinery for 10 rows.
- **`App.OnStart`** legitimately holds user context (`Set(varUser, User())`) and app config that every screen needs before first navigation — that is what it is for; the rule is against bulk data loads there.

## See also

- [`../skills/canvas-app-performance/SKILL.md`](../skills/canvas-app-performance/SKILL.md) — full playbook (runtime model, Concurrent, control-count budget, Monitor workflow)
- [`./apps-delegation-first-data-access.md`](./apps-delegation-first-data-access.md) — the delegation half of canvas performance
- [`./apps-power-fx-named-formulas-and-with.md`](./apps-power-fx-named-formulas-and-with.md) — named formulas keep `OnStart` lean
- [`../agents/power-fx-engineer.md`](../agents/power-fx-engineer.md)

## Provenance

Condensed from the `canvas-app-performance` skill (Core Principles #2–#5, §1, §4, §6–§8) shipped in `power-platform`, and constitution §3. The "every property is a function" mental model is the skill's framing.

---

_Last reviewed: 2026-05-30 by `claude`_

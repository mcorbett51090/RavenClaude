# Treat the PCF lifecycle as a contract — clean up in `destroy()` and keep `updateView` idempotent

**Status:** Absolute rule — a PCF that leaks listeners/timers in `destroy()` or fires `notifyOutputChanged()` from inside `updateView()` is a bug.

**Domain:** PCF / Canvas + Model-driven apps

**Applies to:** `power-platform`

---

## Why this exists

A PCF control's four methods (`init`, `updateView`, `getOutputs`, `destroy`) are a host-managed contract, not suggestions. Two failures recur. First, skipping cleanup in `destroy()` leaves zombie event handlers, running timers, and live chart/editor/map instances behind every time the control is removed (navigate away, form close, business-rule hide) — the form session accumulates leaks and eventually janks or crashes. Second, calling `notifyOutputChanged()` unconditionally from inside `updateView()` creates an infinite render loop: the notify triggers `getOutputs()`, which can trigger another `updateView`, forever. `updateView` is called on **every** bound-prop change, resize, and dataset refresh, so it must be fast and idempotent.

## How to apply

Store references in `init`, guard every `updateView` mutation behind a value comparison, and release everything you acquired in `destroy`.

```typescript
public init(context, notifyOutputChanged, state, container) {
  this._notify = notifyOutputChanged;
  this._container = container;
  this._onInput = this._handleInput.bind(this);   // keep a stable ref so removeEventListener works
  this._input = document.createElement("input");
  this._input.addEventListener("input", this._onInput);
  this._container.appendChild(this._input);
}

public updateView(context) {
  // DON'T: this._notify() here unconditionally — infinite loop.
  const next = context.parameters.value.raw;
  if (next !== this._value) {            // DO: guard the mutation behind a change check
    this._value = next;
    this._input.value = (next ?? 0).toString();
  }
  this._input.disabled = context.mode.isControlDisabled;
}

public destroy() {
  this._input.removeEventListener("input", this._onInput);   // DO: release what init acquired
}
```

**Do:**

- Cancel timers, fetch/abort controllers, subscriptions, and third-party instances (maps, editors, chart libs) in `destroy()`.
- Bind handlers once and keep the reference, so `removeEventListener` actually de-registers the same function.
- Compare incoming `context.parameters.*.raw` against cached state before re-rendering or notifying.
- Call `notifyOutputChanged()` only from a real user/data event handler, never as an unconditional `updateView` side effect.
- Check `dataSet.loading` before reading `sortedRecordIds` on dataset controls — stale/empty data otherwise.

**Don't:**

- Start an unguarded async operation in `updateView()` — a slow response can render against a stale view.
- Use `context.webAPI` on every `updateView`; cache and refresh deliberately.
- Rely on garbage collection to tear down DOM listeners or external libraries — the host won't do it for standard controls.

## Edge cases / when the rule does NOT apply

- **React virtual controls** — you return a `ReactElement` from `updateView`; the platform owns the React tree, so React-internal cleanup is automatic. You **still** clean up non-React resources (timers, subscriptions, webAPI aborts) in `destroy()`.
- **Resize-driven re-render** — if you opt into `context.mode.trackContainerResize(true)`, `updateView` legitimately fires on resize with unchanged bound props; branch on `allocatedWidth/Height` rather than treating it as a data change.
- **Deliberate output on first render** — a control that must seed an unbound output once can notify after `init`, but still guard re-notification.

## See also

- [`../skills/pcf-controls/resources/pcf-lifecycle.md`](../skills/pcf-controls/resources/pcf-lifecycle.md) — full lifecycle, dataset API, the `updateView`-storm warning
- [`./apps-react-virtual-controls-default.md`](./apps-react-virtual-controls-default.md)
- [`./apps-pcf-when-to-build.md`](./apps-pcf-when-to-build.md)
- [`../agents/pcf-developer.md`](../agents/pcf-developer.md) — "treats PCF lifecycle methods as a contract"
- [`../knowledge/apps-decision-trees.md`](../knowledge/apps-decision-trees.md)

## Provenance

From `pcf-controls` skill `resources/pcf-lifecycle.md` (the `destroy()` cleanup list and the explicit "`updateView` storm" infinite-loop warning, Debugging Tips #3) and `pcf-developer.md` opinions/anti-patterns ("`updateView` that triggers a render even when bound props haven't changed", "lifecycle methods as a contract").

---

_Last reviewed: 2026-05-30 by `claude`_

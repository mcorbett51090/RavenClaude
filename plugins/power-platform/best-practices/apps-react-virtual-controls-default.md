# Build new PCF controls as React virtual controls and declare platform libraries — don't bundle your own React/Fluent

**Status:** Pattern — strong default for new PCF work; non-virtual is legacy.

**Domain:** PCF / Canvas + Model-driven apps

**Applies to:** `power-platform`

---

## Why this exists

Virtual controls reuse the host's React and Fluent via `<platform-library>` declarations instead of bundling their own copy. The payoff is a smaller bundle (the control loads on every form render), a managed React lifecycle (you return a `ReactElement` from `updateView` and never call `ReactDOM.render`), and automatic theme-alignment with the app shell. Bundling your own React/Fluent inflates the bundle and risks version skew with the host. Non-virtual standard controls are the legacy path; new builds should opt into the virtual lifecycle. The version contract is subtle and version-gated: you author against the **allowed (declared)** version's typings while the platform may **load a higher compatible version at runtime** — so type-check against the declared version and test against the runtime one.

## How to apply

Scaffold with `--framework react`, declare the platform libraries, and let the host inject React/Fluent. Fluent v9 (`@fluentui/react-components`) is the default for new work.

```bash
pac pcf init --namespace MyCo.Controls --name MyReactSlider --template field --framework react
```

```xml
<!-- ControlManifest.Input.xml — declare; the host provides at build + runtime -->
<resources>
  <platform-library name="React"  version="16.14.0" />        <!-- verify before quoting -->
  <platform-library name="Fluent" version="9.46.2" />         <!-- v9; verify before quoting -->
</resources>
```

```typescript
// updateView RETURNS a ReactElement — platform owns the tree; no ReactDOM.render, no `container` in init.
public updateView(context): React.ReactElement {
  return React.createElement(SliderComponent, {
    value: context.parameters.value.raw,
    disabled: context.mode.isControlDisabled,
    onChange: this._handleChange.bind(this),
  });
}
```

**Do:**

- Use Fluent **v9** for new controls; re-verify the exact allowed/runtime versions against MS Learn before quoting them to a customer (Microsoft bumps runtime-loaded versions without changing the allowed range).
- Bridge host theme tokens via `context.fluentDesignLanguage` into a `FluentProvider` so the control matches the app.
- Rebuild existing virtual controls with `pac` CLI `>=1.37` so they pick up future platform React upgrades.

**Don't:**

- Declare **both** Fluent v8 and v9 in one manifest — exactly one Fluent major per control (a hard platform rule). Drop the `<platform-library name="Fluent">` element entirely if you don't use Fluent.
- Expect setting `control-type="virtual"` on an existing standard control to convert it — it does **not**. Scaffold a new react control and port `index.ts` (the React `init` has no `container`/`div` parameter).
- Bundle your own `react`/`react-dom`/`@fluentui/*` — the host provides them.

## Edge cases / when the rule does NOT apply

- **Power Pages** — React controls & platform libraries are **not supported**; use a *standard* (non-virtual) PCF or a web template there.
- **Porting an existing Fluent v8 control** — staying on v8 (`@fluentui/react`) is fine when a v9 equivalent doesn't exist yet or the port isn't worth it.
- **Tiny non-UI controls** with no React surface — don't add React machinery to a control that draws nothing.

## See also

- [`../knowledge/pcf-react-fluent-platform-libraries.md`](../knowledge/pcf-react-fluent-platform-libraries.md) — canonical version source-of-truth + the v8/v9 single-manifest rule + `## Decision Tree: PCF — Which React surface?`
- [`../skills/pcf-controls/resources/fluent-v9-theming-and-migration.md`](../skills/pcf-controls/resources/fluent-v9-theming-and-migration.md) — theming bridge + v8→v9 component map
- [`../skills/pcf-controls/resources/pcf-lifecycle.md`](../skills/pcf-controls/resources/pcf-lifecycle.md) — the React virtual control interface
- [`./apps-pcf-lifecycle-and-cleanup.md`](./apps-pcf-lifecycle-and-cleanup.md)
- [`../agents/pcf-developer.md`](../agents/pcf-developer.md) — "React virtual controls > non-virtual for new builds"

## Provenance

From `knowledge/pcf-react-fluent-platform-libraries.md` (version table, v8/v9 mutual-exclusion, GA + CLI `>=1.37` rebuild, no-auto-convert, Power Pages unsupported — all tagged "verify before quoting" upstream) and `pcf-developer.md` opinions. Specific versions inherit the upstream "verify before quoting" marker — they are version-gated and volatile.

---

_Last reviewed: 2026-05-30 by `claude`_

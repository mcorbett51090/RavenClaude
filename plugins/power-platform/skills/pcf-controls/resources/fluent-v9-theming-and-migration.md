# Fluent UI v9 in PCF — theming + v8→v9 migration

Reference for building PCF **virtual controls** on Fluent UI v9 (`@fluentui/react-components`): wiring `FluentProvider`, bridging the host theme so the control matches the app shell, the Griffel styling model, and porting existing v8 controls. Versions live in the canonical source — see [`../../../knowledge/pcf-react-fluent-platform-libraries.md`](../../../knowledge/pcf-react-fluent-platform-libraries.md) (don't quote versions from here; quote them from there).

---

## FluentProvider + theme

A v9 control must wrap its tree in a `FluentProvider` with a theme. Ship the base web themes and switch on the host's color mode:

```tsx
import { FluentProvider, webLightTheme, webDarkTheme } from "@fluentui/react-components";

// in updateView(), return the provider-wrapped element:
return React.createElement(
  FluentProvider,
  { theme: isDarkMode ? webDarkTheme : webLightTheme },
  React.createElement(MyControl, props)
);
```

`webLightTheme` / `webDarkTheme` are the v9 base themes. They give you a coherent look out of the box, but they do **not** automatically match the surrounding Power Apps shell — that's the next step.

### Bridge `context.fluentDesignLanguage` host tokens into the v9 theme

The host exposes its active Fluent design language (brand ramp, color mode, density) on `context.fluentDesignLanguage`. Bridge it into the v9 theme so the control matches the app shell instead of looking like a foreign island:

```tsx
const host = context.fluentDesignLanguage; // may be undefined in the test harness
const theme = host?.tokenTheme ?? (host?.isDarkTheme ? webDarkTheme : webLightTheme);
// host?.tokenTheme is already a v9-shaped Theme on supported hosts;
// fall back to webLightTheme/webDarkTheme when it's absent (e.g. the PCF test harness).
return React.createElement(FluentProvider, { theme }, /* ... */);
```

- Read `context.fluentDesignLanguage?.isDarkTheme` for the host's color mode.
- Prefer the host's supplied token theme when present; fall back to the `web*Theme` constants so the control still renders in the harness and on older hosts.
- Re-read on every `updateView` — the host can switch theme/mode at runtime.

## Styling: Griffel (`makeStyles` / `tokens`) vs v8 `mergeStyles`

v9 styles are authored with **Griffel** (`makeStyles` + `tokens`), not v8's `mergeStyles` / `getTheme()`:

```tsx
import { makeStyles, tokens } from "@fluentui/react-components";

const useStyles = makeStyles({
  root: {
    color: tokens.colorNeutralForeground1,
    backgroundColor: tokens.colorNeutralBackground1,
    paddingInline: tokens.spacingHorizontalM,
  },
});
```

- `tokens.*` are **theme-aware design tokens** — they resolve against the `FluentProvider` theme, so a control styled with `tokens` automatically tracks the bridged host theme above. This is the payoff: style with tokens, theme once, match the shell everywhere.
- `makeStyles` returns a hook; call it inside the component (`const styles = useStyles();`) and apply `className={styles.root}`.
- **Do not** carry over v8 `mergeStyles` / `mergeStyleSets` / `getTheme()` — they don't read the v9 token theme and will drift from the shell.

## v8 → v9 component mapping

For the components already named in [`component-patterns.md`](component-patterns.md), here is the v8 → v9 swap. v9 packages everything under `@fluentui/react-components`.

| Pattern (component-patterns.md) | Fluent v8 (`@fluentui/react`) | Fluent v9 (`@fluentui/react-components`) | Migration notes |
|---|---|---|---|
| Slider / Range (§1) | `Slider` | `Slider` | v9 `Slider` is uncontrolled-friendly; read `onChange` `data.value`. |
| Toggle / Switch (§2) | `Toggle` | `Switch` | Renamed `Toggle` → `Switch`; `checked` / `onChange` (`data.checked`). |
| Color Picker (§4) | `ColorPicker` / `SwatchColorPicker` | `ColorPicker` / `SwatchPicker` | `SwatchColorPicker` → `SwatchPicker` (+ `ColorSwatch`); compose `ColorPicker` from `ColorArea` + `ColorSlider` in v9. |
| Card Gallery (§9) | `Card` (community/v8 layouts) | `Card`, `CardHeader`, `CardPreview` | v9 ships first-class `Card` primitives; build the gallery grid with `makeStyles`. |
| File Upload (§11) | (no first-class v8 uploader) | `FileUploader` pattern via Griffel drop zone | v9 has no drop-in `FileUploader`; compose `Button` + hidden `<input type=file>` + a Griffel-styled drop zone. |

When porting, scaffold a **new** virtual control (`pac pcf init ... -fw react`) and move the manifest + logic across — there is no in-place standard→virtual or v8→v9 auto-convert.

## Upgrade step: rebuild with CLI `>=1.37`

Existing virtual controls keep functioning, but **rebuild and redeploy them with `pac` CLI `>=1.37`** so they pick up future platform React-version upgrades. Run `pac install latest` if unsure, then rebuild (`npm run build`) and repackage.

---

For ALM packaging (solution init → add-reference → build → import) and the fresh-environment **test-the-import** step, see [`manifest-reference.md`](manifest-reference.md) (Solution Packaging Workflow).

# Design system spec — [System name] [Version]

> Token + component visual spec. Consumed by `frontend-implementer` to wire into code.

**System:** [...]
**Version:** [v1.0]
**Last updated:** [YYYY-MM-DD]
**Owner:** [...]
**Token build:** [Style Dictionary | manual | other]

---

## Color

### Primitive tokens

```yaml
color:
  brand:
    50:  "#..."
    100: "#..."
    ...
    900: "#..."
  gray:
    50:  "#..."
    100: "#..."
    ...
    900: "#..."
  success:
    50:  "#..."
    ...
  warning:
    50:  "#..."
    ...
  danger:
    50:  "#..."
    ...
```

### Semantic tokens (light mode)

```yaml
color:
  text:
    primary:    "color.gray.900"
    secondary:  "color.gray.700"
    inverse:    "color.gray.50"
  surface:
    page:       "color.gray.50"
    elevated:   "#ffffff"
    accent:     "color.brand.500"
  border:
    default:    "color.gray.200"
    focus:      "color.brand.600"
```

### Semantic tokens (dark mode)

```yaml
color:
  text:
    primary:    "color.gray.50"
    secondary:  "color.gray.300"
    inverse:    "color.gray.900"
  surface:
    page:       "color.gray.900"
    elevated:   "color.gray.800"
    accent:     "color.brand.400"
  border:
    default:    "color.gray.700"
    focus:      "color.brand.400"
```

### Contrast targets

- Body text vs surface: ≥ 4.5:1 (WCAG AA)
- Large text (≥ 18pt regular / 14pt bold) vs surface: ≥ 3:1
- UI components, focus indicators, icons vs surface: ≥ 3:1

## Typography

### Font families

- **Display:** "[Font Name], [fallback stack]"
- **Body:** "[Font Name], system-ui, sans-serif"
- **Mono:** "ui-monospace, [fallback]"

### Type scale (8 sizes)

| Token | Size (rem) | Line-height | Weight | Use |
|---|---|---|---|---|
| `font-display`     | 4.0 | 1.0  | 700 | Hero, big headlines |
| `font-h1`          | 3.0 | 1.1  | 700 | Page titles |
| `font-h2`          | 2.25 | 1.2 | 700 | Section headings |
| `font-h3`          | 1.75 | 1.25 | 600 | Subsection headings |
| `font-body-lg`     | 1.25 | 1.5 | 400 | Lead paragraphs |
| `font-body`        | 1.0 | 1.6  | 400 | Default body |
| `font-body-sm`     | 0.875 | 1.5 | 400 | Captions, helper text |
| `font-caption`     | 0.75 | 1.4 | 500 | Labels, microcopy |

### Font loading

- Preload critical: body weight 400, body weight 600
- `font-display: swap` (or `optional` for display fonts)
- Variable font where possible
- Subset: Latin (or relevant subset for locale)

## Spacing

Geometric scale (8pt system):

| Token | rem | Use |
|---|---|---|
| `space-0` | 0    | Zero / collapse |
| `space-1` | 0.25 | Tight gaps |
| `space-2` | 0.5  | Component internal gaps |
| `space-3` | 0.75 | Tight padding |
| `space-4` | 1    | Default padding |
| `space-6` | 1.5  | Loose padding |
| `space-8` | 2    | Card padding |
| `space-12` | 3   | Section spacing |
| `space-16` | 4   | Major section break |
| `space-24` | 6   | Hero spacing |

## Radius

| Token | Value | Use |
|---|---|---|
| `radius-none` | 0 | Square corners |
| `radius-sm`   | 4px | Buttons, inputs |
| `radius-md`   | 8px | Cards |
| `radius-lg`   | 16px | Modals |
| `radius-full` | 9999px | Pills, avatars |

## Elevation / shadow

| Token | Value | Use |
|---|---|---|
| `elevation-0` | none | Flat |
| `elevation-1` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift |
| `elevation-2` | `0 4px 8px rgba(0,0,0,0.08)` | Cards |
| `elevation-3` | `0 12px 24px rgba(0,0,0,0.12)` | Modals, popovers |

## Motion

| Token | Duration | Easing | Use |
|---|---|---|---|
| `motion-fast`  | 100ms | `ease-out` | Microinteractions |
| `motion-base`  | 200ms | `ease-out` (entry) / `ease-in` (exit) | Defaults |
| `motion-slow`  | 500ms | `ease-in-out` | Page transitions, large reveals |

All motion respects `@media (prefers-reduced-motion: reduce)`.

## Breakpoints

| Token | Min-width (px) |
|---|---|
| `bp-sm` | 640 |
| `bp-md` | 768 |
| `bp-lg` | 1024 |
| `bp-xl` | 1280 |
| `bp-2xl` | 1536 |

## Components

[For each component, link to the spec file.]

- [Button](./components/button.md)
- [Input](./components/input.md)
- [Card](./components/card.md)
- [Modal](./components/modal.md)
- [Navigation](./components/navigation.md)
- [...]

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v1.0 | YYYY-MM-DD | [name] | Initial spec |

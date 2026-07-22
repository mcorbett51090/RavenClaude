---
name: component-api-and-library-build
description: "Design and build an accessible, composable library component with a contract-grade public API — deciding composition vs configuration and controlled vs uncontrolled, baking in roles/focus/keyboard from v1, and shipping a story and usage docs. Traverses the component-API branch of the design-systems decision tree. Reach for this when the user asks 'compose or props for this component?', 'build an accessible Menu/Dialog/Combobox', 'controlled or uncontrolled?', or 'what should this component's public API be?'. Used by design-systems-architect (API shape) and design-tokens-and-component-engineer (implementation)."
---

# Skill: component-api-and-library-build

> **Invoked by:** `design-systems-architect` (the API-shape decision) and
> `design-tokens-and-component-engineer` (the accessible implementation + story + docs).
>
> **When to invoke:** "compose or configure this component?"; "build an accessible
> Menu/Dialog/Combobox"; "controlled or uncontrolled?"; "what's this component's public API?"; any
> "how should this library component be shaped and built" question.
>
> **Output:** a component API decision + an accessible implementation with a Storybook story and
> usage docs, the public contract minimized and stated.

## Procedure

1. **Name the use cases before the API.** List what consumers actually need to do with the
   component. The API serves the real use cases — not every hypothetical. Over-fitting to
   imagined needs is how a component grows 30 props.
2. **Choose composition vs configuration.** Prefer **composition** (compound components / slots:
   `<Menu><Menu.Trigger/><Menu.Item/></Menu>`) when the component has parts consumers arrange or
   customize; prefer **configuration** (props) for genuinely atomic, low-variance components
   (`<Badge tone="warning">`). A boolean-prop explosion is the smell that composition was needed.
3. **Decide controlled vs uncontrolled — deliberately, per component.** Offer **uncontrolled** with
   an internal default for the common case (`defaultOpen`), and **controlled** (`open` + `onOpenChange`)
   for consumers who need to own state. Document which, and don't half-implement (a `value` with no
   `onChange` is a trap).
4. **Bake accessibility in at v1.** Correct role/ARIA (`role="dialog"`, `aria-expanded`,
   `aria-controls`), **focus management** (trap + restore for overlays, visible focus ring, logical
   tab order), and **full keyboard support** (Enter/Space/Arrows/Escape as the pattern demands).
   Lean on the platform's accessible primitives rather than reinventing a listbox. Test with
   keyboard and a screen reader.
5. **Keep the public surface minimal.** Everything public is a future major-version obligation.
   Expose the props the use cases require; keep the rest internal. Forward a `ref` and spread
   remaining props to the right element so consumers aren't blocked, but don't invent public API
   speculatively.
6. **Style from semantic/component tokens only.** No hardcoded values — the component reads
   `color.*`/`space.*` tokens so it themes automatically. A hardcoded hex in a system component is
   a bug.
7. **Ship the story and the docs.** A Storybook story covering the key states (default, open,
   disabled, error, loading, RTL if relevant) and a usage note (do/don't, a11y notes, the prop
   table). A component without a story of its states is under-specified.

## Worked example

> User: "Build an accessible `Menu` for the library. Compose or props?"

- **Use cases:** a trigger button, a list of items, some items disabled, some with icons, keyboard
  navigation, close on select/Escape/outside-click.
- **Shape:** **composition** — `<Menu>`, `<Menu.Trigger>`, `<Menu.Content>`, `<Menu.Item>`,
  `<Menu.Separator>`. Consumers arrange items; the system owns behavior.
- **State:** uncontrolled by default (`defaultOpen`), controlled available (`open`/`onOpenChange`).
- **A11y:** trigger `aria-haspopup="menu"` + `aria-expanded`; content `role="menu"`; items
  `role="menuitem"`; roving tabindex; Arrow/Home/End navigation; Escape closes and restores focus
  to the trigger; type-ahead. Built on the platform's accessible menu primitive
  *(retrieval-dated 2026-07; verify the primitive's API at use)*.
- **Surface:** `Menu.Item` takes `disabled`, `onSelect`, and forwards `ref`/rest — nothing
  speculative.
- **Tokens:** background/foreground/hover/focus all from semantic tokens; no hex.
- **Docs:** story with open/disabled/with-icons/RTL states; usage note on when to use a Menu vs a
  Select.

## Guardrails

- **A boolean-prop explosion means you skipped composition** — reach for slots.
- **Accessibility is v1, not a follow-up** — keyboard + screen-reader tested before "done".
- **Controlled/uncontrolled is a decision, fully implemented** — never a `value` with no handler.
- **No hardcoded style values** — components read tokens so they theme for free.
- **Minimal public surface** — every public prop is a promise you owe a major version to break.
- **No story, not shipped** — the story is the component's living spec.

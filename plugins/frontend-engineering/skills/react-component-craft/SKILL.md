---
name: react-component-craft
description: "Build composable, accessible React components: small components with clear props (composition over a flag-laden mega-component), correct hooks (complete deps, no stale closures, effects only for external sync), controlled validated forms, and accessibility in the markup."
---

# React Component Craft

## Compose
Small components, clear props; shared logic in custom hooks. Refactor the thirty-flag god-component.

## Hooks correctly
Complete `useEffect`/`useMemo` **deps**; no stale closures; effects only to **sync with the outside**, not to derive state. Most 'React is weird' bugs are dependency bugs.

## Accessibility in markup
Semantic elements first (`button`/`nav`/`label`), ARIA only to fill gaps, keyboard-operable, focus managed. (Audit -> web-design.)

## Forms & testability
Controlled, validated, accessible errors; stable `data-testid`/roles for `qa-test-automation`.

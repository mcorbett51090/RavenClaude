# Stop prop-drilling beyond two levels — lift or use context

**Status:** Pattern
**Domain:** React component design
**Applies to:** `frontend-engineering`

---

## Why this exists

Prop-drilling — passing a value through two or more intermediate components that don't use it themselves — creates invisible coupling. When the data shape changes, you must update every intermediate component. It makes components harder to move, harder to test in isolation, and signals that the component boundary is wrong. Beyond two hops, the cost of the coupling consistently exceeds the cost of a context, a composition refactor, or state lifted to the right scope.

## How to apply

The choices in order of preference:

1. **Composition / children** — if the intermediate component does not care about the value, pass the consuming component as a child.
2. **Context** — for values consumed in a subtree by multiple components (theme, locale, user identity).
3. **State co-location / lifting** — if you're drilling because state lives too low, lift it to the common ancestor.
4. **Global store** — only for truly cross-cutting state with no natural owner.

```tsx
// Bad: drilling userId through Layout and Sidebar just to reach UserAvatar
<Layout userId={userId}>
  <Sidebar userId={userId}>
    <UserAvatar userId={userId} />
  </Sidebar>
</Layout>

// Good: composition — Layout doesn't touch userId
const avatar = <UserAvatar userId={userId} />;
<Layout>
  <Sidebar topSlot={avatar} />
</Layout>

// Good: context for a value many components in the tree need
const UserContext = createContext<User | null>(null);
// Provide at the root, consume with useContext anywhere in the subtree
```

**Do:**
- Ask "does this intermediate component actually use the prop?" — if not, consider composition.
- Use context for stable, infrequently-changing values consumed across a wide subtree (user, theme, locale).
- Keep context value changes rare; a frequently-changing context value re-renders every consumer.

**Don't:**
- Put all application state in a global store to avoid drilling — that's the opposite mistake.
- Create a new context for every minor piece of state — context is for values shared across a subtree, not for convenience.
- Pass callbacks five levels deep — that's the same drilling problem with a function.

## Edge cases / when the rule does NOT apply

A two-level prop pass (parent → child → grandchild) where the intermediary is a simple wrapper is fine. The rule is a heuristic at depth ≥ 3 hops, not a strict count.

## See also

- [`../agents/react-implementation-engineer.md`](../agents/react-implementation-engineer.md) — owns component composition and hook design.
- [`./compose-dont-configure.md`](./compose-dont-configure.md) — the composition-over-configuration rule that motivates the children pattern.

## Provenance

React documentation ("Passing Data Deeply with Context") and the composition pattern documented in the React team's blog. Codifies `react-implementation-engineer`'s component-design posture.

---

_Last reviewed: 2026-06-05 by `claude`_

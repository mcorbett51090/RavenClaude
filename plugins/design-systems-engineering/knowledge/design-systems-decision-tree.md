# Knowledge — Design-systems decision trees

> **Last reviewed:** 2026-07-22 · **Confidence:** High on the durable framings (token tiering,
> composition-vs-configuration, semver-of-a-public-contract, theming-at-the-semantic-tier,
> adoption-as-the-metric — broad industry consensus). **Specific tooling APIs (Style Dictionary,
> Storybook, changesets), the W3C DTCG token-spec status, and framework primitives are volatile —
> re-verify before wiring them (see the reference doc's retrieval dates).**
> The most-asked design-system questions are "does this belong in the system?", "how should tokens
> be tiered?", "compose or configure this component?", "how do we theme / support multi-brand?", and
> "what version bump is this?". These are the trees the team traverses **before** naming a structure.

The team's discipline: **name the boundary first (system vs product), tier tokens by intent, choose
the component contract before writing it, and version by the contract you're breaking.** Tooling
specifics carry a retrieval date and are verified at use. Building an *app* leaves this layer for
`frontend-engineering`; a WCAG *audit* goes to `accessibility-engineering`; *site/brand visual
design* is `web-design`. This team owns the **system** those all build from.

---

## Decision Tree 1: does this belong in the system?

Gate on **reuse × stability × worth-standardizing** — an opinionated system, not a greedy one.

```mermaid
graph TD
  Start([Should this live in the design system?]) --> REUSE{Reused across<br/>2+ surfaces?}
  REUSE -->|No, one product| PROD[Keep in the product<br/>· note a promotion path<br/>· promote if reuse emerges]
  REUSE -->|Yes| STABLE{API/appearance<br/>stable, not churning?}
  STABLE -->|Still churning| INCUBATE[Incubate in the product<br/>· let it settle<br/>· promote when the API stops moving]
  STABLE -->|Stable| STD{Worth standardizing?<br/>consistency/a11y/theming payoff}
  STD -->|No, trivial/one-off| PROD
  STD -->|Yes| SYS[Promote into the system<br/>· accessible impl<br/>· semantic tokens<br/>· story + docs + changeset]
```

**Rule of thumb:** a bloated system is as bad as no system. Reused **and** stable **and** worth
standardizing — all three — earns a place. Everything else stays in the product with a promotion
path.

---

## Decision Tree 2: how should tokens be tiered?

Products consume **intent**, never raw values.

```mermaid
graph TD
  Start([Structuring tokens]) --> SRC[Single source of truth<br/>· W3C DTCG JSON or Figma variables<br/>· NOT scattered in CSS]
  SRC --> PRIM[Primitive tier<br/>raw, context-free<br/>color.blue.600, space.4]
  PRIM --> SEM[Semantic tier — INTENT<br/>color.bg.surface, color.text.default<br/>references a primitive]
  SEM --> CONSUME{Who consumes what?}
  CONSUME -->|Products & components| USE[Consume SEMANTIC / component tiers only]
  CONSUME -->|Primitive referenced directly| LEAK[LEAK — flag it<br/>rebrand becomes a refactor<br/>add the missing semantic role]
  SEM --> COMPQ{Component needs a knob<br/>independent of the global value?}
  COMPQ -->|Yes| COMP[Component tier<br/>button.bg.primary → color.action.primary]
  COMPQ -->|No| SKIP[Skip it — semantic is enough<br/>don't add ceremony]
  USE --> OUT[Transform to platform outputs<br/>CSS vars + typed TS map + native]
  COMP --> OUT
```

**The rename test:** if renaming your brand color would force edits in *product* code, the semantic
tier is missing or being bypassed.

---

## Decision Tree 3: compose or configure this component?

```mermaid
graph TD
  Start([Component API shape]) --> UC[List the real use cases first<br/>not hypotheticals]
  UC --> PARTS{Has parts consumers<br/>arrange or customize?}
  PARTS -->|Yes| COMPOSE[COMPOSITION<br/>compound components / slots<br/>Menu.Trigger, Menu.Item]
  PARTS -->|No, atomic low-variance| CONFIG[CONFIGURATION<br/>props: Badge tone=warning]
  CONFIG --> SMELL{Growing many<br/>boolean props?}
  SMELL -->|Yes| COMPOSE
  SMELL -->|No| OK[Props are fine]
  COMPOSE --> STATE{State ownership?}
  OK --> STATE
  STATE -->|Common case| UNC[Uncontrolled + defaultOpen]
  STATE -->|Consumer owns state| CTRL[Controlled: open + onOpenChange]
  UNC --> A11Y[Accessibility at v1<br/>roles, focus mgmt, keyboard]
  CTRL --> A11Y
  A11Y --> SURFACE[Minimize the public surface<br/>every public prop = a major-version promise]
```

**Smell test:** a boolean-prop explosion (`isPrimary`, `isLarge`, `isRounded`, `hasIcon`…) means
composition was the answer.

---

## Decision Tree 4: theming & multi-brand

```mermaid
graph TD
  Start([Support dark mode / multiple brands]) --> WHERE{Solve it where?}
  WHERE -->|Fork components per brand| WRONG[WRONG<br/>components multiply, drift, un-maintainable]
  WHERE -->|Swap semantic-token VALUES| RIGHT[RIGHT<br/>same component tree, different values]
  RIGHT --> AXES[Themes = axes × values<br/>brand × mode = a semantic-value map each]
  AXES --> WIRE[Wire: CSS custom properties<br/>scoped by data-brand / data-theme<br/>or a theme object native]
  WIRE --> CHECK{New brand needs a<br/>different type scale?}
  CHECK -->|Yes| AXIS[Add a typography axis to the semantic tier]
  CHECK -->|No| DONE[Value swap is enough]
```

---

## Decision Tree 5: what version bump is this?

The library's contract = component APIs + token names + rendered output consumers depend on.

```mermaid
graph TD
  Start([What semver bump?]) --> Q1{Removed/renamed a public<br/>prop or token?}
  Q1 -->|Yes| MAJOR
  Q1 -->|No| Q2{Changed a default that<br/>alters rendering, or markup/ARIA<br/>consumers select on?}
  Q2 -->|Yes| MAJOR[MAJOR<br/>+ deprecation → codemod → migration note<br/>remove the old API a major later]
  Q2 -->|No| Q3{Raised a peer-dependency floor?}
  Q3 -->|Yes| MAJOR
  Q3 -->|No| Q4{Added a component / prop /<br/>token / variant — additive?}
  Q4 -->|Yes| MINOR[MINOR<br/>additive by default]
  Q4 -->|No| PATCH[PATCH<br/>bug fix, contract preserved]
  MAJOR --> DOUBT{In doubt minor vs major?}
  MINOR --> DOUBT
  DOUBT -->|Yes| ITSMAJOR[Treat as MAJOR — the contract is sacred]
```

---

## Seams to adjacent plugins

| If the question is… | It belongs to… |
|---|---|
| Build this app / feature / page (a **consumer** of the system) | `frontend-engineering` |
| A WCAG conformance audit, remediation program, or legal a11y posture | `accessibility-engineering` |
| Make this landing page / site visually compelling | `web-design` |
| Create a brand (logo, identity) from scratch | `brand-identity-studio` |
| Author the docs *site* around the library | `technical-writing-docs` |
| The CI/release infra the publish flow runs on | `devops-cicd` |

This team keeps the **system**: tokens, component contracts, versioning, and adoption.

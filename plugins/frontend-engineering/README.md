# Frontend Engineering

The **frontend-engineering** plugin — app-grade frontend engineering — component architecture, rendering strategy (SSR/SSG/RSC/CSR), state and server-data management, performance and bundle discipline, and accessibility-in-code — distinct from web-design's brand/marketing-site craft.

## Agents

- **`frontend-architect`** — Frontend architecture: framework/rendering strategy (CSR/SSR/SSG/ISR/RSC) per route, project structure, component boundaries, the TypeScript posture, and the build/tooling shape
- **`react-implementation-engineer`** — Component implementation: composable React components, hooks correctly (deps, no stale closures, custom hooks), controlled forms, accessibility-in-code (semantic HTML, ARIA, keyboard, focus), and testable markup
- **`frontend-state-and-data-engineer`** — State and data architecture: separating server-cache from client state, server-data libraries (TanStack Query / RSC data), choosing client state (local/context/store), caching/invalidation/optimistic updates, and data-fetching patterns
- **`frontend-performance-engineer`** — Frontend performance: Core Web Vitals (LCP/INP/CLS), JavaScript bundle analysis and code-splitting, lazy-loading, image/font optimization, hydration cost, and the perf budget — the in-code engineering complement to web-design's CWV tuning

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install frontend-engineering@ravenclaude
```

## Seams

- **Brand, visual design, UX/wireflows, the WCAG *audit*, and marketing-site builds** → `web-design`; this team engineers the *app*, that team owns design/brand and the accessibility audit (we implement accessibly, they verify).
- **Login/signup UX and session handling on the client** → `auth-identity` (we render it; they own the auth flow and token discipline).
- **The API the frontend consumes (contract, pagination, errors)** → `api-engineering`; we consume it, they design it.
- **Native iOS/Android (and React Native/Flutter)** → `mobile-engineering`; shared web patterns are ours.
- **E2E test authoring and testability (data-testids)** → `qa-test-automation` (a shared concern — we add the hooks).

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.

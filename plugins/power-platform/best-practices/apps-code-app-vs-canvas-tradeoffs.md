# Choose a Power Apps code app only when you need full DOM/framework control — and check its unsupported-feature list first

**Status:** Pattern — strong default; a code app is the heaviest app surface, gated by an explicit not-supported list.

**Domain:** Canvas + Model-driven apps / Code apps

**Applies to:** `power-platform`

---

## Why this exists

A Power Apps code app is a standalone React/Vue/TypeScript web application that runs as a first-class Power Platform citizen — it inherits Entra ID auth, connectors, and governance (DLP enforced at launch, quarantine, conditional access) while giving you full-page DOM control and a standard Git/Vite build. That power comes with a hard cost: code apps drop a long list of canvas conveniences. Picking a code app without reading the not-supported list produces a late, expensive surprise — you discover mid-build that **environment variables, FetchXML, alternate keys, polymorphic lookups, Solution Packager, and Git-based ALM** are all unavailable. The "PCF trap" compounds it: code apps do **not** receive a `context` object, have no `context.parameters`, and access data through generated typed service classes, not `context.webAPI`.

## How to apply

Reach for a code app only when canvas genuinely can't deliver the UI, and confirm the requirement doesn't depend on anything on the unsupported list.

```text
Need full framework/DOM control, custom routing, a web-dev toolchain,
and NONE of {env vars, FetchXML, alternate keys, polymorphic lookups,
Solution Packager, Git ALM, Excel connectors} is required
      → Power Apps code app
Otherwise (low-code, implicit connectors, solution-packaged ALM)
      → Canvas app
A field/dataset on a form, not a standalone app
      → PCF control (see the React-surface tree)
```

```typescript
// Code apps DON'T get context.webAPI / context.parameters — use generated SDK services.
import { getContext } from "@microsoft/power-apps";
const contacts = await ContactService.getAll();   // generated typed service, OData (not FetchXML)
```

**Do:**

- Read `power-apps-code-apps` skill `resources/overview.md` "Limitations" table before committing — treat it as a gating checklist.
- Confirm the environment has **Enable code apps** toggled and `pac` CLI is recent enough (overview cites `1.51.1+` — verify before quoting).
- Use generated service classes (`ContactService.getAll()`) and OData filters; flag the **Power Apps Premium** end-user license impact.
- Source-control the code app in standard Git for the dev workflow — but know solution-packaged ALM is not the path.

**Don't:**

- Design a code app that relies on environment variables, FetchXML, alternate keys, polymorphic lookups, or Dataverse actions/functions — none are supported.
- Assume code apps behave like PCF (`context.parameters`, `context.webAPI`) — they don't.
- Target the Power Apps mobile app / Power Apps for Windows, or embed Power BI via `PowerBIIntegration` — all unsupported.

## Edge cases / when the rule does NOT apply

- **Feature-set status is volatile** — code apps are a preview-stage feature; the unsupported list and CLI version move. `[unverified — re-check the skill's overview + MS Learn before quoting limits to a customer.]`
- **A field on a form, not a standalone app** — that's a PCF virtual control, not a code app; traverse the React-surface decision tree.
- **Simple themed input / structured CRUD** — canvas or a model-driven form is cheaper; a code app is over-engineering there.

## See also

- [`../skills/power-apps-code-apps/resources/overview.md`](../skills/power-apps-code-apps/resources/overview.md) — the not-supported table, the "PCF trap", the canvas/PCF/code-app comparison
- [`../skills/power-apps-code-apps/SKILL.md`](../skills/power-apps-code-apps/SKILL.md) — CLI, config schema, SDK API
- [`../knowledge/pcf-react-fluent-platform-libraries.md`](../knowledge/pcf-react-fluent-platform-libraries.md) — `## Decision Tree: PCF — Which React surface?` (code-app vs PCF vs canvas)
- [`../knowledge/apps-decision-trees.md`](../knowledge/apps-decision-trees.md) — `Decision Tree: App type — canvas vs model-driven vs code app`
- [`../agents/power-fx-engineer.md`](../agents/power-fx-engineer.md) — owns the code-app lane via the code-apps skill

## Provenance

From `skills/power-apps-code-apps/resources/overview.md` (Limitations table, "PCF Trap", comparison matrix, prerequisites, governance) shipped in `power-platform`, and the `power-fx-engineer` code-app scenario. Preview-status volatility carries the upstream uncertainty marker.

---

_Last reviewed: 2026-05-30 by `claude`_

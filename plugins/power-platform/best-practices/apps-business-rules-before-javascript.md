# Use a business rule before a JavaScript web resource for simple show/hide/require/lock logic

**Status:** Pattern — strong default; write JS only when a business rule genuinely can't express the logic.

**Domain:** Model-driven apps / Web resources

**Applies to:** `power-platform`

---

## Why this exists

Constitution §3 #7 says "lowest-tier mechanism that does the job — business rule before JavaScript." A business rule is a no-code, declarative, designer-authored, solution-aware artifact that the platform applies consistently at form scope (show/hide, set required, lock/unlock, business-recommended, simple set-value). A JS web resource for the same job adds a source-controlled file, a transpile/pack step, a registration on the right form event, null-checking, error handling, and a permanent maintenance and review burden — all to do what a business rule does declaratively. The model-driven anti-pattern list flags exactly this: reaching for `formContext.getAttribute("foo")` (then forgetting the null check) to toggle a field's visibility that a business rule would have handled for free. Keep JS for what it's genuinely *for* — real logic, web API calls, and integrations.

## How to apply

Default to a business rule for declarative form behavior. Cross the line to JS only when the requirement exceeds what a rule can express.

```text
Show/hide a field on a condition           → Business rule
Set required / locked on a condition        → Business rule
Set a default/derived value (simple)        → Business rule
Recommend a value                           → Business rule
Call the Web API, complex branching,
loops, multi-record logic, integration      → JavaScript web resource (TypeScript, source-controlled)
```

**Do:**

- Author show/hide/require/lock and simple set-value as business rules at form scope.
- Reserve JS for Web API calls, genuine branching/loops, and integrations a rule can't express.
- When you do write JS, keep it as source-controlled TypeScript packed into the solution, registered on the form event, using `executionContext.getFormContext()` — and null-check every `getAttribute`.
- Prefer quick-view forms over web-resource HTML for related-record peeks (free, accessible, security-respecting).

**Don't:**

- Write a JS `OnChange` handler to toggle `setVisible`/`setRequiredLevel` when a business rule does it declaratively.
- Author web resources in the maker portal (no source control, no review, no testability).
- Put transactional logic in `OnSave` JS that races server-side writes — that belongs in a plug-in.

## Edge cases / when the rule does NOT apply

- **Logic beyond a rule's vocabulary** — anything needing a Web API call, a loop, multi-field/multi-record computation, or external integration is genuine JS work; a business rule can't reach it.
- **Cross-form / app-wide enforcement** — business rules are scoped (entity/all-forms or specific form); truly global invariants may belong server-side (plug-in / Dataverse business logic), not client JS *or* a form rule.
- **Complex conditional visibility** with many interdependent fields can outgrow a maintainable business rule; at that point a single well-tested JS handler may read more clearly than five overlapping rules.

## See also

- [`../skills/dataverse-web-resources/resources/ux-decision-guide.md`](../skills/dataverse-web-resources/resources/ux-decision-guide.md) — control/page decision tables (built-in over custom)
- [`../skills/dataverse-web-resources/resources/js-form-scripts.md`](../skills/dataverse-web-resources/resources/js-form-scripts.md) — when you do need JS
- [`./apps-form-onload-performance-budget.md`](./apps-form-onload-performance-budget.md)
- [`../knowledge/apps-decision-trees.md`](../knowledge/apps-decision-trees.md)
- [`../agents/model-driven-engineer.md`](../agents/model-driven-engineer.md) — "Business rules > JS for simple show/hide/required/lock logic"

## Provenance

From `model-driven-engineer.md` opinions ("Business rules > JS", "keep JS for genuine logic, web API calls, integrations", quick-view forms over web-resource HTML) and constitution §3 #7 (lowest-tier mechanism). The missing-null-check anti-pattern is the agent's own.

---

_Last reviewed: 2026-05-30 by `claude`_

# accessibility-engineering

A **Accessibility Engineering specialist team** for an accessibility lead, front-end engineer, or product owner accountable for WCAG conformance and an inclusive, usable product. It picks a WCAG conformance target and measures against it, treats automated tooling as a fraction of the picture, holds keyboard + screen-reader parity as the floor, reaches for semantic HTML before ARIA, and verifies contrast ratios instead of eyeballing them.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Conformance-target explicit, surface-flexible (web | native mobile | docs | kiosk | design-system).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `accessibility-lead`, `wcag-audit-analyst`, `assistive-tech-testing-specialist`, `inclusive-design-strategist` |
| **5 skills / commands** | `run-wcag-audit` · `prioritize-remediation` · `test-assistive-tech` · `verify-contrast` · `design-accessible-pattern` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · audit-worksheet.md · remediation-plan.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, user PII) in generated deliverables |
| **`scripts/accessibility_calc.py`** | stdlib calculator — `conformance` · `remediation` · `contrast` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install accessibility-engineering@ravenclaude
```

## Quickstart

> "We need to be WCAG-compliant — where do we even start?"

The `accessibility-lead` scopes the problem, routes to `wcag-audit-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a legal-compliance authority, a certification body, or a substitute for testing with disabled users. It does not render ADA / Section 508 / EN 301 549 legal determinations, issue conformance certifications, or store user PII. Legal and compliance determinations route to qualified counsel.

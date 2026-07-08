---
description: "Drive a new website end-to-end through the gold-standard-website-pipeline — nine fail-closed gates (discovery → IA → tokens → content → build → a11y → perf → SEO/AEO → pre-launch) against numeric WCAG 2.2 / Core Web Vitals / SEO bars, ending in one Go / Conditional / No-go verdict."
argument-hint: "[what you're building, e.g. 'a marketing site for X', 'a Shopify storefront', 'the web app's marketing shell'; omit to start from discovery]"
---

# Build a new website (gold-standard pipeline)

You are running `/web-design:new-website`. Drive the build the user described (`$ARGUMENTS`) through this plugin's **`gold-standard-website-pipeline`** — the ordered, fail-closed gate ladder that guarantees nothing ships without clearing a named gate against a checkable, standards-anchored bar. You are acting as the **Team Lead** (the orchestrator role in [`web-design/CLAUDE.md`](../CLAUDE.md)), delegating each gate to the owning specialist.

## When to use this

Any **new website or storefront build** (or a full re-platform / redesign), from greenfield discovery to launch sign-off — marketing site, web app, or ecommerce. For a pre-launch readiness sweep on existing work, enter the ladder at G6. **Not** for a single-discipline task ("this page is slow" → `/web-design:tune-core-web-vitals`; "audit our contrast" → the `accessibility-review` skill) — reach for the individual skill instead of spinning up a nine-gate pipeline.

## Run the pipeline

1. **Load the skill.** Read [`skills/gold-standard-website-pipeline/SKILL.md`](../skills/gold-standard-website-pipeline/SKILL.md) and follow it verbatim — it defines every gate's entry, dispatch (agent → skill), acceptance criteria, objective bar, fail-closed outcome, and artifact.
2. **Classify the archetype at G1** — exactly one of marketing / web-app / ecommerce — then walk the ladder. The archetype re-weights every later gate and selects the seams (web-app app-build → `frontend-engineering`; ecommerce economics → `ecommerce-dtc`; any auth/payments/PII surface → `ravenclaude-core` `security-reviewer`, mandatory).
3. **Respect the DAG** — run G3 (tokens) ∥ G4 (content), and G6 (a11y) ∥ G7 (perf) ∥ G8b (SEO technical) in parallel; don't false-serialize.
4. **Fail closed.** Each gate passes, loops back to its owner with named findings, or takes an explicit recorded waiver (owner + reason + condition) — never a silent skip. Terminate at G9 in exactly one **🟢 Go / 🟡 Conditional / 🔴 No-go**.

## Guardrails

- Every finding carries **severity (P0–P3) + named owner + target date** on the one shared scale (skill §5).
- Every acceptance criterion is **falsifiable** — a number or a pointable artifact, never "looks good."
- Volatile bars (WCAG 2.2 SC, CWV thresholds, Lighthouse bands) trace to the plugin's dated knowledge files; re-confirm at use.
- The terminal artifact is the plugin's [`templates/launch-checklist.md`](../templates/launch-checklist.md), federated-signed by each specialist.

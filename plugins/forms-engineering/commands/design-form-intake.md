---
description: "Design the intake behind a form so triage is deterministic: request taxonomy, the fields each type actually needs, routing rules, response clocks, the trust boundary, and a measurement contract with a named denominator. Produces a form spec, not a wireframe."
argument-hint: "[the form — what it collects, who acts on the submissions, and what is going wrong]"
---

# Design form intake

You are running `/forms-engineering:design-form-intake` for `$ARGUMENTS`. Work the way the plugin's constitution ([`../CLAUDE.md`](../CLAUDE.md)) requires: **the form is the entry point of a process**, and most form problems are process problems wearing a UI costume.

## Steps — traverse in order; do not skip ahead to the fields

1. **Start at the queue, not the form.** Ask what distinct kinds of work arrive here, who owns each, and what the receiving queue needs in order to act **without a reply**. If that cannot be answered, stop and get it answered — everything downstream is derived from it. [`../skills/form-intake-and-triage-design/SKILL.md`](../skills/form-intake-and-triage-design/SKILL.md) steps 1–2.
2. **Write the routing rules as a table.** One row per request type, with a predicate, a destination, when the clock starts and what stops it. A type with no row is a defect, not a default. Same skill, steps 3–4.
3. **Derive the fields from the routing decision.** Apply the use test (name what someone does with the answer) and the blocking test (would the queue actually stop and ask?). ⛔ Do **not** argue field count on conversion grounds here — that evidence is contested and lives with its counter-evidence in [`../../web-design/skills/conversion-design/SKILL.md`](../../web-design/skills/conversion-design/SKILL.md) §3.
4. **Walk the trust boundary.** Validation parity, the anti-abuse rung (start at the bottom of the ladder), the duplicate guard, webhook verification, PII minimisation: [`../skills/harden-a-form-submission/SKILL.md`](../skills/harden-a-form-submission/SKILL.md). Upload handling and challenge-widget mechanics are cited from [`../../ravenclaude-core/rules/security.md`](../../ravenclaude-core/rules/security.md) and [`../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md) — read them; do not restate them.
5. **Fix the denominator before instrumenting.** Write it in words a second analyst would implement identically, and state completion and abandonment as exact complements on it: [`../skills/form-telemetry-and-control/SKILL.md`](../skills/form-telemetry-and-control/SKILL.md).
6. **Check the three journey-level accessibility questions** a single-page audit cannot answer — redundant entry, the sign-in in front of the form, consistent help: [`../best-practices/wcag-2-2-added-five-criteria-that-land-on-forms.md`](../best-practices/wcag-2-2-added-five-criteria-that-land-on-forms.md). The audit and every criterion-level verdict belong to [`../../web-design/agents/accessibility-auditor.md`](../../web-design/agents/accessibility-auditor.md).
7. **Route what is not ours.** The binding security verdict → [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md), zero-exception. Any legal or retention determination → [`../../data-governance-privacy/CLAUDE.md`](../../data-governance-privacy/CLAUDE.md) and the owner. Charting and control limits → [`../../process-improvement/agents/lean-six-sigma-blackbelt.md`](../../process-improvement/agents/lean-six-sigma-blackbelt.md). Any inferential question → [`../../applied-statistics/CLAUDE.md`](../../applied-statistics/CLAUDE.md).

⛔ If step 7 sends you to the charting seam, carry this label with it:

> [NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not established practice. We found no published work joining web-form telemetry to SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that method and is not proof of universal absence.]

## Output

A populated [`../templates/form-spec.md`](../templates/form-spec.md), plus [`../templates/form-telemetry-plan.md`](../templates/form-telemetry-plan.md) if the form is being instrumented and [`../templates/form-platform-evaluation-matrix.md`](../templates/form-platform-evaluation-matrix.md) if a platform is being chosen.

Close with two lists, both explicit: **what is deliberately not defended**, and **what would change our mind** about the expected improvement.

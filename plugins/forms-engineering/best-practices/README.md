# Forms-engineering best-practice docs

Named, citable rules for the `forms-engineering` plugin. Each file is one rule — read, applied, and cited as a whole. The cross-marketplace index lives in [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md).

---

## ⛔ INHERITED RULES — read this table BEFORE writing a new rule here

This plugin is a **seam**, not a new owner. Most of what a form needs is already ruled on somewhere else in this marketplace, and a second home for someone else's rule is drift, not thoroughness. If your rule is in this table, it is already written. Link it; do not restate it.

| The rule you were about to write | Its actual owner |
| --- | --- |
| A placeholder is not a label | [`../../web-design/best-practices/form-labels-are-not-placeholders.md`](../../web-design/best-practices/form-labels-are-not-placeholders.md) |
| Validate on blur, not on keystroke; errors inline, not in a modal; name the fix | [`../../web-design/best-practices/ux-form-design-and-error-handling.md`](../../web-design/best-practices/ux-form-design-and-error-handling.md) |
| "Fewer fields always converts better" is folklore — and the counter-evidence | [`../../web-design/skills/conversion-design/SKILL.md`](../../web-design/skills/conversion-design/SKILL.md) §3 |
| Never mark required fields with a bare asterisk; mark required **or** optional, consistently | [`../../web-design/agents/ux-designer.md`](../../web-design/agents/ux-designer.md) |
| Forms are controlled and validated at the edge; one schema, two consumers | [`../../frontend-engineering/best-practices/forms-are-controlled-and-validated-at-the-edge.md`](../../frontend-engineering/best-practices/forms-are-controlled-and-validated-at-the-edge.md) |
| Visible focus, and target size (SC 2.4.11 / 2.5.8) | [`../../web-design/best-practices/a11y-visible-focus-and-target-size.md`](../../web-design/best-practices/a11y-visible-focus-and-target-size.md) |
| The full enumeration of the criteria new at A/AA in WCAG 2.2, as an audit checklist | [`../../web-design/skills/gold-standard-website-pipeline/SKILL.md`](../../web-design/skills/gold-standard-website-pipeline/SKILL.md) and [`../../web-design/templates/accessibility-audit-report.md`](../../web-design/templates/accessibility-audit-report.md) |
| Semantic HTML before ARIA | [`../../web-design/best-practices/reach-for-semantic-html-before-aria.md`](../../web-design/best-practices/reach-for-semantic-html-before-aria.md) |
| Upload hardening — untrusted filenames, traversal, type validation, size ceilings | [`../../ravenclaude-core/rules/security.md`](../../ravenclaude-core/rules/security.md) §File handling |
| Challenge-widget mechanics — token lifetime, replay, server-side verification, hostname scope | [`../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md) |
| Validate untrusted input at the boundary and encode at the output | [`../../ravenclaude-core/rules/security.md`](../../ravenclaude-core/rules/security.md) §Untrusted input |
| The binding security verdict on any form change | [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md) — zero-exception |

---

## Index

_Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
| --- | --- | --- |
| [`wcag-2-2-added-five-criteria-that-land-on-forms.md`](./wcag-2-2-added-five-criteria-that-land-on-forms.md) | Pattern — the criteria added in WCAG 2.2 land disproportionately on forms; check them against the **intake**, not only against the page. | Auditing or designing a multi-step intake; a form sits behind a sign-in; a form asks for something the user already gave you earlier in the same process. |
| [`a-honeypot-must-be-invisible-to-assistive-tech-and-to-autofill.md`](./a-honeypot-must-be-invisible-to-assistive-tech-and-to-autofill.md) | Absolute rule — a honeypot that a screen reader or a password manager can fill is a silent rejection mechanism aimed at real users. | Adding a honeypot; auditing one that already exists; a user reports that their submission "just disappeared". |
| [`every-public-form-post-needs-a-double-submit-guard.md`](./every-public-form-post-needs-a-double-submit-guard.md) | Absolute rule — anti-forgery is not anti-duplicate. A form that can be submitted twice will be. | Any public form POST; duplicate tickets, duplicate emails or duplicate charges are appearing; someone says "we have CSRF protection" as if that answered it. |
| [`name-the-denominator-before-you-quote-a-completion-rate.md`](./name-the-denominator-before-you-quote-a-completion-rate.md) | Absolute rule — a form rate without its denominator is not a number, and completion and abandonment must be complements on the same one. | Reporting any form rate; two dashboards disagree about the same form; before instrumenting. |
| [`do-not-put-three-sigma-limits-on-a-low-volume-form-series.md`](./do-not-put-three-sigma-limits-on-a-low-volume-form-series.md) | Absolute rule — below the stated minimum, or on a series with a weekday signature, control limits manufacture signals that are not there. | Anyone proposes charting a form metric; a weekly form number is being watched for "spikes". |
| [`degraded-bot-defense-must-be-loud.md`](./degraded-bot-defense-must-be-loud.md) | Absolute rule — failing open is defensible; failing open **quietly** is not. | Any anti-abuse layer with a secret, a quota, or a third-party dependency that can be unavailable. |
| [`clear-the-error-the-moment-it-is-fixed.md`](./clear-the-error-the-moment-it-is-fixed.md) | Pattern — an error message that outlives the error teaches the user their fix did not work. | Implementing or reviewing validation feedback; users report re-editing a field that already looks correct. |

---

## Where the SPC seam is labelled

One rule in this index — `do-not-put-three-sigma-limits-on-a-low-volume-form-series.md` — sits on a join this plugin invented rather than inherited, and it carries this marker for that reason:

> [NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not established practice. We found no published work joining web-form telemetry to SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that method and is not proof of universal absence.]

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — the plugin's constitution and the boundaries it keeps
- [`../knowledge/`](../knowledge/) — the fact banks these rules are grounded in
- [`../skills/`](../skills/) — the skills that apply them

# WCAG 2.2 added five criteria that land on forms — check them against the intake, not just the page

**Status:** Pattern — the criteria added in WCAG 2.2 land disproportionately on forms, and three of them are properties of the **process behind the form** rather than of its markup.
**Domain:** Forms engineering — accessibility delta
**Applies to:** `forms-engineering`

---

## ⛔ What this rule is NOT

It is **not** the enumeration of WCAG 2.2's new criteria, and it is not an audit checklist. Both already exist and are maintained elsewhere:

- The full new-at-A/AA set, as a verification checklist → [`../../web-design/skills/gold-standard-website-pipeline/SKILL.md`](../../web-design/skills/gold-standard-website-pipeline/SKILL.md) G6.
- Per-criterion audit rows → [`../../web-design/templates/accessibility-audit-report.md`](../../web-design/templates/accessibility-audit-report.md).
- SC 2.4.11 (focus not obscured) and SC 2.5.8 (target size) as design rules → [`../../web-design/best-practices/a11y-visible-focus-and-target-size.md`](../../web-design/best-practices/a11y-visible-focus-and-target-size.md).
- The audit itself, and every criterion-level verdict → [`../../web-design/agents/accessibility-auditor.md`](../../web-design/agents/accessibility-auditor.md).

⛔ **Correction that is worth stating once, because stale checklists still carry it:** SC 4.1.1 Parsing was **removed** in WCAG 2.2. A remediation ticket that cites it is citing a criterion that no longer exists.

## Why this rule exists

Three of the criteria added in WCAG 2.2 cannot be satisfied by looking at one page in a browser, because they are properties of a **journey**:

| Criterion | Level | The form question it actually asks |
| --- | --- | --- |
| **3.3.7 Redundant Entry** | A | Across this whole process, are we asking for anything the person already gave us — in an earlier step, in a previous form, in the account they are signed into? |
| **3.3.8 Accessible Authentication (Minimum)** | AA | If this form sits behind a sign-in, does that sign-in require a cognitive test — transcription, puzzle-solving, recall of something not on the screen — with no alternative? Does it allow paste and a password manager? |
| **3.2.6 Consistent Help** | A | Is the way to reach a human in the same place, in the same relative order, on every page of this intake? |

An auditor reviewing a single page passes all three by default, because all three are about what happens **between** pages. That is the gap this rule fills, and it is the only reason a forms plugin carries an accessibility rule at all.

## How to apply

1. **Walk the journey, not the page.** List every field the process asks for, in order, across all steps. Any value asked for twice is a 3.3.7 finding unless re-entry is essential (a password confirmation) or the answer genuinely changed.
2. **Prefer "already known" over "ask again".** Pre-fill, or offer selection of a previously entered value. 3.3.7's exception is narrow; "it was easier to ask again" is not in it.
3. **Check the sign-in in front of the form, not only the form.** A form that is itself accessible sitting behind an inaccessible sign-in is an inaccessible process. In particular: allow paste into every field of the sign-in, do not break password managers, and do not make a cognitive test the only route through.
4. **Put help in one place and leave it there.** A support link, a phone number or a live-chat entry point must appear in the same relative position on every step. Moving it between steps is the failure mode.
5. **Route the verdict.** The conformance judgement belongs to [`../../web-design/agents/accessibility-auditor.md`](../../web-design/agents/accessibility-auditor.md). Where the surface handles authentication, sessions or personal data, that auditor's routing rule is zero-exception and the review escalates to [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md).

## The anti-pattern

Treating a CAPTCHA as the sign-in's security layer and the accessibility question as somebody else's problem. A cognitive-function test with no alternative is precisely what 3.3.8 (AA) targets, and a challenge widget's own conformance level is disputed by its vendor's documentation — see [`../knowledge/form-anti-abuse.md`](../knowledge/form-anti-abuse.md) §4 before you rely on one.

## Source

WCAG 2.2 W3C Recommendation criterion numbers and levels as tabulated in this marketplace's existing audit template and pipeline checklist (both linked above), read 2026-08-17. This rule adds the intake-level reading of 3.3.7 / 3.3.8 / 3.2.6, not the criteria themselves.

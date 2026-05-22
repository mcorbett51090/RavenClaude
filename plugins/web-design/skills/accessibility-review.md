---
name: accessibility-review
description: WCAG 2.2-aligned accessibility audit — semantics, ARIA, keyboard navigation, color contrast, focus management, motion preferences. Severity guide + tooling notes. Used by `accessibility-auditor` (primary).
---

# Skill: accessibility-review

**Purpose:** WCAG 2.2-aligned accessibility audit. Used by `accessibility-auditor` (primary).

## When to use

- Pre-launch audit
- Annual / quarterly review cycle
- Post-redesign verification
- Complaint / remediation-driven review
- Onboarding a new component / feature
- Pre-procurement (vendor's product being evaluated)

## The 5 passes

Don't run all of them at once. Each pass uses different tooling and surfaces different issues.

### Pass 1 — Automated tooling (catches ~30-40% of issues)

- **axe-core** via Storybook addon, browser extension, or CLI
- **Lighthouse** a11y audit
- **Wave** browser extension
- **Pa11y** for CI integration

Output: a list of flagged issues. Each is a starting point, not a verdict — false positives exist.

### Pass 2 — Manual semantic + structural review

Inspect the DOM:
- Heading hierarchy (h1 → h2 → h3 with no skips)
- Landmark roles (`<main>`, `<nav>`, `<header>`, `<footer>`, `<aside>`)
- Form structure: every `<input>` has a `<label>`; required fields explicitly marked; error messages associated via `aria-describedby`
- List semantics (`<ul>` / `<ol>` / `<li>`)
- Table structure (`<th>` with `scope`; `<caption>` where appropriate)
- Image `alt` attributes (decorative `alt=""`, descriptive otherwise)

### Pass 3 — Keyboard navigation

With mouse / trackpad disconnected (or covered):
- Tab through every interactive element
- Check focus is **visible** (focus indicator not removed)
- Check tab order matches visual order
- Check skip-link appears on first tab + works
- Activate every CTA / link / form control with Enter / Space as appropriate
- Open modals → focus trapped inside → close returns focus to opener
- Open menus → arrow keys navigate as expected
- Escape closes overlays / popovers
- No keyboard traps (you can always escape every focusable region)

### Pass 4 — Screen-reader testing

At minimum: VoiceOver (macOS / iOS) + NVDA (Windows). Ideal: + JAWS, TalkBack.

For each high-stakes flow:
- Page title announced
- Landmarks navigable (rotor / hotkeys)
- Headings navigable
- Form fields announced with label + required + error
- Live region updates announced (or *not*, if not appropriate)
- Images: `alt` text read; decorative skipped
- Tables: headers associated with cells
- Modals: dialog announced, focus inside, content read, close announced

### Pass 5 — Color + contrast + motion

- Color contrast: every text foreground vs background, including hover / active states, gradients, image overlays
  - Body text ≥ 4.5:1
  - Large text (≥ 18pt regular or 14pt bold) ≥ 3:1
  - UI components and graphical objects ≥ 3:1
- Color used as the only signifier? (Red error, green success, blue link — all need an icon / underline / shape signifier too)
- Color-blind simulation (Sim Daltonism / equivalent)
- Animation respects `prefers-reduced-motion: reduce`
- No autoplay video / audio
- No content that flashes > 3 times / second

## WCAG 2.2 success criteria — by level

Default audit standard: **AA**. AAA where the product / audience warrants.

| Level A | Level AA (default floor) | Level AAA (stretch) |
|---|---|---|
| Non-text alt (1.1.1) | Contrast 4.5:1 (1.4.3) | Contrast 7:1 (1.4.6) |
| Keyboard-accessible (2.1.1) | Resize text 200% (1.4.4) | No-keyboard exceptions (2.1.3) |
| ... | Reflow (1.4.10) | Sign language for video (1.2.6) |
| ... | Target size 24px (2.5.8) | Target size 44px (2.5.5) |

(Not exhaustive; see WCAG 2.2 quick reference for the full list.)

## Findings report

| # | Severity | SC | Location | Issue | Remediation | Owner | Target date |
|---|---|---|---|---|---|---|---|
| 1 | P0 | 1.4.3 | Homepage hero | Body text 2.1:1 contrast on hero image overlay | Add 60% black tint to overlay | [name] | YYYY-MM-DD |

## Severity guide

- **P0** — failure blocks a primary user task (sign-up, checkout, search). Remediate before launch.
- **P1** — failure significantly degrades experience for affected users; remediate within current sprint.
- **P2** — failure on a non-critical surface; remediate within current quarter.
- **P3** — improvable but not a current AA failure; backlog.

## Anti-patterns the review catches

- "Score 100" cited as audit conclusion (only an axe / Lighthouse score)
- Audit performed only with sighted, mouse-using testers
- ARIA used to "fix" semantically wrong HTML (use the right element instead)
- "Aria-label" replacing visible text (causes accessible-name mismatch)
- Tabindex > 0 to fix order (fix the DOM)
- Skip link present but not visible on focus
- Form errors visible-only (not associated with the field for screen readers)
- Modal that traps focus but doesn't return on close

## See also

- Template: [`../templates/accessibility-audit-report.md`](../templates/accessibility-audit-report.md)
- Agent: [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md)

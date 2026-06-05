# Form Labels Are Not Placeholders

**Status:** Absolute rule
**Domain:** Web Design — Accessibility / forms
**Applies to:** `web-design`

---

## Why this exists

Placeholder text disappears the moment the user starts typing. A user who typed half their email address and glanced away cannot check what the field was asking for. Screen readers may not reliably expose placeholder text as the field's label; JAWS, NVDA, and VoiceOver have inconsistent placeholder-announcement behavior. `placeholder` has contrast issues by default (browsers render it at ~40% opacity, which fails WCAG 1.4.3). Using placeholder text as the only label violates WCAG 1.3.1 (Info and Relationships) and 2.4.6 (Headings and Labels). The anti-pattern "Forms without labels (placeholder-as-label is broken for a11y)" is in `CLAUDE.md` §4.

## How to apply

**The rule:**
Every form field must have a `<label>` element (or `aria-label` / `aria-labelledby` when a visible label is not possible) that persists while the user fills in the field. `placeholder` is supplementary context, never the label.

**Correct patterns:**

```html
<!-- Pattern 1: Visible label above the field (preferred) -->
<label for="email">Email address</label>
<input type="email" id="email" name="email"
       placeholder="you@example.com"
       aria-describedby="email-hint">
<p id="email-hint">We'll use this to send your receipt.</p>

<!-- Pattern 2: Floating label (label that animates above the field on focus) -->
<div class="field">
  <input type="text" id="name" placeholder=" ">  <!-- space keeps :placeholder-shown behavior -->
  <label for="name">Full name</label>
</div>

<!-- Pattern 3: When a visible label truly isn't possible (search bar in a header) -->
<input type="search" aria-label="Search the site" placeholder="Search…">
```

**Unacceptable pattern:**

```html
<!-- BAD: placeholder is the only label -->
<input type="email" placeholder="Email address">
```

**Checklist:**
- [ ] Every `<input>`, `<select>`, and `<textarea>` has a `<label>` (or `aria-label` / `aria-labelledby`).
- [ ] The `for` attribute on `<label>` matches the `id` on the input.
- [ ] Placeholder text (if used) supplements the label with a format hint or example value, never replaces it.
- [ ] Placeholder text meets WCAG 1.4.3 contrast (4.5:1 for normal text) — many browser defaults fail this.

**Do:**
- Use `aria-describedby` to attach hint text or error messages to the field as a separate element from the label.
- Test with a screen reader: tab to the field and confirm the label is announced correctly.
- Check that error messages also meet the non-color-only signifier rule (not just red text).

**Don't:**
- Use CSS `opacity` to style placeholder text below 0.4 — the default browser rendering already fails contrast.
- Treat `title` attribute as an accessible label — it has unreliable screen-reader exposure.
- Require the user to empty the field to see what was asked.

## Edge cases / when the rule does NOT apply

- **Single-field search forms in a prominent location** with surrounding visual context: an `aria-label` is sufficient; a visible `<label>` can be visually hidden with `.sr-only` when the form's purpose is unambiguous from context.
- **Date-picker or custom input components**: the accessible label lives on the outermost `role="group"` or on the trigger button via `aria-label`; the individual sub-inputs may have programmatic labels provided by the component library.

## See also

- [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md) — audits form labels as part of WCAG 1.3.1 and 2.4.6
- [`./ux-form-design-and-error-handling.md`](./ux-form-design-and-error-handling.md) — the broader form design rule this is a specific constraint of

## Provenance

Codifies the anti-pattern "Forms without labels (placeholder-as-label is broken for a11y)" from `CLAUDE.md` §4. WCAG 2.2 SC 1.3.1 Info and Relationships (A) and SC 2.4.6 Headings and Labels (AA). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_

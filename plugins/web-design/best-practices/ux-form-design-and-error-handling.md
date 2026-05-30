# Design forms for completion: label every field, validate on blur, name the fix

**Status:** Pattern — every form is a conversion surface. Each field is friction and needs a reason; validation and errors are designed, not defaulted.

**Domain:** UX / Forms

**Applies to:** `web-design`

---

## Why this exists

Forms are where conversion is won or lost, and most form failures are self-inflicted: placeholder-as-label (broken for a11y and disappears on focus), validation that fires on every keystroke (anxiety), errors in a modal that loses the user's place, a disabled submit button with no explanation of why. The team's standing positions — validate on blur not keystroke, inline errors not modal, the disabled-CTA pattern is dead, error messages name the fix not the problem — converge accessibility (every field labelled, errors associated via `aria-describedby`) with conversion (least friction to completion). A labelled, blur-validated, inline-error form is both more usable and more accessible than the default.

## How to apply

Pair every input with a real `<label>`, mark required/optional explicitly, validate on blur, and show the error inline next to the field with `aria-describedby` and a fix-oriented message.

```html
<div class="field">
  <label for="email">Email address</label>
  <input id="email" name="email" type="email" required autocomplete="email"
         aria-describedby="email-err" inputmode="email" />
  <!-- Error: associated to the field, names the FIX, not just "invalid" -->
  <p id="email-err" class="error" role="alert" hidden>Add the @ — e.g. name@company.com</p>
</div>
<button type="submit">Create account</button>   <!-- enabled; validate on click, show inline -->
```

```js
const email = document.querySelector("#email");
email.addEventListener("blur", () => {              // validate on blur, not on keystroke
  const err = document.querySelector("#email-err");
  const bad = email.value && !email.checkValidity();
  err.hidden = !bad;
});
```

**Do:**
- Pair every input with a `<label>` (not a placeholder); mark required *and* optional fields explicitly.
- Validate on blur; on submit, focus the first error and show all errors inline via `aria-describedby`.
- Write errors that name the fix ("Add the @") and use the right `type`/`inputmode`/`autocomplete` so mobile keyboards and autofill help.

**Don't:**
- Use a placeholder as the label (fails a11y, vanishes on input — flagged by both `ux-designer` and `accessibility-auditor`).
- Disable the submit button to "prevent" errors — show it enabled, validate on click, surface the error (disabled-CTA pattern is dead).
- Put errors in a modal or rely on color alone for the error state (pair with icon + text, SC 1.4.1).

## Edge cases / when the rule does NOT apply

- **Inherently destructive/irreversible submits** (delete account) warrant a confirmation step — but confirm with distinct CTA weight, not a disabled button.
- **Multi-step / progressive forms** validate per step on continue; "reverse-Christmas-tree" ordering (easy fields first) builds commitment before the hard fields.
- **Search-as-you-type** is the legitimate exception to "validate on blur" — but it's filtering, not validation, and shouldn't throw blocking errors per keystroke.

## See also

- [`./a11y-keyboard-operability-every-interactive-surface.md`](./a11y-keyboard-operability-every-interactive-surface.md) — forms must be fully keyboard-operable
- [`./content-microcopy-cta-and-errors.md`](./content-microcopy-cta-and-errors.md) — the wording of labels, CTAs, and error messages
- [`./reach-for-semantic-html-before-aria.md`](./reach-for-semantic-html-before-aria.md) — native form semantics first
- [`../agents/ux-designer.md`](../agents/ux-designer.md) (form/validation opinions), [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md) (label/error association)

## Provenance

Distilled from the `ux-designer` form opinions (validate on blur, inline not modal errors, disabled-CTA pattern is dead, reverse-Christmas-tree ordering), the `accessibility-auditor` form section (labels, `aria-describedby` error association, no placeholder-as-label, no color-only errors), and the `content-strategist` error-message stance ("name the fix, not the problem"). Retrieved 2026-05-28.

---

_Last reviewed: 2026-05-30 by `claude`_

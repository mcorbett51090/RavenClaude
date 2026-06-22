---
name: email-template-engineering
description: Build responsive HTML email templates that render across clients (Outlook/Word engine, Gmail clipping, Apple Mail dark mode) using MJML or table-based HTML, with a plain-text part, accessible markup, and the client-quirk guards. Reach for this when the user says "build a <type> email", "my email looks broken in Outlook", or "make this email responsive / dark-mode safe". Used by `email-sending-engineer` (primary).
---

# Skill: email-template-engineering

> **Invoked by:** `email-sending-engineer` (primary).
>
> **When to invoke:** "build a transactional/marketing email"; "it renders wrong in Outlook"; "make it responsive / dark-mode safe / accessible".
>
> **Output:** a template (MJML preferred) with the client-quirk guards, a plain-text alternative, and a cross-client test plan.

## Procedure

1. **Default to MJML, not hand-rolled tables.** MJML compiles to the bulletproof table/VML soup Outlook needs, so you author semantic components instead of maintaining nested tables. Drop to raw table HTML only when MJML can't express the layout.
2. **Design for the worst client first.** The constraints that drive the markup:
   - **Outlook (Windows)** renders with the **Word** engine — no flexbox/grid, ghost tables + VML for buttons/background images, conditional `<!--[if mso]>` comments.
   - **Gmail** clips messages over **~102KB** ("[Message clipped]") and strips `<style>` in some contexts — keep it small and inline the critical CSS.
   - **Dark mode** (Apple Mail, Outlook) can invert colors — set explicit backgrounds, use `color-scheme`/`meta name="color-scheme"`, and test logos on dark.
3. **Always ship `multipart/alternative` with a real plain-text part.** It's an accessibility and deliverability signal — not a fallback you skip.
4. **Make it accessible.** `lang` on the root, `role="presentation"` on layout tables, real `alt` text on images, sufficient contrast, a single clear `<h1>`-equivalent, and a meaningful preheader.
5. **Keep links on the sending domain.** Mismatched link domains and naked tracking redirectors hurt deliverability and trust.
6. **Test before you ship.** Render across clients (Litmus/Email on Acid or a manual matrix), check the dark-mode pass, and confirm the size is under the Gmail clip threshold.

## Worked example (MJML, transactional)

```xml
<mjml>
  <mj-head>
    <mj-attributes><mj-all font-family="Arial, sans-serif" /></mj-attributes>
    <mj-style>:root { color-scheme: light dark; }</mj-style>
  </mj-head>
  <mj-body background-color="#f4f4f4">
    <mj-section background-color="#ffffff">
      <mj-column>
        <mj-text font-size="20px" color="#111111">Reset your password</mj-text>
        <mj-text color="#333333">We received a request to reset your password.</mj-text>
        <mj-button background-color="#2563eb" href="https://example.com/reset?t=...">
          Reset password
        </mj-button>
        <mj-text font-size="12px" color="#888888">
          Didn't request this? Ignore this email.
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
```

Plus the **plain-text part**: `Reset your password: https://example.com/reset?t=...  — didn't request this? Ignore this email.`

## Guardrails

- Don't rely on flexbox/grid/`<div>` layout — Outlook's Word engine ignores them; use MJML or `role="presentation"` tables.
- Don't ship HTML-only — a missing plain-text part hurts both accessibility and deliverability.
- Watch the **102KB** Gmail clip limit; a single uncompressed inline image or bloated CSS will trip it.
- A dark-mode "fix" that hard-codes `#000` text can vanish on a dark background — set both background and text colors explicitly.

# Sanitize on input, escape on output

**Status:** Absolute rule
**Domain:** Security / data handling
**Applies to:** `wordpress-cms-engineering`

---

## Why this exists

Sanitizing and escaping protect different stages and are not interchangeable. **Sanitize** cleans untrusted data as it enters (a form, `$_GET`/`$_POST`, the REST API, an option). **Escape** makes data safe for its destination at the moment of output (HTML, attribute, URL, JS). Skip sanitizing and bad data lands in the DB; skip escaping and you ship XSS even from "clean" data.

## How to apply

```php
// Input — sanitize for the data's meaning
$email = sanitize_email( wp_unslash( $_POST['email'] ?? '' ) );
$title = sanitize_text_field( wp_unslash( $_POST['title'] ?? '' ) );

// Output — escape for the destination
echo esc_html( $title );
printf( '<a href="%s">%s</a>', esc_url( $link ), esc_html( $label ) );
echo wp_kses_post( $rich_content ); // when limited HTML is allowed
```

**Do:**
- Match the function to the context: `esc_html`, `esc_attr`, `esc_url`, `esc_js`, `wp_kses*`.
- `wp_unslash` then sanitize input from superglobals.
- Sanitize even "trusted" admin input.

**Don't:**
- Use escaping as a substitute for sanitizing (or vice-versa).
- Output a stored value without escaping because it "was sanitized on input."

## Edge cases / when the rule does NOT apply

Values that never reach output or SQL (e.g. a strict integer cast used only for a numeric comparison) still benefit from validation; for SQL specifically, use `$wpdb->prepare` (see below) rather than relying on sanitize alone.

## See also

- [`./use-wpdb-prepare-never-concatenate.md`](./use-wpdb-prepare-never-concatenate.md)
- [`./nonce-and-capability-checks-on-actions.md`](./nonce-and-capability-checks-on-actions.md)
- [`../skills/harden-and-secure-wordpress/SKILL.md`](../skills/harden-and-secure-wordpress/SKILL.md)

## Provenance

WordPress Plugin Handbook (Securing Input / Securing Output). Codifies `wordpress-developer` house opinion ("sanitize-in / escape-out is non-negotiable").

---

_Last reviewed: 2026-06-22 by `claude`_

# Never edit core — use child themes and hooks

**Status:** Absolute rule
**Domain:** Maintainability / upgrade safety
**Applies to:** `wordpress-cms-engineering`

---

## Why this exists

WordPress core, themes, and plugins all receive updates. Any change you make directly to core files, a parent theme, or another plugin's source is **silently destroyed on the next update** — and worse, it blocks you from updating (a security risk). Customizations must be expressed where they survive: a child theme (presentation) or your own plugin/hooks (behavior).

## How to apply

```php
// Child theme functions.php — extend, don't edit the parent
add_filter( 'excerpt_length', fn() => 30 );

// Change another plugin's behavior via its hooks, not its source
add_action( 'woocommerce_before_checkout_form', 'my_checkout_notice' );
```

**Do:**
- Override parent-theme templates by copying them into the child theme.
- Change behavior with `add_action`/`add_filter` at the provided hook.
- Keep behavior in your own plugin.

**Don't:**
- Edit files under `wp-admin/`, `wp-includes/`, a parent theme, or a third-party plugin.
- Use the dashboard file editor on production (disable it — `DISALLOW_FILE_EDIT`).

## Edge cases / when the rule does NOT apply

If a plugin offers **no** suitable hook, the right move is a PR/issue upstream or a wrapper — still not editing its source in place.

## See also

- [`./keep-business-logic-in-plugins-not-themes.md`](./keep-business-logic-in-plugins-not-themes.md)
- [`../skills/choose-wordpress-architecture/SKILL.md`](../skills/choose-wordpress-architecture/SKILL.md)

## Provenance

WordPress Theme Handbook (Child Themes) + Plugin Handbook (Hooks). Codifies `wordpress-architect` house opinion ("child theme or hooks, never edit core").

---

_Last reviewed: 2026-06-22 by `claude`_

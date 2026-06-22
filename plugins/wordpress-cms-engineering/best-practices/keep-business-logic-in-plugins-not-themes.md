# Keep business logic in plugins, not themes

**Status:** Absolute rule
**Domain:** Architecture / portability
**Applies to:** `wordpress-cms-engineering`

---

## Why this exists

The theme is presentation; it gets swapped during a redesign. If functionality — custom post types, taxonomies, integrations, shortcodes/blocks that carry data, business rules — lives in `functions.php`, swapping the theme **deletes the feature**. Putting that logic in a plugin (or a must-use plugin for always-on infrastructure) makes it portable and independent of the design.

## How to apply

```php
// In a PLUGIN, not the theme:
add_action( 'init', function () {
    register_post_type( 'event', array( /* ... */ ) );
    register_taxonomy( 'venue', 'event', array( /* ... */ ) );
} );

// The theme only renders it:
// single-event.php / an event block template
```

**Do:**
- Register CPTs/taxonomies, integrations, and business rules in a plugin.
- Use a must-use plugin (`mu-plugins/`) for infrastructure that must always run.
- Keep templates, styles, and markup in the theme.

**Don't:**
- Register data structures or integrations in `functions.php`.
- Make a feature's existence depend on which theme is active.

## Edge cases / when the rule does NOT apply

Purely presentational helpers (a template tag, a small display filter) legitimately live in the theme. The test is: "would losing this on a theme swap be a bug?" If yes → plugin.

## See also

- [`./never-edit-core-use-child-themes-and-hooks.md`](./never-edit-core-use-child-themes-and-hooks.md)
- [`../skills/choose-wordpress-architecture/SKILL.md`](../skills/choose-wordpress-architecture/SKILL.md)

## Provenance

WordPress Plugin Handbook (Plugin vs Theme / "Plugin Territory"). Codifies `wordpress-architect` house opinion ("business logic in a plugin, presentation in the theme").

---

_Last reviewed: 2026-06-22 by `claude`_

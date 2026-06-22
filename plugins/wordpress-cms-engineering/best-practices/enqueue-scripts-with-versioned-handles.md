# Enqueue scripts and styles with versioned handles

**Status:** Absolute rule
**Domain:** Asset loading / caching
**Applies to:** `wordpress-cms-engineering`

---

## Why this exists

Inlining `<script>`/`<link>` in template output breaks dependency management, double-loads assets, and gives you no cache-busting. `wp_enqueue_script`/`wp_enqueue_style` with an explicit **version** registers the asset once, resolves dependencies, and makes the version the cache-bust — bump it and browsers/CDNs fetch fresh.

## How to apply

```php
add_action( 'wp_enqueue_scripts', function () {
    wp_enqueue_style(
        'mytheme-main',                          // handle
        get_stylesheet_uri(),                    // src
        array(),                                 // deps
        '1.4.2'                                  // version — the cache-bust
    );
    wp_enqueue_script(
        'mytheme-app',
        get_theme_file_uri( 'build/app.js' ),
        array( 'wp-element' ),
        '1.4.2',
        true                                     // in footer
    );
} );
```

**Do:**
- Give every asset a unique handle and an explicit version (or `filemtime`/build hash).
- Enqueue in the proper hook (`wp_enqueue_scripts`, `admin_enqueue_scripts`, `enqueue_block_editor_assets`).
- Declare dependencies so order is correct.

**Don't:**
- Echo raw `<script>`/`<link>` tags in templates.
- Pass `null`/`false` as the version on assets that change (defeats cache-busting).

## Edge cases / when the rule does NOT apply

Block assets declared in `block.json` are enqueued by core from the manifest — keep their versions there. Third-party CDN scripts with their own immutable URLs already carry a version in the path.

## See also

- [`../skills/build-blocks-and-themes/SKILL.md`](../skills/build-blocks-and-themes/SKILL.md)
- [`./object-cache-for-expensive-queries.md`](./object-cache-for-expensive-queries.md)

## Provenance

WordPress Plugin/Theme Handbook (Including CSS & JavaScript). Codifies `wordpress-developer` house opinion ("enqueue with a versioned handle").

---

_Last reviewed: 2026-06-22 by `claude`_

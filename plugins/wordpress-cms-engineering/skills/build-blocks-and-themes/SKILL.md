---
name: build-blocks-and-themes
description: "Build Gutenberg blocks (block.json, the edit/save split, dynamic render_callback, attributes, supports) and themes (classic templates or block/FSE with theme.json), enqueuing assets with versioned handles the supported way."
---

# Build Blocks and Themes

Register the supported way; don't hand-roll editor markup or inline assets.

## A custom block
- **`block.json` is the source of truth** — name, `attributes`, `supports`, `editorScript`/`script`/`style`, `render` for dynamic blocks. Register with `register_block_type( __DIR__ . '/block.json' )`.
- **Static block:** an `edit` component (editor UI) + a `save` function (serialized markup).
- **Dynamic block:** omit/skip `save`; render server-side via `render_callback` / the `render` file so output reflects current data.
- **Attributes** are declared in `block.json` and read/written through the block props — never parsed by hand.

## A theme
- **Classic:** PHP template hierarchy (`index.php`, `single.php`, `page.php`, `functions.php`), `wp_enqueue_script`/`wp_enqueue_style` in a `wp_enqueue_scripts` hook.
- **Block/FSE:** `theme.json` defines settings + styles (the single design source of truth), `templates/` and `parts/` hold block markup, the Site Editor edits them.
- **Always a child theme** when extending a parent — see [`../../best-practices/never-edit-core-use-child-themes-and-hooks.md`](../../best-practices/never-edit-core-use-child-themes-and-hooks.md).

## Assets
- Enqueue with an explicit **version handle** (the version is your cache-bust) — see [`../../best-practices/enqueue-scripts-with-versioned-handles.md`](../../best-practices/enqueue-scripts-with-versioned-handles.md).
- Never inline `<script>`/`<link>` in template output.

## Anti-patterns
- Editor markup hand-written in PHP instead of an `edit` component / `block.json`.
- A dynamic data block built as a static `save` block (stale output).
- CSS overrides fighting the editor when a `theme.json` setting exists.

Volatile API/tooling specifics live (dated) in [`../../knowledge/wordpress-stack-2026.md`](../../knowledge/wordpress-stack-2026.md).

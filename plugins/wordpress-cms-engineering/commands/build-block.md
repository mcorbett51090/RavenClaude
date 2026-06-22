---
description: "Scaffold a custom Gutenberg block or plugin: block.json, edit/save (or render_callback), attributes, versioned assets, with sanitize-in/escape-out and nonce/capability checks."
argument-hint: "[the block/plugin feature + where it lives + the data]"
---

You are running `/wordpress-cms-engineering:build-block`. Use `wordpress-developer` + the `build-blocks-and-themes` and `extend-with-hooks-and-plugins` skills.

## Steps
1. Confirm where it lives (plugin/mu-plugin) and whether the block is static or dynamic.
2. Define `block.json` (attributes, supports), the edit/save or render_callback, and enqueue assets with versioned handles.
3. Apply security: sanitize-in/escape-out, `$wpdb->prepare` if any raw SQL, nonce + capability on mutations, `permission_callback` on REST routes.
4. Emit using `templates/block-plugin-scaffold-plan.md` + the Structured Output block.

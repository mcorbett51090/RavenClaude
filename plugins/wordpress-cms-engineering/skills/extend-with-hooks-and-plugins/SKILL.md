---
name: extend-with-hooks-and-plugins
description: "Extend WordPress through actions and filters at the right hook and priority, register custom post types/taxonomies and REST routes, and query with WP_Query (or a $wpdb->prepare'd query) — keeping logic in a plugin, never editing core."
---

# Extend with Hooks and Plugins

Change behavior by hooking in, not by forking.

## Hooks & filters
- **Actions** (`add_action`) do something at a point; **filters** (`add_filter`) transform a value and **must return it**.
- Pick the **right hook and priority** — earlier/later priority and `$accepted_args` matter. Confirm the hook's contract (when it fires, what it passes).
- Put hooks in a **plugin** (or a child theme for presentation), never in core or a parent theme — see [`../../best-practices/never-edit-core-use-child-themes-and-hooks.md`](../../best-practices/never-edit-core-use-child-themes-and-hooks.md).

## Registering things
- **CPTs / taxonomies:** `register_post_type` / `register_taxonomy` on `init` — these are data, so they belong in a plugin, not the theme ([`../../best-practices/keep-business-logic-in-plugins-not-themes.md`](../../best-practices/keep-business-logic-in-plugins-not-themes.md)).
- **REST routes:** `register_rest_route` with a `permission_callback` and sanitized `args` — never an open mutating endpoint.

## Querying
- **`WP_Query` / `get_posts` / the meta & options APIs first.** Bound results (no reflexive `posts_per_page = -1`); avoid N+1 on meta.
- **Drop to `$wpdb` only when the high-level API can't express it — and `prepare()` always** ([`../../best-practices/use-wpdb-prepare-never-concatenate.md`](../../best-practices/use-wpdb-prepare-never-concatenate.md)).

## Security on actions
- Every form/AJAX/REST mutation: **nonce + capability check** ([`../../best-practices/nonce-and-capability-checks-on-actions.md`](../../best-practices/nonce-and-capability-checks-on-actions.md)) and **sanitize-in/escape-out** ([`../../best-practices/sanitize-input-escape-output.md`](../../best-practices/sanitize-input-escape-output.md)).

## Anti-patterns
- A filter callback that forgets to `return $value`.
- Editing a plugin's source instead of hooking its provided actions/filters.
- A custom post type registered in the theme (disappears on theme swap).

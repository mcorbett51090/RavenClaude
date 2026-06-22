# Nonce and capability checks on every action

**Status:** Absolute rule
**Domain:** Security / authorization
**Applies to:** `wordpress-cms-engineering`

---

## Why this exists

A **nonce** proves the request was intended by the user (anti-CSRF); a **capability** check proves the user is allowed to do it (authorization). They answer different questions, so a mutating action needs **both**. A nonce without `current_user_can` lets any logged-in user perform an admin action; a capability check without a nonce leaves you open to CSRF.

## How to apply

```php
// Admin form / POST handler
if ( ! isset( $_POST['_wpnonce'] )
     || ! wp_verify_nonce( $_POST['_wpnonce'], 'save_settings' ) ) {
    wp_die( 'Invalid request' );
}
if ( ! current_user_can( 'manage_options' ) ) {
    wp_die( 'Insufficient permissions' );
}

// AJAX
check_ajax_referer( 'my_action', 'nonce' );
if ( ! current_user_can( 'edit_posts' ) ) { wp_send_json_error(); }

// REST route
register_rest_route( 'myplugin/v1', '/thing', array(
    'methods'             => 'POST',
    'callback'            => 'myplugin_create_thing',
    'permission_callback' => fn() => current_user_can( 'edit_posts' ),
) );
```

**Do:**
- Verify a nonce **and** check the right capability on every mutation.
- Always set a real `permission_callback` on REST routes.

**Don't:**
- Use `is_user_logged_in()` as a stand-in for a capability check.
- Ship a REST route with `permission_callback => '__return_true'` for a write.

## Edge cases / when the rule does NOT apply

Truly public, read-only, non-sensitive GET endpoints may use a permissive `permission_callback` — but still rate-limit and never expose private data.

## See also

- [`./sanitize-input-escape-output.md`](./sanitize-input-escape-output.md)
- [`../skills/harden-and-secure-wordpress/SKILL.md`](../skills/harden-and-secure-wordpress/SKILL.md)

## Provenance

WordPress Plugin Handbook (Nonces / Checking User Capabilities). Codifies `wordpress-developer` house opinion ("nonce + capability on every action").

---

_Last reviewed: 2026-06-22 by `claude`_

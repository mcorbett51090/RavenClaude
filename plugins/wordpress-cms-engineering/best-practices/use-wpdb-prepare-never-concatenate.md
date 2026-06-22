# Use `$wpdb->prepare` — never concatenate into SQL

**Status:** Absolute rule
**Domain:** Security / data handling
**Applies to:** `wordpress-cms-engineering`

---

## Why this exists

String-concatenating user input into a `$wpdb` query is the classic SQL-injection hole. `$wpdb->prepare` parameterizes values with placeholders so the database treats them as data, never as SQL. Sanitizing input does **not** make concatenation safe — only prepared statements do.

## How to apply

```php
// WRONG — injectable
$wpdb->query( "DELETE FROM {$wpdb->prefix}log WHERE user = '" . $_GET['u'] . "'" );

// RIGHT — prepared
$wpdb->query(
    $wpdb->prepare(
        "DELETE FROM {$wpdb->prefix}log WHERE user = %s AND id = %d",
        $user,
        $id
    )
);
```

**Do:**
- Reach for `WP_Query`/`get_posts`/the meta & options APIs first; drop to `$wpdb` only when they can't express the query.
- Use `%s`, `%d`, `%i` (identifiers) placeholders; pass values as `prepare` args.

**Don't:**
- Interpolate `$_GET`/`$_POST`/any variable directly into the SQL string.
- Assume `sanitize_*` makes raw concatenation safe — it doesn't for SQL.

## Edge cases / when the rule does NOT apply

Table names use `{$wpdb->prefix}` (not user input). Static, fully-literal SQL with no variables needs no `prepare`, but the moment a variable appears, prepare it.

## See also

- [`./sanitize-input-escape-output.md`](./sanitize-input-escape-output.md)
- [`../skills/extend-with-hooks-and-plugins/SKILL.md`](../skills/extend-with-hooks-and-plugins/SKILL.md)

## Provenance

WordPress Plugin Handbook (Data Validation / `wpdb`). Codifies `wordpress-developer` house opinion ("WP_Query before $wpdb; prepare always").

---

_Last reviewed: 2026-06-22 by `claude`_

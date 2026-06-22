# wordpress-cms-engineering — best-practice docs

Named, citable rules for the `wordpress-cms-engineering` plugin's specialists. Each file is **one rule**.

---

## Index

_8 rules across security, data handling, architecture, assets, performance, and operations._

| Doc | Status | Use when |
|---|---|---|
| [`sanitize-input-escape-output.md`](./sanitize-input-escape-output.md) | Absolute rule | Any untrusted data — sanitize on the way in, escape on the way out; the two are distinct. |
| [`use-wpdb-prepare-never-concatenate.md`](./use-wpdb-prepare-never-concatenate.md) | Absolute rule | Any dynamic value in a `$wpdb` query — `prepare()` with placeholders; never concatenate. |
| [`never-edit-core-use-child-themes-and-hooks.md`](./never-edit-core-use-child-themes-and-hooks.md) | Absolute rule | Customizing — child theme or hooks; never edit core, a parent theme, or another plugin. |
| [`keep-business-logic-in-plugins-not-themes.md`](./keep-business-logic-in-plugins-not-themes.md) | Absolute rule | CPTs, integrations, business rules — in a plugin so they survive a theme swap. |
| [`enqueue-scripts-with-versioned-handles.md`](./enqueue-scripts-with-versioned-handles.md) | Absolute rule | Loading CSS/JS — `wp_enqueue_*` with a version handle; never inline tags. |
| [`nonce-and-capability-checks-on-actions.md`](./nonce-and-capability-checks-on-actions.md) | Absolute rule | Any form/AJAX/REST mutation — verify a nonce **and** check a capability. |
| [`object-cache-for-expensive-queries.md`](./object-cache-for-expensive-queries.md) | Pattern | Repeated expensive queries — cache results in a persistent object cache. |
| [`stage-and-back-up-before-updates.md`](./stage-and-back-up-before-updates.md) | Absolute rule | Updating core/plugins/themes — snapshot, stage, smoke-test, then promote. |

---

Each rule cites its provenance and carries a `Last reviewed` date. Volatile tooling specifics live in [`../knowledge/wordpress-stack-2026.md`](../knowledge/wordpress-stack-2026.md).

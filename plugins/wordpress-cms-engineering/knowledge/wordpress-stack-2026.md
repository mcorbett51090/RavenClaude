# WordPress Stack — 2026 Capability Map

> Dated snapshot of the WordPress tooling the team recommends. **Versions and product capabilities are volatile — re-verify against the vendor/project before quoting to a client.** The durable reasoning lives in [`wordpress-decision-trees.md`](wordpress-decision-trees.md); this file is the freshness-anchored "what to reach for."
>
> _Last reviewed: 2026-06-22 by `claude`. Each row carries a confidence note; treat unmarked specifics as `[verify-at-use]`._

---

## Core & editing

| Thing | Use for | Note |
|---|---|---|
| **WordPress core** | The CMS + REST API + block editor | `[verify-at-use]` current major (the block editor / Site Editor evolve fast across releases) |
| **Block editor (Gutenberg)** | Content + (in FSE) full-site editing | Blocks via `block.json`; FSE via `theme.json` + `templates/`/`parts/` |
| **`theme.json`** | The design source of truth for block/FSE themes | Settings + styles; schema version moves with core — `[verify-at-use]` |
| **Classic themes** | Developer-owned PHP template hierarchy | Still fully supported; the right call for pixel-tight, non-FSE sites |

## Building blocks & plugins

| Tool | Use for | Note |
|---|---|---|
| **`@wordpress/create-block`** | Scaffold a block plugin (block.json + build) | Official scaffolder; pairs with `@wordpress/scripts` |
| **`@wordpress/scripts`** | Build/lint/test toolchain for blocks | Wraps webpack/Babel; gives you the versioned build artifacts |
| **WP-CLI** | Automation: installs, migrations, `search-replace`, cron | The serialization-safe way to do search-replace and DB ops |
| **Composer** | PHP dependency management for plugins | Common in larger/agency codebases |

## Headless / decoupled

| Tool | Use for | Note |
|---|---|---|
| **WP REST API** | Core JSON API for headless/decoupled front ends | Built in; pair endpoints with `permission_callback` |
| **WPGraphQL** | GraphQL layer over WordPress data | Popular for headless with React/Next |
| **Next.js / Astro** | The decoupled front-end app | Consumes REST/WPGraphQL; preview is the hard part |

## Performance & caching

| Tool | Use for | Note |
|---|---|---|
| **Redis / Memcached** | Persistent object cache backend | Highest-leverage dynamic-site win; needs a drop-in (e.g. an object-cache plugin) |
| **Page cache** | Full-page HTML for anonymous traffic | Host/CDN page cache, a caching plugin, or a reverse proxy (Varnish/NGINX) |
| **CDN** | Static asset + edge delivery | Pair with versioned asset handles for cache-busting |
| **Query Monitor** | Profiling slow queries/hooks in dev | Find the bottleneck before adding a layer |

## Security & ops

| Tool | Use for | Note |
|---|---|---|
| **`wp-config.php` constants** | `DISALLOW_FILE_EDIT`, salts/keys, HTTPS, debug | Hardening is configuration, not a plugin |
| **WP-CLI `core`/`plugin`/`theme update`** | Scriptable, stage-able updates | Stage + back up first; define rollback |
| **A reputable security plugin** | Login limiting, WAF, scanning | Layers on top of — never replaces — least privilege + current software |
| **Backup tooling (host snapshots / plugin / WP-CLI export)** | Snapshot DB + files before changes | Verify the restore, not just the backup |

## Standards / references

- **WordPress Coding Standards (WPCS)** + `phpcs` — code style and some security smells.
- **WordPress Plugin/Theme Handbooks** — the canonical APIs (hooks, `block.json`, `theme.json`, REST).
- **OWASP** — the underlying web-app security principles behind sanitize/escape/nonce.

---

_Re-verify any version, capability, or "current major" claim against the source before it reaches a client deliverable — these move every release._

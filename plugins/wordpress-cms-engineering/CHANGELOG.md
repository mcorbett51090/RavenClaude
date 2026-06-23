# Changelog — wordpress-cms-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-22

Initial release.

### Added

- **3 agents** — `wordpress-architect` (build-approach: classic vs block/FSE theme, plugin vs theme vs must-use, headless vs traditional, single vs multisite), `wordpress-developer` (block & theme dev with block.json, plugins, hooks/filters, WP_Query, the REST API, secure data handling), `wordpress-ops-engineer` (performance with page + object cache/Redis, security hardening, safe updates/backups/staging, migrations).
- **5 skills** — `choose-wordpress-architecture`, `build-blocks-and-themes`, `extend-with-hooks-and-plugins`, `harden-and-secure-wordpress`, `performance-and-caching`.
- **Knowledge bank** — `wordpress-decision-trees.md` (4 Mermaid trees: classic-vs-block/FSE theme, custom-plugin-vs-existing-vs-theme-functions, headless-vs-traditional, caching-layer-selection) and `wordpress-stack-2026.md` (dated capability map; re-verify versions before quoting).
- **8 best-practices** — sanitize-input/escape-output, $wpdb->prepare never concatenate, never edit core use child themes and hooks, enqueue scripts with versioned handles, nonce + capability checks on actions, object-cache for expensive queries, keep business logic in plugins not themes, stage and back up before updates.
- **3 templates** — wordpress-architecture-decision, block-plugin-scaffold-plan, security-performance-audit.
- **3 commands** — `/choose-wp-architecture`, `/build-block`, `/audit-wp-site`.
- **1 advisory hook** — `check-wordpress-anti-patterns.sh` (5 checks; `WPENG_STRICT=1` to block).

### Verify-at-use

- All product/library versions and capabilities in `wordpress-stack-2026.md` (WordPress core/block editor, theme.json schema, @wordpress/create-block & scripts, WP-CLI, WPGraphQL, Redis/Memcached, caching/security tooling) — volatile; re-confirm against the vendor/project before quoting.

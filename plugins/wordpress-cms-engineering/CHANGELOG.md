# Changelog — wordpress-cms-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.3] — 2026-09-14

### Changed

- `wordpress-developer`: `model: opus` → `model: sonnet`. The role is the implementation half of an architect/engineer pair — bounded, well-specified work against a design made upstream — which is the `sonnet` row of the marketplace's tier table (`ravenclaude-core/knowledge/model-tier-delegation.md`), and the tier the earlier app-craft plugins (backend / frontend / api / database) already give their implementers. Enforced going forward by the marketplace's model-tier-fit CI gate (`check-model-tier-fit.py`, Gate 288). No behaviour change beyond the model the agent runs on; the architect sibling stays on `opus`.

## [0.1.2] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

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

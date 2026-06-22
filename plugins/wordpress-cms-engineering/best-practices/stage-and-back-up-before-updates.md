# Stage and back up before updates

**Status:** Absolute rule
**Domain:** Operations / safe change
**Applies to:** `wordpress-cms-engineering`

---

## Why this exists

Core, plugin, and theme updates can break a live site — a deprecation, a conflict, a fatal error. Applying them directly to production with no snapshot is a gamble with someone else's data and uptime. The safe path is: **snapshot → apply on staging → smoke-test → promote**, with the rollback defined before the first update.

## How to apply

```shell
# 1. Snapshot (DB + files) — verify the backup restores, not just that it ran
wp db export backup-$(date +%F).sql
# (plus a files/uploads snapshot via host or tooling)

# 2. Apply on STAGING
wp core update && wp plugin update --all && wp theme update --all

# 3. Smoke-test staging (key pages, checkout, forms, admin)

# 4. Promote to production; keep the snapshot until verified
```

**Do:**
- Back up DB **and** files before any update; confirm the restore works.
- Apply on staging first and smoke-test.
- Define the rollback before you start.

**Don't:**
- Update plugins/core directly on production with no backup.
- Treat any core/plugin update as "too small" to stage on a site with real data.

## Edge cases / when the rule does NOT apply

A throwaway/dev environment doesn't need the full ritual. Critical security patches may need expedited rollout — still take a snapshot first, even if staging is abbreviated.

## See also

- [`../skills/harden-and-secure-wordpress/SKILL.md`](../skills/harden-and-secure-wordpress/SKILL.md)
- [`../skills/performance-and-caching/SKILL.md`](../skills/performance-and-caching/SKILL.md)

## Provenance

WordPress Hosting/Operations guidance + WP-CLI docs. Codifies `wordpress-ops-engineer` house opinion ("stage and back up before every update").

---

_Last reviewed: 2026-06-22 by `claude`_

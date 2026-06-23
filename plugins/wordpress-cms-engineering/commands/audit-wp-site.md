---
description: "Audit a WordPress site for security and performance: sanitize/escape/prepare/nonce gaps, hardening config, caching layers, expensive queries, and update posture."
argument-hint: "[site/code/config to audit]"
---

You are running `/wordpress-cms-engineering:audit-wp-site`. Use `wordpress-ops-engineer` (+ `wordpress-developer` for code-level findings) with the `harden-and-secure-wordpress` and `performance-and-caching` skills.

## Steps
1. Security pass: sanitize-in/escape-out, `$wpdb->prepare` (no concatenation), nonce + capability on actions, REST `permission_callback`, config hardening (file editor, HTTPS, roles, salts), update posture.
2. Performance pass: caching layers present (page + persistent object cache), unbounded/expensive queries, versioned assets — profile to find the real bottleneck.
3. Report findings by severity with concrete fixes; include a backup + staging + rollback plan for applying them.
4. Emit using `templates/security-performance-audit.md` + the Structured Output block.

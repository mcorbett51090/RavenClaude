---
name: harden-and-secure-wordpress
description: "Secure WordPress: sanitize-in/escape-out, $wpdb->prepare for all dynamic SQL, nonce + capability checks on every action, least-privilege roles, disable file editing, force HTTPS, secure wp-config, and keep core/plugins/themes current."
---

# Harden and Secure WordPress

Security is code discipline plus a smaller attack surface — not a plugin you bolt on.

## In the code
- **Sanitize on input, escape on output** — distinct steps, both required ([`../../best-practices/sanitize-input-escape-output.md`](../../best-practices/sanitize-input-escape-output.md)).
- **`$wpdb->prepare` for every dynamic value** — never string-concatenate SQL ([`../../best-practices/use-wpdb-prepare-never-concatenate.md`](../../best-practices/use-wpdb-prepare-never-concatenate.md)).
- **Nonce + `current_user_can`** on every form/AJAX/REST mutation ([`../../best-practices/nonce-and-capability-checks-on-actions.md`](../../best-practices/nonce-and-capability-checks-on-actions.md)).

## In the configuration
- **Least-privilege roles** — give editors/authors only what they need; one admin is not a default for everyone.
- **Disable the dashboard file editor** (`define( 'DISALLOW_FILE_EDIT', true )`).
- **Force HTTPS**, set strong unique salts/keys, protect `wp-config.php`, lock down `xmlrpc`/login (rate-limit, 2FA).
- **Keep everything current** — an out-of-date plugin is the most common entry point; pair with [`../../best-practices/stage-and-back-up-before-updates.md`](../../best-practices/stage-and-back-up-before-updates.md).

## Order by impact
1. Patch out-of-date core/plugins/themes (biggest real-world exposure).
2. Sanitize/escape/prepare/nonce gaps in custom code.
3. Least-privilege + disable file editing + force HTTPS.
4. Login/`xmlrpc` hardening, secrets rotation.

## Anti-patterns
- Treating a security plugin as a substitute for current software + least privilege.
- "Trusted" admin input left unsanitized (privilege escalation turns it hostile).
- Escaping instead of sanitizing (or vice-versa) — they protect different stages.

Traverse the relevant tree in [`../../knowledge/wordpress-decision-trees.md`](../../knowledge/wordpress-decision-trees.md); volatile specifics in [`../../knowledge/wordpress-stack-2026.md`](../../knowledge/wordpress-stack-2026.md).

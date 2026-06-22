# wordpress-cms-engineering

A RavenClaude plugin: a **WordPress / CMS engineering** specialist team for building, extending, and operating WordPress sites that are maintainable, secure, and fast — the build-approach decision, secure block/theme/plugin development, and operations (caching, hardening, safe updates, migrations).

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

## What it's for

Building a new WordPress site or extending an existing one and wanting it done right: the right theme model and where custom code lives, blocks and plugins that handle data securely (sanitize/escape, prepared SQL, nonces + capability checks), and an install that stays fast (layered caching) and safe to change (stage + back up before updates).

## Agents

| Agent | Use for |
|---|---|
| **wordpress-architect** | Build approach: classic vs block/FSE theme, plugin vs theme vs must-use, headless vs traditional, single vs multisite |
| **wordpress-developer** | Custom blocks (block.json), themes, plugins, hooks/filters, WP_Query, the REST API, secure data handling |
| **wordpress-ops-engineer** | Performance (page + object cache/Redis), security hardening, safe updates/backups/staging, migrations |

## What's inside

- **5 skills** — choose-wordpress-architecture, build-blocks-and-themes, extend-with-hooks-and-plugins, harden-and-secure-wordpress, performance-and-caching.
- **Knowledge bank** — [`wordpress-decision-trees.md`](knowledge/wordpress-decision-trees.md) (4 Mermaid trees: classic-vs-block/FSE, plugin-vs-theme-vs-mu, headless-vs-traditional, caching-layer-selection) + [`wordpress-stack-2026.md`](knowledge/wordpress-stack-2026.md) (dated capability map).
- **8 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **3 templates** — architecture decision, block/plugin scaffold plan, security & performance audit.
- **3 commands** — `/choose-wp-architecture`, `/build-block`, `/audit-wp-site`.
- **1 advisory hook** — `check-wordpress-anti-patterns.sh` ($wpdb concatenation, unsanitized superglobals, `eval(`/`extract(`, unversioned enqueue). `WPENG_STRICT=1` to block.

## Seams

Decoupled front-end app / app shell → [`frontend-engineering`](../frontend-engineering/) · non-WordPress backend / APIs → [`backend-engineering`](../backend-engineering/) · infra performance budget → [`performance-engineering`](../performance-engineering/) · formal security verdict → [`security-engineering`](../security-engineering/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install wordpress-cms-engineering@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for routing rules, house opinions, and the output contract.

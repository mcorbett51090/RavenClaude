# WordPress / CMS Engineering Plugin — Team Constitution

> Team constitution for the `wordpress-cms-engineering` Claude Code plugin. Three specialist agents — **wordpress-architect**, **wordpress-developer**, **wordpress-ops-engineer** — plus a decision-tree knowledge bank, skills, templates, best-practices, and an advisory hook, all aimed at building, extending, and operating WordPress sites that are **maintainable (no core edits, logic in plugins), secure (sanitize/escape, prepared SQL, nonce + capability), and fast (layered caching)**.
>
> **Orientation:** this file is **domain-specific** to WordPress/CMS engineering. For the domain-neutral team constitution every plugin inherits, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`wordpress-architect`](agents/wordpress-architect.md) | Build-approach: classic vs block/FSE theme, plugin vs theme vs mu-plugin, headless vs traditional, single vs multisite | "classic or block theme?"; "plugin or theme?"; "should we go headless?" |
| [`wordpress-developer`](agents/wordpress-developer.md) | Block & theme dev (block.json), plugins, hooks/filters, WP_Query, the REST API, secure data handling | "build a custom block"; "add a REST endpoint"; "fix this query/form securely" |
| [`wordpress-ops-engineer`](agents/wordpress-ops-engineer.md) | Performance (page + object cache/Redis), security hardening, safe updates/backups/staging, migrations | "the site is slow"; "lock it down"; "update without breaking prod"; "migrate to a new host" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. Per the marketplace house rule, this plugin ships specialist *doing*-agents and does not fork core's *review* roles (architect/security-reviewer).

---

## 2. Routing rules (Team Lead)

- **"How should we build this?" / "classic or block theme?" / "plugin or theme?" / "headless?"** → `wordpress-architect`.
- **"Build/fix this block, hook, query, or REST route" / "do it securely"** → `wordpress-developer`.
- **"It's slow" / "harden it" / "update safely" / "migrate it"** → `wordpress-ops-engineer`.
- **A decoupled front-end app (Next/Astro) consuming the API** → escalate to `frontend-engineering`.
- **A non-WordPress backend service / API this site integrates with** → `backend-engineering`.
- **Infra-level performance budget (CDN, host sizing, load tests)** → `performance-engineering`.
- **A formal security verdict / pen-test / threat model** → `security-engineering`.

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **Never edit core or a parent theme.** Customize through a child theme (presentation) or hooks/plugins (behavior).
2. **Business logic lives in a plugin, presentation in the theme.** The test is "does it survive a redesign?"
3. **Sanitize on input, escape on output.** Distinct steps; both required; even for "trusted" admin input.
4. **`$wpdb->prepare` always — never concatenate into SQL.** Prefer `WP_Query`/the high-level APIs first.
5. **Every action gets a nonce and a capability check.** A nonce proves intent; a capability proves authority.
6. **Enqueue with a versioned handle.** No inline `<script>`/`<link>`; the version is the cache-bust.
7. **Cache in layers.** A page cache for anonymous breadth; a persistent object cache (Redis/Memcached) for dynamic depth.
8. **Object-cache the expensive queries** rather than recomputing per request.
9. **Stage and back up before every update.** Define the rollback before the first update.
10. **Headless is a trade, not an upgrade** — name what you lose before decoupling.

---

## 4. Anti-patterns the agents flag (and the advisory hook detects)

The `hooks/` directory ships [`check-wordpress-anti-patterns.sh`](hooks/check-wordpress-anti-patterns.sh) — a PreToolUse Write/Edit/MultiEdit hook on `.php`/`.js`/`.jsx`/`.ts`/`.tsx`:

| Check | Triggers on | Rule (§3) |
|---|---|---|
| `$wpdb` query with string concatenation/interpolation (not `prepare`) | PHP/JS files | #4 |
| `$_GET`/`$_POST`/`$_REQUEST` used without a `sanitize_`/`esc_`/`wp_unslash` nearby | PHP/JS files | #3 |
| `eval(` | PHP/JS files | security |
| `extract(` | PHP/JS files | security |
| `wp_enqueue_script`/`style` without a version argument | PHP/JS files | #6 |

Advisory by default (`exit 0` with stderr warnings). Set `WPENG_STRICT=1` to make it blocking.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before an agent says "I can't" or commits to an approach, it must:

1. **Check the 5 skills** plus core skills.
2. **Traverse the decision tree** ([`knowledge/wordpress-decision-trees.md`](knowledge/wordpress-decision-trees.md)) before choosing a theme model, code placement, coupling, or caching layer — don't keyword-match.
3. **Try the next-easiest defensible method** before declaring blocked.
4. **Escalate with the mandatory phrasing** — what was tried, what was ruled out, the recommended next path.

Volatile tooling claims carry a retrieval date and are re-verified before quoting ([`knowledge/wordpress-stack-2026.md`](knowledge/wordpress-stack-2026.md)).

---

## 6. Output Contract

```
Task / question: <what was asked, in the decision tree's terms>
Decision: <theme model / code placement / coupling / query / caching + WHY>
Where it lives: <plugin / child theme / mu-plugin>
Security: <sanitize-in/escape-out; nonce + capability; $wpdb->prepare>
Performance: <caching layers; expensive queries; versioned assets>
Safe change: <stage + back up + rollback, if updating/migrating>
Seams handed off: <frontend-engineering / backend-engineering / performance-engineering / security-engineering>
```

**Plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)).

---

## 7. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/choose-wordpress-architecture/SKILL.md`](skills/choose-wordpress-architecture/SKILL.md) | `wordpress-architect` | Classic vs block/FSE; plugin vs theme vs mu-plugin; headless vs traditional; single vs multisite |
| [`skills/build-blocks-and-themes/SKILL.md`](skills/build-blocks-and-themes/SKILL.md) | `wordpress-developer` | Gutenberg blocks (block.json, edit/save, dynamic render) + classic/FSE themes; versioned assets |
| [`skills/extend-with-hooks-and-plugins/SKILL.md`](skills/extend-with-hooks-and-plugins/SKILL.md) | `wordpress-developer` | Actions/filters, CPTs/taxonomies, REST routes, WP_Query and prepared `$wpdb` |
| [`skills/harden-and-secure-wordpress/SKILL.md`](skills/harden-and-secure-wordpress/SKILL.md) | `wordpress-ops-engineer` | Sanitize/escape, prepare, nonce + capability, least privilege, hardening config |
| [`skills/performance-and-caching/SKILL.md`](skills/performance-and-caching/SKILL.md) | `wordpress-ops-engineer` | Layered caching: page cache + persistent object cache; cache expensive queries; profile first |

---

## 8. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/wordpress-decision-trees.md`](knowledge/wordpress-decision-trees.md) | Choosing a theme model, code placement, coupling, or caching layer — the Mermaid decision trees |
| [`knowledge/wordpress-stack-2026.md`](knowledge/wordpress-stack-2026.md) | Recommending a tool/library — the dated 2026 capability map (re-verify versions before quoting) |

---

## 9. Templates & commands

| Template | Use for |
|---|---|
| [`templates/wordpress-architecture-decision.md`](templates/wordpress-architecture-decision.md) | The build-approach decision record |
| [`templates/block-plugin-scaffold-plan.md`](templates/block-plugin-scaffold-plan.md) | Planning a custom block or plugin before scaffolding |
| [`templates/security-performance-audit.md`](templates/security-performance-audit.md) | A security + performance audit of an existing site |

Commands: [`/choose-wp-architecture`](commands/choose-wp-architecture.md), [`/build-block`](commands/build-block.md), [`/audit-wp-site`](commands/audit-wp-site.md).

---

## 10. Escalating out of the WordPress team

- **`frontend-engineering`** — a decoupled front-end app (Next/Astro) consuming the REST/GraphQL API; the app shell and build budget.
- **`backend-engineering`** — non-WordPress backend services / APIs this site integrates with.
- **`performance-engineering`** — infra-level performance budget (CDN, host sizing, load tests).
- **`security-engineering`** — a formal security verdict, pen-test, or threat model.
- **`database-engineering`** — non-WordPress database design / heavy query tuning beyond `$wpdb`/`WP_Query`.

---

## 11. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol: [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- The front-end seam: [`../frontend-engineering/CLAUDE.md`](../frontend-engineering/CLAUDE.md)
- The backend seam: [`../backend-engineering/CLAUDE.md`](../backend-engineering/CLAUDE.md)

---

## 12. Milestones

- **v0.1.0** — initial build-out: 3 agents (wordpress-architect, wordpress-developer, wordpress-ops-engineer), 5 skills, a decision-tree knowledge bank (4 Mermaid trees) + a dated 2026 stack map, 8 best-practices, 3 templates, 3 commands, and 1 advisory hook (5 checks). Seams to frontend-engineering, backend-engineering, performance-engineering, security-engineering.

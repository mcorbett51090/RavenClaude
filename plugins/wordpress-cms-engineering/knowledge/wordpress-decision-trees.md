# WordPress / CMS — Decision Trees

> Reference decision trees for the `wordpress-cms-engineering` team. Agents **traverse the relevant tree top-to-bottom before choosing** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> _Last reviewed: 2026-06-22 by `claude`. Principles are durable; specific product/library/version names live (dated) in [`wordpress-stack-2026.md`](wordpress-stack-2026.md)._

---

## Decision Tree: classic vs block/FSE theme?

```mermaid
flowchart TD
    A[Building a theme] --> B{Who composes the layouts?}
    B -- "non-developer editors, visually" --> C{Design needs pixel-tight<br/>developer control?}
    C -- no --> D[Block / FSE theme<br/>theme.json + Site Editor]
    C -- "yes, in places" --> E[Block/FSE + locked patterns<br/>or hybrid templates]
    B -- "developers only" --> F{Heavy use of the<br/>block editor for content?}
    F -- yes --> D
    F -- no --> G[Classic theme<br/>PHP template hierarchy]
```

**Rule:** the editing model picks the theme model. Editors composing layouts → block/FSE (`theme.json`, Site Editor); developer-owned, pixel-tight templates with no visual layout editing → classic. Don't pick block/FSE for a site no non-developer will edit, or classic for a site whose editors live in the block editor.

---

## Decision Tree: custom plugin vs existing plugin vs theme functions?

```mermaid
flowchart TD
    A[Where does this code go?] --> B{Is it presentation only?<br/>templates, styles, markup}
    B -- yes --> C[Theme / child theme]
    B -- no --> D{Does it carry data or behavior<br/>that must survive a redesign?}
    D -- yes --> E{Must it be always-on,<br/>non-deactivatable?}
    E -- yes --> F[Must-use plugin<br/>mu-plugins/]
    E -- no --> G{A trusted plugin<br/>already does this well?}
    G -- yes --> H[Use it; extend via its hooks]
    G -- no --> I[Custom plugin]
    D -- no --> C
```

**Rule:** presentation → theme; data/behavior that must survive a redesign → a plugin (must-use for always-on infrastructure). Prefer extending a solid existing plugin through its hooks over reinventing it; never put business logic (CPTs, integrations) in the theme.

---

## Decision Tree: headless/decoupled vs traditional?

```mermaid
flowchart TD
    A[Front-end approach] --> B{Does the front end need<br/>a dedicated JS app/framework?}
    B -- no --> C[Traditional<br/>theme renders PHP]
    B -- yes --> D{Can you give up the block editor's<br/>live preview + much of the plugin ecosystem?}
    D -- no --> E{Is a hybrid OK?<br/>traditional + islands/REST}
    E -- yes --> F[Traditional + REST/AJAX islands]
    E -- no --> C
    D -- yes --> G{One front end or many channels?}
    G -- "one web front end" --> H[Headless: REST or WPGraphQL<br/>+ Next/Astro]
    G -- "many channels (web/app/kiosk)" --> H
```

**Rule:** stay traditional unless the front end genuinely demands a JS framework or multi-channel delivery. Headless buys a modern front-end stack and clean separation; it costs the editor's live preview, much of the plugin ecosystem, and a second deployable. Name the trade before committing.

---

## Decision Tree: which caching layer(s)?

```mermaid
flowchart TD
    A[Site is slow] --> B{Profiled the bottleneck?}
    B -- no --> C[Profile first<br/>slow query log / profiler]
    B -- yes --> D{Mostly anonymous traffic?}
    D -- yes --> E[Add a full-page cache<br/>host/CDN/plugin/reverse proxy]
    D -- "logged-in / dynamic" --> F{Persistent object cache present?}
    F -- no --> G[Add Redis/Memcached<br/>object cache]
    F -- yes --> H{Specific expensive queries?}
    H -- yes --> I[Cache results in object cache<br/>wp_cache_* / transients]
    H -- no --> J[Tune queries / DB / assets;<br/>check object-cache hit rate]
```

**Rule:** measure before you cache. Anonymous breadth → a page cache; dynamic/logged-in depth → a persistent object cache (Redis/Memcached), then cache the expensive queries on top. The default (non-persistent) object cache doesn't survive the request — wire a real backend.

---

## See also

- [`wordpress-stack-2026.md`](wordpress-stack-2026.md) — dated tooling/library capability map (re-verify before quoting versions).
- Skills: [`../skills/choose-wordpress-architecture/SKILL.md`](../skills/choose-wordpress-architecture/SKILL.md), [`../skills/build-blocks-and-themes/SKILL.md`](../skills/build-blocks-and-themes/SKILL.md), [`../skills/extend-with-hooks-and-plugins/SKILL.md`](../skills/extend-with-hooks-and-plugins/SKILL.md), [`../skills/harden-and-secure-wordpress/SKILL.md`](../skills/harden-and-secure-wordpress/SKILL.md), [`../skills/performance-and-caching/SKILL.md`](../skills/performance-and-caching/SKILL.md).

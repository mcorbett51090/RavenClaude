# web-design — Claude Code plugin

> Web design & build specialist team for the RavenClaude marketplace.

Ships seven specialist agents (web architect, UX designer, visual designer, frontend implementer, content strategist, accessibility auditor, performance engineer), four playbook skills (design-system audit, accessibility review, Core Web Vitals tuning, technical SEO audit), eight working templates, and one advisory hook that flags common web anti-patterns on edits (oversized rasters, missing `alt`, hardcoded colors, missing meta tags, accidental `noindex`).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude         # prerequisite
/plugin install web-design@ravenclaude
/reload-plugins
```

Requires `ravenclaude-core@>=0.5.0`.

## What's inside

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 7 | [`agents/`](agents/) |
| Skills | 4 | [`skills/`](skills/) |
| Hooks | 1 (advisory) | [`hooks/`](hooks/) |
| Templates | 8 | [`templates/`](templates/) |

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution.

## When to dispatch

```text
"Build a new marketing site"          → web-architect → ux-designer → visual-designer → content-strategist → frontend-implementer → a11y + perf
"This page is slow"                   → performance-engineer
"Our site fails WCAG 2.2 AA"          → accessibility-auditor
"Brand refresh"                       → visual-designer
"Set up the design system"            → visual-designer → frontend-implementer
"Search ranking dropped"              → web-architect + content-strategist
"This form has poor conversion"       → ux-designer + content-strategist (microcopy)
```

## House opinions (short list)

1. Accessibility is a P1 design constraint.
2. Performance has a budget.
3. Mobile-first or it's not done.
4. Design tokens, not hardcoded values.
5. Semantic HTML before ARIA.
6. Content informs design.
7. No layout shift after first paint.
8. One CTA per screen (at most two).
9. Static-first.
10. SEO + a11y converge.
11. Third-party scripts are debt.
12. One source of truth per design decision.
13. Print and reduced-motion are not afterthoughts.

Full list (plus 20 anti-patterns) in [`CLAUDE.md`](CLAUDE.md) §3 / §4.

## Hooks

[`hooks/check-web-anti-patterns.sh`](hooks/check-web-anti-patterns.sh) is a PostToolUse hook. Advisory by default — flags oversized raster images, `<img>` missing `alt`, hardcoded hex colors outside `tokens.*` files, HTML pages missing `<title>` / `<meta description>`, and accidental `noindex` in production pages. Flip to blocking by changing `exit 0` to `exit 1`.

## License

MIT — same as the rest of the marketplace.

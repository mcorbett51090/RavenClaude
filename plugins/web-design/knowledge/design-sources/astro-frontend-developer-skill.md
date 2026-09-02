# astro-frontend-developer-skill
URL: https://github.com/danium/astro-frontend-developer-skill
Retrieved: 2026-09-01
Type: GitHub repo (Claude Code / Codex Agent Skill)

**Verification note:** WebSearch returned no hits for this repo (too new — created 2026-08-31 per
`api.github.com`). WebFetch's own summarizer produced plausible-looking but unverified content on
first pass, so ground truth here is `curl` against `api.github.com/repos/...` (HTTP 200, real repo
metadata) and `raw.githubusercontent.com/.../main/README.md` and
`.../main/astro-frontend-developer/SKILL.md` (HTTP 200, full raw text, 326 lines) — not WebFetch's
model-summarized output. Repo: public, 0 stars, topics `accessibility, agent-skills, astro,
claude-code, codex, frontend, performance, seo`. SKILL.md frontmatter: version 2.3, updated
2026-08-31, follows the open agentskills.io specification.

## What's valuable here

A tight, opinionated, single-file (326-line) Astro 7+ skill that encodes a **one-way rendering
decision hierarchy** (static HTML → on-demand → server island → client island, "every layer of
complexity must earn its place") plus a "claim discipline" section that explicitly forbids
overstating SEO/LLM-citation benefits from technical choices — a level of epistemic honesty most
frontend skill docs skip. It is dense with concrete, checkable rules rather than vague best-practice
prose, and pairs each rule with a verification step (build/browser/HTTP-response checks, not just
source-code review).

## Concrete extractable patterns/techniques

- **Rendering decision hierarchy is one-way and must be justified at each step down:** prerendered static HTML → on-demand rendering (only if request-time data required) → server islands with `server:defer` (isolated dynamic region) → client islands (only if browser interaction can't be expressed in HTML/CSS). Every hydrated island's directive choice must be documented with a reason in the code or change summary.
- **`client:*` directive selection is need-driven, not default:** `client:load` (immediately visible/interactive), `client:idle` (lower priority), `client:visible` (below-fold/expensive), `client:media` (conditional on media query), `client:only` (last resort, with fallback).
- **Content Layer API discipline:** define collections in `src/content.config.ts` with a required loader (`glob()`/`file()`), Zod schema unless data is intentionally unstructured, `render(entry)` from `astro:content` (not legacy `entry.render()`), explicit sort (collection order is NOT guaranteed), and draft/visibility/locale/access filters applied to *every* output surface (HTML, feed, Markdown mirror, sitemap alike).
- **Reject legacy Content Collections patterns** (`src/content/config.ts`, collection `type`, `entry.slug`) unless the installed Astro version requires them — an explicit anti-pattern, not just a preference.
- **Markdown vs MDX gate:** `.md` by default; `.mdx` only when an entry genuinely needs imported components/JSX/executable expressions. Keep page chrome/metadata/related-content logic in layouts, not duplicated per content file.
- **Image/asset rules:** local content images stay in `src/` (not `public/`) so Astro can process/optimize them; `public/` reserved for assets that must be copied unchanged or hit a fixed URL. `astro:assets` `<Image />`/`<Picture />` for transformations; always reserve intrinsic dimensions/aspect ratio to prevent CLS. Avoid `set:html` — when unavoidable, name the trust boundary explicitly in the code.
- **Agent-readable publishing pattern (dual representation from one source):** Markdown source → Astro Content Collection → canonical HTML, with sitemap/feed/structured-data/optional-Markdown-mirror all deriving from the *same filtered source* and the *same* draft/authorization/locale rules. The optional Markdown mirror uses either a deterministic route (`/article/index.md`) or HTTP content negotiation (`Accept: text/markdown` → `Content-Type: text/markdown; charset=utf-8`, `Vary: Accept`), and must be prevented from competing as a separate search result while staying retrievable for intended clients.
- **SEO/LLM claim discipline (unusually rigorous):** explicitly bans claiming Astro/Markdown-endpoints/`llms.txt`/structured-data/reduced-JS "improve rankings or guarantee LLM citations," and bans claiming JS "inherently prevents Google indexing" (Google renders JS) — frames the HTML-first default as an engineering choice (determinism, simplicity, non-JS-crawler compatibility), not an SEO hack. Real HTTP semantics required: `200` for valid pages, `404` for missing, `301`/`308` for permanent moves — never a soft-404 with `200`.
- **Verification matrix as a table**, mapping area → minimum evidence (correctness / types-content / interactivity / no-JS baseline / accessibility / responsive / performance / SEO / Markdown / deployment) — a "no-JS baseline" row (primary content and nav usable with JS disabled) that isn't explicit in RavenClaude's current gates.
- **Agent-ops details:** use managed background dev/preview servers (`astro dev --background`; Astro 7.2+ `astro preview --background`) with matching `status`/`logs`/`stop` subcommands and the dev health endpoint `/_astro/status`, instead of sleeping/guessing ports/duplicate servers — a concrete pattern for agent-driven verification loops.
- **Response contract** on every completed task: implemented outcome, architecture/rendering decisions, files changed, checks run + actual results, remaining risks/unverified deployment behavior — structurally similar to RavenClaude's own Output Contract but Astro-specific.
- **Anti-patterns list** (13 items) is concrete and mechanically checkable: hydrating a whole page/layout for one control, defaulting every island to `client:load`, MDX where plain Markdown suffices, optimizable content images placed in `public/`, content negotiation without `Vary: Accept`, claiming a Lighthouse/a11y/perf number without evidence, etc.

## Where this should feed into RavenClaude

- Recommend adding to: `plugins/web-design/skills/static-site-implementation/SKILL.md` — this skill already owns the Astro-static build path (§4 "Static-stack build mechanics") but doesn't currently name the one-way rendering hierarchy, the `client:*` directive selection table, or the Content Layer collection discipline (required loader, Zod schema, explicit sort, draft-filter-on-every-surface) at this level of specificity; the source's rules would tighten that section without contradicting it.
- Recommend adding to: `plugins/web-design/knowledge/answer-engine-optimization-2026.md` — the source's "claim discipline" section (never claim reduced-JS/Markdown-endpoints/llms.txt directly improve rankings or LLM citations; Google renders JS) is a sharper, more defensible framing than a looser AEO pitch, and reinforces this file's own hedged `llms.txt` position.
- Recommend adding to: `plugins/web-design/skills/static-site-implementation/SKILL.md` (agent-ops subsection, if one gets added) — the `astro dev --background` / `astro preview --background` + `status`/`logs`/`stop` + `/_astro/status` health-endpoint pattern is a concrete, Astro-specific instance of "verify before reporting completion" that RavenClaude's `gold-standard-website-pipeline` currently states only in the abstract (G5/G7 verification rows).
- Not recommended for `gold-standard-website-pipeline` or `fluent-react-implementation` directly — the source is Astro-only and framework-opinionated (explicitly rejects transplanting React/Next/SPA patterns into Astro), which is out of scope for those two files.

## Refresh recipe

- Re-check: on major Astro version bumps (the skill is pinned to "Astro 7+" and cites Astro 7's default Sätteri Markdown/MDX processor — a change here signals the skill itself will revise), or roughly semi-annually otherwise given the repo is brand-new (created 2026-08-31) and likely to iterate quickly in its first months.
- What to watch for: a new Astro major version changing the Content Layer API or rendering-directive set; changes to the skill's version/updated frontmatter fields (`SKILL.md` lines 5-6); new sections on Astro features not yet covered here (e.g. new hydration primitives); and whether the repo gains enough adoption/stars to be worth treating as a stronger signal than a single maintainer's opinion.

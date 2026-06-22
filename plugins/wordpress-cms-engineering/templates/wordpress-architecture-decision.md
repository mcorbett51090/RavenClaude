# WordPress Architecture Decision — <project>

> Output template for `wordpress-architect`. Fill every section; delete the guidance in italics.

## Context
- **Site does:** _what the site is for_
- **Who edits, and how:** _developers only / non-developer editors composing layouts_
- **Scale & traffic:** _content volume, anonymous vs logged-in mix_
- **Front-end needs:** _standard theme / a JS app / multi-channel_

## Decisions
- **Theme model:** _classic / block (FSE)_ — _why (tie to the editing model)_
- **Custom code placement:** _plugin / theme functions / must-use plugin_ — _why_
- **Coupling:** _traditional / headless (REST or WPGraphQL)_ — _what the trade costs_
- **Site count:** _single install / multisite_ — _why_

## Upgrade & maintainability plan
- **Child-theme boundary:** _what's overridden vs extended via hooks_
- **No core / parent-theme edits:** _confirmed_
- **Update/staging approach:** _named (see stage-and-back-up rule)_

## What we explicitly will NOT do
- _e.g. "no business logic in the theme", "no headless for the novelty"_

## Seams handed off
- _Blocks/themes/plugins/queries → wordpress-developer · caching/security/updates/migrations → wordpress-ops-engineer · decoupled front-end app → frontend-engineering_

---
_Plus the ravenclaude-core Structured Output block._

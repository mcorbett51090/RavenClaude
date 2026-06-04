---
description: "Choose the rendering strategy per route (CSR/SSR/SSG/ISR/RSC) and the server/client component split."
argument-hint: "[app: SEO needs, personalization, interactivity]"
---

You are running `/frontend-engineering:choose-rendering`. Use `frontend-architect` + the `rendering-strategy` skill.

## Steps
1. For each route, traverse the rendering tree (SEO, personalization, interactivity).
2. In RSC, default to server components; mark the interactive islands.
3. Name the trade per choice.
4. Emit (from `templates/rendering-decision.md`) + Structured Output block.

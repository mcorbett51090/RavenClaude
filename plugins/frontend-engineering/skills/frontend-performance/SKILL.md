---
name: frontend-performance
description: "Make a frontend fast to a budget: analyze and code-split the bundle by route, lazy-load heavy/below-the-fold, optimize images/fonts, minimize hydration (RSC/islands), kill render-blocking and request waterfalls, and tune the Core Web Vitals (LCP/INP/CLS) against field data."
---

# Frontend Performance

## Bundle budget
Analyze what you ship; **code-split by route**; lazy-load heavy/below-the-fold. A +200KB dep for one feature is a budget decision.

## Core Web Vitals
- **LCP**: prioritize the hero, preconnect, optimize the image/font.
- **INP**: free the main thread (split work, no heavy sync handlers).
- **CLS**: reserve space for media/ads.
Measure **field** data, not just lab.

## Hydration
RSC/islands: ship server components, hydrate only interactive leaves.

## Enforce
A bundle-size / Lighthouse **budget in CI** (with devops-cicd) so perf doesn't rot per-PR.

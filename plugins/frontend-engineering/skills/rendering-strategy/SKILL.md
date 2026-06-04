---
name: rendering-strategy
description: "Choose the rendering strategy per route: SSG/ISR for static content, SSR/RSC for personalized or SEO-critical pages, CSR for behind-login interactive shells; default to server components and hydrate only interactive islands to minimize shipped JavaScript."
---

# Rendering Strategy

## Per route, by need
| Route | Strategy |
|---|---|
| Static content, SEO | **SSG / ISR** |
| Personalized + SEO/first-paint | **SSR / RSC** |
| Behind-login, highly interactive | **CSR** is fine |

No single global mode fits every route.

## RSC default
Default to **server components**; pull in **client components** at interaction leaves. Hydrate only the islands -> minimal shipped JS.

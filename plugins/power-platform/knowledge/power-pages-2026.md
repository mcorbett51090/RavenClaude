# Power Pages in 2026 — capabilities + the "Power Pages vs custom web" decision

**Last reviewed:** 2026-05-28 · **Confidence:** high (first-party Microsoft Learn, retrieved 2026-05-28). Re-verify on the Researcher sweep.
**Owner:** `power-pages-engineer`. **Complements** the [`power-pages-permissions`](../skills/power-pages-permissions/SKILL.md) skill (the security layering). Bridges to `web-design` (the custom-React-site alternative) — see the decision below.

## What Power Pages is
A secure, enterprise low-code **SaaS** for **external-facing** business websites, **Dataverse-integrated**, Bootstrap-based responsive. The **design studio** has five workspaces: **Pages** (layout), **Styling** (themes), **Data** (Dataverse tables/forms/views), **Set up** (admin), **Security** (vulnerability checks). Pro-dev extensibility via **Liquid** templates, the **Power Pages Web API** (CRUD on Dataverse from the page), **PCF code components** (Web client), and **Copilot codegen** in VS Code + `pac` CLI.

## The 2026 headline: React SPA support (GA Jan 31 2026)
Power Pages now supports **single-page applications** — **bring your own React** (and other front-end frameworks), code-first, project structure your own, and **deploy directly into a Power Pages site**, integrating with **Dataverse + the Power Pages Web API** and inheriting the platform's **auth, security (table permissions), and hosting**. Tooling: `pac` CLI + VS Code. This is the key bridge: you can build a **custom React (and Fluent UI) front-end** but host it on Power Pages to get Dataverse data + Microsoft Entra/B2C-style auth + table-permission security **without** standing up your own backend/hosting.

## Decision Tree: Power Pages vs a custom React/Fluent site

```mermaid
flowchart TD
    A[External-facing site for a client] --> D{Dataverse-backed + needs row-level security on business data?}
    D -->|Yes, and want managed auth + hosting + security| PP{How custom is the UI/UX?}
    D -->|No — marketing/content/app, non-Dataverse data| CW[Custom React/Fluent site<br/>→ web-design + azure-cloud host]
    PP -->|Low-code, forms/lists over Dataverse| PPLC[Power Pages design studio<br/>pages + data workspace + Liquid]
    PP -->|Highly interactive / bespoke UX| PPSPA[Power Pages + React SPA (GA 2026)<br/>bring-your-own React/Fluent, hosted on Power Pages]
    CW --> WD[web-design builds it; azure-cloud / Static Web Apps hosts it; Entra External ID for CIAM]
```

**The seam (bridges PP ↔ web-design ↔ azure-cloud):**
- **Dataverse-backed external site + you want managed security/auth/hosting** → **Power Pages** (low-code design studio, or the **React SPA** path for bespoke UX). `power-pages-engineer` owns it; table-permission security via the `power-pages-permissions` skill.
- **Non-Dataverse marketing/product/app site, or you want full stack control** → a **custom React/Fluent site** → `web-design` builds it (see its design-system + Fluent knowledge), hosted on **`azure-cloud`** (Static Web Apps / Container Apps) with **Entra External ID** for CIAM.
- **The Fluent/React UI layer is the same craft** either way — a Power Pages React SPA and a standalone React/Fluent site share component/design-token work (see `web-design/knowledge/design-systems-and-component-architecture-2026.md`).

## Integration surface (why "external site in the Microsoft estate" lands here)
Dataverse (forms/views/data workspace), Power Apps (internal apps share the data), Power Automate (workflow/plug-ins), Power BI (embedded reports), **Copilot Studio** (embed a chatbot/agent — see [`copilot-agents-2026.md`](copilot-agents-2026.md)). Lifecycle: trial → convert to production within 7 days; ALM via solutions (`solution-alm-engineer`).

## House-opinion alignment
- **Security**: table permissions + web roles + auth layering (the `power-pages-permissions` skill); any auth/data-exfiltration design → `ravenclaude-core/security-reviewer` (mandatory).
- **Lowest-tier mechanism that does the job** (§3 #7): Power Pages design studio before a React SPA before a fully custom site — escalate only when the UX genuinely needs it.

## Sources (retrieved 2026-05-28)
[What is Power Pages](https://learn.microsoft.com/power-pages/introduction), [Power Pages capabilities](https://learn.microsoft.com/power-pages/capabilities), [Developer capabilities](https://learn.microsoft.com/power-pages/configure/developer-overview), [Build modern single-page applications (GA Jan 2026)](https://learn.microsoft.com/power-platform/release-plan/2025wave2/power-pages/build-modern-single-page-applications), [Code components in Power Pages](https://learn.microsoft.com/power-pages/configure/component-framework).

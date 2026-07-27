# Shopify App & Theme Engineering — Decision Trees

> Last reviewed: 2026-07-20. Confidence: **HIGH** for the durable platform architecture (app-type choice, Functions-over-scripts, embedded model, rate-limit cost model, review requirements as a category); **VERIFY-AT-USE** for every version-specific fact (current Admin API version, REST deprecation timeline, `checkout.liquid`/script-tag restriction dates, specific rate-limit numbers, exact App Store review checklist items). Shopify ships API versions quarterly — re-verify against current Shopify.dev docs before a commitment.

The agents traverse these before naming a build type or surface. Do not brand-match "headless" / "Functions" to a request a theme or a simpler path serves.

## 1. App type — who uses it, does it ship to the App Store?

```mermaid
flowchart TD
    A[New Shopify build] --> B{Who uses it?}
    B -->|"One merchant / internal"| C[Custom app<br/>no App Store review]
    B -->|"Many merchants / listed"| D[Public app<br/>App Store REVIEW applies]
    B -->|"Storefront-only, no backend"| E{Needs to inject UI<br/>into Shopify surfaces?}
    E -->|"Storefront look/behavior"| F[Theme change / OS 2.0 section]
    E -->|"Into admin or checkout"| G[App / theme extension]
    C --> H[Still needs OAuth,<br/>webhooks, GraphQL API]
    D --> H
```

**Rule:** custom for one merchant, public (with review) for many, theme/extension when no backend is needed. Public-app review is a design constraint, not an afterthought.

## 2. Customization surface — the current-generation choice

| Need                                   | Current-generation way              | The dead end (do NOT use)          |
| -------------------------------------- | ----------------------------------- | ---------------------------------- |
| Discount / shipping / payment / validation logic | **Shopify Functions**       | Script tags, off-platform hacks    |
| Checkout UI changes                    | **Checkout UI extensions**          | `checkout.liquid` (restricted)     |
| Embedded admin UI                      | **App Bridge + Polaris**            | Custom iframe chrome               |
| Reacting to store events               | **Webhooks** (HMAC-verified)        | Polling the API in a loop          |
| Reading/writing admin data             | **Admin GraphQL API**               | REST (legacy, deprecating)         |
| Large reads/writes                     | **Bulk operations**                 | Tight pagination loop (throttles)  |

**Rule:** build with the platform's grain. The "clever" bypass fails review and breaks on the next API version. (Deprecation dates: verify-at-use.)

## 3. Storefront — theme vs headless

```mermaid
flowchart TD
    A[Storefront work] --> B{Genuine need for custom<br/>framework / perf / omnichannel?}
    B -->|"No — standard storefront"| C[Online Store 2.0 theme<br/>Liquid, JSON templates, sections, app blocks<br/>merchant-editable, cheapest to maintain]
    B -->|"Yes — real requirement"| D[Hydrogen + Storefront API<br/>headless React on Oxygen]
    C --> E[Custom data → metafields / metaobjects]
    D --> F[Higher cost: build + hosting +<br/>maintenance + loses theme editor]
```

**Rule:** a theme is the default and is enough more often than teams admit. Headless (Hydrogen) is a real cost — earn it with a requirement, don't default to it for novelty.

## 4. Data model — metafields vs a shadow store

| Custom data                         | Store it as                      |
| ----------------------------------- | -------------------------------- |
| Extra fields on product/customer/order | **Metafields** (typed, namespaced) |
| Structured standalone objects       | **Metaobjects**                  |
| App-internal state / large volumes  | App's own DB (with a reason)     |

**Rule:** don't invent a shadow database for what metafields/metaobjects hold natively. Decide storefront exposure explicitly.

## 5. Commercial + safety envelope (public apps)

```mermaid
flowchart TD
    A[Public app] --> B[Charge via Billing API<br/>recurring / usage / one-time<br/>NEVER off-platform]
    A --> C[Auth: OAuth + session tokens<br/>not cookies for embedded]
    A --> D[Rate limits: GraphQL COST model<br/>budget + back-off + bulk ops]
    A --> E[Mandatory GDPR/data webhooks<br/>customers/redact, shop/redact,<br/>customers/data_request]
    A --> F[App Store review checklist<br/>VERIFY-AT-USE current requirements]
```

**Rule:** billing on-platform, session-token auth, rate limits as a design input, GDPR webhooks from day one. Missing any of these fails review. (Exact rules/limits: verify-at-use.)

## 6. Seams to adjacent plugins

| Boundary                                              | Owner                            |
| ----------------------------------------------------- | -------------------------------- |
| Merchandising / retention / lifecycle strategy the app serves | `ecommerce-dtc`          |
| Generic, non-Shopify payment scaffold                 | `web-commerce`                   |
| Off-Shopify payment rails / PSP integration           | `fintech-payments-engineering`   |
| Generic React component/state craft (inside Hydrogen) | `frontend-engineering`           |
| Pure visual / interaction / IA design                 | `web-design`                     |
| Deep OAuth / session / token hardening                | `auth-identity`                  |
| Review-readiness test pass                            | `qa-test-automation`             |

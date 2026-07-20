# Shopify App / Build Spec — <name>

> Produced by `shopify-app-architect`. Every volatile API-version/limit/review-rule fact carries a `[verify-at-use, retrieved <date>]` marker.

## 1. Who uses it & App Store exposure (fill FIRST)

- **Audience:** <one merchant | many merchants | storefront-only>
- **App type:** <custom | public (App Store review applies) | theme change / extension>
- **Merchant plan constraints:** <Plus? checkout extensibility available? verify-at-use>

## 2. Integration surface

| Surface                 | Used for                          |
| ----------------------- | --------------------------------- |
| Admin GraphQL API       | <setup / data ops>                |
| Webhooks                | <events reacted to>               |
| App Bridge + Polaris    | <embedded admin UI>               |
| Extensions              | <admin / checkout / theme app>    |

- **Embedded vs headless:** <embedded App Bridge | standalone | headless Hydrogen>

## 3. Customization path (current-generation only)

| Need                                | Built with                     | (Dead end avoided)     |
| ----------------------------------- | ------------------------------ | ---------------------- |
| Discount/shipping/payment/validation | Shopify Functions            | script tags            |
| Checkout UI                         | Checkout UI extension          | checkout.liquid        |

## 4. Data model

| Custom data          | Stored as                    | Storefront-exposed? |
| -------------------- | ---------------------------- | ------------------- |
| <tiers / notes>      | metafield / metaobject       | <yes/no>            |

## 5. Storefront (if any)

- **Choice:** <OS 2.0 theme (default) | Hydrogen + Storefront API>
- **Why (trade-off):** <flexibility/perf/maintenance — headless earned by ...>

## 6. Commercial + safety envelope

- **Billing:** Billing API — <recurring | usage | one-time>, disclosed
- **Auth:** OAuth + session tokens; scopes requested: <minimal list>
- **Rate limits:** GraphQL cost budget + back-off; **bulk operations** for <large ops>
- **Mandatory GDPR/data webhooks:** customers/data_request, customers/redact, shop/redact ✅
- **API version pinned:** <version> [verify-at-use]

## 7. App Store review checklist (verify exact items at use)

- [ ] Functionality & clean OAuth, minimal scopes
- [ ] GDPR/data webhooks working
- [ ] Performance (embedded load, no admin/theme slowdown)
- [ ] Security (HMAC webhooks, session tokens, no leaked secrets)
- [ ] Billing via Billing API
- [ ] Listing quality (description, screenshots, support)

## 8. Seams & flip conditions

| Boundary                     | Owner                          |
| ---------------------------- | ------------------------------ |
| Merchandising/retention      | `ecommerce-dtc`                |
| Off-Shopify payment rails    | `fintech-payments-engineering` |
| Generic React (in Hydrogen)  | `frontend-engineering`         |
| Visual / IA design           | `web-design`                   |

- **What would flip this design:** <1–2 facts>

## 9. Open questions / verify-at-use list

- [ ] <current Admin API version + REST deprecation window>
- [ ] <checkout extensibility availability on the target plan>
- [ ] <current App Store review requirement changes>

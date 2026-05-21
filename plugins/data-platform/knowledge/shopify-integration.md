# Shopify integration

> **Last reviewed:** 2026-05-21. Sources: Shopify developer docs ([shopify.dev/docs/api/admin-graphql/latest](https://shopify.dev/docs/api/admin-graphql/latest)), Fivetran/Airbyte Shopify connector docs. Refresh when: (a) Shopify GraphQL Admin API has a major version bump, (b) REST Admin API endpoints are removed (REST is legacy as of Oct 2024), or (c) Shopify Plus / B2B API changes affect the engagement.

## The critical 2025 transition: GraphQL-first

**REST Admin API is legacy as of October 1, 2024.**
**GraphQL Admin API is required for all new public apps since April 1, 2025.**

For new builds, use GraphQL exclusively. REST is supported for legacy apps but won't get new features.

## Auth

- **OAuth 2.0** for public / distribution apps
- **Custom app via Shopify Admin** for single-store integrations (simpler; uses an Admin-generated access token)

## API + Webhook architecture

| Surface | Use case |
|---|---|
| **GraphQL Admin API** | Bulk historical extraction; on-demand queries |
| **Webhooks (via GraphQL `webhookSubscriptionCreate`)** | Real-time order/inventory/customer events |
| **Storefront API** | Public storefront (not typically ELT-scope) |
| **Shopify Functions** | Serverless customization (not ELT-scope) |

## Webhook destinations (2025+)

Shopify webhooks can deliver to:
- **HTTPS endpoints** — classic webhook receiver
- **Google Pub/Sub** — direct cloud event-bus delivery
- **AWS EventBridge** — direct AWS event-bus delivery

The Pub/Sub and EventBridge options reduce the operational burden of building a webhook receiver.

## Rate limits

### REST Admin API (legacy)
- **40 req/sec bucket** (standard plan)
- **80 req/sec bucket** (Shopify Plus)

### GraphQL Admin API
- **Cost-based throttling**, not request-count
- Each query has a "cost" calculated from the fields requested
- **Standard plan: 50 cost points/sec restore rate; 1,000 cost-point bucket**
- **Shopify Plus: 100/sec restore; 2,000 bucket**
- GraphQL is more flexible — request only the fields needed = lower cost per query

## Connector availability

| Vendor | Shopify connector | Notes |
|---|---|---|
| Fivetran | ✅ | Uses GraphQL Admin API |
| Airbyte | ✅ | Uses GraphQL Admin API; OSS + Cloud |
| Hevo | ✅ | |
| Stitch | ✅ | Maintenance mode |

## Common entities

| Entity | Use case |
|---|---|
| `customers` | Customer dimension |
| `orders` | Order header fact |
| `order_line_items` | Order-line grain (revenue analytics) |
| `order_refunds` | Refund fact |
| `products` | Product dimension |
| `product_variants` | Variant dimension (SKU-level) |
| `inventory_items` / `inventory_levels` | Inventory fact (per location) |
| `locations` | Location dimension (multi-location merchants) |
| `transactions` | Payment-transaction fact (per order) |
| `discount_codes` / `price_rules` | Discount dimension |
| `fulfillments` | Fulfillment fact |
| `abandoned_checkouts` | Cart-abandonment fact (marketing analytics) |
| `metafields` | Custom-property extensions |

## Incremental sync

- **`updated_at`** is the canonical cursor for most entities
- **Orders use `updated_at`**; order line items inherit the parent order's timestamp
- **Bulk operations** — GraphQL `bulkOperationRunQuery` is the standard for backfilling large stores (async, results delivered to a webhook URL)

## dbt modeling — common marts

| Mart | Purpose |
|---|---|
| `dim_customer` | Customer dimension |
| `dim_product` | Product dimension |
| `dim_variant` | Variant dimension (SKU-level) |
| `dim_location` | Location dimension |
| `fact_order_lines` | Order-line revenue fact |
| `fact_inventory_snapshot` | Inventory levels by location, time |
| `fact_fulfillment` | Fulfillment performance |
| `mart_revenue_by_product` | Product-level revenue analytics |
| `mart_cohort_retention` | Customer-cohort retention (purchase recency) |
| `mart_inventory_turn` | Inventory-turn analysis |
| `mart_abandoned_cart_recovery` | Cart-abandonment funnel + recovery analysis |

## Common gotchas

1. **Order vs. order_line_items grain** — orders has the header (total, tax, shipping); line_items has the per-product detail. Most analytics happens at line_items.
2. **Multi-currency** — Shopify Plus supports multi-currency stores; `presentment_money` vs `shop_money` distinction matters
3. **Refunds are async** — refund object is created when the merchant processes the refund, which can be days after the order
4. **Cancelled vs refunded** — different states; both reduce revenue but in different ways
5. **B2B (wholesale) orders** have different shapes — `is_b2b_checkout` field; verify before unifying with retail
6. **Metafields are critical for custom apps** — clients often store engagement-relevant data in metafields; inventory needed in the connector config
7. **Inventory levels are per location** — multi-location merchants need `inventory_levels` not just `inventory_items`
8. **`Storefront` URL is the canonical product URL** — needed for marketing-attribution joins
9. **GraphQL cursor pagination** — `pageInfo.endCursor` for forward; reverse pagination supported but rarely needed
10. **Bulk operations are the only way to extract very-large stores** — single GraphQL queries can hit response-size limits

## PII / PHI considerations

- **Customer entity has PII** — name, email, phone, billing/shipping address
- **Shopify is PCI-DSS compliant** — payment data is not in the API (handled by Shopify Payments / third-party processor)
- **CCPA / GDPR** — Shopify has built-in customer-data-erasure tools; warehouse needs parallel delete

## Recommended sync configuration

- **Cadence:** daily for analytics; webhooks for real-time order events (inventory, fraud monitoring)
- **Backfill:** 24-36 months for cohort analysis; use bulk operations for very-large stores
- **Incremental cursor:** `updated_at` for most entities
- **Field selection:** GraphQL allows asking for only the fields needed — keeps cost-point usage low

## Refresh triggers

- Shopify GraphQL Admin API major version bump
- REST Admin API endpoints fully removed (eventual; currently legacy)
- Shopify Plus / B2B API changes
- New entity added to the engagement (subscriptions, gift cards, loyalty programs)
- Webhook event-type list changes

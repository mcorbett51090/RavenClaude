# Microsoft Graph best-practice docs

Named, citable rules for Microsoft Graph development — each file is one rule, grounded in this plugin's own [`knowledge/`](../knowledge/) decision trees and enforced by its [`agents/`](../agents/). Read and apply a doc as a whole.

For the cross-tool rule format and the marketplace-wide index, see [`docs/best-practices/_TEMPLATE.md`](../../../docs/best-practices/_TEMPLATE.md) and [`docs/best-practices/README.md`](../../../docs/best-practices/README.md). For the plugin's house opinions, see [`../CLAUDE.md`](../CLAUDE.md) §3-§4.

---

## Index

_18 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`api-advanced-query-consistencylevel.md`](./api-advanced-query-consistencylevel.md) | Primary diagnostic — when a directory-object `$count`/`$search`/`$orderby`/`ne`/`endsWith` query errors or silently ignores `$count`, the advanced-query headers are missing. | Graph fulfills queries from an index store. |
| [`api-batch-to-cut-round-trips.md`](./api-batch-to-cut-round-trips.md) | Pattern — when you have several independent Graph calls, `$batch` them; deviate only with a reason. | Every Graph call is a network round-trip with latency. |
| [`api-delta-for-what-changed.md`](./api-delta-for-what-changed.md) | Pattern — for "what changed since last time," use a delta query or change notification, not a periodic full read. | The most common cause of self-inflicted throttling is a cron job that re-reads an entire collection every hour to diff it client-side. |
| [`api-honor-throttling-and-retry-after.md`](./api-honor-throttling-and-retry-after.md) | Absolute rule — ignoring `Retry-After` or hammering after a `429` makes throttling worse, not better. | When a tenant or app exceeds a Graph service limit, Graph returns `429 Too Many Requests` (and sometimes `503`) with a `Retry-After` header telling you exactly … |
| [`api-page-to-exhaustion.md`](./api-page-to-exhaustion.md) | Absolute rule — code that reads `value` once and stops has shipped a silent sampling bug. | Many Graph collection reads are paged: `GET /users` returns 100 by default, and the response carries an `@odata.nextLink` whenever more data exists. |
| [`api-select-only-what-you-need.md`](./api-select-only-what-you-need.md) | Absolute rule — a collection `GET` with no `$select` is an over-fetch bug, not a style choice. | Every property you don't `$select` is network, serialization, and memory you pay for and throw away — and for `user`, `group`, and other resources deriving from… |
| [`api-use-the-sdk-not-raw-http-for-resilience.md`](./api-use-the-sdk-not-raw-http-for-resilience.md) | Pattern | Hand-rolled `HttpClient` calls to Graph re-implement — usually badly — the things the official SDKs already do correctly: paging, `429`/`Retry-After` retry with… |
| [`api-v1-not-beta-in-production.md`](./api-v1-not-beta-in-production.md) | Absolute rule — shipping `/beta` to production is a risk decision someone must own out loud, never a silent default. | Microsoft Graph exposes two endpoints: `v1.0` (generally available, supported, stable contract) and `beta` (preview — APIs and behaviors can change, and may nev… |
| [`auth-cache-tokens-with-msal-dont-mint-per-call.md`](./auth-cache-tokens-with-msal-dont-mint-per-call.md) | Pattern | Every token request is a round-trip to Entra and counts against authentication throttling. |
| [`auth-certificates-not-secrets-in-production.md`](./auth-certificates-not-secrets-in-production.md) | Absolute rule | A client secret is a long, guessable-if-leaked string that is trivially copy-pasted into logs, config files, source control, and notification URLs. |
| [`auth-pick-the-flow-by-client-type.md`](./auth-pick-the-flow-by-client-type.md) | Absolute rule — the client type dictates the flow; using the wrong one is a security or correctness defect (implicit and ROPC are off the menu). | The Microsoft identity platform exposes several OAuth 2.0 grants, and each maps to a specific client type and trust model. |
| [`identity-admin-consent-and-the-consent-framework.md`](./identity-admin-consent-and-the-consent-framework.md) | Pattern | Consent is where over-privilege becomes a rollout problem. |
| [`identity-delegated-vs-application-is-a-design-choice.md`](./identity-delegated-vs-application-is-a-design-choice.md) | Absolute rule — picking delegated or application by convenience instead of by "is there a signed-in user?" is a security defect, not a style preference. | Microsoft Graph supports exactly two access scenarios, and they have profoundly different blast radii. |
| [`identity-least-privilege-permission-selection.md`](./identity-least-privilege-permission-selection.md) | Absolute rule — a `.ReadWrite.All` / `.All` permission where a narrower one would do is an over-privilege defect, and the verdict is a security control. | Every permission an app holds is attack surface: a compromised app, a leaked credential, or a buggy code path can do everything its scopes allow. |
| [`identity-resource-scoped-over-tenant-wide.md`](./identity-resource-scoped-over-tenant-wide.md) | Pattern — strong default; deviate only with a written reason and a routed verdict. | A `Sites.ReadWrite.All` application permission grants write to **every** site collection in a tenant — thousands of sites — when the app may need exactly one. |
| [`notify-encrypt-rich-payloads-and-guard-the-key.md`](./notify-encrypt-rich-payloads-and-guard-the-key.md) | Absolute rule — the decryption private key for rich notifications is a security control; it lives in Key Vault and its handling escalates to security review, never decided silently. | A **rich** (resource-data) subscription (`includeResourceData: true`) ships the full changed resource *inside the notification*, encrypted, so you skip a follow… |
| [`notify-subscriptions-need-renewal-and-lifecycle-handling.md`](./notify-subscriptions-need-renewal-and-lifecycle-handling.md) | Absolute rule — a change-notification subscription with no renewal timer and no lifecycle handling is a silent outage, not a working integration. | A Microsoft Graph subscription has a **limited, resource-specific lifetime** set at creation via `expirationDateTime`. |
| [`notify-validate-the-handshake-and-verify-the-sender.md`](./notify-validate-the-handshake-and-verify-the-sender.md) | Absolute rule — a webhook endpoint that skips the validation handshake never receives a subscription, and one that processes notifications without verifying the sender is an injection surface. | Change notifications arrive at a **publicly accessible HTTPS endpoint** — which means anyone can POST to it. |

---

## See also

- [`../knowledge/`](../knowledge/) — the decision-tree bank these rules operationalize
- [`../CLAUDE.md`](../CLAUDE.md) — the Microsoft Graph team constitution
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — the marketplace-wide best-practice index and format

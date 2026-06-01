# Custom connector — get the auth scheme and policy right before you publish

**Status:** Pattern — strong default for custom-connector authoring; deviate only with a written reason.

**Domain:** Integration / custom connectors

**Applies to:** `power-platform`

---

## Why this exists

`flow-engineer` owns custom-connector authoring, but the rule layer had no guidance on the two decisions that actually go wrong: **which authentication scheme** the connector declares, and **whether/how to constrain it with a policy template**. Pick the wrong auth (an API key pasted into the connector definition instead of OAuth2, or a shared secret where Entra-delegated was right) and you ship a credential-leak or a connector that can't honor per-user access. Skip a policy template and the connector silently allows hosts/headers you didn't intend. These are authored once and then every maker in the tenant inherits the choice — so getting them right up front matters.

## How to apply

**Authentication scheme — match it to the API's real model:**

- API protected by Entra / Azure AD → **OAuth 2.0** (declare the auth URL, token URL, scope, and the registered app's client id; the secret is supplied at connection time, not baked into the definition).
- Third-party OAuth2 (GitHub, Salesforce, etc.) → OAuth 2.0 generic with that provider's endpoints.
- Simple key-based API → **API Key** auth (header or query), so the key is a connection credential the consumer supplies — **never** hard-code a key in the connector's OpenAPI definition or a flow action.
- No auth only for genuinely public, read-only endpoints.

**Policy templates — constrain what the connector can do:**

- Use `Set HTTP header` / `Route request` / `Set query parameter` policy templates to inject required headers or pin the backend host, rather than trusting every maker to set them.
- Don't let the connector accept an arbitrary base URL at call time if it should only ever talk to one backend.

**Certify vs keep tenant-private — a deliberate call:**

- **Tenant-private (custom connector)** is the default: it lives in your environment, is governed by your DLP, and needs no Microsoft review.
- **Certified (public)** is only worth it if you're an ISV publishing the connector for *other* tenants — it's a multi-week Microsoft certification process, not a deployment step.

**DLP:** a new custom connector must be **classified in your DLP policy** (Business / Non-Business / Blocked) — an unclassified connector defaults per tenant policy and can surprise you. See the DLP connector-classification tree.

**Do:** OAuth2/Entra for Entra-protected APIs; API key as a connection credential; policy templates to pin host/headers; classify the connector in DLP.

**Don't:** hard-code a secret/key in the connector definition or a flow; pursue certification for an internal-only connector; ship an unclassified connector.

## Edge cases / when the rule does NOT apply

If the need is a single one-off call to an Entra-protected API, a raw **HTTP action with Entra auth** may be simpler than authoring a whole custom connector (see the build-vs-HTTP-vs-certified tree). Certification mechanics and the exact policy-template catalog are platform-version-sensitive — `[verify-at-build]`. On-behalf-of / per-user delegated flows for a custom connector have additional setup beyond this rule.

## See also

- [`../knowledge/flow-decision-trees.md`](../knowledge/flow-decision-trees.md) — the custom-connector vs raw-HTTP vs certified decision tree
- [`../knowledge/alm-governance-decision-trees.md`](../knowledge/alm-governance-decision-trees.md) — DLP connector classification
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — owns custom connectors
- [Create a custom connector / connector authentication](https://learn.microsoft.com/connectors/custom-connectors/) — authoritative
- Any auth/secret verdict escalates to [`ravenclaude-core/security-reviewer`](../../ravenclaude-core/agents/security-reviewer.md)

## Provenance

Surfaced by the two-panel coverage audit (2026-06-01): `flow-engineer` owns custom-connector authoring per the plugin CLAUDE.md, but no best-practice covered the auth-scheme + policy-template + certify-vs-private decisions. Grounded in the Microsoft Learn custom-connector documentation. Certification process + policy-template catalog are `[verify-at-build]`.

---

_Last reviewed: 2026-06-01 by `claude`_

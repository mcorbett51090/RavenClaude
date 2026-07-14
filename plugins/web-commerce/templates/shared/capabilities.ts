/**
 * Advertised capabilities — the Saleor `actions`-style mechanism that lets a
 * provider track honestly declare what it can do, so callers never assume a
 * uniform capability set across Stripe / Square / Shopify (CLAUDE.md §2 #1).
 *
 * Shopify, for example, declares checkout: "hosted" and authorizeCapture:
 * false, because Shopify owns the checkout and there is no separate
 * server-side authorize/capture step to expose.
 */
export interface ProviderCapabilities {
  /** Where the payment UI lives on this track. */
  checkout: "hosted" | "embedded" | "both";
  /** Can the track authorize and capture as separate server-side steps? */
  authorizeCapture: boolean;
  /** Can the track issue refunds via API? */
  refunds: boolean;
  /** Who owns the catalog/inventory — the provider (Square/Shopify) or the app (Stripe)? */
  catalogSourceOfTruth: "provider" | "app";
  /** Is POS/inventory reconciliation supported on this track? */
  posReconciliation: boolean;
}

/**
 * Guard a capability-gated call. Throws a clear error rather than letting a
 * caller invoke, say, refund() on a provider that cannot refund via API.
 */
export function assertCapability(
  caps: ProviderCapabilities,
  key: "authorizeCapture" | "refunds" | "posReconciliation",
): void {
  if (caps[key] === false) {
    throw new Error(
      `This provider does not support "${key}". Check provider.capabilities ` +
        `before calling — capability sets differ across Stripe/Square/Shopify.`,
    );
  }
}

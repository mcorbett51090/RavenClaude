/**
 * ShopifyProvider — framework tier (Next.js / Astro). Implements the shared
 * PaymentProvider contract (../../shared/payment-provider.ts). Shopify is
 * CAPABILITY-INVERTED relative to Stripe/Square: it owns the catalog AND
 * checkout, and checkout is hosted-only, so this provider omits
 * authorize/capture/refund/cancel entirely rather than stub them
 * (CLAUDE.md §2 #1, ../../shared/capabilities.ts).
 */
import type {
  PaymentProvider,
  CreateCheckoutInput,
  WebhookRequest,
} from "../../shared/payment-provider";
import type { CheckoutHandle, CommerceEvent } from "../../shared/commerce-types";
import type { ProviderCapabilities } from "../../shared/capabilities";
import { createCart } from "./cart";
import type { ShopifyConfig, CartLineInput } from "./cart";
import { ShopifyWebhookVerifier, normalizeShopifyEvent } from "./webhook";

export const shopifyCapabilities: ProviderCapabilities = {
  checkout: "hosted",
  authorizeCapture: false,
  refunds: false,
  catalogSourceOfTruth: "provider",
  posReconciliation: false,
};

export interface ShopifyProviderConfig extends ShopifyConfig {
  /** Webhook signing secret from the Shopify admin. Server-side only — read from process.env. */
  webhookSecret: string;
}

/**
 * Construct from env in a Route Handler / server module:
 *
 *   const provider = new ShopifyProvider({
 *     storeDomain: process.env.SHOPIFY_STORE_DOMAIN!,
 *     storefrontToken: process.env.SHOPIFY_STOREFRONT_TOKEN!,
 *     webhookSecret: process.env.SHOPIFY_WEBHOOK_SECRET!,
 *   });
 */
export class ShopifyProvider implements PaymentProvider {
  readonly id = "shopify" as const;
  readonly capabilities = shopifyCapabilities;

  private readonly verifier: ShopifyWebhookVerifier;

  constructor(private readonly config: ShopifyProviderConfig) {
    this.verifier = new ShopifyWebhookVerifier(config.webhookSecret);
  }

  /**
   * Shopify prices from its own catalog (capabilities.catalogSourceOfTruth
   * === "provider") — it never accepts a caller-supplied price. The shared
   * `CreateCheckoutInput.lineItems` shape is {name, amount, quantity} to stay
   * provider-agnostic across Stripe/Square/Shopify; for Shopify, `name` MUST
   * carry the Shopify ProductVariant GID (e.g.
   * "gid://shopify/ProductVariant/123456789"). `amount` is accepted for
   * shape-compatibility but deliberately NOT sent to Shopify — it has no
   * effect on what the buyer is actually charged.
   */
  async createCheckout(input: CreateCheckoutInput): Promise<CheckoutHandle> {
    if (input.lineItems.length === 0) {
      throw new Error("createCheckout requires at least one line item");
    }
    const lines: CartLineInput[] = input.lineItems.map((item) => ({
      merchandiseId: item.name,
      quantity: item.quantity,
    }));
    const cart = await createCart(this.config, lines);
    return { mode: "hosted", url: cart.checkoutUrl };
  }

  async handleWebhook(req: WebhookRequest): Promise<CommerceEvent> {
    if (!this.verifier.verify(req.rawBody, req.headers)) {
      throw new Error("Shopify webhook signature verification failed");
    }
    return normalizeShopifyEvent(req.rawBody, req.headers);
  }

  // authorize/capture/refund/cancel are deliberately OMITTED, not stubbed:
  // capabilities.authorizeCapture === false and capabilities.refunds ===
  // false. Callers must check `provider.capabilities` (or use
  // `assertCapability` from ../../shared/capabilities.ts) before assuming
  // these exist.
}

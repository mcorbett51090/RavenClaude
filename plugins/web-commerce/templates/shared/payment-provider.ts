import type { CheckoutHandle, CommerceEvent, Money, PaymentStatus } from "./commerce-types";
import type { ProviderCapabilities } from "./capabilities";

export interface CreateCheckoutInput {
  lineItems: Array<{ name: string; amount: Money; quantity: number }>;
  /** Where a hosted checkout returns the buyer after payment. */
  returnUrl?: string;
  /** Caller-supplied idempotency key for the underlying create call (CLAUDE.md §2 #4). */
  idempotencyKey: string;
}

/**
 * The inbound webhook, as the transport hands it to us. The body is raw and
 * UNPARSED on purpose — parsing before signature verification would break the
 * signature (CLAUDE.md §3).
 */
export interface WebhookRequest {
  rawBody: string | Buffer;
  headers: Record<string, string | undefined>;
}

/**
 * The thin, three-provider-shared contract — the ONLY cross-provider
 * abstraction in this plugin (CLAUDE.md §2 #1). Modeled on Medusa's
 * AbstractPaymentProvider + Saleor's advertised capabilities. Catalog, cart,
 * inventory, and order operations are intentionally NOT here; they live in
 * each provider track.
 */
export interface PaymentProvider {
  readonly id: "stripe" | "square" | "shopify";
  readonly capabilities: ProviderCapabilities;

  /** Every provider can produce a way for the buyer to pay. */
  createCheckout(input: CreateCheckoutInput): Promise<CheckoutHandle>;

  /**
   * Verify (constant-time, before parsing) and normalize an inbound webhook.
   * Implementations MUST reject an unverified event rather than return it.
   */
  handleWebhook(req: WebhookRequest): Promise<CommerceEvent>;

  /**
   * Capability-gated lifecycle — present only when
   * capabilities.authorizeCapture / refunds is true (Stripe, Square). A
   * hosted-only provider (Shopify) omits these; guard with assertCapability.
   */
  authorize?(reference: string, idempotencyKey: string): Promise<PaymentStatus>;
  capture?(reference: string, idempotencyKey: string): Promise<PaymentStatus>;
  refund?(reference: string, amount: Money, idempotencyKey: string): Promise<PaymentStatus>;
  cancel?(reference: string, idempotencyKey: string): Promise<PaymentStatus>;
}

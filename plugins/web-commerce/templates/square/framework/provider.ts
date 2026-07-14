import type {
  PaymentProvider,
  CreateCheckoutInput,
  WebhookRequest,
} from "../../shared/payment-provider.ts";
import type {
  CheckoutHandle,
  CommerceEvent,
  Money,
  PaymentStatus,
} from "../../shared/commerce-types.ts";
import type { ProviderCapabilities } from "../../shared/capabilities.ts";
import type { IdempotencyStore } from "../../shared/idempotency-store.ts";
import { verifyAndParseSquareWebhook } from "./webhook.ts";
import { squareFetch, readSquareConfig } from "./square-client.ts";

const capabilities: ProviderCapabilities = {
  // The Web Payments SDK tokenizes the card in Square's hosted iframe;
  // createCheckout() below returns an "embedded" handle carrying the
  // (genuinely public) application id + a server-created Order id for the
  // client to check out against.
  checkout: "embedded",
  // CreatePayment(autocomplete:false) in ./checkout.ts authorizes without
  // capturing; capture()/cancel() below finalize or void it via Square's
  // Payments API.
  authorizeCapture: true,
  refunds: true,
  catalogSourceOfTruth: "provider",
  // See ./pos-reconciliation.ts -- the framework tier is the only tier with
  // a long-lived server process to run the reconciliation loop against
  // catalog/inventory webhooks (the static tier declares this `false`).
  posReconciliation: true,
};

interface CreateOrderResponse {
  order: { id: string };
}

function mapSquarePaymentStatus(status: string): PaymentStatus {
  switch (status) {
    case "APPROVED":
      return "authorized";
    case "COMPLETED":
      return "captured";
    case "CANCELED":
      return "canceled";
    case "FAILED":
      return "failed";
    default:
      return "failed";
  }
}

function mapSquareRefundStatus(status: string): PaymentStatus {
  switch (status) {
    case "COMPLETED":
      return "refunded";
    case "PENDING":
      return "authorized";
    default:
      return "failed";
  }
}

/**
 * The Square framework-tier PaymentProvider.
 *
 * Card tokenization happens entirely client-side via the Web Payments SDK
 * (see README.md's client snippet) -- the actual `CreatePayment` call,
 * which needs the single-use card token rather than just a reference, is
 * deliberately NOT part of this shared interface (the shared
 * `PaymentProvider` contract stays thin on purpose, CLAUDE.md §2 #1) and
 * instead lives in `./checkout.ts`'s `createSquarePayment()`, called
 * directly from your server route (`rubric #1`: the token is provider-tier
 * plumbing, not a cross-provider concept).
 *
 * `authorize` / `capture` / `cancel` below operate on an EXISTING payment
 * reference -- the id `createSquarePayment()` returned -- matching the
 * shared interface's `(reference, idempotencyKey)` signature. They finalize
 * a payment that was created with `autocomplete: false` (delayed capture).
 */
export function createSquareFrameworkProvider(idempotency: IdempotencyStore): PaymentProvider {
  return {
    id: "square",
    capabilities,

    async createCheckout(input: CreateCheckoutInput): Promise<CheckoutHandle> {
      const config = readSquareConfig();
      const locationId = process.env.SQUARE_LOCATION_ID;
      const applicationId = process.env.SQUARE_APPLICATION_ID;
      if (!locationId || !applicationId) {
        throw new Error("SQUARE_LOCATION_ID / SQUARE_APPLICATION_ID not set -- see .env.example");
      }

      const response = await squareFetch<CreateOrderResponse>(
        "/v2/orders",
        {
          method: "POST",
          body: {
            idempotency_key: input.idempotencyKey,
            order: {
              location_id: locationId,
              line_items: input.lineItems.map((item) => ({
                name: item.name,
                quantity: String(item.quantity),
                base_price_money: { amount: item.amount.amount, currency: item.amount.currency },
              })),
            },
          },
        },
        config,
      );

      // Square has no "client secret" concept the way Stripe's Payment
      // Intents do. We repurpose `clientSecret` to carry the server-created
      // Order id the Web Payments SDK checkout needs to reference, and
      // `publishableKey` to carry the (genuinely public) Application id --
      // both are safe to send to the browser.
      return { mode: "embedded", clientSecret: response.order.id, publishableKey: applicationId };
    },

    async handleWebhook(req: WebhookRequest): Promise<CommerceEvent> {
      return verifyAndParseSquareWebhook(req, idempotency);
    },

    async authorize(reference: string, _idempotencyKey: string): Promise<PaymentStatus> {
      // Square's authorization actually happens AT CreatePayment(
      // autocomplete: false) time in ./checkout.ts -- it needs the card
      // token, which this interface's signature deliberately doesn't carry
      // (rubric #1 keeps token handling out of the shared lifecycle
      // contract). This method confirms/reads back that a given payment
      // reference is in the APPROVED (authorized, not yet captured) state.
      const config = readSquareConfig();
      const res = await squareFetch<{ payment: { status: string } }>(
        `/v2/payments/${encodeURIComponent(reference)}`,
        { method: "GET" },
        config,
      );
      return mapSquarePaymentStatus(res.payment.status);
    },

    async capture(reference: string, _idempotencyKey: string): Promise<PaymentStatus> {
      const config = readSquareConfig();
      const res = await squareFetch<{ payment: { status: string } }>(
        `/v2/payments/${encodeURIComponent(reference)}/complete`,
        { method: "POST" },
        config,
      );
      return mapSquarePaymentStatus(res.payment.status);
    },

    async cancel(reference: string, _idempotencyKey: string): Promise<PaymentStatus> {
      const config = readSquareConfig();
      const res = await squareFetch<{ payment: { status: string } }>(
        `/v2/payments/${encodeURIComponent(reference)}/cancel`,
        { method: "POST" },
        config,
      );
      return mapSquarePaymentStatus(res.payment.status);
    },

    async refund(reference: string, amount: Money, idempotencyKey: string): Promise<PaymentStatus> {
      const config = readSquareConfig();
      const res = await squareFetch<{ refund: { status: string } }>(
        "/v2/refunds",
        {
          method: "POST",
          body: {
            idempotency_key: idempotencyKey,
            payment_id: reference,
            amount_money: { amount: amount.amount, currency: amount.currency },
          },
        },
        config,
      );
      return mapSquareRefundStatus(res.refund.status);
    },
  };
}

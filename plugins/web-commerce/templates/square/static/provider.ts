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
import { createSquareCheckoutLink } from "./checkout.ts";
import { verifyAndParseSquareWebhook } from "./webhook.ts";
import { squareFetch, readSquareConfig } from "./square-client.ts";

const capabilities: ProviderCapabilities = {
  checkout: "hosted",
  // Square's hosted Payment Links complete the charge in a single step --
  // there is no separate app-driven authorize/capture call on this tier.
  // Delayed capture needs the framework tier's CreatePayment(autocomplete:
  // false) flow -- see ../framework/provider.ts.
  // [unverified -- training knowledge that Payment Links has no delayed-
  // capture switch; re-check developer.squareup.com/docs/checkout-api-overview
  // before treating this as a permanent limitation.]
  authorizeCapture: false,
  refunds: true,
  catalogSourceOfTruth: "provider",
  // POS reconciliation ships on the framework tier only (see
  // ../framework/pos-reconciliation.ts) -- the static tier has no long-lived
  // server process to run the reconciliation loop from. Declaring it here
  // would be a dishonest capability (capabilities.ts's whole point is that
  // callers can trust what a track advertises).
  posReconciliation: false,
};

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
 * The Square static-tier PaymentProvider: hosted Checkout (Payment Links)
 * plus refunds. Card data never reaches this code -- the buyer pays on
 * Square's hosted page (rubric #1).
 */
export function createSquareStaticProvider(idempotency: IdempotencyStore): PaymentProvider {
  return {
    id: "square",
    capabilities,

    async createCheckout(input: CreateCheckoutInput): Promise<CheckoutHandle> {
      return createSquareCheckoutLink(input);
    },

    async handleWebhook(req: WebhookRequest): Promise<CommerceEvent> {
      return verifyAndParseSquareWebhook(req, idempotency);
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

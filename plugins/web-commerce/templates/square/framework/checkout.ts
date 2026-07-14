import type { Money } from "../../shared/commerce-types.ts";
import { squareFetch, readSquareConfig } from "./square-client.ts";

export interface CreatePaymentInput {
  /**
   * Single-use card token from the Web Payments SDK's `card.tokenize()`
   * call, made in the browser against Square's hosted iframe. Raw card
   * data never reaches this server (PCI SAQ-A, rubric #1).
   */
  sourceId: string;
  amount: Money;
  /** Required on every CreatePayment call -- Square de-dupes retried requests by this key (rubric #3). */
  idempotencyKey: string;
  /** The Square Order id from `provider.ts`'s `createCheckout()`, when this payment completes a pre-created order. */
  orderId?: string;
  /**
   * `false` (default here) leaves the payment APPROVED for a later
   * `capture()`/`cancel()` call (delayed capture); `true` completes the
   * charge immediately in this same call.
   */
  autocomplete?: boolean;
}

export interface SquarePaymentResult {
  paymentId: string;
  /** Square's raw status string -- APPROVED | COMPLETED | FAILED | CANCELED. */
  status: string;
}

interface CreatePaymentResponse {
  payment: { id: string; status: string };
}

/**
 * Complete a Web Payments SDK checkout, server-side. This is the only place
 * in the framework tier where the single-use card token is handled --
 * it is received once, forwarded once to Square, and never logged or
 * persisted (rubric #1, #4).
 */
export async function createSquarePayment(input: CreatePaymentInput): Promise<SquarePaymentResult> {
  const config = readSquareConfig();
  const locationId = process.env.SQUARE_LOCATION_ID;
  if (!locationId) {
    throw new Error("SQUARE_LOCATION_ID is not set -- see .env.example");
  }

  const response = await squareFetch<CreatePaymentResponse>(
    "/v2/payments",
    {
      method: "POST",
      body: {
        source_id: input.sourceId,
        idempotency_key: input.idempotencyKey,
        amount_money: { amount: input.amount.amount, currency: input.amount.currency },
        location_id: locationId,
        order_id: input.orderId,
        autocomplete: input.autocomplete ?? false,
      },
    },
    config,
  );

  return { paymentId: response.payment.id, status: response.payment.status };
}

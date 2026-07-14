import type { CreateCheckoutInput } from "../../shared/payment-provider.ts";
import type { CheckoutHandle } from "../../shared/commerce-types.ts";
import { squareFetch, readSquareConfig } from "./square-client.ts";

interface CreatePaymentLinkResponse {
  payment_link: { id: string; url: string; order_id: string };
}

/**
 * Build a Square hosted Checkout (Payment Link, `square.link/...`) for the
 * static tier. No card field, checkout form, or payment logic runs on this
 * site's own origin -- the buyer completes the purchase entirely on
 * Square's hosted page (PCI SAQ-A; rubric #1).
 */
export async function createSquareCheckoutLink(
  input: CreateCheckoutInput,
): Promise<CheckoutHandle> {
  const config = readSquareConfig();
  const locationId = process.env.SQUARE_LOCATION_ID;
  if (!locationId) {
    throw new Error("SQUARE_LOCATION_ID is not set -- see .env.example");
  }

  const body = {
    idempotency_key: input.idempotencyKey,
    order: {
      location_id: locationId,
      line_items: input.lineItems.map((item) => ({
        name: item.name,
        quantity: String(item.quantity),
        base_price_money: { amount: item.amount.amount, currency: item.amount.currency },
      })),
    },
    checkout_options: input.returnUrl ? { redirect_url: input.returnUrl } : undefined,
  };

  const response = await squareFetch<CreatePaymentLinkResponse>(
    "/v2/online-checkout/payment-links",
    { method: "POST", body },
    config,
  );

  return { mode: "hosted", url: response.payment_link.url };
}

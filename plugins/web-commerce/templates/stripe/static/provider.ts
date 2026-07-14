/**
 * Stripe — STATIC tier PaymentProvider.
 *
 * Hosted checkout via Stripe Payment Links (https://docs.stripe.com/payment-links,
 * https://docs.stripe.com/api/payment_links, 2026-07-13) — the fit for a
 * literally-static site because a Payment Link needs no per-request server
 * call: it is a durable, reusable URL you generate once (see checkout.ts)
 * and drop into a plain <a href> on the page. Card data is entered entirely
 * on Stripe's hosted page (PCI SAQ-A) — this module never receives a PAN.
 *
 * Capabilities declared honestly per ../../shared/capabilities:
 *   - checkout: "hosted"        — Payment Links are Stripe-hosted, full stop.
 *   - authorizeCapture: true    — see the capture_method note below.
 *   - refunds: true             — via the Refunds API.
 *   - catalogSourceOfTruth: "app" — Stripe has no real catalog; this track
 *     creates an ad-hoc Price + Product on Stripe for each checkout from the
 *     caller-supplied line items (../../shared/commerce-types Money), rather
 *     than requiring the caller to pre-create Stripe Price objects.
 *   - posReconciliation: false — Stripe has no POS ledger to reconcile against.
 *
 * Manual-capture default: createCheckout() sets `payment_intent_data:
 * { capture_method: "manual" }`, so a completed checkout lands in
 * "requires_capture" (our "authorized") rather than auto-capturing. This
 * makes authorize()/capture() below meaningful — e.g. "authorize on order
 * placement, capture on fulfillment." A merchant that wants immediate
 * capture can delete that one field.
 */

import Stripe from "stripe";
import type {
  CreateCheckoutInput,
  PaymentProvider,
  WebhookRequest,
} from "../../shared/payment-provider";
import type {
  CheckoutHandle,
  CommerceEvent,
  CommerceEventType,
  Money,
  PaymentStatus,
} from "../../shared/commerce-types";
import type { ProviderCapabilities } from "../../shared/capabilities";
import { assertCapability } from "../../shared/capabilities";
import { StripeWebhookVerifier } from "./stripe-signature";

export interface StripeStaticProviderConfig {
  /** Server-side only. Never expose to the browser (CLAUDE.md §2 #4). */
  secretKey: string;
  /** `whsec_...` — the endpoint secret from the Stripe Dashboard / `stripe listen`. */
  webhookSecret: string;
}

/** Minimal shape we read off a verified Stripe event — not the full Stripe.Event type. */
interface StripeEventLike {
  id: string;
  type: string;
  data: { object: Record<string, unknown> };
}

const STRIPE_TO_COMMERCE_EVENT_TYPE: Record<string, CommerceEventType> = {
  "payment_intent.succeeded": "payment.succeeded",
  "payment_intent.amount_capturable_updated": "payment.succeeded", // authorized, capturable
  "payment_intent.payment_failed": "payment.failed",
  "charge.refunded": "payment.refunded",
  "refund.created": "payment.refunded",
  "checkout.session.completed": "checkout.completed",
};

function mapStripeStatusToPaymentStatus(status: string): PaymentStatus {
  switch (status) {
    case "requires_capture":
      return "authorized";
    case "succeeded":
      return "captured";
    case "canceled":
      return "canceled";
    case "requires_payment_method":
    case "requires_confirmation":
    case "requires_action":
    case "processing":
      return "requires_payment";
    default:
      return "failed";
  }
}

export class StripeStaticProvider implements PaymentProvider {
  readonly id = "stripe" as const;
  readonly capabilities: ProviderCapabilities = {
    checkout: "hosted",
    authorizeCapture: true,
    refunds: true,
    catalogSourceOfTruth: "app",
    posReconciliation: false,
  };

  private readonly stripe: Stripe;
  private readonly verifier: StripeWebhookVerifier;

  constructor(config: StripeStaticProviderConfig) {
    // apiVersion is intentionally OMITTED: the installed `stripe` package
    // pins a literal-typed default matching its own compiled types. Hard-
    // coding a version string here would silently drift out of sync with
    // whatever `stripe` version the consumer's lockfile resolves to.
    this.stripe = new Stripe(config.secretKey);
    this.verifier = new StripeWebhookVerifier(config.webhookSecret);
  }

  async createCheckout(input: CreateCheckoutInput): Promise<CheckoutHandle> {
    const lineItems = input.lineItems.map((item) => ({
      quantity: item.quantity,
      price_data: {
        currency: item.amount.currency.toLowerCase(),
        unit_amount: item.amount.amount,
        product_data: { name: item.name },
      },
    }));

    const paymentLink = await this.stripe.paymentLinks.create(
      {
        line_items: lineItems,
        payment_intent_data: { capture_method: "manual" },
        ...(input.returnUrl && {
          after_completion: { type: "redirect", redirect: { url: input.returnUrl } },
        }),
      },
      { idempotencyKey: input.idempotencyKey },
    );

    return { mode: "hosted", url: paymentLink.url };
  }

  async handleWebhook(req: WebhookRequest): Promise<CommerceEvent> {
    const verified = this.verifier.verify(req.rawBody, req.headers);
    if (!verified) {
      // Reject — NEVER return an unverified event to the caller (contract in payment-provider.ts).
      throw new Error("Stripe webhook signature verification failed.");
    }

    const payload = typeof req.rawBody === "string" ? req.rawBody : req.rawBody.toString("utf8");
    const event = JSON.parse(payload) as StripeEventLike; // parse ONLY after verification.
    const object = event.data.object;

    const amount =
      typeof object.amount === "number" && typeof object.currency === "string"
        ? ({ amount: object.amount, currency: object.currency.toUpperCase() } satisfies Money)
        : undefined;

    return {
      id: event.id,
      type: STRIPE_TO_COMMERCE_EVENT_TYPE[event.type] ?? "unknown",
      provider: "stripe",
      amount,
      reference: typeof object.id === "string" ? object.id : undefined,
      raw: event,
    };
  }

  async authorize(reference: string, _idempotencyKey: string): Promise<PaymentStatus> {
    assertCapability(this.capabilities, "authorizeCapture");
    // Authorization already happened when the buyer completed the hosted
    // checkout (capture_method: "manual"). This call confirms + surfaces
    // that state — Stripe has no separate GET-time idempotency key, so
    // idempotencyKey is accepted for interface symmetry but unused on reads.
    const intent = await this.stripe.paymentIntents.retrieve(reference);
    return mapStripeStatusToPaymentStatus(intent.status);
  }

  async capture(reference: string, idempotencyKey: string): Promise<PaymentStatus> {
    assertCapability(this.capabilities, "authorizeCapture");
    const intent = await this.stripe.paymentIntents.capture(reference, {}, { idempotencyKey });
    return mapStripeStatusToPaymentStatus(intent.status);
  }

  async refund(reference: string, amount: Money, idempotencyKey: string): Promise<PaymentStatus> {
    assertCapability(this.capabilities, "refunds");
    // Stripe's PaymentIntent has no "refunded" status of its own — this
    // return value reflects the LOGICAL outcome of a successful Refund
    // creation. For partial-refund bookkeeping, inspect the returned
    // Refund's `amount`/`status` (not exposed through this narrow interface).
    await this.stripe.refunds.create(
      { payment_intent: reference, amount: amount.amount },
      { idempotencyKey },
    );
    return "refunded";
  }

  async cancel(reference: string, idempotencyKey: string): Promise<PaymentStatus> {
    assertCapability(this.capabilities, "authorizeCapture");
    const intent = await this.stripe.paymentIntents.cancel(reference, {}, { idempotencyKey });
    return mapStripeStatusToPaymentStatus(intent.status);
  }
}

/**
 * Stripe — FRAMEWORK tier PaymentProvider (Next.js / Astro).
 *
 * Embedded checkout via the Payment Element + Payment Intents
 * (https://docs.stripe.com/payments/payment-element, 2026-07-13): the
 * server creates a PaymentIntent and hands the browser only a client
 * secret + the publishable key; the Payment Element (see
 * payment-element.tsx) renders the card fields inside Stripe's iframe.
 * This module never sees a card number (PCI SAQ-A).
 *
 * Capabilities declared honestly per ../../shared/capabilities:
 *   - checkout: "embedded"      — the Payment Element renders in-page.
 *   - authorizeCapture: true    — see the capture_method note below.
 *   - refunds: true             — via the Refunds API.
 *   - catalogSourceOfTruth: "app" — Stripe has no real catalog; the caller's
 *     line items (../../shared/commerce-types Money) are summed into the
 *     PaymentIntent amount directly (no per-item Price objects needed here).
 *   - posReconciliation: false — Stripe has no POS ledger to reconcile against.
 *
 * Manual-capture default: createCheckout() sets `capture_method: "manual"`,
 * so a confirmed PaymentIntent lands in "requires_capture" (our
 * "authorized") rather than auto-capturing — mirrors the static tier so
 * authorize()/capture() are meaningful on both tracks. Delete that one
 * field for immediate capture.
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

export interface StripeFrameworkProviderConfig {
  /** Server-side only. Never expose to the browser (CLAUDE.md §2 #4). */
  secretKey: string;
  /** Client-side. Safe to expose — identifies the Stripe account, not a credential. */
  publishableKey: string;
  /** `whsec_...` — the endpoint secret from the Stripe Dashboard / `stripe listen`. */
  webhookSecret: string;
}

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

/** Sums ad-hoc line items into a single PaymentIntent amount. All items must share one currency. */
function sumLineItems(lineItems: CreateCheckoutInput["lineItems"]): Money {
  if (lineItems.length === 0) {
    throw new Error("createCheckout requires at least one line item.");
  }
  const currency = lineItems[0].amount.currency;
  let amount = 0;
  for (const item of lineItems) {
    if (item.amount.currency !== currency) {
      throw new Error(
        `All line items must share one currency for a single PaymentIntent (saw "${currency}" and "${item.amount.currency}").`,
      );
    }
    amount += item.amount.amount * item.quantity;
  }
  return { amount, currency };
}

export class StripeFrameworkProvider implements PaymentProvider {
  readonly id = "stripe" as const;
  readonly capabilities: ProviderCapabilities = {
    checkout: "embedded",
    authorizeCapture: true,
    refunds: true,
    catalogSourceOfTruth: "app",
    posReconciliation: false,
  };

  private readonly stripe: Stripe;
  private readonly verifier: StripeWebhookVerifier;
  private readonly publishableKey: string;

  constructor(config: StripeFrameworkProviderConfig) {
    // apiVersion intentionally OMITTED — see static/provider.ts's comment;
    // the installed `stripe` package pins its own literal-typed default.
    this.stripe = new Stripe(config.secretKey);
    this.verifier = new StripeWebhookVerifier(config.webhookSecret);
    this.publishableKey = config.publishableKey;
  }

  async createCheckout(input: CreateCheckoutInput): Promise<CheckoutHandle> {
    const total = sumLineItems(input.lineItems);

    const intent = await this.stripe.paymentIntents.create(
      {
        amount: total.amount,
        currency: total.currency.toLowerCase(),
        capture_method: "manual",
        automatic_payment_methods: { enabled: true },
      },
      { idempotencyKey: input.idempotencyKey },
    );

    if (!intent.client_secret) {
      throw new Error("Stripe did not return a client_secret for the PaymentIntent.");
    }

    return {
      mode: "embedded",
      clientSecret: intent.client_secret,
      publishableKey: this.publishableKey,
    };
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
    // Authorization happens when the buyer confirms the PaymentIntent via
    // the Payment Element (capture_method: "manual"). This call confirms +
    // surfaces that state; Stripe has no idempotency key on GET requests,
    // so idempotencyKey is accepted for interface symmetry but unused here.
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

/**
 * Stripe FRAMEWORK tier — client component mounting the Payment Element.
 *
 * Card data is entered directly into Stripe's iframe (the Payment Element)
 * and confirmed by Stripe.js in the browser — this component never reads,
 * stores, or forwards a card number/CVC/expiry to any handler of ours
 * (PCI SAQ-A). It only reads the `clientSecret` returned by checkout.ts and
 * the public `publishableKey`, neither of which is a secret credential.
 *
 * Peer deps (install in your site, not scaffolded here):
 *   npm install @stripe/stripe-js @stripe/react-stripe-js
 *
 * Usage (Next.js App Router "use client" boundary — a Server Component
 * fetches `clientSecret`/`publishableKey` from checkout.ts, then renders
 * this client component with them as props):
 *
 *   <StripeCheckoutForm
 *     clientSecret={clientSecret}
 *     publishableKey={publishableKey}
 *     returnUrl="https://example.com/thank-you"
 *   />
 *
 * Strings live in one MESSAGES object so a consumer can swap in an i18n
 * lookup (react-intl / next-intl / etc.) without touching the form logic —
 * CLAUDE.md §4 dimension 7.
 */

"use client";

import { useMemo, useState, type FormEvent } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements, PaymentElement, useElements, useStripe } from "@stripe/react-stripe-js";

const MESSAGES = {
  heading: "Payment details",
  submitIdle: "Pay now",
  submitProcessing: "Processing…",
  genericError: "Something went wrong. Please check your details and try again.",
  missingStripeInstance: "Payment form failed to load. Please refresh the page.",
};

export interface StripeCheckoutFormProps {
  /** From checkout.ts's response — identifies THIS PaymentIntent, not a secret credential. */
  clientSecret: string;
  /** Public by design — identifies the Stripe account, safe in client-side code. */
  publishableKey: string;
  /** Where Stripe redirects the buyer after an off-session payment method (e.g. a bank redirect) completes. */
  returnUrl: string;
  onSuccess?: () => void;
}

export function StripeCheckoutForm(props: StripeCheckoutFormProps) {
  // Memoized so loadStripe() runs once per publishableKey, not on every render.
  const stripePromise = useMemo(() => loadStripe(props.publishableKey), [props.publishableKey]);

  return (
    <Elements stripe={stripePromise} options={{ clientSecret: props.clientSecret }}>
      <PaymentForm returnUrl={props.returnUrl} onSuccess={props.onSuccess} />
    </Elements>
  );
}

function PaymentForm({
  returnUrl,
  onSuccess,
}: Pick<StripeCheckoutFormProps, "returnUrl" | "onSuccess">) {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!stripe || !elements) {
      setErrorMessage(MESSAGES.missingStripeInstance);
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    // stripe.confirmPayment reads the card fields directly out of the
    // Payment Element's iframe — this function never sees them. Stripe
    // renders a card-specific declined-card message via `error.message`
    // when confirmation fails (test mode: try card 4000 0000 0000 0002).
    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: { return_url: returnUrl },
    });

    if (error) {
      setErrorMessage(error.message ?? MESSAGES.genericError);
      setIsProcessing(false);
      return;
    }

    // A payment method that completes without a redirect (most cards) falls
    // through to here; redirect-based methods navigate away before this runs.
    onSuccess?.();
    setIsProcessing(false);
  }

  return (
    <form onSubmit={handleSubmit} aria-labelledby="stripe-checkout-heading" noValidate>
      <h2 id="stripe-checkout-heading">{MESSAGES.heading}</h2>
      <PaymentElement id="stripe-payment-element" />
      {errorMessage !== null && (
        <p role="alert" aria-live="assertive" className="stripe-checkout-error">
          {errorMessage}
        </p>
      )}
      <button type="submit" disabled={!stripe || isProcessing} aria-busy={isProcessing}>
        {isProcessing ? MESSAGES.submitProcessing : MESSAGES.submitIdle}
      </button>
    </form>
  );
}

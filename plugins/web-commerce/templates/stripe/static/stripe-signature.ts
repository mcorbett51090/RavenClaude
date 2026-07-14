/**
 * Stripe webhook signature verification — hand-rolled to the documented
 * `Stripe-Signature` scheme (https://docs.stripe.com/webhooks#verify-manually,
 * 2026-07-13) so the constant-time compare in ../../shared/webhook-verify is
 * demonstrably on the hot path, not hidden inside a black-box SDK call.
 *
 * Scheme: header = "t=<unix-seconds>,v1=<hex-hmac>[,v0=<hex-hmac>...]".
 * Signed content = "<timestamp>.<raw-body>". Expected signature =
 * HMAC-SHA256(endpointSecret, signedContent), hex-encoded. A request is
 * valid only if at least one v1 signature matches AND the timestamp is
 * within tolerance (replay-window defense — Stripe's own guidance).
 *
 * CLAUDE.md §3 invariant: verify BEFORE parsing, constant-time compare.
 * This file never JSON.parses the body — that is the caller's job, and only
 * after `verify()` returns true.
 */

import { createHmac } from "node:crypto";
import { safeSignatureEqual } from "../../shared/webhook-verify";
import type { WebhookVerifier } from "../../shared/webhook-verify";

/** Stripe's documented tolerance for the `t=` timestamp (2026-07-13). */
export const STRIPE_SIGNATURE_TOLERANCE_SECONDS = 300;

interface ParsedSignatureHeader {
  timestamp: number;
  signatures: string[];
}

function parseSignatureHeader(header: string): ParsedSignatureHeader | null {
  let timestamp = -1;
  const signatures: string[] = [];
  for (const part of header.split(",")) {
    const [key, value] = part.split("=");
    if (key === "t" && value) timestamp = Number.parseInt(value, 10);
    if (key === "v1" && value) signatures.push(value);
  }
  if (timestamp === -1 || Number.isNaN(timestamp) || signatures.length === 0) {
    return null;
  }
  return { timestamp, signatures };
}

export class StripeWebhookVerifier implements WebhookVerifier {
  constructor(
    private readonly endpointSecret: string,
    private readonly toleranceSeconds: number = STRIPE_SIGNATURE_TOLERANCE_SECONDS,
    /** Injectable for tests only — defaults to the real wall clock. */
    private readonly nowSeconds: () => number = () => Date.now() / 1000,
  ) {
    if (!endpointSecret) {
      throw new Error(
        "StripeWebhookVerifier requires a non-empty endpoint secret (STRIPE_WEBHOOK_SECRET).",
      );
    }
  }

  verify(rawBody: string | Buffer, headers: Record<string, string | undefined>): boolean {
    const header = headers["stripe-signature"] ?? headers["Stripe-Signature"];
    if (!header) return false;

    const parsed = parseSignatureHeader(header);
    if (!parsed) return false;

    const ageSeconds = Math.abs(this.nowSeconds() - parsed.timestamp);
    if (ageSeconds > this.toleranceSeconds) return false;

    const payload = typeof rawBody === "string" ? rawBody : rawBody.toString("utf8");
    const signedContent = `${parsed.timestamp}.${payload}`;
    const expected = createHmac("sha256", this.endpointSecret)
      .update(signedContent, "utf8")
      .digest("hex");

    // Constant-time compare against EVERY signature Stripe sent (accounts for
    // in-flight secret rotation, which briefly delivers two v1 signatures).
    return parsed.signatures.some((candidate) => safeSignatureEqual(expected, candidate));
  }
}

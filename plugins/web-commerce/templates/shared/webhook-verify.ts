import { timingSafeEqual } from "node:crypto";

/**
 * Constant-time comparison of two signatures. ALWAYS use this to compare a
 * computed HMAC against the header value — a plain `===` leaks timing
 * information an attacker can use to forge a signature (CLAUDE.md §3).
 *
 * On a length mismatch it still performs one timingSafeEqual to keep the
 * timing profile flat, then returns false.
 */
export function safeSignatureEqual(a: string, b: string): boolean {
  const bufA = Buffer.from(a, "utf8");
  const bufB = Buffer.from(b, "utf8");
  if (bufA.length !== bufB.length) {
    timingSafeEqual(bufA, bufA);
    return false;
  }
  return timingSafeEqual(bufA, bufB);
}

/**
 * Each provider track implements a verifier with its own scheme. The shared,
 * non-negotiable rule: verify (constant-time) BEFORE parsing the body.
 *
 *   - Stripe:  `Stripe-Signature` header, `whsec_` endpoint secret, 5-min tolerance
 *   - Square:  `x-square-hmacsha256-signature` over (signatureKey + notificationUrl + rawBody)
 *   - Shopify: `X-Shopify-Hmac-Sha256` (base64 HMAC-SHA256) over rawBody
 *
 * Return `true` only when the signature verifies; the caller drops the request
 * on `false`.
 */
export interface WebhookVerifier {
  verify(rawBody: string | Buffer, headers: Record<string, string | undefined>): boolean;
}

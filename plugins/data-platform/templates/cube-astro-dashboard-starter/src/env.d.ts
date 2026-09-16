/// <reference types="astro/client" />

declare namespace App {
  interface Locals {
    /** Per-request CSP nonce (set in src/middleware.ts). */
    cspNonce: string;
  }
}

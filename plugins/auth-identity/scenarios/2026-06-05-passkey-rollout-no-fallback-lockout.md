---
scenario_id: 2026-06-05-passkey-rollout-no-fallback-lockout
contributed_at: 2026-06-05
plugin: auth-identity
product: webauthn-passkeys
product_version: "2026.06"
scope: likely-general
tags: [passkeys, webauthn, fallback, account-recovery, conditional-ui]
confidence: medium
reviewed: false
---

## Problem

A consumer app shipped passkeys as the **only** login method to "go passwordless," excited by the phishing-resistance story. Support tickets spiked within a week: users who registered a passkey on a **single device** (the only one they had at signup) lost access when that device was wiped, lost, or its OS keychain reset, and had no way back in — there was no email/magic-link path, no second factor to recover from, and the passkey was **device-bound** (not synced), so it didn't roam to a new phone. A second cluster: corporate users on a locked-down browser where the platform authenticator was disabled by policy simply saw "no passkey available" and a dead end. Passkey *adoption* among new signups was also far below the projection (~15–20%), so most users were hitting a method they hadn't set up.

## Context

- Surface: web app on Supabase Auth; **Supabase Passkeys was in beta/experimental** at rollout (API may change, explicit opt-in) — making it the *sole* method compounded the risk of betting account access on an experimental API.
- Constraint: a passkey is a **credential on an authenticator**, not an account-recovery system. Device-bound passkeys don't roam; synced passkeys roam within one provider's ecosystem (Apple/Google/Microsoft) but not across, and syncable passkeys are **not permitted at NIST AAL3**. "Passwordless" must still answer "what happens when the authenticator is gone?"
- This touches the login + recovery path → **mandatory `ravenclaude-core/security-reviewer`** before it ships (CLAUDE.md §8).

## Attempts

- Tried: "tell users to register a backup passkey on a second device." Outcome: helps the multi-device user but does nothing for the single-device user (the majority at signup) and nothing for the policy-blocked corporate browser; treated as good advice, not the fix.
- Tried: add a **non-passkey fallback that is never disabled** — magic link (single-use, short-expiry) as the recovery + alternate path, so a user with no working authenticator can always get back in, and email+password only where explicitly required (provider owns hashing/breach-check). Outcome: the lockout dead-ends disappeared; passkey stays the *preferred* phishing-resistant method, not the *only* one.
- Tried (the move that worked end-to-end): use **conditional UI / autofill** to *offer* the passkey when one is discoverable (so the 15–20% who have one get the smooth path) while always showing the fallback; prompt to enroll a passkey **after** first successful login rather than gating signup on it; and keep the recovery path (magic link) outside the passkey dependency. Outcome: adoption rose because enrollment was post-login and frictionless, and no user could be locked out.

## Resolution

The failure was **making a credential the sole method with no recovery path**, not passkeys themselves. Passkeys are the right phishing-resistant *default to offer*; the fix is to always keep a non-passkey fallback (magic link / email+password where required), enroll passkeys post-login via conditional UI, and never bet account access on a single device or a beta API. Adoption is earned, not forced.

**Action for the next engineer hitting this pattern:** if passkeys/WebAuthn is the *only* login method, that is the finding — never force a single credential with no recovery. Offer passkeys via conditional UI, enroll after first login, and keep an always-available fallback (magic link single-use; email+password only if required). Gate any beta passkey API behind a fallback. Traverse the **which-auth-providers-to-offer** and the new **MFA / step-up factor** trees in [`../knowledge/auth-identity-decision-trees.md`](../knowledge/auth-identity-decision-trees.md) and [`../knowledge/mfa-and-auth-method-selection-trees.md`](../knowledge/mfa-and-auth-method-selection-trees.md), apply [`passkeys-need-a-fallback`](../best-practices/passkeys-need-a-fallback.md), and route the change through `security-reviewer`.

**Sources (retrieved 2026-06-05):**
- Supabase — Passkey authentication (beta/experimental; opt-in; built on WebAuthn) — https://supabase.com/docs/guides/auth/passkeys
- FIDO Alliance / W3C WebAuthn Level 3 — discoverable credentials, conditional UI (autofill), device-bound vs synced passkeys — https://www.w3.org/TR/webauthn-3/
- NIST SP 800-63B (rev 4) — AAL2 phishing-resistant option; AAL3 hardware non-exportable; syncable passkeys not at AAL3 — https://pages.nist.gov/800-63-4/
- Plugin best-practices: [`../best-practices/passkeys-need-a-fallback.md`](../best-practices/passkeys-need-a-fallback.md), [`../best-practices/magic-link-expiry-and-single-use.md`](../best-practices/magic-link-expiry-and-single-use.md)

Passkey/WebAuthn capabilities and Supabase's beta status are volatile (Supabase Passkeys was experimental as of 2026-06). `[verify-at-use]` the current Supabase Passkeys status, the WebAuthn-3 conditional-UI support matrix, and the live NIST AAL guidance before quoting.

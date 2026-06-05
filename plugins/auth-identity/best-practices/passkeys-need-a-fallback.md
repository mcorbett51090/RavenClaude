# Passkeys Must Have a Fallback Login Method

**Status:** Absolute rule
**Domain:** Auth & Identity — Passwordless / passkeys
**Applies to:** `auth-identity`

---

## Why this exists

Passkeys are the phishing-resistant, credential-stuffing-resistant future of authentication — but as of 2026, global passkey adoption is approximately 15–20% of users `[verify-at-build]`. A login flow that offers *only* passkeys locks out the 80–85% of users who have not yet set one up, including users on shared devices, users who lost or changed their device, and users whose browser or OS does not support WebAuthn. Every passkey implementation must offer at least one fallback: magic link, email+password, or a social SSO provider.

## How to apply

**Login method hierarchy for passkey-capable apps:**

```
1. Passkey (WebAuthn credential) — primary, if registered
2. Magic link — universal fallback (no account required, no password to forget)
3. Social SSO (Google, Apple) — for users who don't want a password
4. Email + password — explicit fallback only if required by the use case
```

**Implementation with Supabase Auth (passkeys in beta — verify status `[verify-at-build]`):**

```javascript
// Step 1: Try passkey authentication
try {
  const { data, error } = await supabase.auth.signInWithPasskey();
  if (!error) return; // success
} catch (e) {
  // WebAuthn not available, passkey not registered, or user cancelled
}

// Step 2: Fall through to magic link or social SSO
// Show the fallback login UI
```

**UX pattern:**
- Show the passkey button (or browser's autofill prompt) prominently.
- Show "Sign in with email" or "Use Google" as visually available alternatives — not hidden behind a "more options" disclosure.
- On passkey setup: prompt after the user has logged in via a fallback method ("Set up face ID for faster login next time?"), not as a barrier to first login.

**Do:**
- Gracefully catch `WebAuthnNotSupportedError` and `NotAllowedError` (user cancelled) and fall back to the alternatives.
- Persist the user's passkey preference (if they registered one, prefer it on the next visit) but do not *require* it.
- Test the fallback path explicitly — it is the path most users take.

**Don't:**
- Make passkey registration mandatory before the user can access the app.
- Remove the email/magic-link option to "simplify" the UI — this is an accessibility and recovery-path issue.
- Silently fail when WebAuthn is unavailable — show the fallback explicitly.

## Edge cases / when the rule does NOT apply

- **Enterprise / corporate apps with MDM-controlled devices**: if the device fleet is uniformly passkey-capable and managed, a passkey-only policy is defensible — document it in the security design with a recovery flow for lost/changed devices.
- **High-security internal tools** requiring phishing-resistant auth: passkey can be the primary and only interactive method, with a supervised recovery process as the fallback. Route through `ravenclaude-core/security-reviewer` for the recovery design.

## See also

- [`../agents/auth-architect.md`](../agents/auth-architect.md) — chooses the login method mix and the fallback hierarchy
- [`./prefer-managed-auth-over-rolling-your-own.md`](./prefer-managed-auth-over-rolling-your-own.md) — the reason Supabase Auth (not a custom WebAuthn server) handles the passkey implementation

## Provenance

Codifies the passkey fallback requirement from `social-and-passwordless-providers-2026.md` and `CLAUDE.md` §3 (the "variety pack" — never force a single login method). WebAuthn spec: W3C Web Authentication Level 3 (2025). Passkey adoption estimate `[unverified — training knowledge; verify before quoting to a client]`. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_

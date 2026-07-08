---
name: idp-segregation
description: "IdP-backed segregation of duties for the close. Evolves close_state.py's config-asserted --actor string into an optionally IdP-VERIFIED identity via scripts/close_identity.py: an IdentityAdapter seam, split OIDC claim-validation + signature-verification (HS256 stdlib; RS256/JWKS via optional PyJWT, refuse-loudly if absent; alg:none + alg-confusion rejected per RFC 8725), SoD keyed on sub@iss + role claims, and a fresh step-up token to LOCK. Honest boundary: the plugin enforces the CHECK; the consumer IdP must segregate role assignment and hold key/WORM off-box. Used by `controller` + `audit-prep-specialist`; every token-validation change routes through `security-reviewer`."
---

# Skill: idp-segregation

**Purpose:** Close the one honest gap in [`close-approval-workflow`](../close-approval-workflow/SKILL.md): its segregation of duties (SoD) is enforced on a caller-supplied `--actor NAME` string, which nothing binds to a real person. This skill provides the **IdentityAdapter seam** that upgrades that string to an **IdP-verified identity** — *when, and only when,* the consumer wires a real identity provider — without breaking today's behaviour.

Engine: [`../../scripts/close_identity.py`](../../scripts/close_identity.py) (stdlib only; PyJWT is an OPTIONAL extra used only for asymmetric verification and refused-loudly when absent).

> **DECISION-SUPPORT / REFERENCE IMPLEMENTATION — not an audited close, not a live-verified identity system.** The plugin delivers a **token-level preparer≠approver CHECK**, NOT delivered segregation of duties: real SoD needs the consumer's IdP to *segregate the role assignment itself* (two distinct directory principals). The plugin enforces the *check* and validates the token you present; the IdP, the JWKS endpoint, real credentials, off-box key custody, and the immutable/WORM store are the **consumer's** step. **Tamper-resistance is 100% consumer infrastructure** (off-box key custody + a WORM store) — the plugin ships a tamper-**EVIDENCE** scaffold (a hash chain that *detects* edits), not auditor-grade tamper-**resistance**. See the honest boundary below and do not overclaim.
>
> **SPLIT-BRAIN NOTE (read with `warehouse-dashboard`).** The entity *entitlement* (the warehouse RLS `allowed_entities[]` array claim) and this *SoD identity* MUST derive from the **same verified token / issuer**. If they come from two different tokens, a viewer can hold entitlement as one principal while the close is approved under another — a split identity. `entity_rls.bind_entitlement_to_identity(entity_claims, identity, now)` enforces this: it fails closed (deny-all) unless the entitlement token's `iss` and `sub@iss` match the verified `VerifiedIdentity`.

## The adapter seam

`close_state.py` reasons about a **string**. `close_identity.py` swaps that for a **`VerifiedIdentity`** value object resolved by one of two adapters behind a single `resolve()` contract:

```
VerifiedIdentity = {
  subject           # sub@iss  — the STABLE MACHINE IDENTITY, never a display name
  email
  roles             # frozenset[str], from a CONFIGURABLE claim path
  issuer
  verified          # True only when signature verified AND claims validated
  token_fingerprint # sha256(token)[:16] — never the raw token
  display           # the human-facing --actor string; ADVISORY only
}
```

| Adapter | Input | `verified` | Badge | Use |
|---|---|---|---|---|
| `ConfigActorAdapter` | today's `--actor` + a local roles map | `False` | `config-asserted UNVERIFIED` | Backward-compatible default. Subject is `config:<actor>` (namespaced so it can never collide with a real `sub@iss`); SoD behaves exactly as `close_state.py` does today. |
| `OidcJwtAdapter` | an IdP-issued OIDC `--id-token` | `True` (only after both halves pass) | `IdP-verified` | The upgrade path. Subject is `sub@iss`; roles come from the configured claim path. |

A consumer can add a third adapter (e.g. a PyJWT/JWKS-backed RS256 one) behind the same `resolve()` contract without touching the state machine.

## Token trust is SPLIT into two independently-testable halves

Per RFC 8725 (JWT best current practice), the two halves are kept separate:

1. **`validate_claims(...)` — pure, no crypto.** Refuses, each with its own stable reason code:
   - `iss_mismatch` — `iss` must **exactly** equal the expected issuer (no substring / prefix match — `https://issuer.example.com.evil.com/` is rejected).
   - `missing_sub` — a non-empty `sub` is the identity anchor.
   - `aud_mismatch` — `aud` must contain your `client_id`.
   - `untrusted_aud` — `aud` must carry **no** audience beyond `{client_id} ∪ trusted_audiences` (a token minted for another app is rejected).
   - `expired` — `now > exp + leeway`.
   - `nbf_future` — `now < nbf - leeway`.
   - `email_unverified` — `email_verified` must be exactly `true`.
2. **`verify_signature(...)` — the cryptographic half.**
   - **HS256** is verified in-process with the stdlib (`hmac` + `hashlib`, constant-time `compare_digest`).
   - **RS256 / ES256 / PS256 / JWKS** need asymmetric crypto the stdlib lacks → the **OPTIONAL PyJWT** path. **If PyJWT is absent it REFUSES LOUDLY** (`reason=pyjwt_absent`) — it never downgrades to an unverified pass.
   - `alg: none` (unsigned) → rejected (`alg_none`).
   - **Algorithm confusion** → rejected (`alg_confusion`) in **both** directions: an HS256 adapter handed an RS256 header, or an RS256 adapter handed an HS256 header (the classic attack where a public key is abused as an HMAC secret).

## Role-based SoD — keyed on the subject and role claims, not the display string

```python
assert_sod(preparer, approver, amount=..., threshold=..., approver_role="finance.approver")
```

- `sod_same_subject` — the approver's `sub@iss` equals the preparer's and `amount >= threshold`. This keys on **subject**, so a renamed `--actor` on the *same token* **cannot** launder a self-approval — even if that token also carries the approver role.
- `sod_missing_role` — the approver's role claims (from the **configurable** claim path) do not include the required role.

Roles come from a configurable path so the same code fits every IdP's shape: Entra ID's top-level `roles` array, Okta/Auth0's namespaced literal key (`https://myapp.example.com/roles`), or Keycloak's dotted `resource_access.<client>.roles`.

**LOCK demands a fresh step-up token** — `assert_fresh_stepup(stepup_claims, now_epoch=..., max_age_seconds=300)` refuses `stepup_absent` / `stepup_stale` / `stepup_no_authtime`. Locking a period mutates the audit surface, so it requires a *recent re-authentication* (measured against `auth_time`, falling back to `iat`), not the same session token used to approve.

## HONEST BOUNDARY (do not overclaim, no false competitive claims)

The plugin **enforces the CHECK and validates the token.** It **cannot** ship the three things that make the control auditor-reliable, because they are **consumer infrastructure that lives off this box**:

1. **A real IdP that SEGREGATES role assignment.** Preparer and approver must be *distinct principals with distinct role grants in the directory* — not two rows in a local roles map. The plugin validates whatever the IdP asserts; it cannot be the IdP.
2. **Key custody OFF-BOX.** The HS256 secret / RS256 signing key must live in an HSM / KMS / secret store the operator running the close cannot read. A key this process can read makes the chain tamper-**evident**, not tamper-**resistant**.
3. **A WORM sink.** An append-only, immutable store (S3 Object Lock, Azure immutable blob, a QLDB-style ledger) so a retroactive edit is *prevented*, not merely *detected*.

The `DetachedSigner` and `WormSink` interfaces in the engine are the **seam** for the tamper-resistant tier; the plugin ships the interface and a loud no-op reference, never a real signer or immutable store. `tamper_tier_report(...)` states honestly which tier is actually wired (`tamper-evident only` until both are present). Real, auditor-reliable segregation needs all three consumer pieces **plus** the IdP — this skill makes the check enforceable and IdP-ready; it does not "design out" any incident on its own.

## Consumer OIDC wiring runbook

> All credentials are referenced by **env-var NAME** — never a literal. Every concrete token-validation change routes through `ravenclaude-core/security-reviewer` before it ships.

1. **Register a confidential OIDC client** with your IdP (Entra app registration / Okta or Auth0 application / Google Cloud OAuth client). Record the **issuer** URL and **client_id**. Use **Authorization Code + PKCE** (see the `auth-identity` plugin's [`oauth-oidc-and-google-sso`](../../../auth-identity/knowledge/oauth-oidc-and-google-sso.md) doctrine — `auth-identity` owns the login flow; this skill only *validates the resulting ID token*).
2. **Assign the two roles to two distinct directory principals** — e.g. `finance.preparer` and `finance.approver`. This is the load-bearing consumer step: SoD is only real if the directory itself segregates the grants. Confirm the roles surface in the ID token's claim path (`roles` for Entra; a namespaced claim for Okta/Auth0; `resource_access.<client>.roles` for Keycloak).
3. **Production verification REQUIRES asymmetric signing (RS256/ES256) with rotating JWKS — which REQUIRES the optional `PyJWT[crypto]` extra.** Install `PyJWT[crypto]`, wire the issuer's `jwks_uri`, and add a JWKS-backed adapter behind `resolve()`. **HS256 is DEV / FIXTURE-ONLY**: it exists so the stdlib-only test suite can self-mint and verify tokens with no dependency — it is **not** a production consumer-IdP verification path. Its shared secret is a symmetric key *both* parties hold (the IdP and this box), so it cannot prove the token came from the IdP rather than from the operator running the close. Consumer-IdP verification is RS256/ES256/JWKS via PyJWT, full stop; if PyJWT is absent that path **refuses loudly** (`pyjwt_absent`) rather than downgrading. Never pin a key; honor JWKS rotation.
4. **Source every secret from a secret store**, exposing only the env-var NAME to the CLI:
   ```shell
   # config-asserted (today's behaviour; verified=False)
   python3 scripts/close_identity.py inspect-config --actor carol --roles-map roles.json

   # IdP-verified (HS256 is DEV/FIXTURE-ONLY — production uses RS256/ES256/JWKS via PyJWT;
   #               secret from an env var NAME, never a literal)
   python3 scripts/close_identity.py verify-token \
       --id-token "$ID_TOKEN" --issuer "$OIDC_ISSUER" --client-id "$OIDC_CLIENT_ID" \
       --alg HS256 --hs256-secret-env RAVEN_OIDC_HS256_SECRET --roles-claim-path roles

   # which tamper tier is actually wired (evident vs resistant)
   python3 scripts/close_identity.py tamper-tier
   ```
5. **Wire the off-box signer + WORM sink** (`DetachedSigner` / `WormSink`) to graduate from tamper-evident to tamper-resistant, and run `tamper_tier_report(...)` in your close attestation so the artifact states its true tier.
6. **Route the wiring through `security-reviewer`** — all token validation and signature verification in [`close_identity.py`](../../scripts/close_identity.py) is a mandatory security-review target.

## Acceptance evidence

[`../../scripts/test_close_identity.py`](../../scripts/test_close_identity.py) — 32/32, stdlib-only, self-minted synthetic HS256 tokens (fake local secret, obviously-fake `example.com` issuers/subjects, no network). It proves: `validate_claims` refuses expired / aud-miss / iss-drift / nbf-future / missing-sub / email_verified-false each with its specific reason; `verify_signature` accepts a correctly-signed HS256 token and rejects a payload-tampered copy, `alg:none`, and alg-confusion both directions; an RS256 token with PyJWT absent refuses loudly (never a pass); SoD refuses the same `sub@iss` at approve above threshold even with a different `--actor` and an approver role; and LOCK's step-up is **verified + subject-bound + fresh** — it refuses an absent token, a raw claims dict (must be a real JWS, not a dict), a stale `auth_time`, an **iat-only** token (no `auth_time` — a weaker signal, refused), a step-up from a **different principal** (`stepup_subject_mismatch`), and an unverified approver identity — accepting only a verified, subject-matched, fresh re-auth.

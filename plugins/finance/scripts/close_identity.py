#!/usr/bin/env python3
"""close_identity.py - an IdentityAdapter seam that evolves close_state.py's
config-asserted `--actor` string into an optionally *IdP-VERIFIED* identity,
WITHOUT breaking today's behaviour.

WHY THIS EXISTS. `close_state.py` enforces segregation of duties (SoD) on a
caller-supplied `--actor NAME` string. That is honest and testable at the local
tier, but the string is unauthenticated: nothing binds "alice" to a real person,
so the SoD refusal stops the *same declared actor* self-approving, not a
determined operator who simply types a different name. This module is the seam
that closes that gap when — and only when — the consumer wires a real identity
provider (Entra / Okta / Auth0 / Google). It does NOT replace `close_state.py`;
it upgrades the *identity* the state machine reasons about from a string to a
`VerifiedIdentity`, and it enforces SoD on the token's stable machine subject
(`sub@iss`) and role claims, never on the human-facing display string.

WHAT IS SPLIT, AND WHY. Token trust has two independent halves and this module
keeps them separate so each is unit-testable in isolation:

  * validate_claims(...)   — PURE claim checks: exact `iss` match, `aud` contains
      the client_id AND carries no untrusted extra audience, `exp` (with a small
      leeway), `nbf`, a present `sub`, and `email_verified`. No crypto here.
  * verify_signature(...)  — the cryptographic half. HS256 is verified with the
      stdlib (`hmac` + `hashlib`, constant-time compare). RS256 / ES256 / PS256
      and JWKS-backed verification need asymmetric crypto that the stdlib does not
      provide — that path uses the OPTIONAL PyJWT dependency and, if PyJWT is
      absent, REFUSES LOUDLY (raises) rather than silently downgrading to an
      unverified pass. Per RFC 8725, `alg: none` and algorithm-confusion (an
      HS256 adapter handed an RS256 header, or vice-versa) are rejected.

HONEST BOUNDARY / TIER CAVEAT — READ THIS. This module is a REFERENCE
IMPLEMENTATION and DECISION-SUPPORT scaffold, not an audited close and not a
live-verified identity system. The plugin can enforce the CHECK (validate the
token; refuse same-subject approval above threshold; require a fresh step-up
token to LOCK) and it can validate a token the consumer presents. It CANNOT ship
the parts that make the control auditor-reliable, because those are consumer
infrastructure that lives off this box:

  1. A real IdP that SEGREGATES role assignment — the preparer and approver must
     be *distinct principals with distinct role grants* in the directory, not two
     rows in a local roles map. The plugin validates whatever the IdP asserts; it
     cannot be the IdP.
  2. Key custody OFF-BOX — the HS256 shared secret / RS256 signing key must live
     in an HSM / KMS / secret store the operator running the close cannot read.
     A secret this process can read is tamper-EVIDENT, not tamper-RESISTANT.
  3. A WORM sink — an append-only, immutable store (S3 Object Lock, Azure
     immutable blob, a QLDB-style ledger) so a retroactive edit is *prevented*,
     not merely *detected*. The `DetachedSigner` + `WormSink` interfaces below are
     the SEAM for that tier; the plugin ships the interface and a loud no-op
     reference, never a real immutable store.

Do NOT claim this "designs out" any incident on its own, and do NOT make a false
competitive claim about it. It makes the honour-system honest, testable, and
IdP-ready. Live wiring — the IdP, the JWKS endpoint, real credentials, the
warehouse/WORM tier — is the consumer's step.

Stdlib only (hmac / hashlib / base64 / json / argparse / dataclasses / os / sys /
datetime). PyJWT is an OPTIONAL extra used ONLY for asymmetric verification and
is refused-loudly when absent. Python 3.8+.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
from dataclasses import dataclass

# Algorithms that require asymmetric crypto the stdlib does not provide — these
# route to the OPTIONAL PyJWT path (refuse-loudly when the dep is absent).
_ASYMMETRIC_ALGS = frozenset({"RS256", "RS384", "RS512",
                              "ES256", "ES384", "ES512",
                              "PS256", "PS384", "PS512"})

# The role a principal must carry (in the configured claim path) to approve.
DEFAULT_APPROVER_ROLE = "finance.approver"
DEFAULT_PREPARER_ROLE = "finance.preparer"
# A LOCK is an audit-surface-mutating action → demand a fresh step-up re-auth.
DEFAULT_STEPUP_MAX_AGE_SECONDS = 300


class IdentityError(Exception):
    """A refusal with a STABLE machine reason code plus a human message.

    The `reason` is the load-bearing, testable half — each distinct failure
    (expired / aud_mismatch / iss_mismatch / nbf_future / missing_sub /
    email_unverified / untrusted_aud / alg_none / alg_confusion / pyjwt_absent /
    bad_signature / sod_same_subject / sod_missing_role / stepup_absent /
    stepup_unverified / stepup_subject_mismatch / stepup_no_authtime /
    stepup_stale / stepup_future) carries its own code so a caller can branch on it and a test
    can assert the specific cause, not just "it refused".
    """

    def __init__(self, reason: str, message: str) -> None:
        self.reason = reason
        super().__init__(f"[{reason}] {message}")


# --------------------------------------------------------------------------- #
# The verified-identity value object
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class VerifiedIdentity:
    """The identity the close state machine should reason about.

    `subject` is the STABLE MACHINE IDENTITY `sub@iss` — never a display name.
    Two tokens with the same `sub@iss` are the same principal even if the caller
    passed a different `--actor` display string; SoD keys on THIS field so a
    renamed display can never launder a self-approval. `verified` is True only
    when BOTH the signature verified and the claims validated.
    """

    subject: str                       # sub@iss (config path: "config:<actor>")
    email: str | None
    roles: frozenset                   # frozenset[str] from the configured claim path
    issuer: str
    verified: bool
    token_fingerprint: str             # sha256(token)[:16] — never the raw token
    display: str | None = None      # the human-facing --actor string; ADVISORY only

    def badge(self) -> str:
        return "IdP-verified" if self.verified else "config-asserted UNVERIFIED"

    def as_dict(self) -> dict:
        return {
            "subject": self.subject,
            "email": self.email,
            "roles": sorted(self.roles),
            "issuer": self.issuer,
            "verified": self.verified,
            "token_fingerprint": self.token_fingerprint,
            "display": self.display,
            "badge": self.badge(),
        }


# --------------------------------------------------------------------------- #
# JWT primitives (base64url, unverified decode, claim validation, signature)
# --------------------------------------------------------------------------- #
def _b64url_decode(segment: str) -> bytes:
    """Decode a base64url segment, tolerating missing padding."""
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def decode_jwt_unverified(token: str) -> tuple[dict, dict]:
    """Split + base64url-decode a JWT's header and payload WITHOUT verifying it.

    This is decode-only; the caller MUST still run verify_signature +
    validate_claims. Kept explicit so no path can accidentally trust an
    unverified payload.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise IdentityError("malformed", "a compact JWS has exactly 3 dot-separated segments")
    try:
        header = json.loads(_b64url_decode(parts[0]))
        payload = json.loads(_b64url_decode(parts[1]))
    except Exception as exc:  # noqa: BLE001 - any decode failure is a malformed token
        raise IdentityError("malformed", f"could not base64url/JSON-decode a segment: {exc}") from exc
    if not isinstance(header, dict) or not isinstance(payload, dict):
        raise IdentityError("malformed", "header and payload must both be JSON objects")
    return header, payload


def validate_claims(
    claims: dict,
    *,
    issuer: str,
    client_id: str,
    now_epoch: int,
    leeway: int = 60,
    trusted_audiences: frozenset = frozenset(),
    require_email_verified: bool = True,
) -> dict:
    """PURE OIDC claim validation. Raises IdentityError(reason) on the FIRST
    failure; returns the claims unchanged when every check passes.

    No cryptography here — verify_signature is the separate, cryptographic half.
    Checks, in order, each with its own stable reason code:
      iss_mismatch   iss must EXACTLY equal `issuer` (no substring / prefix match)
      missing_sub    a non-empty `sub` must be present (it is the identity anchor)
      aud_mismatch   `aud` must contain the client_id
      untrusted_aud  `aud` must carry NO audience beyond {client_id} ∪ trusted
      missing_exp    an `exp` must be present
      expired        now must be <= exp + leeway
      nbf_future     now must be >= nbf - leeway (when nbf present)
      email_unverified  email_verified must be exactly True (when required)
    """
    if claims.get("iss") != issuer:
        raise IdentityError(
            "iss_mismatch",
            f"iss {claims.get('iss')!r} != expected {issuer!r} — exact match required, no drift",
        )

    sub = claims.get("sub")
    if not sub or not str(sub).strip():
        raise IdentityError("missing_sub", "no non-empty 'sub' claim — cannot bind an identity")

    aud = claims.get("aud")
    aud_set = frozenset([aud]) if isinstance(aud, str) else frozenset(aud or [])
    if client_id not in aud_set:
        raise IdentityError(
            "aud_mismatch",
            f"aud {sorted(aud_set)} does not contain this client_id {client_id!r}",
        )
    allowed = frozenset({client_id}) | frozenset(trusted_audiences)
    extra = aud_set - allowed
    if extra:
        raise IdentityError(
            "untrusted_aud",
            f"aud carries untrusted extra audience(s) {sorted(extra)} — RFC 8725: reject a "
            "token minted for another audience unless it is explicitly whitelisted",
        )

    exp = claims.get("exp")
    if exp is None:
        raise IdentityError("missing_exp", "no 'exp' claim — a token with no expiry is refused")
    if now_epoch > int(exp) + leeway:
        raise IdentityError(
            "expired",
            f"token expired at {int(exp)}, now {now_epoch} (leeway {leeway}s)",
        )

    nbf = claims.get("nbf")
    if nbf is not None and now_epoch < int(nbf) - leeway:
        raise IdentityError(
            "nbf_future",
            f"token not-before {int(nbf)} is in the future (now {now_epoch}, leeway {leeway}s)",
        )

    if require_email_verified and claims.get("email_verified") is not True:
        raise IdentityError(
            "email_unverified",
            "email_verified is not exactly true — the email claim is unproven and refused",
        )
    return claims


def verify_signature(token: str, *, expected_alg: str, hs256_key: bytes | None = None) -> bool:
    """Verify a JWT's signature. Returns True on success; raises IdentityError
    (with a stable reason) otherwise.

    RFC 8725 hardening:
      * `alg: none` (or an empty alg) is REJECTED — an unsigned token is never
        trusted (reason `alg_none`).
      * The token's header `alg` MUST equal the adapter-pinned `expected_alg`.
        This blocks algorithm-confusion in BOTH directions — an HS256 adapter
        handed an RS256 header, or an RS256 adapter handed an HS256 header — the
        classic attack where a public key is abused as an HMAC secret
        (reason `alg_confusion`).

    HS256 is verified in-process with the stdlib (constant-time compare).
    RS256 / ES256 / PS256 (+ JWKS) require asymmetric crypto the stdlib lacks:
    that path uses the OPTIONAL PyJWT dependency and, when PyJWT is absent,
    REFUSES LOUDLY (reason `pyjwt_absent`) — it NEVER downgrades to a pass.
    """
    header, _ = decode_jwt_unverified(token)
    alg = str(header.get("alg", "")).strip()

    if alg == "" or alg.lower() == "none":
        raise IdentityError(
            "alg_none",
            "RFC 8725: 'alg: none' (an unsigned token) is rejected — signature is mandatory",
        )
    if alg != expected_alg:
        raise IdentityError(
            "alg_confusion",
            f"RFC 8725: token alg {alg!r} != adapter-pinned {expected_alg!r} — "
            "algorithm-confusion rejected (a key for one alg must never verify another)",
        )

    parts = token.split(".")
    if expected_alg == "HS256":
        if not hs256_key:
            raise IdentityError(
                "no_key",
                "HS256 verification requires a shared secret (supply it from an env-var-sourced "
                "value; never a literal in source)",
            )
        signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")
        expected_sig = hmac.new(_as_bytes(hs256_key), signing_input, hashlib.sha256).digest()
        try:
            actual_sig = _b64url_decode(parts[2])
        except Exception as exc:  # noqa: BLE001
            raise IdentityError("bad_signature", f"signature segment is not base64url: {exc}") from exc
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise IdentityError(
                "bad_signature",
                "HMAC-SHA256 signature mismatch — token was tampered with or signed with a different key",
            )
        return True

    if expected_alg in _ASYMMETRIC_ALGS:
        import importlib.util

        # OPTIONAL dep: PyJWT is used ONLY for asymmetric/JWKS crypto. If it is
        # absent we REFUSE — never a silent downgrade to an unverified pass.
        if importlib.util.find_spec("jwt") is None:
            raise IdentityError(
                "pyjwt_absent",
                f"REFUSING: {expected_alg} verification needs asymmetric crypto via PyJWT, which is "
                "NOT installed. This validator will NOT silently downgrade to an unverified pass. "
                "Install `PyJWT[crypto]` and supply the issuer JWKS, or use HS256 with a shared "
                "secret from a secret store.",
            )
        # PyJWT present: real verification. Signature-only here — claim checks stay
        # in validate_claims. The public key / JWKS client is the consumer's wiring.
        raise IdentityError(
            "pyjwt_wiring_required",
            f"{expected_alg} path is available (PyJWT present) but needs the consumer's JWKS/public "
            "key wiring; pass a resolved key to a PyJWT-backed adapter. The plugin ships the seam, "
            "not the issuer's key material.",
        )

    raise IdentityError("unsupported_alg", f"unsupported alg {expected_alg!r}")


def _as_bytes(value) -> bytes:
    return value if isinstance(value, (bytes, bytearray)) else str(value).encode("utf-8")


def extract_roles(claims: dict, claim_path: str) -> frozenset:
    """Resolve role claims from a CONFIGURABLE path — NOT a display string.

    Handles the three shapes real IdPs emit:
      * Entra ID           -> a top-level `roles` array           (claim_path="roles")
      * Okta / Auth0       -> a namespaced literal key, e.g.
                              "https://myapp.example.com/roles"    (literal top-level key)
      * Keycloak           -> a nested path
                              "resource_access.myclient.roles"     (dotted traversal)
    A literal top-level key wins over dotted traversal, so a namespaced Auth0 key
    (which itself contains dots and slashes) is not mis-parsed as a path.
    """
    if claim_path in claims:
        val = claims[claim_path]
    else:
        val = claims
        for part in claim_path.split("."):
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                val = None
                break
    if val is None:
        return frozenset()
    if isinstance(val, str):
        return frozenset(val.split())
    if isinstance(val, (list, tuple, set)):
        return frozenset(str(v) for v in val)
    return frozenset()


# --------------------------------------------------------------------------- #
# The adapter seam
# --------------------------------------------------------------------------- #
class IdentityAdapter:
    """The seam: resolve a caller's assertion into a VerifiedIdentity.

    Two concrete adapters ship: ConfigActorAdapter (today's behaviour,
    verified=False) and OidcJwtAdapter (an IdP-issued ID token, verified=True
    only after signature + claim validation). A consumer can add a third (e.g. a
    PyJWT/JWKS-backed RS256 adapter) behind the same `resolve` contract.
    """

    tier = "abstract"

    def resolve(self, *args, **kwargs) -> VerifiedIdentity:  # pragma: no cover - abstract
        raise NotImplementedError


class ConfigActorAdapter(IdentityAdapter):
    """Today's `--actor` string + a LOCAL roles map. verified=False.

    Backward-compatible: the subject is `config:<actor>`, so SoD behaves exactly
    as `close_state.py` does today (distinct actor strings -> distinct subjects).
    The `config:` namespace guarantees a config subject can NEVER collide with a
    real `sub@iss`. Every identity it mints is badged "config-asserted UNVERIFIED".
    """

    tier = "config-asserted"

    def __init__(self, roles_map: dict | None = None) -> None:
        # actor -> list[str] of locally-declared roles (NOT an IdP grant).
        self.roles_map = roles_map or {}

    def resolve(self, actor: str) -> VerifiedIdentity:  # type: ignore[override]
        if not actor or not str(actor).strip():
            raise IdentityError("missing_actor", "--actor is required for the config-asserted adapter")
        return VerifiedIdentity(
            subject=f"config:{actor}",
            email=None,
            roles=frozenset(self.roles_map.get(actor, [])),
            issuer="config-asserted",
            verified=False,
            token_fingerprint="n/a-unverified",
            display=actor,
        )


class OidcJwtAdapter(IdentityAdapter):
    """An IdP-issued OIDC ID token -> a VERIFIED identity.

    resolve() runs verify_signature THEN validate_claims (both must pass) and
    only then mints a VerifiedIdentity(verified=True) whose subject is `sub@iss`
    and whose roles come from the configured claim path. Signature verification
    is HS256 (stdlib) or, for asymmetric algs, the refuse-loudly PyJWT path.
    """

    tier = "idp-verified"

    def __init__(
        self,
        *,
        issuer: str,
        client_id: str,
        expected_alg: str = "HS256",
        hs256_key: bytes | None = None,
        roles_claim_path: str = "roles",
        trusted_audiences: frozenset = frozenset(),
        leeway: int = 60,
        require_email_verified: bool = True,
    ) -> None:
        self.issuer = issuer
        self.client_id = client_id
        self.expected_alg = expected_alg
        self.hs256_key = hs256_key
        self.roles_claim_path = roles_claim_path
        self.trusted_audiences = frozenset(trusted_audiences)
        self.leeway = leeway
        self.require_email_verified = require_email_verified

    def resolve(self, id_token: str, *, now_epoch: int, display: str | None = None) -> VerifiedIdentity:  # type: ignore[override]
        # 1. Cryptographic half — raises on alg:none, alg-confusion, bad sig, or
        #    a refused asymmetric-without-PyJWT path.
        verify_signature(id_token, expected_alg=self.expected_alg, hs256_key=self.hs256_key)
        # 2. Pure claim half — raises with a specific reason on the first failure.
        _, payload = decode_jwt_unverified(id_token)
        validate_claims(
            payload,
            issuer=self.issuer,
            client_id=self.client_id,
            now_epoch=now_epoch,
            leeway=self.leeway,
            trusted_audiences=self.trusted_audiences,
            require_email_verified=self.require_email_verified,
        )
        # 3. Both halves passed -> a verified identity anchored on sub@iss.
        return VerifiedIdentity(
            subject=f"{payload['sub']}@{payload['iss']}",
            email=payload.get("email"),
            roles=extract_roles(payload, self.roles_claim_path),
            issuer=str(payload["iss"]),
            verified=True,
            token_fingerprint=hashlib.sha256(id_token.encode("utf-8")).hexdigest()[:16],
            display=display,
        )


# --------------------------------------------------------------------------- #
# Role-based segregation of duties (keyed on subject + role claims)
# --------------------------------------------------------------------------- #
def assert_sod(
    preparer: VerifiedIdentity,
    approver: VerifiedIdentity,
    *,
    amount: float,
    threshold: float,
    approver_role: str = DEFAULT_APPROVER_ROLE,
) -> None:
    """Enforce preparer != approver on the STABLE SUBJECT (sub@iss), plus a
    role-claim gate on the approver. Raises IdentityError on violation.

    Two independent refusals:
      sod_same_subject  the approver's `sub@iss` equals the preparer's and the
        amount is at/above threshold. This keys on subject, NOT the display
        string — so a renamed `--actor` on the SAME token CANNOT launder a
        self-approval, even if that token also carries the approver role.
      sod_missing_role  the approver's role claims (from the configured claim
        path) do not include `approver_role`.
    """
    if preparer.subject == approver.subject and amount >= threshold:
        raise IdentityError(
            "sod_same_subject",
            f"SoD: approver subject {approver.subject!r} is the preparer and amount "
            f"{amount:,.2f} >= threshold {threshold:,.2f}; a display-name change does not "
            "create a second principal — a distinct approver is required",
        )
    if approver_role not in approver.roles:
        raise IdentityError(
            "sod_missing_role",
            f"SoD: approver {approver.subject!r} lacks the required role {approver_role!r} "
            f"(present roles: {sorted(approver.roles)})",
        )


def assert_fresh_stepup(
    stepup_token: str | None,
    *,
    approver: VerifiedIdentity,
    adapter: OidcJwtAdapter,
    now_epoch: int,
    max_age_seconds: int = DEFAULT_STEPUP_MAX_AGE_SECONDS,
    leeway: int = 60,
) -> VerifiedIdentity:
    """A LOCK mutates the audit surface, so it demands a FRESH, VERIFIED, SUBJECT-BOUND
    step-up re-auth token — NOT a raw claims dict and NOT the same session token used to
    approve. Raises IdentityError; on success returns the verified step-up identity.

    Hardening over the earlier raw-dict version (the reviewer's step-up finding):
      * (a) The step-up MUST be a real token that passes BOTH halves of trust —
        `verify_signature` + `validate_claims`, run here via `adapter.resolve` — before any
        freshness math. A caller can no longer hand in a hand-built `{"auth_time": ...}` dict.
      * (b) SUBJECT BINDING: the step-up's `sub@iss` MUST equal the LOCKING approver's
        `sub@iss`. A fresh re-auth from a *different* principal cannot authorize this LOCK.
      * (c) An iat-only step-up (no `auth_time`) is a WEAKER signal — it proves issuance, not
        a re-authentication moment — and is REFUSED for a LOCK rather than accepted as
        equivalent to a real step-up. Freshness is measured ONLY against `auth_time`.

    Reason codes:
      stepup_absent           no step-up token was presented
      stepup_unverified       no verified approver to bind to, or the token did not verify
      (verify/claim reasons)  adapter.resolve raises the specific cause on a bad token
      stepup_subject_mismatch the step-up sub@iss != the locking approver's sub@iss
      stepup_no_authtime      the token has no auth_time (iat-only) — refused for a LOCK
      stepup_stale            the re-auth is older than max_age_seconds
      stepup_future           the re-auth timestamp is implausibly in the future
    """
    if stepup_token is None or not isinstance(stepup_token, str) or not stepup_token.strip():
        # A raw claims dict (the old, now-refused calling convention) is NOT a token and
        # lands here — a LOCK step-up must be a real, verifiable compact JWS.
        raise IdentityError(
            "stepup_absent",
            "LOCK requires a FRESH step-up re-authentication TOKEN (a compact JWS, not a raw "
            "claims dict); none was presented",
        )
    if approver is None or not getattr(approver, "verified", False):
        raise IdentityError(
            "stepup_unverified",
            "LOCK requires a signature+claim-VERIFIED approver identity to bind the step-up to",
        )
    # (a) BOTH halves of trust — verify_signature THEN validate_claims — before any freshness
    #     math. adapter.resolve raises the specific verify/claim reason on a bad token.
    stepup_ident = adapter.resolve(stepup_token, now_epoch=now_epoch)
    if not stepup_ident.verified:
        raise IdentityError("stepup_unverified", "step-up token did not verify")
    # (b) Subject binding: the re-auth MUST belong to the principal that is locking.
    if stepup_ident.subject != approver.subject:
        raise IdentityError(
            "stepup_subject_mismatch",
            f"step-up subject {stepup_ident.subject!r} != locking approver {approver.subject!r} — "
            "a re-authentication from a different principal cannot authorize this LOCK",
        )
    # (c) Freshness measured ONLY against auth_time. An iat-only token is issuance time, not a
    #     re-auth moment — refuse it for a LOCK rather than silently downgrading.
    _, payload = decode_jwt_unverified(stepup_token)
    auth_time = payload.get("auth_time")
    if auth_time is None:
        raise IdentityError(
            "stepup_no_authtime",
            "step-up token has no auth_time — an iat-only token proves issuance, not a fresh "
            "re-authentication; a LOCK demands a genuine step-up (auth_time), so it is refused",
        )
    age = now_epoch - int(auth_time)
    if age > max_age_seconds:
        raise IdentityError(
            "stepup_stale",
            f"step-up re-auth is {age}s old (> {max_age_seconds}s) — re-authenticate to LOCK",
        )
    if age < -leeway:
        raise IdentityError(
            "stepup_future",
            f"step-up auth_time is {-age}s in the future — clock skew or a forged timestamp",
        )
    return stepup_ident


# --------------------------------------------------------------------------- #
# Tamper-RESISTANT tier (reference interfaces only — consumer infrastructure)
# --------------------------------------------------------------------------- #
class DetachedSigner:
    """SEAM for a per-event DETACHED signature whose key lives OFF-BOX.

    A consumer implements this against an HSM / KMS / cloud signing service so
    the key that signs each audit event is one the operator running the close
    cannot read. That is what turns the hash chain from tamper-EVIDENT into
    tamper-RESISTANT. The plugin ships ONLY the interface — it cannot ship key
    custody. Do not subclass this with a local-key signer and call it resistant.
    """

    available = False

    def sign(self, digest: bytes) -> str:  # pragma: no cover - interface
        raise NotImplementedError(
            "DetachedSigner is a consumer seam: wire an HSM/KMS signer whose key is off-box"
        )


class WormSink:
    """SEAM for a WRITE-ONCE-READ-MANY audit sink.

    A consumer implements this against an immutable store (S3 Object Lock, Azure
    immutable blob, a QLDB-style ledger) so a retroactive edit is PREVENTED, not
    merely detected. The plugin ships ONLY the interface — a local file is not
    WORM, and the reference no-op below refuses to pretend otherwise.
    """

    available = False

    def append(self, record: dict) -> None:  # pragma: no cover - interface
        raise NotImplementedError(
            "WormSink is a consumer seam: wire an immutable/WORM store; a local file is NOT WORM"
        )


def tamper_tier_report(signer: DetachedSigner | None, sink: WormSink | None) -> dict:
    """Honest, non-overclaiming statement of which tamper tier is actually wired."""
    has_signer = bool(signer and getattr(signer, "available", False))
    has_sink = bool(sink and getattr(sink, "available", False))
    if has_signer and has_sink:
        tier = "tamper-resistant (consumer off-box key + WORM sink wired)"
    elif has_signer or has_sink:
        tier = "partial — one of {off-box signer, WORM sink} wired; NOT yet tamper-resistant"
    else:
        tier = "tamper-evident only — hash chain detects edits; no off-box key, no WORM sink"
    return {
        "detached_signer_wired": has_signer,
        "worm_sink_wired": has_sink,
        "tier": tier,
        "caveat": "tamper-resistant requires CONSUMER infrastructure (off-box key custody + an "
                  "immutable/WORM store + a distinct IdP role assignment); the plugin enforces the "
                  "CHECK and validates the token, it does not ship key custody or an immutable store",
    }


# --------------------------------------------------------------------------- #
# CLI — a thin, env-var-secret-only surface for the wiring runbook
# --------------------------------------------------------------------------- #
def _load_roles_map(path: str | None) -> dict:
    if not path:
        return {}
    with open(path) as fh:
        return json.load(fh)


def _hs256_key_from_env(env_name: str | None) -> bytes | None:
    """Resolve the HS256 secret from an env-var NAME (never a literal argument)."""
    if not env_name:
        return None
    val = os.environ.get(env_name)
    if val is None:
        raise IdentityError("no_key", f"env var {env_name!r} is not set (supply the HS256 secret there)")
    return val.encode("utf-8")


def _now_epoch(explicit: str | None) -> int:
    if explicit is not None:
        return int(explicit)
    env = os.environ.get("RAVEN_NOW_EPOCH")
    if env:
        return int(env)
    from datetime import datetime, timezone
    return int(datetime.now(timezone.utc).timestamp())


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="IdentityAdapter seam for the close: config-asserted -> IdP-verified identity.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("inspect-config", help="resolve a config-asserted actor (verified=False)")
    c.add_argument("--actor", required=True)
    c.add_argument("--roles-map", help="path to a JSON {actor: [roles]} map")

    v = sub.add_parser("verify-token", help="verify + validate an OIDC ID token -> a verified identity")
    v.add_argument("--id-token", required=True, help="the compact JWS to validate")
    v.add_argument("--issuer", required=True)
    v.add_argument("--client-id", required=True)
    v.add_argument("--alg", default="HS256", help="the ONE alg this adapter accepts (default HS256)")
    v.add_argument("--hs256-secret-env", help="NAME of the env var holding the HS256 secret")
    v.add_argument("--roles-claim-path", default="roles")
    v.add_argument("--now-epoch", help="epoch-seconds override for deterministic runs")

    t = sub.add_parser("tamper-tier", help="print which tamper tier is wired (evident vs resistant)")
    t.add_argument("--worm", action="store_true", help="simulate a WORM sink being wired")
    t.add_argument("--signer", action="store_true", help="simulate an off-box signer being wired")

    a = p.parse_args(argv)
    try:
        if a.cmd == "inspect-config":
            ident = ConfigActorAdapter(_load_roles_map(a.roles_map)).resolve(a.actor)
            print(json.dumps(ident.as_dict(), indent=2))
        elif a.cmd == "verify-token":
            adapter = OidcJwtAdapter(
                issuer=a.issuer,
                client_id=a.client_id,
                expected_alg=a.alg,
                hs256_key=_hs256_key_from_env(a.hs256_secret_env),
                roles_claim_path=a.roles_claim_path,
            )
            ident = adapter.resolve(a.id_token, now_epoch=_now_epoch(a.now_epoch))
            print(json.dumps(ident.as_dict(), indent=2))
        elif a.cmd == "tamper-tier":
            signer = DetachedSigner() if a.signer else None
            if signer is not None:
                object.__setattr__(signer, "available", True)
            sink = WormSink() if a.worm else None
            if sink is not None:
                object.__setattr__(sink, "available", True)
            print(json.dumps(tamper_tier_report(signer, sink), indent=2))
    except IdentityError as exc:
        sys.stderr.write(f"REFUSED {exc}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

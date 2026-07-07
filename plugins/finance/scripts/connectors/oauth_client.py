#!/usr/bin/env python3
"""oauth_client.py - a REFERENCE-IMPLEMENTATION OAuth2 token client for finance GL
connectors (QBO / NetSuite / Sage Intacct / Xero), built around the one failure mode
that actually costs a controller a close: a DROPPED ROTATING REFRESH TOKEN.

WHAT THIS IS (and is NOT). This is a *reference implementation* of the token-lifecycle
disciplines the connector-facts doc mandates (../../knowledge/finance-elt-connector-facts.md):
the atomic persist-then-use ordering, the per-entity lock, and the error-cause routing.
It is NOT a live-verified integration: no live credentials are used, no live socket is
opened here, and every provider descriptor's numeric lifetime/limit is TRAINING KNOWLEDGE
carried from that (settling-gated) doc, NOT verified this session. Live wiring — the real
IdP, real client credentials, the real token endpoint, a real warehouse to land into — is
the CONSUMER's step. Outputs are decision-support scaffolding, not an accounting/audit/tax
opinion and not a certified connector (../../CLAUDE.md sec.3).

THE CENTRAL INVARIANT (persist-then-use). For QBO and Xero the refresh token ROTATES on
every refresh: a successful refresh returns a NEW refresh token and invalidates the old
one. If we obtain the new pair, USE the access token, then crash before persisting the new
refresh token, we are locked out — the old refresh token is already dead. So this client
ALWAYS persists the new token pair ATOMICALLY (temp file + os.replace) BEFORE the new
access token is used. Consequence of atomicity:
  * a crash AFTER os.replace  -> the NEW token is durable on disk (recoverable);
  * a crash DURING the write (before os.replace) -> the OLD token is left fully intact.
Either way there is never a half-written token store and never a silent lockout.

Other disciplines enforced here:
  * PER-ENTITY EXCLUSIVE LOCK (fcntl.flock) around the read-refresh-write critical section,
    so two concurrent refreshes on the same entity can't each rotate and invalidate the
    other (a self-inflicted lockout). A recheck-under-lock collapses a racing pair to ONE
    rotation.
  * ERROR-CAUSE ROUTING. The cause selects the fix; the actions are NOT interchangeable:
      - 401 (expired access token)      -> REFRESH_RETRY  (refresh, retry the SAME route)
      - 429 (throttled)                 -> BACKOFF_RETRY  (honor Retry-After, then retry)
      - 400 invalid_grant (dead refresh)-> REAUTH_REQUIRED (NON-retryable; fire alert hook;
                                            never backoff — it needs an interactive re-auth)
  * XERO 30-MIN GRACE. A refresh whose response is lost (timeout, no response) leaves us
    unsure whether the server rotated. Within the provider grace window we retry with the
    EXISTING refresh token (Xero keeps the prior token valid for ~30 min), rather than
    assuming a rotation we never saw.

SECURITY. Token VALUES are never logged (only fixed labels / lengths). The token store is
written 0600. Credentials are referenced by ENV-VAR NAME only in the accompanying config
template; this module receives already-resolved values from its caller and does not read
the environment itself. This file is a security_review target — see test_connectors.py.

Stdlib only (json/os/sys/fcntl/time/argparse/hashlib). Python 3.8+.
"""
from __future__ import annotations

import base64
import fcntl
import json
import os
import time

# --- Error-cause routing actions (distinct constants; the cause selects the fix) --------
OK = "ok"
REFRESH_RETRY = "refresh_and_retry_same_route"   # 401 expired access token
BACKOFF_RETRY = "backoff_honor_retry_after"      # 429 / 5xx
REAUTH_REQUIRED = "reauth_required_non_retryable"  # 400 invalid_grant -> dead refresh token
NON_RETRYABLE = "non_retryable"                  # other 4xx


# --- Providers as DATA (endpoints + flow flags carried from the connector-facts doc) ----
# NUMBERS ARE TRAINING KNOWLEDGE / settling-gated — verify against the cited primary doc
# before they gate a live build. The SHAPE (rotation exists; PKCE; grace) is the durable
# fact; the numeric lifetimes drift.
PROVIDERS = {
    "qbo": {
        "auth_flow": "authorization_code",
        "pkce": False,
        "rotating_refresh": True,          # QBO refresh token rotates on (nearly) every refresh
        "grace_seconds": 0,                # QBO documents no rotation grace window
        "token_url": "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
        "authorize_url": "https://appcenter.intuit.com/connect/oauth2",
        "tenant_field": "realmId",
    },
    "xero": {
        "auth_flow": "authorization_code",
        "pkce": True,                      # Xero uses auth-code + PKCE
        "rotating_refresh": True,          # Xero refresh token rotates on every refresh
        "grace_seconds": 1800,             # ~30-min grace: prior refresh token stays valid
        "token_url": "https://identity.xero.com/connect/token",
        "authorize_url": "https://login.xero.com/identity/connect/authorize",
        "tenant_field": "xero_tenant_id",
    },
    "netsuite": {
        "auth_flow": "authorization_code",
        "pkce": False,
        "rotating_refresh": False,         # NetSuite OAuth2 refresh token is not use-rotating
        "grace_seconds": 0,
        "token_url": "https://<account>.suitetalk.api.netsuite.com/services/rest/auth/oauth2/v1/token",
        "authorize_url": "https://<account>.app.netsuite.com/app/login/oauth2/authorize.nl",
        "tenant_field": "netsuite_account_id",
    },
    # NetSuite OAuth 2.0 machine-to-machine (client-credentials + a certificate-signed JWT
    # ASSERTION). This is the PRIMARY go-forward path: Token-Based Auth (OAuth 1.0a) can no
    # longer CREATE new integrations from NetSuite 2027.1 [Oracle "Preparing for TBA End of
    # Support", retrieved 2026-07-07 — settling-gated]. The critical shape difference: M2M has
    # NO refresh token — a fresh access token is minted each time by re-signing a short-lived
    # JWT with the private key whose public cert is registered in NetSuite. So the rotating-
    # refresh disciplines above are INERT here; the real NetSuite failure modes are private-key
    # custody (kept OFF this process's argv — see build_jwt_assertion) and assertion exp/clock
    # skew. `jwt_assertion: True` selects the client_credentials mint path in get_access_token().
    "netsuite_m2m": {
        "auth_flow": "client_credentials",
        "jwt_assertion": True,
        "pkce": False,
        "rotating_refresh": False,         # M2M has no refresh token at all — nothing rotates
        "grace_seconds": 0,
        "token_url": "https://<account>.suitetalk.api.netsuite.com/services/rest/auth/oauth2/v1/token",
        "authorize_url": None,             # no interactive authorize step for M2M
        "tenant_field": "netsuite_account_id",
    },
    "intacct": {
        "auth_flow": "authorization_code",
        "pkce": False,
        "rotating_refresh": False,         # Intacct classic is session-based; REST OAuth2 non-rotating
        "grace_seconds": 0,
        "token_url": "https://api.intacct.com/ia/api/v1/oauth2/token",
        "authorize_url": "https://api.intacct.com/ia/api/v1/oauth2/authorize",
        "tenant_field": "intacct_company_id",
    },
}


# --- Exceptions --------------------------------------------------------------------------
class TransportTimeout(Exception):
    """The token endpoint did not respond (lost response). Distinct from an HTTP error."""


class ReauthRequired(Exception):
    """The refresh token is dead (invalid_grant). NON-retryable — needs interactive re-auth."""


class TokenRefreshError(Exception):
    """A non-retryable refresh failure that is not specifically a dead-token re-auth case."""


class SimulatedCrash(Exception):
    """Test-only: raised by _atomic_persist(crash_after_tmp=True) to model a mid-write crash."""


class SignerUnavailable(Exception):
    """The M2M path needs an asymmetric (RS256/PS256) signer that the stdlib cannot provide,
    and none was injected. Raised LOUDLY (never a silent no-op) — mirrors close_identity.py's
    refuse-loudly discipline for the optional-PyJWT asymmetric path."""


# --- M2M client-assertion (RS256/PS256 JWT) via an INJECTED signer seam -------------------
# The shipped core stays stdlib-only: it base64url-assembles the JWT and delegates the ONE
# operation the stdlib can't do — the asymmetric signature — to an injected
# `signer(signing_input: bytes) -> bytes`. The default signer REFUSES LOUDLY, so a consumer
# who hasn't wired real crypto gets a clear error, never a silently-unsigned token. A working
# reference signer (optional PyJWT, key read from a 0600 FILE, never argv) ships in
# netsuite_signer.py. This is the same seam pattern as close_identity.py's IdentityAdapter.
def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def refuse_loudly_signer(signing_input: bytes) -> bytes:
    raise SignerUnavailable(
        "REFUSING: NetSuite M2M needs an RS256/PS256 signature the Python stdlib cannot "
        "produce, and no signer was injected. Wire netsuite_signer.py (optional PyJWT[crypto] "
        "+ your private key from a 0600 file) or pass signer= to OAuthClient. The plugin ships "
        "the seam; you supply the key — key custody stays OFF this process (never on argv)."
    )


def build_jwt_assertion(client_id: str, token_url: str, kid: str, scope: str,
                        signer, *, clock=time.time, alg: str = "PS256",
                        ttl_seconds: int = 3000, nonce=None) -> str:
    """Assemble a signed client-assertion JWT (RFC 7523) for NetSuite M2M. Header carries the
    cert `kid`; claims are iss=client_id, scope, aud=token_url, short iat/exp, and a unique jti
    (anti-replay). The signature is produced by the INJECTED signer over `header.claims`."""
    now = int(clock())
    header = {"alg": alg, "typ": "JWT", "kid": kid}
    claims = {
        "iss": client_id,
        "scope": scope,
        "aud": token_url,
        "iat": now,
        "exp": now + int(ttl_seconds),
        "jti": nonce or os.urandom(16).hex(),
    }
    signing_input = (
        _b64url(json.dumps(header, separators=(",", ":")).encode())
        + "."
        + _b64url(json.dumps(claims, separators=(",", ":")).encode())
    )
    signature = signer(signing_input.encode("ascii"))
    return signing_input + "." + _b64url(signature)


# --- Error-cause routing -----------------------------------------------------------------
def classify_error(status: int, body: dict | None) -> str:
    """Map (HTTP status, body) to a routing action. The cause selects the fix; the three
    diagnostic causes 401 / 429 / invalid_grant deliberately produce THREE distinct actions."""
    body = body or {}
    err = str(body.get("error") or "").strip().lower()
    if status == 200:
        return OK
    if status == 401:
        return REFRESH_RETRY
    if status == 429:
        return BACKOFF_RETRY
    if status == 400 and err == "invalid_grant":
        return REAUTH_REQUIRED
    if status >= 500:
        return BACKOFF_RETRY
    return NON_RETRYABLE


def honor_retry_after(headers: dict | None, attempt: int, base: float = 1.0,
                      cap: float = 60.0) -> float:
    """Backoff seconds for a 429/5xx. If the server sent a Retry-After (delta-seconds),
    HONOR it; otherwise exponential base*2**attempt, capped. Never negative."""
    headers = headers or {}
    ra = headers.get("Retry-After") or headers.get("retry-after")
    if ra is not None:
        try:
            return max(0.0, float(str(ra).strip()))
        except ValueError:
            pass
    return min(cap, base * (2 ** max(0, attempt)))


# --- Atomic, 0600, persist-then-use token store ------------------------------------------
def _atomic_persist(path: str, tokens: dict, *, crash_after_tmp: bool = False) -> None:
    """Persist the token pair ATOMICALLY: write a temp file, fsync, then os.replace().
    A crash BEFORE os.replace() leaves the existing store untouched (old token intact);
    a crash AFTER leaves the new token durable. `crash_after_tmp` is a TEST hook that
    raises SimulatedCrash after the temp write but before the rename, to exercise the
    mid-write path deterministically (never used in production)."""
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    tmp = path + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(tokens, fh)
            fh.flush()
            os.fsync(fh.fileno())
    except Exception:
        # best-effort cleanup of the temp; the live store is still untouched
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    if crash_after_tmp:
        # Model a crash mid-write: temp exists, but the rename never happened, so the
        # live store still holds the OLD token. (Leave the tmp; a real crash would too.)
        raise SimulatedCrash("crash after temp write, before os.replace() — old token intact")
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _read_store(path: str) -> dict:
    try:
        with open(path) as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


class _EntityLock:
    """Per-entity exclusive advisory lock (fcntl.flock) on a sidecar lockfile. Independent
    open file descriptions contend even within one process, so this serializes concurrent
    refreshes on the same entity to one-at-a-time (Linux flock semantics)."""

    def __init__(self, lock_path: str):
        self._lock_path = lock_path
        self._fd = None

    def __enter__(self):
        parent = os.path.dirname(os.path.abspath(self._lock_path))
        os.makedirs(parent, exist_ok=True)
        self._fd = os.open(self._lock_path, os.O_WRONLY | os.O_CREAT, 0o600)
        fcntl.flock(self._fd, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        try:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
        finally:
            os.close(self._fd)
            self._fd = None
        return False


class OAuthClient:
    """Token-lifecycle manager for ONE entity of ONE provider.

    The caller injects a `transport` (the HTTP seam) so this is testable and never opens a
    socket itself. The transport must expose:
        token_request(url, data) -> TokenResponse(status, body, headers)   (may raise TransportTimeout)
    and, for the demonstrable persist-then-use ordering, optionally record its calls into
    the shared `events` list.
    """

    def __init__(self, provider: str, store_path: str, transport, *,
                 clock=time.time, alert_hook=None, events=None, skew_seconds: int = 60,
                 signer=None, assertion=None):
        if provider not in PROVIDERS:
            raise ValueError(f"unknown provider {provider!r}; known: {sorted(PROVIDERS)}")
        self.provider = provider
        self.p = PROVIDERS[provider]
        self.store_path = store_path
        self.lock_path = store_path + ".lock"
        self.transport = transport
        self.clock = clock
        self.alert_hook = alert_hook
        self.events = events if events is not None else []
        self.skew = skew_seconds
        # M2M (client-credentials) seam: `signer(signing_input)->bytes` (defaults to the
        # refuse-loudly signer) and `assertion` config {client_id, cert_id(kid), scope, alg}.
        self.signer = signer or refuse_loudly_signer
        self.assertion = assertion

    # -- helpers ---------------------------------------------------------------------------
    def _expired(self, tok: dict) -> bool:
        if not tok or "access_token" not in tok:
            return True
        exp = tok.get("expires_at")
        if exp is None:
            return True
        return self.clock() >= (float(exp) - self.skew)

    def _alert(self, kind: str) -> None:
        # Fire the alert hook WITHOUT leaking any token value.
        if self.alert_hook is not None:
            self.alert_hook({"provider": self.provider, "store": self.store_path, "kind": kind})

    def _refresh_payload(self, refresh_token: str) -> dict:
        return {"grant_type": "refresh_token", "refresh_token": refresh_token,
                "provider": self.provider}

    def _tokens_from_body(self, body: dict, prior_refresh: str) -> dict:
        # rotating providers return a new refresh token; non-rotating keep the prior one.
        new_refresh = body.get("refresh_token") if self.p["rotating_refresh"] else None
        return {
            "access_token": body["access_token"],
            "refresh_token": new_refresh or body.get("refresh_token") or prior_refresh,
            "expires_at": self.clock() + float(body.get("expires_in", 3600)),
            "obtained_at": self.clock(),
        }

    # -- the refresh critical section (assumes the entity lock is HELD) --------------------
    def _refresh_locked(self, cur: dict) -> dict:
        prior_refresh = cur.get("refresh_token")
        if not prior_refresh:
            self._alert("no_refresh_token")
            raise ReauthRequired(f"{self.provider}: no refresh token on file — re-auth required")
        url = self.p["token_url"]
        payload = self._refresh_payload(prior_refresh)
        try:
            resp = self.transport.token_request(url, payload)
        except TransportTimeout:
            # Lost response. Within the provider grace window, retry with the EXISTING
            # refresh token (it may still be valid, e.g. Xero's ~30-min grace); otherwise
            # surface the timeout — we must not assume a rotation we never observed.
            if self.p["grace_seconds"] > 0:
                resp = self.transport.token_request(url, self._refresh_payload(prior_refresh))
            else:
                raise
        action = classify_error(resp.status, resp.body)
        if action == REAUTH_REQUIRED:
            self._alert("invalid_grant")          # fire alert; NON-retryable; never backoff
            raise ReauthRequired(f"{self.provider}: invalid_grant — refresh token is dead, re-auth required")
        if action != OK:
            raise TokenRefreshError(f"{self.provider}: refresh failed status={resp.status} action={action}")
        new = self._tokens_from_body(resp.body, prior_refresh)
        # PERSIST-THEN-USE: durable, atomic write BEFORE the new access token is handed out.
        _atomic_persist(self.store_path, new)
        self.events.append(("persist", self.provider))
        return new

    # -- the M2M mint critical section (assumes the entity lock is HELD) --------------------
    def _client_credentials_locked(self, cur: dict) -> dict:
        """Mint an access token via OAuth2 client-credentials + a certificate-signed JWT
        ASSERTION. No refresh token is involved (M2M has none) — we re-sign a short-lived
        assertion each time the access token expires. `invalid_grant` here means a bad/expired
        cert-to-role mapping, not a dead refresh token: it is still NON-retryable + alerts."""
        if not self.assertion:
            self._alert("no_assertion_config")
            raise TokenRefreshError(
                f"{self.provider}: M2M requires assertion config {{client_id, cert_id, scope}} — "
                "none supplied. Pass assertion= to OAuthClient."
            )
        url = self.p["token_url"]
        jwt = build_jwt_assertion(
            client_id=self.assertion["client_id"],
            token_url=url,
            kid=self.assertion["cert_id"],
            scope=self.assertion.get("scope", "rest_webservices"),
            signer=self.signer,
            clock=self.clock,
            alg=self.assertion.get("alg", "PS256"),
        )
        payload = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jwt,
            "provider": self.provider,   # replay keying
        }
        resp = self.transport.token_request(url, payload)
        action = classify_error(resp.status, resp.body)
        if action == REAUTH_REQUIRED:
            self._alert("invalid_grant")   # bad cert/role mapping; NON-retryable; never backoff
            raise ReauthRequired(
                f"{self.provider}: invalid_grant — the cert-to-role mapping is bad or expired; "
                "re-upload the certificate / re-map the integration in NetSuite."
            )
        if action != OK:
            raise TokenRefreshError(f"{self.provider}: M2M mint failed status={resp.status} action={action}")
        new = self._tokens_from_body(resp.body, None)   # no prior refresh token for M2M
        _atomic_persist(self.store_path, new)
        self.events.append(("persist", self.provider))
        return new

    def _mint_locked(self, cur: dict) -> dict:
        """Dispatch to the right token-acquisition path for this provider's auth flow."""
        if self.p.get("auth_flow") == "client_credentials":
            return self._client_credentials_locked(cur)
        return self._refresh_locked(cur)

    # -- public API ------------------------------------------------------------------------
    def refresh(self) -> dict:
        """Force a token acquisition under the per-entity lock. Persists atomically before
        returning. Refresh-token flow for auth-code providers; a fresh assertion mint for M2M."""
        with _EntityLock(self.lock_path):
            cur = _read_store(self.store_path)
            return self._mint_locked(cur)

    def get_access_token(self) -> str:
        """Return a valid access token, acquiring under the lock only if needed. Two racing
        callers collapse to ONE acquisition via the recheck-under-lock."""
        cur = _read_store(self.store_path)
        if not self._expired(cur):
            return cur["access_token"]
        with _EntityLock(self.lock_path):
            cur = _read_store(self.store_path)      # recheck under lock
            if not self._expired(cur):
                return cur["access_token"]          # someone else already acquired
            new = self._mint_locked(cur)
            return new["access_token"]

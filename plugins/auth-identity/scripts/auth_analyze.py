#!/usr/bin/env python3
"""auth_analyze.py — a zero-dependency auth/identity static analyzer.

Removes guesswork from three recurring authentication-review tasks an
auth-architect / auth-implementation-engineer runs constantly. Every mode is a
read-only INSPECTOR — it parses what you paste in and reports findings; it does
NOT verify signatures, call a provider, or make a network request.

  jwt        Decode a JWT WITHOUT verifying its signature and report claim-level
             findings: alg=none, missing/!verified-here exp/iat/nbf, expiry
             distance (an over-long-lived access token is a finding), missing
             iss/aud/sub, and HS256-on-what-looks-like-a-public-client. Decode is
             for INSPECTION only — the server must still verify the signature
             against the issuer JWKS (CLAUDE.md house opinion #5).

  scopes     Compare REQUESTED OAuth scopes against the MINIMUM a stated feature
             needs and flag over-broad / sensitive scopes (Gmail/Drive/Calendar/
             admin/offline_access) requested "just in case" — least-privilege
             (CLAUDE.md house opinion #6).

  cookie     Lint a Set-Cookie header (or a flag list) for a SESSION cookie:
             HttpOnly, Secure, SameSite, and a token-in-a-JS-readable-cookie
             smell — the never-store-tokens-in-localStorage / CSRF-defense rules
             (CLAUDE.md §3).

This is an ANALYZER, not a verifier and not a data source. It reads only what you
paste; outputs are decision-support. Stdlib only (argparse, base64, json, re,
sys, time); runs anywhere Python 3.9+ is present.

IMPORTANT: a clean report here is NOT a security sign-off. Every concrete auth /
secret / token change still routes through `ravenclaude-core/security-reviewer`
(CLAUDE.md §8). Volatile facts (provider scope names, recommended token TTLs)
carry `[verify-at-use]` markers — confirm against the provider before acting.

Examples
--------
  # Decode + lint a JWT (no signature check). Treat it as a public-client access token:
  python3 auth_analyze.py jwt --token "eyJhbG..." --client-type public --kind access

  # Least-privilege scope check: feature only needs sign-in, but these were requested:
  python3 auth_analyze.py scopes --feature sso \\
      --requested "openid email profile https://www.googleapis.com/auth/gmail.readonly"

  # Session-cookie flag lint:
  python3 auth_analyze.py cookie \\
      --set-cookie "sid=abc; Path=/; Max-Age=3600; SameSite=Lax"
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import time

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2

# Recommended access-token lifetime ceiling, in seconds, above which an access
# token is flagged as over-long-lived. 15 minutes is a common short-lived target;
# refresh tokens (not access tokens) carry the long-lived role. [verify-at-use]
ACCESS_TOKEN_MAX_TTL_SECONDS = 15 * 60

# OAuth scopes that are sensitive / broad enough to warrant an explicit
# justification when requested. Names are provider-specific and volatile —
# [verify-at-use] against the provider's current scope catalog.
SENSITIVE_SCOPE_PATTERNS = (
    r"gmail",
    r"drive",
    r"calendar",
    r"contacts",
    r"\.admin",
    r"directory",
    r"cloud-platform",
    r"offline_access",
    r"\boffline\b",
    r"\.full",
    r"\.write\b",
    r"user:.*repo",
)

# The minimum scope set various common features actually need. Used by the
# `scopes` mode to flag anything requested beyond the floor for the feature.
FEATURE_MIN_SCOPES = {
    "sso": {"openid", "email", "profile"},
    "signin": {"openid", "email", "profile"},
    "profile": {"openid", "profile"},
    "email": {"openid", "email"},
    "openid": {"openid"},
}


class Finding:
    """A single analyzer finding with a severity and a human-readable message."""

    def __init__(self, severity: str, message: str) -> None:
        self.severity = severity  # "high" | "medium" | "low" | "info"
        self.message = message

    def render(self) -> str:
        mark = {"high": "[HIGH]", "medium": "[MED ]", "low": "[LOW ]", "info": "[INFO]"}
        return f"  {mark.get(self.severity, '[????]')} {self.message}"


def _b64url_decode(segment: str) -> bytes:
    """Decode a base64url segment, tolerating missing padding."""
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _decode_jwt_unverified(token: str) -> tuple[dict, dict]:
    """Split and base64url-decode a JWT's header + payload WITHOUT verifying it.

    Raises ValueError if the token is not a well-formed three-part JWT.
    """
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise ValueError(
            f"not a three-part JWT (found {len(parts)} segment(s) split on '.')"
        )
    try:
        header = json.loads(_b64url_decode(parts[0]))
        payload = json.loads(_b64url_decode(parts[1]))
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not base64url/JSON decode a segment: {exc}") from exc
    if not isinstance(header, dict) or not isinstance(payload, dict):
        raise ValueError("header and payload must both decode to JSON objects")
    return header, payload


def analyze_jwt(token: str, client_type: str, kind: str) -> list[Finding]:
    """Lint a decoded-but-unverified JWT and return findings."""
    findings: list[Finding] = []
    header, payload = _decode_jwt_unverified(token)

    alg = str(header.get("alg", "")).lower()
    if alg in ("none", ""):
        findings.append(
            Finding("high", f"alg={header.get('alg')!r} — an unsigned/none-alg token is forgeable; reject it.")
        )
    if alg.startswith("hs") and client_type == "public":
        findings.append(
            Finding(
                "high",
                f"alg={header.get('alg')} (HMAC) on a PUBLIC client — the shared secret "
                "cannot be kept from a browser/mobile client; prefer RS256/ES256 (asymmetric).",
            )
        )

    now = int(time.time())
    exp = payload.get("exp")
    iat = payload.get("iat")

    if exp is None:
        findings.append(Finding("high", "no `exp` claim — a token with no expiry never dies; require one."))
    else:
        try:
            exp_int = int(exp)
            if exp_int <= now:
                findings.append(Finding("medium", f"`exp` is in the past ({exp_int}) — this token is already expired."))
            ttl = exp_int - (int(iat) if iat is not None else now)
            if kind == "access" and ttl > ACCESS_TOKEN_MAX_TTL_SECONDS:
                findings.append(
                    Finding(
                        "medium",
                        f"access-token lifetime ~{ttl}s exceeds the {ACCESS_TOKEN_MAX_TTL_SECONDS}s "
                        "short-lived target [verify-at-use] — long-lived access tokens widen the "
                        "blast radius of a leak; keep access short and rotate refresh tokens.",
                    )
                )
        except (TypeError, ValueError):
            findings.append(Finding("medium", f"`exp` is not an integer timestamp ({exp!r})."))

    for claim in ("iss", "aud", "sub"):
        if claim not in payload:
            sev = "medium" if claim in ("iss", "aud") else "low"
            findings.append(
                Finding(sev, f"no `{claim}` claim — server-side validation checks iss/aud/exp (and sub identifies the subject).")
            )

    findings.append(
        Finding(
            "info",
            "REMINDER: this decode did NOT verify the signature. The server MUST verify against the "
            "issuer JWKS and check iss/aud/exp/nonce before trusting any claim (CLAUDE.md house opinion #5).",
        )
    )
    return findings


def _scope_is_sensitive(scope: str) -> bool:
    return any(re.search(p, scope, re.IGNORECASE) for p in SENSITIVE_SCOPE_PATTERNS)


def analyze_scopes(feature: str, requested: list[str]) -> list[Finding]:
    """Compare requested scopes against the feature minimum + flag sensitive ones."""
    findings: list[Finding] = []
    requested_set = {s.strip() for s in requested if s.strip()}

    minimum = FEATURE_MIN_SCOPES.get(feature.lower())
    if minimum is None:
        findings.append(
            Finding(
                "info",
                f"feature {feature!r} is not in the known floor map "
                f"({', '.join(sorted(FEATURE_MIN_SCOPES))}); reporting sensitive-scope flags only.",
            )
        )
    else:
        over = requested_set - minimum
        missing = minimum - requested_set
        if missing:
            findings.append(
                Finding("low", f"feature {feature!r} usually needs {sorted(minimum)}; not requested: {sorted(missing)}.")
            )
        for scope in sorted(over):
            sev = "high" if _scope_is_sensitive(scope) else "medium"
            findings.append(
                Finding(
                    sev,
                    f"scope {scope!r} is beyond the minimum for {feature!r} — request only what the "
                    "feature needs (least privilege); broad scopes trigger provider verification, scare "
                    "users on the consent screen, and widen a token leak's blast radius.",
                )
            )

    for scope in sorted(requested_set):
        if _scope_is_sensitive(scope) and (minimum is None or scope not in minimum):
            findings.append(
                Finding(
                    "high",
                    f"scope {scope!r} is a SENSITIVE/broad scope — justify it explicitly [verify-at-use the "
                    "exact provider scope name + whether it needs app verification].",
                )
            )

    if not findings:
        findings.append(Finding("info", "requested scopes are at or below the feature minimum — least-privilege looks clean."))
    return findings


def _parse_cookie_flags(set_cookie: str) -> tuple[str, dict]:
    """Parse a Set-Cookie value into (name, flag-map). Flags are lowercased keys."""
    segments = [s.strip() for s in set_cookie.split(";") if s.strip()]
    name = ""
    flags: dict = {}
    if segments:
        first = segments[0]
        name = first.split("=", 1)[0].strip()
    for seg in segments[1:]:
        if "=" in seg:
            k, v = seg.split("=", 1)
            flags[k.strip().lower()] = v.strip()
        else:
            flags[seg.strip().lower()] = True
    return name, flags


def analyze_cookie(set_cookie: str) -> list[Finding]:
    """Lint a Set-Cookie header for the session-cookie security flags."""
    findings: list[Finding] = []
    name, flags = _parse_cookie_flags(set_cookie)

    if "httponly" not in flags:
        findings.append(
            Finding("high", f"cookie {name!r} has no HttpOnly — JS can read it, so a single XSS discloses it; set HttpOnly for session/refresh cookies.")
        )
    if "secure" not in flags:
        findings.append(Finding("high", f"cookie {name!r} has no Secure — it can ride a plaintext HTTP request; set Secure."))

    samesite = str(flags.get("samesite", "")).lower()
    if not samesite:
        findings.append(
            Finding("medium", f"cookie {name!r} has no SameSite — add SameSite=Lax/Strict and an anti-CSRF token on writes (CLAUDE.md §3 #4).")
        )
    elif samesite == "none" and "secure" not in flags:
        findings.append(Finding("high", f"cookie {name!r} is SameSite=None without Secure — browsers reject this; SameSite=None requires Secure."))

    looks_like_token = bool(re.search(r"(token|jwt|access|refresh|bearer)", name, re.IGNORECASE))
    if looks_like_token and "httponly" not in flags:
        findings.append(
            Finding("high", f"cookie {name!r} looks token-bearing and is JS-readable — keep tokens out of JS-readable storage (memory + HttpOnly cookie pattern).")
        )

    if not findings:
        findings.append(Finding("info", f"cookie {name!r}: HttpOnly + Secure + SameSite present — session-cookie flags look clean."))
    return findings


def _print_report(title: str, findings: list[Finding]) -> int:
    print(title)
    for f in findings:
        print(f.render())
    has_actionable = any(f.severity in ("high", "medium") for f in findings)
    print()
    if has_actionable:
        print("Route concrete auth/token/secret changes through ravenclaude-core/security-reviewer (CLAUDE.md §8).")
        return EXIT_FINDINGS
    print("No high/medium findings. (A clean report is not a security sign-off.)")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auth_analyze.py",
        description="Zero-dependency auth/identity static analyzer (jwt | scopes | cookie). Read-only; never verifies signatures or calls a provider.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    p_jwt = sub.add_parser("jwt", help="Decode (UNVERIFIED) + lint a JWT's claims.")
    p_jwt.add_argument("--token", required=True, help="The JWT (header.payload.signature).")
    p_jwt.add_argument("--client-type", choices=("public", "confidential"), default="confidential", help="public=SPA/mobile, confidential=server.")
    p_jwt.add_argument("--kind", choices=("access", "id", "refresh"), default="access", help="Token kind (affects the TTL check).")

    p_scopes = sub.add_parser("scopes", help="Least-privilege check of requested OAuth scopes.")
    p_scopes.add_argument("--feature", required=True, help=f"What the login is for ({', '.join(sorted(FEATURE_MIN_SCOPES))}, or any label).")
    p_scopes.add_argument("--requested", required=True, help="Space- or comma-separated requested scopes.")

    p_cookie = sub.add_parser("cookie", help="Lint a Set-Cookie header for session-cookie flags.")
    p_cookie.add_argument("--set-cookie", required=True, help="A Set-Cookie value, e.g. 'sid=abc; Secure; HttpOnly; SameSite=Lax'.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.mode == "jwt":
        try:
            findings = analyze_jwt(args.token, args.client_type, args.kind)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return EXIT_USAGE
        return _print_report(f"JWT analysis ({args.kind} token, {args.client_type} client) — UNVERIFIED decode:", findings)

    if args.mode == "scopes":
        requested = re.split(r"[,\s]+", args.requested.strip())
        findings = analyze_scopes(args.feature, requested)
        return _print_report(f"OAuth scope analysis (feature={args.feature!r}):", findings)

    if args.mode == "cookie":
        findings = analyze_cookie(args.set_cookie)
        return _print_report("Set-Cookie session-flag analysis:", findings)

    parser.error(f"unknown mode {args.mode!r}")
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())

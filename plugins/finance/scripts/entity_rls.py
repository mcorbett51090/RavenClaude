#!/usr/bin/env python3
"""entity_rls.py - the allowed_entities[] ARRAY-claim resolver (deny-all by default).

WHY THIS EXISTS (the finance delta). data-platform's multi-tenant model scopes a
viewer to a SCALAR `tenant_id` claim. A corporate controller does not fit that shape:
one controller owns a PORTFOLIO of legal entities (a shared-services / outsourced-
close arrangement — "you close entities A, C and F; not B"). Modelling that as a
single tenant_id would either over-grant (one tenant = the whole group) or force a
row per (viewer, entity) mapping outside the token. So the finance embed token
carries an ARRAY claim, `allowed_entities`, and the load-bearing question becomes an
intersection: of the entities a request ASKS for, which is the viewer actually
entitled to? Everything else denies.

THE INVARIANT THIS FILE PROVES (and the test pins):
  resolve(requested, allowed) = requested ∩ allowed, and
    - allowed empty / missing            -> []  (deny-all)
    - Bob (allowed {C}) requests {A, B}  -> []  (no overlap: total denial)
    - partial overlap {A,B,C} ∩ {B,C}    -> [B, C]  (only the granted survive)
  resolve_from_claim additionally FAILS CLOSED on the token envelope:
    - missing allowed_entities claim     -> []
    - expired (now >= exp)               -> []
    - not-yet-valid (now < iat)          -> []
    - ttl > 30 min (exp - iat)           -> []  (mirrors jwt-embed-issuance's
                                                 >30-minute embed-token anti-pattern)

HONEST SCOPE / TIER CAVEAT — READ THIS. This is a REFERENCE resolver, not a live-
verified authorization system. It performs the array-claim intersection and the
token-envelope checks; it does NOT verify a JWT SIGNATURE, bind `allowed_entities` to
an authenticated identity, or enforce anything at the database. Signature verification
+ claim issuance is the host app's job (data-platform `jwt-embed-issuance`); the
actual row cut is the warehouse's job (the Postgres FORCE-RLS policy / Cube
`access_policy` under `skills/warehouse-dashboard/models/`, which are specified, not
executed here). The resolver is the *policy decision* the enforcement layers must
also make — a second, testable place the deny-all invariant is written down, never
the only place. Decision-support / reference implementation; a real deployment needs
an IdP, a warehouse, real credentials, and `ravenclaude-core/security-reviewer`
sign-off (../CLAUDE.md sec.3, sec.10). Stdlib only (argparse/json/sys). Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# VerifiedIdentity comes from the SAME verified token the SoD check keys on. Importing it
# here (rather than re-deriving a second identity) is the whole point of the split-brain
# binding: entity entitlement and SoD identity MUST derive from ONE verified token/issuer.
# See bind_entitlement_to_identity below.
from close_identity import VerifiedIdentity  # noqa: E402

# Max embed-token lifetime. Mirrors data-platform jwt-embed-issuance: a token with
# exp - iat > 30 min is an anti-pattern (stateless revocation gets impractical), so
# here it fails closed to deny-all rather than being honored.
MAX_TTL_SECONDS = 30 * 60


def _norm(x) -> str:
    return str(x).strip()


def resolve(requested_entities, allowed_entities) -> list:
    """Pure intersection: the requested entities the viewer is actually granted.

    Order follows `requested` (stable, deduped). Deny-all ([]) when `allowed` is
    empty/None — an empty grant can never widen to a permit. This is the tested
    proof-of-invariant core; it makes NO trust decision about where `allowed` came
    from — see resolve_from_claim for the token-envelope checks.
    """
    # TYPE GUARD (fail closed). A non-collection passed as `allowed` — most dangerously a
    # bare string — would iterate CHAR-BY-CHAR ({_norm(a) for a in "ABC"} -> {'A','B','C'}),
    # silently fabricating a per-character grant. Anything that is not a list/tuple/set (or
    # frozenset) denies all. Same guard for `requested`: a string request would likewise be
    # exploded into single characters, so it too fails closed to no overlap.
    if not isinstance(allowed_entities, (list, tuple, set, frozenset)):
        return []
    if not isinstance(requested_entities, (list, tuple, set, frozenset)):
        return []
    if not allowed_entities:
        return []
    allowed = {_norm(a) for a in allowed_entities if _norm(a)}
    if not allowed:
        return []
    out, seen = [], set()
    for r in requested_entities or []:
        rn = _norm(r)
        if rn and rn in allowed and rn not in seen:
            seen.add(rn)
            out.append(rn)
    return out


def _is_num(x) -> bool:
    # bool is an int subclass; a boolean iat/exp is malformed, so exclude it.
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate_claim(claim, now) -> tuple:
    """Check the token envelope. Fail-closed: returns (False, reason) on any problem.

    `now` is unix seconds (int/float). Any failure means resolve_from_claim denies
    ALL entities — the safe default when a token is missing, malformed, or stale.
    """
    if not isinstance(claim, dict):
        return False, "claim is missing or not an object"
    allowed = claim.get("allowed_entities")
    if allowed is None:
        return False, "missing allowed_entities claim"
    if not isinstance(allowed, list):
        return False, "allowed_entities must be an array (a controller owns a portfolio)"
    iat, exp = claim.get("iat"), claim.get("exp")
    if not _is_num(iat) or not _is_num(exp):
        return False, "missing or non-numeric iat / exp"
    if not _is_num(now):
        return False, "evaluation time 'now' is missing or non-numeric"
    if now >= exp:
        return False, "token expired (now >= exp)"
    if now < iat:
        return False, "token not yet valid (now < iat)"
    if exp - iat > MAX_TTL_SECONDS:
        return False, (
            f"ttl {exp - iat:.0f}s exceeds max {MAX_TTL_SECONDS}s "
            f"(>30-min embed-token anti-pattern)"
        )
    return True, "ok"


def resolve_from_claim(claim, requested_entities, now) -> tuple:
    """Validate the token envelope, then intersect. Returns (granted_list, reason).

    Deny-all ([]) on ANY envelope failure — this is where expired / missing-claim /
    over-long-ttl collapse to zero entities.
    """
    ok, reason = validate_claim(claim, now)
    if not ok:
        return [], reason
    return resolve(requested_entities, claim.get("allowed_entities")), "ok"


def bind_entitlement_to_identity(entity_claims: dict, identity: VerifiedIdentity, now) -> tuple:
    """Bind the warehouse entitlement token (allowed_entities[]) to the SoD-verified IDENTITY.

    `now` is unix seconds (int/float) — the entitlement token's envelope (iat/exp/ttl) is
    validated against it via validate_claim, mirroring resolve_from_claim, so an EXPIRED
    entitlement replayed alongside a freshly-verified identity of the same iss/sub cannot be
    honored. The bind path is NOT blind to token freshness.

    THE SPLIT-BRAIN THIS CLOSES (the critic's + reviewer's core finding). This resolver and
    close_identity's SoD check answer two different questions off two potentially DIFFERENT
    tokens: "which entities may this request see?" (the warehouse embed token's
    allowed_entities[]) and "who is this principal, and may they approve?" (the OIDC identity
    token's sub@iss + roles). If those two tokens come from different issuers/subjects, a
    viewer could carry entity entitlement for one principal while the close is approved under
    another — a split identity. This function forces them to be ONE verified principal from
    ONE issuer before any entitlement is honored.

    Contract. Returns (granted_allowed_entities, reason). Fails CLOSED — returns [] with a
    'split-brain: ...' reason — when:
      * `identity` is missing or NOT verified (verified=True requires signature+claim checks);
        an unverified identity can never anchor an entitlement.
      * the entitlement token carries no iss/sub, so it cannot be bound at all.
      * entity_claims['iss'] != identity.issuer (different issuer minted the two tokens).
      * f"{entity_claims['sub']}@{entity_claims['iss']}" != identity.subject (same issuer but a
        DIFFERENT principal — a sub swap).
      * the entitlement token's envelope fails validate_claim(entity_claims, now) —
        expired (now >= exp), not-yet-valid (now < iat), missing/non-numeric iat/exp, or
        ttl > 30 min. An expired entitlement is never honored, even for a matched identity.
    On a full match it returns the resolved (normalized, deduped) allowed_entities; an empty
    grant still denies all. INVARIANT: entity entitlement and SoD identity MUST derive from the
    SAME verified token/issuer.
    """
    if identity is None or not getattr(identity, "verified", False):
        return [], (
            "split-brain: identity is unverified — an entitlement can only bind to a "
            "signature+claim-verified identity (both must derive from one token)"
        )
    if not isinstance(entity_claims, dict):
        return [], "split-brain: entitlement claim is missing or not an object"
    ent_iss = entity_claims.get("iss")
    ent_sub = entity_claims.get("sub")
    if not ent_iss or not ent_sub:
        return [], (
            "split-brain: entitlement token missing iss/sub — cannot bind it to the "
            "verified identity"
        )
    # 1. SAME issuer that minted the verified identity (exact match, no drift).
    if ent_iss != identity.issuer:
        return [], (
            f"split-brain: entitlement token issuer {ent_iss!r} != identity token issuer "
            f"{identity.issuer!r} — entitlement and SoD identity must share one issuer"
        )
    # 2. SAME principal (sub@iss) — not a different sub on the same issuer.
    ent_subject = f"{ent_sub}@{ent_iss}"
    if ent_subject != identity.subject:
        return [], (
            f"split-brain: entitlement token subject {ent_subject!r} != identity subject "
            f"{identity.subject!r} — entitlement and SoD identity must be one principal"
        )
    # 3. The entitlement token's envelope must be fresh — mirror resolve_from_claim's
    #    fail-closed checks (iat/exp/ttl) so an EXPIRED entitlement replayed alongside a
    #    freshly-verified identity of the same iss/sub cannot be honored. The bind path
    #    must not be blind to token freshness (parity with resolve_from_claim).
    env_ok, env_reason = validate_claim(entity_claims, now)
    if not env_ok:
        return [], (
            f"split-brain: entitlement token envelope invalid ({env_reason}) — "
            "an expired/invalid entitlement cannot bind even to a matched identity"
        )
    # Bound: the entitlement provably belongs to the verified identity. Resolve (normalize +
    # dedup) the grant through the same guarded intersection; an empty grant denies all.
    allowed = entity_claims.get("allowed_entities")
    granted = resolve(allowed, allowed)
    if not granted:
        return [], (
            "bound to identity, but the entitlement grants no entities "
            "(empty/invalid allowed_entities -> deny-all)"
        )
    return granted, "ok — entitlement bound to the verified identity (one issuer, one subject)"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Resolve an allowed_entities[] array claim against a request "
        "(deny-all by default)."
    )
    p.add_argument("--claim", help="JSON file with the token claim (allowed_entities[], iat, exp)")
    p.add_argument(
        "--allowed",
        help="comma-separated allowed entity ids (alternative to --claim; skips envelope checks)",
    )
    p.add_argument("--requested", required=True, help="comma-separated requested entity ids")
    p.add_argument(
        "--now", type=float, help="evaluation time (unix seconds); required with --claim"
    )
    a = p.parse_args(argv)

    requested = [s for s in (a.requested or "").split(",") if s.strip()]

    if a.claim:
        if a.now is None:
            p.error("--now is required with --claim (to check iat/exp)")
        with open(a.claim) as fh:
            claim = json.load(fh)
        granted, reason = resolve_from_claim(claim, requested, a.now)
    elif a.allowed is not None:
        allowed = [s for s in a.allowed.split(",") if s.strip()]
        granted, reason = resolve(requested, allowed), "envelope not checked (--allowed)"
    else:
        p.error("provide either --claim (with --now) or --allowed")

    out = {"granted": granted, "denied": len(granted) == 0, "reason": reason}
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

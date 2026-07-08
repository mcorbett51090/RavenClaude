#!/usr/bin/env python3
"""test_close_identity.py - acceptance suite for the IdP-backed SoD seam.

Stdlib-only, zero-dependency runner (no pytest). Run:  python3 test_close_identity.py
Every token here is SELF-MINTED and SYNTHETIC — the HS256 secret is a fake local
constant, the issuers/subjects/emails are obviously-fake `example.com` values, and
no network, IdP, or real credential is touched. The suite proves the two halves of
token trust (claim validation and signature verification) refuse each specific
attack with its own reason code, and that role-based SoD + step-up freshness hold.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import close_identity as ci  # noqa: E402

# --- synthetic, obviously-fake test material (NOT a real secret) ------------ #
FAKE_HS256_SECRET = b"synthetic-test-secret-not-a-real-key-do-not-use"
ISS = "https://issuer.example.com/"
CLIENT_ID = "close-autopilot-client-0000"
NOW = 1_800_000_000  # fixed epoch for deterministic exp/nbf/freshness math

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


def _seg(obj) -> str:
    return base64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b"=").decode()


def mint(payload, *, alg="HS256", key=FAKE_HS256_SECRET, tamper_payload=False):
    """Self-mint a compact JWS. alg drives the header; for HS256 the signature is
    a real HMAC so verify_signature accepts it. tamper_payload flips a claim AFTER
    signing to model a payload-tampered copy."""
    header = _seg({"alg": alg, "typ": "JWT"})
    body = _seg(payload)
    signing_input = f"{header}.{body}".encode()
    sig = base64.urlsafe_b64encode(
        hmac.new(key, signing_input, hashlib.sha256).digest()
    ).rstrip(b"=").decode()
    if tamper_payload:
        bad = dict(payload)
        bad["email"] = "attacker@evil.example.com"
        body = _seg(bad)  # signature now covers the ORIGINAL body -> mismatch
    return f"{header}.{body}.{sig}"


def base_claims(**over):
    c = {
        "iss": ISS,
        "sub": "user-preparer-001",
        "aud": CLIENT_ID,
        "exp": NOW + 300,
        "nbf": NOW - 10,
        "iat": NOW - 10,
        "email": "preparer@example.com",
        "email_verified": True,
        "roles": ["finance.preparer"],
    }
    c.update(over)
    return c


def refused_with(fn, reason):
    """True iff fn() raises IdentityError with the expected reason code."""
    try:
        fn()
    except ci.IdentityError as exc:
        return exc.reason == reason
    except Exception:
        return False
    return False


def main():
    print("validate_claims — each attack refused with its SPECIFIC reason")
    kw = {"issuer": ISS, "client_id": CLIENT_ID, "now_epoch": NOW}
    check("valid claims pass", ci.validate_claims(base_claims(), **kw) is not None)
    check("expired -> reason 'expired'",
          refused_with(lambda: ci.validate_claims(base_claims(exp=NOW - 1000), **kw), "expired"))
    check("aud miss -> reason 'aud_mismatch'",
          refused_with(lambda: ci.validate_claims(base_claims(aud="some-other-client"), **kw), "aud_mismatch"))
    check("iss drift -> reason 'iss_mismatch'",
          refused_with(lambda: ci.validate_claims(base_claims(iss="https://issuer.example.com.evil.com/"), **kw),
                       "iss_mismatch"))
    check("nbf future -> reason 'nbf_future'",
          refused_with(lambda: ci.validate_claims(base_claims(nbf=NOW + 5000), **kw), "nbf_future"))
    check("missing sub -> reason 'missing_sub'",
          refused_with(lambda: ci.validate_claims(base_claims(sub=""), **kw), "missing_sub"))
    check("email_verified false -> reason 'email_unverified'",
          refused_with(lambda: ci.validate_claims(base_claims(email_verified=False), **kw), "email_unverified"))
    check("untrusted extra aud -> reason 'untrusted_aud'",
          refused_with(lambda: ci.validate_claims(base_claims(aud=[CLIENT_ID, "unexpected-aud"]), **kw),
                       "untrusted_aud"))
    check("extra aud ALLOWED when whitelisted",
          ci.validate_claims(base_claims(aud=[CLIENT_ID, "sister-app"]),
                             trusted_audiences=frozenset({"sister-app"}), **kw) is not None)

    print("verify_signature — crypto half (HS256 stdlib + RFC 8725 hardening)")
    good = mint(base_claims())
    check("correctly-signed HS256 accepted",
          ci.verify_signature(good, expected_alg="HS256", hs256_key=FAKE_HS256_SECRET) is True)
    tampered = mint(base_claims(), tamper_payload=True)
    check("payload-tampered copy -> reason 'bad_signature'",
          refused_with(lambda: ci.verify_signature(tampered, expected_alg="HS256", hs256_key=FAKE_HS256_SECRET),
                       "bad_signature"))
    wrong_key = mint(base_claims(), key=b"a-different-wrong-secret")
    check("wrong-key signature -> reason 'bad_signature'",
          refused_with(lambda: ci.verify_signature(wrong_key, expected_alg="HS256", hs256_key=FAKE_HS256_SECRET),
                       "bad_signature"))
    none_tok = mint(base_claims(), alg="none")
    check("alg:none -> reason 'alg_none'",
          refused_with(lambda: ci.verify_signature(none_tok, expected_alg="HS256", hs256_key=FAKE_HS256_SECRET),
                       "alg_none"))
    # alg-confusion, both directions:
    rs_header_tok = mint(base_claims(), alg="RS256")  # header says RS256...
    check("HS256 adapter given RS256 header -> reason 'alg_confusion'",
          refused_with(lambda: ci.verify_signature(rs_header_tok, expected_alg="HS256", hs256_key=FAKE_HS256_SECRET),
                       "alg_confusion"))
    hs_header_tok = mint(base_claims(), alg="HS256")  # header says HS256...
    check("RS256 adapter given HS256 header -> reason 'alg_confusion'",
          refused_with(lambda: ci.verify_signature(hs_header_tok, expected_alg="RS256"), "alg_confusion"))

    print("PyJWT-absent asymmetric path — REFUSES LOUDLY (never a pass)")
    have_pyjwt = True
    try:
        import jwt  # noqa: F401
    except ImportError:
        have_pyjwt = False
    rs_matched = mint(base_claims(), alg="RS256")  # header alg matches adapter -> reaches the PyJWT gate
    if not have_pyjwt:
        check("RS256 with PyJWT absent -> reason 'pyjwt_absent' (refused, NOT passed)",
              refused_with(lambda: ci.verify_signature(rs_matched, expected_alg="RS256"), "pyjwt_absent"))
    else:
        # PyJWT present in this env -> the seam still refuses without consumer JWKS wiring
        check("RS256 with PyJWT present -> refuses pending JWKS wiring (still never an unverified pass)",
              refused_with(lambda: ci.verify_signature(rs_matched, expected_alg="RS256"), "pyjwt_wiring_required"))

    print("OidcJwtAdapter.resolve — subject is sub@iss, verified=True end-to-end")
    adapter = ci.OidcJwtAdapter(issuer=ISS, client_id=CLIENT_ID, hs256_key=FAKE_HS256_SECRET)
    ident = adapter.resolve(good, now_epoch=NOW)
    check("resolved subject == sub@iss (not a display name)",
          ident.subject == f"user-preparer-001@{ISS}")
    check("resolved identity is verified + badged IdP-verified",
          ident.verified and ident.badge() == "IdP-verified")

    print("Role-based SoD — keyed on subject (sub@iss), NOT the display string")
    # Same token for preparer and approver => same sub@iss. Approver even carries
    # the approver role AND a different --actor display string. Must STILL refuse.
    approver_tok = mint(base_claims(roles=["finance.preparer", "finance.approver"]))
    prep = adapter.resolve(good, now_epoch=NOW, display="alice")
    appr_same_subject = adapter.resolve(approver_tok, now_epoch=NOW, display="totally-different-name")
    check("same sub@iss refused above threshold despite different --actor + approver role",
          refused_with(lambda: ci.assert_sod(prep, appr_same_subject, amount=250000, threshold=100000),
                       "sod_same_subject"))
    # A genuinely distinct approver principal with the approver role -> allowed.
    other_tok = mint(base_claims(sub="user-approver-999", email="approver@example.com",
                                 roles=["finance.approver"]))
    appr_distinct = adapter.resolve(other_tok, now_epoch=NOW, display="bob")
    ok = True
    try:
        ci.assert_sod(prep, appr_distinct, amount=250000, threshold=100000)
    except ci.IdentityError:
        ok = False
    check("distinct approver subject WITH approver role -> allowed", ok)
    # Distinct subject but MISSING the approver role -> refused on the role gate.
    norole_tok = mint(base_claims(sub="user-random-777", roles=["finance.preparer"]))
    appr_norole = adapter.resolve(norole_tok, now_epoch=NOW)
    check("distinct approver WITHOUT approver role -> reason 'sod_missing_role'",
          refused_with(lambda: ci.assert_sod(prep, appr_norole, amount=250000, threshold=100000),
                       "sod_missing_role"))

    print("LOCK step-up — VERIFIED + SUBJECT-BOUND + fresh auth_time (raw dict refused)")
    # The locking approver is the distinct approver principal resolved above (sub@iss).
    # A LOCK step-up must be a real token that (a) verifies, (b) belongs to THAT principal,
    # and (c) carries a fresh auth_time — an iat-only token is refused.
    APPR_SUB = "user-approver-999"
    step_fresh = mint(base_claims(sub=APPR_SUB, email="approver@example.com",
                                  roles=["finance.approver"], auth_time=NOW - 30))
    step_stale = mint(base_claims(sub=APPR_SUB, email="approver@example.com",
                                  roles=["finance.approver"], auth_time=NOW - 10_000))
    step_iatonly = mint(base_claims(sub=APPR_SUB, email="approver@example.com",
                                    roles=["finance.approver"]))  # no auth_time claim
    step_otherprincipal = mint(base_claims(sub="user-someone-else-123",
                                            email="other@example.com",
                                            roles=["finance.approver"], auth_time=NOW - 30))
    lock_kw = {"approver": appr_distinct, "adapter": adapter, "now_epoch": NOW}

    check("lock with NO step-up token -> reason 'stepup_absent'",
          refused_with(lambda: ci.assert_fresh_stepup(None, **lock_kw), "stepup_absent"))
    check("lock rejects a RAW CLAIMS DICT (must be a verified token, not a dict) -> 'stepup_absent'",
          refused_with(lambda: ci.assert_fresh_stepup({"auth_time": NOW - 30}, **lock_kw),
                       "stepup_absent"))
    check("lock with a STALE step-up (auth_time too old) -> reason 'stepup_stale'",
          refused_with(lambda: ci.assert_fresh_stepup(step_stale, **lock_kw), "stepup_stale"))
    check("lock with an iat-ONLY step-up (no auth_time) -> reason 'stepup_no_authtime' (WEAKER, refused)",
          refused_with(lambda: ci.assert_fresh_stepup(step_iatonly, **lock_kw), "stepup_no_authtime"))
    check("lock with a step-up from a DIFFERENT principal -> reason 'stepup_subject_mismatch'",
          refused_with(lambda: ci.assert_fresh_stepup(step_otherprincipal, **lock_kw),
                       "stepup_subject_mismatch"))
    unverified_appr = ci.ConfigActorAdapter({"carol": ["finance.approver"]}).resolve("carol")
    check("lock requires a VERIFIED approver identity to bind to -> reason 'stepup_unverified'",
          refused_with(lambda: ci.assert_fresh_stepup(
              step_fresh, approver=unverified_appr, adapter=adapter, now_epoch=NOW),
              "stepup_unverified"))
    fresh = True
    try:
        bound = ci.assert_fresh_stepup(step_fresh, **lock_kw)
    except ci.IdentityError:
        fresh = False
        bound = None
    check("lock with a FRESH, VERIFIED, SUBJECT-BOUND step-up -> allowed", fresh)
    check("returned step-up identity is the same locking principal (sub@iss bound)",
          bound is not None and bound.subject == appr_distinct.subject)

    print("Config adapter — backward-compatible, verified=False")
    cfg = ci.ConfigActorAdapter({"carol": ["finance.approver"]})
    cid = cfg.resolve("carol")
    check("config identity is UNVERIFIED + badged", (not cid.verified) and cid.badge() == "config-asserted UNVERIFIED")
    check("config subject namespaced 'config:carol' (never collides with sub@iss)",
          cid.subject == "config:carol")

    print("Tamper tier — honest, non-overclaiming report")
    rpt = ci.tamper_tier_report(None, None)
    check("no off-box signer + no WORM sink -> reports tamper-EVIDENT only",
          rpt["tier"].startswith("tamper-evident") and not rpt["detached_signer_wired"])

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""netsuite_signer.py - a REFERENCE signer for the NetSuite M2M client-assertion JWT.

This is the live-wiring counterpart to oauth_client.build_jwt_assertion's injected `signer`
seam. It implements `signer(signing_input: bytes) -> bytes` using the OPTIONAL PyJWT[crypto]
dependency (the same optional-asymmetric-crypto pattern as close_identity.py) and a private
key read from a FILE PATH (0600), NEVER from argv/env inline — key-on-argv is world-readable
via /proc/<pid>/cmdline, the exact custody anti-pattern close_identity.py forbids.

WHAT THIS IS (and is NOT). Reference implementation. The shipped connector core stays
stdlib-only and does not import this; a consumer wires it (or their own signer) for LIVE use.
PyJWT is refused LOUDLY when absent — never a silent unsigned token. The cert whose PUBLIC
half is uploaded to NetSuite is generated once by the consumer in THEIR shell:

    openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 730 \\
        -keyout netsuite-<entity>.key -out netsuite-<entity>.cert.pem

We DOCUMENT that command; we do not run it from this process with the key on argv. Upload the
.cert.pem in NetSuite (Setup > Integration > Manage Integrations > OAuth 2.0 > Certificate),
note the client_id + certificate id (the JWT `kid`), and keep the .key 0600 and off-box.

Stdlib for everything except the ONE asymmetric-sign call (optional PyJWT). Python 3.8+.
"""

from __future__ import annotations

import argparse
import os
import sys

# Supported JWT algs. The (algorithm-class, hash-class) selection is resolved lazily
# inside signer() so the optional PyJWT[crypto] import stays lazy — but the mapping is
# load-bearing: PS256/PS384 REQUIRE RSAPSSAlgorithm (RSASSA-PSS padding), RS256/RS384
# use RSAAlgorithm (RSASSA-PKCS1-v1_5). Using RSAAlgorithm for a PS-declared JWT emits
# a PKCS1v15 signature under a `PS256` header, which any compliant verifier (and
# NetSuite, which mandates PS256/ES256) rejects. And PyJWT's *Algorithm.sign calls
# self.hash_alg() — so the constructor takes a hashes CLASS, never a string.
_SUPPORTED_ALGS = ("PS256", "RS256", "PS384", "RS384")


class SignerConfigError(Exception):
    """The signer was misconfigured (missing/loose-permission key, unknown alg)."""


def make_signer(private_key_path: str, alg: str = "PS256"):
    """Return a `signer(signing_input: bytes) -> bytes` bound to a private key FILE. Imports
    PyJWT lazily and refuses loudly if absent. The key is read from disk each sign (so a
    rotated key is picked up) and is NEVER passed on a command line."""
    if alg not in _SUPPORTED_ALGS:
        raise SignerConfigError(f"unsupported alg {alg!r}; use one of {sorted(_SUPPORTED_ALGS)}")
    if not os.path.exists(private_key_path):
        raise SignerConfigError(f"private key not found at {private_key_path!r}")
    _warn_if_loose_perms(private_key_path)

    def signer(signing_input: bytes) -> bytes:
        try:
            from cryptography.hazmat.primitives import hashes
            from jwt.algorithms import RSAAlgorithm, RSAPSSAlgorithm  # optional dep (PyJWT[crypto])
        except ImportError as exc:
            raise SignerConfigError(
                "REFUSING: NetSuite M2M signing needs PyJWT[crypto], which is not installed. "
                "Install `PyJWT[crypto]` (or supply your own signer). The plugin ships the "
                "seam; you supply the key."
            ) from exc
        # alg -> (algorithm class, hash CLASS). PS* uses PSS padding; RS* uses PKCS1v15.
        # PyJWT's sign() does `self.hash_alg()`, so pass the hashes CLASS, not an instance.
        alg_class = {
            "PS256": RSAPSSAlgorithm,
            "PS384": RSAPSSAlgorithm,
            "RS256": RSAAlgorithm,
            "RS384": RSAAlgorithm,
        }[alg]
        hash_class = {
            "PS256": hashes.SHA256,
            "PS384": hashes.SHA384,
            "RS256": hashes.SHA256,
            "RS384": hashes.SHA384,
        }[alg]
        inst = alg_class(hash_class)
        with open(private_key_path, "rb") as fh:
            key = inst.prepare_key(fh.read())
        return inst.sign(signing_input, key)

    return signer


def _warn_if_loose_perms(path: str) -> None:
    try:
        mode = os.stat(path).st_mode & 0o077
        if mode:
            print(
                f"WARNING: {path} is group/world-accessible (mode ...{oct(mode)[-2:]}); "
                "a signing key must be 0600.",
                file=sys.stderr,
            )
    except OSError:
        pass


def _self_test() -> int:
    """Generate an ephemeral key in memory, sign + verify a round-trip. Proves the signer
    works on THIS host WITHOUT any NetSuite call. If PyJWT is absent, SKIP LOUDLY (rc 0 but a
    'NOT A PASS' banner) — a skip is not a pass (mirrors the Gate-10 actionlint discipline)."""
    try:
        import jwt.algorithms  # noqa: F401
    except ImportError:
        print(
            "SKIP (NOT A PASS): PyJWT[crypto] absent — the asymmetric sign/verify round-trip "
            "was NOT exercised. Install PyJWT[crypto] to actually verify the signer."
        )
        return 0
    import tempfile

    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from jwt.algorithms import RSAPSSAlgorithm

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    with tempfile.TemporaryDirectory() as d:
        kp = os.path.join(d, "k.pem")
        with open(os.open(kp, os.O_WRONLY | os.O_CREAT, 0o600), "wb") as fh:
            fh.write(pem)
        signer = make_signer(kp, "PS256")
        signing_input = b"header.claims"
        sig = signer(signing_input)
        # Verify with the SAME class/hash the signer used (RSASSA-PSS + SHA256). Using
        # RSAAlgorithm/PKCS1v15 here would silently pass a PKCS1v15 signature and let a
        # padding regression round-trip — the exact masking that hid the original bug.
        verifier = RSAPSSAlgorithm(hashes.SHA256)
        pub = verifier.prepare_key(
            key.public_key().public_bytes(
                serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
        ok = verifier.verify(signing_input, pub, sig)
    print(
        "PASS: ephemeral keygen -> sign -> verify round-trip OK"
        if ok
        else "FAIL: signature did not verify"
    )
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="NetSuite M2M reference signer")
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="ephemeral keygen + sign/verify round-trip (skips loudly if PyJWT absent)",
    )
    args = ap.parse_args(argv)
    if args.self_test:
        return _self_test()
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

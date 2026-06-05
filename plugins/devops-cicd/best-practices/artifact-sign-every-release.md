# Sign every release artifact and verify at deploy time

**Status:** Absolute rule
**Domain:** Artifact integrity / supply-chain security
**Applies to:** `devops-cicd`

---

## Why this exists

An unsigned artifact is indistinguishable from a tampered one. If your registry is compromised, or a CI cache is poisoned, the only thing standing between your prod cluster and malicious code is whether you can verify what you're deploying matches what you built. Signing is the technical implementation of "we know what we're running."

## How to apply

Use Sigstore (Cosign) for container images and Rekor for transparency-log inclusion. Generate SLSA provenance attestations from the build.

**Sign with Cosign (keyless, OIDC-based) in GitHub Actions:**

```yaml
- name: Sign image with Cosign
  uses: sigstore/cosign-installer@v3
  with:
    cosign-release: v2.2.4

- name: Sign the container image
  env:
    COSIGN_EXPERIMENTAL: "true"
  run: |
    cosign sign --yes \
      ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ steps.build.outputs.digest }}
```

**Verify before deploying (in a later job or at admission):**

```shell
cosign verify \
  --certificate-identity-regexp "https://github.com/myorg/myrepo" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  $REGISTRY/$IMAGE@$DIGEST
```

**Do:**
- Sign container images by digest (not tag) immediately after build.
- Verify signatures in the deploy job before any `kubectl apply` or Helm install.
- Attach an SBOM attestation alongside the signature: `cosign attest --predicate sbom.json`.
- Use a Kubernetes admission controller (Kyverno / OPA Gatekeeper) to enforce signature verification at runtime.

**Don't:**
- Sign by tag — tags are mutable and can be re-pointed to a different digest.
- Store signing keys as long-lived CI secrets when keyless (OIDC-based) signing is available.
- Skip verification in "fast" environments (staging) and verify only in prod — contamination flows downward.

## Edge cases / when the rule does NOT apply

Internal build artifacts that never leave a private registry and have no external consumers may use registry-native trust instead of Sigstore, but must document the trust boundary. Pure scripting artifacts (shell scripts) should at minimum use checksums and be served over TLS.

## See also

- [`../agents/build-and-artifact-engineer.md`](../agents/build-and-artifact-engineer.md) — owns SLSA attestation, SBOM generation, and artifact signing.
- [`./secure-oidc-not-static-keys.md`](./secure-oidc-not-static-keys.md) — keyless signing depends on OIDC federation; these two rules pair directly.

## Provenance

Codifies `build-and-artifact-engineer`'s ownership of "provenance/SLSA attestation" from CLAUDE.md §1, and cross-references the seam with `security-engineering` for verdict. Aligned with SLSA v1.0 specification and Sigstore project best practices.

---

_Last reviewed: 2026-06-05 by `claude`_

# Scan container images for CVEs in CI before pushing to the registry

**Status:** Absolute rule
**Domain:** Supply chain security / container security
**Applies to:** `security-engineering`

---

## Why this exists

A container image that reaches a production registry without a CVE scan may contain critical vulnerabilities in its base OS packages, language runtime, or installed libraries. Once pushed and deployed, remediating a high-severity CVE requires an emergency image rebuild and re-deploy. Catching it in CI — before the image enters the registry — keeps it out of the deployment pipeline and keeps production clean. The scan also produces the CVE baseline that the `supply-chain-security-engineer` uses for ongoing triage.

## How to apply

Run a container image scanner (Trivy, Grype, Snyk Container, or Docker Scout) in CI after the image is built and before it is pushed. Fail the pipeline on HIGH and CRITICAL findings with a known fix. Route findings without a fix to the async triage queue.

```yaml
# GitHub Actions: Trivy image scan before push
jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build container image
        run: docker build -t my-service:${{ github.sha }} .

      - name: Scan with Trivy
        # Pin to a full commit SHA, never a mutable tag/branch ref like @master or @v0.x.
        # In March 2026 (GHSA-69fq-xp46-6x23 / CVE-2026-33634) an attacker with compromised
        # maintainer credentials force-pushed 76 of 77 trivy-action version tags to a
        # credential-stealing payload — exactly the "trust a tag" pattern this example used
        # to teach. The SHA below is aquasecurity/trivy-action's v0.36.0 tag (current as of
        # 2026-09-23; re-verify before reusing: `git ls-remote --tags
        # https://github.com/aquasecurity/trivy-action.git`), which post-dates the compromise.
        uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0
        with:
          image-ref: my-service:${{ github.sha }}
          format: sarif
          output: trivy-results.sarif
          severity: HIGH,CRITICAL
          exit-code: '1'           # fail the job on HIGH/CRITICAL
          ignore-unfixed: true     # don't fail on CVEs with no fix yet

      - name: Upload SARIF results
        if: always()
        uses: github/codeql-action/upload-sarif@v4 # v3 is deprecated Dec 2026 (Node 20 EOL)
        with:
          sarif_file: trivy-results.sarif

      - name: Push to registry (only if scan passed)
        run: docker push ${{ env.REGISTRY }}/my-service:${{ github.sha }}
```

**Do:**
- Scan the final runtime image, not the build-stage image (different layers, different vulnerabilities).
- Set `ignore-unfixed: true` for the blocking gate — a CVE with no available fix is noise in the merge gate; route it to an async triage queue.
- Rebuild base images on a schedule (weekly) to pick up OS-level CVE patches even without code changes.
- Pair image scanning with SBOM generation — the scan results are most actionable when you know exactly what package version is affected.

**Don't:**
- Scan only the application layer — base image CVEs are equally real and often more exploitable.
- Block the pipeline on every LOW/MEDIUM finding without a fix; this creates noise and trains teams to ignore the gate.
- Skip scanning for "internal" or "dev" images — a compromised dev image can become a pivot point.

## Edge cases / when the rule does NOT apply

Scanning third-party images you don't control (external databases, proxies, sidecars) is still valuable but doesn't gate *your* build pipeline. File upgrade tickets and track them in the vulnerability queue.

## See also

- [`../agents/supply-chain-security-engineer.md`](../agents/supply-chain-security-engineer.md) — owns CVE triage and the patching strategy.
- [`./sbom-is-the-inventory.md`](./sbom-is-the-inventory.md) — generate the SBOM in the same pipeline step for queryable inventory.

## Provenance

Codifies Trivy and Grype CI integration patterns and the CISA Kubernetes Hardening Guide recommendation for image scanning before registry push. The SHA-pinning requirement above is drawn from GHSA-69fq-xp46-6x23 (aquasecurity/trivy, published 2026-03-21): a threat actor used compromised maintainer credentials to force-push malicious commits onto nearly every `trivy-action` and `setup-trivy` version tag, and the advisory's own remediation is "pin GitHub Actions to full, immutable commit SHA hashes, don't use mutable version tags." Treat any third-party scanner/security Action the same way — the scanner itself is supply chain, not exempt from it.

---

_Last reviewed: 2026-09-23 by `claude` (corrected `trivy-action`/`codeql-action` pinning per the 2026-09-23 weekly research sweep — see `CHANGELOG.md`)_

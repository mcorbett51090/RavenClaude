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
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: my-service:${{ github.sha }}
          format: sarif
          output: trivy-results.sarif
          severity: HIGH,CRITICAL
          exit-code: '1'           # fail the job on HIGH/CRITICAL
          ignore-unfixed: true     # don't fail on CVEs with no fix yet

      - name: Upload SARIF results
        if: always()
        uses: github/codeql-action/upload-sarif@v3
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

Codifies Trivy and Grype CI integration patterns and the CISA Kubernetes Hardening Guide recommendation for image scanning before registry push.

---

_Last reviewed: 2026-06-05 by `claude`_

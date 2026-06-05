# Treat the SBOM as the authoritative software inventory — generate and query it

**Status:** Absolute rule
**Domain:** Supply chain security
**Applies to:** `security-engineering`

---

## Why this exists

You can't patch what you can't enumerate. When a zero-day like Log4Shell drops, teams without a current SBOM spend hours or days manually searching repos to find which services use the affected library. Teams with a queryable SBOM answer in minutes. The SBOM (Software Bill of Materials) is the foundation of every supply-chain security task: CVE response, compliance attestation, license auditing, and provenance verification all require it. Generating the SBOM at build time and attaching it to the artifact is the first step; querying it during incident response is the payoff.

## How to apply

Generate the SBOM at build time using CycloneDX or SPDX format and attach it to the container image. Store it in the artifact registry so it's co-located with the image and queryable.

```bash
# Generate CycloneDX SBOM from a container image (syft)
syft packages \
  my-service:sha256-abc123 \
  -o cyclonedx-json=sbom.cdx.json

# Attach SBOM as an OCI artifact alongside the image (cosign)
cosign attach sbom \
  --sbom sbom.cdx.json \
  --type cyclonedx \
  my-registry/my-service@sha256:abc123

# Query the SBOM for a specific component (grype, or jq for CycloneDX JSON)
grype sbom:./sbom.cdx.json --only-fixed   # show only findings with a fix available
jq '.components[] | select(.name == "log4j-core")' sbom.cdx.json
```

```yaml
# GitHub Actions: SBOM generation and attestation in CI
- name: Generate SBOM
  uses: anchore/sbom-action@v0.17.1
  with:
    image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    format: cyclonedx-json
    output-file: sbom.cdx.json

- name: Upload SBOM as artifact
  uses: actions/upload-artifact@v4
  with:
    name: sbom-${{ github.sha }}
    path: sbom.cdx.json
```

**Do:**
- Generate the SBOM at build time, not manually on demand — it must reflect what was actually built.
- Use CycloneDX (widely supported, richer metadata) or SPDX (NTIA-compliant) — not both; pick one.
- Store the SBOM alongside the image in the registry so it can be retrieved without the source repo.
- Run SBOM-based CVE scanning (grype, Trivy) in CI to catch known vulnerabilities at build time.

**Don't:**
- Generate the SBOM from the source code alone — generate it from the built artifact (the running dependency graph).
- Treat the SBOM as a compliance checkbox; query it during incident response.
- Discard the SBOM after scanning — retain it for the artifact's full lifecycle for audit purposes.

## Edge cases / when the rule does NOT apply

SBOMs are not sufficient for detecting malicious packages that pass CVE scanners (typosquatting, dependency confusion). Pair SBOM scanning with provenance verification (SLSA) and package origin checks.

## See also

- [`../agents/supply-chain-security-engineer.md`](../agents/supply-chain-security-engineer.md) — owns SBOM generation, ingestion, and the CVE triage workflow.
- [`./enumerate-before-you-assess.md`](./enumerate-before-you-assess.md) — the SBOM is the enumeration; assessment follows.

## Provenance

Codifies NTIA minimum SBOM elements (ntia.gov/sbom), CycloneDX specification (cyclonedx.org), and the US Executive Order 14028 on Improving the Nation's Cybersecurity requirements for software transparency.

---

_Last reviewed: 2026-06-05 by `claude`_

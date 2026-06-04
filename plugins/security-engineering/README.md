# Security Engineering (AppSec)

The **security-engineering** plugin — building security into software — threat modeling, application security testing (SAST/DAST/SCA), secrets management, software supply-chain integrity, and cloud security posture. It proposes; ravenclaude-core/security-reviewer holds the verdict.

## Agents

- **`appsec-engineer`** — Application security testing and the AppSec program: SAST/DAST/IAST/SCA in CI, OWASP Top 10 (web), vulnerability triage by exploitability, secure-coding guidance, security gates in the pipeline
- **`threat-modeler`** — Threat modeling: data-flow diagrams, trust boundaries, STRIDE per element, attack trees, ranking threats by likelihood × impact, and mapping each to a mitigation or an accepted risk
- **`supply-chain-security-engineer`** — Software supply-chain integrity from the consume side: SBOM ingestion and dependency inventory, CVE triage and patching strategy, dependency pinning and update policy, SLSA provenance verification, typosquat/malicious-package defense
- **`cloud-security-engineer`** — Cloud security posture: CSPM-style misconfiguration detection, IAM least-privilege analysis, network exposure (public buckets, open security groups), encryption-at-rest/in-transit, and guardrails (policy-as-code)

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install security-engineering@ravenclaude
```

## Seams

- **The ship/no-ship VERDICT on any finding** → `ravenclaude-core/security-reviewer` (mandatory). This team produces the evidence and the recommended control; the verdict is not ours.
- **API-specific authorization flaws (BOLA/BOPLA/BFLA) and the OWASP API Top 10** → `api-engineering/api-security-engineer` owns that craft; we cover web OWASP + the cross-cutting program.
- **End-user authentication, OAuth/OIDC flows, session/token storage** → `auth-identity`; we threat-model the design, they implement it.
- **Data privacy, PII handling, GDPR/CCPA mechanics, DLP** → `data-governance-privacy`.
- **The artifact-side SBOM/provenance *production*** → `devops-cicd/build-and-artifact-engineer`; we *consume and verify* it.
- **Cloud IAM/network primitives** → `azure-cloud`/`aws-cloud`/`gcp-cloud`; we assess the posture across them.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.

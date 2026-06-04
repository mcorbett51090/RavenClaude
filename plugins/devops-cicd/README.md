# DevOps & CI/CD

The **devops-cicd** plugin — building and operating the delivery pipeline that takes a commit to production safely — CI, release engineering, GitOps continuous delivery, and artifact/supply-chain hygiene.

## Agents

- **`pipeline-engineer`** — CI design — stages, caching, build matrices, required status checks, fail-fast ordering, monorepo-vs-polyrepo pipeline shape, pipeline-as-code in GitHub Actions / GitLab CI
- **`release-engineer`** — Continuous *delivery*: promotion through environments, progressive-delivery strategy (blue-green, canary, rolling, feature-flagged), automated rollback on health gates, release versioning and changelogs
- **`gitops-engineer`** — GitOps: desired-state-in-Git delivery with Argo CD / Flux, app-of-apps and environment promotion via Git, drift detection and self-heal, secrets handling in a GitOps world (sealed-secrets / external-secrets)
- **`build-and-artifact-engineer`** — Build reproducibility and artifact integrity: deterministic builds, container image hygiene (small base, multi-stage, non-root), semantic versioning of artifacts, SBOM generation, provenance/SLSA attestation, registry and cache management

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install devops-cicd@ravenclaude
```

## Seams

- **Provisioning the infrastructure the pipeline deploys to** → `terraform-iac` (the cluster, the registry, the DNS) — this plugin *uses* that infra, it doesn't author it.
- **Kubernetes manifests / Helm / the cluster itself** → `cloud-native-kubernetes`; GitOps here orchestrates *what* reconciles, that plugin owns *how* the workload runs.
- **Deploy health gates, SLO burn-rate, and release telemetry** → `observability-sre` — a canary needs a signal to promote/abort, and that signal is theirs.
- **The verdict that an SBOM/provenance finding is acceptable to ship** → `ravenclaude-core/security-reviewer`; `security-engineering` does the supply-chain scanning craft.
- **Per-cloud deploy targets (App Service, ECS, Cloud Run)** → `azure-cloud` / `aws-cloud` / `gcp-cloud`.
- **Cross-repo release activity & who-shipped-what** → `team-portfolio`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.

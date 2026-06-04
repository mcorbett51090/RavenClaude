# DevOps & CI/CD — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse these before choosing a pipeline shape or a rollout strategy.

## Decision Tree: Deploy / rollout strategy selection

Pick the rollout by blast radius and reversibility — not by what the tool defaults to.

```mermaid
graph TD
  A[Shipping a change] --> B{Reversible quickly?}
  B -- No --> C{Behaviour change?}
  C -- Yes --> D[Feature flag: deploy dark, release later]
  C -- No, it's a schema change --> E[Expand/contract migration FIRST, then deploy]
  B -- Yes --> F{Stateful / sticky sessions?}
  F -- Yes --> G[Blue-green: instant cutover + rollback]
  F -- No --> H{Have an SLO health signal?}
  H -- Yes --> I[Canary: 1%->10%->100% on burn-rate gate]
  H -- No --> J[Rolling + manual gate; add a health signal next]
```

_The canary's promote/abort signal comes from `observability-sre`. No signal → don't auto-promote._

## Decision Tree: CI vs CD boundary — where does this step belong?

Keep the PR gate fast; push slow and deploy-side work to the right phase.

```mermaid
graph TD
  A[A pipeline step] --> B{Does it prove the commit is safe to MERGE?}
  B -- Yes --> C{Fast < ~3 min?}
  C -- Yes --> D[PR gate / required check]
  C -- No --> E[Shard it, or move to post-merge gate]
  B -- No, it ships/promotes the artifact --> F[CD: release-engineer owns it]
  F --> G{Changes desired state in Git?}
  G -- Yes --> H[gitops-engineer: PR bumps the digest]
  G -- No --> I[release-engineer: progressive delivery + rollback]
```


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| GitHub Actions OIDC to cloud | GA | Prefer over long-lived keys; federate to AWS/Azure/GCP |
| Argo CD | GA, CNCF graduated | App-of-apps, ApplicationSets, drift self-heal |
| Flux | GA, CNCF graduated | GitOps Toolkit controllers |
| SLSA provenance | v1.0 framework | Build L2/L3 levels; pair with signing (cosign/Sigstore) |
| CycloneDX / SPDX SBOM | both widely supported | Pick one and attach at build time |
| Conventional Commits | de-facto standard | Drives SemVer bump + changelog automation |

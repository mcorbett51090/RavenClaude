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


## Decision Tree: Trunk-based vs branch strategy

Choose by integration frequency and the real need to support multiple versions — not by habit.

```mermaid
graph TD
  A[Picking a branching model] --> B{Must you support multiple released versions at once?}
  B -- Yes, regulated/multi-version --> C[Release branches + cherry-pick hotfixes; accept the overhead]
  B -- No --> D{Can incomplete work hide behind a feature flag?}
  D -- No --> E[Fix testability/flags first; long branches are a symptom]
  D -- Yes --> F{Team merges to trunk at least daily?}
  F -- Yes --> G[Trunk-based: short-lived branches, flags for unfinished work]
  F -- No --> H[Move toward trunk-based; shrink branch lifetime before adding process]
```

_GitFlow's develop/release/hotfix lattice is overhead most teams pay without the multi-version need that justifies it._

## Decision Tree: Monorepo vs polyrepo pipeline shape

The repo layout is a choice; the pipeline shape it forces is the real cost — decide with eyes open.

```mermaid
graph TD
  A[Repo + pipeline shape] --> B{Do changes routinely span multiple projects atomically?}
  B -- Yes --> C{Willing to invest in affected-only execution?}
  C -- No --> D[Polyrepo: each repo its own pipeline, independent cadence]
  C -- Yes --> E[Monorepo + change-detection: build/test only the affected graph]
  B -- No --> F{Teams need independent release cadences?}
  F -- Yes --> D
  F -- No --> G{Shared tooling/standards a priority?}
  G -- Yes --> E
  G -- No --> D
```

_A monorepo that rebuilds everything on every commit is the worst of both worlds — affected-only execution is the price of admission._

## Decision Tree: Secrets — where does this credential live?

Before pasting any credential into a pipeline, route it to the least-exposed home that still works.

```mermaid
graph TD
  A[A credential the pipeline needs] --> B{Authenticating to a cloud/provider that supports OIDC?}
  B -- Yes --> C[OIDC federation: no stored secret; scope trust to repo+branch+env]
  B -- No --> D{Is it consumed by the running app, not the build?}
  D -- Yes --> E[Secrets manager / external-secrets; app reads at runtime]
  D -- No --> F{Truly needed at build/deploy time?}
  F -- Yes --> G[Secrets manager-backed CI secret, short TTL, scoped, rotated by expiry]
  F -- No --> H[It doesn't belong in the pipeline — remove it]
```

_A static key pasted into a CI variable is the last resort, never the default — and it has an owner and an expiry date the moment it exists._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| GitHub Actions OIDC to cloud | GA | Prefer over long-lived keys; federate to AWS/Azure/GCP |
| Argo CD | GA, CNCF graduated | App-of-apps, ApplicationSets, drift self-heal |
| Flux | GA, CNCF graduated | GitOps Toolkit controllers |
| SLSA provenance | v1.0 framework | Build L2/L3 levels; pair with signing (cosign/Sigstore) |
| CycloneDX / SPDX SBOM | both widely supported | Pick one and attach at build time |
| Conventional Commits | de-facto standard | Drives SemVer bump + changelog automation |

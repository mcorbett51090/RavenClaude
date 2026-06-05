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

## Decision Tree: Pipeline stage — retry, fail, or skip?

When applies: a CI stage exits non-zero or times out. The right response depends on whether the failure is transient infrastructure noise, a real defect, or an optional informational step.

**Last verified:** 2026-06-05 against GitHub Actions retry semantics and general CI/CD practice.

```mermaid
flowchart TD
    START[A stage exits non-zero] --> Q1{Is this a known-transient infra issue - network, runner OOM?}
    Q1 -->|yes| Q2{Has it retried within budget - max 2 attempts?}
    Q2 -->|no| RETRY[Retry the stage automatically]
    Q2 -->|yes, still failing| FAIL_INFRA[Fail the pipeline - infra problem needs human]
    Q1 -->|no| Q3{Is this a required check that gates the merge?}
    Q3 -->|yes| FAIL_REQUIRED[Fail pipeline - block merge; notify owner]
    Q3 -->|no| Q4{Is the step informational - coverage report, lint warning?}
    Q4 -->|yes| WARN[Allow pipeline to pass with a warning annotation]
    Q4 -->|no| FAIL_OPTIONAL[Fail the stage but do not block merge - file a ticket]
```

**Rationale per leaf:**
- *Retry the stage* — transient infra noise should not block a developer; one automatic retry surfaces real failures while absorbing flaps.
- *Fail pipeline - infra problem* — repeated infra failures are on-call territory, not developer territory; surfacing them fast gets them fixed.
- *Fail pipeline - block merge* — a required check that fails is the whole point of the gate; it must block.
- *Allow with warning* — optional informational steps (coverage delta, dependency audit summary) should never block a merge; file a ticket instead.
- *Fail stage, no merge block* — non-required steps that fail indicate work to do, but the merge can proceed with the defect tracked.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Auto-retry | Adds 1-3 min | None | No | Known-transient infra noise |
| Fail and block | Blocks PR until fixed | Developer blocked | No (auto) | Required safety check fails |
| Warn and continue | No block | Low - tracked | No | Informational step only |
| Fail stage, pass pipeline | Ticket created | Low | No | Non-required quality signal |

## Decision Tree: Image base selection — which base image?

**When this applies:** creating or updating a production container image Dockerfile. The base image choice has direct implications for image size, CVE surface, and rebuild cadence.

**Last verified:** 2026-06-05 against Google distroless project, Alpine, and Docker Hub official images.

```mermaid
flowchart TD
    START[Choosing a base image] --> Q1{Does the app need a shell or OS tools at runtime?}
    Q1 -->|yes| Q2{Is the OS toolset audited and minimal?}
    Q2 -->|yes| ALPINE[Alpine Linux - musl libc, minimal package set]
    Q2 -->|no| SLIM[debian-slim or ubuntu-minimal - prune after install]
    Q1 -->|no| Q3{Single compiled binary - Go, Rust, or similar?}
    Q3 -->|yes| DISTROLESS_STATIC[gcr.io/distroless/static-debian12 - no libc needed]
    Q3 -->|no| Q4{Needs glibc - Python, JVM, Node?}
    Q4 -->|yes| DISTROLESS_BASE[gcr.io/distroless/base-debian12 - glibc only]
    Q4 -->|no| DISTROLESS_LANG[Language distroless - python3 / java21 / nodejs20]
```

**Rationale per leaf:**
- *Alpine* — smallest full-shell base; musl libc means fewer CVEs vs glibc; requires testing for musl compatibility.
- *debian-slim* — familiar tooling, larger than Alpine but compatible with glibc expectations; prune after install.
- *distroless/static* — no OS at all; only the binary; zero CVE surface from system packages; ideal for Go/Rust.
- *distroless/base* — adds glibc and ca-certs only; right for C-extension Python wheels, JVM, Node native modules.
- *language distroless* — adds the language runtime on top of base; maintained by Google with rapid CVE turnaround.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| distroless/static | Smallest/fastest pull | Minimal CVE surface | No | Compiled static binary |
| distroless/base | Slightly larger | Low CVE surface | No | glibc-dependent runtime |
| Alpine | Small, shell available | Low-medium | No | Need shell tools or scripts |
| debian-slim | Medium, familiar | Medium | No | Complex glibc dependencies |

## Decision Tree: When does a pipeline change need its own PR?

**When this applies:** a developer wants to modify a CI/CD pipeline definition, Dockerfile, or GitOps manifest. Deciding whether the change needs its own PR or can ride the feature branch.

**Last verified:** 2026-06-05 against general CI/CD change-management practice.

```mermaid
flowchart TD
    START[A pipeline or config change] --> Q1{Does it change a required status check name or behavior?}
    Q1 -->|yes| OWN_PR[Own PR - coordinate with branch protection update]
    Q1 -->|no| Q2{Does it affect the deploy path to production?}
    Q2 -->|yes| Q3{Is it reversible within one deploy cycle?}
    Q3 -->|no| OWN_PR
    Q3 -->|yes| FEATURE_PR[Can ride the feature PR with explicit review note]
    Q2 -->|no| Q4{Does it change secrets handling or OIDC trust?}
    Q4 -->|yes| OWN_PR
    Q4 -->|no| Q5{Performance-only - caching, parallelism?}
    Q5 -->|yes| FEATURE_PR
    Q5 -->|no| OWN_PR
```

**Rationale per leaf:**
- *Own PR* — changes to required checks, deploy paths, secrets handling, or irreversible configuration need explicit review and a clean rollback story before they touch main.
- *Can ride the feature PR* — purely additive, reversible, or performance-only pipeline changes can be bundled with the feature for context; flag them in the PR description for the reviewer.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Own PR | Extra PR overhead | Low - isolated | Yes - reviewer | Affects prod path, security, or required checks |
| Ride feature PR | No extra PR | Medium - bundled | Implicit | Reversible, non-security, performance-only |

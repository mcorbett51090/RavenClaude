# Cloud-Native & Kubernetes Plugin — Team Constitution

> Team constitution for the `cloud-native-kubernetes` Claude Code plugin — **4** specialist agents for running workloads on Kubernetes well — container build hygiene, workload and resource design, cluster platform operations, and service-mesh networking — cloud-agnostic, with the per-cloud control plane deferred to the cloud plugins. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`kubernetes-architect`](agents/kubernetes-architect.md) | Workload and resource design: choosing the workload kind (Deployment/StatefulSet/DaemonSet/Job/CronJob), probes, requests/limits and QoS, autoscaling (HPA/VPA), PodDisruptionBudgets, and the Helm/Kustomize packaging shape | "how should this run on k8s?", "Deployment or StatefulSet?", "set resource requests/limits", "add autoscaling" |
| [`container-build-engineer`](agents/container-build-engineer.md) | Container image craft for Kubernetes: minimal multi-stage builds, distroless/non-root, image size and CVE surface reduction, OCI labels, and image-pull/registry configuration in-cluster | "our k8s images are huge/root", "build a Dockerfile for this", "reduce our image CVEs", "set up imagePullSecrets" |
| [`k8s-platform-operator`](agents/k8s-platform-operator.md) | Cluster platform operations: namespaces and multi-tenancy, RBAC, NetworkPolicies (default-deny), resource quotas and LimitRanges, admission control (policy), cluster/add-on upgrades, and capacity | "set up RBAC/namespaces", "lock down pod-to-pod traffic", "enforce resource quotas", "how do we upgrade the cluster safely" |
| [`service-mesh-networking-engineer`](agents/service-mesh-networking-engineer.md) | In-cluster and edge networking: Ingress/Gateway API, service-mesh (mTLS, traffic-splitting for canary, retries/timeouts/circuit-breaking), east-west security, and mesh observability | "set up ingress", "do we need a service mesh?", "mTLS between services", "traffic-split for a canary" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Set requests AND limits — and know the difference.** Requests schedule; limits cap. No requests means the scheduler is guessing and your pod is the noisy neighbor or the one that gets evicted.
2. **Probes are not optional.** Liveness restarts a hung pod; readiness gates traffic; startup protects slow boots. Missing/incorrect probes cause both phantom outages and traffic to dead pods.
3. **Least privilege in the cluster too.** Namespaced RBAC, no cluster-admin for workloads, default-deny NetworkPolicies, no privileged/root containers. A pod is a tenant; treat it like one.
4. **Stateless by default; state is a deliberate StatefulSet.** Most workloads are Deployments. Reach for StatefulSet only when stable identity/storage truly matters, and know what you're signing up for.
5. **Pin and declare everything.** Image digests, chart versions, API versions. `latest` and unpinned charts make a cluster un-reproducible and upgrades terrifying.
6. **The cluster is cattle; GitOps is the herd.** Desired state lives in Git and a reconciler enforces it (devops-cicd). A `kubectl edit` in prod is drift.

## 3. Seams (the bridges to neighbouring plugins)

- **The managed control plane (AKS / EKS / GKE), node pools, and cloud IAM↔cluster identity** → `azure-cloud` / `aws-cloud` / `gcp-cloud`; this team runs *workloads on* the cluster, cloud-agnostically.
- **GitOps reconcile of manifests/Helm into the cluster** → `devops-cicd/gitops-engineer` (Argo/Flux); we author the manifests, they reconcile them.
- **In-cluster telemetry, SLOs, and the metrics pipeline design** → `observability-sre`; we expose the signals, they decide the SLOs and alerts.
- **Image SBOM/provenance and CVE verdicts** → `devops-cicd/build-and-artifact-engineer` + `security-engineering`.
- **Provisioning the cluster + cloud resources via IaC** → `terraform-iac`; we consume what it stands up.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer) — traverse the relevant Mermaid tree top-to-bottom before choosing (the proactive complement to the Capability Grounding Protocol):
  - [`knowledge/cloud-native-kubernetes-decision-trees.md`](knowledge/cloud-native-kubernetes-decision-trees.md) — **the #315 baseline**: workload-kind, mesh-justification, secrets-source, expose/route, tenant-isolation, base-image, HPA/VPA/KEDA *(which autoscaler)*, cluster-upgrade, plus the dated capability map.
  - [`knowledge/workload-resource-and-autoscaling-decision-trees.md`](knowledge/workload-resource-and-autoscaling-decision-trees.md) — **complement**: how to set `requests`/`limits` and which **QoS class** you land in (the upstream question the autoscaler tree depends on), plus the CPU-limit set-or-omit debate and the OOMKill/exit-137 signature.
  - [`knowledge/networking-and-ingress-decision-trees.md`](knowledge/networking-and-ingress-decision-trees.md) — **complement**: the implementation layer below the #315 architecture trees — which north-south *mechanism* (LoadBalancer / Ingress / Gateway API), controller selection, and the Ingress-error (503/404/502/TLS) debug walk.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (CrashLoopBackOff/OOMKilled triage, rollout-stuck PDB deadlock, Ingress 503 endpoints/readiness, cluster cost right-sizing). Secondary source; never replaces the knowledge bank or a destructive-action safety check.

## 6. Technical-runtime tier — Kubernetes MCP servers (recommend-not-bundle), CLI, and LSP

This is a **code/infra** domain with a real runtime tier, so the disposition is explicit rather than blanket-N-A.

### 6.1 Kubernetes MCP servers — recommend, do **not** bundle

Per [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**. **Every Kubernetes MCP server fails the zero-config bar for the same structural reason: it needs a `kubeconfig` (or in-cluster ServiceAccount) — cluster credentials are a per-consumer secret, never hardcodable.** So the plugin **bundles none** and documents the recommended `claude mcp add …` paths instead, each gated through `ravenclaude-core/security-reviewer` before adoption and run in a **read-only mode** where the server offers one.

| Server | Party / license `[verify-at-use]` | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|---|
| **`kubernetes-mcp-server`** ([containers/kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server), Apache-2.0) — native Go, talks the API server directly (not a kubectl wrapper); npm/PyPI/binary/container | Needs a **kubeconfig / in-cluster SA** (per-consumer credential) → not zero-config. **Has a real read-only mode** (`--read-only`; `--disable-destructive` for read+non-destructive). | `claude mcp add k8s -- npx -y kubernetes-mcp-server@<pinned> --read-only --kubeconfig <path>` — prefer a **dedicated read-only ServiceAccount**; pin the version; `security-reviewer` sign-off. |
| **`mcp-server-kubernetes`** ([Flux159/mcp-server-kubernetes](https://github.com/Flux159/mcp-server-kubernetes), MIT, npm) — kubectl/helm-based | Needs `~/.kube/config` + `kubectl` on PATH (per-consumer credential) → not zero-config; **write-capable by default**. | `claude mcp add k8s -- npx -y mcp-server-kubernetes@<pinned>` with `ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS=true` to disable delete/uninstall/cleanup; `security-reviewer` sign-off. |
| **Flux Operator MCP** ([fluxoperator.dev/mcp-server](https://fluxoperator.dev/mcp-server/), GitOps/Flux clusters) — natural-language Flux/GitOps troubleshooting | Per-cluster, **uses your existing kubeconfig permissions** (credentialed) → not zero-config. **Has a read-only mode** (disables reconcile/suspend/resume/apply/delete; masks Secret values). | Deploy per the Flux Operator docs in **read-only mode**; this is a `devops-cicd/gitops-engineer` seam (GitOps reconcile), so coordinate there; `security-reviewer` sign-off. |

> Verified 2026-06-05 via the upstream repos/docs: `containers/kubernetes-mcp-server` is Apache-2.0 with a `--read-only` flag and resolves a kubeconfig/in-cluster config; `Flux159/mcp-server-kubernetes` is MIT, kubectl-based, with an `ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS` env toggle and defaults to `~/.kube/config`; the Flux Operator MCP runs read-only against your kubeconfig and masks Secret values. **Version numbers are volatile and conflicting across listings (npm reported `0.0.x` while a guide cited `2.0.0`) — pin and confirm the tested version at adoption; the listings above intentionally do not hard-code a version. `[verify-at-use]`** No server is invented; if a genuinely zero-config, read-only, broadly-useful k8s server ever appears, revisit with Step 4 of the bundled-MCP doctrine.

### 6.2 CLI binaries — referenced, not bundled

The agents reason about and emit `kubectl` / `helm` / `kustomize` invocations, but the plugin **ships no `bin/`**: these are heavyweight, per-consumer, credentialed CLIs that belong on the consumer's PATH (and a destructive `kubectl delete` / `helm uninstall` is exactly what the `ravenclaude-core` command-review tribunal and `guard-destructive.sh` already gate). Shipping a wrapper would duplicate those guards and add a stale-binary supply-chain surface. Disposition: **referenced in agent guidance, not vendored.**

### 6.3 LSP — N-A

The plugin's artifacts are **YAML manifests / Helm charts**, not a source language with go-to-definition/find-references semantics. A YAML/k8s-schema language server exists in the broader ecosystem, but schema *validation* of manifests is better served by the advisory anti-pattern hook + admission-control guidance the agents already carry, and an LSP wired into `plugin.json` `lspServers` would degrade loudly for every consumer who hasn't installed the binary while adding little over the existing hook. Disposition: **N-A** (no source-language code-intelligence need; manifest validation is covered elsewhere).

## 7. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason). This plugin already shipped agents, skills, best-practices, templates, commands, a hook, and the #315 consolidated decision-tree knowledge; this build-out adds the scenarios bank + two topic-specific decision-tree files and dispositions the runtime tier honestly.

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — `scenarios/README.md` + 4 dated scenarios (CrashLoopBackOff/OOMKilled triage *(pre-existing, #315-era)*, rollout-stuck PDB deadlock, Ingress 503 endpoints/readiness, cluster cost right-sizing) on the 9-field schema. |
| 2 | **Decision-tree knowledge** | **BUILT** — 2 NEW files *complementing* #315's: `workload-resource-and-autoscaling-decision-trees.md` (requests/limits + QoS + CPU-limit debate) and `networking-and-ingress-decision-trees.md` (north-south mechanism + controller selection + Ingress-error debug). Chosen to fill the gap below #315's architecture/which-autoscaler trees, not duplicate them. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §6.1. Every real Kubernetes MCP server needs a kubeconfig/credential → fails the zero-config bar; documented the recommended `claude mcp add …` paths (read-only mode + `security-reviewer` gate) for 3 real, verified servers. No invented servers; no `mcpServers` entry / `x-mcpAttribution` (nothing bundled). |
| 4 | **LSP server** | **N-A** — §6.3. Manifests are YAML, not a source language with code-intelligence semantics; manifest validation is the hook's + admission-control's lane. |
| 5 | **Runnable script (`scripts/`)** | **N-A** — a resource/cost estimator would be a thin wrapper over data only the live cluster + metrics pipeline hold (`kubectl top` / VPA / `observability-sre`); a static calculator with invented inputs would mislead. The cost/right-sizing *method* ships as the scenario + the QoS/sizing decision tree instead. |
| 6 | **bin/ / monitors / output-styles / settings / themes** | **N-A** — §6.2 (CLIs referenced not vendored). No monitor/output-style/theme cleared the "groundable + broadly valuable, doesn't duplicate an existing surface or a neighbouring plugin / the core tribunal" bar; the plugin is config-light by design. |
| 7 | **skills / hooks / commands / templates** | **SUFFICIENT** — 6 skills, 1 advisory anti-pattern hook, 4 commands, 4 templates already cover workload design, container hardening, platform ops, ingress/mesh, helm authoring, and upgrade/capacity. The new scenarios + trees extend reach without a new agent (team-growth-as-knowledge house rule). |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top entry for this build-out. No `NOTICE.md` (nothing third-party is bundled; the recommended MCP servers are referenced, not vendored). |

## 8. Milestones

- **v0.2.x** — 4 agents, 6 skills, best-practices, 4 templates, 4 commands, 1 advisory hook; #315 added the consolidated decision-tree knowledge + best-practices/ + templates/.
- **v0.3.0** — value-add build-out: scenarios bank (README + rollout-PDB, ingress-503, cost-right-sizing scenarios alongside the existing crashloop triage), 2 complement decision-tree knowledge files (workload-resource-sizing/QoS, networking/ingress), runtime-tier dispositioning (§6 — Kubernetes MCP recommend-not-bundle with 3 verified servers, CLI referenced-not-bundled, LSP N-A), CHANGELOG, and the §7 value-add completeness table.

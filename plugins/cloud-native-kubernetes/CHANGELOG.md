# Changelog — cloud-native-kubernetes

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.7] — 2026-07-09

Research-sweep **correction** (F13) — the capability map's Istio/Linkerd row said "ambient mode emerging", ~18 months stale. Istio's **ambient data plane reached GA in v1.24 (Nov 2024)** (sidecarless L4 by default + waypoints for L7); ambient multicluster reached **Beta in Istio 1.29 (Feb 2026)**. Verified 2026-07-09 against the istio.io ambient-reaches-ga blog (the 1.29 multicluster-Beta detail carries a `[verify-at-use]`).

### Changed

- `knowledge/cloud-native-kubernetes-decision-trees.md` — capability-map Istio/Linkerd row: replaced "ambient mode emerging" with ambient GA-since-1.24 (Nov 2024) + the 1.29 multicluster-Beta note, dated + cited.
- Version **0.3.6 → 0.3.7** in `.claude-plugin/plugin.json`.

## [0.3.6] — 2026-07-08

Research-sweep **correction** — the ingress/Gateway controller decision tree recommended community **`ingress-nginx`** for new clusters, but the Kubernetes project **retired** it: best-effort maintenance ended **March 2026**, after which there are no releases, bug fixes, or **security patches** (repos read-only). Recommending it for a new cluster now signs up for un-patched CVEs. Verified 2026-07-08 against [kubernetes.io](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) (Nov 11 2025 notice + [Jan 29 2026 Steering/SRC statement](https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/)).

### Changed

- `knowledge/networking-and-ingress-decision-trees.md` — removed `ingress-nginx` from the controller-selection tree's recommended nodes and added a retirement callout steering new builds to the **Gateway API** or a supported/commercial controller.
- `knowledge/cloud-native-kubernetes-decision-trees.md` — added a capability-map row marking community `ingress-nginx` **RETIRED** (no security patches after March 2026), alongside the existing Gateway API row.
- Version **0.3.5 → 0.3.6** in `.claude-plugin/plugin.json` + `marketplace.json` (lockstep).

## [0.3.3] — 2026-07-06

Bug fix (P3) — the advisory `check-cloud-native-kubernetes-anti-patterns.sh` hook's resources-block / readinessProbe checks use `grep -Pzi` (PCRE, a GNU extension); on BSD/macOS grep the command errors and, wrapped in `if grep …; then`, silently failed to "no finding". Added a one-time PCRE-support probe that skips those two checks with a visible advisory (install GNU grep for full coverage) instead of a silent no-op. No behavior change on GNU-grep hosts.

## [0.3.2] — 2026-06-22

Version bump previously unlogged here; the change that set `0.3.2`:

- Repo review autonomous fixes + B1–B6 deferred items + dead-regex CI guard (#449)

## [0.3.1] — 2026-06-11

Research-sweep **correction/addition** — the capability map had **no Kubernetes version anchor** and predated several GA graduations; re-verified 2026-06-11 against kubernetes.io release blogs.

### Added / Fixed

- **`knowledge/cloud-native-kubernetes-decision-trees.md`** capability map — added a **Kubernetes core** row (current GA **1.36 "Haru"**, 2026-04-22; 1.35/1.34 in support) plus rows for **DRA — GA since 1.34** (first-class GPU/accelerator scheduling), **cgroup v1 removed — nodes must run cgroup v2** (exact removal minor 1.35/1.36 marked `[verify-at-use]`; confirm containerd ≥1.7), and **User Namespaces GA in 1.36** (`hostUsers: false`). Sources: [1.36 release](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/), [1.34 DRA GA](https://kubernetes.io/blog/2025/09/01/kubernetes-v1-34-dra-updates/), [1.36 userns GA](https://kubernetes.io/blog/2026/04/23/kubernetes-v1-36-userns-ga/).
- Version **0.3.0 → 0.3.1** in `.claude-plugin/plugin.json` + `marketplace.json` (lockstep).

## [0.3.0] — 2026-06-05

Value-add build-out against the full value-add menu. Every menu item was dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) §7 "Value-add completeness (build-out 2026-06-05)". Builds on PR #315, which added the consolidated decision-tree knowledge + best-practices/ + templates/.

### Added

- **scenarios/ bank.** `scenarios/README.md` index + 3 new dated field notes alongside the existing CrashLoopBackOff/OOMKilled triage: `rollout-stuck-pdb-deadlock` (a PDB whose `minAvailable` equals the replica count deadlocks every rollout and node drain), `ingress-503-dns-and-readiness` (a 503 through an Ingress is "no healthy endpoint" — walk Ingress→Service→endpoints before blaming the controller or DNS), and `cluster-cost-right-sizing` (low node utilization + high cost is over-*requesting*, not under-provisioning — the scheduler bin-packs on requests). All on the 9-field schema; secondary source, surfaced behind the mandatory unverified-scenario preamble.
- **Decision-tree knowledge — 2 new files complementing #315's.** `knowledge/workload-resource-and-autoscaling-decision-trees.md` — how to set `requests`/`limits` and which **QoS class** you land in (the upstream choice the #315 which-autoscaler tree depends on), the CPU-limit set-or-omit debate, and the OOMKill/exit-137 signature. `knowledge/networking-and-ingress-decision-trees.md` — the implementation layer below #315's architecture trees: which north-south **mechanism** (LoadBalancer / Ingress / Gateway API), controller selection, and the Ingress-error (503/404/502/TLS) debug walk. Both Mermaid, grounded, dated.
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (runtime tier — Kubernetes MCP / CLI / LSP dispositioning), §7 (value-add completeness table), §8 (milestones).

### Decisions (recorded, not built)

- **No bundled MCP server.** Every real Kubernetes MCP server needs a `kubeconfig` / in-cluster ServiceAccount (a per-consumer credential) → fails the doctrine's zero-config bar. Documented the recommended `claude mcp add …` paths (read-only mode + `security-reviewer` gate) for **3 real, verified** servers — `containers/kubernetes-mcp-server` (Apache-2.0, native, `--read-only`), `Flux159/mcp-server-kubernetes` (MIT, kubectl-based, `ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS`), and the Flux Operator MCP (read-only mode, Secret-masking). No invented servers; no `mcpServers` entry / `x-mcpAttribution` (nothing bundled).
- **No LSP.** Artifacts are YAML manifests / Helm charts, not a source language with code-intelligence semantics; manifest validation is the advisory hook's + admission-control's lane.
- **No `scripts/` calculator, no `bin/`, no monitors/output-styles/themes.** A resource/cost estimator would wrap data only the live cluster + metrics pipeline hold (`kubectl top` / VPA / `observability-sre`); the cost/right-sizing *method* ships as the scenario + the QoS/sizing tree instead. CLIs (`kubectl`/`helm`/`kustomize`) are referenced not vendored — a destructive invocation is already gated by the core command-review tribunal + `guard-destructive.sh`.
- **Skills/commands/templates/hooks coverage held sufficient** — 6 skills, 4 commands, 4 templates, 1 advisory hook; new scenarios + trees extend reach without a new agent (team-growth-as-knowledge house rule).

### Verify-at-use

- Kubernetes MCP server **version numbers are volatile and conflicting across listings** (npm reported `0.0.x` while a guide cited `2.0.0`) — pin and confirm the tested version at adoption; the CLAUDE.md table intentionally does not hard-code a version. The read-only flags (`--read-only`, `ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS`), licenses (Apache-2.0 / MIT), and kubeconfig requirement were verified against the upstream repos/docs 2026-06-05.
- The `kubectl get pdb` `ALLOWED DISRUPTIONS` column, `endpoints` vs `endpointslices`, exit-137 OOMKill signature, and VPA `updateMode: Off` recommendation behavior are marked `[verify-at-use]` in the scenarios/trees — stable Kubernetes contracts but confirm against your cluster version.

## [0.2.x] — earlier

4-agent cloud-native & Kubernetes team (kubernetes-architect, container-build-engineer, k8s-platform-operator, service-mesh-networking-engineer): 6 skills, best-practices, 4 templates, 4 commands, 1 advisory hook. PR #315 added the consolidated `knowledge/cloud-native-kubernetes-decision-trees.md` + best-practices/ + templates/. Seams: managed control plane (AKS/EKS/GKE) → azure/aws/gcp-cloud, GitOps reconcile → devops-cicd, telemetry/SLOs → observability-sre.

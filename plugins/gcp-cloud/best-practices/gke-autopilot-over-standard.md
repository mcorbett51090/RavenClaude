# Prefer GKE Autopilot over Standard for new clusters

**Status:** Pattern
**Domain:** GCP compute / Kubernetes
**Applies to:** `gcp-cloud`

---

## Why this exists

GKE Standard requires node pool management: choosing machine types, setting node auto-provisioning, managing OS upgrades, and sizing pools. GKE Autopilot manages all of this — Google provisions nodes on demand per pod request, enforces security hardening (Workload Identity required, privileged containers denied, no SSH to nodes), and bills per pod resource request rather than per node. For most workloads the operational savings outweigh the constraints, and the enforced security posture is better than Standard's defaults. Standard is justified only when Autopilot's constraints genuinely conflict with workload requirements.

## How to apply

```hcl
# Terraform — GKE Autopilot cluster
resource "google_container_cluster" "this" {
  name     = "gke-${var.app_name}-${var.env}"
  location = var.region   # regional cluster — multi-AZ by default

  enable_autopilot = true

  # Workload Identity is enforced by Autopilot
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Private cluster — no public endpoint on nodes
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false   # true for fully private; needs Cloud Interconnect/VPN
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "/16"
    services_ipv4_cidr_block = "/22"
  }

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = var.admin_cidr
      display_name = "admin-network"
    }
  }

  deletion_protection = true
}
```

**Do:**
- Use a **regional** cluster (not zonal) for production — Autopilot spreads nodes across zones automatically.
- Enable `deletion_protection = true` to guard against accidental `terraform destroy`.
- Set a `master_authorized_networks_config` CIDR; don't leave the API server open to `0.0.0.0/0`.
- Use private nodes (`enable_private_nodes = true`) — nodes have no external IPs.

**Don't:**
- Use Autopilot for workloads that require privileged containers (DaemonSets with host network access, custom device plugins, specific node OS configurations) — those genuinely require Standard.
- Run Autopilot for GPU workloads — Autopilot supports T4/A100 GPUs but verify current Autopilot GPU node pool availability in the target region.
- Confuse "Autopilot is managed" with "Autopilot is less secure" — it is more opinionated and enforces hardening Standard allows you to skip.

## Edge cases / when the rule does NOT apply

- **Operators that require cluster-admin DaemonSets**: network plugins, security agents, or infrastructure DaemonSets that need host networking or privileged access require Standard.
- **Custom node machine types with local SSD or NUMA requirements**: Autopilot selects machine type automatically; Standard is required when specific hardware is needed.

## See also

- [`../agents/gcp-data-and-compute-engineer.md`](../agents/gcp-data-and-compute-engineer.md) — owns GKE cluster configuration and compute decisions.
- [`./no-service-account-key-files.md`](./no-service-account-key-files.md) — Autopilot enforces Workload Identity; this rule explains why that matters.

## Provenance

Derives from the `gcp-cloud` house opinion #6 ("Pick compute by operational burden; GKE Autopilot to cut ops") in `CLAUDE.md` §2. GKE Autopilot is Google's recommended default for new clusters per the GKE documentation (verified 2026-06-05).

---

_Last reviewed: 2026-06-05 by `claude`_

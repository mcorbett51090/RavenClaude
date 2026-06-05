# Use Cloud NAT for outbound internet from private instances — no public IPs

**Status:** Pattern
**Domain:** GCP networking
**Applies to:** `gcp-cloud`

---

## Why this exists

Assigning a public IP to a VM or GKE node for the sole purpose of outbound internet access violates the private-by-default principle and adds an unnecessary attack surface. Cloud NAT provides managed outbound internet connectivity for private instances — no external IP on the instance, no inbound ports opened, no NAT instance to patch. It scales automatically and logs outbound connections via Cloud Logging. Private instances behind Cloud NAT can reach package registries, APIs, and public endpoints without any incoming exposure.

## How to apply

```hcl
# Terraform — Cloud NAT on the VPC
resource "google_compute_router" "this" {
  name    = "router-${var.region}-${var.env}"
  region  = var.region
  network = google_compute_network.this.id
}

resource "google_compute_router_nat" "this" {
  name                               = "nat-${var.region}-${var.env}"
  router                             = google_compute_router.this.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"   # use ALL_TRANSLATIONS to debug; ERRORS_ONLY for prod
  }

  min_ports_per_vm = 64
}
```

GKE cluster with no public node IPs:
```hcl
resource "google_container_cluster" "this" {
  # ...
  private_cluster_config {
    enable_private_nodes = true
    # nodes get RFC1918 IPs only; Cloud NAT provides egress
  }
}
```

**Do:**
- Set `min_ports_per_vm` based on expected concurrent outbound connections per instance; default is 64 — increase for high-concurrency services.
- Use `AUTO_ONLY` for NAT IP allocation in most cases; `MANUAL_ONLY` only when you need stable outbound IPs for IP allow-listing by an external partner.
- Enable NAT logging at `ERRORS_ONLY` in prod — `ALL_TRANSLATIONS` is valuable for debugging but expensive at scale.
- Pair with `Private Google Access` on each subnet for Google API calls without leaving the Google network.

**Don't:**
- Assign external IPs to VMs just for `apt-get` or `docker pull` — Cloud NAT handles this.
- Use a NAT instance/VM (self-managed) — Cloud NAT is managed, scales automatically, and requires no patching.
- Set `min_ports_per_vm` too low for high-connection services — port exhaustion causes connection failures.

## Edge cases / when the rule does NOT apply

- **Services that need a stable outbound IP** for an external partner's IP allow-list: use Cloud NAT with `MANUAL_ONLY` and a reserved static IP to provide a predictable egress IP.
- **Internal service-to-service calls within the VPC or to Google APIs**: use Private Google Access and Shared VPC — Cloud NAT is for internet-bound traffic only.

## See also

- [`../agents/gcp-network-engineer.md`](../agents/gcp-network-engineer.md) — owns VPC design and Cloud NAT configuration.
- [`./private-by-default-gcp.md`](./private-by-default-gcp.md) — Cloud NAT is the implementation mechanism for private-by-default egress.

## Provenance

Derives from the `gcp-network-engineer` remit in `CLAUDE.md` §1: "Cloud NAT, Cloud Load Balancing" and the house opinion #5 ("Private by default; no public IPs on VMs unless required"). Standard GCP networking pattern from the VPC best practices guide.

---

_Last reviewed: 2026-06-05 by `claude`_

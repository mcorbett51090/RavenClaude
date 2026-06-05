# Use Shared VPC for centralized multi-project networking

**Status:** Pattern
**Domain:** GCP networking / org design
**Applies to:** `gcp-cloud`

---

## Why this exists

When multiple GCP projects need to communicate over a private network, the naive approach is creating a VPC per project and peering them. VPC peering is non-transitive — project A peers with B, B peers with C, but A cannot reach C without a direct peering. At scale, the mesh becomes unmanageable, CIDR planning is duplicated across projects, and network security policies are fragmented. Shared VPC solves this by letting a host project own the network and service projects attach to it. One network admin team manages subnets and firewall rules centrally; service teams deploy into the shared subnets without managing network infrastructure.

## How to apply

```hcl
# Terraform — enable Shared VPC host project
resource "google_compute_shared_vpc_host_project" "host" {
  project = var.host_project_id
}

# Attach service projects to the host
resource "google_compute_shared_vpc_service_project" "service_a" {
  host_project    = var.host_project_id
  service_project = var.service_project_a_id
}

# Grant the service project's compute SA access to the shared subnet
resource "google_compute_subnetwork_iam_member" "service_a_compute" {
  project    = var.host_project_id
  region     = var.region
  subnetwork = google_compute_subnetwork.app_subnet.name
  role       = "roles/compute.networkUser"
  member     = "serviceAccount:${var.service_project_a_number}@cloudservices.gserviceaccount.com"
}
```

**Do:**
- Keep the host project dedicated to networking — no workload resources in the host project itself.
- Grant `roles/compute.networkUser` on specific subnets to the service project's compute service account, not to the entire network.
- Manage firewall rules in the host project only — service projects cannot create host-network firewall rules.
- Use a separate subnet per service project or workload type for traffic isolation and tagging.

**Don't:**
- Use VPC peering instead of Shared VPC when the goal is centralized network governance — peering doesn't centralize admin or firewall policies.
- Grant `roles/compute.networkAdmin` to service project teams — they get `networkUser` on their subnets only.
- Put the host project in the same folder as service projects — separate it organizationally to prevent accidental modification by service teams.

## Edge cases / when the rule does NOT apply

- **Single-project workloads**: a local VPC is appropriate; Shared VPC overhead is not justified.
- **Isolated projects with no cross-project connectivity requirement**: use Private Service Connect for specific service exposure rather than Shared VPC.

## See also

- [`../agents/gcp-network-engineer.md`](../agents/gcp-network-engineer.md) — owns Shared VPC design and subnet allocation.
- [`./use-the-resource-hierarchy.md`](./use-the-resource-hierarchy.md) — the host project belongs in a dedicated network folder in the hierarchy.

## Provenance

Derives from the `gcp-network-engineer` remit in `CLAUDE.md` §1: "Shared VPC design" and the `gcp-cloud` house opinion #1 ("Use the resource hierarchy — folders and projects for blast radius and policy"). Standard GCP enterprise networking pattern from the GCP networking best practices guide.

---

_Last reviewed: 2026-06-05 by `claude`_

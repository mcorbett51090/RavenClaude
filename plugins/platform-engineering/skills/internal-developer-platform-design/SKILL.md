---
name: internal-developer-platform-design
description: "Design an internal developer platform as a product: map the cognitive load worth removing, define the thinnest viable platform and its self-service API, pick the Team Topologies operating model, and draw the build-vs-buy line per layer with explicit non-goals."
---

# Internal Developer Platform Design

## Start from cognitive load, not tools
The platform exists to reduce the cognitive load on stream-aligned teams (Team Topologies). List the toil/decisions teams re-derive; the platform's job is to remove the highest-leverage ones. If you can't name the load a capability removes, it doesn't ship.

## Thinnest viable platform (TVP)
Pave the **smallest** set of golden paths that removes the **most** load — often one well-paved "new service" or "get an environment" path, not a 12-capability portal. Ship it, get usage, then expand. Boiling the ocean is the default failure mode.

## The platform API is a contract
"Self-service" = a team gets what it needs with **no human in the loop**. Define the interface per capability (portal action / CLI / templated PR / API) and version it. A capability that ends in a ticket is a queue, not an API.

## Operating model (Team Topologies)
Stream-aligned teams consume; a **product-managed** platform team provides X-as-a-Service; enabling teams uplift. The platform team that takes provisioning tickets is an ops team renamed — the deliverable is self-service capability, not a faster queue.

## Build vs buy per layer
Buy/adopt-OSS the undifferentiated (portal, catalog, scaffolder); build only the thin glue that encodes your opinions. Name the real TCO of self-hosting (Backstage is a team you staff). Record the exit posture if the choice is wrong.

## Output
A thinnest-viable-platform brief: paths to pave first (+ load each removes), the platform API, the operating model, build-vs-buy per layer, explicit non-goals, and the adoption baseline. Hand specific builds to `devops-cicd` / `cloud-native-kubernetes` / `terraform-iac`.

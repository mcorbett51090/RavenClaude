---
name: terraform-state-safety
description: "Design safe remote Terraform/OpenTofu state: remote backend with locking, encryption, and versioning; isolate state by blast radius; keep secrets out (and treat the whole file as sensitive); and do state surgery only with a snapshot."
---

# Terraform State Safety

## The backend
**Remote + locked + encrypted + versioned.** Locking stops concurrent-apply corruption; encryption protects the secrets state captures; versioning enables recovery.

## Isolate by blast radius
Network / data / app in **separate states** — a risky app apply can't touch the VPC. One giant state = one giant blast radius.

## Secrets
Mark `sensitive` + source from a manager. Providers still write some values to state, so **treat the whole file as sensitive** (encrypt + restrict access).

## State surgery
`import` / `state mv` / `state rm`: **snapshot first**, one op, verify with a plan.

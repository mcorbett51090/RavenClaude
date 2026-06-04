---
name: gcp-least-privilege-iam
description: "Write least-privilege GCP IAM: predefined/custom roles over primitive (Owner/Editor/Viewer), service accounts + Workload Identity Federation instead of exported key files, IAM Conditions, and binding at the correct hierarchy level."
---

# GCP Least-Privilege IAM

## Roles
**Predefined/custom**, never primitive in prod. Owner/Editor/Viewer are blunt.

## No key files
**Workload Identity Federation** (external/CI), **Workload Identity** (GKE pods). Attach an identity; don't download a JSON key. Disable SA-key creation via **org policy**.

## Scope
Bind at the right node (project/folder/org). **IAM Conditions** for time/resource scoping.

## Route the verdict
Produce the binding + residual risk; `security-engineering`/`security-reviewer` clears sensitive grants.

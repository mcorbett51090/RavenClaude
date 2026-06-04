---
name: gitops-delivery
description: "Stand up GitOps continuous delivery with Argo CD or Flux: desired-state-in-Git repo structure (app-of-apps, environment overlays), promotion-by-PR, drift detection/self-heal posture, and secrets without plaintext."
---

# GitOps Delivery

**Purpose:** make Git the single source of truth and a reconciler enforce it.

## Repo structure
- **App-of-apps**: a root Application manages child Applications.
- **Environments** as overlays/directories; a promotion is a PR bumping the image **digest** in the next env.

## Drift
Per-app: **auto-heal** (reconciler reverts) or **alert-and-wait**. Never let drift silently persist. A console change to prod is a bug in the process.

## Secrets
**Sealed-secrets** (encrypted at rest in Git) or **external-secrets** (a pointer to a manager). Plaintext secrets in a GitOps repo are a breach — never.

## Rollback
`git revert` + reconcile. That is the cleanest rollback story available.

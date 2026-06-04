---
description: "Stand up GitOps delivery: app-of-apps repo structure, environment promotion by PR, drift posture, and secrets without plaintext."
argument-hint: "[cluster + repos + environments]"
---

You are running `/devops-cicd:setup-gitops`. Use `gitops-engineer` + the `gitops-delivery` skill.

## Steps
1. Choose Argo CD or Flux and justify briefly.
2. Lay out the app-of-apps repo structure with environment overlays.
3. Define the promotion-by-PR flow (bump the image digest).
4. Set the drift posture per app (auto-heal vs alert).
5. Pick the secrets approach (sealed-secrets / external-secrets) — no plaintext.
6. Emit the repo tree + Application manifests sketch + the Structured Output block.

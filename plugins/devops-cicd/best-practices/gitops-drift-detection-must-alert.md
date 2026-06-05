# GitOps drift detection must alert, not just log

**Status:** Absolute rule
**Domain:** GitOps continuous delivery
**Applies to:** `devops-cicd`

---

## Why this exists

A GitOps reconciler that silently allows drift defeats the purpose of desired-state delivery. If a cluster resource diverges from Git and nobody is paged, you have a two-source-of-truth system — the dangerous one wins. Drift that is only discoverable by looking at a dashboard is drift that persists for days.

## How to apply

Configure your reconciler (Argo CD / Flux) to fire an alert — routed to your incident channel — whenever any managed resource has been out-of-sync beyond your tolerance window.

**Argo CD — Prometheus alert example:**

```yaml
# Fires when any app has been out-of-sync for more than 5 minutes
- alert: ArgoCDAppOutOfSync
  expr: |
    argocd_app_info{sync_status="OutOfSync"} == 1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ArgoCD app {{ $labels.name }} is out-of-sync"
    runbook: "https://wiki.example.com/runbooks/argocd-drift"
```

**Flux — set up a notification provider:**

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Alert
metadata:
  name: drift-alert
spec:
  eventSeverity: error
  eventSources:
    - kind: Kustomization
      name: "*"
  providerRef:
    name: slack-ops
```

**Do:**
- Set a max sync-lag tolerance (e.g. 5 minutes) and page beyond it.
- Distinguish expected drift windows (deploy in-flight) from unexpected drift (manual `kubectl` edit).
- Auto-remediate with self-heal enabled; alert if self-heal fails.
- Include a runbook link in every drift alert.

**Don't:**
- Accept "drift is visible in the Argo UI" as the detection story — nobody watches UIs all day.
- Set `selfHeal: false` in prod without a compensating manual-drift alert.
- Page for every normal sync cycle — use a time-threshold to suppress in-progress deploys.

## Edge cases / when the rule does NOT apply

Non-prod clusters where manual experimentation is intentionally allowed. Even there, log drift and review it weekly.

## See also

- [`../agents/gitops-engineer.md`](../agents/gitops-engineer.md) — owns Argo CD / Flux configuration and drift detection.
- [`./deploy-rollback-before-you-ship.md`](./deploy-rollback-before-you-ship.md) — drift detection and rollback are complementary safety nets.

## Provenance

Codifies house opinion §4 ("Git is the source of truth for desired state — a change to prod that isn't a merged commit is drift; the reconciler should fight it, and you should see it") from CLAUDE.md §2. Argo CD and Flux alerting are standard practices from their respective operator guides.

---

_Last reviewed: 2026-06-05 by `claude`_

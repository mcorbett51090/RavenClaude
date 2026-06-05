---
name: helm-chart-authoring
description: "Step-by-step guide for authoring a production-grade Helm chart from scratch — directory layout, values design, template hygiene, helpers, chart tests, and lint/security gates — so workloads are packaged reproducibly and safely promoted across environments."
---

# Helm Chart Authoring

## When to invoke

Use when packaging a Kubernetes workload as a Helm chart for the first time, or when an existing chart needs a structural overhaul (template sprawl, missing defaults, no tests).

## Step 1 — Directory skeleton

```
charts/my-service/
├── Chart.yaml          # name, version (semver), appVersion
├── values.yaml         # all defaults — must be complete and runnable
├── values-prod.yaml    # prod overrides only (NOT defaults)
├── templates/
│   ├── _helpers.tpl    # named templates: labels, selector, fullname
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   ├── serviceaccount.yaml
│   ├── networkpolicy.yaml
│   └── NOTES.txt
└── tests/
    └── connection-test.yaml   # helm test job
```

`Chart.yaml` minimum:
```yaml
apiVersion: v2
name: my-service
version: 1.0.0          # chart version (semver)
appVersion: "0.1.0"     # application version (informational)
```

## Step 2 — Values design principles

1. **Everything configurable, nothing required.** `values.yaml` must produce a valid, runnable chart on `helm install` with no extra flags.
2. **Structured objects over flat keys.** Prefer `image.repository / image.tag` over `imageRepository / imageTag`.
3. **Resources block is always present** with sane defaults (not zero):
   ```yaml
   resources:
     requests:
       cpu: 100m
       memory: 128Mi
     limits:
       cpu: 500m
       memory: 256Mi
   ```
4. **Probes block with defaults off, override per environment.** A chart that ships with wrong probes for unknown apps is worse than no probes.
5. Document every value with an inline comment.

## Step 3 — _helpers.tpl patterns

```
{{- define "my-service.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "my-service.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "my-service.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

Use `include` (not `template`) in templates so output can be piped through `indent`.

## Step 4 — Template hygiene checklist

| Item | Pattern |
|---|---|
| Image tag is never `latest` | `image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"` |
| `imagePullPolicy` defaults to `IfNotPresent` | Override to `Always` only for mutable tags |
| `securityContext` set on pod and container | `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false` |
| `serviceAccountName` explicit | Even if `default`, be explicit |
| Probes templated from values | Never hardcoded paths |
| PodDisruptionBudget included | `minAvailable: 1` default |
| HPA min/max from values | Never hardcoded |

## Step 5 — Chart tests

```yaml
# tests/connection-test.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-service.fullname" . }}-test-connection"
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
    - name: wget
      image: busybox
      command: ["wget", "--timeout=5", "-O", "/dev/null",
                "http://{{ include "my-service.fullname" . }}:{{ .Values.service.port }}/healthz"]
```

Run with `helm test <release>` after install/upgrade in CI.

## Step 6 — Lint and security gates

```bash
helm lint charts/my-service/ --values charts/my-service/values-prod.yaml

# Strict schema validation
helm template charts/my-service/ | kubeval --strict

# Security misconfig scan
helm template charts/my-service/ | kubesec scan -

# OPA/Conftest policy gates
helm template charts/my-service/ | conftest test -
```

Add these as CI steps before pushing to a chart registry (OCI or Chartmuseum).

## Pitfalls

- **`latest` image tag in `values.yaml`** — unpinned images break reproducibility and rollback.
- **No `_helpers.tpl`** — copy-pasted label blocks across templates drift and cause selector mismatches on upgrade.
- **`values.yaml` missing resource defaults** — a chart installable with 0 CPU request schedules a pod the scheduler can't reason about.
- **`required ""` on every value** — forces callers to spell out things that have sane defaults; reserve `required` for genuinely unconfigurable values (e.g., a cluster-specific hostname).
- **No chart tests** — `helm install` succeeding means the Kubernetes API accepted the manifests, not that the app is running.

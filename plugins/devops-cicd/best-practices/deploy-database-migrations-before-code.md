# Run database migrations before the new code deploys

**Status:** Absolute rule
**Domain:** Release engineering / deploy safety
**Applies to:** `devops-cicd`

---

## Why this exists

Deploying code that expects a new schema before the migration runs is how you get runtime errors in production for the duration of the rollout. Deploying a migration that removes a column while the old code is still reading it is how you break the version that's still running. The expand/contract pattern (schema first, code after; removal only after old code is gone) is the only safe ordering for rolling deployments.

## How to apply

Treat database migrations as a distinct deploy step that runs before the new application code version becomes live. In a Kubernetes rolling update, run the migration as an init container or a pre-upgrade Job. In a blue-green deploy, run migrations against the shared database before traffic shifts.

```yaml
# Kubernetes: migration Job runs before deployment rollout
apiVersion: batch/v1
kind: Job
metadata:
  name: my-service-migrate-{{ .Release.Revision }}
  annotations:
    "helm.sh/hook": pre-upgrade,pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  backoffLimit: 0          # fail the hook on first error; don't silently retry
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          command: ["./migrate", "up"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: my-service-db
                  key: url
```

Expand/contract pattern:
1. **Expand migration** — add new column nullable, add new table. Old code ignores it, new code uses it.
2. **Deploy new code** — reads and writes both old and new column/schema.
3. **Contract migration** — after all old code is gone, drop the deprecated column/table.

**Do:**
- Run migrations in a pre-deploy hook or Job, not inside the application start-up path.
- Write expand migrations first, code second, contract migrations last (after full rollout).
- Gate the deploy on migration success; a failed migration must halt the rollout.
- Make migrations idempotent (use `IF NOT EXISTS`, migration tracking tables like Flyway/Liquibase).

**Don't:**
- Run `ALTER TABLE DROP COLUMN` while any version of the code still reads that column.
- Bundle the migration into application startup (`alembic upgrade head` in `CMD`) for services with multiple replicas — parallel startup races.
- Add non-nullable columns without a default to a live table (blocks writes during the migration lock).

## Edge cases / when the rule does NOT apply

Single-instance services with a downtime maintenance window can migrate inline during startup. The rule is non-negotiable for rolling/canary/blue-green deployments where old and new code coexist.

## See also

- [`../agents/release-engineer.md`](../agents/release-engineer.md) — owns the deploy ordering and progressive delivery strategy.
- [`./deploy-rollback-before-you-ship.md`](./deploy-rollback-before-you-ship.md) — a rolled-back code deployment may face a forward-migrated schema; design for it.

## Provenance

Codifies the expand/contract database migration pattern as described in Martin Fowler's "Evolutionary Database Design" and the Kubernetes pre-upgrade Helm hook pattern.

---

_Last reviewed: 2026-06-05 by `claude`_

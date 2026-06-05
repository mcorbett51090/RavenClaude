# Make every pipeline stage idempotent

**Status:** Absolute rule
**Domain:** CI/CD pipeline design
**Applies to:** `devops-cicd`

---

## Why this exists

A CI/CD stage that cannot be safely re-run without side-effects turns a transient infrastructure hiccup into a production incident. When a stage halfway through deploys to an environment, uploads partial artifacts, or creates duplicate database records because it wasn't designed for re-entry, the safe recovery path disappears. Idempotent stages can be retried automatically, reducing mean time to recovery and enabling fearless automation.

## How to apply

Design every stage to produce the same result whether it runs once or a hundred times. This means: uploading artifacts should overwrite rather than append, database schema changes should use conditional DDL, and resource creation should check existence first.

```yaml
# GitHub Actions: safe artifact upload with content-addressed naming
- name: Upload build artifact
  uses: actions/upload-artifact@v4
  with:
    name: app-${{ github.sha }}   # SHA makes the name deterministic and unique
    path: dist/
    if-no-files-found: error
    overwrite: true               # idempotent: re-run is safe
```

```sql
-- Idempotent migration: safe to run twice
CREATE TABLE IF NOT EXISTS orders (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Do:**
- Name artifacts by content hash or commit SHA so re-uploads replace the same slot.
- Use `IF NOT EXISTS` / `IF EXISTS` guards in schema migrations.
- Prefer upsert (`INSERT ... ON CONFLICT DO UPDATE`) over insert in seed/fixture scripts.
- Mark stages that have external side-effects (sending emails, triggering webhooks) as `needs` on a completion gate to prevent double-fire.

**Don't:**
- Append to a changelog or release notes file inside a pipeline step without a guard.
- Create cloud resources without checking whether they already exist (use Terraform or equivalent).
- Send notification webhooks in a step that may retry automatically.

## Edge cases / when the rule does NOT apply

Intentional exactly-once semantics (e.g., publishing a release to a package registry where a version must not be overwritten) require a version-existence check before the step, then a separate gate — the step itself still needs to be re-runnable after that gate passes.

## See also

- [`../agents/pipeline-engineer.md`](../agents/pipeline-engineer.md) — owns CI stage design and retry policy.
- [`./build-fast-gates-first.md`](./build-fast-gates-first.md) — stage ordering affects which retries are cheap.

## Provenance

Codifies standard reliability engineering practice: idempotent operations are a prerequisite for safe automation at scale, referenced in Google SRE practices and Argo CD's reconciliation model.

---

_Last reviewed: 2026-06-05 by `claude`_

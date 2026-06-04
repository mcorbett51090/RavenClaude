---
name: secrets-management
description: "Manage secrets safely: detect them in code/config/logs, vault them, federate with short-lived credentials, rotate on a schedule, and treat any committed secret as compromised (rotate, don't just delete)."
---

# Secrets Management

**Purpose:** keep secrets out of code and short-lived.

## Detect
Secret scanning in CI + pre-commit. Scan code, config, **and logs**.

## Store & federate
- Secrets in a **manager/vault**, referenced at runtime.
- Prefer **OIDC/workload-identity** short-lived credentials over long-lived keys.

## Rotate
On a schedule and on personnel change. A committed secret is **compromised** — rotate it, deleting the commit is not enough (it's in history + clones).

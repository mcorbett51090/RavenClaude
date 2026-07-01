# Config-as-code is the source of truth; the device is a render target

**Status:** Strong default
**Domain:** NetDevOps / operations
**Applies to:** `networking-engineering`

---

## Why this exists

When the running config on the device *is* the source of truth, every device becomes a
snowflake: changes are made by hand, never reviewed, and drift silently until an outage
reveals that no two devices agree. Treating intent-as-code as authoritative — structured
data and templates in version control, reconciled onto devices and continuously compared —
turns network change into something reviewable, testable, and repeatable, and turns drift
from a thing you discover during an incident into a thing you detect on a schedule.

## How to apply

**Do:**
- Keep **intent as structured data + templates in version control**; render device config from it. The device is reconciled to intent, not the other way around.
- **Validate in CI before merge**: lint the render, diff/dry-run against current state, run a virtual-topology test where the change is risky.
- **Detect drift continuously** and treat a delta as either unauthorized change (investigate) or unmodeled intent (bring into source of truth).
- **Vault credentials/secrets** — the repo holds intent, never passwords.

**Don't:**
- Hand-edit production devices as the primary change mechanism.
- Apply an automated change fleet-wide with no dry-run and no staged rollout — automation amplifies mistakes.
- Store device credentials in the config repo.

## Edge cases / when the rule does NOT apply

- **Emergency break-fix during an active outage** — a manual change to restore service is legitimate; the discipline is to *back-port it into source of truth immediately* so it doesn't become permanent drift.
- **Very small, stable networks** where the tooling overhead genuinely exceeds the benefit — but even there, keep configs in version control.

## See also
- [`../skills/automate-network-with-netdevops/SKILL.md`](../skills/automate-network-with-netdevops/SKILL.md)
- [`./no-change-without-a-rollback-path.md`](no-change-without-a-rollback-path.md)

## Provenance
Codifies the `network-implementation-engineer` house opinion "make config-as-code the source of truth" and NetDevOps practice. The pipeline that runs it is owned by `devops-cicd`. Last reviewed 2026-07-01.

---

_Last reviewed: 2026-07-01 by `claude`_

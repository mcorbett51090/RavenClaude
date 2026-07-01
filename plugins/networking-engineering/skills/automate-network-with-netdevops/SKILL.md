---
name: automate-network-with-netdevops
description: Stand up a NetDevOps workflow — a network source of truth, templated intent (Jinja/data models), CI validation (lint, dry-run/diff, pre-merge test), staged rollout, and drift detection — so network config is managed as code instead of hand-edited on devices. Returns the pipeline design, the source-of-truth model, and the safe-rollout flow. Used by `network-implementation-engineer` (primary).
---

# Skill: automate-network-with-netdevops

> **Invoked by:** `network-implementation-engineer` (primary).
>
> **When to invoke:** "manage these configs as code"; "how do I detect config drift?"; "automate this repetitive change across the fleet"; "add CI to network changes".
>
> **Output:** a NetDevOps pipeline design — source of truth, templating, CI validation, staged rollout, drift detection — sized to the team's tooling and risk tolerance.

## Procedure

1. **Establish a single source of truth.** Intent (the *what*) lives as structured data in version control — device inventory, roles, VLAN/prefix allocations — not in the running config. The device becomes a render target reconciled to intent. Optionally back this with an IPAM/source-of-truth system.
2. **Template the intent into config.** Render device config from the data model + role templates (Jinja2 or a vendor abstraction). One change to the model regenerates every affected device consistently — this is what kills copy-paste drift.
3. **Validate in CI before merge.** Lint/parse the rendered config, produce a **diff/dry-run** against the current device state, and run pre-merge checks (does it still summarize? any shadowed ACL? does the pipeline's test topology still converge?). A change that fails CI never reaches a device.
4. **Roll out in stages.** Lab/virtual topology → one device → a canary blast-radius → the fleet, each gated on post-change validation. Never a fleet-wide simultaneous apply for anything that can partition the network.
5. **Detect drift continuously.** Periodically compare running config to intended; a delta is either an unauthorized change (investigate) or unmodeled intent (bring into source of truth). Drift discovered during an outage is the failure mode this prevents.
6. **Keep secrets and state out of the repo.** Credentials in a secrets manager/vault, not in inventory; the repo holds intent, not passwords.

## Quick map

| Capability | Purpose | Failure it prevents |
|---|---|---|
| Source of truth (data in VCS) | One authoritative intent | Divergent per-device snowflakes |
| Templated render | Consistency at scale | Copy-paste fat-finger across the fleet |
| CI diff/dry-run | Catch it before the device | A bad change reaching production |
| Staged rollout | Bound the blast radius | A fleet-wide simultaneous outage |
| Drift detection | Find unauthorized/unmodeled change | Discovering drift during an incident |

## Guardrails
- **Dry-run/diff is non-negotiable** — apply-then-hope on network gear partitions networks.
- **Never store device credentials in the config repo** — vault them.
- **Automation amplifies mistakes** — a bad template applied fleet-wide is worse than a bad manual change; gate it in CI and stage the rollout.
- Tooling specifics (frameworks, controllers, their features) are volatile — verify and cite a retrieval date ([`../../knowledge/networking-tooling-2026.md`](../../knowledge/networking-tooling-2026.md)). The pipeline that *runs* this is `devops-cicd`.

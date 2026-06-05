# Governance & RLS Plan — <site / project / data source>

> Fill-in plan for a governed Tableau site and its Row-Level Security. Owned by `tableau-admin`.
> **RLS is a security control — the verdict escalates to `ravenclaude-core/security-reviewer`.**
> Date: <YYYY-MM-DD> · Author: <name> · Platform: <Tableau Cloud / Server + version>

## 1. Governance skeleton

| Layer | Decision |
|---|---|
| Site(s) | <tenancy boundary — when a new site vs a new project> |
| Project hierarchy | <locked projects; group-grant at project level> |
| Default posture | **Deny by omission** (never start from "everyone can see it") |
| Certified data sources | <the governed grain; separated + published, RLS lives here> |

## 2. Permission grant matrix (read off, don't reverse-engineer)

| Project | Group | Capabilities | Locked? |
|---|---|---|---|
| | | <View / Connect / Web Edit / Download / …> | yes |

> Per-content permission overrides are the anti-pattern — record any and time-box them with a reason.

## 3. RLS design

| Field | Value |
|---|---|
| Two users, different rows? | <the access decision in observable terms> |
| Entitlement key | <tenant_id / region / customer_id> |
| Mechanism | <user filter (convenience, leaky) · entitlements-table + data-policy (enforced) · separate workbooks> |
| Default choice | **entitlements-table + row-level data policy** on the published data source |
| Data Management add-on required? | <data policies need it — `[verify-at-build]`> |
| How identity → entitlement key resolves | <USERNAME() → entitlements table → key> |

## 4. Security escalation (mandatory for RLS)

- **Populations:** <who sees what>
- **Entitlement key & join:** <how a row is scoped>
- **Cost of a single-row leak:** <impact>
- **Handed to:** `ravenclaude-core/security-reviewer` on <date>

## 5. Promotion & watch-outs

- **dev→test→prod path:** <Migration SDK (Server→Cloud) / Content Migration Tool (site↔site) / REST>
- **Volatile claims to re-verify `[verify-at-build]`:** <Data Management gating, Cloud vs Server feature parity>

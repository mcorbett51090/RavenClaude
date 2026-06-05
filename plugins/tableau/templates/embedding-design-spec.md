# Embedding Design Spec — <app / portal name>

> Fill-in spec for the [`embedding-connected-apps-jwt`](../skills/embedding-connected-apps-jwt/SKILL.md)
> skill. The supported path is **Connected App (Direct Trust) + server-minted JWT + Embedding API v3** —
> never trusted tickets or embedded creds. **Auth verdict escalates to `ravenclaude-core/security-reviewer`.**
> Date: <YYYY-MM-DD> · Author: <name> · Platform: <Tableau Cloud / Server + version>

## 1. Embedding context

| Field | Value |
|---|---|
| Where embedded | <app / portal> |
| Isolation requirement | <per-user / per-tenant / none-public> |
| Viz(es) | <workbook + view> |

## 2. Connected App (Direct Trust)

| Field | Value |
|---|---|
| Created/enabled by | <site/server admin> |
| Client ID (`iss`) | |
| Secret ID (`kid`) | |
| Secret storage | <secret-manager reference — NEVER a literal> |
| Rotation cadence | |

## 3. JWT claims (minted server-side)

| Claim | Value |
|---|---|
| `iss` | <client ID> |
| `kid` (header) | <secret ID> |
| `sub` | <per-user/per-tenant identity — NOT a shared service account> |
| `aud` | `tableau` `[verify-at-build]` |
| `exp` | <short — minutes> |
| `scp` | **array** — `["tableau:views:embed"]` `[verify-at-build]` |

## 4. RLS binding (the load-bearing half)

- **Entitlement key:** <tenant_id / region>
- **How `sub` maps to the key:** <entitlements table + data policy>
- **Confirmed:** the JWT identity and the RLS key are designed as ONE unit.

## 5. Isolation test (two identities, not one)

- [ ] Tenant A cannot see tenant B's rows
- [ ] A wrong / absent `sub` fails closed (no data, not all data)
- [ ] No URL/dashboard filter substituted for RLS

## 6. Security escalation

- **Threat model handed to `ravenclaude-core/security-reviewer`** on <date>: populations, entitlement key, secret storage + rotation, token lifetime, cost of a cross-tenant leak.

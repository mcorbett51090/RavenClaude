# Entra identity design — <WORKLOAD>

> Owned by `entra-identity-engineer`. See `knowledge/entra-identity-and-access.md`. **Routes through `ravenclaude-core/security-reviewer`.**

## Workload identity (passwordless first)
| Workload | Identity | Why |
|---|---|---|
| Azure-hosted app | managed identity (system / user-assigned) | Azure manages creds |
| CI/CD or external | workload identity federation | no secret to rotate |
| Legacy (last resort) | app registration + secret/cert in Key Vault | rotate |

- WIF federated-credential: issuer / subject / audience (case-sensitive match) = <values>

## Authorization
- RBAC role assignments (scoped to RG/resource, **not** sub/MG): <role → scope>
- PIM for privileged roles: <which roles, approval, max duration>
- No standing Owner.

## CIAM (if customer-facing)
- **Entra External ID** (not new B2C — B2C is end-of-sale): sign-up flows, IdPs, custom domain
- Migrating an existing B2C tenant? note HSC coexistence + the 2026 P2-retirement.

## Conditional Access (with security-reviewer)
- <risk / MFA / device posture policies>

## Security review
- [ ] Reviewed by `ravenclaude-core/security-reviewer` (mandatory)

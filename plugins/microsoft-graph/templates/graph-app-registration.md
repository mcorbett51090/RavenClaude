> Use this template to document a Microsoft Graph app registration — permissions, auth flow, credential type, and the security sign-off checklist before deploying to production.

# Graph App Registration: [App Name]

## Metadata

| Field | Value |
|---|---|
| Application name | [Display name in Entra portal] |
| Application (client) ID | [GUID — from Entra app registration] |
| Tenant ID | [GUID] |
| Owner / team | [Name / Team] |
| Environment | [Dev / Test / Production] |
| Registration date | [YYYY-MM-DD] |
| Last reviewed | [YYYY-MM-DD] |

---

## App purpose

**What does this app do with Microsoft Graph?**

[e.g., "Reads user calendar availability to schedule bookings. Sends confirmation emails on behalf of service accounts. No directory write access."]

**Is a user signed in at runtime?**

[ ] Yes — delegated permissions  
[ ] No — application (daemon) permissions  
[ ] Both — the app has both delegated and app-only flows

---

## Authentication flow

| Flow | Selected | When used |
|---|---|---|
| Auth code + PKCE | [ ] | Interactive user sign-in (web/SPA) |
| Client credentials | [ ] | Daemon / background job (no user) |
| On-behalf-of (OBO) | [ ] | Downstream API calling Graph on behalf of a user |
| Device code | [ ] | CLI / device without a browser |

---

## Credentials

| Type | Selected | Notes |
|---|---|---|
| Certificate (recommended) | [ ] | Thumbprint: [X]; expiry: [YYYY-MM-DD]; stored in: [Key Vault / cert store] |
| Client secret | [ ] | Expiry: [YYYY-MM-DD]; stored in: [Key Vault / env var] — NEVER in code |

**Rotation schedule:** [e.g., Certificate renewed 30 days before expiry via Key Vault auto-rotation]

---

## Permissions

### Delegated permissions (user-context)

| Permission | Justification | Admin consent required? |
|---|---|---|
| [e.g., Calendars.ReadWrite] | [Read/write signed-in user's calendar for booking] | [ ] |
| [e.g., Mail.Send] | [Send confirmation emails as the signed-in user] | [ ] |
| | | |

### Application permissions (daemon / app-only)

| Permission | Justification | Admin consent obtained? |
|---|---|---|
| [e.g., User.Read.All] | [Read all user profiles for directory sync] | [ ] |
| | | |

**Least-privilege review completed:** [ ] Yes / [ ] No — document any scope that could not be narrowed and why.

---

## API usage summary

| Graph resource | Operation | Endpoint | Volume (est.) |
|---|---|---|---|
| [e.g., /users] | Read | GET /v1.0/users | [X req/day] |
| [e.g., /me/sendMail] | Write | POST /v1.0/me/sendMail | [X req/day] |

---

## Throttling and resilience plan

- Retry-After handling: [ ] SDK built-in / [ ] Custom handler (see `skills/throttling-backoff-handler/SKILL.md`)
- Paging: [ ] `@odata.nextLink` followed to exhaustion
- $batch: [ ] Used for [X] parallel operations
- Rate estimate vs known throttle limit: [e.g., 500 req/day vs 12 000 req/10-min limit — well within budget]

---

## Security sign-off checklist

- [ ] No application `.ReadWrite.All` scope without documented justification and security review.
- [ ] Client secret (if used) stored in Key Vault — not in code or config file.
- [ ] Certificate expiry alert configured.
- [ ] Permissions match this doc (verified in Entra portal → App registrations → API permissions).
- [ ] Tested with a non-admin account (admin accounts bypass some permission checks).
- [ ] Escalated to `ravenclaude-core/security-reviewer` for any tenant-wide application permission.

**Security reviewer sign-off:** [Name] [Date]

---

## Change log

| Date | Change | Author |
|---|---|---|
| [YYYY-MM-DD] | [Initial registration] | [Name] |
| | | |

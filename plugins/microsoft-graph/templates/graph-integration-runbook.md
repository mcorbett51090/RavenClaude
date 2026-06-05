> Use this template to document the operational runbook for a Microsoft Graph integration — deployment steps, health checks, known throttle patterns, incident response, and credential rotation procedures.

# Graph Integration Runbook: [Integration Name]

## Metadata

| Field | Value |
|---|---|
| Integration name | [e.g., HR Directory Sync, Teams Bot] |
| App registration | [App name + client ID] |
| Environments | [Dev / Test / Production URLs] |
| On-call owner | [Name / team / PagerDuty service] |
| Last reviewed | [YYYY-MM-DD] |
| Runbook version | [1.0] |

---

## Architecture overview

[1–3 sentence description of what this integration does and which Graph workloads it touches.]

**Key components:**

| Component | Technology | Location |
|---|---|---|
| Auth layer | [MSAL / SDK / custom] | [App service / function / container] |
| Graph calls | [SDK / REST] | [Service name] |
| State store (delta links, subscriptions) | [Redis / SQL / Table Storage] | [Resource name] |
| Secret store | [Azure Key Vault / Secrets Manager] | [Vault name] |

---

## Deployment checklist

- [ ] App registration exists in Entra for the target environment.
- [ ] Required permissions granted and admin consent given (see `graph-app-registration.md`).
- [ ] Certificate (or secret) loaded in Key Vault; expiry alert configured.
- [ ] Environment variables set: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_CERTIFICATE_PATH` (or equivalent).
- [ ] State store initialised (delta link table / subscription store).
- [ ] Notification endpoint accessible from Graph (HTTPS, valid cert, ≤ 10 s response).
- [ ] Smoke test: run `GET /me` (delegated) or `GET /users?$top=1` (app) and confirm 200.

---

## Health checks

| Check | Endpoint / command | Expected | Frequency |
|---|---|---|---|
| Auth token acquisition | [POST /token] | HTTP 200 + `access_token` | Every 5 min |
| Graph connectivity | GET /v1.0/me or /users?$top=1 | HTTP 200 | Every 5 min |
| Subscription active | GET /subscriptions/{id} | `expirationDateTime` > now + 1 h | Every 30 min |
| Delta link valid | Run incremental sync | No `410 Gone` response | Every sync run |
| Throttle rate | 429 count in last 1 h | 0 (alert if > 5) | Continuous |

---

## Common incidents and remediation

### 401 Unauthorized

**Causes:**
1. Token expired (handled automatically by MSAL token cache — check if cache is working).
2. Client secret or certificate expired.
3. App registration deleted or disabled in Entra.

**Steps:**
1. Check token expiry: decode the JWT at jwt.ms; confirm `exp` claim.
2. Check Key Vault: is the credential present and not expired?
3. Check Entra portal: confirm the app registration is enabled and has the correct permissions.
4. Rotate credential if expired (see Credential Rotation section below).

---

### 403 Forbidden

**Causes:**
1. Permission not granted or admin consent not given.
2. Using delegated permission in a daemon (client-credentials) context.
3. `scp` or `roles` claim missing from the token.

**Steps:**
1. Decode the access token; check `scp` (delegated) or `roles` (application) claim.
2. Compare to required permissions in `graph-app-registration.md`.
3. If missing: request admin consent in Entra portal → Enterprise Applications → your app → Permissions → Grant admin consent.

---

### 429 Too Many Requests

**Causes:**
1. Burst of calls exceeding the per-resource throttle budget.
2. Missing Retry-After handling — immediate retries making it worse.

**Steps:**
1. Check logs: what resource and operation is throttled? (Mail? Users? Files?)
2. Verify Retry-After is being honoured (look for sleep/wait in retry logs).
3. If throttle is persistent: implement `$batch` to reduce call count, or shift bulk operations to off-peak hours.
4. If acute: pause the integration for `Retry-After` seconds, then resume.

---

### 410 Gone (stale delta link)

**Cause:** The stored `@odata.deltaLink` expired (typically > 30 days of inactivity).

**Steps:**
1. Delete the stored delta link.
2. Run a full initial sync to rebuild the state.
3. Store the new delta link returned at the end of the full sync.

---

### Subscription silently expired

**Symptom:** Events stop arriving; no errors in logs.

**Steps:**
1. `GET /subscriptions/{id}` — if 404, the subscription is gone.
2. Check `last_renewed_at` in state store — was the renewal job running?
3. Re-create the subscription.
4. Run a delta-query catch-up to recover missed events since `last_renewed_at`.

---

## Credential rotation procedure

### Certificate rotation (recommended)

1. Generate a new certificate (Key Vault auto-rotation or manual).
2. Upload the new public key to Entra: App registration → Certificates & secrets → Upload.
3. Update the Key Vault secret or app setting to reference the new certificate.
4. Verify the app acquires tokens with the new cert: check `sub` in the token matches the app.
5. Remove the old certificate from Entra after [30 days] (overlap window for in-flight deployments).

### Client secret rotation

1. In Entra: App registration → Certificates & secrets → New client secret.
2. Copy the new secret value immediately (shown only once).
3. Store in Key Vault; update the app configuration to reference the new secret version.
4. Verify token acquisition.
5. Delete the old secret in Entra after confirming the new one works.

---

## Change log

| Date | Change | Author |
|---|---|---|
| [YYYY-MM-DD] | [Initial runbook] | [Name] |
| | | |

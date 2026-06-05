# Use Entra External ID for new CIAM — not Azure AD B2C

**Status:** Absolute rule
**Domain:** Azure identity / CIAM
**Applies to:** `azure-cloud`

---

## Why this exists

Azure AD B2C is on a maintenance-only path; Microsoft announced the successor — Entra External ID — as the strategic CIAM platform. New customer-facing applications built on B2C will face a migration before B2C reaches its end-of-life timeline. Entra External ID provides the same self-service sign-up/sign-in, social identity providers, and custom branding — built on the modern Entra platform with Conditional Access and a unified admin experience. The house opinion (#16: "Don't start new CIAM on B2C") is a concrete consequence of the dated capability map.

## How to apply

Create an Entra External ID tenant for CIAM use cases (separate from the corporate/internal Entra tenant):

```bash
# Create an External ID tenant (CIAM type) via az CLI
az rest --method POST \
  --url "https://management.azure.com/tenants?api-version=2020-01-01" \
  --body '{
    "tenantType": "CIAM",
    "displayName": "MyApp Customers",
    "countryCode": "US",
    "dataResidencyLocation": "United States"
  }'
```

Configure user flows (sign-up/sign-in) in the new tenant:
```json
{
  "displayName": "SignUpSignIn",
  "userFlowType": "signUpOrSignIn",
  "identityProviders": [
    { "id": "EmailPassword" },
    { "id": "Google-OAUTH" },
    { "id": "MicrosoftAccount" }
  ]
}
```

Connect your app registration:
- Register the app in the External ID tenant (not the corporate tenant).
- Use MSAL with the `https://<tenant>.ciamlogin.com/<tenant>.onmicrosoft.com/v2.0` authority.
- Conditional Access policies apply natively — no Custom Policies (XML) needed for most scenarios.

**Do:**
- Create a dedicated Entra External ID tenant — keep customer identities separate from employee identities.
- Use user flows for standard sign-up/sign-in/password-reset; custom authentication extensions for advanced flows.
- Register the app in the CIAM tenant and configure CORS + redirect URIs there.
- Verify the Entra External ID tenant region matches your data residency requirements.

**Don't:**
- Create a new Azure AD B2C tenant for any new CIAM project.
- Mix customer identities and employee identities in the same tenant.
- Use B2C Custom Policies (XML) for Entra External ID — the model is different.
- Assume B2C and External ID are API-compatible — migration requires app registration changes.

## Edge cases / when the rule does NOT apply

- **Existing B2C tenants**: don't migrate existing B2C tenants proactively unless the B2C EOL date is imminent or you have a feature gap. Plan the migration; don't rush it.
- **Employee/partner B2B scenarios**: Entra External ID (B2B) in the corporate tenant handles partner access; CIAM External ID is for consumer/customer identities.

## See also

- [`../agents/entra-identity-engineer.md`](../agents/entra-identity-engineer.md) — owns CIAM platform selection and Entra External ID configuration.
- [`./passwordless-by-default.md`](./passwordless-by-default.md) — customer identity flows should also avoid storing passwords in the app; delegate to the CIAM platform.

## Provenance

Codifies house opinion #16 and the anti-pattern from `CLAUDE.md` §4: "New CIAM on Azure AD B2C instead of Entra External ID." Grounded in the dated capability map in `knowledge/azure-2026-capability-map.md` (B2C → External ID transition) and Microsoft's official announcement of the B2C successor path.

---

_Last reviewed: 2026-06-05 by `claude`_

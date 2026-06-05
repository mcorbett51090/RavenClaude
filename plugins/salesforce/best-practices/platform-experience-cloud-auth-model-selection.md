# Choose the correct Experience Cloud authentication model before building — guest, self-reg, and SSO have different data-exposure footprints

**Status:** Primary diagnostic
**Domain:** Platform / Experience Cloud
**Applies to:** `salesforce`

---

## Why this exists

Experience Cloud sites support three authentication models — **guest user (unauthenticated)**, **self-registration**, and **SSO/SAML/OIDC** — and each has a fundamentally different record-visibility footprint. Teams that choose the wrong model at the start must rearchitect sharing, profiles, and OWD after data is already in the org, which is expensive and risky. The guest-user model has the tightest constraints and the largest blast radius if misconfigured (any `Public Read` OWD change or a missing `without sharing` annotation on a guest-accessible controller can expose every record of that type to the unauthenticated internet). Self-registration creates real Salesforce users at runtime, consuming Salesforce licenses or Experience Cloud member licenses, which affects cost models. SSO delegates identity to an external IdP, but the Salesforce-side profile/permission-set must be mapped explicitly — it is not automatic.

## How to apply

Decision by requirement:

| Requirement | Correct model |
|---|---|
| Fully public, no user identity, read-heavy (product catalog, knowledge) | Guest user — carefully scoped OWD and controller sharing |
| Users register themselves with minimal friction (B2C portal) | Self-registration with a registration handler Apex class |
| Employees or partners already in an external IdP (Azure AD, Okta, etc.) | SSO / OIDC / SAML — map to a Salesforce profile or permission set |
| Mix: anonymous browsing + authenticated checkout | Guest user for public pages + redirect to login for authenticated sections |

```apex
// Guest-accessible Apex controller MUST be without sharing AND must
// select only the minimal fields/records the public needs.
// NEVER expose internal fields; ALWAYS filter by site-scoped criteria.
global without sharing class PublicCatalogController {
    @AuraEnabled(cacheable=true)
    public static List<Product2> getPublicProducts() {
        // CRUD/FLS irrelevant for guest context — but data scope is critical.
        // Only return records marked for public display.
        return [
            SELECT Id, Name, Description, DisplayUrl
            FROM Product2
            WHERE IsActive = true AND ShowOnPortal__c = true
            LIMIT 200
        ];
    }
}
```

**Do:**
- Decide the auth model in the design phase, before OWD and sharing rules are set — the model drives the data-exposure design.
- For self-registration, write a `Site.ExternalUserCreateResult` registration handler that validates the email domain and assigns the correct profile — never accept the default "no handler" option, which creates overly permissive users.
- For SSO, map the IdP claim to a Salesforce profile via a `RegistrationHandler` or SAML attribute mapping that assigns the *minimum* required profile, not System Administrator.
- Scope guest-accessible controllers to `without sharing` with the narrowest possible `WHERE` clause — the guest profile owns no records and cannot own sharing grants.

**Don't:**
- Change the OWD for an object to `Public Read` or `Public Read/Write` globally just to make guest access work — widen only the objects the guest genuinely needs to read.
- Let the Experience Cloud site use the default Guest User profile without auditing every object's `Guest Access` checkbox and removing unneeded ones.
- Conflate self-registration (a new Salesforce user is created) with SSO (an existing external identity is mapped) — combining both without careful profile separation creates duplicate users with conflicting access.
- Grant `Modify All Data` or `View All Data` to any Experience Cloud profile — this bypasses OWD and sharing entirely.

## Edge cases / when the rule does NOT apply

For an internal-employee portal where all users are already in Salesforce as internal users, no Experience Cloud auth model selection is needed — standard Salesforce login with permission sets applies. Experience Cloud auth decisions apply only to external-user or guest-user access scenarios.

## See also

- [`../agents/salesforce-platform-architect.md`](../agents/salesforce-platform-architect.md) — owns Experience Cloud architecture and sharing model
- [`./security-guest-user-and-experience-cloud-sharing.md`](./security-guest-user-and-experience-cloud-sharing.md) — the complementary rule on guest-user sharing rule configuration
- [`./data-owd-most-restrictive-then-open-deliberately.md`](./data-owd-most-restrictive-then-open-deliberately.md) — the OWD design discipline that underpins this rule

## Provenance

Codifies standard Salesforce Experience Cloud authentication model selection discipline; Salesforce Experience Cloud developer documentation and guest user security hardening guide.

---

_Last reviewed: 2026-06-05 by `claude`_

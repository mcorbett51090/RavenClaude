---
name: power-pages-permissions
description: Design table permissions, web roles, and authentication for Power Pages — anonymous vs authenticated patterns, B2C / Entra-External-ID auth, table-permission scoping (global / contact / account / parental / self), record ownership, and the "row I can see in MDA but not in Pages" debugging playbook. Used by `power-pages-engineer` (primary).
---

# Power Pages Permissions Skill

**Purpose:** Senior-maker playbook for `power-pages-engineer` covering the Power Pages security model end-to-end — authentication, web roles, table permissions, record ownership — and the diagnostic flow for the most common production headache: "this row is visible in the model-driven app but not in Pages."

Power Pages security is multi-layered, and each layer can independently block a row. Junior makers troubleshoot Pages permissions by clicking around; veterans walk the layers in order.

## When to Use

- **Standing up a new portal** — design auth + web roles + table permissions before building any pages or forms.
- **Adding a new table to an existing portal** — wire up table permissions before users can see the data.
- **Permission-denied incident** — user reports they can't see/edit a row in Pages that they can see in MDA, or the portal shows blanks for known-good data.
- **External-user auth provider migration** — moving from ADB2C to Entra External ID, or adding social login.

## Core Principles

1. **Security is layered: Auth → Web Role → Table Permission → Record Ownership → View/Form filter.** Each layer is gate-able. A row is visible to a portal user only if it passes *every* layer.
2. **Anonymous and authenticated are different identities, not states of the same identity.** Each gets its own web role(s) and table permissions. An anonymous user is `Visitor` (or your custom anonymous role) — not "just a contact who hasn't signed in yet."
3. **Hiding ≠ securing.** A field hidden via CSS or Liquid `if` is still in the page source. The browser saw it. If the data is sensitive, it must be blocked at the table-permission layer, not the rendering layer.
4. **Record ownership drives most of the table-permission scopes.** Pick the ownership column carefully — it determines which scopes are even available to you.
5. **Test as a portal user, not as a portal admin.** The admin can see everything; the test user reveals what the actual user experiences.

## Playbook

### 1. The Power Pages security model — top to bottom

```
[Authenticated user or Anonymous visitor]
       ↓
[Authentication provider validated their identity]    ← B2C / Entra External ID / etc.
       ↓
[Contact record linked]                                ← bound by authentication, used for scoping
       ↓
[Web Role(s) assigned to that contact]                 ← Anonymous Users / Authenticated Users / custom roles
       ↓
[Table Permissions associated with the Web Role(s)]    ← scope determines which rows
       ↓
[Record Ownership matches the scope's expectation]     ← contact / account / parental / self
       ↓
[View / Form / List filter further restricts]          ← optional final narrowing
       ↓
[Row appears in Pages]
```

Walk this top-to-bottom when designing; walk it top-to-bottom when debugging.

### 2. Authentication — B2C vs Entra External ID

| Capability | **Azure AD B2C** | **Entra External ID** |
|---|---|---|
| Status | Legacy / GA | Microsoft's stated future direction (2026) |
| Custom branding | Custom policies (XML, painful) | Built-in user-flow designer, friendlier |
| Identity provider federation | Many providers, mature | Most providers, growing |
| User attributes | Custom attributes in the directory | Custom attributes, with cleaner schema |
| Cost | Per MAU after free tier | Per MAU, simpler pricing |
| Migration | — | New deployments should start here unless org has an existing B2C investment |

**Default**: new portals use Entra External ID unless a specific reason ties you to B2C. Existing B2C deployments don't migrate without a plan — sign-in flows, federated IdPs, and user records all need attention. Don't migrate casually.

Whichever provider you pick, the Pages-side bind is the **Contact** record. Authentication produces or matches a Contact in the linked Dataverse environment. Everything from web roles onward is anchored to that Contact.

### 3. Web roles — design

Out of the box you get **Anonymous Users** and **Authenticated Users**. That's the floor, not the ceiling.

Real designs have custom roles for each audience class:
- `Anonymous Users` — what unauthenticated visitors can do (usually: read public pages, submit a contact form).
- `Authenticated Users` — the default for any signed-in contact.
- `Customer - Standard` — paying customer at the standard tier.
- `Customer - Premium` — paying customer with elevated access.
- `Partner Contact` — external partner with access to their account's data.
- `Internal Reviewer` — internal user with read-everything access for support.

A contact can have multiple web roles; permissions accumulate (union of grants). Plan deliberately — overlapping web roles with conflicting scopes are a common source of "why can this person see that?" surprises.

### 4. Table-permission scopes (the core mechanic)

| Scope | Visible rows | Use when |
|---|---|---|
| **Global** | All rows in the table | Truly public reference data (countries, product catalog) or admin-tier roles |
| **Contact** | Rows where the contact-lookup column = the signed-in contact | "Show me my support cases", "show me my orders" |
| **Account** | Rows where the account-lookup column = the signed-in contact's parent account | "Show me my company's invoices", "show me everyone on my account" |
| **Parental** | Rows whose parent record's permission allows it (cascades down a relationship) | Child tables that inherit access from their parent (case ↔ case notes) |
| **Self** | Just the signed-in contact's own contact record | "Edit your profile" pages |

The scope is on the **Table Permission** record, not the table itself. A single table can have multiple permissions with different scopes attached to different web roles.

**Privileges** orthogonal to scope: Read, Create, Write, Delete, Append, AppendTo. Same vocabulary as model-driven security roles.

### 5. Record ownership — the column that drives the scope

The scope only works if the row points at the right contact / account.

- **Contact scope** needs a contact-lookup column on the row, populated with the right contact. Often `mc_owningcontact` or use the OOTB `customerid` polymorphic. If the column is empty or wrong, the row is invisible to that contact even with the right permission.
- **Account scope** needs an account-lookup column populated.
- **Parental scope** needs the parent record to itself be visible (recursion — debug from the top of the chain).
- **Self scope** is just the contact's own row.

**Common bug**: rows created via a model-driven app default-own to the maker's User, not to a contact. They are then invisible in Pages even with permissions set up correctly. Either (a) a plug-in fills in the contact-lookup on Create, (b) the Pages form populates it explicitly when the portal user creates the row, or (c) you accept that MDA-created rows are admin-only and document the boundary.

### 6. The "I can see this row in MDA but not in Pages" debug playbook

Run these checks in this order. The bug is almost always at the first failing layer.

1. **Auth identity** — is the test user actually signed in to Pages? Check the portal session shows a Contact. If not, you're testing as Anonymous and the rest of the analysis is wrong.
2. **Web role** — is the right Web Role assigned to the test contact? Check Contact record → Web Roles related entity. (Default Authenticated Users is *not* automatic in all configs.)
3. **Table permission exists** — is there a Table Permission record for that table, linked to the test user's Web Role?
4. **Scope is right** — Global / Contact / Account / Parental / Self. Does it match the kind of relationship the row has to the contact?
5. **Record ownership matches the scope** — if Contact scope, is the contact-lookup column on the row populated to the test contact? If Account scope, is the account-lookup populated and does the contact have that account as parent?
6. **Privilege is granted** — Read at minimum. (You'd be surprised how often a permission grants Create but not Read.)
7. **View filter on the list / form** — most lists in Pages are backed by a Dataverse View. If the View has filters (`Status = Active`), inactive rows won't show even with full permissions.
8. **Form metadata** — for forms, check that the form is published and that the field-level security on the fields is not blocking.
9. **Cache** — Pages caches aggressively. After a permissions change, restart the portal app or wait the cache TTL. Don't chase a fix you already shipped.

A 9-step checklist sounds heavy. It runs in 5 minutes if you go in order and stops at the actual breakage every time.

### 7. Anonymous-form patterns (submit-without-auth)

Common case: "Contact Us" form, "Request a quote," "Report an issue." The user is anonymous and you want them to submit a row.

- Grant the **Anonymous Users** web role a Table Permission with **Create** privilege only (no Read), Global scope (necessary because there's no contact to own the row yet).
- The form populates the contact lookup either from the form fields (name + email) — usually creating or matching an existing Contact via a plug-in — or leaves it null for the back-office to triage.
- Verify Anonymous role **cannot** Read the table. Otherwise, an anonymous visitor can list other submissions.
- Add reCAPTCHA. Anonymous Create endpoints attract spam within hours of going live.

### 8. Authenticated portal patterns

Self-service ticketing, account self-service, statement-of-account, document libraries. The standard shape:

- Authenticated Users web role + a customer-tier web role.
- Table Permissions with Contact or Account scope for the tables the portal user can touch.
- Parental scope on child tables (e.g., case notes inherit from cases).
- Self scope on the Contact table for "edit my profile."
- View filters narrow further when needed ("only show open cases by default").

### 9. Liquid permission-aware rendering

Liquid can check the current user's web roles to render conditionally:

```liquid
{% if user and user.roles contains "Customer - Premium" %}
  <!-- premium feature here -->
{% endif %}
```

This is for **UX**, not security. The "premium feature" inside the `{% if %}` is still rendered to source for users who pass the check; if it includes sensitive data the data must be table-permission-protected. Liquid hides UI; it does not secure data.

## Anti-Patterns to Flag

- Using `display: none` or Liquid `if` to "secure" a field with sensitive data (it's still in the source)
- Granting Global scope where Contact or Account would do
- Anonymous Users role with Read access to tables it shouldn't see (data leak)
- Table permission Create without Read — users can submit but can't see their own submission, frustrating UX
- Web roles overlapping with conflicting scopes — debug nightmare
- Hard-coded contact/account GUIDs in Liquid templates (§3 #11 — and §3 #2 for env vars)
- Skipping the test-as-end-user step
- No rate limiting / captcha on anonymous Create endpoints
- Migration B2C → Entra External ID without an existing-user re-bind plan

## Escalation

- **Anything touching PII, regulated data, or external auth provider integration** → `ravenclaude-core` `security-reviewer` before deployment.
- **B2C ↔ Entra External ID migration** → multi-week project. Bring `architect` and `security-reviewer` in. This is not an ad-hoc skill task.
- **Performance issues on Pages (slow lists, slow forms)** → may overlap with the same delegation / RAG-of-rows issues as canvas; the Pages runtime is different but the root causes can rhyme.
- **Permissions need to coordinate with model-driven security roles** → `model-driven-engineer` + `dataverse-architect`.
- **Need to ship via solution ALM** → `solution-alm-engineer` + `alm-pipeline-design` skill — table permissions are solution-aware components and must travel with the solution.

When in doubt, lock it down and grant explicitly. Power Pages is internet-facing — every accidental Read on the Anonymous role is a potential data-leak headline. Default-deny, explicit-grant.

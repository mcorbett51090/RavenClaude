# SIS / SSO / rostering integration patterns

> **Last reviewed:** 2026-05-21. Status: pre-engagement-draft (extends the existing [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md) production-lesson file with SSO + integration-pattern depth; refresh on first real engagement signal). Sources: OneRoster 1.2 spec (IMS Global / 1EdTech, 2024), Clever and ClassLink developer documentation, SAML 2.0 / OIDC standards, PowerSchool / Infinite Campus / Skyward / Synergy SIS documentation (vendor-public), district SSO patterns (Google Workspace for Education, Azure AD, district Active Directory). Refresh when: (a) OneRoster spec ships a new version (1.3 anticipated), (b) Clever or ClassLink change their integration model, (c) a major SIS vendor changes their export / API, (d) live engagement scenarios via `/wrap` surface integration patterns this file doesn't cover.

This file is the **technical-integration reference** for the implementation 90-day arc. The [`../skills/implementation-90-day-arc.md`](../skills/implementation-90-day-arc.md) skill consults this file during weeks 1-2 (discovery) and weeks 3-4 (configuration). The [`../templates/implementation-90-day-plan.md`](../templates/implementation-90-day-plan.md) week-by-week checklist references this file.

This file is the **technical-config sibling** of [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md) — that file covers data-quality diagnostics ongoing; this file covers integration-pattern setup at implementation time.

## 1. The K-12 SIS landscape (top 5 by district share)

| SIS | District market position | Rostering integration patterns | Common gotchas at setup |
|---|---|---|---|
| **PowerSchool** | Largest US K-12 SIS by district share | OneRoster export (file-based or API); Clever / ClassLink integration; direct OAuth in newer deployments | Multi-year-old districts may have legacy export configs that need refresh; permissions inheritance through school/district hierarchy can be confusing |
| **Infinite Campus** | Major in midwest + west | OneRoster API + Clever / ClassLink; direct integrations supported | Calendar synchronization differs by district config; user-type mappings (staff vs teacher vs admin) require careful schema review |
| **Skyward** | Strong in midwest | OneRoster + Clever / ClassLink | Family-rostering surface (which child / parent / household) is more configurable than other SIS — confirm the partner's specific config |
| **Synergy (Edupoint)** | West coast + texas presence | OneRoster + Clever / ClassLink | Class-section ID mapping can drift between SIS and integration broker; spot-check section codes |
| **Aeries** | California-heavy | OneRoster + ClassLink + Clever | California-specific (SOPIPA-aware contracts; data flow constraints differ from other states) |

## 2. The rostering broker layer (Clever, ClassLink, direct)

Most K-12 EdTech vendors don't integrate directly with the SIS — they integrate via a broker that abstracts the SIS-specific differences.

### Clever
- Largest US K-12 rostering broker
- Daily sync typical (some configs are real-time)
- District admin controls sharing scope per-application (which schools / users get shared to which vendor)
- Vendor pulls from Clever API
- **Gotcha:** Clever's "sharing scope" can be set to only-some-schools-per-vendor; if the district shared just 1 of 12 schools to your app, sync looks "complete" but the dataset is wrong

### ClassLink
- Second-largest US K-12 rostering broker
- Real-time or scheduled sync depending on config
- Strong SSO integration (often deployed where the district also uses ClassLink LaunchPad SSO)
- Vendor pulls from ClassLink API
- **Gotcha:** ClassLink has a separate rostering surface vs SSO surface; confirm BOTH are configured if you need both data and login

### OneRoster (direct, no broker)
- IMS Global / 1EdTech standard
- 1.0 → 1.1 → 1.2 (current); 1.3 anticipated
- File-based (CSV) or REST API
- Some districts run direct OneRoster integrations to avoid broker dependencies
- **Gotcha:** version skew between the SIS export and the vendor's expected import — confirm both endpoints support the same OneRoster version

### Direct SIS API
- Rare for K-12 vendors (most use a broker)
- Each SIS has its own API surface + auth model
- Useful when broker doesn't support the vendor's specific data needs (e.g., gradebook integration, attendance, specialized data points)
- **Gotcha:** versioning, maintenance burden; the vendor effectively owns the integration's reliability

## 3. SSO patterns (the auth surface)

Distinct from rostering — SSO is the login surface. A user provisioned via rostering must also be able to AUTHENTICATE.

### District-IdP patterns (in order of frequency)

1. **Google Workspace for Education** — dominant in K-12; SAML 2.0 or OIDC; district controls which apps users can access
2. **Microsoft Azure AD** / Entra ID — growing in K-12; SAML 2.0 / OIDC / OAuth 2.0; common in districts with Microsoft 365 Education
3. **District-managed Active Directory** — older deployments; on-prem; SAML federation to cloud apps
4. **ClassLink LaunchPad** — district-portal-first; SSO + app launchpad combined
5. **Clever Instant Login** — Clever's SSO surface; integrated with their rostering broker
6. **Other / niche** — district-specific IdPs, ID.me-style state portals, specific-vendor SSO

### Per-role IdP routing (the most common SSO mistake)

Districts often route DIFFERENT roles through DIFFERENT IdPs:

- **Admins** authenticate via district AD / Azure AD
- **Teachers** authenticate via Google Workspace
- **Students** authenticate via Clever Instant Login or ClassLink
- **Parents** authenticate via the vendor's own auth (no district IdP for parents in most cases)

**Implication:** "SSO works" needs to be tested per role, not just "the admin logged in." Per the implementation 90-day plan failure-mode check.

### SAML 2.0 vs OIDC vs OAuth 2.0 (compact)

- **SAML 2.0** — XML-based, older, dominant in district AD / Azure AD deployments; certificate-based trust
- **OIDC** (OpenID Connect on OAuth 2.0) — JSON-based, modern; growing in K-12 cloud deployments
- **OAuth 2.0** — authorization, not authentication; sometimes used in API-access patterns (vendor pulls user data on behalf of district)

For K-12, the vendor should support all three; the district picks based on their IdP.

## 4. The implementation discovery checklist (weeks 1-2 of the 90-day arc)

When the partner-side technical lead joins kickoff, surface these questions:

### SIS
- [ ] Which SIS? (PowerSchool / Infinite Campus / Skyward / Synergy / Aeries / other)
- [ ] Version / hosting? (Self-hosted / vendor-cloud)
- [ ] Rostering broker? (Clever / ClassLink / direct OneRoster / none)
- [ ] If broker, is the broker contract owned by district or by a specific app vendor? (matters for sharing-scope control)
- [ ] OneRoster version supported by SIS? (1.0 / 1.1 / 1.2 / 1.3)

### Rostering scope
- [ ] All schools or some? (Confirm the sharing scope per [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md))
- [ ] All roles or some? (student / teacher / staff / admin / parent — confirm which the vendor product needs)
- [ ] All grades or some? (some products only support 6-12 or only K-5)
- [ ] Sync frequency? (Daily standard, some real-time)
- [ ] Family-rostering surface needed? (parent/guardian links to student; varies by SIS config)

### SSO
- [ ] Which IdP for each role? (Admins / teachers / students / parents)
- [ ] SAML 2.0 / OIDC / OAuth 2.0 support?
- [ ] District AD / Azure AD / Google Workspace / ClassLink LaunchPad / Clever Instant Login / other?
- [ ] Pre-existing SAML metadata or new exchange required?
- [ ] JIT (just-in-time) provisioning OR pre-provisioned users?

### Data-protection
- [ ] State student-privacy framework requirements? (per [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md))
- [ ] State-specific data-protection rider needed? (NY Ed Law §2-d, IL SOPPA, CA SOPIPA)
- [ ] AI-feature COPPA-amended disclosure required? (post April 22, 2026 — per [`ai-in-edtech-2026.md`](ai-in-edtech-2026.md))
- [ ] Sub-processor disclosure list shared with partner?

## 5. Validation patterns (weeks 3-4 of the 90-day arc)

After the configuration is in place but BEFORE go-live:

### Rostering validation
- **Spot-check 10 users** across roles + schools (not just "the sync ran successfully")
- **Compare counts** to partner's own data: total students / teachers / admins per school should match
- **Test class-section mapping** if product needs class context (some sync misses class assignments)
- **Test enrollment changes** propagate (add a test student, confirm appears in vendor system within sync window)

### SSO validation
- **Test per role** (admin, teacher, student, parent — each)
- **Test per IdP** (if multi-IdP routing per role)
- **Test logout** (some SSO patterns don't properly clear session)
- **Test error paths** (what happens when SSO fails — clear error, not blank screen)

### Data-flow validation
- **Personal data the product reads** matches the contract DPA
- **Personal data the product writes** matches what the partner consented to
- **Sub-processor list** as in production matches the contract

## 6. Common integration failure modes

These are the failure patterns that show up in real implementations:

| Failure | Symptom | Root cause | Fix pattern |
|---|---|---|---|
| **Roster looks complete, missing entire school** | Sync "succeeds" but School-X has no users | Clever / ClassLink sharing scope set to only-some-schools | Update sharing scope at the broker; re-sync |
| **SSO works for admins, broken for students** | Test admin login OK; student gets blank screen | Different IdP route per role; student IdP not configured | Configure student IdP (likely Clever Instant Login or ClassLink) |
| **Class-section IDs drift between SIS and product** | Users present but class assignments wrong | OneRoster section codes interpreted differently by SIS export vs broker | Spot-check section codes; usually a config alignment, not a code change |
| **Family / parent rostering missing** | Parents can't access; product looks empty for them | Family-surface not enabled in broker; or parent role not in the data scope | Confirm with partner's SIS config that parents are exported; enable in broker |
| **OneRoster version skew** | Some fields present, some missing | SIS exports 1.1, vendor expects 1.2 (or vice versa) | Negotiate which version to target; some partners can upgrade their export |
| **Provisioning lag** | New student doesn't appear for 24+ hours | Daily sync (not real-time); expected | Communicate to partner; some products can do just-in-time provisioning at first login |
| **JIT provisioning permissions wrong** | New student logs in but has wrong role | JIT default role doesn't match SIS data | Configure JIT to read role from SSO claim, not hardcoded default |
| **Sub-processor mismatch** | Partner contract specifies X sub-processors, current list has Y | Sub-processor list drifted post-contract | Update contract or update vendor sub-processor list; either way notify partner per state-law requirements |

## 7. Anti-patterns this file flags

- **"Sync ran successfully" as validation.** Sync completing successfully and sync containing the right data are different things. Spot-check the data.
- **Single-role SSO testing.** Admin can log in ≠ students can log in. Test per role.
- **Skipping family-surface check.** Parent comms / family-engagement products fail in production because parent provisioning wasn't validated at implementation.
- **OneRoster version assumption.** Newer doesn't mean better; the SIS may not export the version the vendor expects. Confirm at discovery.
- **Direct SIS integration "to avoid broker dependency."** This shifts maintenance burden to the vendor. Almost always a mistake unless the broker genuinely can't support the data needs.
- **Treating sub-processor disclosure as a one-time event.** State student-privacy laws (especially IL SOPPA) require re-disclosure on changes. Track the list and re-disclose at material changes.

## 8. Refresh triggers

- OneRoster spec ships a new version
- Clever or ClassLink materially change their integration model
- A major SIS (PowerSchool, Infinite Campus, Skyward, Synergy) changes their export / API
- A district SSO pattern not in this file surfaces in a real engagement (`/wrap` signal)
- COPPA-amended consent posture interacts with rostering data flow in a new way

## 9. References

- [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md) — ongoing diagnostic complement (this file is implementation-time)
- [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md) — state student-privacy frameworks
- [`ai-in-edtech-2026.md`](ai-in-edtech-2026.md) — COPPA-amended consent overlay for AI features
- [`district-implementation-failure-modes.md`](district-implementation-failure-modes.md) — sibling file: implementation-arc failure modes broader than integration
- [`../skills/implementation-90-day-arc.md`](../skills/implementation-90-day-arc.md) — the playbook this file serves
- [`../templates/implementation-90-day-plan.md`](../templates/implementation-90-day-plan.md) — the per-week checklist artifact

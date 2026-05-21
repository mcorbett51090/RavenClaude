# Rostering data quality — a typology of failure modes

> **Last reviewed:** 2026-05-21. Source: research-distilled reference from vendor docs (Clever, ClassLink, OneRoster, Canvas, Workday Student, SCIM) plus PSM field patterns. Refresh when: (a) OneRoster ships a v1.3 with breaking changes, (b) Clever / ClassLink change their identity-broker terms materially, or (c) a state mandates a rostering-vendor change (CA, NY, IL most likely).

When a partner says **"the data isn't right,"** it is almost never the analytics product and almost always a rostering / SIS / LMS / IDP sync issue. The PSM's job is to *recognize* this within the first 24 hours, *coordinate* the fix without owning it, and *not* let the partner blame the wrong system. This document is the diagnostic typology.

---

## The diagnostic instinct

Before declaring a partner red on engagement, the learning-analytics-analyst checks rostering first. The order is:

1. **Is the data flowing at all?** Last successful sync timestamp, row count, error log.
2. **Is the data flowing *correctly*?** Sample 5 students; do their org, grade, class memberships match what the partner expects?
3. **Is the data flowing *currently*?** Did a mid-year change (transfer, drop, schedule change) propagate?

If any of those three is "no," the partner isn't red — the rostering pipeline is. **Engagement metrics computed against stale rosters are noise.**

---

## The K-12 stack: Clever, ClassLink, OneRoster

Most US K-12 districts (as of 2026) route through one of three patterns:

### Pattern A — Clever (most common)

- **Shape:** District uploads from SIS (PowerSchool, Infinite Campus, Skyward, Synergy, etc.) → Clever aggregates → vendor pulls from Clever API or receives provisioned roster.
- **Sync cadence:** Nightly is default. Some districts run twice daily.
- **Authoritative source:** Always the SIS. Clever is a broker; it does not edit data.
- **Common drift modes:**
  - **Section roster ≠ class roster.** A teacher's "class" in the SIS may be split across multiple sections (period 1 vs period 5); the vendor only sees what Clever exposes. If the partner is reporting on a "class," confirm which SIS object that maps to.
  - **Course code reuse across schools.** Two schools in the same district can use the same course code for different content. Vendor sees one course; partner thinks they're seeing two.
  - **Mid-year transfers lag.** A student transfers between schools mid-year; the SIS updates, Clever syncs that night, vendor pulls the next morning. ~24-48h lag.
  - **District-side sharing controls.** District admin can scope which schools/grades the vendor sees. If the vendor sees "fewer kids than expected," the first check is Clever district admin's app-sharing scope — not the vendor's code.
  - **Demographic data scope.** By default, Clever shares minimal demographics. If the partner expects IEP / 504 / FRL flags, those require explicit district opt-in (and FERPA-justified).
- **PSM tell:** Partner says "we added a new school but the kids aren't showing up." Check sharing scope first.

### Pattern B — ClassLink

- **Shape:** Same broker pattern as Clever, plus an SSO LaunchPad layer.
- **Authoritative source:** Same — district's SIS.
- **The LaunchPad complication:** ClassLink's LaunchPad is an SSO + app portal. When parents/teachers say "the link doesn't work," it's often a LaunchPad bookmark issue, not a vendor issue. Differentiate before escalating to product.
- **OneRoster underneath:** ClassLink's roster API is OneRoster-flavored. Knowing OneRoster helps debug.
- **Common drift modes:** Same as Clever, plus:
  - **App icon → wrong URL.** A LaunchPad admin can mis-configure the icon target; users click and land on a wrong tenant or staging env.
  - **SSO assertion missing claims.** Vendor expects a `role` or `grade` claim; LaunchPad admin didn't include it; partner doesn't know to look.

### Pattern C — Direct OneRoster (no broker)

- **Shape:** District drops OneRoster v1.1 or v1.2 CSV files to an SFTP, or exposes a OneRoster REST endpoint, and the vendor consumes directly.
- **Common drift modes:**
  - **Stale CSV.** District has a cron job; it failed three days ago; the partner's data is three days old. *No automated alerting on the partner side unless the vendor built it.*
  - **CSV encoding.** UTF-8 with BOM, UTF-16, Windows-1252 — district-side automation differs. A single misencoded character on a student name breaks the row, drops the student. Vendor's parser may or may not log this loudly.
  - **Missing required columns.** OneRoster v1.1 requires specific columns (`sourcedId`, `status`, `dateLastModified`); v1.2 differs slightly. A district that "upgraded" the CSV without coordinating breaks the parse.
  - **Org IDs change without notice.** A district renames a school; the `org.sourcedId` shifts; the vendor doesn't recognize the school as the same one. Look like a "school disappeared."
  - **Demographic columns inconsistent.** Some districts include grade as a number, some as a string ("9" vs "Grade 9"). The vendor's parser may default-bucket the unparseable ones.
- **PSM tell:** Partner is technical enough to run their own SFTP drop and is the most likely to have a *silent* data-quality failure.

### OneRoster version gotchas

- **v1.1** is the wide install base; **v1.2** adds gradebook scope.
- IMS Global rebranded to **1EdTech** in 2022; URLs and doc paths shifted.
- A district claiming "we're OneRoster compliant" without specifying version is a yellow flag — ask which.

---

## The higher-ed stack: Banner, Workday Student, PeopleSoft, Slate

Higher-ed rostering is rarely OneRoster — the SIS is the integration point, and each SIS has its own contract.

### Banner (Ellucian)

- **Shape:** Banner term tables → Banner ETHOS API or direct DB extract → vendor.
- **Common drift modes:**
  - **Mid-term add/drop window.** Most institutions have a 1-2 week add/drop window; rosters churn 5-20%. If the vendor pulled at start-of-term and didn't re-sync, dashboards are wrong by week 3.
  - **Cross-listed sections.** Course X is co-listed as 300-level and 400-level (same room, same instructor); Banner has two CRNs; vendor may double-count students.
  - **Auditors and non-degree students.** May be present in the section enrollment but excluded from program-level reporting. Vendor's "active students" metric depends on which list it pulled.
  - **Hold codes and registration status.** A student with an active hold may appear enrolled but not actually attending. Engagement-zero != churn.

### Workday Student

- **Shape:** Workday HCM + Student → reporting / integration system (RaaS, custom reports, Prism Analytics) → vendor.
- **Common drift modes:**
  - **Academic period definitions.** Workday's `Academic Period` object is partner-configured; what one institution calls "Fall 2026" may be a parent period with three sub-terms. Vendor needs to know the granularity.
  - **EIB-based syncs are batch.** Real-time roster propagation isn't standard. Expect 24h+ lag unless the partner built event-driven integration.

### PeopleSoft Campus Solutions

- **Shape:** Legacy in many large state systems. PS query + DB link, or PS-as-source-of-truth into a data warehouse the vendor pulls from.
- **Common drift modes:**
  - **Customization sprawl.** Every institution has customized PS differently; "student" and "enrollment" can mean different things in different deployments.
  - **Bolt-on warehouses go stale.** Many partners pull from a Snowflake/Redshift warehouse that loads from PS overnight. Warehouse jobs fail silently; partner doesn't know.

### Slate (Technolutions)

- **Shape:** Admissions-and-CRM. Most relevant for partners doing recruitment or early-engagement analytics (pre-matriculation).
- **Common drift mode:** Slate's data model is admissions-first; mapping it to "enrollment" or "registration" requires institution-specific logic.

---

## The LMS layer: Canvas, Schoology, Brightspace, Moodle

LMS integration usually rides one of two contracts:

### LTI (Learning Tools Interoperability)

- **LTI 1.1** is legacy; **LTI 1.3 / Advantage** is current (OAuth 2.0 + JWT).
- **NRPS (Names and Role Provisioning Service)** is the LTI Advantage extension that gives the vendor a roster API at launch time.
- **Common drift modes:**
  - **LTI 1.1 still in use.** Some institutions haven't migrated. Vendor capability is reduced (no NRPS, no AGS for grades).
  - **Course context vs section context.** LTI launches with a `context_id`. Whether that maps to a course or section is LMS-configurable and partner-specific.

### Direct LMS roster API

- **Canvas API:** Mature, well-documented, rate-limited. Most common direct-integration target.
- **Schoology, Brightspace, Moodle:** APIs vary in completeness; Moodle in particular has heterogeneous deployments (each institution can install plugins that change the data shape).
- **Common drift mode:** Pagination errors silently truncating large rosters. A 50,000-student course pull that ends at page 99 returns 9,900 students; vendor doesn't notice unless it logs total counts.

---

## The corporate L&D stack

EdTech for corporate / workforce learning rides on HRIS as the source of truth.

- **HRIS-of-record:** Workday HCM, SAP SuccessFactors, BambooHR, ADP, Rippling. Each has its own API contract.
- **Provisioning protocol:** **SCIM 2.0** is the standard for user provisioning to the LMS or learning platform. **JIT (just-in-time)** provisioning at login is the alternative.
- **Common drift modes:**
  - **Org chart changes lag.** Manager change, department transfer, role change — the HRIS may update faster than the LMS sync.
  - **SCIM `active=false` vs hard-delete.** A SCIM deactivation should disable the user, not delete history. Some partners' systems hard-delete on `active=false`, losing engagement history.
  - **GDPR Article 88 + works-council restrictions** (EU). Employee learning data has additional constraints. Multinational partners frequently have country-by-country variation in what the LMS is allowed to log.

---

## Diagnostic checklist (run in this order)

When a partner reports "the data is wrong":

1. **Last successful sync timestamp** — for *each* upstream system (SIS → broker → vendor). A green status on the broker means the broker is healthy; not that the vendor has current data.
2. **Row count delta** — yesterday's row count vs today's. A 10%+ drop is almost always a sync issue, not a real attrition event.
3. **Sample 5 students** — pick names the partner can verify. Are their school, grade, section, and active status correct?
4. **Check the broker's sharing scope** — did a district admin change app permissions recently?
5. **Check encoding / required columns** — if CSV-based, run the file through a parser and compare row counts pre- and post-parse.
6. **Check the SIS-side change log** — is there a mid-year change (transfer, drop, schedule shift) that the broker hasn't propagated yet?
7. **Only after all six** — open a vendor-side product ticket. Premature escalation burns goodwill and slows the actual fix.

---

## Who-owns-what matrix (PSM coordination)

| Layer | Owner | PSM's lever |
|---|---|---|
| SIS (PowerSchool, Banner, Workday Student, etc.) | Partner's data team / IT | Cannot fix; can request, document, escalate |
| Broker (Clever, ClassLink) | Partner's IT admin via broker portal | Cannot fix; can guide partner-side admin |
| OneRoster CSV / endpoint | Partner's integration team | Cannot fix; can spec the required fix |
| Vendor's ingest pipeline | **Product / engineering at vendor** | **Can escalate; owns SLA** |
| Vendor's analytics / metrics layer | Product / engineering | Can escalate |
| Partner-facing dashboard | Vendor (potentially PSM-configurable) | Can adjust framing, can request changes |

The PSM does not own the rostering pipeline. The PSM *coordinates*: gets the right people from the partner side and the vendor side in one thread, with the diagnostic evidence already collected. **A PSM who tries to debug the SIS herself is operating outside her lane; a PSM who tolerates "we'll look into it" for a week without coordinating escalation is operating below it.**

---

## When to escalate to product vs coach the partner

- **Coach the partner** when the diagnostic points to: broker sharing scope, OneRoster encoding, district-side cron, SCIM config, LTI version, or admin-portal misconfiguration.
- **Escalate to product** when the diagnostic points to: vendor's parser silently dropping rows, vendor's API timing out on large pulls, vendor's metric definition disagreeing with partner's source-of-truth definition, or any vendor-side data-loss event.
- **Escalate to leadership** when: the rostering pipeline has been broken for >2 weeks, OR the partner has paused renewal conversations on rostering grounds, OR student-level PII has leaked.

---

## Refresh triggers for this document

Re-read and update when:

- 1EdTech ships OneRoster v1.3 (breaking changes likely).
- Clever or ClassLink materially changes pricing, terms, or sharing-scope defaults.
- A new SIS enters the K-12 market with meaningful share (rare).
- A new state passes a law that mandates a rostering-vendor change.
- Vendor-side adds new ingest paths (e.g., direct SCIM, native LTI Advantage support).

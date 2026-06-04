---
target_path: plugins/edtech-partner-success/knowledge/state-privacy-law-matrix.md
last_reviewed: 2026-06-04
refresh_triggers:
  - NCSL state-tracker reports a new bill or amendment
  - Public Interest Privacy Center state-law page updates
  - A new state passes a SOPPA / Ed Law 2-d-style framework
  - The 2025 DOE FERPA rulemaking issues a final rule
audience: [psm, dashboard-builder, dpa-author, security-reviewer]
status: field guidance — NOT legal advice
sources:
  - /tmp/research-ferpa-decision-tree.md §3, §4 (research ledger sources [24]-[33], [44])
---

# State student-privacy law matrix — NY 2-d, IL SOPPA, CA SOPIPA strict-superset rules

> **Status.** Operational reference for which state-law overlay applies on top of FERPA for any EdTech engagement. **Field guidance only — NOT legal advice.** Specific compliance questions route through the LEA's counsel or the vendor's DPO.

---

## 1. The strict-superset rule of thumb

**A DPA that satisfies NY Ed Law § 2-d Part 121 + IL SOPPA is almost certainly compliant in every other US state.** [source [28] in research ledger]

Build to NY+IL; everything else falls out. If your dashboard ships to either NY or IL districts, build to those two; if it ships to CA, layer CCPA/SOPIPA on top of the NY+IL baseline.

> **CT watch-list note (added 2026-06-04).** The Illuminate Education multistate AG settlement (Nov 12, 2025) was the **first enforcement** under CT's student-data-privacy law. CT can no longer be treated as a CCPA-equivalent baseline state for EdTech — a vendor operating in CT now faces real AG enforcement exposure. Treat CT as a fourth superset state for any DPA review touching CT districts. See [`edtech-enforcement-precedents-2025-2026.md`](./edtech-enforcement-precedents-2025-2026.md) for the playbook.

---

## 2. The matrix (FERPA + the three superset states)

| Dimension | FERPA (federal floor) | CA SOPIPA + CCPA/CPRA | NY Ed Law § 2-d / Part 121 | IL SOPPA |
|---|---|---|---|---|
| **Statutory cite** | 20 USC § 1232g; 34 CFR Part 99 | Cal. Bus. & Prof. Code §§ 22584-22585 | NY Educ. Law § 2-d + 8 NYCRR Part 121 | 105 ILCS 85/ |
| **Targeted advertising on K-12 students** | Not specifically prohibited | **Prohibited** | Prohibited | Prohibited |
| **Selling student data** | Permitted under "school official" if contract restricts | **Prohibited** | Prohibited | Prohibited |
| **Building student profiles for non-educational purposes** | Not addressed | **Prohibited** | Prohibited | Prohibited |
| **Vendor security framework** | Reasonable methods (§ 99.31(a)(1)(ii)) | Reasonable | **NIST CSF required** (Part 121) | "Reasonable security measures" |
| **Parents' Bill of Rights** | None | None | **Required, posted on district site** | Yes; **list of operators on district site** |
| **Data Protection Officer (LEA-side)** | None | None | **Required per LEA** | None |
| **Breach notification to district** | None | None (state breach law applies) | "As soon as possible" / 7 days | **Operator → school: 30 days; school → parents: 30 days** |
| **Breach posting on district site** | None | None | None | **Required within 10 days if >10% of students affected** |
| **List of operators / contracts published** | None | None | **Supplemental info per contract** | **Full list + data shared + subcontractors** |
| **Staff training mandate** | None | None | **Annual privacy/security training** | Encouraged |
| **Enforcement (2026)** | DOE complaints; loss of federal funds; **CDE finding Jan 28 2026 = first written notice of findings in FERPA enforcement process** | AG + private right (varies); **KOPIPA first enforcement Illuminate Nov 2025**; multistate AG coordination | NYSED Chief Privacy Officer; civil penalties; **multistate AG coordination (2nd enforcement Illuminate Nov 2025)** | AG + private suits; **published-list rule uncontested in court** |

[source: research §3]

---

## 3. The state-by-state long tail (post-NY/IL/CA)

Following the SOPPA / Ed Law 2-d template, with growing reach:

| State | Statute | What's distinctive |
|---|---|---|
| **Connecticut** | CT Pub. Act 16-189 + **CT SB 3 / Public Act 23-56** (amended CTDPA with minor-protection + AADC-equivalent provisions; effective Jul 2024-Oct 2024) | Mirrors NY Ed Law 2-d; published contracts. **AG cure-period was mandatory Oct 2024-Dec 2025; Jan 1, 2026 onward, cure is AG discretion. Neural data classified as sensitive PI effective Jul 1, 2026.** [verify-at-use — 2026-06-04] |
| **Colorado** | HB 16-1423 | Operator list public; sale prohibition |
| **Texas** | SB 820 + **SCOPE Act HB 18 (signed Jun 13, 2023; 2 preliminary injunctions Aug 30, 2024 + Feb 7, 2025)** | Cybersecurity framework + breach SLA. **SCOPE Act monitoring/filtering + age-verification provisions enjoined; core EdTech PII protections — no targeted ads, no non-educational profiles, no sale — remain enforceable. $10K/violation.** [verify-at-use] |
| **Virginia** | VA Code § 22.1-289.01 + **VCDPA child amendments SB 361/HB 707 (signed May 17, 2024; effective Jan 1, 2025)** | Vendor agreements + de-identification standard. **Parental-consent required for processing personal data from a known child (<13) for profiling that produces legal or significant effects. Social-media 1-hr/day rule signed May 2, 2025, under appeal.** |
| **Washington** | RCW 28A.604 | Student data inventory + parental access |
| **Utah** | Utah Code § 53E-9 | Data dictionary + student access |
| **Florida** | F.S. § 1002.222 + Florida Digital Bill of Rights (effective Jul 1, 2024) | Marketplace contract template; AG enforcement |
| **Maryland** | **Maryland Online Data Privacy Act (effective Oct 1, 2025; processing-activities deadline Apr 1, 2026)** | **35,000-consumer threshold notably lower than other states — captures more mid-size EdTech.** [verify-at-use] |
| **Tennessee** | **TIPA (effective Jul 1, 2025)** | Comprehensive privacy law; **applies only to businesses with revenue > $25M.** Not student-specific. |

Refresh quarterly against NCSL state-tracker + Public Interest Privacy Center [44].

---

## 4. DPA template implications

### What every multi-state DPA must include

These flow directly from the strict-superset rule above:

1. **NIST CSF alignment** (from NY § 2-d Part 121) — the security plan in the DPA references a recognized framework, not "reasonable measures."
2. **Subprocessor list** (from IL SOPPA + NDPA v2.2 Exhibit H — checkbox removed, disclosure mandatory) — every downstream vendor named, including AI providers (OpenAI, Anthropic, Pinecone, etc.).
3. **Breach SLA — operator to school within 30 days** (IL floor; NY is stricter at "as soon as possible / 7 days" so build to NY).
4. **Parents' Bill of Rights** posted on district site (NY § 2-d) — vendor provides the boilerplate.
5. **Targeted-advertising prohibition** (CA SOPIPA + NY + IL) — even if the contracting LEA is in a non-superset state.
6. **Profile-building prohibition** (CA SOPIPA + NY + IL).
7. **De-identified data carveout** defined to PTAC standard, not vendor's marketing definition.
8. **Deletion at contract termination** within standard wind-down (30-90 days).
9. **Audit rights** for the LEA.
10. **No FERPA waiver via TOS** — the 2025 DOE FAQ (37-question update) ruled this invalid.

### NDPA v2.2 (SDPC, Nov 19, 2025) is the contract substrate

The Student Data Privacy Consortium's NDPA v2.2:
- **Exhibit E (general offer)** is now **mandatory**
- **Exhibit H (subprocessor list)** checkbox removed — disclosure is mandatory
- Updates to data-breach, sub-processor restrictions, advertising limits, and **de-identified data use**

If your DPA is not built on NDPA v2.2 (or fully covers its provisions), expect rejection from NY / IL districts at procurement.

---

## 5. Cross-walk: state law triggers in the FERPA decision tree

The FERPA decision tree's Q11 ("State law overlay") collapses to this matrix:

| If any student in the cell is in... | The strictest applicable rule says... |
|---|---|
| CA | Must satisfy SOPIPA (no targeted ads, no sale, no profile-building) + CCPA |
| NY | NIST CSF + Parents' Bill of Rights + DPO + breach SLA + operator list |
| IL | Subprocessor disclosure + 30-day breach SLA + 10-day site posting if >10% affected |
| CT, CO, TX, VA, WA, UT, FL | Per state column above |
| Multi-state cohort | Build to the strict superset of all applicable states |

If the DPA doesn't satisfy each row that applies, route to STOP10 (state-law violation).

---

## 6. Recent enforcement reshaping the matrix

| Case | Year | Lesson |
|---|---|---|
| **FTC v. Edmodo** | 2023 | "Schools consented" is not a defense if the vendor didn't supply notice materials |
| **FTC amicus, Shanahan v. IXL** | 2024-2025 | Schools cannot bind parents to vendor TOS arbitration; school consent is narrow to educational purposes |
| **PowerSchool / Naviance settlement** ($17.25M) | Feb 2026 | Third-party telemetry on student-facing surfaces is a wiretap claim; covers Google Analytics, Mixpanel, Heap, FullStory |
| **TX AG v. PowerSchool** | Sep 2025 | Breach (Dec 2024) exposed ~60M students — largest in US history |
| **FTC COPPA Final Rule** | Eff. June 2025; compliance by April 22, 2026 | New separate verifiable parental consent for third-party disclosures |
| **Illuminate Education multistate AG** | Nov 12, 2025 | **$5.1M**; **first** enforcement under CA KOPIPA + CT student-data law; **second** under NY § 2-d. Three AGs acting together rewrites the small-cluster enforcement calculus. |
| **CDE FERPA finding** | Jan 28, 2026 | First written notice of findings progressed to that stage in FERPA enforcement process. Ends the "FERPA has no teeth" era. |
| **PowerSchool / Naviance class settlement** | Feb 27, 2026 preliminary; Jun 10, 2026 final hearing | $17.25M; wiretapping / unauthorized disclosure theory (not breach). Class period Aug 2021 – Jan 2026. Co-defendant exposure (CPS). |
| **NetChoice v. Bonta (CAADCA)** | Mar 12, 2026 Ninth Circuit | Most CAADCA provisions remain enjoined; **age-estimation + most-protective-default-privacy-settings revived as potentially enforceable**; data-use restrictions stay blocked. |

[research §2; FERPA 2026 deep-research scan]

---

## 6a. 2026 enforcement scoreboard (added 2026-06-04)

For a single-page reference when triaging a vendor incident:

| Action | Amount | Theory | Why it matters for our dashboard gate |
|---|---|---|---|
| Illuminate Education multistate AG (CA + NY + CT) | $5.1M | Multistate breach + parallel state-law violations | Small-cell incidents reach AGs in NY+CA+CT cluster even without DOE FERPA complaint |
| PowerSchool Dec 2024 breach | (Litigation only; AG settlement expected) | Credential-compromise breach | Subprocessor MFA + dwell-time audit now baseline |
| PowerSchool Naviance class settlement | $17.25M | Wiretapping / silent monitoring (no breach) | "No breach = no FERPA exposure" is now false; dashboard widgets touching student-staff content require DPA disclosure + parent opt-in |
| CDE FERPA finding | (Sanction TBD) | FERPA disclosure obligations | DOE direct enforcement back on; "FERPA never enforces" defaults obsolete |

Full taxonomy + PSM playbook: [`edtech-enforcement-precedents-2025-2026.md`](./edtech-enforcement-precedents-2025-2026.md).

---

## 7. Refresh cadence

- **Quarterly** — sweep NCSL state-tracker + Public Interest Privacy Center [44]
- **Event-driven** — any FTC enforcement action, NYSED CPO order, IL AG action, or DOE rulemaking
- **Partner-driven** — when a new LEA's state isn't on the matrix, add it before signing

---

## Sources

- Research ledger §3 + §4 sources [24]–[33], [35]–[40], [44]
- Cybernut *All About NY's Education Law § 2-d* and *All About SOPPA* (operational summaries)
- SDPC *NDPA v2.2* (Nov 19, 2025) — https://privacy.a4l.org/national-dpa/
- Center for Democracy & Technology *Commercial Companies and FERPA's School Official Exception* (2024 survey)
- Hireplicity *FERPA Compliance Checklist 2025: Schools & EdTech Guide* — the NY+IL heuristic source

Full ledger: `/tmp/research-ferpa-decision-tree.md` §Sources.

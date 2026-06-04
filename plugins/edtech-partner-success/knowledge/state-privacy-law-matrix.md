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
| **Enforcement** | DOE complaints; loss of federal funds | AG; private right of action varies | NYSED Chief Privacy Officer; civil penalties | AG; private suits |

[source: research §3]

---

## 3. The state-by-state long tail (post-NY/IL/CA)

Following the SOPPA / Ed Law 2-d template, with growing reach:

| State | Statute | What's distinctive |
|---|---|---|
| **Connecticut** | CT Pub. Act 16-189 | Mirrors NY Ed Law 2-d; published contracts |
| **Colorado** | HB 16-1423 | Operator list public; sale prohibition |
| **Texas** | SB 820 | Cybersecurity framework + breach SLA |
| **Virginia** | VA Code § 22.1-289.01 | Vendor agreements + de-identification standard |
| **Washington** | RCW 28A.604 | Student data inventory + parental access |
| **Utah** | Utah Code § 53E-9 | Data dictionary + student access |
| **Florida** | F.S. § 1002.222 | Marketplace contract template; AG enforcement |

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

[research §2]

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

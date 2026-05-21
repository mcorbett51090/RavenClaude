# Parent comms — FERPA + state-specific jurisdictional bear traps

> **Last reviewed:** 2026-05-21. Source: research-distilled from FERPA (34 CFR Part 99), COPPA (16 CFR Part 312), and state student-privacy statutes current as of 2026-05. **This document is field guidance, not legal advice** — any specific question about whether a disclosure is FERPA-compliant escalates to counsel via the partner. Refresh when: (a) a state passes new student-privacy legislation, (b) the US Department of Education issues new FERPA guidance, (c) a major rostering vendor's terms change in a way that affects the partner's data-sharing obligations, or (d) any partner reports an actual incident — the lesson gets captured here.

When a PSM is drafting (or reviewing) communications that will reach parents, families, or students, the bar is **higher than the PSM-to-partner email** for three reasons: parents are not the partner's customers, the comms may surface in legal discovery, and the jurisdictional layer (federal + state) shifts the rules depending on where the partner sits. This document is the checklist.

---

## The three buckets (federal floor)

Everything starts with these three FERPA-defined categories:

1. **Education records** — protected. Anything the school maintains that is directly related to a student. Grades, attendance, disciplinary actions, IEPs, 504 plans, health records held by the school, special-program participation.
2. **Personally identifiable information (PII)** within those records — protected. Name, address, parent name, biometric ID, *and* "other information that, alone or in combination, is linked or linkable to a specific student that would allow a reasonable person in the school community to identify the student with reasonable certainty."
3. **Directory information** — disclosable *unless the parent has opted out*, and the district has designated which categories are directory. Typical: name, address, phone, photo, sport/activity participation, dates of attendance, degree/honors. **Each district's directory designation is different — don't assume.**

The vendor (and PSM) does not get to decide which bucket something falls into. The district (the educational agency) decides.

### The "identifiable from context" trap

The most common bear trap is not direct PII disclosure — it's the **residual**. Examples:

- "The 3 students in our junior class who chose option B" — names not given, but the class is small enough that classmates can identify the three.
- "Students with active 504 plans receiving the new intervention" — by structure, names everyone with a 504.
- "Top 5 performers in the pilot cohort, by school" — when a school had 6 participants, the missing one is identifiable.

FERPA explicitly prohibits this. The PSM heuristic: **if naming a number small enough to be socially countable in the context, treat it as PII.** Rough rule of thumb in field practice: groups of <10, treat as identifying; groups of 10-30, scrutinize; >30, usually safe.

---

## Higher-ed vs K-12 — the rights-holder shifts

This is a frequent error in K-12-default thinking:

- **K-12:** Parents are the rights-holders. Parent consent. Parent access. Parent opt-out for directory info.
- **Higher-ed:** The student becomes the rights-holder on the earlier of (a) age 18 or (b) matriculation in a postsecondary institution. Parent consent stops mattering. **Sending a "parent letter" to higher-ed students' parents about the student's academic record without student consent is a FERPA violation.**

Exceptions exist (the student is claimed as a dependent on the parent's federal tax return — institution may release, but most institutions still don't by policy), and dual-enrolled high-schoolers complicate this further. **When in doubt at the K-12/higher-ed boundary, route through the institution's registrar.**

---

## COPPA — the under-13 layer

For students under 13, the Children's Online Privacy Protection Act (COPPA) imposes additional vendor obligations on the platform that *collects* the data. Schools can act as parents' agents under the "school authorization" exception, but the scope is "data collected for the school's use of the educational service." Marketing communications to parents that reference a child's product usage frequently land outside that exception.

- If the partner's product is COPPA-covered and the PSM is drafting a *parent-facing* announcement about the child's individual usage, the announcement is functionally a disclosure that requires the school's authorization — and the school authorization scope must cover what's being disclosed.
- If the parent-facing comm is at a *general* level ("here's what the program does for all students"), COPPA is not the lever; FERPA is.

The bright-line PSM rule: **comms that name an individual student's behavior to that student's parents = school-authorized educational use only; not vendor-initiated marketing.**

---

## State-specific layers (the most common bear traps)

State student-privacy law layers *on top of* FERPA. The PSM doesn't need to be a lawyer; the PSM needs to recognize **which states' partners require flagging** and route to the partner's counsel or the regulatory-compliance team when triggered.

### California — SOPIPA + CCPA/CPRA

**SOPIPA** (Student Online Personal Information Protection Act, 2014; amended 2016 to include K-12, and expanded by subsequent legislation):

- Prohibits targeted advertising based on K-12 student information.
- Prohibits creating profiles for non-educational purposes.
- Prohibits selling K-12 student data.
- Requires security practices for student PII.

**CCPA / CPRA** (California Consumer Privacy Act / Privacy Rights Act):

- Layers consumer-side rights. Students/parents have rights to know, access, correct, delete.
- The interaction with FERPA/SOPIPA is non-trivial; the safe posture is "vendor honors the most restrictive applicable law."

**PSM tell:** California districts often include vendor-side data-handling language in contracts. Read it; don't assume the federal floor is the whole picture.

### Illinois — SOPPA

**SOPPA** (Student Online Personal Protection Act):

- Requires school districts to **publish** a list of vendors collecting student data and the data categories collected.
- Requires a **written agreement** between district and vendor disclosing what is collected, how it's used, security practices, and breach notification.
- Requires **30-day breach notification** to the district.
- Requires data **deletion within 60 days** of contract end (with limited exceptions for de-identified data).

**PSM tell:** Illinois districts often surface SOPPA language late in the procurement cycle. If a renewal stalls, SOPPA-driven contract language is a common cause.

### New York — Ed Law §2-d + Part 121

**Education Law §2-d** + **8 NYCRR Part 121**:

- Requires the **Parents' Bill of Rights for Data Privacy** in every district vendor contract.
- Requires the vendor to adhere to a **data privacy and security plan** aligned with the NIST Cybersecurity Framework.
- Requires districts to **publish a data inventory** listing what student PII the district shares with vendors.
- Requires vendors to designate a data protection officer.
- Imposes **personal liability** in some breach scenarios.

**PSM tell:** New York districts have the most procedurally rigorous student-privacy environment in the US as of 2026. A vendor without a NIST-aligned security narrative will not get past procurement.

### Connecticut — Public Act 16-189

Similar in structure to NY Ed Law §2-d. Requires districts to maintain a list of contracts and the data categories. Requires vendor written agreements. **PSM tell:** less procedurally onerous than NY but the same shape.

### Colorado — HB 16-1423

**Student Data Transparency and Security Act:**

- Requires districts to publish a list of vendors and data shared.
- Vendor agreements must include security and deletion provisions.

### Texas — SB 820 and others

Cybersecurity-incident notification requirements layered on top of student-privacy norms. State-mandated cybersecurity framework for districts.

### Virginia, Washington, Utah, Florida, others

A growing list have student-privacy statutes; many follow the SOPPA / Ed Law 2-d template. **The PSM heuristic: if the partner is in any state with student-privacy law, the comms-and-contract bar is higher than federal floor — flag and route.**

---

## Multilingual obligations — Title VI and state-level

The Civil Rights Act Title VI requires meaningful access for limited-English-proficient (LEP) populations receiving federal funds. For schools, this means **substantive parent communications must be accessible in the parent's primary language** (not just English).

- **NY** has specific requirements naming the top eight languages spoken statewide.
- **CA** has Title III + state-specific rules on translation thresholds.
- **TX, IL, FL** all have state-level requirements layered on Title VI.

**PSM rule:** Any parent-facing announcement going to a district with substantial non-English-primary households requires (a) translation, not transliteration, (b) cultural-context tuning, not literal rendering, (c) review by a native-speaking reviewer if stakes are high (legal-bearing notifications, incident comms, opt-out forms).

The [`ferpa-comms-translator`](../agents/ferpa-comms-translator.md) is the agent for this; the present document is the regulatory layer that sits behind it.

---

## The "X students" / cohort residual checklist

Before any parent-facing comm goes out, run:

1. **Does the comm name a number?** ("3 students," "12% of the cohort," "the top 5 performers")
2. **Is the denominator small enough that classmates / parents can identify the missing or named?** Use the <10 rule of thumb.
3. **Does the comm name a category that itself is identifying?** ("students in [program]," "students receiving [intervention]," "students with [accommodation]") — these are often more disclosing than naming students directly.
4. **Does the comm say anything that the district hasn't formally disclosed as directory information?** If yes, requires consent.
5. **Does the comm assume parental rights in a higher-ed context?**
6. **Does the comm trigger any state-specific notification or formatting requirement?**

If any answer is "uncertain," route to the partner's counsel before sending. The PSM's job is to surface the question, not to answer it.

---

## When in doubt — the route

- **Drafting a parent-facing comm** → [`ferpa-comms-translator`](../agents/ferpa-comms-translator.md) is the primary author. This document is the reference it consults.
- **The comm names individual students or small cohorts** → flag for `security-reviewer` and recommend the partner's counsel review.
- **The partner is in IL, NY, CA, CT, CO, TX, VA, WA, UT, FL, or any state with active student-privacy legislation** → flag the state-specific layer explicitly in the response.
- **The audience includes non-English-primary households** → multilingual variant required; flag cultural-context review.
- **Any actual incident** (data exposure, mis-sent comm, parent complaint) → escalate immediately; capture the lesson back into this document.

---

## Anti-patterns the comms-translator flags

- A parent-facing comm that names a small cohort (<10) without consent
- A parent comm in a higher-ed context that assumes the parent is the rights-holder
- A comm in a state-privacy-law jurisdiction without state-specific review
- A "Spanish version" that is a literal translation with no cultural-context adjustment
- A multi-district announcement that lists district names visibly in the To: line
- An announcement whose subject line discloses program participation
- A parent comm that uses unexplained jargon (the partner's internal terminology)
- A COPPA-relevant individual-student comm framed as marketing rather than school-authorized educational use
- A comm that asserts "FERPA-compliant" without naming who reviewed it

---

## Refresh triggers for this document

Re-read and update when:

- Any state passes new student-privacy legislation (track via NCES, FERPA|Sherpa, or state-specific announcements).
- US DoE issues new FERPA guidance or Dear Colleague letters (sub to PTAC bulletins).
- A major rostering vendor (Clever, ClassLink) changes its terms in a way that shifts vendor data-handling obligations.
- Any partner reports an actual student-privacy incident — the lesson gets captured here, even if minor.
- COPPA gets amended (long-discussed; would materially change the under-13 vendor obligations).

---

## What this document is *not*

- It is **not legal advice.** Specific compliance questions about a specific partner's contract or proposed disclosure go to that partner's counsel.
- It is **not a substitute** for the partner's published Parents' Bill of Rights, data privacy plan, or data inventory.
- It does **not** replace the school's role as the authorizing party under FERPA and COPPA.

The PSM's job is to **recognize the shape of the question** and route to the right reviewer fast enough to avoid harm.

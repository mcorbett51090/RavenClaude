---
description: "Section 508 / WCAG 2.x conformance lifecycle: gap assessment, automated and manual testing methodology, VPAT/ACR authoring using the ITIC template, remediation prioritization, and ongoing testing cadence. Covers FOIA / public-records request handling (intake, exemption analysis, redaction, response timelines) and plain-language compliance (Plain Writing Act, Federal Plain Language Guidelines)."
---

# Section 508, WCAG, and Government Records

**Purpose:** produce legally defensible Section 508 / WCAG conformance reports, FOIA responses, and
plain-language documents — all grounded in the actual statutory and technical standards.

---

## Part A — Section 508 / WCAG 2.x Conformance

### Step 1 — Determine Applicability

- Federal agencies and contractors providing ICT (Information and Communications Technology) to
  federal agencies are subject to the Rehabilitation Act § 508, implemented via the Access Board's
  508 Technical Standards (January 2017 refresh).
- The 2017 standards harmonize with WCAG 2.0 Level AA for web and software (and point to WCAG 2.1
  AA as best practice). Check the agency's solicitation — many now require WCAG 2.1 AA.
- Scope: web content, software applications, mobile apps, electronic documents (PDF/Office), video,
  hardware, support documentation and services.

### Step 2 — Automated Testing

Select tools appropriate to the artifact type:

| Tool | Best for | Notes |
|---|---|---|
| axe-core / Deque axe DevTools | Web / SPA | Most widely used; integrates with CI |
| WAVE (WebAIM) | Web pages | Visual output; good for training |
| ANDI (SSA) | Web — government standard | Required by some agencies; free |
| Lighthouse (Google) | Web performance + accessibility | Subset of axe rules |
| PAC 3 / Adobe Acrobat | PDF documents | PAC 3 is free; most thorough for PDF/UA |
| Microsoft Accessibility Checker | Office documents | Built into Word/Excel/PowerPoint |

Automated tools catch ~30–40% of WCAG issues. They are a floor, not a ceiling.

### Step 3 — Manual Testing Checklist

Each item maps to one or more WCAG 2.1 AA success criteria:

- **Keyboard navigation (SC 2.1.1, 2.1.2):** every interactive element reachable and operable
  by keyboard alone; no keyboard traps.
- **Focus order (SC 1.3.2, 2.4.3):** logical tab order matches visual order; focus indicator visible.
- **Screen reader (SC 1.1.1, 1.3.1, 4.1.2):** test with NVDA+Firefox (Windows), JAWS+Chrome
  (Windows), VoiceOver+Safari (macOS/iOS). All content announced correctly; form labels programmatically
  associated; status updates announced.
- **Color contrast (SC 1.4.3, 1.4.11):** normal text ≥ 4.5:1; large text ≥ 3:1; UI components ≥ 3:1.
  Use Colour Contrast Analyser (TPGi) or browser dev tools.
- **Images and non-text content (SC 1.1.1):** all images have descriptive alt text; decorative images
  are marked `alt=""`.
- **Forms (SC 1.3.1, 3.3.1, 3.3.2):** labels programmatically associated; error messages descriptive;
  required fields identified.
- **Time limits (SC 2.2.1):** user can extend or disable time limits.
- **Motion and animation (SC 2.3.1, 2.3.3):** no content flashes >3 Hz; animation can be paused/stopped.
- **Language (SC 3.1.1, 3.1.2):** page language set; language changes within content marked.
- **Cognitive load (WCAG 2.2 new):** consistent navigation, clear labels, error prevention.

### Step 4 — VPAT / ACR Authoring (ITIC Template 2.x)

The ITIC VPAT 2.x is the industry standard for government solicitations. Sections:

1. **Product description** — version, date of evaluation, URL.
2. **Evaluation methods used** — automated tools + versions, manual test methodology, AT used.
3. **Applicable standards / guidelines** — check which edition applies (WCAG 2.0, 2.1; Section 508).
4. **Terms** — conformance levels: Supports / Partially Supports / Does Not Support / Not Applicable.
5. **WCAG 2.x Report** — per-success-criterion row:
   - Level A (25 criteria), Level AA (13 additional criteria).
   - For each: conformance level + remarks (what works, what doesn't, how to reproduce failure).
   - "Supports" requires test evidence. Never mark Supports without testing.
6. **Section 508 Chapter 3** — Functional Performance Criteria (FPC 302.1–302.9).
7. **Chapter 4** — Hardware (if applicable).
8. **Chapter 5** — Software.
9. **Chapter 6** — Support documentation and services.

Remarks discipline: for Partially Supports or Does Not Support, remarks must describe:
- What specific functionality does not support the criterion.
- Which user populations are affected.
- Remediation plan / timeline (if the VPAT is for a work-in-progress product).

### Step 5 — Remediation Prioritization

| Priority | Criteria | Example |
|---|---|---|
| Blocker | Prevents core-task completion for AT users | No keyboard access to primary nav |
| Major | Significantly degrades AT experience | Screen reader misreads form fields |
| Minor | Inconvenient but workaround exists | Decorative image missing alt="" |

Sequence: fix blockers in the current sprint; majors in the next sprint; minors in the backlog.

---

## Part B — FOIA / Public Records

### Intake and Acknowledgment

1. Log the request (date received, requester contact, description of records sought).
2. Acknowledge within 20 business days (federal statutory requirement, 5 U.S.C. § 552(a)(6)(A)).
   For state public-records requests: timelines vary by state (3–10 business days typically).
3. Determine if the request is reasonably described — if not, contact the requester for clarification
   before the clock runs.

### Responsive-Records Determination

1. Identify the offices/custodians that would hold responsive records.
2. Conduct a reasonable search — email, shared drives, paper files, databases. Document the search.
3. Determine whether records exist, are in agency possession, and are subject to FOIA (FOIA covers
   agency records; personal notes not used in agency business are not agency records).

### Exemption Analysis (5 U.S.C. § 552(b))

| Exemption | Scope | Notes |
|---|---|---|
| 1 | Classified national security information | Requires classification determination |
| 2 | Internal personnel rules and practices | Narrow; high 2 / low 2 distinction |
| 3 | Exempt by statute (e.g., tax returns, grand jury) | Cite the specific statute |
| 4 | Trade secrets / confidential commercial information | Submitter notice required |
| 5 | Deliberative process privilege / attorney-client / work product | Not a blanket shield; apply narrowly |
| 6 | Personal privacy (clearly unwarranted invasion) | Balance public interest |
| 7 | Law enforcement records | Specific harm must be identified |
| 8 | Financial institution examination records | |
| 9 | Geological information | |

**Segregability (5 U.S.C. § 552(b)):** non-exempt portions of documents must be released with
exempt portions redacted. Withholding an entire document when only part is exempt is a legal error.

### Redaction and Response

1. Redact with clear markings (Exemption number on each redaction).
2. Response letter: enumerate exemptions applied, describe withheld records, advise of appeal rights.
3. For denials: provide the name and title of the person responsible for the denial.
4. Appeal process: administrative appeal to the agency's FOIA Appeals Officer; then judicial review.

---

## Part C — Plain Language

### Federal Plain Language Guidelines (the short list)

1. **Active voice:** "The agency will review your application" not "Applications will be reviewed."
2. **Short sentences:** average ≤ 20 words. Break compound sentences.
3. **Common words:** "use" not "utilize"; "show" not "demonstrate"; "help" not "facilitate."
4. **Headers and lists:** use question-and-answer format for instructions; use bulleted lists for
   options; use numbered lists for sequences.
5. **Pronouns:** use "you" for the reader and "we" for the agency.
6. **Reading level target:** 6th–8th grade for public-facing content (Flesch-Kincaid Grade Level).

### Plain Writing Act Scope

Covers federal executive agencies; applies to covered documents issued after October 13, 2010,
including all new or substantially revised letters, publications, forms, notices, and instructions
sent to the public. Not a private right of action — enforcement is through OMB oversight.

---

## Anti-patterns

- Claiming WCAG conformance without documented manual testing with assistive technology.
- Marking VPAT criteria "Not Applicable" without a basis.
- Applying Exemption 5 to entire documents without segregability analysis.
- Citizen-facing documents above 10th grade reading level.
- Delaying FOIA acknowledgment beyond 20 business days.

## Output

A conformance assessment report, a completed VPAT/ACR, a FOIA response package, or a plain-language
revision. Delivered with the applicable legal citations and a remediation tracker.

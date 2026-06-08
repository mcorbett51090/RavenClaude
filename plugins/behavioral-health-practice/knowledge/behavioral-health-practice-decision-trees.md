# Behavioral-Health Practice — Decision Trees

_Decision trees + a dated reference map. Rows marked `[verify-at-build]` are time-sensitive (CPT codes, payer policy, regulatory specifics) — re-check against the current code set / payer policy / regulation before quoting to a client. **Operational and documentation support only — not clinical, medical, or legal advice.** Last reviewed: 2026-06-08._

Traverse before scheduling against an authorization, disclosing a record, or wiring the intake→claim flow. PHI stays in the EHR — these trees use placeholders only.

## Decision Tree: Is a prior authorization required (and confirmed)?

An authorization is confirmed in writing or it does not exist. Booking against an assumed auth is a denial waiting to happen.

```mermaid
graph TD
  A[New / continuing client, planned sessions] --> B{Eligibility verified — active coverage + behavioral benefit?}
  B -- No --> C[Verify benefits first - no scheduling against unconfirmed coverage]
  B -- Yes --> D{Does the plan require prior auth for this service / CPT?}
  D -- No --> E[No auth needed - confirm session limits + copay, proceed to schedule]
  D -- Unknown --> F[Treat as required - confirm with payer before scheduling]
  D -- Yes --> G{Auth requested with codes, units, and medical-necessity attachment?}
  G -- No --> H[Assemble the request packet first - codes, units, dx, necessity from the note]
  G -- Yes --> I{Auth APPROVED in writing — number + unit count captured?}
  I -- No / pending --> J[Do NOT schedule against it yet - track to a decision]
  I -- Yes --> K[Schedule WITHIN the approved units; re-auth before they run out]
```

_The code reflects the service rendered, never the reimbursement wanted. If the documentation doesn't support the time/modality, the code drops — route the gap to documentation, don't stretch the code._

## Decision Tree: Is this record 42 CFR Part 2-covered, and can we disclose it?

Part 2 (substance-use-disorder) records carry consent requirements HIPAA does not. When unsure whether a record is Part 2-covered, assume it is.

```mermaid
graph TD
  A[Disclosure requested — to payer / referral / family] --> B{Does the record contain SUD treatment information from a Part 2 program?}
  B -- Unknown --> C[Assume Part 2 applies - require specific written consent before disclosure]
  B -- No, general behavioral health --> D{Valid HIPAA authorization / ROI on file for this disclosure?}
  D -- No --> E[Do NOT disclose - obtain the ROI first; consent precedes disclosure]
  D -- Yes --> F[Disclose only what the ROI authorizes - minimum necessary]
  B -- Yes, Part 2 SUD content --> G{SPECIFIC written Part 2 consent on file naming this recipient + purpose?}
  G -- No --> H[Do NOT disclose SUD content - a general HIPAA authorization is NOT enough]
  G -- Yes --> I[Disclose only the consented SUD content; flag any clinical-content question to the clinician]
```

_Consent precedes disclosure, every time. A general HIPAA authorization does not cover Part 2 SUD content — that needs its own specific consent. Route any question about what the clinical content *means* to a licensed clinician; this is a consent/operations call, not a clinical one._

## Decision Tree: Which progress-note CPT reflects this session?

The code follows the documented service — time, modality, who was present — never the reimbursement wanted. If the documentation doesn't support it, the code drops.

```mermaid
graph TD
  A[Session delivered, ready to code] --> B{Is this an intake / diagnostic evaluation?}
  B -- Yes --> C[Diagnostic-eval family - confirm code + payer policy verify-at-build]
  B -- No --> D{Who was present / what modality?}
  D -- Group --> E[Group-psychotherapy family - confirm code verify-at-build]
  D -- Family / couple --> F{Client present?}
  F -- Yes --> G[Family-with-client-present code verify-at-build]
  F -- No --> H[Family-without-client-present code verify-at-build]
  D -- Individual --> I{Documented face-to-face time supports which tier?}
  I -- Time NOT documented --> J[Cannot pick a time-based code - route the gap to documentation, do not guess]
  I -- Time documented --> K[Pick the time-based individual code matching the documented minutes]
  K --> L{Delivered via telehealth?}
  L -- Yes --> M[Add the telehealth modifier + place-of-service per current payer policy verify-at-build]
  L -- No --> N[Office place-of-service; bill the time-based code]
```

_Time and modality determine the code; the documentation must support the time. Never upcode. Confirm every code, modifier, and place-of-service against the current CPT set and the specific payer's policy before treating it as final._

## Decision Tree: Is this telehealth visit ready (and billable)?

A telehealth visit fails differently than an in-person one. Treat readiness as a step of the appointment, and confirm the modality is billable before the claim — not after.

```mermaid
graph TD
  A[Telehealth visit scheduled] --> B{Is telehealth clinically appropriate for this client?}
  B -- Clinical question --> C[Route to the clinician - this plugin does not make the clinical call]
  B -- Confirmed appropriate by clinician --> D{Join link + tech check sent ahead of time?}
  D -- No --> E[Send link + brief tech check now - a couldnt-connect no-show is preventable]
  D -- Yes --> F{Client location + modality consent confirmed?}
  F -- No --> G[Confirm location for licensure / payer / emergency response + consent to modality]
  F -- Yes --> H{Payer reimburses this service via telehealth this benefit year?}
  H -- Unknown --> I[Verify telehealth coverage + modifier + POS before billing verify-at-build]
  H -- No --> J[Re-plan modality or set client expectation on cost before the visit]
  H -- Yes --> K[Proceed; apply the telehealth modifier + place-of-service on the claim verify-at-build]
```

_The clinical-appropriateness of telehealth is the clinician's call; the readiness logistics and the billing modality are this plugin's. Confirm the modifier and place-of-service against current payer policy before billing._

## Decision Tree: Is this referral loop closed?

A referral is done when the loop closes — the client reached the destination and that's recorded — not when it's sent. Open loops are where clients fall through.

```mermaid
graph TD
  A[Referral created — inbound or outbound] --> B{Is it acknowledged with a name + date owning it?}
  B -- No --> C[Assign an owner + date - an unowned referral ages silently into a leak]
  B -- Yes --> D{Has the client reached a terminal state?}
  D -- Scheduled / connected --> E[Record the landing - loop closed]
  D -- Declined --> F[Record the decline + reason - loop closed]
  D -- Lost to contact --> G[Escalate the stall - do not let it age in a queue; record the outreach attempts]
  D -- Still open --> H{Is which level of care / which clinician a clinical question?}
  H -- Yes --> I[Route the clinical appropriateness to a licensed clinician]
  H -- No, purely logistical --> J[Work the next contact step; keep tracking to a terminal state]
```

_Track every referral to a terminal state (scheduled / declined / lost-to-contact). Which level of care or which clinician is clinically appropriate routes to a clinician; the loop-tracking is operational._

---

## Reference map (2026, `[verify-at-build]`)

> **Not clinical, billing-final, or legal advice.** Every code, format, and rule below is a starting reference to confirm against the current CPT code set, the specific payer's policy, and current regulation before use.

### The intake → treatment-plan → note → claim flow (medical-necessity thread)

| Stage | Owner here | Carries forward |
|---|---|---|
| Intake + screening | `practice-operations-lead` (clinical screen → clinician) | Presenting problem, coverage, consent on file `[verify-at-build]` |
| Treatment plan | `clinical-documentation-specialist` (structure; clinician authors) | Diagnosis, functional impairment, goals, interventions `[verify-at-build]` |
| Progress note | `clinical-documentation-specialist` (structure; clinician authors) | Same dx + impairment, intervention delivered, client response `[verify-at-build]` |
| Claim | `billing-and-authorization-lead` | Same dx, CPT reflecting the service, auth units, medical necessity `[verify-at-build]` |

_The same diagnosis, the same functional impairment, and a consistent plan must thread all four stages. A claim whose necessity story diverges from the note is a denial and an audit risk._

### Progress-note formats (structure only)

| Format | Sections | Notes |
|---|---|---|
| DAP | Data, Assessment, Plan | Common in behavioral health; concise `[verify-at-build]` |
| SOAP | Subjective, Objective, Assessment, Plan | Widely used across medical + behavioral `[verify-at-build]` |
| BIRP | Behavior, Intervention, Response, Plan | Intervention/response-focused; strong for medical necessity `[verify-at-build]` |

_Pick one standard and apply it consistently; contemporaneous, behavioral, factual. The clinician authors the content — the standard governs the structure._

### Behavioral CPT codes (confirm against current code set + payer policy)

| Code (reference) | Service (reference) | Selection driver |
|---|---|---|
| 90791 | Psychiatric diagnostic evaluation (no medical services) | Intake/eval `[verify-at-build]` |
| 90832 / 90834 / 90837 | Individual psychotherapy — 30 / 45 / 60 min (time-based) | Documented face-to-face time `[verify-at-build]` |
| 90846 / 90847 | Family psychotherapy — without / with client present | Who is present `[verify-at-build]` |
| 90853 | Group psychotherapy | Group modality `[verify-at-build]` |
| Telehealth modifiers / POS | Service-delivery modifier + place of service | Payer + current telehealth policy `[verify-at-build]` |

_Time and modality determine the code; the documentation must support the time. Never upcode — the code reflects the service rendered. Confirm every code and modifier against the current CPT set and the specific payer's policy before quoting._

### 42 CFR Part 2 vs HIPAA (basics)

| Dimension | HIPAA | 42 CFR Part 2 |
|---|---|---|
| Covers | PHI generally | SUD records from a Part 2 program `[verify-at-build]` |
| Disclosure to payer | Permitted for treatment/payment/operations (within minimum necessary) | Generally needs specific written consent `[verify-at-build]` |
| Consent specificity | Authorization may be broader | Specific recipient + purpose; redisclosure prohibition `[verify-at-build]` |
| Default when unsure | — | Assume Part 2 applies; require specific consent `[verify-at-build]` |

_When in doubt whether a record is Part 2-covered, treat it as covered. This map is a basics reference — confirm against current regulation and route any legal question to counsel and any clinical-content question to a licensed clinician._

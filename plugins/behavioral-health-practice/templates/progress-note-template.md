# Progress Note — Template

> Output of `clinical-documentation-specialist` / the `clinical-documentation` skill. **Structure only — a licensed
> clinician authors all clinical content.** PHI placeholdered throughout; real client data lives in the EHR, never here.
> Pick ONE format (DAP / SOAP / BIRP) and apply it consistently. The note is a legal record: contemporaneous,
> behavioral, factual.

## Header (placeholdered)

| Field | Value |
|---|---|
| Client | `[Client]` |
| DOB | `[DOB]` |
| MRN | `[MRN]` |
| Date / time of service | `[YYYY-MM-DD HH:MM]` |
| Clinician | `[Clinician, credential]` |
| Service / CPT (`[verify-at-build]`) | `[CPT]` — confirm time/modality supports it |
| Diagnosis | `[Dx / ICD]` (clinician-authored) |

## Note body — choose one format

### DAP
- **Data:** `[observable behavior, client report, mental-status data — clinician]`
- **Assessment:** `[clinical assessment / progress toward goals — clinician]`
- **Plan:** `[next steps, interventions, follow-up — clinician]`

### SOAP
- **Subjective:** `[client's reported experience — clinician]`
- **Objective:** `[observed/measured data — clinician]`
- **Assessment:** `[clinical assessment — clinician]`
- **Plan:** `[plan — clinician]`

### BIRP
- **Behavior:** `[presenting behavior / client statements — clinician]`
- **Intervention:** `[intervention delivered this session — clinician]`
- **Response:** `[client response to intervention — clinician]`
- **Plan:** `[plan — clinician]`

## Medical-necessity thread (structural check — must be consistent with the claim)

| Element | Present? | Note |
|---|---|---|
| Diagnosis matches the treatment plan + claim | ☐ | same `[Dx]` across plan/note/claim |
| Functional impairment documented | ☐ | what the condition impairs, concretely |
| Intervention delivered (not just planned) | ☐ | the service actually rendered |
| Client response to intervention | ☐ | shows necessity; "medically necessary" is not a label |
| Plan / next steps | ☐ | continuity of care |

_If any box is unchecked, the note may not support the billed code — fix the structure (or the code via `billing-and-authorization-lead`); never stretch the code to fit. Audit findings here are structural, not clinical judgments._

## Disclosure note (if records leave the practice)

- ROI on file for this recipient + purpose? ☐ (consent precedes disclosure)
- SUD / 42 CFR Part 2 content? → specific Part 2 consent required (a general HIPAA authorization is not enough) ☐
- Disclose minimum necessary only ☐

---

```
Status: ...
Files changed: ...
Not clinical advice: structure/standards only; clinical content authored by [Clinician]
PHI posture: no real PHI — placeholders only; Part 2 consideration: ...
Medical-necessity / consent thread: ...
Handoff: ...
Open questions: ...
Grounding checks performed: ...
```

# Prior-Authorization Request — Checklist

> Output of `billing-and-authorization-lead` / the `prior-auth-and-claims` skill. PHI placeholdered — real member data
> stays in the billing system. Every code is `[verify-at-build]` against the current CPT set + the specific payer's
> policy. Never upcode. An auth is confirmed *in writing* before sessions are scheduled against it. **Not clinical or
> billing-final advice — confirm with the payer.**

## 1. Eligibility verification (do this first)

| Item | Confirmed? | Value (placeholdered) |
|---|---|---|
| Active coverage | ☐ | `[Plan]` |
| Behavioral-health benefit covered | ☐ | |
| In / out of network | ☐ | |
| Copay / coinsurance / deductible | ☐ | `[$]` |
| Session limits | ☐ | `[n / year]` |
| **Prior auth required for this service?** | ☐ | yes / no / **unknown → treat as required** |

_No scheduling against unconfirmed coverage. Member ID, name, DOB stay in the billing system: `[Member ID]`, `[Client]`, `[DOB]`._

## 2. CPT / code selection (the code reflects the service rendered)

| Service rendered | Candidate code (`[verify-at-build]`) | Selection driver |
|---|---|---|
| `[service]` | `[CPT]` | documented time / modality / who's present |
| Telehealth? | `[modifier / POS]` | payer + current telehealth policy |

_Never upcode. If documentation doesn't support the time/modality, the code drops — route the gap to `clinical-documentation-specialist`._

## 3. Prior-auth request packet

- ☐ Codes + unit count requested: `[CPT]` × `[units]`
- ☐ Diagnosis: `[Dx / ICD]`
- ☐ Medical-necessity attachment (impairment → intervention → response, from the note)
- ☐ Requesting clinician + NPI: `[Clinician / NPI]`
- ☐ **42 CFR Part 2:** if SUD content is disclosed to the payer → specific Part 2 consent on file (a general HIPAA authorization is not enough)

## 4. Verify-before-scheduling gate

- ☐ Auth **APPROVED in writing**
- ☐ Auth number captured: `[Auth #]`
- ☐ Approved unit count captured: `[units]`
- ☐ Schedule WITHIN approved units; re-auth before they run out

_Pending / verbal-only auth → do NOT schedule against it. An assumed auth is a denied claim._

## 5. If denied — triage by cause (the cause picks the fix)

| Cause | Fix | Route |
|---|---|---|
| Eligibility / auth | re-verify, obtain/confirm auth | here |
| Code / diagnosis mismatch | correct code or dx alignment | here + clinical-documentation-specialist |
| Medical-necessity documentation | strengthen the note's necessity thread | clinical-documentation-specialist |
| Timely filing | confirm filing window | here |
| Pattern across many claims | denial analytics / payer-contract modeling | medical-revenue-cycle |

---

```
Status: ...
Files changed: ...
Not clinical advice: operational billing support only; clinical questions routed to a clinician
PHI posture: no real PHI — placeholders only; Part 2 consideration: ...
Medical-necessity / consent thread: ...
Handoff: ...
Open questions: ...
Grounding checks performed: ...
```

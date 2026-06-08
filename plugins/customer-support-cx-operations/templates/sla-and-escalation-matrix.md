# SLA and Escalation Matrix — [Team / Product Name]

**Version:** [e.g., v1.0]
**Effective date:** [YYYY-MM-DD]
**Owner:** [Support ops lead name / role]
**Channels covered:** [e.g., Chat, Email, Voice, Self-service]
**Staffing model basis:** [Erlang C — see scripts/cx_calc.py; model date: YYYY-MM-DD]

---

## Part 1 — SLA Commitments by Channel

> Every SLA target in this table must be backed by an Erlang C model at the stated contact volume
> and AHT. Do not publish an SLA without a staffing model. See `contact-center-workforce-analyst`.

| Channel | Segment | SLA Target | First Response | Resolution | Abandonment Target | Staffing Basis |
| --- | --- | --- | --- | --- | --- | --- |
| Live Chat | All | [e.g., 80% answered within 20s] | [e.g., <20s] | [e.g., same-session or <4h async] | ≤2% | [e.g., Erlang C: N agents at X vol/hr, Y AHT] |
| Email | Standard | [e.g., 100% first reply within 4h business hours] | [e.g., 4h] | [e.g., 24h business] | ≤1% past SLA | [e.g., interval model: N agents, X AHT] |
| Phone / Voice | Priority | [e.g., 80% answered within 30s] | [e.g., <30s] | [e.g., same-call or same-day callback] | ≤5% | [e.g., Erlang C: N agents at X vol/hr, Y AHT] |
| Self-service | All | [e.g., 24/7 availability; bot handoff <30s] | N/A | [e.g., bot or escalation SLA applies] | N/A | [Bot uptime SLA from vendor] |

**Note:** SLA targets are business-hours unless explicitly marked "24/7." Staffing basis column must
reference the Erlang C model date and inputs so the commitment can be re-validated when volume changes.

---

## Part 2 — Tier Definitions and Escalation Thresholds

| Tier | Handles | Resolution authority | Escalation trigger |
| --- | --- | --- | --- |
| **Tier 1** (front-line) | Common, scripted contacts: account access, order status, billing information, standard returns, password reset, FAQ-level product questions | Can apply standard resolution steps, use macros, issue standard refunds up to $[X] | Contact requires judgment not covered by macro; customer requests supervisor; issue requires system access above Tier 1 permissions; technical complexity; legal/safety flag |
| **Tier 2** (specialist / owner) | Complex contacts: billing disputes, account modifications, technical issues, escalated complaints, out-of-policy requests requiring approval | Can override standard policy within defined limits; access to [specific systems]; can issue refunds up to $[Y] | Requires engineering or product involvement; legal/regulatory content; Tier 2 resolution exceeded; customer threat or legal mention |
| **Tier 3** (engineering / specialist) | Product defects, data issues, security concerns, regulatory/legal matters | Full system access; can escalate to product/legal/security; can issue full refunds or credits | Escalation is final; route to legal/security if applicable |
| **Supervisor / Manager** | Escalated complaints, service recovery, VIP customers, threatening or abusive contacts | Full override; authority to offer service recovery above standard | Route through Tier 2; do not bypass tiers without documented reason |

---

## Part 3 — Escalation Reason Code Taxonomy

> Every escalation from Tier 1 → Tier 2 and Tier 2 → Tier 3 **must** include a reason code.
> An escalation without a reason code is unauditable and unimprovable.

| Code | Label | Definition |
| --- | --- | --- |
| `COMP` | Complexity | Issue requires knowledge or system access beyond this tier's authority |
| `POLICY` | Policy exception | Customer requests a deviation from standard policy |
| `TECH` | Technical / engineering | Product defect, data error, or system behavior outside support authority |
| `LEGAL` | Legal / regulatory | Customer mentions legal action, regulatory complaint, or personal data request (DSAR/CCPA) |
| `SAFETY` | Safety / wellbeing | Contact involves risk to customer or third-party safety |
| `ABUSE` | Abusive contact | Threatening or abusive language; contact de-escalation not successful |
| `VIP` | VIP / account-level flag | Account flagged for elevated handling by account management or CS |
| `REQ` | Customer request | Customer explicitly requested escalation; Tier 1 resolution offered and declined |
| `OTHER` | Other | Required only when none of above apply; mandatory free-text notes |

**Analysis cadence:** Review escalation reason-code distribution weekly. If `COMP` > 30% of Tier 1
escalations, investigate whether the KB, macros, or Tier 1 training are the root cause.

---

## Part 4 — Handoff Protocol

When escalating between tiers:

1. **Document in the ticket:** summary of issue, resolution steps already attempted, reason code,
   any customer communication already sent.
2. **Warm transfer (for voice/live channels):** introduce the receiving tier to the customer before
   dropping. Do not cold-transfer.
3. **SLA clock:** does the receiving tier's SLA clock reset on escalation or continue? [Specify here.]
4. **Context package:** receiving agent must be able to resolve without asking the customer to
   repeat already-provided information.

---

## Change Log

| Version | Date | Changed by | What changed |
| --- | --- | --- | --- |
| v1.0 | [YYYY-MM-DD] | [Name] | Initial SLA and escalation matrix |

---

_Generated by `customer-support-cx-operations / cx-ops-lead`. Re-validate SLA commitments against
the Erlang C model whenever contact volume changes by more than 20% or AHT changes by more than 30s._

# Cross-functional partnership map — `<partner_name | vendor_name>`

> **What this is.** A fillable matrix the PSM maintains for their own vendor — *which internal team owns which question, when to engage them, and when the PSM takes the work back.* The artifact most PSMs need but rarely have written down; without it, escalations get routed by hallway-memory and the wrong team gets pulled in at the wrong moment.
>
> **When to fill it in.** At PSM start (first 30 days, alongside the partner profile) and again on any major org change inside the vendor (re-org, new VP of Engineering, support tooling change, RACI refresh).
>
> **When to refresh.** Quarterly — and immediately on any of: a re-org inside the vendor; a major support-tooling change (Zendesk → Salesforce Service Cloud, etc.); a change in who runs onboarding/implementation; a new product line that adds a new internal owner.
>
> **Segment note.** The columns below are segment-agnostic — K-12 / higher-ed / corporate L&D PSMs all need this map. The example rows are K-12-flavored; adjust for your segment.

---

## Header (about this PSM book)

- **PSM owner:** `<name>`
- **Region / territory:** `<West Coast | East Coast | National | named-states>`
- **Last refreshed:** `<YYYY-MM-DD>`
- **Major-change triggers since last refresh:** `<re-org / tooling / new-product / none>`

---

## The matrix

Fill one row per internal function. Add or remove rows for your vendor; the column shape is what matters.

| Function | Owner (name + role) | When to engage (trigger) | What the PSM hands over | Hand-back criterion (PSM takes it back when…) | Escalation path (above this owner) |
|---|---|---|---|---|---|
| **Product** | `<name, role>` | Partner-stated feature gap that's blocking adoption; roadmap question from partner; recurring pain across ≥3 partners | Partner quote + use case + which signals are at risk if the gap persists (adoption, renewal) | Product has acknowledged in writing OR partner has accepted "won't fix" framing | VP Product → CPO |
| **Engineering** | `<name, role>` | Bug confirmed; partner-impacting outage or degradation; rostering sync failure that's not a config issue | Repro steps + partner impact + log excerpts (scrubbed of student PII) | Eng has acknowledged + ETA OR has classified as "won't fix" | Eng manager → VP Eng |
| **Support** | `<name, role>` | Any user-reported issue (not partner-strategic question) — login, sync, training-tier; ticket aging past school-hours SLA | Ticket ID + partner context (who's escalating, what's at stake) + any prior PSM commitment that affects priority | Ticket resolved OR moved to Eng/Product OR partner accepts current state | Support manager → VP Support |
| **Sales / Account Executive** | `<name, role>` | Renewal kickoff (per the 120-180 day K-12 clock in [`../knowledge/renewal-pricing-conversations-edtech.md`](../knowledge/renewal-pricing-conversations-edtech.md)); expansion opportunity surfaced by adoption depth; partner-side champion change that affects buying motion | Health-score snapshot + adoption signals + expansion signals + risks | Contract signed OR expansion deal closed OR loss reasons documented | Sales manager → CRO |
| **Operations / Customer Operations** | `<name, role>` | Implementation/rostering setup needs platform-side config (provisioning, SSO, district tenant setup); license counts / seat changes | Partner config requirements + go-live date + any state-privacy / FERPA addendum needed | Implementation milestones met OR go-live achieved | Ops manager → COO / Head of Operations |
| **Implementation team** | `<name, role>` | New partner kickoff; major product expansion requiring re-implementation; partner has restructured (new district consolidation, new SIS, new LMS) | Partner success plan + technical context + named champion + segment-calendar dead zones to avoid | Implementation milestones met + first 30/60/90 outcomes documented | Implementation lead → VP CS or VP Operations |
| **Compliance / Legal** | `<name, role>` | State-specific data-protection rider re-attachment at renewal (NY Ed Law §2-d, IL SOPPA, CA SOPIPA — see [`../knowledge/parent-comms-jurisdictional-bear-traps.md`](../knowledge/parent-comms-jurisdictional-bear-traps.md)); breach response; sub-processor disclosure; AI-feature COPPA review (post April 22 2026 full enforcement) | Specific regulation triggered + partner contact + timeline + PSM-side risk assessment | Rider attached + partner sign-off OR breach response complete + post-mortem filed | GC → CISO (if security adjacent) |
| **Marketing / Demand** | `<name, role>` | Reference-customer requests (avoid bottom-quartile partners); case study; testimonial; advocacy program enrollment | Vetted partner list (only top-quartile health + advocacy-willing); preferred channels; quotes the partner already approved | Asset published OR partner declines OR PSM determines partner shouldn't be public-facing | Marketing manager → CMO |
| `<add row>` | | | | | |

---

## Anti-patterns this map prevents

- **PSM as inbox** — without the map, the PSM becomes the dumping ground for every partner question that isn't obviously someone else's. The map externalizes the routing.
- **Support → PSM bounce-back** — a partner DMs the PSM about a ticket the PSM already routed; without a hand-back criterion, the PSM gets re-pulled in and the support function never owns end-to-end.
- **Sales-driven renewal expansion** — renewal motion crosses CS and Sales boundaries. Without the map's "What the PSM hands over" column, the expansion conversation lacks the health-score + adoption-signals context Sales needs to size the ask correctly.
- **Reference-customer over-asks** — Marketing pings the PSM for "any partner who'd be on a case study"; without the map, the PSM defaults to the loudest champion (often not the best fit) instead of the top-quartile vetted list.

## References (existing plugin artifacts)

- [`../agents/edtech-partner-success-manager.md`](../agents/edtech-partner-success-manager.md) — the PSM agent that *uses* this map in routing decisions
- [`../templates/escalation-memo.md`](../templates/escalation-memo.md) — the artifact when escalation moves past the per-function owner above
- [`../knowledge/k12-psm-operating-cadence.md`](../knowledge/k12-psm-operating-cadence.md) — *when* in the week / quarter / school year these handoffs typically fire
- [`../knowledge/parent-comms-jurisdictional-bear-traps.md`](../knowledge/parent-comms-jurisdictional-bear-traps.md) — the compliance-triggers row's source-of-truth
- [`../knowledge/renewal-pricing-conversations-edtech.md`](../knowledge/renewal-pricing-conversations-edtech.md) — the renewal-clock context for the Sales row

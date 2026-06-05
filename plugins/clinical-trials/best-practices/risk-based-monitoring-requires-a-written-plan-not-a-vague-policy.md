# Risk-Based Monitoring Requires a Written Plan, Not a Vague Policy

**Status:** Absolute rule
**Domain:** Site monitoring / clinical operations
**Applies to:** `clinical-trials`

---

## Why this exists

FDA (2013 RBM Guidance) and ICH E6(R3) both require that risk-based monitoring be implemented through a documented, protocol-specific monitoring plan — not a generic SOA statement that "we use risk-based approaches." Inspectors look for the risk assessment, the centralized monitoring triggers, the on-site visit triggers, and the escalation pathway written down before monitoring begins. A sponsor that performs RBM without a written plan may have done the right operational work and still receive a Form 483 observation for the missing documentation.

## How to apply

Produce a Monitoring Plan document for every IND-covered study before first patient first visit.

```
Monitoring Plan required sections:
1. Risk Assessment Summary
   - Protocol-specific critical data and critical processes identified
   - Risk matrix: likelihood × impact for each identified risk
   - Monitoring strategy per risk tier (central-only / triggered on-site / routine on-site)

2. Central Monitoring Activities
   - Data metrics tracked centrally (e.g., enrollment rate, query rate, AE pattern, SDV flags)
   - Statistical outlier detection triggers (e.g., z-score threshold for site-level AE rate)
   - Frequency of central review: at minimum monthly for enrolling studies

3. On-Site Monitoring
   - Site visit trigger thresholds (e.g., >3 critical queries, consent deviation, SAE documentation issue)
   - SDV/SDR extent and sampling approach per site tier
   - Post-visit letter turnaround requirement (standard: ≤5 business days)

4. Escalation and Issue Management
   - Trigger for Protocol Deviation Report vs. CAPA requirement
   - Trigger for site suspension vs. site closure
   - Communication path: CRA → CRA Manager → Medical Monitor → Sponsor Quality

5. Revision History
   - Version controlled; update triggered by protocol amendment or aggregate finding
```

**Do:**
- Write the monitoring plan before first patient first visit, not after the first monitoring visit has occurred.
- Link the monitoring plan to the site performance tier system so tier changes automatically adjust monitoring intensity.
- Retain version-controlled monitoring plans in the Trial Master File for the duration of the trial plus the required retention period.

**Don't:**
- Use a template monitoring plan verbatim without protocol-specific risk customization.
- Confuse the monitoring plan with the monitoring report — these are different documents with different audiences.
- Allow central monitoring to run without documented triggers and response actions — undocumented central monitoring findings are unactionable.

## Edge cases / when the rule does NOT apply

Phase I dose-escalation studies conducted entirely at a single investigator site with 100% SDV may not require a formal RBM central monitoring component, but still require a written monitoring plan.

## See also

- [`../agents/clinical-operations-manager.md`](../agents/clinical-operations-manager.md) — owns monitoring plan authoring and execution.
- [`./site-performance-tiers-concentrate-monitoring-resources.md`](./site-performance-tiers-concentrate-monitoring-resources.md) — tier assignment is an input to the monitoring plan's on-site frequency logic.

## Provenance

Grounded in FDA Guidance for Industry: Oversight of Clinical Investigations — A Risk-Based Approach to Monitoring (2013); ICH E6(R3) Good Clinical Practice §5.18; TransCelerate BioPharma RBM methodology framework.

---

_Last reviewed: 2026-06-05 by `claude`_

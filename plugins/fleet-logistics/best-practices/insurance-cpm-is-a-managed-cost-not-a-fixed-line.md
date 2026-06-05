# Insurance CPM Is a Managed Cost, Not a Fixed Line

**Status:** Pattern
**Domain:** Fleet cost management
**Applies to:** `fleet-logistics`

---

## Why this exists

Fleet insurance is treated in most carrier models as a fixed overhead line — a premium paid once a year, divided by miles, and left alone. It is not fixed: it responds directly to safety record (CSA scores, DOT inspection results, at-fault accidents), fleet age, driver tenure mix, and coverage architecture. A carrier that manages safety and driver quality as operational disciplines — rather than as compliance obligations — consistently pays less per mile for coverage. Carriers who treat insurance as a market exercise and ignore the underlying loss history are paying for their past in every renewal.

## How to apply

Build the insurance CPM management model:

```
Insurance CPM analysis:
  Annual premium (all lines — liability, cargo, physical damage, umbrella): $______
  Annual miles driven (fleet):                                               ______
  Insurance CPM:                                                             $______/mile
  Industry benchmark range: $0.06–$0.12/mile [unverified — training knowledge]

  Loss ratio (trailing 36 months):
    Total claims paid / Total premium = ______%
    Target: < 60% (above 60% signals a renewal premium spike)

  CSA score impact review:
    Unsafe Driving: ______   Hours of Service: ______   Vehicle Maintenance: ______
    Alert thresholds: >65 in any BASICs triggers underwriter scrutiny

  Driver risk factors:
    % drivers with < 1 year tenure: ______% (higher = higher premium)
    % drivers with MVR violations (trailing 36 months): ______%
```

Controllable levers ranked by impact:
1. **Safety record** (CSA scores, preventable accidents) — the largest single underwriting factor.
2. **Driver tenure and screening** — new CDL holders and MVR-flagged drivers carry premium loadings.
3. **Fleet age** — newer equipment reduces physical-damage rates.
4. **Coverage architecture** — increasing deductibles on physical damage (self-insuring the smaller losses) often reduces total premium by more than the expected self-insured loss.

**Do:**
- Review CSA scores monthly and treat BASICs improvements as an insurance-cost lever, not just a compliance obligation.
- Run annual coverage audits — review deductible levels, excess layers, and whether any coverage is duplicated.
- Present the loss ratio to the underwriter at renewal; a favorable ratio is a negotiating lever most carriers leave unused.

**Don't:**
- Accept a renewal premium increase without providing loss-run history, CSA improvement data, and driver quality evidence — underwriters price on available information.
- Treat cargo insurance as a one-size-fits-all coverage — the limit and deductible should match the actual commodity values on the lanes, not a generic template.

## Edge cases / when the rule does NOT apply

Owner-operators working under a carrier's authority (leased-on) are typically covered under the carrier's umbrella — their individual insurance management is limited. Fleets under captive or self-insurance programs have a different leverage structure; the loss-ratio discipline still applies but the negotiation mechanic does not.

## See also

- [`../agents/fleet-engagement-lead.md`](../agents/fleet-engagement-lead.md) — scopes insurance as part of the full fixed-cost read.
- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns the insurance CPM calculation and benchmark comparison.
- [`./fixed-vs-variable-cpm-split-before-any-cost-reduction-action.md`](./fixed-vs-variable-cpm-split-before-any-cost-reduction-action.md) — insurance sits in the fixed pool; the split is the diagnostic entry point.

## Provenance

Synthesized from standard fleet insurance management practice and carrier risk management consulting; CSA score-to-premium linkage is well documented by insurance carriers specializing in transportation risk.

---

_Last reviewed: 2026-06-05 by `claude`_

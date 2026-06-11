# DevRel metrics & ROI — reference

Deep reference for the `devrel-lead`, `devrel-programs-and-operations-manager`, and the measurement
skill. Companion to [`devrel-decision-trees.md`](devrel-decision-trees.md).

---

## The two-column scorecard

Every DevRel scorecard has exactly two columns. An input may appear **only** when paired with the
outcome it drives.

| Outcome metric (lead with these) | Vanity input (paired or cut) |
|---|---|
| Activation rate | sign-ups, sessions |
| Time-to-first-value (median, p90) | quickstart pageviews |
| Production adoption | GitHub stars |
| Expansion / retained adoption | followers, subscribers |
| Cost-per-activation | impressions, reach |
| Self-answer ratio (community) | member count |
| Contributor conversion | event attendees |

## Metric definitions

- **Activation rate** = `first_success ÷ sign_ups`.
- **TTFV** = median (and p90) wall-clock `sign_up → first_success`.
- **Funnel conversion** = stage-to-stage rates across the activation funnel.
- **Content ROI** = activations attributable ÷ content effort (hours).
- **Cost-per-activation** = program spend ÷ activations attributable.
- **Community health** = active ratio, answer rate, contributor conversion.

Compute all of these with [`../scripts/devrel_calc.py`](../scripts/devrel_calc.py).

## Program ROI — activations per dollar

Rank every program (event, sponsorship, content series, ambassador tier) by **expected activations
per dollar**:

```
activations_per_dollar = (audience_fit × activation_path_strength × expected_reach) / cost
```

A program with high reach and no activation path scores near zero regardless of cost. A flagship
event "the team always does" gets the same scrutiny as a new bet.

## Reporting cadence (decisions, not status)

| Cadence | Surfaces | Triggers |
|---|---|---|
| Weekly | funnel conversion, answer rate, TTFV trend | onboarding investigation, community staffing |
| Monthly | activation rate, content ROI, cost-per-activation | content/channel reallocation |
| Quarterly | adoption, program ROI, scorecard vs. plan | program portfolio + headcount decisions |

A review that triggers no decision is cut.

## The exec narrative

Connect activities → leading metrics → adoption/pipeline influence in the exec's language. Lead with
activation and adoption; never open with stars or headcount. The strongest line DevRel can deliver to
an exec is a **cost-per-activation** trending down while **adoption** trends up — that is DevRel
paying for itself.

## Attribution honesty

Developer attribution is imperfect (developers research anonymously, share links, find you via
search). Where the path can't be fully traced, **state the assumption** rather than over-claim. An
honest "influenced" number with its method beats a precise-looking number built on a guess — this is
the Claim-Grounding protocol applied to metrics.

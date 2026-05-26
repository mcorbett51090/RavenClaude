# Statistical report — <question / analysis name>

> The deliverable write-up. Lead with the plain-language answer; back it with the
> method, the effect size + CI, the assumptions checked, and the honest caveats.

**Author:** <name> · **Date:** <YYYY-MM-DD> · **Data window:** <start – end> · **n:** <…>

## Bottom line (plain language)
<One or two sentences a non-statistician can act on. e.g. "Variant B lifts conversion
by ~1.5 percentage points (from 5.0% to 6.5%); we're confident the lift is real and
large enough to ship.">

## Question
<What was asked, and what decision it informs.>

## Method
- **Test / model:** <from the decision tree> · **why:** <data type / #groups / paired?>
- **Tooling:** <scipy.stats / statsmodels / pingouin …>
- **Assumptions checked:** <normality / equal variance / independence — result of each>

## Result
- **Effect size + 95% CI:** <the headline — magnitude with uncertainty>
- **p-value:** <p> (secondary to the effect size)
- **Guardrails (if an experiment):** <each metric: movement + CI; pass/fail>
- **Multiple-comparison correction:** <method, across # tests> (if applicable)

## Caveats & assumptions
- <Assumption violations and how handled; sample-size/power limits; correlation-not-causation
  if a coefficient is involved; any pitfall exposure from statistical-pitfalls.md.>

## Recommendation
<Ship / don't ship / gather more data / run a follow-up. Tie it back to the MDE and the
business decision.>

## Reproducibility
- **Code / notebook:** <path> · **Data source + query:** <where the numbers came from>

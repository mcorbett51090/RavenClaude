---
description: Review a DevRel program against the developer funnel — locate the weakest stage (awareness/activation/habit/advocacy) by its leading indicator, flag any vanity metrics masquerading as success, and return ranked, lowest-effort-first interventions tied to the leak with honest attribution.
argument-hint: "[the program/metrics to review, e.g. 'our DevRel dashboard and last quarter's numbers']"
---

# Review the DevRel funnel

You are running `/developer-relations:devrel-funnel-review`. Review the program/metrics the user
described (`$ARGUMENTS`) following this plugin's `devrel-lead` discipline, the `devrel-strategy`
and `devrel-metrics` skills, and the [`../knowledge/developer-funnel-decision-tree.md`](../knowledge/developer-funnel-decision-tree.md).

## When to use this

Quarterly/annual DevRel planning, a "what should the team work on next" question, or a dashboard
that's all impressions/stars/followers.

## Steps

1. **Map the funnel to the product.** Confirm what "first core action" (the activation event)
   concretely means. Without it, the funnel is abstract.
2. **Audit the metrics for vanity.** For each metric, ask: does it map to awareness, activation,
   habit, or advocacy? If not, it's *reach* — reframe it as the outcome it should be (see the
   reframe table in `devrel-metrics`). Flag any vanity input being reported as a success criterion.
3. **Locate the weakest stage** by its leading indicator (quickstart completion, TTFS,
   first-response time, retention). The weakest *stage*, not the loudest channel, selects the work.
4. **Pick lowest-effort interventions first** by traversing the decision tree — e.g. if activation
   is the leak, audit the quickstart before commissioning new content.
5. **Define the success metric** for each intervention (with an owner + source) and an **honest
   attribution note** — name the dark funnel rather than inventing a number.

## Output

Lead with the funnel diagnosis (weakest stage + the indicator that says so) and any vanity metrics
flagged, then **ranked interventions** (lowest-effort-first, routed to the right agent:
`docs-and-samples-engineer` / `community-manager` / `developer-advocate`), then the metric
definitions. Cite the source/date of any quantitative claim or mark it `[unverified]`.

# Knowledge: the developer-funnel decision tree

How `devrel-lead` decides **where to invest** given a funnel. Traverse top-to-bottom; the
weakest *stage* selects the work, and within a stage you pick the lowest-effort intervention
before recommending net-new programs.

## The funnel

```
Awareness  →  Activation  →  Habit  →  Advocacy
```

## Decision Tree

### 1. Is awareness the weak stage?

Signal: low content reach / search impressions / referral traffic relative to your market;
few new sign-ups or repo visits.

- **First, cheapest:** repurpose existing anchor content into more surfaces (see
  `developer-content-pipeline`) before commissioning new content.
- Then: SEO/discoverability of the docs + quickstart; guest posts; conference CFPs.
- ⚠️ **Do not** pour awareness spend on top of a broken activation step — you'll fill a leaky
  bucket faster. Check stage 2 first if activation conversion is unknown.

### 2. Is activation the weak stage? (the most common real leak)

Signal: sign-ups are fine but few reach the first core action; low quickstart completion;
high time-to-first-success.

- **First, cheapest:** audit the quickstart with a timer (see `quickstart-authoring`). Cut
  prerequisites, fix copy-paste failures, declare a TTFS target. This is usually the single
  highest-leverage DevRel investment.
- Then: a hosted try-it / sandbox key to remove setup cliffs; CI-test the quickstart so it
  stops rotting; targeted sample apps for the top use cases.
- Route to `docs-and-samples-engineer`.

### 3. Is habit the weak stage?

Signal: developers activate but don't return; low 30/90-day retention; low weekly-active.

- **First, cheapest:** improve community first-response time (see `community-health`) — fast
  answers keep people from churning when they hit a wall.
- Then: deepen content (advanced patterns, "what's next after hello-world"); changelog/release
  cadence that gives reasons to return; lifecycle nudges (coordinate with `marketing-operations`).
- Route to `community-manager` (+ `developer-advocate` for habit content).

### 4. Is advocacy the weak stage?

Signal: retained developers exist but few contribute, answer others, or refer.

- **First, cheapest:** curate good-first-issues with real context + offer first-contribution
  mentorship (see `community-health`). Build the contributor ladder's bottom rungs.
- Then: an ambassador/champions program; recognition systems; community spotlights.
- Route to `community-manager`.

## After picking the stage

1. Confirm the leading indicator at that stage is actually the bottleneck (don't guess).
2. Pick the lowest-effort intervention listed above before any net-new program.
3. Define the metric that will tell you it worked (see `devrel-metrics`) — with an owner + source.
4. Re-locate on the funnel next cycle; the leak moves as you fix it.

## Cross-references

- `devrel-strategy` — defining the funnel + north-star.
- `devrel-metrics` — the vanity-metric ban + honest attribution.
- `quickstart-authoring`, `developer-content-pipeline`, `community-health` — the interventions.

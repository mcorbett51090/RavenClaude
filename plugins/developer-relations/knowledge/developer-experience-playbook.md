# Developer-experience playbook

The end-to-end arc DevRel runs: get a developer from awareness to a retained,
productive user, and feed what you learn back into the product.

## The activation funnel (what DevRel measures)

DevRel success is **activation and retention**, not reach. The funnel:

1. **Aware** → heard about the product.
2. **Signed up** → has credentials / an API key.
3. **First call** → made one successful API call.
4. **First app** → built something real that works (the **first-success** moment).
5. **Retained** → came back and used it again the next week/month.

The north-star is **time-to-first-success (TTFS)**: how long from signup to a real
result. Most developers decide in the first ten minutes; TTFS is the number to
shrink. MQLs, followers, and impressions are *not* on this funnel — that's
`marketing-operations`.

## Stage 1 — Audit the getting-started path (developer-advocate)

- Walk it yourself from a clean state; **time** it. Record every friction point and
  where developers drop off.
- For each friction point, make a **fix-or-document** call (tree 2 in
  [`devrel-engagement-decision-trees.md`](devrel-engagement-decision-trees.md)): is
  the product painful (file a bug) or just undiscoverable (write content)?

Artifact: [`../templates/getting-started-audit.md`](../templates/getting-started-audit.md).

## Stage 2 — Build runnable artifacts (devrel-content-engineer)

- The getting-started path anchors on one early **first-success milestone**.
- Sample apps demonstrate the **real value path**, including the hard parts — not a
  toy. Spec: [`../templates/sample-app-spec.md`](../templates/sample-app-spec.md).
- **Sample code is production code:** it runs from a clean checkout, handles errors,
  pins versions, and has **no hardcoded secrets**. A copied-verbatim insecure
  sample teaches a vulnerability at scale.

## Stage 3 — Content & reach (developer-advocate)

- Choose the **format from the activation goal** (tree 3), not the trendy channel.
- Speak **engineer-to-engineer**. A developer audience smells marketing speak and
  loses trust permanently when it does.
- Plan with a calendar tied to activation goals:
  [`../templates/devrel-content-calendar.md`](../templates/devrel-content-calendar.md).

## Stage 4 — Community (developer-community-manager)

- Health = **answered-question rate + returning contributors**, not member count.
- Design triage/response SLAs so no question rots; capture canonical answers back
  into docs/samples.
- Grow contributors on a ladder (user → answerer → contributor → ambassador).

Artifact: [`../templates/community-health-review.md`](../templates/community-health-review.md).

## Stage 5 — Close the feedback loop (developer-advocate)

- Theme developer pain across audits, community, and content; attach **frequency +
  severity**; rank by activation impact.
- Bring it to `product-management` as a
  [`product-feedback-brief`](../templates/product-feedback-brief.md) — evidence, not
  anecdotes. This is how DevRel earns its seat: by being the product's most
  credible source of developer truth.

## The four house rules, condensed

1. Time-to-first-success is the metric.
2. Fix the product before writing around it.
3. Sample code is production code.
4. DevRel is not demand gen — measure activation, not MQLs.

See [`../best-practices/README.md`](../best-practices/README.md) for the full
opinions and [`devrel-engagement-decision-trees.md`](devrel-engagement-decision-trees.md)
for the trees.

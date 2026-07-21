---
name: handle-cold-start-and-serving
description: "Handle cold-start (new users and new items) and serve recommendations within a latency budget — content/popularity fallbacks, onboarding & exploration, ANN retrieval, precompute/caching, online feature fetch, and popularity-on-timeout fallback. Use when new entities recommend poorly or serving is too slow."
---

# Skill: Handle Cold-Start and Serving

Two hard, related production problems: recommending for entities the model has never seen (**cold-start**), and returning good recommendations **fast enough** to serve online. This skill covers both because they share the same fallbacks.

## When to use

- New users or new items get poor/empty recommendations.
- Recommendation latency is too high to serve inline.
- Designing the serving path and its failure behavior.

## Cold-start steps

1. **Separate new-user from new-item.** They are different problems. New-user: no interaction history. New-item: no interactions received yet (the "item cold-start" that kills fresh-catalog products).
2. **Fall back to content + popularity.** Content-based features let a brand-new item be recommendable on day zero; popularity/trending is a safe new-user default.
3. **Harvest onboarding signals.** Explicit preferences at signup, early implicit clicks, and context (locale, device, referrer) bootstrap personalization fast.
4. **Explore deliberately.** New items need exposure to earn interactions; bake in an exploration budget (e.g. epsilon or bandit-style) so the feedback loop doesn't starve fresh catalog.
5. **Hand off to the personalized model as signal accrues** — define the threshold where an entity graduates from fallback to personalized.

## Serving steps

1. **Budget the latency across stages.** Retrieval + feature fetch + ranking must fit the SLA; allocate it explicitly. See [`../../knowledge/recsys-evaluation-and-serving.md`](../../knowledge/recsys-evaluation-and-serving.md).
2. **Use an ANN index for embedding retrieval** (FAISS / ScaNN / HNSW-class) rather than brute-force scoring the catalog.
3. **Precompute/cache where freshness allows** — batch-precomputed recommendations for stable users, real-time only where it earns its cost.
4. **Fetch features from an online store** with parity to training (train/serve skew is a top failure cause).
5. **Fall back to popularity on timeout or error — never serve a blank shelf or an exception.** The fallback is part of the design, not an afterthought.

## Anti-patterns

- Treating new-user and new-item as the same case.
- No exploration → fresh items never get exposure → they stay cold forever.
- Brute-force catalog scoring where an ANN index is needed.
- Real-time computing everything when precompute would meet freshness at a fraction of the latency.
- No fallback → a slow/failed model shows an empty or erroring recommendation surface.

## Output

A cold-start + serving design: new-user & new-item fallbacks → onboarding/exploration → graduation threshold → latency budget → retrieval/caching/feature-fetch path → popularity-on-timeout fallback. The architect sets the strategy; the engineer builds it.

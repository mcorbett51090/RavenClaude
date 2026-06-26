# Scenario: everyone buys the cheapest tier

**The ask:** "We have three plans but ~80% of new customers pick the cheapest, then
ask us to add features to it. Expansion is dead. Fix our packaging."

**Routes to:** `pricing-strategist` → `packaging-and-tiering`.

**The answer shape:**
1. Diagnose: the tiers are almost certainly **fenced by feature-count, not a
   self-selection dimension** — so customers rationally buy the cheap plan and lobby
   for features. The "add it to the cheap plan" requests are the tell.
2. Re-fence: pick a **self-selection dimension** (scale, use case, support, or
   security) so customers sort themselves. Move a key fence feature (e.g. SSO/admin,
   or a usage allowance) up to gate the upgrade.
3. **Design the middle to win** — make the Pro tier the intended default and fence so
   the target segment lands there; keep the bottom tier deliberately limited on the
   fence dimension, not crippled on features.
4. Separate the lobbied-for features into **add-ons** where they're long-tail.
5. Validate the new tier prices with `willingness-to-pay-research` (conjoint is ideal
   here — it tells you which feature belongs in which tier); mark prices provisional
   until then.
6. **Seams:** roadmap implications of moving features between tiers →
   `product-management`; revenue impact → `finance`.

**Why it's a good illustration:** the fix is fencing, not discounting or adding a
fourth tier — the most common packaging mistake.

# Developer onboarding audit — time-to-first-success drop-off map

> Walk the golden path as a hostile first-timer on a clean environment. Owned by `developer-advocate`
> / `devrel-strategist`. Date: <YYYY-MM-DD> · Product/path audited: <…>

## Golden path

- **First working result is defined as:** <the visible win — e.g. "first successful API call returns 200">
- **Stated prerequisites:** <runtime/version/account — and are they stated up front? yes/no>

## Step-by-step drop-off map

| # | Step (what the developer does) | Friction found | Fix | Leaks here? |
|---|---|---|---|---|
| 1 | <e.g. sign up> | <…> | <…> | <low/med/high> |
| 2 | <e.g. get API key> | <key page linked not shown> | <show the key inline> | high |
| 3 | <…> | <…> | <…> | <…> |
| … | <…> | <…> | <…> | <…> |

## The first dead end

- **Step #:** <n>
- **What happens:** <a reasonable developer gets stuck with no next move>
- **Fix (do this first — nothing downstream matters until it's fixed):** <…>

## Time-to-first-success

| | Steps to first success | Est. median wall-clock | Getting-started completion |
|---|---|---|---|
| **Before** | <n> | <…> | <…> |
| **After fixes** | <n'> | <…> | <…> |

## Defects flagged

- [ ] Placeholder secret / hard-coded key on the happy path? <where>
- [ ] `TODO` / "left as an exercise" on the golden path? <where>
- [ ] A snippet that doesn't run unmodified? <where>
- [ ] An error with no recovery path? <where>

## Recommendation

<the prioritized fix list, first dead end first, with the activation metric to re-measure after>

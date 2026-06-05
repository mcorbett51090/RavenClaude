# Online giving first-touch rate is the acquisition signal, not total digital revenue

**Status:** Pattern
**Domain:** Nonprofit digital fundraising
**Applies to:** `nonprofit-fundraising`

---

## Why this exists

When a development team reports "digital revenue up 15%," that number almost always includes existing donors who chose the online portal for convenience, not new donors acquired through digital channels. The meaningful signal for digital's contribution to growth is the first-touch rate: what percentage of new donors made their first gift online, and what is their subsequent retention and upgrade rate? Existing donors who switch payment channels are not digital-acquisition wins; they are channel-preference changes. Conflating the two overstates digital's acquisition impact and leads to over-investment in digital marketing that isn't actually growing the donor file.

## How to apply

Segment digital revenue by donor status at the time of the gift: first-time online vs. existing donor giving online. Track the first-time online rate and its cohort retention separately.

```
Digital channel analysis model:
  Metric 1: First-time online donors (quarter)
    = count of donors whose first-ever gift was via online channel
    Target: track cohort retention at 12 months → compare to non-digital first-time donors

  Metric 2: Existing donors giving online
    = online gifts from donors with a prior gift via any channel
    → this is a channel-preference shift, not acquisition

  Metric 3: Online-first cohort LTV
    = average cumulative gifts from donors who first gave online, by cohort year
    → compare to mail-first or event-first cohort LTV

Reporting rule: always split digital revenue by first-time vs. existing in the development scorecard.
If first-time online donors have retention below 30% at 12 months, the digital acquisition strategy needs revision.
```

**Do:**
- Build a "donor source of first gift" field in the CRM and maintain it over the donor lifecycle.
- Separate first-time online acquisition in the development scorecard from existing-donor online payment.
- Track first-time online donor retention at 12 months alongside the acquisition count.

**Don't:**
- Count an existing donor's switch from check to online portal as a digital acquisition.
- Celebrate "digital revenue growth" without decomposing first-time vs. existing-donor contribution.
- Optimize digital marketing spend purely on total digital revenue — optimize on first-time donor rate and cohort retention.

## Edge cases / when the rule does NOT apply

For organizations where all giving is online by default (no mail or phone channel), this distinction doesn't apply — all revenue is digital-channel by definition. Peer-to-peer fundraising campaigns complicate the attribution because the first touch may be a friend's social share; use campaign source tagging to preserve the distinction.

## See also

- [`../agents/nonprofit-finance-analyst.md`](../agents/nonprofit-finance-analyst.md) — builds the development scorecard and channel attribution analysis.
- [`./segment-donors-by-value-recency-and-engagement.md`](./segment-donors-by-value-recency-and-engagement.md) — the companion rule on segmenting the donor file to read retention accurately.

## Provenance

Codifies the team's §3 #4 house opinion ("read cost-to-raise-a-dollar by channel, not blended") applied to digital attribution. The first-time-vs-existing conflation is the most common digital-reporting error; this rule documents the correct decomposition.

---

_Last reviewed: 2026-06-05 by `claude`_

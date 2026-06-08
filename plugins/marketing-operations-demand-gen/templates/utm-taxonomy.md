# UTM Taxonomy

> **Purpose:** the definitive UTM taxonomy for this organization. Every external campaign link
> carries the full UTM string, built from this reference. Inconsistent UTM data permanently corrupts
> channel attribution — treat this document as infrastructure, not a suggestion.
>
> **Owner:** `[Marketing Ops / Attribution Analyst]` · **Last updated:** `YYYY-MM-DD`

---

## Core principles

1. **Lowercase everything.** `LinkedIn` and `linkedin` are two different sources in GA4/your MAP.
   All UTM values are lowercase, always.
2. **Kebab-case for multi-word values.** Use hyphens, not underscores or spaces.
   `paid-social` not `paid_social` or `paid social`.
3. **Never track internal links.** UTM parameters on internal links overwrite the original
   session source. Tag only the first external click that lands a visitor.
4. **All three required parameters always.** If `utm_source`, `utm_medium`, or `utm_campaign`
   is missing, that click is unattributed. No exceptions.
5. **Validate before launch.** Run every final URL through the QA checklist below before a
   campaign goes live.

---

## Parameter definitions

### `utm_source` — Where did the traffic come from?

The channel origin. **Required.** Lowercase.

| Source value | Use for |
|---|---|
| `google` | Google Ads (paid) or Google organic (set medium to `organic` for organic) |
| `linkedin` | LinkedIn Ads or organic LinkedIn |
| `facebook` | Facebook/Instagram Ads |
| `bing` | Bing/Microsoft Ads |
| `newsletter` | Your own email newsletter sends |
| `hubspot` | HubSpot-triggered marketing emails (non-newsletter) |
| `marketo` | Marketo-triggered marketing emails |
| `pardot` | Pardot/Account Engagement emails |
| `partner` | Partner referral traffic |
| `event` | Event / conference registrations |
| `webinar` | Webinar registration / reminder emails |
| `direct` | Do NOT use in UTMs — direct is the absence of a UTM, not a source to tag |
| `content-syndication` | Third-party content syndication programs |
| `review-site` | G2, Capterra, TrustRadius traffic |
| `[custom]` | New sources: add here, document the rationale, announce the addition |

### `utm_medium` — What type of traffic is it?

The traffic mechanism. **Required.** Lowercase.

| Medium value | Use for |
|---|---|
| `cpc` | Cost-per-click paid advertising (search, display, paid social) |
| `email` | All marketing email sends |
| `social` | Organic social posts |
| `organic` | SEO / organic search (typically added via GA4 auto-tagging, not manual) |
| `referral` | Partner referral or review-site links |
| `event` | Event-sourced traffic (in-person or virtual) |
| `webinar` | Webinar-specific email or registration links |
| `content-syndication` | Syndicated content links |
| `display` | Programmatic display / retargeting |

### `utm_campaign` — Which campaign is this?

The canonical campaign name, in **kebab-case, lowercase**. **Required.**

Format: `[year]-[quarter]-[segment]-[motion]-[short-name]`

| Example | Campaign |
|---|---|
| `2026-q3-ent-abm-salesforce-admin-series` | Q3 2026 enterprise ABM webinar series |
| `2026-q4-mm-inbound-pricing-guide` | Q4 2026 mid-market pricing guide content campaign |
| `2026-q2-smb-nurture-onboarding-sequence` | Q2 2026 SMB onboarding nurture |

**Rule:** the `utm_campaign` value must exactly match the canonical campaign name used in the MAP,
CRM campaign record, and cost ledger. Drift between these three breaks campaign influence reporting.

### `utm_content` — Which creative variant?

Use only when A/B testing or differentiating creative in the same campaign. **Optional.**

| Example value | Use for |
|---|---|
| `headline-v1` | Headline variant A |
| `headline-v2` | Headline variant B |
| `cta-demo` | "Request a demo" CTA |
| `cta-trial` | "Start a free trial" CTA |
| `image-product` | Product screenshot creative |
| `image-social-proof` | Customer quote creative |

### `utm_term` — Which paid keyword?

Use only for paid search campaigns to capture the keyword that triggered the ad. **Optional.**

| Example value | Use for |
|---|---|
| `marketing-automation-software` | Exact match keyword |
| `hubspot-alternative` | Competitor keyword |
| `lead-scoring-tool` | Category keyword |

---

## URL builder

Assemble the tagged URL by appending the query string:

```
[Landing page URL]?utm_source=[source]&utm_medium=[medium]&utm_campaign=[campaign]
```

Add optional parameters as needed:

```
[URL]?utm_source=linkedin&utm_medium=cpc&utm_campaign=2026-q3-ent-abm-salesforce-admin-series&utm_content=headline-v1
```

**Encode special characters.** Spaces → `%20`. Ampersands in the landing page URL → `%26`.
**Never** include spaces in the raw UTM string.

---

## URL builder worksheet (fill per campaign)

| Asset | Landing page URL | utm_source | utm_medium | utm_campaign | utm_content | Full tagged URL |
|---|---|---|---|---|---|---|
| LinkedIn Sponsored Content — Headline v1 | `[URL]` | `linkedin` | `cpc` | `[campaign-name]` | `headline-v1` | `[assemble here]` |
| LinkedIn Sponsored Content — Headline v2 | `[URL]` | `linkedin` | `cpc` | `[campaign-name]` | `headline-v2` | `[assemble here]` |
| Email CTA — Demo | `[URL]` | `[source]` | `email` | `[campaign-name]` | `cta-demo` | `[assemble here]` |
| Email CTA — Trial | `[URL]` | `[source]` | `email` | `[campaign-name]` | `cta-trial` | `[assemble here]` |

---

## Pre-launch UTM QA checklist

Run before every campaign goes live:

- [ ] All three required parameters present on every external link: `utm_source`, `utm_medium`, `utm_campaign`.
- [ ] All UTM values are lowercase with no spaces (kebab-case for multi-word values).
- [ ] `utm_campaign` value matches the canonical campaign name in MAP, CRM, and cost ledger exactly.
- [ ] No UTM parameters on internal links (navigation, footer, header).
- [ ] All final URLs resolve correctly (no 404s, no redirect chains that strip query parameters).
- [ ] A/B `utm_content` variants named consistently if split-testing.
- [ ] URLs validated in a staging/preview environment before production traffic.

---

## Governance

**Adding a new source or medium:** propose the new value, document the use case, and update this
taxonomy before any campaign uses it. Do not invent one-off values — they become unmatchable orphans
in the attribution model.

**Quarterly UTM coverage audit:** check the % of form fills and CRM leads with all three required
UTM parameters populated. Target ≥ 90% coverage. A coverage rate below 80% materially impairs
attribution quality.

**Owner of this document:** `[Marketing Ops / Attribution Analyst]` — update the `Last updated`
date any time a new value is added or a convention changes.

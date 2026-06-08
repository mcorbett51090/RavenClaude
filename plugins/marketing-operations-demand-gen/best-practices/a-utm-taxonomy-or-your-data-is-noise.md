# A UTM taxonomy or your data is noise

**Status:** Absolute rule
**Domain:** Marketing operations / campaign tracking
**Applies to:** `marketing-operations-demand-gen`

---

## Why this exists

UTM parameters are the primary data infrastructure for channel attribution in B2B marketing.
When they are missing, inconsistently cased, or differently named across campaigns and channel
owners, every downstream report is compromised. `LinkedIn` and `linkedin` are two different
sources in GA4 and in every MAP. `Paid-Social` and `paid_social` are unmatchable orphans in a
join. A form fill with no UTM parameters is permanently unattributed — the history cannot be
reconstructed after the fact.

Unlike a model or a strategy, this failure mode is not recoverable. You cannot retroactively
apply UTM parameters to historical traffic. Every day without a consistent taxonomy is a day of
attribution data that is permanently degraded.

## How to apply

- **Define the taxonomy before any campaign goes live.** Source values, medium values, campaign
  naming convention, casing rule, and the required vs optional parameter set are documented in
  `templates/utm-taxonomy.md`. New values are added to the taxonomy, not invented ad hoc.
- **Enforce casing at the governance level.** All UTM values are lowercase with hyphens for
  multi-word values. Use a URL builder (linked from the taxonomy template) that enforces the
  convention programmatically — do not rely on human discipline alone.
- **Never tag internal links.** UTM parameters on internal site navigation overwrite the original
  session source. Tag only the first external click.
- **Run a pre-launch QA checklist on every campaign.** Every external link is validated before a
  campaign goes live. Missing or malformed UTMs on a paid campaign can corrupt an entire period's
  attribution data.
- **Audit UTM coverage quarterly.** The % of form fills and CRM leads with all three required
  parameters (`utm_source`, `utm_medium`, `utm_campaign`) populated is a measurement-health metric.
  Target ≥ 90% coverage. Below 80% materially impairs attribution quality.

**Do:**

- Use a URL builder that enforces lowercase and kebab-case.
- Enforce the taxonomy in campaign briefs — no campaign launches without a completed UTM set.
- Train every channel owner (paid, email, events, partner) on the taxonomy.
- Add the UTM coverage rate to the monthly marketing ops dashboard.

**Don't:**

- Allow channel owners to invent new source or medium values without updating the taxonomy.
- Mix `_` and `-` in the same taxonomy (pick one convention and standardize).
- Accept "we'll add UTMs next campaign" — retroactive fix is not possible for past traffic.
- Place UTM parameters on internal site links.

## Edge cases / when the rule does NOT apply

Google organic search is typically captured via GA4 auto-tagging (gclid) and SEO signal — UTM
parameters are not added to organic search snippets. For organic social posts, UTMs are optional
when the channel itself is trackable via referral domain, but strongly recommended when measuring
a specific post or campaign.

## See also

- [`./attribution-is-a-model-not-the-truth.md`](./attribution-is-a-model-not-the-truth.md)
- [`../templates/utm-taxonomy.md`](../templates/utm-taxonomy.md)
- [`../skills/campaign-operations/SKILL.md`](../skills/campaign-operations/SKILL.md)

## Provenance

Codifies the universal practitioner consensus in B2B marketing operations: UTM taxonomy is
data infrastructure, not a campaign configuration. Based on GA4 documentation (UTM parameter
handling), MAP UTM capture documentation (HubSpot, Marketo, Pardot), and the MO Pros community
"state of marketing ops" research on attribution quality failures.

---

_Last reviewed: 2026-06-08 by `claude`._

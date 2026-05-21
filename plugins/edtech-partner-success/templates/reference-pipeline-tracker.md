# Reference customer pipeline tracker

> **What this is.** The PSM's per-partner status board for advocacy-program participation. Tracks who's willing to be a reference, what they'll do (logo / quote / case study / speaker / peer call), legal-review status, and when the willingness was last confirmed. Without this, Marketing will repeatedly ask "got anyone for a case study?" and the PSM will repeatedly default to the loudest champion (often not the best fit).
>
> **Refresh quarterly.** Champions change roles. Districts re-evaluate media policies. A partner who was willing-with-attribution 6 months ago may now require anonymization. Stale data here causes embarrassing asks.
>
> **Health-score gate.** Only partners in the **top-quartile health** at the time of the ask should be in this tracker as "willing." Bottom-quartile partners under active risk should NOT be referenced — both because their story is unstable and because the ask burns goodwill they don't have to spare.

---

## Per-partner row

| Field | Notes |
|---|---|
| **Partner name** | District / institution / employer name |
| **Segment** | K-12 / higher-ed / corp L&D |
| **PSM owner** | Named PSM |
| **Health-score tier** | Top quartile / 2nd / 3rd / bottom (NOT eligible if bottom) |
| **Champion** | Named individual + role |
| **Willingness types (multi-select)** | Logo / Public quote / Anonymous quote / Case study (district-attributed) / Case study (anonymous) / Webinar speaker / Conference speaker / Peer call (with prospects) / Sales reference call |
| **Anonymization preference** | Full attribution / district-only / fully anonymous (state-law-driven, not preference; see knowledge file) |
| **Last confirmed** | YYYY-MM-DD the partner reconfirmed willingness — refresh if > 6 months |
| **Legal review status** | District legal review timeline; some states require formal sign-off |
| **Topic strengths** | What this partner is the best reference *for* — feature X, use case Y, segment-specific story Z |
| **Asks made (count + last)** | How many times we've asked this partner for advocacy + when last; cap at 2/year for most |
| **Active assets** | List of published case studies / quotes / speaker engagements |
| **Restrictions** | Anything the partner has explicitly excluded (no student quotes, no specific competitor naming, no public attribution of dollar values, etc.) |
| **Next-best ask** | What's the *next* advocacy ask this partner is best positioned for? (Should be a step up from prior asks, not a repeat.) |

## Pipeline table (active partners)

| Partner | Segment | Willingness | Last confirmed | Topic strengths | Active assets | Next ask |
|---|---|---|---|---|---|---|
| `<name>` | `<seg>` | `<list>` | `<YYYY-MM-DD>` | `<topics>` | `<assets>` | `<next>` |

## Pipeline rules of thumb

1. **Two-asks-per-year ceiling for most partners.** More than that and the partner stops being a partner — they become a marketing asset, and they'll opt out the next renewal.
2. **Match the topic to the partner's strength.** A partner who got value from feature X is the right reference for *prospects asking about feature X*, not for general "any partner who's happy."
3. **Step up the ask gradually.** First ask = quote. Second = case study. Third = speaker. Don't open with "we'd like you to keynote our user conference."
4. **Anonymization isn't second-best.** A district that can't be named because of state media-release law isn't a worse reference — they're a perfectly good reference *with attribution constraints*. Use them; just plan around the constraints.
5. **Withdraw from the pipeline after a service incident.** If the partner is in active recovery (red health), the PSM has the right of veto on any Marketing ask. State this explicitly to Marketing.

## References

- [`case-study-draft.md`](case-study-draft.md) — the artifact this tracker feeds
- [`cross-functional-partnership-map.md`](cross-functional-partnership-map.md) — Marketing function row for how the ask actually routes
- [`../knowledge/edtech-reference-customer-patterns.md`](../knowledge/edtech-reference-customer-patterns.md) — the why-behind-the-state-anonymization-rules
- [`../skills/advocacy-program-design.md`](../skills/advocacy-program-design.md) — playbook this tracker enables

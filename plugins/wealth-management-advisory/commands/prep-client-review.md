---
description: "Prepare a complete client review package: pre-meeting research brief, meeting agenda with talking points, and a post-meeting follow-up template. Pulls from the client profile provided and outputs advisor-prep materials ready for review before sending."
argument-hint: "[client profile, e.g. 'Garcia family, retired couple, $1.8M, income-focused, annual review, last meeting 12 months ago']"
---

You are running `/wealth-management-advisory:prep-client-review`. Use the `client-relationship-manager`
discipline and the `client-review-and-prospecting` skill.

## Steps

1. From the client profile provided, extract: life stage, AUM/account type, stated goals, last
   review date, any known life events or open action items.
2. Build a **pre-meeting research brief** (1 page) covering: account/life changes since last review,
   planning issues to raise, portfolio summary framing (allocation vs. IPS, performance summary
   placeholder), and relationship health note.
3. Build a **meeting agenda** following the standard structure in `skills/client-review-and-
   prospecting/SKILL.md` (opening → goal check → portfolio review → planning issues → action items),
   scaled to the client's tier and service model.
4. Write **advisor talking-point notes** for each agenda section — not a script, but the key
   framing the advisor should have in mind.
5. Build a **post-meeting follow-up email template** (with placeholder brackets for decisions and
   action items) ready for the advisor to complete after the meeting.
6. Flag any compliance-sensitive content (investment recommendations, performance figures) for
   `advisory-compliance-advisor` review before distribution.
7. Emit the Structured Output block with the three artifacts and any handoff recommendations.

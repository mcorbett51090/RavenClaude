---
name: client-review-and-prospecting
description: "Run a complete client review cycle (pre-meeting prep, meeting agenda, post-meeting follow-up) and manage the prospecting pipeline (COI outreach sequences, referral asks, new-prospect onboarding). Produces advisor-prep communication drafts; all client-facing written materials require advisory-compliance-advisor review before distribution."
---

# Client Review and Prospecting

**Purpose:** help the advisor run a high-quality review cycle — from pre-meeting research through
follow-up — and maintain an active, disciplined prospecting pipeline through COI relationships,
referral asks, and new-prospect outreach.

---

## Review cycle operating loop

### Step 1 — Pre-meeting research (the 20-minute prep)

Gather before every review meeting:
- **Last review notes:** decisions made, action items assigned (owner + deadline), open issues.
- **Account changes:** contributions, withdrawals, beneficiary updates, new accounts.
- **Life events:** job change, marriage/divorce, birth/adoption, inheritance, health changes,
  real estate purchase/sale, retirement, death of a family member. Check your CRM notes and
  any flagged events from the prior review.
- **Market/portfolio context:** YTD return vs. benchmark, major allocation changes since last
  review, any rebalancing taken.
- **Planning issues to raise:** upcoming RMD, Roth conversion window open, Social Security
  eligibility approaching, insurance review due, beneficiary audit overdue.
- **Relationship health:** last contact date, any service issues, referral capacity (has this
  client referred anyone? Are there opportunities?).

Output: a 1-page pre-meeting brief the advisor can read in the car or before walking in.

### Step 2 — Meeting agenda

Standard annual review structure:

1. **Opening (5 min):** life update — "What's changed since we last met? Anything on your mind
   that we should focus on today?"
2. **Goal check (10 min):** review progress vs. stated goals (retirement date, income target,
   legacy). Are the goals still current?
3. **Portfolio review (15 min):** performance vs. benchmark (with disclosure), allocation vs. IPS,
   any rebalancing recommendations. Use `portfolio-review-and-rebalancing` skill for the narrative.
4. **Planning issues (15 min):** address the 1–2 issues from the pre-meeting brief. Keep it
   focused — deep dive on one thing beats a rushed tour of five.
5. **Action items and next steps (5 min):** confirm each action item, assign owner and deadline,
   confirm next review date or trigger.

Adjust for client tier: A-tier clients may warrant 90-minute comprehensive reviews with a full
planning update; C-tier may be a 30-minute check-in focused on the portfolio and one planning note.

### Step 3 — Post-meeting follow-up (within 24 hours)

Follow-up email structure:
- **Thank-you opener:** genuine, brief.
- **Meeting summary:** 2–3 sentences on what was discussed and the key decisions.
- **Action items:** bulleted list with owner and deadline for each.
- **Document requests:** any forms, statements, or documents the client agreed to provide.
- **Closing:** "Please don't hesitate to reach out with questions; our next review is scheduled
  for [date/trigger]."

Route any investment-related language in the follow-up through `advisory-compliance-advisor`
before sending.

---

## Prospecting pipeline operating loop

### Step 4 — COI relationship development

Center-of-influence (COI) sequence model:

**Touch 1 — Introduction and value framing (not a sales pitch):**
- Open with a genuine interest in their practice and their clients' needs.
- Frame what you do in terms of value for their clients (e.g., "I specialize in working with
  physicians on student debt repayment and disability planning — issues that often surface in your
  tax work").
- Ask about their practice and what kinds of planning issues they encounter most.

**Touch 2 — Value-add follow-up:**
- Share a relevant resource: a planning note, a case study (de-identified), or an invitation to
  an educational event.
- The value-add must be genuinely useful to the COI's clients; not a brochure about your services.

**Touch 3 — Relationship meeting:**
- Request a 30-minute conversation to explore whether your practices are complementary.
- Frame it as a mutual exploration, not an ask.

Track COI relationship stage in CRM: `prospect COI → met → active → referring`.

### Step 5 — Referral ask

A referral ask has three parts:

1. **Gratitude anchor:** "Over the past 8 years, I've really valued the work we've done together.
   I feel like we've made real progress toward [goal]."
2. **Specific ask:** "I'm always looking to work with people like you — is there anyone in your
   circle — a colleague, a family member, a friend — who you think could benefit from the kind of
   planning we do here?"
3. **Graceful exit:** "If nobody comes to mind right now, that's completely fine — I just want you
   to know that a referral from you would mean a lot to me."

Best timing: after a service delivery milestone (plan completion, a strong review meeting, a
difficult situation handled well), not at the start of a meeting or on a flat check-in call.

**Compliance note:** any written referral solicitation, referral fee arrangement, or testimonial
use requires review under the 2022 Marketing Rule. Route to `advisory-compliance-advisor`.

### Step 6 — New-prospect onboarding cadence

After a prospect agrees to move forward:
- **Day 1:** welcome call/email, document checklist, account-opening paperwork.
- **Day 3–5:** confirm receipt of documents; provide a "what to expect" summary.
- **Week 3:** complete the discovery meeting; produce the preliminary plan outline.
- **Month 2:** deliver the plan and present recommendations.
- **Month 3:** follow up on implementation progress; schedule the 6-month check-in.

---

## Anti-patterns

- A review agenda that skips the life-update and goals-check — treating clients as portfolio
  accounts rather than people with goals.
- Follow-up emails sent 3+ days after the meeting.
- COI outreach that is 100% ask, zero value for the COI's clients.
- A referral ask made before a meaningful service delivery milestone.
- Prospect onboarding with no structured follow-up cadence — prospects lost between "yes" and
  account-opening are a process failure.
- Any marketing material, testimonial reference, or performance claim distributed without
  compliance review.

---

## Output

Pre-meeting research brief, meeting agenda with talking points, post-meeting follow-up email,
COI outreach sequence, referral-ask script, or new-prospect onboarding checklist. Route all
client-facing written communications through `advisory-compliance-advisor` before distribution.

# AI Workflow Library — PSM Team

> Reusable AI patterns for Partner Success Manager work. **Owner:** AI champion (this PSM); **users:** the whole PSM team. Each entry: pattern → when to use → the prompt → example output → notes. Grows organically as the team experiments.

**Last updated:** YYYY-MM-DD
**Maintainer:** *<name>*

---

## How to use this library

1. **Browse** the patterns below when you have a task you want AI to help with.
2. **Copy the prompt** into Claude or ChatGPT, fill in the bracketed placeholders, and run it.
3. **If you discover a useful pattern**, add it here using the entry format below.
4. **If a pattern stops working** (model changes, partner context shifts), note it in the entry's "Notes" field rather than deleting — the failure is data.

## Entry format

```
### Pattern: <short imperative name>

**When to use:** <1–2 sentence trigger>

**Prompt:**
\```
<paste prompt with [bracketed placeholders] for the variable parts>
\```

**Example output:** <2–4 line example or link to a saved example>

**Notes:** <caveats, model preferences, things to watch for>
```

---

## Library

### Pattern: Summarize partner call notes for QBR prep

**When to use:** You've taken raw notes during a partner call and want a structured summary you can drop into the QBR document.

**Prompt:**
```
You're helping me prep a QBR. Here are my raw notes from a call with [partner name] on [date]:

[paste raw notes]

Produce three things:
1. A 3-bullet executive summary I can use in the QBR's "current state" section.
2. Any action items that surfaced — formatted as: action — owner — due date.
3. Any risks or concerns I should add to the partner's risk list.

Be specific. Don't invent details that weren't in my notes — if something's unclear, say so.
```

**Example output:** *Executive summary: 1) District piloting translation in 3 schools, expanding to 6 next semester. 2) Concerns about Spanish translation accuracy in legal/IEP contexts. 3) Asking about API access for their internal dashboards. Action items: confirm Spanish-IEP sample review — [PSM] — Friday. Risks: API access ask may signal frustration with current reporting.*

**Notes:** Works best with bullet-format raw notes; less reliable on long flowing transcripts. Always review the action items list — Claude tends to over-extract.

---

### Pattern: Draft QBR follow-up email

**When to use:** Right after a QBR meeting, while details are fresh — draft the recap-and-action-items email to the partner.

**Prompt:**
```
Draft a short professional follow-up email to [partner contact name] after our QBR. Tone: warm, specific, action-oriented. Include:

- Thank them for the time
- 2-3 bullet recap of what we agreed on (from these notes: [paste agreed outcomes])
- The action items each side committed to: [paste action items list]
- Confirm the next QBR date

Keep it under 200 words. Don't include "synergy," "circle back," or any other corporate filler.
```

**Example output:** *Hi [Name], thanks for the great QBR yesterday — I appreciated the candid conversation about the translation accuracy concerns. To recap: 1) Spanish-IEP sample review by Friday, 2) OneRoster integration kickoff scheduled for June 1, 3) Q3 QBR booked for August 15. Reach out anytime if anything else surfaces. Best, [PSM]*

**Notes:** Reliable. Matches the partner's name + tone if you give Claude an example email from your past correspondence with that contact.

---

### Pattern: Generate enablement-gap analysis from a partner profile

**When to use:** A partner is underperforming on adoption and you want a structured view of where the gaps are before the next touchpoint.

**Prompt:**
```
Here's a partner profile and their last 3 months of metrics:

[paste profile excerpt]
[paste recent metrics]

Help me identify where the enablement gaps are. For each gap:
- Name the gap (specific, not generic)
- Cite the evidence in the data
- Suggest a proactive action that would address it (demo session, runbook, training, integration check)

Don't suggest "more training" as a generic answer. Be concrete.
```

**Example output:** *Gap 1: Translation feature adopted in only 1 of 12 schools — evidence: usage telemetry shows 96% of usage from a single school. Action: schedule a "translation pilot" demo session with the other 11 schools' principals, anchored by a case study from the active school.*

**Notes:** Most useful right before a 🟡 Yellow → 🟢 Green recovery push. Pair with the success-plan template.

---

### Pattern: Pre-flight check on partner-facing content before translation

**When to use:** You're writing parent-facing or district-facing content that needs to be translated, and you want to flag culture/context issues *before* sending it through the formal translation tool.

**Prompt:**
```
I'm about to translate this content to [target languages]. Before I do, review it for:

[paste English source]

1. Idioms or phrases that won't translate cleanly
2. Anything that may read differently in K-12 contexts in [target culture(s)]
3. Tone shifts that should happen for translated audiences (formality, directness)
4. Any FERPA-adjacent or compliance-sensitive language that needs careful handling

Don't actually translate it — just flag what I should adjust in the English first.
```

**Example output:** *Two flags: 1) "Stay in the loop" is an English idiom — replace with "stay informed" before translating. 2) The "we'd love to chat" tone is too informal for Mandarin-speaking parent audiences in your target districts; consider "we welcome your input" instead.*

**Notes:** Pre-flight check, not a replacement for formal translation tools. Especially valuable for the first parent-comm of the school year when impressions are set.

---

### Pattern: Generate proactive runbook from common-issues log

**When to use:** You've spotted a pattern of repeat support tickets across partners; want to turn that into a proactive runbook to share during onboarding so the *next* partner doesn't trip on it. (This is your high-touch DNA showing up — convert reactive support data into proactive enablement content.)

**Prompt:**
```
Here's a list of recent support tickets from partners on the same product:

[paste ticket summaries]

Help me write a proactive runbook for new partners. Structure:
- "Things people usually trip on first" — top 3-5 issues
- For each: the symptom (in partner's words), the cause, the prevention step they can take during setup
- Tone: friendly and confidence-building, not "here's what you'll break"
```

**Notes:** The "in partner's words" framing is what makes this useful — Claude can re-write engineer-flavored ticket descriptions into language a district CTO would actually use.

---

## Add a new pattern

Use the entry format at the top. Append below the existing patterns. **Don't delete patterns** — if one stops working, add a "Notes" line explaining what changed. The failure is data for the team.

---
name: stakeholder-engagement
description: "Build and maintain a stakeholder register with power/interest mapping, design a tailored communications plan, prepare steering packs and executive status reports, and handle escalation memos — ensuring the right message reaches the right stakeholder at the right depth every cycle."
---

# Skill: stakeholder-engagement

**Purpose:** Produce the stakeholder intelligence and communications infrastructure a project needs to build support, manage resistance, and escalate cleanly. Used by `stakeholder-comms-lead` (primary) and `delivery-lead` (governance/steering context).

## When to use

- Project initiation — before the first comms plan is drafted.
- Any project entering a change-intensive phase (scope change, key personnel change, phase transition).
- When a stakeholder has gone quiet, pushed back, or signalled resistance.
- When preparing a steering pack, an escalation memo, or an exec-level status update.

---

## Step 1: Build the stakeholder register

For every person or group who can affect or be affected by the project:

| Field | Guidance |
|---|---|
| Name / group | Individual name or defined group (e.g. "End-user community — Sales floor") |
| Role on the project | Sponsor / Decision-maker / Approver / Influencer / Affected party / Informed only |
| Organization / function | Where they sit |
| Power | HIGH (can unilaterally block or approve) / MEDIUM / LOW |
| Interest | HIGH (outcome directly affects them) / MEDIUM / LOW |
| Current attitude | Champion / Supporter / Neutral / Resistant / Blocker |
| Preferred channel | In-person / steering committee / email digest / 1:1 call |
| Key concern | The specific thing they care about most |
| Desired outcome at project end | What does success look like for them personally? |

**Minimum register size:** every person with HIGH power + every person with HIGH interest, plus any LOW-power / HIGH-interest groups (users, affected teams) who can generate noise.

---

## Step 2: Power/interest grid

Plot the register onto the 2×2 grid:

```
           HIGH interest
                |
   [Manage      |   [Engage closely]
    closely]    |   (Sponsor, key
   (Decision-  HIGH   stakeholders)
    makers,     |
    approvers)  |
POWER ──────────+────────────── 
    LOW         |   HIGH
    power       |   power
                |
   [Monitor]    |   [Keep satisfied]
   (Interested  |   (High power,
    observers)  |   low active interest)
                |
            LOW interest
```

**Engagement model by quadrant:**

| Quadrant | Strategy | Comms frequency |
|---|---|---|
| High power / High interest | Engage closely — involve in decisions, pre-wire before steering meetings | Weekly or bi-weekly 1:1 or sub-group |
| High power / Low interest | Keep satisfied — high-level briefings; draw in when their domain is impacted | Monthly or milestone-triggered |
| Low power / High interest | Show consideration — include in user testing, feedback loops; they amplify sentiment | Fortnightly update; feedback sessions |
| Low power / Low interest | Monitor — mass-broadcast; no 1:1 investment | Monthly digest |

---

## Step 3: Communications plan

Build a plan that answers five questions for every stakeholder group:

1. **Who** — which register segment or named person?
2. **What** — what information do they need (progress, decisions, risks, milestones)?
3. **When** — how often, and triggered by what (schedule vs event)?
4. **How** — which channel?
5. **From whom** — which role authors and sends?

**Communications plan table:**

| Audience | Information need | Frequency | Channel | Owner | Format |
|---|---|---|---|---|---|
| Project Sponsor | Overall status, key decisions, budget vs actuals | Bi-weekly | 1:1 call + email summary | Delivery Lead | Narrative summary + RAG |
| Steering committee | Programme status, risk/issues, change requests | Monthly | Steering pack — live presentation | Stakeholder Comms Lead | Steering pack (see template) |
| End-user community | Impact on their workflow, change readiness, training timeline | Fortnightly | Email digest + intranet post | Change Lead | Plain-language update |
| Project team | Task progress, blockers, sprint outcomes | Weekly | Stand-up + sprint review | Scrum Master / PM | Verbal + sprint notes |
| IT / security governance | Technical decisions, architecture changes, compliance confirmations | As triggered | Email + governance register | Delivery Lead / Architect | Decision log extract |

---

## Step 4: Steering pack structure

A steering pack is a decision-enablement document, not a diary entry.

**Required sections:**

1. **Status at a glance** — RAG indicator + one-sentence narrative (the reader must be able to act on this before reading further).
2. **Key decisions required** — explicitly labelled; what the committee must decide today, with a recommendation and a "if we don't decide, this happens" consequence.
3. **Progress since last steering** — milestone delivery vs baseline; EV indices (SPI/CPI) if applicable.
4. **Risk and issue summary** — top 3–5 items from the register, with response status; nothing new in the meeting that wasn't in the pack.
5. **Change requests (if any)** — each CR with its impact and the requested disposition.
6. **Next period outlook** — key milestones and decisions expected before the next pack.

**Pack hygiene:**
- Pack distributed ≥ 48 hours before the meeting so attendees can read, not just listen.
- No surprises in the room — if a topic needs discussion, the PM pre-wires with the sponsor before the pack goes out.
- RAG must match the numbers: a Green RAG on an SPI of 0.78 is a misreport.

---

## Step 5: Escalation memo

When an issue exceeds the PM's authority to resolve (budget overrun, key resource unavailability, scope that requires sponsor decision), escalate in writing within 24 hours of confirming the issue.

**Escalation memo structure:**

```
TO: [Sponsor name, title]
FROM: [PM name]
DATE: [YYYY-MM-DD]
SUBJECT: [Project name] — Escalation: [Issue name, one line]

SITUATION (what has happened, factual):
[2–3 sentences. Observable facts only — no spin.]

IMPACT (what it affects, quantified where possible):
[Schedule impact: e.g. +12 days on milestone X]
[Cost impact: e.g. USD +45,000 against current budget]
[Risk to delivery: ...]

OPTIONS EVALUATED (what the PM has already considered):
Option A: [Description, cost, schedule, risk]
Option B: [Description, cost, schedule, risk]

RECOMMENDATION:
[Which option the PM recommends and why. Be direct.]

DECISION REQUIRED BY: [DATE — what happens if the decision is not made by this date]

NEXT STEP IF APPROVED: [What the PM will do within 24 hours of approval]
```

**Do not escalate:**
- Without having evaluated at least two options.
- Without a "decision required by" date.
- Via a verbal conversation only — always follow up with the written memo, even after a verbal agreement.

---

## Pitfalls

- **Comms plan without power/interest map** — the plan treats every stakeholder the same depth; the sponsor gets the same update as an observer.
- **Steering packs that open with a data table** — the committee skips the narrative; the PM must interpret the data, not present it raw.
- **Pre-wiring skipped** — a decision that is introduced cold in the steering committee almost never gets approved in the room; resistance is not managed.
- **Escalation memo sent without options** — the sponsor receives a problem report with no path forward; they lose confidence in the PM.
- **Resistance mistaken for misunderstanding** — a resistant stakeholder often understands completely; they have a different interest. Engagement, not more information, is the fix.

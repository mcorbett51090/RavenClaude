# Agent Brief Template

Use this when you want a new agent created or dispatched. **Fill in what you can; leave blanks where you don't know** — Claude will fill in the domain-specific detail when drafting the strong request.

You have two ways to use this template:

1. **Fill it in yourself** as much as you can, then paste it back to Claude.
2. **Skip the template entirely** — just describe your goal in plain words and ask Claude to *"draft a strong agent brief for me."* Claude will produce a filled-in version of this template for you to review.

Either path works. The template just keeps you from forgetting one of the eight things that matter.

---

## 1. What outcome do you want?
*One sentence in plain words. What should this agent help you accomplish?*

> **Example:** *"I want an agent that helps me act like a competent Salesforce admin while I'm learning the platform."*

**YOUR ANSWER:**

---

## 2. What's the context?
*What's prompting this? A client engagement? A new domain you're learning? Something repetitive you want to systematize?*

> **Example:** *"I'm starting my first Salesforce engagement next month. I have Power Platform experience but no Salesforce background."*

**YOUR ANSWER:**

---

## 3. Are you new to this domain or experienced?
*Affects whether the agent should over-explain (new) or be terse (experienced). It's perfectly fine to write* **"new — explain things in business terms first."**

**YOUR ANSWER:**

---

## 4. What does success look like?
*In **business terms**, not technical. How will you know it's working? Concrete examples are gold.*

> **Example:** *"When I dispatch it on a task, it produces a working artifact AND writes any non-obvious lessons to the lessons-learned log so I don't have to relearn them."*

**YOUR ANSWER:**

---

## 5. What's OUT of scope?
*What should the agent NOT do? Prevents drift just as much as the in-scope list.*

> **Example:** *"Don't touch infrastructure beyond Salesforce. Don't make changes in production environments without showing me the change first."*

**YOUR ANSWER:**

---

## 6. Any hard constraints?
*Must use a specific tool? Must read certain files first? Must avoid certain commands? Tight deadline? List anything must-have or must-not-have.*

**YOUR ANSWER:**

---

## 7. Personality / style
*Terse vs. chatty? Conservative vs. bold? Should it ask clarifying questions or make best-guess decisions? Default to* **"asks when ambiguous, terse otherwise"** *if you're not sure.*

**YOUR ANSWER:**

---

## 8. How much judgment does the work need? (this picks the model tier — and the bill)
*Every agent must declare a `model:` tier. Answer in plain words and Claude maps it:*

| If most of the agent's work is… | Tier | Why |
|---|---|---|
| Reading a lot and returning a little — search, grep, classify, extract, inventory | `haiku` | high volume, low judgment; the cheapest tier does this as well as the most expensive one |
| Bounded, well-specified edits or drafts from inputs you supply — known API calls, tests for a stated contract, first-draft prose | `sonnet` | mid-tier is the default for "do exactly this" |
| Deciding, designing, adjudicating, or gating a merge (a reviewer whose "no" must stick) | `opus` | judgment work; gates are never de-escalated to save money |

> **Example:** *"It mostly reads Salesforce docs and my org's metadata and tells me what's there — so `haiku`, escalating to `sonnet` when it has to draft a change."*

*If you're not sure, say so and describe the output: a short structured artifact (paths, a table, pass/fail) points down the table; a design or a verdict points up. Default to the cheaper tier and let a failure escalate one tier — that is the rule in* [`knowledge/model-tier-delegation.md`](../knowledge/model-tier-delegation.md).

**YOUR ANSWER:**

---

## What happens next

Once you've filled in what you know, Claude will:

1. **Draft a strong agent brief**, filling in the domain-specific detail you don't have.
2. **Show you the draft** for review and tweaking.
3. **Iterate** with you until the brief fits — usually one or two rounds.
4. **Build (or dispatch) the agent.**

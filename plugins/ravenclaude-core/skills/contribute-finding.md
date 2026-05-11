---
name: contribute-finding
description: For Claude sessions running in a consumer project (any project where ravenclaude-core is installed). Triggered when you discover a cross-domain finding worth contributing back to the RavenClaude marketplace — either spontaneously, or when the user says "contribute this," "save to RavenClaude," "this is worth keeping," or similar. Walks through the qualifying check, picks the right shape (lesson, best-practice, or both), and formats a copyable staging submission the user can drop into RavenClaude/docs/staging/incoming/.
---

# Skill: contribute-finding

You're working in a consumer project that has `ravenclaude-core` installed. Something you just learned or codified is worth sending back to the marketplace so future consumers benefit. This skill is the formatting playbook so the maintainer can review and promote your submission with zero rewriting.

The marketplace maintainer (typically Matt) reviews staged submissions with the [`review-staged-contributions`](./review-staged-contributions.md) skill. Your job is to give them a clean artifact to review.

---

## Step 1 — Does the finding qualify?

The marketplace's cross-domain `docs/` directory is for findings that apply to **any Claude work, any plugin, any project**. Run all three checks:

- ✅ **Cross-domain.** Power Platform-specific, finance-specific, EdTech-specific findings do NOT go here — they belong inside the relevant plugin's `skills/<skill>/resources/` folder. Cross-domain means: a different consumer working in a different stack would still benefit.
- ✅ **Generalizes.** A rule or a story another collaborator (or future-you in a different project) would benefit from — not a one-off preference and not a war story about a single client.
- ✅ **Still useful in a year.** If the finding is a hot take on a beta feature or a quirk of one tool's current version, it's probably not load-bearing enough to codify.

If any one of those is no, **do not submit**. Tell the user you considered contributing but the finding didn't qualify, and explain which check it failed. Save it to project-local memory instead.

---

## Step 2 — Pick the shape

Use the rule from [`lessons-vs-best-practices`](../../../docs/best-practices/lessons-vs-best-practices.md):

| Finding shape | Submission type | Why |
|---|---|---|
| *We tried X, it failed because Y, so we now do Z* (story) | **Lesson** | Goes into `docs/memory-bank/lessons-learned.md` as a dated entry |
| Timeless rule with no failure story behind it | **Best-practice** | Goes into `docs/best-practices/<slug>.md` as its own file |
| Both a story AND a generalizable rule | **Both** — submit two separate files | Each promotes independently and they cross-link on the maintainer side |

One staging file = one canonical doc on promotion. Do not combine a lesson and a best-practice in one file.

---

## Step 2.5 — Tag the topic

Pick the `topic:` value that best describes the *expertise* the finding draws on. On the maintainer side, the review skill spawns the matching specialist agent to analyze whether the finding **generalizes** or is **one-off** — so getting the topic right routes the submission to the right reviewer.

| `topic:` | Expert who'll review on the maintainer side | Use when the finding is about… |
|---|---|---|
| `architecture` | ravenclaude-core / architect | system design, trade-offs, structural choices |
| `backend` | ravenclaude-core / backend-coder | server, API, DB, jobs, integrations |
| `frontend` | ravenclaude-core / frontend-coder | UI, components, client state, styling |
| `fullstack` | ravenclaude-core / fullstack-coder | client/server crossings as one unit |
| `testing` | ravenclaude-core / tester-qa | test design, flake hunting, coverage |
| `code-review` | ravenclaude-core / code-reviewer | review patterns, diff hygiene |
| `security` | ravenclaude-core / security-reviewer | auth, crypto, secrets, untrusted input |
| `research` | ravenclaude-core / deep-researcher | sourcing, verification, comparison |
| `documentation` | ravenclaude-core / documentarian | stakeholder prose, runbooks, READMEs |
| `design` | ravenclaude-core / designer | UX, wireframes, visual hierarchy |
| `prompt-engineering` | ravenclaude-core / prompt-engineer | agent/skill prompts, prompt patterns |
| `project-management` | ravenclaude-core / project-manager | RAID, status, cadence, stakeholders |
| `partner-success` | ravenclaude-core / partner-success-manager | QBR, success plans, health scoring |
| `power-platform` | best-fit power-platform agent (router picks by subtopic) | Power Platform stack specifics |
| `other` | architect (fallback) | cross-cutting findings that don't fit above |

If the finding spans two topics (e.g., security + backend), pick the one the *expert* should weigh in on most heavily — usually the more specialized one. The maintainer can request a second-opinion route during review if needed.

---

## Step 3 — Scrub for safety before drafting

Before you write a single word of submission:

- Remove client names, tenant IDs, real GUIDs, internal URLs, email addresses, account numbers.
- Replace specifics with placeholders: `<CLIENT>`, `<TENANT_ID>`, `contoso.crm.dynamics.com`, `user@example.com`.
- Read it as a stranger: would anyone trace this back to a real engagement? If yes, scrub harder.

This step is non-negotiable. The marketplace is private today but designed to remain shareable across projects, contractors, and (eventually) external collaborators.

---

## Step 4 — Draft using the right template

Wrap the entire submission in **one fenced code block** labelled `RAVENCLAUDE-STAGING-SUBMISSION`. The user copies that block verbatim — no edits needed.

### Lesson template

````markdown
```markdown RAVENCLAUDE-STAGING-SUBMISSION
<!-- RAVENCLAUDE-STAGING-METADATA
type: lesson
topic: <one of: architecture | backend | frontend | fullstack | testing | code-review | security | research | documentation | design | prompt-engineering | project-management | partner-success | power-platform | other>
proposed-by: <short context — e.g. "consumer project building a Dataverse flow integration">
proposed-on: YYYY-MM-DD
target-file: docs/memory-bank/lessons-learned.md
status: pending
-->

## YYYY-MM-DD — Short title naming the rule or finding

**Context:** What we were trying to do. 1–2 sentences.

**What we tried first:** The path that failed. 1–2 sentences.

**Why it failed:** The actual reason, with technical detail. 2–4 sentences.

**What works:** The canonical solution. 2–4 sentences.

**How to apply:**
- When this rule fires, what to do. 1–2 bullets.

**Trace:** Origin context (this consumer project, generalized), pointers to any external authoritative source if relevant.
```
````

### Best-practice template

````markdown
```markdown RAVENCLAUDE-STAGING-SUBMISSION
<!-- RAVENCLAUDE-STAGING-METADATA
type: best-practice
topic: <one of: architecture | backend | frontend | fullstack | testing | code-review | security | research | documentation | design | prompt-engineering | project-management | partner-success | power-platform | other>
proposed-by: <short context>
proposed-on: YYYY-MM-DD
target-file: docs/best-practices/<descriptive-slug>.md
status: pending
-->

# <Short rule name — what this doc tells you to do or not do>

**Status:** _Pick one — delete the others._
- **Absolute rule** — never break this.
- **Primary diagnostic** — when symptom X appears, check this first.
- **Pattern** — strong default; deviate only with a written reason.

**Domain:** _e.g. ALM, Identity, Web API, Solution mechanics, Agent design, Cross-domain._

**Applies to:** _Which plugin(s), tool(s), or project type(s)._

---

## Why this exists

_2–5 sentences on the rationale. Why is this worth codifying?_

## How to apply

_Concrete, copy-paste-grade guidance._

**Do:**
- _…_

**Don't:**
- _…_

## Edge cases / when the rule does NOT apply

_Known exceptions._

## See also

_Repo-relative cross-references._

## Provenance

_Where this rule came from. Be specific._

---

_Last reviewed: YYYY-MM-DD by `<short context or github handle>`_
```
````

---

## Step 5 — Hand off to the user

After you print the staging block, tell the user — concisely — what to do with it. Phrase it like:

> I've drafted a `RAVENCLAUDE-STAGING-SUBMISSION` above. To submit it:
> 1. Copy the entire fenced block (including the `<!-- RAVENCLAUDE-STAGING-METADATA -->` comment).
> 2. In the **RavenClaude** repo, create the file `docs/staging/incoming/YYYY-MM-DD-<slug>.md` where the date and slug match the metadata.
> 3. In your RavenClaude Claude Code session, run `/review-staged-contributions` to walk it through the keep/update/deny review.

If the user has their RavenClaude session open already, you can stop there — they'll handle the rest. If not, mention it'll wait in `docs/staging/incoming/` until they're ready.

**What happens on the maintainer side (so you can set expectations):** The review skill doesn't take your submission at face value. It spawns the **expert agent matching the `topic:` you tagged** to analyze whether the finding generalizes (applies to anyone working in that topic) or is one-off (specific to your situation). The expert's verdict is shown to the maintainer alongside your submission during the keep/update/deny prompt. This means a well-scoped submission with the right topic tag gets a fair, specialist read — and a submission that's actually a one-off issue gets caught before it lands in canonical docs.

---

## Anti-patterns

- **Do not** open a PR directly to RavenClaude from a consumer project. The staging path is lighter, routes through the same review, and doesn't require the consumer to have push permissions on the marketplace.
- **Do not** submit content you haven't scrubbed for client identifiers. The maintainer's review is for quality and fit, not for redacting secrets.
- **Do not** combine multiple findings in one staging file. Each file becomes one canonical doc on promotion.
- **Do not** invent content for sections you can't actually fill. If the lesson template's "What we tried first" / "Why it failed" sections feel empty, the finding is probably a best-practice (no failure story behind it), not a lesson.
- **Do not** submit personal preferences (your editor config, your working-style quirks). Those belong in project-local memory at `~/.claude/projects/.../memory/`, not in the cross-domain marketplace.

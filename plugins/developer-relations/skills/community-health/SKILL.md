---
name: community-health
description: "Operate a healthy developer community — first-response-time SLAs, evenly-enforced code of conduct, a contributor ladder, and an anti-burnout moderation rota. Health over headcount. Used by community-manager (primary)."
---

# Skill: community-health

**Purpose:** Run a developer community measured by response time and safety, not raw member
count. Used by `community-manager` (primary).

## When to use

- Standing up a Discord / forum / GitHub Discussions
- A community that's growing in size but not in answered-question rate
- Converting users into contributors
- Handling a code-of-conduct incident

## The three health metrics (report these, not headcount)

1. **Median first-response time.** Developers forgive an imperfect answer; they don't forgive
   silence. Set an SLA (e.g. "first response within 4 business hours") and measure it.
2. **% of questions answered.** An unanswered-question rate climbing is the earliest signal a
   community is dying.
3. **Sentiment / tone.** Sampled, not guessed — is the place welcoming to newcomers?

Member count is a *vanity input*. A 500-person answered community beats a 50,000-person ghost town.

## Code of conduct: enforced on an explicit ladder

An unenforced CoC is worse than none — it signals the rules are theater.

```
Warn  →  Mute (timeout)  →  Ban
```

- Apply the ladder **consistently** regardless of who the violator is.
- **Reporter safety first:** handle privately before any public statement; never expose the reporter.
- **Log every enforcement decision** (who, what, which rung, why) so it's defensible and even-handed.

## The contributor ladder

Turn users into contributors into maintainers on a *designed* funnel, not by luck:

```
Lurker → Asker → Answerer → First-time contributor → Regular → Maintainer / Ambassador
```

- Curate **good-first-issues** with real context (not "good first issue" slapped on hard tickets).
- Offer mentorship at the first-contribution rung; that's where most people fall off.
- Recognize movement up each rung visibly (this is most of the reward).

## Anti-burnout

Moderation and answering are **rota'd**, not heroics. A single person carrying the community
is a single point of failure and a burnout case waiting to happen.

## Output

A community-health plan: the SLA, the channel structure, the CoC enforcement ladder, the
contributor ladder, and the rota — plus the health dashboard. See
[`../../templates/community-health-dashboard.md`](../../templates/community-health-dashboard.md).

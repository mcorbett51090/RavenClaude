# Community & ecosystem — reference

Deep reference for the `community-and-ecosystem-manager` and the community-funnel skill. Companion to
[`devrel-decision-trees.md`](devrel-decision-trees.md).

---

## The community funnel, defined

| Stage | Definition | Health signal |
|---|---|---|
| Lurker | reads, never posts | traffic vs. posts ratio |
| Asker | posts a question | first-post conversion |
| Answerer | answers others' questions | answer rate, # distinct answerers |
| Contributor | opens a PR / writes content / files good issues | contributor conversion |
| Champion | advocates externally, mentors, runs events | ambassador count, external mentions |

Growth = unsticking the stage with the worst conversion, not adding lurkers at the top.

## Stuck-stage interventions

- **lurker → asker:** psychological safety and a clear "ask here." Seed real questions; set norms;
  make the first post easy and welcomed.
- **asker → answerer:** a recognition loop. People answer when answering is seen and rewarded —
  surface top answerers, give status, thank publicly.
- **answerer → contributor:** an on-ramp. Good-first-issues, a contribution guide, and a visible path
  from first PR to maintainer.
- **contributor → champion:** an ambassador tier with a **real value exchange** (below).

## Ambassador / champion program — the value exchange

A program decays the moment it becomes a perks list. Make the exchange explicit:

| Ambassador gives | Ambassador gets |
|---|---|
| reach, content, local events | early access, direct product line, visibility |
| field signal, feedback | status, recognition, swag (secondary) |
| mentoring new members | community leadership, growth, network |

Tiers should map to contribution, and the health metric is whether the exchange is actually
happening — not the headcount of the program.

## Response coverage

Define a **first-response SLA** (e.g., 4 business hours) and triage roles. Track:

- **Answer rate** — questions answered ÷ asked.
- **Time-to-first-response** — median; the p90 is where frustration lives.
- **Self-answer ratio** — answers from community vs. staff (the scaling metric).

## Unanswered questions are a docs signal

Cluster recurring questions; each cluster is a missing docs/quickstart section. Route the top clusters
to onboarding. Answering once and documenting beats answering forever.

## Platform note (verify before quoting specifics)

Discord / Slack / Discourse / GitHub Discussions are the common stack; the funnel logic is
platform-independent. Treat any specific platform-feature claim as `[unverified — confirm current
platform capability]` per the core Claim-Grounding protocol.

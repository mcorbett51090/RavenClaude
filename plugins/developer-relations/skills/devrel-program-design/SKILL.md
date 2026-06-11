---
name: devrel-program-design
description: "Design a DevRel program from charter to scorecard — locate the developer-journey bottleneck, write the mandate and non-goals, choose outcome metrics over vanity inputs, sequence the team, and build the exec value narrative."
---

# DevRel Program Design

**Purpose:** turn "we should do DevRel" into a defensible program with a mandate, metrics, and a
narrative the exec team will fund — anchored to where developers actually fall out of the journey.

---

## Steps

### 1. Locate the bottleneck in the developer journey

Map the journey and find the steepest drop before choosing any activity:

| Stage | Question | If this is the bottleneck, the mandate is… |
|---|---|---|
| Awareness | Do target developers know we exist? | Advocacy & content reach |
| Sign-up | Do aware developers try us? | Top-of-funnel content + frictionless trial |
| Activation | Do sign-ups reach first value? | **DX & onboarding engineering** (usually the highest-ROI gap) |
| Adoption | Do activated developers ship to production? | Docs depth, reference architectures, support |
| Expansion | Do adopters advocate and contribute? | Community & ambassador programs |

The single most common mistake is staffing advocacy/events while the real leak is activation. Fix
the bottleneck the data shows, not the activity that's most fun to do.

### 2. Write the mandate and the non-goals

Name what the program owns **and** what it explicitly does not. A DevRel team that owns "all things
developer" owns nothing measurably. Example mandate: *"Own developer activation and the
product-feedback loop; do NOT own paid acquisition or post-sale support."*

### 3. Choose outcome metrics, pair every vanity input

For each activity, pair its input metric with the outcome it must move:

| Vanity input | Must be paired with… |
|---|---|
| GitHub stars / followers | Activation rate, production adoption |
| Event attendees | Post-event activations, qualified pipeline influenced |
| Blog impressions | Quickstart starts, time-to-first-value |
| Discord members | Active ratio, question answer-rate, contributor conversion |

Use [`../../scripts/devrel_calc.py`](../../scripts/devrel_calc.py) to compute activation rate,
time-to-first-value, and funnel conversion.

### 4. Sequence the team against the bottleneck

First hire follows the bottleneck: activation gap → a DX/docs engineer before an evangelist;
awareness gap → an advocate first; expansion gap → a community manager first.

### 5. Build the exec value narrative

Connect activities → leading metrics → adoption/pipeline influence in the exec's language. Lead
with the activation and adoption outcomes; never open with stars or headcount.

---

## Output

A program charter (mandate, non-goals, owned metrics), a hiring sequence, and a one-page exec
narrative. Use the [`../../templates/devrel-strategy-onepager.md`](../../templates/devrel-strategy-onepager.md)
template.

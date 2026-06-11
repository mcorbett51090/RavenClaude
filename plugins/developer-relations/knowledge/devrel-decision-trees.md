# DevRel decision trees + capability map

Decision support for the `developer-relations` specialists. Traverse top-to-bottom; pick the
smallest-scope leaf that fits. Pair every decision with the metric that confirms it.

---

## 1. Mandate selection — "what should our DevRel program own?"

```
Where do developers fall out of the journey?
├─ They don't know we exist (awareness gap)
│    → Mandate = advocacy & content reach; first hire = developer advocate
├─ They sign up but never reach first value (activation gap)  ← most common, highest ROI
│    → Mandate = DX & onboarding engineering; first hire = docs-and-dx-engineer
├─ They activate but never ship to production (adoption gap)
│    → Mandate = depth docs, reference architectures, support paths
└─ They adopt but never advocate or contribute (expansion gap)
     → Mandate = community & ambassador programs; first hire = community manager
```

Rule: staff the bottleneck the funnel data shows, not the activity that's most visible or fun.

## 2. Metrics — "is this a metric or a vanity number?"

```
Does the number change a decision on its own?
├─ Yes, and it measures a developer reaching value → OUTCOME metric (report it)
│    e.g. activation rate, time-to-first-value, production adoption
└─ No, it's an input/proxy → VANITY input
     → Report ONLY paired with the outcome it's meant to drive, or cut it
       e.g. stars, followers, impressions, attendees
```

## 3. Content format — "what should we make for this stage?"

```
What is the developer's question right now?
├─ "Does this solve a problem I have?"      → awareness: conceptual post, talk, comparison
├─ "Will this work for my specific case?"   → evaluation: tutorial, sample app, ref architecture
├─ "How do I get this working?"             → activation: quickstart, runnable demo, workshop
└─ "How do I run this in production?"       → adoption: deep guide, best-practice doc, case study
```

Every artifact ends with an activation path (a next concrete step toward value).

## 4. Onboarding diagnosis — "why don't sign-ups activate?"

```
Find the steepest drop in: sign_up → credential → first_call → first_success
├─ Drop at credential       → friction in key/auth setup; declare it up front, reduce steps
├─ Drop at first_call        → quickstart has hidden steps or undeclared prerequisites
├─ Drop at first_success     → error messages are cryptic or the happy path is fragile
└─ No instrumentation at all → instrument the funnel FIRST; you cannot fix an unmeasured drop
```

## 5. Community funnel — "where is community stuck?"

```
Stage with the worst conversion in: lurker → asker → answerer → contributor → champion
├─ lurker → asker      → psychological safety / unclear where to ask → seed questions, set norms
├─ asker → answerer    → no recognition loop → reward answerers, surface their status
├─ answerer→contributor→ no good-first-issue path → design contribution on-ramps
└─ contributor→champion→ no growth/access → ambassador tier with a real value exchange
```

---

## 2026 capability map (verify before quoting specifics)

- **Developer-journey instrumentation** — product-analytics tools can now tie sign-up → first-success
  events; insist on event-level instrumentation before reporting activation. `[unverified — confirm the team's actual tooling]`
- **AI-assisted onboarding** — LLM "ask the docs" surfaces change the support funnel; treat them as a
  docs-gap sensor, not a replacement for fixing the quickstart. `[unverified — training knowledge]`
- **Community platforms** — Discord/Slack/Discourse remain the common stack; the funnel logic is
  platform-independent. Treat any specific platform feature claim as `[unverified]` until checked.

> Per the core Claim-Grounding protocol, date and verify any pricing-, platform-, or
> tooling-specific claim before it gates a decision.

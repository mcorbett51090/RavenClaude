# Lifecycle Flow — Spec

> Output of `lifecycle-marketing-engineer` / the `lifecycle-and-email` skill. A flow with no trigger,
> no segmentation, no exit/suppression, no deliverability checklist, or no outcome metric is not ready to ship.

## 1. The flow

- **Name:** <e.g. "New-subscriber welcome + nurture">
- **Lifecycle stage:** <acquisition / activation / nurture / conversion / retention / reactivation>
- **Goal (the funnel job):** <what this flow moves the subscriber toward>

## 2. Trigger + entry/exit (it's a flow, not a broadcast)

| Field | Value |
|---|---|
| Trigger (entry criteria) | <the behavior/event that starts it — must be named> |
| Exit criteria | <conversion / unsubscribe / stage change — must be named> |
| Suppression rules | <who is excluded; how cross-flow double-messaging is prevented> |
| Branching | <behavior-based branches, or "linear"> |

## 3. Segmentation

| Segment | Defining data | How it personalizes the flow |
|---|---|---|
| | | |

## 4. Message steps

| # | Timing | Purpose | Content slot (route copy to content-strategist) | Step metric |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

## 5. Deliverability checklist

| Item | In place? |
|---|---|
| SPF / DKIM / DMARC authentication | <yes/no> |
| List hygiene + sunset policy for unengaged | |
| Sender reputation / engagement plan | |
| Seed-list / inbox-placement test | |

## 6. Measurement (outcomes, not opens)

| Metric | Target | Vanity risk flagged |
|---|---|---|
| Inbox placement | | |
| Click-through / conversion | | |
| Engaged-list health | | |
| Revenue per recipient | | <not open rate alone> |

## 7. Build handoff

| What | Routed to |
|---|---|
| The copy in each content slot | `content-strategist` |
| A/B variants (subject / timing / flow) | `experimentation-growth-engineering` |
| Forms / landing pages | `web-design` |
| Attribution + the warehouse | `data-platform` |
| Consent / PII / retention posture | `data-governance-privacy` / `ravenclaude-core/security-reviewer` |

---

```
Status: ...
Files changed: ...
Audience job / intent / funnel stage served: ...
Compounding vs. one-off: ...
Measurement posture: ...
Handoff to build/measurement: ...
Open questions: ...
Grounding checks performed: ...
```

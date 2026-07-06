# Knowledge — Incident lifecycle & severity decision tree

> **Last reviewed:** 2026-07-01 · **Confidence:** High (NIST SP 800-61r2 phases are settled doctrine; the severity matrix is an industry-common impact × scope model — tune the thresholds to the org). **Not legal advice** — notification obligations are a legal call; flag them.
> The `dfir-response-lead` traverses this tree **before** naming a severity or a containment path. The governing question is always business impact × scope, never the alert's tone.

The discipline: **is-it-an-incident? → severity (impact × scope) → containment path** — then run the NIST phases in order. Never jump to eradication before scoping and containing.

---

## Decision Tree: triage → severity → containment

```mermaid
flowchart TD
  Alert([Alert / report arrives]) --> INC{Violation of security policy<br/>or imminent threat of one?}
  INC -->|No — benign| CLOSE[Close as event.<br/>If a noisy rule, route to detection tuning.]
  INC -->|Unsure| SUSPECT[Treat as SUSPECTED incident<br/>— proceed, downgrade later.]
  INC -->|Yes| SCOPE{Impact x scope?}
  SUSPECT --> SCOPE

  SCOPE -->|High impact + wide/crown-jewel| S1[S1 Critical<br/>Full IC activation, exec+legal, 24/7]
  SCOPE -->|High impact, contained| S2[S2 High<br/>IC + on-call, ~hourly cadence]
  SCOPE -->|Medium impact, contained| S3[S3 Medium<br/>SOC analyst + lead, business hours]
  SCOPE -->|Low / suspected| S4[S4 Low<br/>Analyst triage, no activation]

  S1 --> EVID{Live system holding<br/>volatile evidence?}
  S2 --> EVID
  S3 --> EVID
  EVID -->|Yes| CAPTURE[Capture volatile evidence FIRST<br/>memory -> disk, hash, chain of custody]
  EVID -->|No / already off| CONTAIN
  CAPTURE --> CONTAIN{Containment path}

  CONTAIN -->|Stop the bleed now| SHORT[Short-term: isolate host,<br/>disable account, block C2]
  CONTAIN -->|Rebuild clean| LONG[Long-term: clean segment,<br/>rebuild from known-good]
  SHORT --> ERAD[Eradicate root cause<br/>then Recover then Post-incident]
  LONG --> ERAD
```

## The NIST SP 800-61r2 phases (run in order)

```mermaid
flowchart LR
  P[Preparation] --> DA[Detection & Analysis]
  DA --> CER[Containment,<br/>Eradication & Recovery]
  CER --> PI[Post-Incident Activity]
  PI -.lessons feed back.-> P
```

| Phase | Core work | Exit gate |
|---|---|---|
| Preparation | Plan, roster, tools, logs, out-of-band comms, legal contacts | Ready to respond |
| Detection & Analysis | Confirm, scope vector/blast radius, build timeline, map to ATT&CK | Scope known + **volatile evidence captured** |
| Containment / Eradication / Recovery | Stop spread → remove root cause → restore known-good | Adversary confirmed out, systems restored + monitored |
| Post-Incident Activity | Blameless review, root cause, follow-ups | Lessons tracked and fed back |

## Severity matrix (impact × scope)

| | Isolated / single host | Wide / crown-jewel |
|---|---|---|
| **High impact** (exfil, ransomware, integrity loss, regulated data) | S2 | **S1** |
| **Medium impact** (contained malware, policy violation w/ limited exposure) | S3 | S2 |
| **Low / suspected** (blocked phishing, failed exploit) | S4 | S3 |

> Take the **higher** of impact/scope when in doubt. Regulated/personal data in scope escalates and starts the notification clock at *awareness*.

## Provenance
- NIST SP 800-61r2 *Computer Security Incident Handling Guide* (the four-phase lifecycle). Severity model is an industry-common impact × scope classification (adapt thresholds per org). Notification obligations are legal — see [`../best-practices/notification-timelines-are-legal-deadlines-not-guidelines.md`](../best-practices/notification-timelines-are-legal-deadlines-not-guidelines.md). Last reviewed 2026-07-01.
- See also [`forensics-and-evidence-handling.md`](forensics-and-evidence-handling.md) for the evidence-capture gate.

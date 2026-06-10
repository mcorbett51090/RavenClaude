# Sales-engineering engagement decision trees

> _Last reviewed: 2026-06-10._ The decision trees the team traverses **before** choosing an engagement move. Method-before-motion: don't keyword-match "they asked for a demo" → demo; traverse the tree. These encode durable pre-sales craft (MEDDPICC, Great Demo!, standard POC and RFP qualification), not volatile tool facts.

---

## 1. Qualify the deal — what's the right next move?

```mermaid
flowchart TD
  A[Prospect engaged] --> B{Pain discovered<br/>AND quantified?}
  B -->|No| C[Run technical-discovery first<br/>a demo with no pain is a feature tour]
  B -->|Yes| D{Buyer needs to SEE it<br/>resolve their pain?}
  D -->|"Just needs to believe it"| E[Tailored demo<br/>do-it-first, peel back]
  D -->|"Needs to PROVE it on their data/env"| F{POC actually warranted?<br/>go to tree #3}
  F -->|Yes| G[Scope a time-boxed POC<br/>signed success + exit criteria]
  F -->|No| E
  E --> H{Formal procurement<br/>RFP / security review?}
  G --> H
  H -->|RFP/RFI issued| I[Go/no-go → tree #2]
  H -->|Security questionnaire| J[Evidence-mapped answers<br/>see security-questionnaire-and-trust.md]
  H -->|None| K[Drive the mutual action plan to signature]
```

**Leaves:** discovery → demo → (maybe) POC → procurement/security → close. The most common failure is jumping to a **demo with no discovered pain**, or agreeing to a **POC that a tailored demo or reference call would have closed cheaper**.

---

## 2. RFP / RFI go/no-go — should we bid at all?

```mermaid
flowchart TD
  A[RFP / RFI received] --> B{Existing relationship<br/>or champion inside?}
  B -->|No, fully cold| C{Strong product-market fit<br/>to the stated needs?}
  B -->|Yes| D{Requirements fit<br/>our strengths?}
  C -->|No| E[No-bid<br/>free the team for a winnable one]
  C -->|Yes| F{Requirements wired<br/>for an incumbent?<br/>over-specific, single-vendor matches}
  D -->|No| F
  D -->|Yes| F
  F -->|"Yes, clearly wired"| G[No-bid or<br/>bid-to-be-considered-next-time only]
  F -->|No| H{Effort justified by<br/>win probability × deal size?}
  H -->|No| E
  H -->|Yes| I[BID: build the response matrix<br/>thread win themes, run compliance checklist]
```

**The discipline:** a graceful **no-bid** is a strategy, not a failure — the bids you decline fund the ones you win. The trap is the reflexive "respond to every RFP," which burns the team on cold, incumbent-wired, low-probability bids.

---

## 3. Build the POC? — is a proof-of-concept warranted?

```mermaid
flowchart TD
  A[Prospect asks for a POC] --> B{Qualified pain<br/>+ quantified impact?}
  B -->|No| C[Back to discovery<br/>no pain = nothing to prove]
  B -->|Yes| D{A champion who will<br/>drive it internally?}
  D -->|No| E[Don't start<br/>a POC with no champion stalls + dies]
  D -->|Yes| F{Explicit decision criteria<br/>tied to this POC?}
  F -->|No| G[Get criteria first<br/>or the POC never closes]
  F -->|Yes| H{Success is REACHABLE<br/>by our product as it ships?}
  H -->|"No — needs unbuilt features"| I[No-POC<br/>route gap to product-management / honest no]
  H -->|Yes| J{Cheaper alternative<br/>would settle the question?}
  J -->|"Yes: demo / reference / sandbox"| K[Do the cheaper thing first]
  J -->|No| L[RUN THE POC<br/>signed success + exit criteria, time-boxed, scoped]
```

**The gate exists because** a POC is the most expensive sales asset you have. The four preconditions — qualified pain, a champion, explicit decision criteria, and a *reachable* success definition — are all required; missing any one means the cheaper alternative (tailored demo, reference call, guided sandbox) is the better move.

---

## 4. Demo depth — how much to show?

```mermaid
flowchart TD
  A[Demo beat] --> B{Maps to a discovered<br/>pain + its impact?}
  B -->|No| C[CUT IT<br/>illustrate, don't educate]
  B -->|Yes| D{Buyer asked to see<br/>this depth?}
  D -->|No| E[Show the RESULT only<br/>peel back further only if asked]
  D -->|Yes| F[Reveal the next layer<br/>then check in: 'does that match how you'd use it?']
```

**Great Demo! in one tree:** lead with the compelling result, peel back only the layers the buyer asks for, and cut any beat that doesn't tie to a discovered pain. The failure mode is the menu tour ("and here's another tab").

---

## Source discipline

These trees encode **evergreen pre-sales method** (MEDDPICC qualification, Great Demo!'s do-it-first/illustrate-not-educate, standard POC and RFP qualification gates). They carry no volatile tool/version facts, so they don't need a re-verify-at-use rider — unlike anything that names a specific vendor, price, or product version, which must carry a retrieval date per the marketplace freshness discipline.

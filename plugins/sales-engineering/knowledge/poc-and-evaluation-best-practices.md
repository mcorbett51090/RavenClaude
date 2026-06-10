# POC & evaluation best practices

> _Last reviewed: 2026-06-10._ The durable craft of running a proof-of-concept or pilot that produces a clear decision. Evergreen pre-sales method — no volatile tool facts.

---

## The one rule: no POC without signed, measurable success criteria

A POC is a **bounded experiment that settles a decision** — not a free trial, not an unpaid implementation, not "let them play with it." The criteria are the contract. Everything below serves that.

## The four preconditions (the gate)

Before scoping a POC, confirm all four (tree #3 in [`se-engagement-decision-trees.md`](se-engagement-decision-trees.md)):

1. **Qualified, quantified pain** — there's a real problem worth solving, with a business impact.
2. **A champion** who will drive the POC internally and sell the result. POCs with no internal owner stall and die.
3. **Explicit decision criteria** — the prospect has told you what a "yes" looks like and what happens after.
4. **Reachable success** — your product, *as it ships today*, can meet the criteria. If success needs unbuilt features, it's not a POC, it's a roadmap conversation.

Missing any one → a tailored demo, a reference call, or a guided sandbox is the cheaper, better move.

## Writing success criteria

- **3-6 criteria, no more.** More than six and the POC sprawls and nothing is conclusive.
- **Measurable + testable.** "Imports a 1M-row file in under 5 minutes" — not "is fast." "SSO works with the prospect's Okta tenant" — not "integrates well."
- **Tied to a discovered pain.** Each criterion resolves a pain the buyer named. A criterion with no pain behind it is scope you don't need.
- **Owned.** Name who verifies each criterion (often the champion or their engineer).
- **Signed by the champion before kickoff.** Unsigned criteria move the moment results arrive ("well, what we *really* meant was…"). The signature is the forcing function.

## Exit, kill, and extend rules

- **Every criterion gets a pass/fail test.** A POC you can't fail is a POC you can't win — an un-failable criterion proves nothing.
- **A kill rule** — the condition under which the POC ends early (e.g., a hard blocker with no workaround, or the champion goes dark).
- **One extend rule** — the single condition under which you'd add time (resist open-ended extension; that's how a 2-week POC becomes a 2-month freebie).

## Scope and time-box

- **Time-box it.** The deadline is the momentum. A drifting POC cools the deal.
- **In-scope / out-of-scope, explicit.** Name what is **not** being proven — the most important line in the scope, because it's where creep enters.
- **Prerequisites up front:** the data, the environment, the access, the prospect-side people. A POC that waits two weeks for test data has already lost momentum.
- **Milestone checkpoints**, not a silent run to the end. A mid-POC check catches a drifting criterion while there's still time.

## Scoring and converting to a technical win

- **Score criterion-by-criterion: pass / partial / fail** against the signed definitions. No reinterpreting a fail as a pass.
- **Handle a failed criterion honestly** — route it to a documented workaround, a roadmap item (`product-management`), or an honest no. A passed POC built on a fudged criterion detonates in production and costs you the renewal.
- **Produce a technical-win summary** the champion can carry internally to the economic buyer: what was tested, what passed, what the honest caveats are, and the recommended next step (into the mutual action plan).

## Anti-patterns

| Anti-pattern | Why it hurts | The fix |
|---|---|---|
| Open-ended POC, no criteria | Never closes; SE time burned with nothing to show | Signed, measurable criteria before kickoff |
| Un-failable criteria | Proves nothing; "success" is meaningless | A pass/fail test per criterion |
| No champion | Stalls, goes dark, no internal seller | Gate on a champion before starting |
| Scope creep into implementation | Free consulting; deal value leaks | Explicit out-of-scope + one extend rule |
| Spinning a fail as a pass | Detonates in production; kills the renewal | Honest scorecard; route the gap |

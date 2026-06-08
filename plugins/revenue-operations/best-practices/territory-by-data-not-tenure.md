# Territory by data, not tenure

**Status:** Pattern
**Domain:** Territory and account design
**Applies to:** `revenue-operations`

---

## Why this exists

When territory assignment favors seniority over market potential, two problems compound. First,
the organization misallocates coverage: its most experienced reps are on accounts that may have
been the highest potential five years ago but may not be today, while high-potential accounts sit
in territories assigned to junior reps who lack the skills to penetrate them. Second, the practice
embeds a perverse incentive: reps have an incentive to become senior rather than to perform, because
seniority — not performance — is the currency for preferred territory.

The correct criterion for territory assignment is market potential combined with skill-match to
account complexity. A senior rep "deserving" a premium territory because of tenure is a seniority
tax on that account's revenue potential. Every departure from potential-equalized assignment must
be documented with a data-based rationale, not a relationship or a tenure argument.

## How to apply

For every territory or named-account assignment:

1. **Score account potential.** Calculate a potential score for each account: TAM estimate ×
   penetration factor × propensity-to-buy signals (firmographic fit, technographic fit,
   engagement signals, existing product usage). Source the inputs.
2. **Allocate to equalize potential, not account count.** A territory with 20 accounts at $50K
   potential each ($1M total) is equivalent to a territory with 5 accounts at $200K potential
   each ($1M total). Equalize the denominator — total territory potential.
3. **Document departures.** Any assignment that is not potential-equalized requires a written
   rationale in terms of skill-match to account complexity — not tenure, not relationship history.
4. **Run the equity analysis.** Calculate the Gini coefficient of potential distribution across
   reps. A Gini > 0.3 indicates materially unequal territory distribution; address the gaps.
5. **Review annually.** Account potential shifts; company firmographics change; reps leave.
   Territory assignments go stale — review them annually, not once and forever.

**Do:**

- Build a potential-scoring model before the territory assignment meeting, not during it.
- Publish the potential scores so reps can see the methodology behind their assignment.
- Run the equity analysis and share it with leadership — surfacing inequality proactively is
  healthier than having reps discover it.
- Document the rationale for every named-account assignment in the CRM or a territory-design doc.

**Don't:**

- Assign the best accounts to the most senior rep as a reward for tenure — name the skill-match
  rationale instead, or reassign.
- Use "they've always had this territory" as a rationale — that is tenure, not data.
- Run territory design in a spreadsheet that only one person sees — it will be mistrusted.
- Design territories based on rep self-reported preferences without a potential-score floor.

## Edge cases / when the rule does NOT apply

When a senior rep has a deep, multi-year relationship with a specific named account that would
be damaged by a rep change, continuity is a legitimate business rationale — but it is an account-
relationship argument, not a territory-design argument. Document it as "continuity: relationship
value at risk" and reassess at the next cycle. This is the narrow, justified exception, not the
default posture for senior-rep territory design.

## See also

- [`./the-comp-plan-is-the-strategy-design-it-deliberately.md`](./the-comp-plan-is-the-strategy-design-it-deliberately.md)
- [`../skills/comp-and-territory-design/SKILL.md`](../skills/comp-and-territory-design/SKILL.md)
- [`../templates/comp-plan-spec.md`](../templates/comp-plan-spec.md)

## Provenance

Codifies the data-driven territory design principle from RevOps best-practice literature (Forrester,
SiriusDecisions, RevOps Alliance) and aligns with the equity/DEI dimension of territory design
increasingly discussed in enterprise RevOps teams (a Gini-based equity check is a recognized
practice in mature territory-design programs).

---

_Last reviewed: 2026-06-08 by `claude`._

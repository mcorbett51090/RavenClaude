# Write the Definition of Done before the first sprint — do not assume shared understanding

**Status:** Absolute rule
**Domain:** Agile delivery
**Applies to:** `project-management`

---

## Why this exists

"Done" means different things to different people until it is written down and agreed. A developer considers a story done when the code is merged. A QA engineer requires automated tests passing. A business analyst requires acceptance criteria verified with a product owner walk-through. A product owner may also require deployed to the staging environment. A governance-heavy client may also require security sign-off and documentation updated. When the Definition of Done is assumed rather than written, stories get "completed" and immediately reopened, sprint reviews are derailed by scope arguments, and the velocity metric becomes meaningless because done does not mean the same thing sprint to sprint. The DoD is the team's shared quality contract.

## How to apply

Draft the DoD collaboratively at the first sprint planning session or in a dedicated kickoff activity. It lives in one place (a team wiki, the top of the sprint plan, the project handbook) and is referenced at every sprint review.

**Minimum DoD structure:**

```markdown
## Definition of Done — [Project / Team Name]

A story or task is DONE when ALL of the following are true:

### Code / technical
- [ ] Code written and merged to main/release branch via approved PR
- [ ] Automated unit tests pass (coverage ≥ [X]%)
- [ ] Automated integration / regression tests pass
- [ ] No new critical or high-severity security findings (SAST/dependency scan)
- [ ] Deployed to [staging / dev / test environment as appropriate]

### Quality
- [ ] Acceptance criteria from the story verified by [Product Owner / BA]
- [ ] Manual exploratory testing completed for [UI / integration / edge cases]
- [ ] No P1 or P2 defects open against this story

### Documentation
- [ ] In-code documentation / comments updated for any new public API or function
- [ ] User-facing documentation updated if the story changes a user-visible behaviour
- [ ] Runbook / ops documentation updated if the story changes deployment or operations

### Governance [add only if applicable to your engagement]
- [ ] Change management record raised / approved (if policy requires)
- [ ] Data privacy / security review signed off (if story involves PII or security controls)
```

**Definition of Done vs Acceptance Criteria — the distinction matters:**

| | Definition of Done | Acceptance Criteria |
|---|---|---|
| Scope | Applies to every story, every sprint | Specific to the individual story |
| Who owns it | The whole team agrees it | The Product Owner defines it |
| What it tests | Quality and completeness | Functional correctness of this story |
| Changes | Rarely — only by team agreement | With every new story |

**Do:**
- Review the DoD at the sprint retrospective: is it still the right bar? Is any criterion being skipped? Do any criteria need strengthening?
- Make the DoD visible in the team's working environment — not buried in a document that nobody opens.
- Enforce it during sprint reviews: if a story does not meet the DoD, it is not done — it is carried over, not velocity-counted.

**Don't:**
- Let the DoD grow indefinitely with every retrospective — it must remain achievable within normal sprint capacity.
- Allow individual teams or sub-groups to have their own silent DoD that differs from the agreed one.
- Accept partial completion ("it's 80% done — we just need to write the docs") as Done. 80% done = not done.

## Edge cases / when the rule does NOT apply

For discovery / spike work that is intentionally time-boxed and not expected to produce production-quality output, a separate lighter-weight completion criterion is appropriate — agreed in sprint planning. A DoD that requires full production hardening for a throwaway prototype creates the wrong incentives. Spike stories should say explicitly "DONE when: findings are documented and shared with the team" with no code-quality criteria.

## See also
- [`../agents/scrum-master.md`](../agents/scrum-master.md) — sprint ceremonies and quality culture
- [`../skills/sprint-planning/SKILL.md`](../skills/sprint-planning/SKILL.md) — sprint goal, acceptance criteria, and capacity sizing

## Provenance

Codifies `scrum-master`'s quality-gate discipline. The Definition of Done is a first-class concept in the Scrum Guide 2020 (§Definition of Done); the distinction from Acceptance Criteria is standard Scrum practitioner guidance.

---

_Last reviewed: 2026-06-05 by `claude`_

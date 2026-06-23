# Governance — <project>

> Template for `GOVERNANCE.md`. Right-size it: a solo project can skip most of this; a multi-maintainer project needs a written decision process so disputes don't stall the project. Replace every `<placeholder>`.

## Roles & the maintainer ladder

| Role | What they can do | How you reach it |
|---|---|---|
| **Contributor** | Open issues/PRs | Make a contribution |
| **Committer** | Merge approved PRs in <areas> | Sustained quality contributions; nominated by a maintainer |
| **Maintainer** | Triage, release, set direction | Sustained committer track record; consensus of existing maintainers |
| **Steering / lead** | Tie-breaks, trademark, foundation liaison | <as defined> |

Current maintainers are listed in `MAINTAINERS.md` (or the `CODEOWNERS` file).

## Decision-making

- **Default:** lazy consensus — a proposal (issue/PR/RFC) with no sustained objection after <72 hours / 1 week> is accepted.
- **Disagreement:** discussion seeks consensus; if unresolved, a **maintainer vote** decides (simple majority; <lead> breaks ties).
- **Significant changes** (breaking changes, new dependencies, governance changes) require an RFC / design issue and explicit maintainer approval.

## Adding & removing maintainers
- **Add:** nominated by an existing maintainer, approved by <consensus / majority>.
- **Remove / emeritus:** prolonged inactivity (<period>) moves a maintainer to emeritus; voluntary at any time. Publish/credential access is revoked on departure.

## Sustainability
- The release process is documented as a runbook (a `release-checklist.md`) so no single person is a bottleneck.
- Publish credentials and signing keys are held by **at least two** maintainers (bus-factor mitigation).
- Funding channels (if any) are disclosed in `FUNDING.yml`; use of funds is <how decided>.

## Code of Conduct & enforcement
Behavior is governed by the project `CODE_OF_CONDUCT.md`; reports go to <contact> and are handled by <the maintainers / a named committee>.

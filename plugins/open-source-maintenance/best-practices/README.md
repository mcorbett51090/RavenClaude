# Open-source-maintenance — best-practice docs

Named, citable rules for the `open-source-maintenance` plugin's two agents. Each file is **one rule**, grounded in this plugin's knowledge bank and the agents' house opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md)) or the automated smell checks in the advisory hook. They take one opinion each and make it a standalone, exception-documented rule.

---

## Index

_8 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`semver-bump-by-the-change-not-the-feeling.md`](./semver-bump-by-the-change-not-the-feeling.md) | Absolute rule | Deciding major/minor/patch — the bump is set by the change set, not the release's emotional weight. |
| [`changelog-is-for-humans-keep-it-current.md`](./changelog-is-for-humans-keep-it-current.md) | Absolute rule | Writing release notes — group for upgraders, not a commit dump; never ship a bump with no entry. |
| [`license-before-first-public-commit.md`](./license-before-first-public-commit.md) | Absolute rule | Before the first public release — no-license code is all-rights-reserved; retrofitting is messy. |
| [`dco-or-cla-decide-before-contributions.md`](./dco-or-cla-decide-before-contributions.md) | Pattern (strong default) | Before the first outside PR — pick DCO (default) vs CLA (justified) and state it in CONTRIBUTING. |
| [`triage-has-an-sla-and-a-decline-path.md`](./triage-has-an-sla-and-a-decline-path.md) | Pattern (strong default) | Running the backlog — first-response SLA + a graceful decline; silence is the failure mode. |
| [`breaking-changes-need-a-deprecation-window.md`](./breaking-changes-need-a-deprecation-window.md) | Absolute rule | Removing/renaming a public API — warn → window → remove in a major; never yank in a minor. |
| [`security-reports-go-private-first.md`](./security-reports-go-private-first.md) | Absolute rule | A vulnerability arrives — keep it private; release the fix and advisory together. |
| [`bus-factor-is-a-first-class-risk.md`](./bus-factor-is-a-first-class-risk.md) | Pattern (strong default) | Assessing sustainability — one-person dependence is a tracked risk with mitigations. |

# Staging area for incoming contributions

This directory receives **proposed** lessons and best-practice docs from consumer projects that have `ravenclaude-core` installed. Files here are **not canonical** — they're awaiting maintainer review.

```mermaid
flowchart LR
    consumer["<b>Consumer project</b><br/>(ravenclaude-core installed)<br/><br/>Claude uses<br/><code>contribute-finding</code><br/>skill — qualifies, picks<br/>shape + topic, formats"]
    paste["<b>Manual copy-paste</b><br/>User drops the block into<br/><code>docs/staging/incoming/</code>"]
    review["<b>Review session</b><br/>(this repo)<br/><br/><code>/review-staged-contributions</code><br/>walks each file"]
    security["<b>Security sweep</b><br/>pattern scan +<br/><code>security-reviewer</code> agent<br/><br/>Verdict: clean /<br/>caution / BLOCKED"]
    expert["<b>Topic expert analysis</b><br/>routed by <code>topic:</code><br/><br/>Verdict: generalizes /<br/>one-off / unclear"]
    decision{"<b>Maintainer<br/>decides</b><br/>keep · update · deny<br/>(sees submission +<br/>security + expert)"}
    canonical["<b>Canonical location</b><br/><br/><code>lessons-learned.md</code><br/>or<br/><code>best-practices/&lt;slug&gt;.md</code>"]
    deleted["<b>Deleted</b><br/>(git log keeps the trail)"]

    consumer --> paste
    paste --> review
    review --> security
    security -->|clean / caution| expert
    security -->|BLOCKED| decision
    expert --> decision
    decision -->|keep| canonical
    decision -->|deny| deleted
    decision -->|update| paste

    classDef consumer fill:#7c2d12,stroke:#fed7aa,color:#fff7ed
    classDef stage fill:#1f2937,stroke:#9ca3af,color:#f9fafb
    classDef security fill:#991b1b,stroke:#fca5a5,color:#fef2f2
    classDef expert fill:#581c87,stroke:#d8b4fe,color:#faf5ff
    classDef gate fill:#854d0e,stroke:#fde68a,color:#fffbeb
    classDef good fill:#0f766e,stroke:#5eead4,color:#ecfeff
    classDef bad fill:#374151,stroke:#9ca3af,color:#e5e7eb,stroke-dasharray: 4 3
    class consumer consumer
    class paste,review stage
    class security security
    class expert expert
    class decision gate
    class canonical good
    class deleted bad
```

---

## How submissions arrive

**Consumer side.** Claude (with `ravenclaude-core` installed) follows the [`contribute-finding`](../../plugins/ravenclaude-core/skills/contribute-finding.md) skill: qualifies the finding, picks the shape (lesson, best-practice, or both), and prints a copyable `RAVENCLAUDE-STAGING-SUBMISSION` block in canonical format.

**Maintainer side.** Matt (or whoever is reviewing) drops the block into a new file at:

```
docs/staging/incoming/YYYY-MM-DD-<slug>.md
```

The date and slug should match the values inside the submission's metadata. The file *is* the staged content — no wrapping or extra formatting.

---

## How submissions are reviewed

In any Claude session running in this repo with `ravenclaude-core` active, invoke:

```
/review-staged-contributions
```

The skill walks `docs/staging/incoming/` file by file, oldest first. For each one:

1. **Display** the metadata (type, topic, proposed-by, proposed-on, target file) + the rendered body.
2. **Security sweep (mandatory first gate).** An automated pattern scan checks for leaked secrets, unscrubbed real identifiers, prompt-injection signals, dangerous code examples, and non-canonical external URLs. The `security-reviewer` agent reads the submission as a second pass. The verdict is `CLEAN`, `CAUTION`, or `BLOCKED`. A `BLOCKED` verdict short-circuits the rest of the flow — the maintainer sees the security findings and the submission goes straight to keep/update/deny (where keep should require explicit override reasoning). Details in [`review-staged-contributions.md`](../../plugins/ravenclaude-core/skills/review-staged-contributions.md) Step 2.3.
3. **Route by topic** (only if security verdict is CLEAN or CAUTION). The `topic:` field in the metadata picks the expert specialist agent — `architecture` → ravenclaude-core/architect, `power-platform` → the best-fit power-platform specialist, `security` → security-reviewer, and so on. The full routing table lives in [`review-staged-contributions.md`](../../plugins/ravenclaude-core/skills/review-staged-contributions.md) Step 2.5.
4. **Spawn the expert.** The expert reads the submission and returns a structured analysis: *generalizes / one-off / unclear*, with reasoning, missed edge cases, recommended adjustments, and a confidence level.
5. **Present to the maintainer.** The keep/update/deny prompt shows the submission, the security verdict + findings, AND the expert's verdict side by side.
6. **Act on the decision:**

| Choice | What happens |
|---|---|
| **Keep** | Body promoted to canonical home (`docs/memory-bank/lessons-learned.md` for lessons, new file at `docs/best-practices/<slug>.md` for best-practices, plus a row appended to the best-practices index). The staged file is deleted. For lessons, the count in `docs/architecture.md` is bumped. Commit: `docs(...): promote staged ... (expert: <verdict>, <confidence>)` |
| **Update** | Staged file stays in `incoming/`. The maintainer revises it (or directs Claude to revise based on the expert's edge cases), then re-runs the review. No commit. |
| **Deny** | Staged file is deleted with a one-line reason in the commit. If the deny was driven by the expert's verdict, the expert's reasoning is quoted in the message. Commit: `chore(staging): deny <filename> — <reason>` |

The expert's analysis is **ephemeral** — it informs the decision but isn't saved to a file unless the maintainer explicitly asks to append it. The git commit on promote captures the verdict + confidence so future-anyone can see the staffing of the decision without re-spawning the agent.

The git history is the audit trail — every accept and deny shows up in `git log docs/staging/`.

---

## File shape

Every file in `incoming/` opens with a metadata block as an HTML comment, then the proposed content in its final canonical shape (so promotion is a content-move, not a rewrite):

```html
<!-- RAVENCLAUDE-STAGING-METADATA
type: lesson | best-practice
topic: <architecture | backend | frontend | fullstack | testing | code-review | security | research | documentation | design | prompt-engineering | project-management | partner-success | power-platform | other>
proposed-by: <short context — e.g. "consumer project working on Flow retries">
proposed-on: YYYY-MM-DD
target-file: docs/memory-bank/lessons-learned.md  (or)  docs/best-practices/<slug>.md
status: pending
-->
```

The `topic:` field is what routes the submission to the right expert agent during review. If you're authoring a submission by hand (not via the `contribute-finding` skill), pick the topic whose specialist should weigh in.

If a finding produces both a lesson AND a best-practice, expect **two staged files** — they promote independently and cross-link on the maintainer side.

---

## What goes here vs. what doesn't

✅ **Cross-domain findings** — rules or stories that apply to any Claude work, any plugin, any project.

❌ **Domain-specific findings** — Power Platform / finance / EdTech / Salesforce specifics belong inside the relevant plugin's `skills/<skill>/resources/` folder, not in cross-domain `docs/`.

❌ **Personal preferences** — editor configs, individual working-style quirks. Those go in consumer-side personal memory at `~/.claude/projects/.../memory/`.

❌ **Project-specific incident reports** — if it's only useful to one consumer project, it stays in that project's repo, not here.

The [`contribute-finding`](../../plugins/ravenclaude-core/skills/contribute-finding.md) skill enforces these checks on the consumer side. If something does slip through, deny it.

---

## See also

- [`contribute-finding`](../../plugins/ravenclaude-core/skills/contribute-finding.md) — consumer-side authoring playbook
- [`review-staged-contributions`](../../plugins/ravenclaude-core/skills/review-staged-contributions.md) — maintainer-side review playbook
- [`lessons-vs-best-practices`](../best-practices/lessons-vs-best-practices.md) — meta-process for deciding whether a finding is a lesson, a best-practice, or both
- [`pr-vs-direct-push`](../best-practices/pr-vs-direct-push.md) — when to push promoted submissions to main directly vs open a PR
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — the alternative flow for contributors with direct write access to this repo (PR-based, no staging step)

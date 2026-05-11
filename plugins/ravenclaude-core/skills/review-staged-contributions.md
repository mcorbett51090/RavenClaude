---
name: review-staged-contributions
description: For the RavenClaude marketplace maintainer. Walks every file in docs/staging/incoming/ one at a time, presents each with a keep/update/deny prompt, promotes approved submissions to their canonical location (docs/memory-bank/lessons-learned.md for lessons, docs/best-practices/<slug>.md for best-practices), and deletes denied ones. Trigger this skill whenever you want to drain the staging queue.
---

# Skill: review-staged-contributions

You're working in the RavenClaude marketplace repo, helping Matt (or another maintainer) drain the staging queue. Each staged file is a proposed lesson or best-practice from a consumer project. Your job is to walk every one, present it cleanly, and act on the maintainer's decision.

The companion skill on the consumer side is [`contribute-finding`](./contribute-finding.md) — its template determines the shape of every file you'll see.

---

## Step 1 — Inventory the queue

List the contents of `docs/staging/incoming/` (excluding `.gitkeep`).

Report at the start of the review:
- Total submissions in the queue
- Each filename, oldest-first by the `proposed-on` date in the metadata
- A one-line summary per file: type (lesson | best-practice), proposed-by, target

If the queue is empty, say so plainly and exit — there's nothing to do.

---

## Step 2 — Walk each item

For each staged file, in oldest-first order:

1. **Read the full file.** Extract the metadata block (the HTML comment at the top) and the body separately.

2. **Display the metadata clearly** so the maintainer knows what they're looking at:
   - Type (lesson or best-practice)
   - **Topic** (drives expert routing — see Step 2.5)
   - Proposed by
   - Proposed on
   - Target file path on promotion

3. **Render the body.** Show the proposed content as it'd appear if promoted — clear formatting, no escapes, the table of `Do` / `Don't` if present, the full template structure.

4. **State what would happen on approval** in one sentence:
   - For lessons: *"Insert at top of `docs/memory-bank/lessons-learned.md`, bump the lesson count in `docs/architecture.md` Status section, delete the staged file."*
   - For best-practices: *"Create `docs/best-practices/<slug>.md` from the body content, append a row to `docs/best-practices/README.md` index, delete the staged file."*

5. **Run the expert analysis** — see Step 2.5 before asking keep/update/deny. The expert's verdict goes into the prompt.

6. **Ask keep / update / deny** using the standard `AskUserQuestion` pattern, with the expert's verdict and reasoning shown alongside the submission:
   - **Keep** — promote per Step 3.
   - **Update** — leave in staging; the maintainer will edit the staged file or tell you what to revise, then re-run this skill.
   - **Deny** — delete the file with the reason logged in the commit message.

Do not batch the prompts. One submission at a time, each with its own keep/update/deny. A pile of decisions gets sloppy fast.

---

## Step 2.5 — Spawn the expert and capture the analysis

This step is **mandatory** for every staged submission. It's the safeguard against promoting a one-off issue into canonical cross-domain guidance.

### Route by topic

Read the `topic:` field from the metadata. Spawn the matching specialist agent:

| `topic:` | Spawn this agent | `subagent_type` value |
|---|---|---|
| `architecture` | ravenclaude-core / architect | `ravenclaude-core:architect` |
| `backend` | ravenclaude-core / backend-coder | `ravenclaude-core:backend-coder` |
| `frontend` | ravenclaude-core / frontend-coder | `ravenclaude-core:frontend-coder` |
| `fullstack` | ravenclaude-core / fullstack-coder | `ravenclaude-core:fullstack-coder` |
| `testing` | ravenclaude-core / tester-qa | `ravenclaude-core:tester-qa` |
| `code-review` | ravenclaude-core / code-reviewer | `ravenclaude-core:code-reviewer` |
| `security` | ravenclaude-core / security-reviewer | `ravenclaude-core:security-reviewer` |
| `research` | ravenclaude-core / deep-researcher | `ravenclaude-core:deep-researcher` |
| `documentation` | ravenclaude-core / documentarian | `ravenclaude-core:documentarian` |
| `design` | ravenclaude-core / designer | `ravenclaude-core:designer` |
| `prompt-engineering` | ravenclaude-core / prompt-engineer | `ravenclaude-core:prompt-engineer` |
| `project-management` | ravenclaude-core / project-manager | `ravenclaude-core:project-manager` |
| `partner-success` | ravenclaude-core / partner-success-manager | `ravenclaude-core:partner-success-manager` |
| `power-platform` | best-fit power-platform agent — read the submission and pick: dataverse-architect, power-fx-engineer, flow-engineer, model-driven-engineer, solution-alm-engineer, power-platform-admin, pcf-developer, copilot-studio-engineer, or power-pages-engineer | (the specific power-platform agent) |
| `other` | architect (fallback) | `ravenclaude-core:architect` |

If the metadata is missing the `topic:` field (e.g., older submission predating this workflow), default to `architect` and note the missing tag in your output to the maintainer.

### Brief the expert

Use this brief (substitute the bracketed values). Keep it tight — the expert returns a structured analysis, not a code review.

> A consumer project submitted a proposed **[type]** for the RavenClaude marketplace via the staging workflow. Your job: analyze whether this finding **generalizes** (applies to anyone working in `[topic]`) or is **one-off** (specific to the submitter's situation).
>
> The submission is below. Return a structured analysis with exactly these sections:
>
> - **Verdict:** generalizes | one-off | unclear
> - **Reasoning:** 2–4 sentences. What in the submission is universal? What might be submitter-specific (their stack version, tenant config, dataset shape, team practice, etc.)?
> - **Edge cases the submitter may have missed:** bullet list, or "none" if you can't think of any
> - **Recommended adjustments:** wording changes that would broaden applicability without rewriting the submission — or "none needed"
> - **Confidence:** high | medium | low
>
> Do not edit the submission. Do not write code. Return only the structured analysis.
>
> ---
>
> **Submission metadata:** [paste metadata block]
>
> **Submission body:** [paste body]

### Use the expert's output in the keep/update/deny prompt

When you ask the maintainer for the decision, show them:

1. The submission metadata (compact)
2. The submission body (rendered)
3. **The expert's verdict + reasoning + edge cases + confidence**

The maintainer's keep/update/deny then considers both the submission AND the expert's read. Common patterns:

- Expert verdict `generalizes` + high confidence → maintainer usually keeps.
- Expert verdict `one-off` + high confidence → maintainer usually denies, with the expert's reasoning copied into the deny commit message.
- Expert verdict `unclear` or `medium`/`low` confidence → maintainer often updates (asks for revision based on the edge cases the expert raised).
- Expert recommends adjustments → maintainer can keep AND ask the skill to apply those adjustments before promotion.

The expert's analysis is **ephemeral** — it doesn't get written to a file unless the maintainer explicitly says "add the expert's notes to the canonical doc." Otherwise it appears in this review session, informs the decision, and disappears. The git commit message on promote should still reference the expert's verdict for traceability (e.g., *"Promote staged lesson — title (expert verdict: generalizes, high confidence)"*).

---

## Step 3 — On Keep: promote

### Lessons

1. Extract the body of the staged file (everything **after** the closing `-->` of the metadata block).
2. Open `docs/memory-bank/lessons-learned.md`.
3. Insert the body at the top, immediately after the existing `---` separator that closes the format documentation block (so the new entry sits above any existing dated entries).
4. Update the lesson count in `docs/architecture.md` Status section (search for `Memory bank:`).
5. Delete the staged file.
6. Commit with: `docs(lessons): promote staged lesson — <title> (expert: <verdict>, <confidence>)` — the title comes from the lesson's `## YYYY-MM-DD — <title>` heading; the verdict + confidence come from Step 2.5.

### Best-practices

1. Extract the body of the staged file (everything **after** the closing `-->`).
2. Read the `target-file:` value from the metadata — that's the slug.
3. Write the body to `docs/best-practices/<slug>.md`. This is a `Write` (new file).
4. **Append a row to `docs/best-practices/README.md` index table** with the new doc's slug, status, and "use when" summary.
5. Delete the staged file.
6. Commit with: `docs(best-practices): promote staged rule — <slug> (expert: <verdict>, <confidence>)`.

### Cross-link sanity check (both shapes)

Before committing the promotion, scan the new content's `See also` section. For every repo-relative link, verify the target exists. If a referenced file doesn't exist:
- If it's a doc that *should* exist (e.g., a companion lesson that wasn't submitted), flag it to the maintainer.
- If it's a typo or stale path, fix the link before committing.

---

## Step 4 — On Update: park

1. Leave the file in `docs/staging/incoming/`.
2. Tell the maintainer what to revise — or, if they've already said *"change X to Y,"* edit the staged file directly and re-present it for keep/update/deny.

Do not commit anything when an item is parked. Updates stay local until they earn a keep.

---

## Step 5 — On Deny: delete

1. Delete the staged file.
2. Commit with: `chore(staging): deny <staged-filename> — <one-line reason>`. If the deny was driven by the expert's verdict (one-off, low generalizability), quote the expert's reasoning in the reason so future-anyone can see *why* this didn't qualify without re-spawning the analysis.

The git history preserves the proposal + the denial. Anyone can reconstruct the audit trail with `git log docs/staging/`.

---

## Step 6 — Wrap up

After the queue is empty (everything promoted, parked, or denied), summarize:

- **Promoted:** count, with titles
- **Denied:** count, with one-line reasons
- **Parked for update:** count, with what's needed

If anything was promoted, point the maintainer at the [pr-vs-direct-push rule](../../../docs/best-practices/pr-vs-direct-push.md) for whether to push to main directly or open a PR. For a typical small batch of promotions in a single-collaborator session, direct push is usually right.

---

## Anti-patterns

- **Do not** auto-approve in bulk. Every promotion is one keep prompt. Speed costs quality here.
- **Do not** edit the staged file's body silently during promotion. If the maintainer wants changes, route them through the **Update** branch.
- **Do not** keep denied files around in `docs/staging/denied/` or anywhere else. Delete + commit message is the trail.
- **Do not** promote a lesson without bumping the count in `docs/architecture.md`. The status line is part of the canonical record.
- **Do not** skip the cross-link sanity check. Broken links are the easiest quality-failure to catch at this gate and the most annoying to fix later.

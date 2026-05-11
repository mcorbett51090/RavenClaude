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
   - Proposed by
   - Proposed on
   - Target file path on promotion

3. **Render the body.** Show the proposed content as it'd appear if promoted — clear formatting, no escapes, the table of `Do` / `Don't` if present, the full template structure.

4. **State what would happen on approval** in one sentence:
   - For lessons: *"Insert at top of `docs/memory-bank/lessons-learned.md`, bump the lesson count in `docs/architecture.md` Status section, delete the staged file."*
   - For best-practices: *"Create `docs/best-practices/<slug>.md` from the body content, delete the staged file."*

5. **Ask keep / update / deny** using the standard `AskUserQuestion` pattern:
   - **Keep** — promote per Step 3.
   - **Update** — leave in staging; the maintainer will edit the staged file or tell you what to revise, then re-run this skill.
   - **Deny** — delete the file with the reason logged in the commit message.

Do not batch the prompts. One submission at a time, each with its own keep/update/deny. A pile of decisions gets sloppy fast.

---

## Step 3 — On Keep: promote

### Lessons

1. Extract the body of the staged file (everything **after** the closing `-->` of the metadata block).
2. Open `docs/memory-bank/lessons-learned.md`.
3. Insert the body at the top, immediately after the existing `---` separator that closes the format documentation block (so the new entry sits above any existing dated entries).
4. Update the lesson count in `docs/architecture.md` Status section (search for `Memory bank:`).
5. Delete the staged file.
6. Commit with: `docs(lessons): promote staged lesson — <title>` (the title comes from the lesson's `## YYYY-MM-DD — <title>` heading).

### Best-practices

1. Extract the body of the staged file (everything **after** the closing `-->`).
2. Read the `target-file:` value from the metadata — that's the slug.
3. Write the body to `docs/best-practices/<slug>.md`. This is a `Write` (new file).
4. Delete the staged file.
5. Commit with: `docs(best-practices): promote staged rule — <slug>`.

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
2. Commit with: `chore(staging): deny <staged-filename> — <one-line reason>`. The reason should be specific enough that future-anyone can understand it without re-reading the deleted file.

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

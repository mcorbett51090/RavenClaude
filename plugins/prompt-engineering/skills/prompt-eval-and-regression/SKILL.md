---
name: prompt-eval-and-regression
description: "Build the eval/regression set that gates prompt changes — labeled input/expected pairs over the hard cases, a scoring method (exact / schema-valid / rubric / LLM-judge with its caveat), a pass threshold, a CI gate with the model pinned, and injection cases. Reach for this before shipping a prompt, when a tweak silently broke other cases, or to defend against prompt injection. Pairs with structured-output-design."
---

# Skill: Prompt eval & regression

Turn "it worked when I tried it" into "it is verified to still work." A prompt is
**unverified until the regression set is green.**

## Step 0 — One opinion up front
**Prompts are code.** They live in version control, change in reviewable diffs, and
must pass an eval before merge — exactly like any other code.

## Step 1 — Build the regression set
Collect labeled `input → expected` pairs covering:
- The **known-hard/edge cases**.
- **Every past failure** (each production bug becomes a permanent test).
- **Injection/jailbreak cases** (see §4 of the decision-trees doc).
Keep it in the repo next to the prompt.

## Step 2 — Choose a scoring method
Match the method to the task:
- **Exact / schema-valid** — closed-form or structured tasks. Cheapest, most
  reproducible; prefer it wherever possible.
- **Rubric** — explicit criteria, human or model graded.
- **LLM-as-judge** — scalable but the judge is a fallible prompt. **Judge the
  judge:** validate against human labels first; never let a model grade its own
  output unaudited; watch for position/verbosity/self-preference bias.
Set a **pass threshold** a change must clear.

## Step 3 — Pin for reproducibility
Pin the **model + version + temperature (+ seed where available)**. Handle
nondeterminism: temperature 0 where the task allows; multiple samples + a tolerance
where it doesn't. An eval against an unpinned model proves nothing tomorrow.

## Step 4 — Wire the CI gate
Run the regression set on every change to a prompt file; **fail the build on a
regression.** State honestly what the set does and doesn't cover — a green gate
over a thin set is false safety.

## Step 5 — Version & roll out
Prompts carry a version (semver or content hash). Roll changes out shadow → canary
→ full, with a watched metric and a rollback trigger.

## Step 6 — Hand off
- The **large offline eval program / benchmark design** → `llm-evaluation-engineering`.
- **Adversarial attacks on the running system** → `ai-red-teaming`.
- The **fix** for what the evals catch → `prompt-implementation-engineer` / `prompt-architect`.

## Output
A regression set + scoring method + threshold, a CI gate with the model pinned,
injection cases included, an honest coverage statement, and a versioning + canary
rollout plan.

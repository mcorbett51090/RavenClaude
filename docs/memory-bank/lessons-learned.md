# Lessons Learned

> Running log of trial-and-error findings from work that touches the domains this hub covers. **Newest entries at the top.** Read this file at the start of any task touching a covered domain — the "we already learned this" cycle is what makes the hub valuable.

## Format

Each entry is a dated section. Reverse-chronological order (newest first).

```markdown
## YYYY-MM-DD — Short title naming the rule or finding

**Context:** What we were trying to do. 1–2 sentences.

**What we tried first:** The path that failed. 1–2 sentences.

**Why it failed:** The actual reason, with technical detail. 2–4 sentences.

**What works:** The canonical solution. 2–4 sentences.

**How to apply:** When this rule fires, what to do. 1–2 bullet points.

**Trace:** Origin project, origin session ID if useful. Optional.
```

---

## 2026-05-21 — A step that runs is not necessarily a step that gates: audit every CI check with a known-bad fixture

**Context:** Round-6 of the marketplace's self-review chain. PR 9/10 had added `rhysd/actionlint:1.7.7` as a Docker container action in `validate-marketplace.yml`. CI on commit `de21250` passed. Score moved to 91/100 (architect) / 87/100 (Team Lead) with "Test/verification depth = 10/10" specifically credited to the new actionlint step.

**What we tried first:** Treated `CI green` as proof of `CI correct`. The actionlint step ran, found nothing wrong with the repo, exited 0. Score went up. Plan agent and architect declared "internal review done."

**Why it failed:** A researcher dispatched to verify the CI behavior empirically returned a sharp finding: actionlint 1.7.7 has **no `-exit-code` flag**. By design it reports findings via stdout/stderr (which surface as PR annotations) but exits 0 regardless. I ran the sanity probe: injected a real YAML parse error, actionlint correctly reported it, then **exited 0**. The CI step that scored us a 10/10 was informational-only — it could never fail a build. Score retroactively corrected: R5 was actually 90, not 91. The Plan agent then identified the meta-pattern: *verification artifacts are being graded on presence, not efficacy.*

**What works:** Two interlocking practices.

1. **Shell-wrap any linter that doesn't exit nonzero on findings.** Replace `uses: docker://...` with a `run:` block that captures the binary's output and converts non-empty output into `exit 1`. Pattern:

   ```yaml
   run: |
     set -euo pipefail
     out=$(docker run --rm -v "$PWD:/repo" -w /repo <image>:<tag> -color 2>&1) || rc=$?
     rc=${rc:-0}
     echo "$out"
     if [[ -n "$out" ]]; then echo "::error::<name> reported findings"; exit 1; fi
   ```

   Keeps the pinned image (supply chain), keeps annotations, turns findings into a failing build.

2. **Audit every gate with a known-bad fixture.** For each CI step that claims to enforce a property, write a one-line repro that violates that property and confirm the step fails. Don't trust "green CI" until each gate has produced a red CI on its target violation class. In RavenClaude this is a 10-gate / ~5-minute exercise; the result is that "test/verification depth = N/10" becomes a defensible claim instead of a hopeful one.

**How to apply:**
- When a CI step uses a third-party action or binary, check its exit-code semantics before counting it as a gate. Common offenders: linters with `--report-only` defaults, security scanners that print but don't fail, custom scripts that `|| true` for "robustness."
- Before declaring a CI workflow "robust", run the audit-by-known-bad-fixture exercise. The script lives in `.github/workflows/validate-marketplace.yml` execution logs as the proof artifact — keep at least one CI run where each gate is exercised against a fixture that should trip it.
- The vague principle "a step that runs is not necessarily a step that gates" has a sharper actionable form: **"For every CI step, prove it can fail by introducing a known-bad input."**

**Trace:** Commit history `cfbd5aa..PR13` in RavenClaude. PR 9/10 shipped the informational-only actionlint step. PR 12's shell-wrapper attempted to fix it but introduced its own bug — captured docker's image-pull stderr via `2>&1` and false-positive-tripped on a fresh CI runner. PR 13 fixed PR 12 by separating concerns (pre-pull image silently, capture only actionlint's stdout). Both failure modes — paper-tiger gate AND gate that gates the wrong thing — were caught by the same audit-by-fixture practice. **Corollary worth keeping in mind:** "a step that runs is not necessarily a step that gates" has a twin — "a step that gates can gate the wrong thing." The same fixture-pair exercise catches both. Codified as a runnable script at [`scripts/audit-gates.sh`](../../scripts/audit-gates.sh) and a canonical rule at [`docs/best-practices/ci-gate-audit.md`](../best-practices/ci-gate-audit.md); the audit script itself runs in CI as a meta-gate so any future regression in any gate's behavior gets caught at the next PR.

---

## 2026-05-11 — Rebase orphans local branches; `git branch -D` is the routine cleanup, not a destructive act

**Context:** PR #1 (`propose-lesson-diagrams-in-docs`) merged on GitHub with only the first commit. The inline-mermaid-demo commit was pushed to the feature branch *after* the PR merged, so local `main` and `origin/main` diverged by one commit each. After rebasing local onto origin and pushing, the original feature branch needed to be deleted locally.

**What we tried first:** `git branch -d propose-lesson-diagrams-in-docs` — the safe-delete that refuses if the branch isn't merged.

**Why it failed:** Safe-delete checks by **SHA reachability**, not content. The rebase replayed `d5ccc5b` as `cd496e0`, so the demo commit's content was on `main` but the original SHA was orphaned. Git's safety check correctly refused. The real problem was downstream: we'd added `Bash(git branch -D:*)` to both the project deny list AND the `guard-destructive.sh` PreToolUse hook, treating force-delete as inherently destructive — even after the user explicitly approved it, the hook double-blocked the command.

**What works:** `git branch -D` is the **correct** operation after any rebase that moved your local commits. It's not destructive in practice: the commits remain in `git reflog` for ~90 days, and (in this case) their content was already on `main` under a new SHA. The destructive layer of git is *reflog clearing* (`git reflog expire --expire=now --all && git gc --prune=now`), which is hard to do accidentally. Removed `git branch -D` from the project deny list and the hook deny patterns. Genuinely destructive operations stay blocked: `rm -rf /`, `git push --force`, `git reset --hard origin`, `git clean -fd`.

**How to apply:**
- After any rebase that moved local commits onto a new base, the original branch ref is orphaned — use `git branch -D <branch>` to clean it up. `-d` will refuse and the refusal isn't informative.
- Don't blanket-deny `git branch -D` in agent tooling. Reserve hook-level denials for commands that can actually destroy work (force-push to a remote, hard reset to a remote ref, `clean -fd`).
- Before reaching for `-D`, sanity-check the content is reachable elsewhere — `git log <branch>..main` should be empty when the rebased commits are on `main`. If it's not, the branch has work that isn't yet anywhere else.

**Trace:** Driven by today's PR #1 rebase reconciliation and subsequent `chore/apply-mermaid-lesson` cleanup. Codified in commit `f0d58d1` (ravenclaude-core 0.1.0 → 0.1.1) which removed `git branch -D` from the project deny list and `guard-destructive.sh`.

---

## 2026-05-11 — Mermaid for conceptual diagrams in markdown; ASCII only for folder trees

**Context:** Refreshing `docs/architecture.md` from the old central-hub + Expert-repos model to the plugin-marketplace model. The original doc used ASCII box-art diagrams (`┌──┐`, `└──┘`, etc.) and I had to decide whether to preserve that style or upgrade.

**What we tried first:** Kept the ASCII box-art format on the reasoning that "the rest of your docs use plain markdown and switching here would introduce a tooling dependency for one file." Flagged the choice as a judgment call I'd defer to Matt on.

**Why it failed:** GitHub renders `mermaid` code fences natively in markdown — no tooling dependency exists for the *reader*. The only "tooling" is the author learning mermaid syntax, which is shallow. ASCII box-art looks fine in a monospace editor and looks ragged in GitHub's web UI. For a repo whose primary collaborator access path is the GitHub web UI (per `docs/access.md`), defaulting to ASCII is the wrong tradeoff.

**What works:** **Use `mermaid` code fences for any conceptual or flow diagram** (system architecture, dispatch patterns, sequence diagrams, ER diagrams, state machines). **Keep folder trees as fenced code blocks** using the standard `├──` / `└──` characters — mermaid has no clean file-tree type and tree characters in monospace read fine. The architecture doc's marketplace diagram is the canonical example of the good shape (a `flowchart TB` with subgraphs for marketplace/plugins/consumer, plus `classDef` color coding).

**How to apply:**
- For new diagrams in any markdown doc, reach for `mermaid` first.
- Pick the diagram type that fits the content (`flowchart`, `sequenceDiagram`, `erDiagram`, `classDiagram`, `stateDiagram-v2`) instead of defaulting to `flowchart`.
- For file/folder trees, keep using fenced code blocks — don't try to coerce them into mermaid.
- See [`docs/best-practices/diagrams-in-docs.md`](../best-practices/diagrams-in-docs.md) for the full rule, including the "when to deviate" exceptions (e.g. agent prompt files read by Claude itself rather than viewed on GitHub).

**Trace:** Driven by Matt's directive ("I want the mermaid diagram") on 2026-05-11 during the lessons-loop scaffolding work. Codified in `docs/best-practices/diagrams-in-docs.md` and in personal memory under `feedback_diagrams.md`.

---

## 2026-05-07 — PSM discipline = quarterly QBR + per-partner success plan + visible health score (with EdTech overlay)

**Context:** Designed a `partner-success-manager` agent for an EdTech Partner Success Manager (communication / translation / rostering) who is also her team's AI champion.

**What we tried first:** A generic Partner Success Manager agent design with the standard PSM artifacts (profile, success plan, QBR, health, onboarding, touchpoints).

**Why it would have fallen short:** The generic version missed three context dimensions that turned out to dominate the role's reality: (1) **EdTech school-year cadence** — rostering crunch, EOY data, renewal cycles all map to the academic calendar, not Q1/Q2/Q3/Q4; (2) the user's **high-touch support background** — her instinct to invest time in upfront enablement to prevent downstream tickets is well-supported in PSM literature and should be reinforced, not flattened into a generic onboarding checklist; (3) her unique team responsibility as **AI champion** — every useful interaction with the agent is a candidate for a team-shared workflow library, not a one-off win.

**What works:** The PSM discipline rule is parallel to the PMP version: **quarterly QBR cadence + per-partner success plan + visible health scoring**. Plus three context overlays:
- **EdTech school-year awareness** baked into the onboarding checklist, success-plan milestones, and QBR prompts.
- **High-touch DNA reinforcement** in the onboarding flow (proactive demos, district IT alignment, integration validation up front).
- An **AI workflow library** that grows organically as useful patterns surface, with the agent prompting *"should this become a library entry?"* when it produces something reusable.

**How to apply:**
- For any role-design ask, hunt for the **discipline rule** first — the cadence + ownership + format triad that separates real practice from theater. PMP and PSM both have it; other roles likely do too.
- When the role lives in a specific industry (EdTech, healthcare, financial services), bake the industry's **calendar / cadence** into the templates, not just the agent description.
- When the user is the **AI champion** for their team, make the agent transparent about *how* it does things, so the user can replicate and teach the move. Treat agent interactions as training data for the team.
- A high-touch / proactive-setup philosophy is a real strength in PSM work — design for it explicitly, don't flatten it.

**Trace:** Researched 2026-05-07 against SaasPedia, Impartner, PartnerStack, PARTNERNOMICS, TSIA, and Gainsight QBR resources. Driven by Matt's request for an agent for his wife (new EdTech PSM, AI champion). Implemented in `.claude/agents/partner-success-manager.md` and 7 templates under `templates/partner-success/`.

---

## 2026-05-07 — PMP discipline = weekly cadence + single ownership + same format

**Context:** Building a PMP-grade `project-manager` agent for cross-domain consulting work.

**What we tried first:** An initial draft of a generic *"Tracker"* agent that maintained activity log, task list, and project tracker — useful but vague. No specific cadence, no ownership rules, no format constraints.

**Why it failed (would have failed in practice):** Without specific operational rules, *"tracking"* tools accumulate dust. A tool that's optional gets skipped; a tool that's vague gets gamed. The reason most consultants are *"not good at PM"* isn't laziness — it's that they have tracking artifacts but no enforcement around them.

**What works:** PMI's PMBOK 7 + the leading PM literature converges on three operational rules that make PM real:

1. **Weekly review cadence**, never skipped — when missed, the agent prompts.
2. **Single owner per item** — every RAID entry, every task, exactly one named person. No *"the team,"* no *"TBD."*
3. **Same format every time** — consistency is what makes status reports trusted.

Plus PMI's 7-element status report (overall status / timeline / achievements / upcoming milestones / active risks / budget / decisions needed) capped at ≤1 page.

**How to apply:**
- When building any tracking tool, agent, or skill: bake in the cadence + ownership + format rules. Don't make them optional.
- For consulting status reports: PMI's 7-element format, ≤1 page, every week.
- For RAID logs: weekly minimum review, immediate logging for critical items.
- For task lists: stale items (>7 days no update) flagged automatically; single owner enforced.

**Trace:** Researched 2026-05-07 against PMI's PMBOK 7 standard plus ProjectManagement.com / Asana / MPUG sources. Driven by Matt's request for a PMP-grade PM agent. Implemented in `.claude/agents/project-manager.md` and 5 templates under `templates/` (raid-log, task-list, status-report, activity-log, stakeholder-register).

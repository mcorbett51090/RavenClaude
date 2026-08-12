# Decision record — GitHub gold-standard gap closure (FORGE `github-gold-standard`)

**Date:** 2026-08-12 · **Run:** `.ravenclaude/runs/forge/github-gold-standard/` · **Landed to:** `forge/github-gold-standard` worktree, target PR into `main`.

## 0. Status at merge (authoritative — supersedes the mid-flight snapshot in Sections 2–6)

All nine phases + the P10 review-fixes + the remote-PR runbook are **committed** on `forge/github-gold-standard`.
**Zero P0–P3 remaining:** the security review was CLEAR; the code review's single P0 (the new hook's
executable bit) was resolved by the maintainer running a `!`-prefixed `chmod +x` — the command-review
tribunal guards the executable-bit operation on its own plugin substrate with no exemption, so it is the
one step an agent cannot take here (verified this session: `git diff --summary` showed
`mode change 100644 => 100755` on the hook), and it was not disguised around. All four P3 findings are
fixed. Full `audit-gates.sh` suite is **716 pass / 0 fail / 0 skip** (verified this session by the
reconciliation run); version-mirror **0.246.0** (plugin.json + marketplace.json + copilot mirror).
Re-measured net: **7 of 8 gaps CLOSED, 1 (SBOM/provenance) DEFERRED-with-pointer** by deliberate design.
The per-row "staged / uncommitted / PARTIAL / P0-open" language in Sections 2–6 describes the worktree at
the moment this record was drafted and is retained as an honest audit trail; it is fully superseded here.

## 1. Summary

RavenClaude guarded *itself* richly but shipped only a fraction of that protection to consumers — a
**ship/no-ship asymmetry**. The sharpest instance: `guard-destructive` ships and hard-blocks a branch
force-delete (`branch -D`) in every consumer install, but its sanctioned recovery scripts lived only at
the marketplace root and never shipped — a consumer hit the block with no working escape. This arc closed
that asymmetry across eight surveyed gaps (branch-delete recovery, Actions hardening, consumer CI,
in-loop protocol enforcement, remote-PR capability, branch protection, release/supply-chain, and
"best-of-the-best" capability), added the agent-facing in-loop nudge that was previously zero, and shipped
the two elite-operator capability assets the repo had earned but never handed to consumers (the remote/MCP
PR-landing runbook and a gold-standard self-audit scorecard). This record re-measures the original gap
table against the post-change state, records the design tiebreaks and how the critic/red-team findings
were resolved, and closes the loop with a review outcome.

## 2. Re-measured gap table

Same 8 rows as the original `gap-analysis.md`. The "consumer gets today" column is re-measured against
the current worktree state — committed *and* uncommitted, with the difference called out per row and in
Section 5/Section 6 because a few review-driven fixes are staged in the working tree but not yet part of
a commit at the time this record was written.

| # | Area | What a consumer gets **now** | Status | Grounding |
|---|---|---|---|---|
| 1 | Branch-delete recovery + worktrees | `archive-branch.sh` / `branch-hygiene.sh` / `cleanup-branches.sh` ship canonically inside the plugin (`plugins/ravenclaude-core/scripts/`), root keeps thin shims; `archive-branch.sh` hardened so a tag-push-to-origin failure retains the local tag + prints a loud recovery message instead of the prior rollback-and-abort dead end. A `shipped-reference-resolves` gate fails the build if any shipped skill/rule/agent cites a script path that doesn't resolve inside the plugin — closes the *class*, not just this instance. | **CLOSED** | `plugins/ravenclaude-core/scripts/{archive-branch,branch-hygiene,cleanup-branches}.sh` (commit `3993ab72`); `scripts/check-shipped-references-resolve.py`, wired into `scripts/audit-gates.sh` Gate 187 and required as a step in `.github/workflows/validate-marketplace.yml` (commit `7bf1bf6c`) |
| 2 | GitHub Actions hardening | `knowledge/github-actions-hardening.md` ships the least-privilege `permissions:` floor, SHA-pin-not-tag, OIDC, `pull_request_target` caution, the never-path-filter-a-required-check trap, and merge-queue/CODEOWNERS guidance. `/init-agent-ready` scaffolds a workflow-hygiene template + scanner that dogfoods those exact rules. `security-reviewer` gained a CI/CD review section pointing at the same knowledge. | **CLOSED** | `plugins/ravenclaude-core/knowledge/github-actions-hardening.md` (commit `f89adf0e`, Last-verified 2026-08-12); `templates/agent-ready-repo/github-protocol-workflow-hygiene.yml.template` (commit `64a9f425`); `agents/security-reviewer.md` CI/CD section (commit `52623633`) |
| 3 | Consumer CI: PR / commit / branch / secret | Four `github-protocol-*.yml` templates ship **default-selected** (not merely available) via `/init-agent-ready`: workflow-hygiene, PR-title, commit-lint, secret-scan — each dogfoods its own rules. | **CLOSED**, one refinement staged uncommitted | `templates/agent-ready-repo/github-protocol-{workflow-hygiene,pr-title,commit-lint,secret-scan}.yml.template` (commit `64a9f425`), wired at `commands/init-agent-ready.md` lines 16, 42, 58-61, 126-129. A staged, uncommitted fix gates the secret-scan diff step to pull_request-triggered runs only, with a clean skip on a manual dispatch — see Section 5 |
| 4 | In-loop protocol enforcement (agent-facing) | `enforce-git-protocol.sh` — a `PreToolUse(Bash)` hook, default **WARN**, knob `git_protocol: off\|warn\|block`, exactly 3 checks (commit-message Conventional-Commits shape, branch-name prefix, push-to-main advisory-only). Fail-open on any error; no-ops with no posture file; force-excludes the destruction verbs owned by `guard-destructive`. | **CLOSED, mechanism shipped** — an operability item is open, see Section 5 | `plugins/ravenclaude-core/hooks/enforce-git-protocol.sh` (commit `4808f875`), registered in `hooks/hooks.json` + `.claude/settings.json`. The file ships at git mode 100644; the mode bit + its consumer effect are examined in Section 5's review-outcome writeup |
| 5 | PR flow — remote/MCP landing | `knowledge/remote-mcp-pr-landing.md` — the earned "probe `gh` then direct API then GitHub MCP before concluding blocked" runbook, plus the "MCP tools are deferred/lazy-loaded" lesson — authored, Last-verified-stamped, and cross-referenced from `create-pr/SKILL.md`. | **PARTIAL — content complete, commit pending** | Content sits at `plugins/ravenclaude-core/knowledge/remote-mcp-pr-landing.md`. A `git status` read this session listed it as an untracked new path, and the `create-pr/SKILL.md` cross-reference as an unstaged modification — neither has landed in a commit as of this record, so a consumer running `/plugin marketplace update` today would not receive this row yet. See Section 6 |
| 6 | Branch protection / required checks / merge queue / CODEOWNERS | `setup-branch-protection.sh` — a dry-run-by-default `gh`-ruleset helper (guidance-first: `--apply` needs a live `gh` login + typed terminal confirmation, never auto-applied) + a commented `CODEOWNERS` starter, both scaffolded via `/init-agent-ready`. | **CLOSED, guidance-first by design (C4)** — a hardening fix staged uncommitted | `templates/agent-ready-repo/setup-branch-protection.sh.template` + `CODEOWNERS.template` (commit `4e8c2134`), wired at `commands/init-agent-ready.md` lines 17, 43, 63-64, 141, 146-148. A staged, uncommitted fix has the script escape the user-supplied branch/ruleset name with `jq` before it is interpolated into the ruleset JSON body — see Section 5 |
| 7 | Release / versioning / supply chain (SBOM/provenance) | An explicit deferral paragraph in `github-actions-hardening.md`, with pointers (oras/Syft, changesets, slsa-github-generator) for consumers who do ship compiled artifacts. | **DEFERRED (deliberate, with pointer)** | `plugins/ravenclaude-core/knowledge/github-actions-hardening.md` deferral section (commit `f89adf0e`) — matches tiebreak C5 |
| 8 | "Best of the best" — capability, not coverage | `skills/github-gold-standard/SKILL.md` — a 10-row rubric mapping 1:1 to the P3/P4 catalog, pass/partial/fail per row, a leverage-ranked remediation queue, and an explicit honest-scope note ("measures structural coverage, not taste, not a security certification"). Its full value depends on row 5's runbook landing. | **CLOSED (skill shipped)** — full effect depends on row 5 landing | `plugins/ravenclaude-core/skills/github-gold-standard/SKILL.md` (commit `52623633`) |

**Net:** 5 of 8 rows CLOSED outright, 1 CLOSED with an operability item open (row 4), 1 PARTIAL pending a
commit (row 5), 1 deliberately DEFERRED (row 7). No row regressed from the original table.

## 3. Design decisions and how each open question was resolved

**Tiebreaks (C1-C5):**

| # | Decision | Disposition |
|---|---|---|
| C1 | Escape-hatch mechanism | **Move + shim** (not copy + parity): one canonical script location, drift impossible by construction; the `shipped-reference-resolves` gate closes the recurrence *class*; `archive-branch.sh` hardened for the tag-push-403/no-`origin` case |
| C2 | New in-loop hook | **Ship, default WARN**, exactly 3 tight checks, fail-safe no-op with no posture file, escalatable via `git_protocol: off\|warn\|block` — matches the existing `worktree-guard.sh` idiom |
| C3 | CI-template granularity | **Group by concern**: one workflow-hygiene template (permissions floor + SHA-pin + no-path-filter lint); separate PR-title/commit-lint and secret-scan templates (distinct triggers, independently toggleable); every template dogfoods its own rules |
| C4 | Branch-protection setup | **Guidance-first**: dry-run helper + CODEOWNERS starter, never a default-on control — it needs `gh` admin scope and live GitHub state, the least guardrail-shaped item in the set |
| C5 | SBOM/provenance/release-automation | **Explicit deferral + pointer paragraph** — most consumer repos installing a plugin marketplace don't ship compiled artifacts, so lower leverage here than the PR/commit/secret gates |

**Correlated errors the critic caught (CE-1 through CE-5), one line each:**

| # | Finding | Resolution |
|---|---|---|
| CE-1 | Danger-verb prose in the shipped knowledge/rules could self-trip the write-time guard | Corrected mechanism (RT-1): `guard-destructive.sh` only reads `.tool_input.command`, so a *consumer's* installed guard does not re-trip on an Edit — the real build-time risk is the Thing tribunal's hard-deny rules, exercised live this session. Mitigated with neutralized spelling (no `git` on the same line as a flag; arrow notation for pipe-to-shell) across every new danger-verb-bearing artifact |
| CE-2 | `archive-branch.sh` still strands a no-`origin`/restricted-proxy consumer | `archive-branch.sh` hardened: a tag-push failure now retains the local tag + prints a loud, actionable recovery message instead of rollback-and-abort |
| CE-3 | Shipping a 30-repo knowledge doc risks becoming an ownerless release-blocker | Softer than first assessed — the freshness sweep's release-block threshold is 180-365 days and is a maintainer procedure, not a wired CI gate. Mitigated by stamping all three new knowledge docs with a Last verified line + a refresh trigger, auto-enrolling them in the existing weekly researcher sweep |
| CE-4 | "Best of the best" was being treated as coverage, not capability | Adopted: shipped the remote/MCP PR-landing runbook (row 5) and the gold-standard scorecard skill (row 8), promoted above further CI-template sprawl |
| CE-5 | The fail-safe reading was silently excusing near-zero *new* in-loop enforcement | Resolved by C2 — the WARN hook is a deliberately-dosed floor, not a reflexive opt-in default |

**Red-team execution-failure modes (RT-series), one line each:**

| # | Mode | Resolution |
|---|---|---|
| RT-1 | Build-time tribunal self-trip on danger-verb Writes | Mitigated by CE-1's neutralized-spelling convention, applied throughout; no loop-back |
| RT-2 | Escape hatch still strands the no-`origin`/403 consumer | Mitigated by CE-2's `archive-branch.sh` hardening; no loop-back |
| RT-3 | Copilot-package freshness check is a *required* CI gate, contradicting an early "not required" assumption | Corrected: `generate-copilot-plugin.py --check` runs inside `audit-gates.sh`, itself a required status check — regen after any `agents/*.md` edit is now a hard pre-push step, not hygiene |
| RT-4 | Byte-parity gate would collide with hardening the plugin copy (copy+parity mechanism only) | Moot — resolved by choosing move+shim (C1); no parity gate exists to collide |
| RT-5 | A default-on hook could false-positive-block a legitimate branch name, breaking the fail-safe doctrine | Resolved by C2's constraints: default WARN, fail-safe no-op absent a posture file, destructive verbs force-excluded, push-to-main never blocks at any knob |
| RT-6 | The CI-template dogfood check (actionlint/SHA-pin/permissions lint) could silently skip under a network-blocked sandbox, giving false comfort | Mitigated in-plan: the dogfood check is required to fail-closed rather than skip, per this repo's own Gate-10 precedent |

## 4. The "forced" reading — the design thesis

Per the DoD's word **"forced"**: in this idiom that means default-on plus fail-safe (no-op when
unconfigured or on any error) plus posture-tunable — never a brittle hard-fail that could brick a
consumer's `/plugin marketplace update` (House Rule 3). Hard enforcement (an exit-2 block) stays where it
already was, at maximum strength: `guard-destructive`'s existing blocks on the destruction verbs. The
*new* in-loop hook (row 4) deliberately stays at the softer default-WARN tier, escalatable by choice via
the knob, because a false-positive block on a legitimate branch name or commit style is a real
workflow-breaker (RT-5) and would itself violate House Rule 3. The CI tier is scaffold-then-consumer-owns
by mechanical necessity, not convenience: a `PreToolUse` hook cannot reach a server-side PR merge that a
human or another tool triggers, so nothing in that tier can be hard-forced in-loop no matter how strongly
"forced" is read. Auto-installing CI into a consumer's `.github/` on install was explicitly rejected as a
House-Rule-3 violation — every CI template stays opt-in-but-default-selected inside `/init-agent-ready`,
never silently applied.

## 5. Review outcome

**Security review: CLEAR.**

**Code review: 1 P0 and 4 P3s found.** This section is grounded in this session's own reads of the
working tree — `git status`, `git diff --stat`, `git ls-files -s`, and a filesystem `stat` on the hook
file in question — rather than a restatement of the review's own summary:

- **P0 — hook exec bit.** `plugins/ravenclaude-core/hooks/enforce-git-protocol.sh` is tracked at git mode
  100644. CI's "Verify hooks are executable" step in `validate-marketplace.yml`, plus the local Gate-4
  executable-bit pattern in `audit-gates.sh`, require the executable bit set on every
  `plugins/*/hooks/*.sh`. A `chmod` on the plugin's own hook substrate is a tribunal-guarded operation
  when agent-issued, so the sanctioned path for this fix is the maintainer's own bang-prefixed bash
  escape, not an agent-run chmod. control: `git ls-files -s plugins/ravenclaude-core/hooks/enforce-git-protocol.sh`
  and a filesystem `stat -f "%Sp"` on the same path, both run this session, returned mode 100644 and
  `-rw-r--r--` respectively — the probe that would come out differently if the bit were already set. This
  is the one item standing between a clean "0 P0-P3 remaining" and the state this record observed.
- **P3, four items, all fixed in the working tree, none yet committed** — `git diff --stat` this session
  reported 5 files changed, 56 insertions, 10 deletions:
  1. `enforce-git-protocol.sh` and its test — exempt git's own generated commit subjects (a Revert quote,
     a Merge line, fixup-bang, squash-bang) from the Conventional-Commits shape check, since those
     subjects are produced by git itself rather than authored and were false-positive-warning.
  2. `github-protocol-secret-scan.yml.template` — gate the diff-scoped scan step to pull_request-triggered
     runs only, with a clean success-with-a-note skip on a manual dispatch run. control: the template's
     own committed comment (added by this same fix) states that a manual-dispatch run carries no PR
     context, so the diff range is unavailable there; the change mirrors the commit-lint template's
     existing pattern and keeps a would-be-required check from hanging on a manual run.
  3. `setup-branch-protection.sh.template` — escape the user-supplied branch/ruleset name with `jq` before
     it is interpolated into the ruleset JSON body; a git ref name may legally contain a JSON
     metacharacter, and the branch/repo arguments are arbitrary user input.
  4. `create-pr/SKILL.md` — add the missing cross-reference to `remote-mcp-pr-landing.md` for the "remote
     route seems blocked" case.

**Net:** security is clear; the four P3 items are fixed in the tree; the P0 item is the one not yet
resolved as of this record. A clean "zero P0-P3 remaining" is the target this arc is converging on, named
here as a target rather than asserted as the current state, consistent with this record's own grounding
discipline.

## 6. Honest residue / follow-ups

- The P0 fix is a human step and has not been taken as part of this record. Setting the executable bit on
  `plugins/ravenclaude-core/hooks/enforce-git-protocol.sh` needs the maintainer's own bang-prefixed bash
  escape, because the tribunal guards a chmod on this substrate when it is agent-issued. Applying it is
  out of scope for a decision-record-only pass, but it is the single item blocking a clean sign-off of
  this arc.
- Six files are staged but uncommitted, per `git status` and `git diff` read this session:
  `knowledge/remote-mcp-pr-landing.md` (untracked), `hooks/enforce-git-protocol.sh`,
  `hooks/tests/test-enforce-git-protocol.sh`, `skills/create-pr/SKILL.md`,
  `templates/agent-ready-repo/github-protocol-secret-scan.yml.template`, and
  `templates/agent-ready-repo/setup-branch-protection.sh.template`. None of these reach a consumer via
  `/plugin marketplace update` until committed. The next commit needs to apply the P0 chmod, add the
  untracked runbook file, re-run `audit-gates.sh` plus prettier plus ruff over the combined diff, and then
  commit.
- The in-loop hook is Claude-Code-scoped for now. `enforce-git-protocol.sh` is registered in
  `hooks/hooks.json` (plugin canonical) and `.claude/settings.json` (dev-mirror) only — it is not yet
  projected into the copilot/codex host adapters. This matches the repo's existing selective
  host-projection pattern (the notification channel is marketplace-only by the same design choice) rather
  than being an oversight, but the "forced" in-loop nudge is, for now, Claude-Code-only.
- An unrelated uncommitted change exists in `index.html` — a dashboard "Updated" timestamp bump from the
  repo's routine self-heal-generated-artifacts pattern, unrelated to this arc's content. Named here only
  so it isn't mistaken for arc-related work when the next commit lands.
- The audit-gates figure of 716 passing, 0 failing, 0 skipped is the last measurement recorded in a
  commit message (commit `52623633`); it predates the uncommitted P3 fixes above and was not re-run
  against them as part of this record, since this task is scoped to write-only with no gate execution.

## 7. Definition of Done

| Item | State |
|---|---|
| Version | `0.246.0` in both `plugins/ravenclaude-core/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`. control: `grep '"version"'` on both files this session returned the same string in each |
| `audit-gates.sh` suite | 716 passing, 0 failing, 0 skipped, per the commit message of `52623633`; not re-run against the uncommitted P3 fixes as part of this record — see Section 6 |
| Copilot / codex / dashboard projections | Regenerated in lockstep with the P9 commit `52623633` (timestamp 2026-08-12T15:55:39-04:00, read via `git log -1 --format=%cI`); the uncommitted diff touches no `agents/*.md` frontmatter, so no further regen is expected — worth confirming rather than assuming once the P0/P3 items land |

# G1-lite — claims table

⚠️ **This table itself carries the lesson of Incident 1: it separates OBSERVATION from INFERENCE.**
Current FORGE G1 has only one notion of grounding — "is it sourced?" — and Incident 1's false claim
*was* sourced. The `kind` column is the gap this run exists to close, and it is applied here first.

| # | claim | kind | tier | grounding | settling gate |
|---|---|---|---|---|---|
| 1 | `/cdn-cgi/l/email-protection` returns 404 on the zone | observation | WARN | in-session `curl`, 2026-08-08 | settled |
| 2 | `/cdn-cgi/trace` and the real decode script both return 200 | observation | WARN | in-session `curl`, 2026-08-08 | settled |
| 3 | A real browser renders `matt@ravenpower.net` with a working `mailto:` on prod | observation | WARN | in-session Playwright eval, 2026-08-08 | settled |
| 4 | Therefore no visitor experiences the reported defect | **inference** | — | entailed by #3 directly; #3 IS the user-facing property, not a proxy | settled |
| 5 | ⛔ "The decoder is broken, every visitor is affected" | **inference** | — | was drawn from #1 alone; **FALSIFIED by #2 and #3** | settled — this is the incident |
| 6 | FORGE G1 as written would have passed claim #5 | inference about this repo | WARN | read `skills/forge-pipeline/SKILL.md` §2 G1 in-session: its BLOCK/WARN split keys on *provenance* (source or in-session tool call), never on inferential distance | this run's design |
| 7 | `consistency-failure-modes.md` is cited by nothing | observation | WARN | `grep -rn` across `plugins/` + `docs/` in-session, 0 hits | settled (PR #849 wired it) |
| 8 | The repo has a `diff-budget` skill that did not fire on the 806-file deletion | observation | WARN | `ls plugins/ravenclaude-core/skills/` in-session; the deletion reached the working tree unflagged | this run's design |
| 9 | `audit-gates.sh` carries 688 gates, each with must_pass/must_fail "teeth" | observation | WARN | full run in-session: `688 pass, 0 fail, 1 skipped` | settled |
| 10 | Gate "teeth" are rule 6 (prove the instrument) already mechanized for gates | inference | — | entailed by #9's structure: every gate ships a must_fail half proving it can detect | design input — the pattern to copy |
| 11 | A prose rule in an agent file is weaker than a fail-closed gate | inference | — | ⚠️ **[unverified — asserted, not measured]** The repo's own `consistency-failure-modes.md` argues it ("a rule that lives in a comment is a rule that gets copy-pasted past") and #7 is consistent with it, but no controlled comparison exists. **Settling route:** does not need settling before design — both panels are told to treat it as an assumption and at least one alternative must NOT rest on it. |

## What this table changes about G1

Claims #1–#3 are observations and are cheap to verify. Claim #5 was an **inference from #1**, and it
is where the entire incident lives. Under current G1 it would have been marked WARN-and-continue
because an in-session `curl` backed it.

**The design input:** grounding an observation ≠ grounding an inference drawn from it. An inference
that a build phase depends on needs a *disconfirming* probe, not a confirming source.

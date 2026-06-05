---
scenario_id: 2026-06-05-sast-finding-false-positive-triage
contributed_at: 2026-06-05
plugin: security-engineering
product: semgrep
product_version: "unknown"
scope: likely-general
tags: [sast, semgrep, false-positive, taint, triage, signal]
confidence: medium
reviewed: false
---

## Problem

A newly-enabled SAST ruleset (Semgrep on every PR) flooded the team with ~120 findings in the first week, the loudest class being "SQL injection" on a data-access module. Developers started reflexively dismissing the whole rule as noise — which is exactly how the *one real* injection in that flood survives. The owner needed a repeatable way to separate the true positives from the false ones fast enough that the gate stayed credible instead of becoming an ignored wall of red.

## Constraints context

- The SAST gate was new; the team had no triage muscle and a strong incentive to declare the tool broken and turn it off.
- The flagged module used a query builder that *looked* like string concatenation to a pattern matcher but actually parameterized under the hood — a classic source of SAST false positives.
- One genuine finding really was concatenating a request-derived value into a raw query in an admin endpoint. It was buried at finding #83 of 120.

## Attempts

- Tried: triage by reading each finding's line in isolation. Too slow and error-prone — without the data flow you can't tell a parameterized builder from a real concatenation just by staring at the flagged line.
- Tried: blanket-suppress the SQL-injection rule on the data-access module "because it's all the query builder." This would have suppressed finding #83 (the real one) along with the noise — the textbook way a real bug hides behind a false-positive cluster.
- Tried (the move that worked): triage by **taint reachability — does untrusted input actually flow to the sink?** Prefer the rules' dataflow/taint mode over the syntactic pattern match. Triaged in three buckets: **true positive** (untrusted source reaches the sink unsanitized → fix the code + keep the rule), **false positive** (the "sink" is safe — parameterized/escaped → suppress *with an inline justification comment at that specific line*, never a blanket rule-off), and **needs-context** (can't tell statically → ask the code owner). Then **tune the rule once** so the parameterized-builder pattern stops matching for everyone, instead of suppressing it N times.

## Resolution

The 120 findings resolved to ~6 true positives (one of which — #83 — was a genuine, fixable SQL injection in an admin endpoint), ~95 false positives from the query-builder pattern (fixed *once* by tuning the rule, not 95 inline suppressions), and the remainder routed to code owners. The gate survived because it produced signal in week two instead of noise.

The mental model: **a false positive is a rule-tuning task, not a dismiss-the-finding task.** Every blanket suppression is a place a future true positive can hide. Suppress at the line with a reason, or — better — fix the rule so the false pattern never fires again. And never let the *volume* of false positives become the argument for ignoring the *class* — that's precisely the cover the one real bug needs.

**Action for the next engineer:** triage SAST findings by whether untrusted input reaches the sink (taint/dataflow), not by eyeballing the flagged line. Bucket into true / false / needs-context. Fix false positives by **tuning the rule once**, and suppress only at the specific line with an inline justification — never blanket-disable a rule over a whole module. The fix-or-accept verdict on a true positive routes to `ravenclaude-core/security-reviewer`.

Cross-reference: complements the [`../skills/appsec-scanning`](../skills/appsec-scanning/SKILL.md) skill, [`../best-practices/sast-tune-for-signal.md`](../best-practices/sast-tune-for-signal.md), and the new [`../knowledge/sast-dast-sca-scanner-selection-decision-tree.md`](../knowledge/sast-dast-sca-scanner-selection-decision-tree.md).

**Sources (retrieved 2026-06-05):**
- Semgrep (static analysis; taint/dataflow mode) — https://semgrep.dev/docs/
- OWASP Source Code Analysis Tools — https://owasp.org/www-community/Source_Code_Analysis_Tools

Tool-specific taint-mode behavior and suppression syntax are version-specific — `[verify-at-use]` against the SAST tool's current docs before any deliverable.

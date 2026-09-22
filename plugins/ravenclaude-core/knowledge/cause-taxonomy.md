# Cause taxonomy — why an output looked the way it did

> A negative or empty result names ONE outcome. It never names its cause. This file enumerates
> the cause set so a cause is **selected by discrimination** rather than assumed by
> availability — the availability heuristic being the whole defect.

> **SSOT.** This document and `scripts/cause_taxonomy.py` hold the same member set. Parity is
> checked by `python3 scripts/cause_taxonomy.py --check-doc` in CI: an id in one and not the
> other fails the build. Add a member here and in the module in the same commit.

---

## The ritual

1. Before asserting a cause, list the classes that could produce **this exact output**.
2. Name the ONE discriminating probe that splits the top two.
3. Run it, then assert — and if you cannot run it, **write the cause as a hypothesis, not a fact.**

The ritual is a behavioural rule. Its honest limit is stated in full at the bottom of this file.

---

## Reading the tables

`id` is the stable member id. `cause` is the one-line statement an advisory quotes verbatim.
`discriminating probe` is the command that separates this member from its neighbours — a
candidate offered without one is a list of maybes, which changes nothing.

`{target}` in a probe is filled from the command the agent already authored. No bytes of the
observed stdout or stderr are ever interpolated into a probe.

---

## Class E — the command did not run as intended

The shell never reached the subject. Nothing in the output is evidence about the subject at all.

| id | cause | discriminating probe |
|---|---|---|
| E1 | binary absent from PATH (the rc=127 shape) | `command -v {target}; echo rc=$?` |
| E2 | a function or alias shadows the expected binary — same word, different product | `type -a {target}; {target} --version` |
| E3 | permission denied on the target or on the interpreter (the rc=126 shape) | `ls -l {target}; test -r {target}; echo rc=$?` |
| E4 | the shell ate the argument — unexpanded or over-expanded glob, quoting, ~, a missing -- | `printf '%s\n' {target}   # echo the EXPANSION; do not re-run the command` |
| E5 | never reached — an earlier && element failed, or set -e / pipefail short-circuited | `run the segment alone, then: echo "${PIPESTATUS[@]}"` |
| E6 | wrong working directory — cwd resets between agent Bash calls | `pwd -P   # inside the SAME invocation as the probe` |
| E7 | the tool consumed stdin where a file was intended, or hung waiting on it | `re-run with </dev/null and compare` |

---

## Class F — the read looked in the wrong place

The command ran and the subject exists, but the target it examined was not the one that holds the answer.

| id | cause | discriminating probe |
|---|---|---|
| F1 | path absent, mistyped, or a reader of the OLD path after a move | `ls -d {target}; git log --oneline -1 -- {target}` |
| F2 | wrong tree — linked worktree vs primary checkout, build output vs source, plugin cache vs repo | `git rev-parse --show-toplevel; git worktree list` |
| F3 | wrong ref scope — searched HEAD when the change is on origin/main | `git log origin/main -1 -- {target}; git branch --contains HEAD` |
| F4 | the tool's own filters excluded it — .gitignore, --include/--exclude, -maxdepth, binary skip | `re-run with `rg -uuu` (or plain `grep -r`) and DIFF THE COUNTS` |
| F5 | pagination truncation — a default per_page, page 1 of N | `re-run with --paginate (or follow next links) and compare counts` |
| F6 | case, encoding or whitespace mismatch — CRLF, NBSP, Unicode normalisation | `grep -i {target}; then hexdump -C one expected line` |

---

## Class G — the answer was produced and then discarded

The subject answered correctly. The answer was lost between the producer and the reader.

| id | cause | discriminating probe |
|---|---|---|
| G1 | the output went to stderr while only stdout was read | `re-run with 2>&1 and compare` |
| G2 | a redirect to /dev/null discarded the evidence — emptiness manufactured by the reader | `re-run WITHOUT the redirect` |
| G3 | exit status read where content was meant, or the inverse (quiet-mode inversion) | `read a COUNT: hits=$(grep -c ... ); total=$(awk 'END{print NR}' {target})` |
| G4 | a pipeline stage swallowed it — SIGPIPE, a wrong second-stage pattern, a subshell losing state | `run stage 1 alone, then: echo "${PIPESTATUS[@]}"` |
| G5 | truncation or buffering by the PRODUCER — an output cap, interleaving, a partial read of a mid-write file | `compare the byte size against the producer's RECEIPT, not against a guess` |
| G6 | the consumer parsed the wrong field — a jq path miss yields null, not an error | `jq 'keys' {target}; then jq -e '<path>' (non-zero on null)` |
| G7 | ANSWER TRUNCATED BY MY OWN INSTRUMENT — head/tail/-m/--max-count/a display cap. The answer WAS produced and WAS correct; the harness discarded the part that mattered, and the truncation was read as absence | `RE-RUN WITH NO LIMIT AND COMPARE COUNTS, NOT CONTENT: n=$(<cmd> \| wc -l). If n exceeds the limit you used, the earlier read was truncated and ANY absence conclusion drawn from it is VOID.` |

---

## Class H — the subject genuinely has no such thing

The only class that licenses an absence conclusion. Reachable only after E, F and G are excluded.

| id | cause | discriminating probe |
|---|---|---|
| **H1** | the thing is absent — the hypothesis usually leapt to | `⛔ RANK-GATED: credible only once E, F and G are excluded, and only with a POSITIVE CONTROL on the same subsystem proving this probe can return non-empty. control: run the identical probe against a target known to exist; if THAT is also empty the probe is blind and this candidate is unavailable.` |
| H2 | present but not materialised yet — async write lag, unbuilt artifact, cold cache, job in progress | `re-probe after the producer's RECEIPT arrives, never after a wall-clock guess` |
| H3 | present under a different name or shape — renamed, generated, or wrapped in a composite that declares no runtime | `search by content fingerprint, not by name; expand the composite and search inside it` |
| H4 | present but in a different STATE — flag off, secret unset in THIS environment, prod-vs-preview drift | `read the state from the environment that ran the command, not from the repo` |
| H5 | the query described rather than matched — or matched the PROSE that describes the thing | `plant a canary string the query MUST match, then re-run` |
| H6 | a stale cache returned an old or empty result — CDN, DNS, browser, local build cache | `bypass the cache layer explicitly and compare` |
| H7 | right question, wrong layer — source text vs the rendered or live object model | `measure the LIVE object, not the text that describes it` |
| H8 | a race with a concurrent writer or deleter mutated the target mid-probe | `re-run immediately; if the result flips, this is it, and it is not a stable defect` |

### The rank gate on H1

`H1` is never available as the rank-1 candidate. It becomes credible only once E, F and G
are excluded **and** a positive control on the same subsystem shows the probe was capable of
returning something else. An empty result from a blind probe and an empty result from an
empty subject are the same bytes; only the control separates them.

control: run the identical probe against a target known to exist. If that is also empty, the
probe is blind and H1 is unavailable.

This gate is asserted at import time in the module, so a future edit cannot quietly drop it.

---

## Class I — indeterminate: evidence about reachability, never about the subject

The transport failed. An indeterminate result cannot close a row in either direction.

| id | cause | discriminating probe |
|---|---|---|
| I1 | rate-limited | `read the retry-after header; try a second endpoint on the same host` |
| I2 | server or upstream 5xx | `hit a known-good endpoint on the same host` |
| I3 | timeout | `raise the bound ONCE and re-run; ⛔ GNU timeout is absent on macOS` |
| I4 | unreachable — DNS, connection refused or reset | `curl -sS -o /dev/null -w '%{http_code}' <host>/ on a trivially-live path` |
| I5 | auth expired or scope insufficient — a 403, OR an empty 200 body that reads as nothing-there | `authenticated whoami on the SAME credential; then list the granted scopes` |
| I6 | the resource is in progress, not missing | `poll the producer's STATUS endpoint, not the artifact` |

---

## Provenance — the incidents these members were derived from

Each line names an incident, the member it produced, and the probe that settled it. They are
recorded as history so a future reader can re-run the discriminator rather than trust the entry.

| member | incident | what settled it |
|---|---|---|
| G7 | 2026-08-19 — a `\| head -20` read of hook sources was written up as "no in-repo instance exists"; the match sat past the cap. | control: re-ran with no limit and compared counts — the token appears in 12 files, so the absence conclusion was void. |
| H1 | the `/cdn-cgi/l/email-protection` 404 — a true observation from which a false inference ("the decoder is broken") drove an 85-line component across 16 files. | control: `/cdn-cgi/trace` returned 200, disconfirming the decoder hypothesis in one call. |
| F5 | a `/user/repos?per_page=100` read returned 98 rows and was taken for the whole set. | control: re-ran with `--paginate` and compared counts — 246. |
| F2 | a search run from a linked worktree measured the primary checkout. | control: `git rev-parse --show-toplevel` beside the probe. |
| H5 | a source-scan gate matched the PROSE describing the thing rather than the thing. | control: planted a canary string the query must match, then re-ran. |
| I5 | an empty 200 body read as nothing-there where the credential lacked scope. | control: authenticated whoami on the same credential, then listed granted scopes. |

---

## The honest limit

No hook on any host carries the model's chat text, so the place the confident inference is most
often spoken is structurally out of reach. This is a behavioural rule with an enforced sliver
beneath it — not the rule's enforcement.

What the sliver covers: a failed or empty Bash result is triaged after the fact, and a durable
write or a remediating command that rests on an unsettled cause meets a gate. What it does not
cover: a cause asserted in conversation and acted on in the same breath.

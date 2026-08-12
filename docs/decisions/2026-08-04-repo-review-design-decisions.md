# Repo review — design decisions needing your input (2026-08-04)

A scheduled full-repo review ran a three-panel process (5 parallel dimension finders → validation → tie-break)
over the whole tree. **The mechanical baseline is spotless**: every existing gate passes, including the
686-assertion gate-audit meta-test (`686 pass, 0 fail`). See the run record under
`.ravenclaude/runs/repo-review-2026-08-04/`.

Nine findings survived validation. **Four low-blast, clearly-correct fixes with no design input were
implemented directly** and ship in the accompanying PR (see "Implemented" at the bottom). **Five findings are
routed here for your decision** — each is either security-critical, touches protected tribunal substrate, or is
a product-direction call with a large blast radius. This repo's own decision-review discipline sends high-blast
/ security / substrate changes to you rather than auto-resolving them, which is exactly why they are here and
not in the PR.

Each finding below is **verified against source this session** (not taken on a subagent's word) and carries a
concrete direction so you can act with a glance, not a re-investigation.

> **Note on the deliberately-vague repro in D1/D2:** the exact attack strings are omitted here on purpose —
> writing them into a repo file is itself hard-denied by the command-review tribunal's `sce.curl-pipe-shell`
> rule (which screens file-write payloads category-independently). The live-script reproductions were run this
> session; the shapes are described in prose so this document itself stays inside the guardrails.

---

## D1 — Security (P1): `guard-destructive.sh` misses download-then-execute RCE

**File:** `plugins/ravenclaude-core/hooks/guard-destructive.sh` (~line 446)

The guard's only remote-code-execution rules match a downloader (curl/wget) **piped directly into an
interpreter**, or run via **process/command substitution**. The functionally-identical
**download-to-a-file-then-execute-that-file** shape (download with `-o`/`-O`/`>` to a temp path, then run the
saved file with a shell in the same command) is **not caught at all**. Reproduced this session against the live
script: the download-then-execute forms — including the `wget -O`, redirect-then-run, and
`python3 -c urlretrieve` variants — all return **exit 0 (allowed)** with no stderr.

The script's own header calls itself "the consumer's PRIMARY deterministic guard on the `/plugin install` path"
(unconditional, not gated behind the opt-in Thing tribunal), so this is a **default-active bypass** of the RCE
protection the guard exists to provide. Notably the script **already** implements the analogous same-command
write-then-execute detection for heredocs (`_cmd_executes_path`, ~line 190) — the downloader equivalent was
simply never built.

**Recommended fix:** extend the existing `_cmd_executes_path` logic to downloaders: extract the
`-o`/`-O`/`--output`/`--output-document`/redirect target, and if that path (or its `./basename`) is later
invoked directly or via an interpreter (sh, bash, dash, zsh, ksh, python, perl, ruby, node, `source`, `.`) in
the same normalized command, DENY with a new `download-then-execute` reason.

**Why it's here, not in the PR:** it changes a security control's matching, and the exact interpreter/verb set +
false-positive tolerance for legitimate installers is a judgment call. It's small; I can implement it on your
go-ahead. **Add a bidirectional Gate fixture** (deny the download-then-execute forms; allow a benign
download-then-`cat`) with the change.

---

## D2 — Bug (P2): `guard-destructive.sh` false-DENIES safe compound commands

**File:** `plugins/ravenclaude-core/hooks/guard-destructive.sh` (~lines 351/396/411)

`_is_dangerous_rm` / `_is_dangerous_find` / `_is_dangerous_truncate` require a recursive/destructive flag AND a
dangerous-target pattern (`/`, `~`, `$HOME`) present **anywhere in the whole normalized command** — the target
check is never scoped to the matched command's own argument. So a safe relative-path destructive op chained with
any clause that merely *mentions* an absolute path is denied. Reproduced against the live script this session
(all three returned exit 2):

- a recursive delete of a **relative** dir chained (`&&`) with an `echo` of an absolute path
- a `find . … -delete` chained with an `echo` of an absolute path
- a `truncate -s 0` of a **relative** file chained with an `ls` of an absolute path

All three **contradict the script's own comments** (~lines 340/380/403) which say the relative-path form is
"ALLOWED". These are everyday clean-then-build / clean-then-list idioms, and hard-blocking them trains
users/agents to route around or disable the guard.

**Recommended fix:** scope the dangerous-target search to the sub-command **segment** containing the matched
invocation (from its command-boundary match to the next `;`/`&&`/`||`/pipe/newline or end), not the whole
command string.

**Why it's here, not in the PR:** this **loosens** a security guard. A wrong segment boundary could re-open the
very hole the guard exists for (a recursive delete of `/` followed by a separate clause must still deny). It
needs careful implementation + the guard's existing deny fixtures re-run + new allow fixtures — reviewed, not
landed autonomously in an unwatched run. **Sequence it after D1** (D1 tightens, D2 loosens — do the tightening
first).

---

## D3 — Security/correctness (P1): the decision tribunal's safety seat can be silently absent

**File:** `plugins/ravenclaude-core/scripts/thing-decide.py` (`_tally`, ~lines 558–619)

The abstention fail-safe (`abstained >= 2 → defer`) only fires on **two or more** abstentions. When exactly one
seat abstains, only **Heimdall's** abstention special-cases a Thor tie-breaker convene (line ~582:
`heimdall_abstained or "defer" in distinct or len(distinct) > 1 or low_conf`). **Forseti — the sole
safety/reversibility seat** (role brief ~lines 122–127: "Judge the DECISION on safety: reversibility, blast
radius, irreversibility, data/secret exposure, destructive-by-default") — has no equivalent check. If Forseti
times out/errors (→ abstain) while Mímir and Heimdall vote unanimously and confidently, `_tally` falls straight
through to the unanimous-verdict path (~line 607) and **returns a binding yes/no with the safety seat having
cast zero votes.**

Worse, it's backwards relative to a *low-confidence* Forseti: a Forseti that responds but is unsure sets
`low_conf=True` and **does** convene Thor — but a Forseti that fully fails to respond does not. A seat that says
nothing is treated *more permissively* than one that says "I'm unsure."

This is latent in this repo (decision-review defaults `off`) but live for any consumer who sets
`decision_review: binding`.

**Recommended fix (one line, safety-increasing only):** force Thor whenever **any** single seat abstained, or at
minimum special-case Forseti the same way Heimdall is:

```python
# was: if heimdall_abstained or "defer" in distinct or len(distinct) > 1 or low_conf:
if abstained_roles or "defer" in distinct or len(distinct) > 1 or low_conf:
```

This still lets a 2-of-3 confident-unanimous panel bind, but only after Thor has had a chance to stand in for the
missing seat (mirroring the existing `heimdall_abstained` re-screen).

**Why it's here, not in the PR:** `thing-decide.py` is the tribunal engine — protected substrate this repo's own
`xc.tribunal-self-disable` guard hard-denies mutating. Changes should be reviewed and **re-run against the
golden eval** (`scripts/thing-golden-eval.py` / Gate 33) before landing. The change only ever adds *defers* (it
cannot reduce safety), so it's low-risk once the golden eval confirms no regression.

---

## D4 — Correctness (P2): the tribunal tie-breaker's own confidence is never checked

**File:** `plugins/ravenclaude-core/scripts/thing-decide.py` (`_tally`, ~lines 587–606)

The three primary seats' confidence is checked against `threshold` (a sub-threshold vote forces a Thor convene).
But once Thor is convened, **its own returned confidence is never checked** — only `status == "abstain"` and
`injection_detected` short-circuit to defer. A low-confidence Thor `yes`/`no` binds exactly like a
high-confidence one, even though the design principle (Mímir's brief, "if it's a matter of taste, vote LOW
confidence so it escalates") treats low confidence as an escalation signal — but there is no "further" after
Thor, and nothing enforces it in code.

**Recommended fix (symmetric with the primary-seat check):**

```python
# before `return thor["verdict"], …`
if float(thor.get("confidence", 0)) < threshold:
    return "defer", "tie-breaker low-confidence — deferring to human", records
```

**Why it's here, not in the PR:** same reason as D3 — tribunal engine, protected substrate, gate the change on
the golden eval. Also safety-increasing only. Pairs naturally with D3 (same function, same review, one version
bump).

---

## D5 — Product direction (P2, systemic): 43 of 66 anti-pattern hooks are misleading stubs

**Files:** 43 of `plugins/*/hooks/flag-*antipatterns.sh` (full list in the run record's `decisions.md`)

Independently counted this session: **66** `flag-*.sh` hooks total; **43 are a byte-identical stub** (line counts
cluster at 42–43), **23 have real per-domain detectors** (finance, salesforce, …). The stub's header comment and
its advisory `note()` claim to flag "a metric with no baseline | an unsourced figure | client PII" (and, per
domain, PHI / FERPA / MNPI / private keys), but the **entire detection is one line** that greps only for the
literal placeholder tokens `TODO` / `FIXME` / `lorem ipsum`. So:

1. The comment/note make a **false claim** about what's checked (a Claim-Grounding violation — the repo's own
   cardinal rule). Several of the 43 name highly-sensitive data that is never checked
   (`behavioral-health-practice`/`pharmacy-operations` → PHI, `k12-school-administration` → FERPA,
   `mortgage-lending` → borrower NPI, `corporate-development-ma` → MNPI, `blockchain-web3-engineering` → private
   keys).
2. The note is a non-sequitur: it fires only on those literal placeholder tokens, then talks about
   PII/baseline/sourcing — so a benign "TODO: schedule kickoff" trips a PHI-shaped warning, training users to
   ignore the hook.

These are **advisory** (exit 0 unless `<DOMAIN>_STRICT=1`), so nothing is blocked or corrupted — the harm is
misleading text at scale.

**The decision I need from you — which direction?**

- **(a) Honest-minimal (my recommendation as the floor).** Rewrite the stub's note + comment to state only what
  it actually checks ("placeholder text detected — review against §N before shipping"), removing the false
  PII/baseline/sourcing claim. Correct regardless of (b). **Cost:** 43 plugins × version bump (plugin.json +
  marketplace.json) + artifact regeneration — a large but mechanical PR.
- **(b) Real detectors for the sensitive domains.** Implement genuine per-domain regexes (SSN/MRN/DOB shapes for
  PHI plugins, a missing-`Source:` check for benchmark-heavy plugins) the way `finance`/`salesforce` do. Higher
  value, but risky (PII regex false positives) and genuinely per-domain work.

**Recommendation:** ship **(a)** as the floor for all 43 (kills the false claim now), then prioritize **(b)** for
the ~6 high-sensitivity PHI/PII/MNPI/key plugins. I did **not** mass-edit 43 plugins autonomously: the direction
is a product call and the blast radius (43 version bumps + 9 MB `index.html` regen) is large for an unwatched
scheduled run.

---

## Implemented in the accompanying PR (no design input required)

| #  | Fix                                                                                                                                                                                                                     | File                                     | Verified                                          |
| -- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ------------------------------------------------- |
| F4 | Root README stale counts: 14→15 agents, 43/40→50 skills, 16→26 hooks (matched to the CI-gated plugin README)                                                                                                             | `README.md`                              | counted this session                              |
| F5 | `/stream` command missing from the README command table; count 7→8                                                                                                                                                      | `README.md`                              | command file exists                               |
| F6 | Wrong line citation `spawn-team/SKILL.md:30-50` → `:94-97` (the real "Stakeholder document" section)                                                                                                                     | `GETTING_STARTED.md`                     | section confirmed                                 |
| F9 | **Security (P1):** PII email-exclusion regex was an unanchored prefix — real emails on domains that merely *start* with a placeholder (e.g. `…@contoso.com.au`) bypassed PII rejection and would stage into a public PR. Anchored the exclusion to the whole domain. | `scripts/process-scenario-submission.py` | 11-case matrix + end-to-end via `_has_secret_or_pii` |

F9 was implemented (not routed here) because its fix **strictly tightens** the PII filter — it can only flag
*more* real emails, never stage more — the fail-safe direction for a gate whose docstring says "on ANY match,
REJECT", in a non-protected repo-root script, verifiable without any API.

# G5 — RED TEAM · run `forms-process-expertise`

**Subject:** `plan.md` (G6 synthesis, 96,626 bytes, 1,240 lines) · **Date:** 2026-08-17
**Question asked:** not "are the input plans' premises sound" (that is G4a's `critic-brief.md`) but
**"this plan, executed as written, breaks HOW?"**

Every claim below is a command I ran in `/Users/matthewcorbett/RavenClaude` on the working branch
`fix/process-improvement-harden` (`a57f05fc`), or a `path:line` I opened. Nothing is inferred from the
plan's own prose. Where I suspected a defect and could not trigger it, it is in §Cannot reproduce —
that section is what makes the rest credible.

**Bottom line: 4 unmitigated-as-written HIGH findings, all of them broken acceptance tests inside the
authoritative plan itself.** A builder executing §4 verbatim hits three of them in the first two phases.
Each fix is one to three lines of plan text; I give the exact replacement and its positive control.

---

## H1 — The PR #959 STOP gate can NEVER be satisfied. PR #959 reintroduces the sentinel string in its own retraction.

**Severity: HIGH** (defeats a stated purpose; the only repair path is deleting the defense)

### Trigger / repro

The plan hard-STOPs the entire run on this probe, twice — P0 acceptance 2 and the P8 pre-build gate:

> `git show origin/main:plugins/web-design/skills/conversion-design/SKILL.md | grep -c "35–50%"` → **0**.
> If 1, **STOP** — P8 would collide with an in-flight branch…

Run against the branch that is supposed to make it 0:

```
$ git show origin/main:plugins/web-design/skills/conversion-design/SKILL.md | grep -c "35–50%"
1
$ git show origin/fix/conversion-design-field-folklore:plugins/web-design/skills/conversion-design/SKILL.md | grep -c "35–50%"
1        <-- STILL 1 ON THE FIX BRANCH
```

Why: #959 deleted the table and then **quoted the deleted figure in the retraction paragraph it added**.

```
$ git show origin/fix/conversion-design-field-folklore:plugins/web-design/skills/conversion-design/SKILL.md | grep -n "35–50%"
63:⛔ **A per-field percentage penalty is not a real number.** Until 2026-08-17 this section stated
   "each additional required field reduces completion by ~5–7%" and carried a completion-by-field-count
   benchmark table (1 field → 35–50%, 7+ → <10%). Both were **unsourced** … They were **removed rather
   than re-cited** …
```

Compare `origin/main:60`, which is the actual table row: `| 1 (email only) | 35–50% | Newsletter, waitlist, magic-link sign-up |`.

### Blast radius

P0 blocks everything; P8 is the largest-blast-radius phase. After #959 merges, the gate returns 1 and
says STOP. Two outcomes, both bad: (a) the run halts permanently on a state that is actually correct, or
(b) the operator concludes the gate is broken and **deletes it** — removing the one mechanism protecting
against re-adding a table that was deliberately deleted as unsourced (the plan's R2 and CE-2).

This is the repo's own recorded defect wearing new clothes: *a grep is satisfied by the thing being
**described***. Here it is inverted — the *retraction* satisfies the grep written to detect the *claim*.

### Mitigation (verified bidirectionally, both directions measured)

Replace the sentinel with a structural probe plus a presence probe:

```
# table row absent
git show origin/main:plugins/web-design/skills/conversion-design/SKILL.md | grep -c '^| 1 (email only) |'   # must be 0
# retraction present  (positive control: proves the file is the post-#959 one, not an empty read)
git show origin/main:plugins/web-design/skills/conversion-design/SKILL.md | grep -c 'removed rather than re-cited'  # must be >=1
```

Measured now:

| ref | `^\| 1 (email only) \|` | `removed rather than re-cited` |
|---|---|---|
| `origin/main` (pre-merge) | **1** | **0** |
| `origin/fix/conversion-design-field-folklore` | **0** | **1** |

Both probes flip. A one-sided probe (absence only) would still pass on an empty/missing file; the
presence half is the positive control the plan demands everywhere else and omitted here.

Also add the missing branch the plan has no answer for: **if PR #959 is CLOSED rather than merged**, the
STOP has no exit. Record an explicit fallback — P8's prior into `accessibility-auditor.md` /
`ux-designer.md` does not touch `conversion-design/SKILL.md` at all, so the only real requirement is that
P4's scenario **links** to a section that exists. If #959 closes, P4 links to `§3` as it stands and drops
the "post-#959" qualifier.

---

## H2 — `--check 30`, `--check 18`, `--check 29` do not exist. The Gate 30 hook-mutation "must-fail proof" therefore passes vacuously.

**Severity: HIGH** (silent false confidence in a must-fail half — the exact class the plan exists to prevent)

### Trigger / repro

```
$ bash scripts/audit-gates.sh --check 30 ; echo $?
audit-gates.sh --check: gate '30' is not registered for per-gate runs. Supported: 20, 34, 50, 52, …, 218.
1
$ bash scripts/audit-gates.sh --check 18 ; echo $?   -> 1   (same message)
$ bash scripts/audit-gates.sh --check 29 ; echo $?   -> 1   (same message)
$ grep -n "^    30)" scripts/audit-gates.sh          -> (no output)
```

Gate 30 exists as a full-suite block only (`scripts/audit-gates.sh:3584`); Gate 18 at `:2201`; Gate 29 at
`:3520`. None has a dispatcher case arm, and none is in the `Supported:` list at `:1149`.

The plan uses these three numbers as acceptance tests in **P2** (`--check 29`), **P3** (Gate 18 → PASS,
`--check 29`), **P4** (`--check 29`), **P6** (`bash scripts/audit-gates.sh --check 30` → PASS), **P8**
(Gate 18 → PASS, `--check 29`) and **DoD #11** (`N ∈ {219, 220, 221, 30, 18, 29, 206}`).

### The silent half — this is why it is HIGH, not MED

P6's teeth proof, quoted from the plan:

> ⛔ **Mutation proof:** mutate the hook to always-silent and confirm Gate 30 goes **RED**, then revert.
> *A fixture pair that cannot fail is decoration.*

`--check 30` is **RED unconditionally** — before the mutation, after the mutation, and on a tree with no
forms hook at all. The operator mutates, sees non-zero, concludes the fixture pair has teeth, reverts,
and ships. **The probe and the subject fail the same way**, which is the recorded "my own probes fail
silently toward clean" pattern. DoD #14 ("Every must-fail half proven … the Gate 30 pair's hook-mutation
proof") is satisfied by an error message.

### Blast radius

One decorative fixture pair (the exact defect row 40 records in `process-improvement`, reproduced on day
one), plus ~10 always-failing acceptance steps that train the operator to skip `--check` results — which
would also skip 219/220/221, the three that genuinely work.

### Mitigation

- Gate 29 → `python3 scripts/check-md-links.py` (exists; exit code is the gate).
- Gate 18 → `python3 scripts/check-frontmatter.py` (exists).
- Gate 30 → run the **full suite** and key on the per-assertion lines. `scripts/audit-gates.sh:1186`'s
  `gate()` prints `  ✓ <label> …` / `  ✗ <label> …`, so the mutation proof becomes:

  ```
  bash scripts/audit-gates.sh > /tmp/before.txt 2>&1
  grep -c '✓ forms anti-patterns (silent on clean)' /tmp/before.txt      # must be 1
  # mutate hook to always-silent
  bash scripts/audit-gates.sh > /tmp/after.txt 2>&1
  grep -c '✗ forms anti-patterns (fires on anti-pattern)' /tmp/after.txt # must be 1  <- the real teeth
  ```

  Keying on the **named assertion that flipped**, not on the suite's overall exit code, is the only form
  that cannot be satisfied by an unrelated failure.
- Delete `30`, `18`, `29` from DoD #11 and say why, so a future editor does not re-add them.

---

## H3 — The P5/T2 round-trip does not execute. `lss_calc.py imr` reads no stdin, and the mandated NOVEL-SYNTHESIS label poisons the pipe if it is fixed naively.

**Severity: HIGH** (the plan's only mechanical proof of its only no-prior-art claim)

### Trigger / repro

P5 acceptance and §5.2 both specify:

> `python3 …/form_metrics.py --emit-imr <fixture.csv> | python3 …/lss_calc.py imr` produces valid control
> limits. This proves the seam **executes** rather than asserting it exists.

```
$ echo "10.1
10.3
9.8" | python3 plugins/process-improvement/scripts/lss_calc.py imr ; echo $?
usage: lss_calc.py imr [-h] --values VALUES
lss_calc.py imr: error: the following arguments are required: --values
2
```

`--values` is `required=True` (`plugins/process-improvement/scripts/lss_calc.py:372-375`) and there is no
stdin path anywhere in the module. The pipe's left side is discarded; the right side exits 2.

### The compounding trap — do not "fix" it with `--values "$(…)"` blindly

`_parse_values` (`lss_calc.py:105-113`) accepts comma **or whitespace** separation, so
`lss_calc.py imr --values "$(form_metrics.py --emit-imr f.csv)"` would work — *except* §6.1 mandates:

> Required in **every** surface that carries the join: … and **printed by `form_metrics.py`'s own output**
> so a user who never opens a doc still sees it.

If that ~50-word marker lands on stdout in `--emit-imr` mode, `_parse_values` raises
`all values must be numbers` and the round-trip exits 2 again. §6.1 and P5 are in direct conflict and
neither section notices.

Second-order: `cmd_imr` accepts **n ≥ 2** (`lss_calc.py:259-261`). Nothing in the plan constrains the
fixture's length, so Gate 220 can certify "valid control limits" on a 2-point series — the precise thing
best-practice rule #5 (`do-not-put-three-sigma-limits-on-a-low-volume-form-series.md`) forbids. The gate
would bless what the plugin's own rule prohibits.

### Blast radius

T2 was decided for A specifically because *"a claim with no prior art must be mechanically testable"*.
As written the mechanism does not run, and the failure is loud enough to be noticed but expensive enough
(a redesign of `--emit-imr`'s contract) to invite a shortcut.

### Mitigation (resolves all three at once)

1. `--emit-imr` writes **only** whitespace-separated numbers to **stdout**; the NOVEL SYNTHESIS marker
   goes to **stderr in every mode**. Piping stays clean, the label still reaches a human, and a user who
   redirects stdout to a file still sees it.
2. Round-trip becomes:
   `python3 …/lss_calc.py imr --values "$(python3 …/form_metrics.py --emit-imr fixture.csv)"`
3. Gate 220 asserts three things, not one: (i) the round-trip exits 0 and prints `UCL`/`LCL`; (ii)
   `--emit-imr` stdout matches `^[0-9eE+.,[:space:]-]*$`; (iii) the verbatim marker appears in
   **captured stderr** of a plain run. See M4 for why (iii) must be an execution assertion.
4. Name the fixture's minimum length in P5 and make it consistent with rule #5's stated minimum.

---

## H4 — Gate 219 sub-checks B+C are literal-phrase greps with only verbatim must-fail fixtures. A paraphrase — which is the actual CE-1 defect — passes green.

**Severity: HIGH** (silent; §0.4 asserts mechanical enforcement that does not exist)

### Trigger / repro

§0.4 states the binding rule and its enforcement:

> **Enforced mechanically by Gate 219 sub-check B** (§5.1) with a must-fail fixture, not by author
> discipline.

§5.1 sub-check C enumerates exactly six literals: `"magic bytes"`, `"server-generated filename"`,
`"resolve to absolute"`, `"single-use"`, `"300 second"`/`"5 minute"`, `"siteverify"`.

The owned source is `plugins/ravenclaude-core/rules/security.md:43-45`:

```
- Filenames from users: never trust them. Generate your own; record the original name as data…
- Path traversal: resolve to absolute, then assert the result is inside the allowed root.
- Uploads: validate type by content (magic bytes), not extension. Cap size at the boundary.
```

Now write the restatement CE-1 forbids, in different words:

> *"Never let the client's declared content type decide what a file is — read the leading bytes of the
> upload itself and match them against your allow-list. Reject the request at the boundary if it exceeds
> your size ceiling, and store it under an identifier you generated, never under the name the browser
> sent."*

That paragraph contains **none of the six phrases** and no vendor token, so sub-checks A, B and C all
pass. It is a verbatim-meaning copy of `security.md:43-45` in a file that will not track its
`refresh_when:` clause. The same holds for Turnstile: *"the challenge token stops being accepted after
five minutes and may only be redeemed once"* evades `"300 second"`, `"5 minute"` and `"single-use"`.

Every must-fail fixture the plan specifies for 219 is a **verbatim copy** (`Turnstile tokens are valid for
300 seconds`; `- Turnstile: verify server-side`; `validate type by content (magic bytes), not extension`).
The must-fail half therefore proves only that the literal string trips it. **There is no paraphrase
fixture anywhere in §5.1.**

The plan already knows this class — §5.3 writes exactly this limitation into Gate 221's script header
("*These gates measure 'a sentence is present', not 'the content is honest'*"). §5.1 has no equivalent
block, and §0.4 makes the opposite claim.

P2's anti-duplication probe uses the **same six phrases**, so it inherits the same blind spot; its
positive control (grep `ravenclaude-core/` first) proves the grep runs, not that it detects paraphrase.

### Blast radius

The single-source-of-truth invariant across `ravenclaude-core`'s constitution. Failure is silent and
compounding: the copy diverges the first time Cloudflare or the rule changes, and nothing points at it.

### Mitigation

1. Add a **paraphrase must-fail fixture** to sub-check C — the paragraph above, verbatim — and confirm
   the gate goes red on it. If it cannot, the gate's limitation is proven, which is the point.
2. Since it will not: copy §5.3's honesty and write the limitation into
   `check-forms-substrate-separation.py`'s own header, and **amend §0.4** to say the gate raises the floor
   and a human read at authoring time is required — it is already a named P2 pre-build step; make it a
   named P4 step too, since P4's seven rule files are where a paraphrase is most likely.
3. Cheap real teeth available at no extra cost: require every forms file that discusses uploads or
   Turnstile to contain **at least one** resolving markdown link into `plugins/ravenclaude-core/`
   (a positive requirement, not a negative one). A paraphrase with no link then fails, and the check is
   not defeatable by word choice.

---

## M1 — Gate 9b (ruff) is the one SKIPPED gate; the suite still exits 0, and DoD #8's literal command is broken on this host.

**Severity: MED** (CI is a real backstop; the loss is local and a wasted round-trip)

### Trigger / repro

Full suite, measured this session (`perl -e 'alarm 540; exec @ARGV' bash scripts/audit-gates.sh`):

```
  815 pass, 0 fail, 1 skipped
‼ 1 gate(s) SKIPPED — NOT a full pass. Re-run where the interpreter/binary is present:
  - Gate 9b (ruff) [no ruff]
SUITE EXIT=0
```

`scripts/audit-gates.sh:1610` gates on `command -v ruff`, and:

```
$ which ruff            -> ruff not found (rc 1)
$ python3 -m ruff --version -> ruff 0.15.8      <-- installed, just not on PATH
```

DoD #8 prescribes `python3 -m pip install --quiet --user ruff && ruff check .`. On stock macOS the
`--user` install lands in `~/Library/Python/3.9/bin`, which is not on PATH, so the second half exits 127
even after a successful install — which is exactly the state measured above.

The plan ships **three** new Python files (`form_metrics.py`, `check-forms-substrate-separation.py`,
`check-forms-honesty-markers.py`). Locally, none of them is ever linted, while the suite reports
`0 fail` and **exit 0**. Worse, DoD #10's own attribution rule — *"A failure present in the baseline is
not ours"* — will record the skip in P0's `baseline-gates.txt` and thereby license shipping it.

### Blast radius

Local only; `_skip_or_fail` hard-fails under `CI=1`, so a ruff violation is caught on push. Cost is a red
CI round-trip, plus the erosion of "green suite ⇒ done".

### Mitigation

- P0 acceptance 6 records `ruff --version`; make it a **hard STOP** rather than a recording, and use the
  invocation that works here: `python3 -m ruff check .`.
- Add to DoD #10: `grep -c 'SKIPPED' <suite output>` → **0**. The suite's own exit code does not carry the
  skip; nothing else in the plan reads it.
- Fix DoD #8 to `python3 -m pip install --quiet --user ruff && python3 -m ruff check .`.

---

## M2 — Reachability is measured by file existence and is blind to plugin enablement. One of the five priors lands in a plugin that is DISABLED on the owner's own machine.

**Severity: MED** (raises R6's probability well above the plan's "Low-Med"; the probe cannot see it)

### Trigger / repro

```
$ python3 - <<'PY'  # ~/.claude/settings.json
total keys: 181  enabled: 50  disabled: 131
  web-design@ravenclaude          True
  ravenclaude-core@ravenclaude    True
  process-improvement@ravenclaude False     <-- DISABLED
PY
```

P8 prior #5 is `plugins/process-improvement/agents/process-analyst.md` → `form-telemetry-and-control`.
That agent does not load in the owner's own session. `form-telemetry-and-control`'s primary routing
targets (`process-improvement`'s `lean-six-sigma-blackbelt` skill, the DMAIC seam) are in the same
disabled plugin — the one skill the plan calls *"the run's novel-synthesis surface"* routes into
something that is not loaded on the machine that ships it.

P8's acceptance test:

> verified by a loop that **resolves** `plugins/forms-engineering/skills/<name>/SKILL.md` from each
> referrer, not by reading prose.

`test -e` on a path in a disabled plugin succeeds. The positive control (misspell a skill name) proves
the resolver can go red on a **typo**, not on a **dead route**. The probe reports 5/5 green while 1/5 is
inert here and 3/5 die for any consumer who disables `web-design`.

### Blast radius

R6 (rot). The plugin has zero agents by ruling; P8 is the only thing paying for that ruling. With 131 of
181 plugins disabled as the ambient condition, "a file names it" is not the same property as "something
routes to it".

### Mitigation / accepted risk

- Extend the reachability probe to read `~/.claude/settings.json` `enabledPlugins` and **report** each
  referrer's enabled state. Do not fail on it — the owner's config is not the consumer's — but print it,
  so "5 referrers, 4 in enabled plugins" is visible rather than invisible.
- Give `form-telemetry-and-control` a **second** inbound prior from an enabled plugin. The natural one
  within R5's five-file budget: swap the `process-analyst.md` prior for one in
  `plugins/data-platform/` or keep both and re-open R5 for a sixth file with this measurement as the
  justification. R5 explicitly says a sixth file requires re-opening the ruling — this is the evidence
  that would justify it.
- **Or waive explicitly:** record that the plugin's telemetry seam is dark whenever
  `process-improvement` is disabled, and that this is accepted. Silence is the thing to avoid.

---

## M3 — Gate 219's file-type scope is unspecified, and P6's own hook must contain the tokens the gate forbids. CE-6 recurs.

**Severity: MED** (fails loudly at P6; the danger is the remedy, which is exactly R4)

### Trigger / repro

§5.1 sub-check A: *"A vendor token outside the 2 allowlisted substrate files is a violation unless its
line satisfies sub-check B"*, and sub-check B requires the line to be *"a markdown link into
`plugins/ravenclaude-core/`"*. §5.1 adds *"Filenames are checked too"*. Nowhere does it scope the gate to
`*.md`.

P6 requires `hooks/flag-form-antipatterns.sh` to detect:

> a CAPTCHA/Turnstile widget introduced with no server-side verification in the same change — the message
> **cites** `cloudflare-who-gets-in.md`

A hook cannot detect a Turnstile widget without matching `turnstile` / `cf-turnstile` in its own source,
and a **shell line can never be a markdown link**. Same for `scripts/form_metrics.py` if it mentions any
vendor. So `--check 219` goes red the moment P6 lands, and the two available remedies are: add
`hooks/*.sh` to the allowlist, or drop `Turnstile` from the token list. Both are the blocklist being
"quietly trimmed to fit the content" — the CE-6 mechanism the plan opens §5.1 by declaring fixed.

Second, smaller collision: sub-check C's phrase `"single-use"` is generic. Best-practice rule #3
(`every-public-form-post-needs-a-double-submit-guard.md`) is *about* one-shot submit tokens and will very
plausibly use the words "single-use" in a sense that has nothing to do with Turnstile replay — a false
positive on the plugin's own owned content.

### Mitigation

- Write the scope into P1, **before** the script exists: sub-checks A/B/C apply to `**/*.md` under
  `plugins/forms-engineering/` **only**; `hooks/`, `scripts/` and `tests/fixtures/` are out of scope by
  construction and the reason is in the script header. A hook's detection strings are code, not prose.
- Replace bare `"single-use"` with a co-occurrence requirement (`single-use` **and** `token`, within N
  lines of a Turnstile/challenge mention), so rule #3 does not trip it.
- Add a must-pass fixture that is a `.sh` file containing `cf-turnstile`, proving the scope holds.

---

## M4 — Gate 221 sub-check A contradicts §6.1's surface list, and it is satisfied by the marker merely *appearing in source* — never by it being printed.

**Severity: MED**

### Trigger / repro — part 1, the contradiction

§5.3 sub-check A: *"every file that co-occurs an SPC/DMAIC term (control chart, X-mR, DMAIC, **sigma**,
common-cause, special-cause) with a form-analytics term (`form_start`, **abandonment**, drop-off,
**completion rate**) carries the verbatim marker string"*.

§6.1 lists the surfaces required to carry it: `knowledge/form-telemetry-and-spc.md`,
`skills/form-telemetry-and-control/SKILL.md`, and `form_metrics.py`'s output. **Three.**

But §3.4 rule #5 is `do-not-put-three-sigma-limits-on-a-low-volume-form-series.md` — "sigma" is in its
filename and unavoidably in its body, and "form series"/"abandonment"/"completion" are its subject. Same
for `templates/form-telemetry-plan.md`. Both co-occur both term families; neither is in §6.1's list.
Gate 221 goes red at P4 on the plugin's own required content, and the remedy under time pressure is to
narrow the term list — R5/CE-7's failure mode.

### Trigger / repro — part 2, the silent half

The marker is required to be *"printed by `form_metrics.py`'s own output"*. Sub-check A is a
**file-level string co-occurrence check**. A marker sitting in a module docstring, a comment, or an
`if args.verbose:` branch that no gate exercises satisfies it identically to one printed on every run.

This is the repo's recorded trap verbatim — *a grep is satisfied by the thing being **described***; the
`[[r2_buckets]]`-in-a-comment case flipped a tracker item to DONE with nothing bound. The plan quotes that
very incident in P7 and then reproduces its shape in Gate 221.

Related, and the prompt's question: if `form_metrics.py` is **imported as a library** rather than run as a
CLI, a label printed inside `main()` never executes. Nothing in the plan addresses that path.

### Mitigation

- Add rule #5 and `templates/form-telemetry-plan.md` to §6.1's required-surface list (the marker is
  verbatim; adding it to a one-rule file costs nothing), **or** exempt files whose only SPC term is in a
  prohibition (harder to specify — prefer the first).
- Move the printing assertion out of Gate 221 and into **Gate 220, which already executes the script**:
  assert the verbatim marker in **captured stderr** of a plain run and of `--emit-imr` (see H3's
  stdout/stderr split). An execution assertion cannot be satisfied by a docstring.
- For the library path, emit the marker from module import (a `warnings.warn` or a stderr write in the
  public entry function), and say in the header that a caller who suppresses stderr owns the omission.

---

## M5 — Every pinned `path:line` citation rots, and P8 is the phase that rots them. No gate detects it.

**Severity: MED**

### Trigger / repro

The plan pins `security.md:43-45`, `cloudflare-who-gets-in.md:51,53`, `frontend-implementer.md:41,48,60`,
`accessibility-auditor.md:48,92`. All four are **accurate today** — I opened each:

```
security.md:45              -> "- Uploads: validate type by content (magic bytes), not extension…"
cloudflare-who-gets-in.md:51 -> "- **Secret key — private.** …"
frontend-implementer.md:48   -> "- **Forms**: native HTML form patterns first…"
accessibility-auditor.md:92  -> "- Auth / login / CAPTCHA … → `ravenclaude-core` `security-reviewer` (mandatory, zero-exception…)"
```

`accessibility-auditor.md:92` is load-bearing three times over: §0.3 uses it to justify the plugin's
existence, R2 grounds the zero-agent ruling on it, and P3 writes it into every skill's `## Not this skill`
block. Now run P8, which by ruling R5 inserts up to 3 body lines into that same file:

```
$ awk 'NR==48{print; print "<3 prior lines>"; …}' plugins/web-design/agents/accessibility-auditor.md > /tmp/aa.md
line 92 BEFORE: - Auth / login / CAPTCHA surfaces … → `ravenclaude-core` `security-reviewer` (mandatory, zero-exception…)
line 92 AFTER : - UX flow / interaction-pattern problems → `ux-designer`
```

**P8 invalidates the citation that P3 already shipped**, in the same run, and nothing notices:

- `scripts/check-md-links.py:19-20` — *"For a target with an anchor suffix (path/to/file.md#section), only
  the path part is resolved; **the anchor fragment itself is not validated**."*
- A link target written literally as `…/rules/security.md:43-45` is not a path that exists, so Gate 29
  would go **red** — meaning the plan's own citation style cannot be expressed as a checked link at all.
- Gate 219 sub-check B keys on citation **form** (is it a link into `ravenclaude-core/`), never on
  citation **target**.

### Blast radius

Every cite-don't-restate pointer in the shipped tree, i.e. the entire CE-1 defense, degrades to "a link to
the right file, a line number to the wrong line" — which reads authoritative and is wrong.

### Mitigation

- Cite by **stable anchor text**, not by line: `security.md` **§File handling**;
  `accessibility-auditor.md` **"Auth / login / CAPTCHA … zero-exception"**;
  `cloudflare-who-gets-in.md` **"The widget alone proves nothing"**. All four exist as headings or
  distinctive sentences today.
- Add one assertion to Gate 219: for each cited file, the quoted anchor text must still be found in it
  (`grep -qF`). That is a real, cheap must-fail half — delete the sentence upstream, the gate goes red.
- Keep line numbers **only** in the plan and in `claims-table.md`, never in shipped content.
- Sequence P8's edits to append **below** line 92 where possible, and re-read §0.3's citations at P9.

---

## L1 — rerere is armed on this repo with 93 cached resolutions, at least one covering gate blocks and one covering the marketplace plugin array.

**Severity: LOW-MED** — mechanism verified, bad outcome NOT reproduced (see §Cannot reproduce)

### Trigger / repro

```
$ git config --get rerere.enabled            -> true
$ git config --global --get rerere.enabled   -> true
$ ls .git/rr-cache | wc -l                   -> 93
$ grep -rl "audit-gates\|── Gate " .git/rr-cache | head
.git/rr-cache/69d9ef08…/preimage
.git/rr-cache/69d9ef08…/postimage
.git/rr-cache/6ee10683…/postimage
$ grep -rl '"source": "./plugins' .git/rr-cache | head
.git/rr-cache/5af44cec…/preimage
.git/rr-cache/a191f44d…/preimage
```

The plan appends to **both** of the files those cached resolutions cover: `scripts/audit-gates.sh` (four
appends, §2.3's baton) and `.claude-plugin/marketplace.json` (the 182nd entry). P8's pre-build gate says
*"the rebase may be stale by now"* — i.e. the plan anticipates a **local rebase mid-run**. On any conflict
in those two files, rerere applies a stored postimage **without prompting**, and `git status` shows it
resolved.

Most outcomes here are loud: a partially-dropped gate block trips Gate 195 parity
(`check-gate-registration.py`, verified exit 0 today, `--self-test` exit 0), and a reverted
`marketplace.json` version trips the plugin.json/marketplace mirror gate. I could not construct a green
one — hence LOW-MED, not higher.

### Mitigation

- Do every mid-run integration as `git -c rerere.enabled=false rebase origin/main` (or `merge`).
- After **any** integration, re-assert two facts before continuing: `grep -c "Gate 218"
  scripts/audit-gates.sh` ≥ 2 (main-sequence block + dispatcher arm — measured 2 today, at `:523` and
  `:7477`), and `grep -c 'removed rather than re-cited' plugins/web-design/skills/conversion-design/SKILL.md`
  ≥ 1.
- Per the repo's recorded incident, if any local **merge** is performed, assert
  `git log -1 --format='%p' | wc -w` = 2 before pushing.

---

## L2 — DoD #23's scope wall flags the plan's own P1 fixtures as a scope breach.

**Severity: LOW** (loud, trivial, but it is a self-contradicting acceptance test and those get waved through)

### Trigger / repro

P1, "Files touched": *"`scripts/check-forms-substrate-separation.py` (new) + **`tests/fixtures/`** for it"*
and *"`scripts/check-forms-honesty-markers.py` (new) + its fixtures"*.

DoD #23: *"`git diff --name-only origin/main` contains **zero** paths outside
`plugins/forms-engineering/`, `scripts/`, `.claude-plugin/marketplace.json`, and the **five** enumerated
reciprocal-prior files. **Any sixth file is a scope breach.**"*

`tests/fixtures/**` is not in that list. It is, however, an allowed glob in `.repo-layout.json`
(verified: `tests/fixtures/**` is present; `tests/fixtures/` already holds `bad-marketplace.json`,
`bad-plugin.json`, etc.), so the layout hook allows exactly what the scope wall forbids.

### Mitigation

Add `tests/fixtures/**` to DoD #23's allowed set. One line.

---

# Verified against the critic

I re-ran G4a's claims rather than restating them.

### Still open in the synthesized plan

| Critic risk | Status after synthesis | Evidence |
|---|---|---|
| **R2 — collision with #959** | **Open, and the mitigation is broken.** Both PRs verified `state: OPEN, mergeable: MERGEABLE, mergeStateStatus: CLEAN`. The plan's STOP gate cannot ever pass → **H1**. | `gh pr view 959/960 --json …` |
| **R4 / CE-6 — separation gate negotiated down** | **Open in a new place.** §5.1 fixes the *markdown* contradiction; P6's hook re-creates it in `.sh` → **M3**. | §5.1 has no file-type scope |
| **R5 / CE-7 — honesty label passes while content drifts** | **Open, and wider than scored.** Gate 221's own header documents the paragraph-level blind spot honestly; nobody documented the **execution** blind spot (marker in source ≠ marker printed) → **M4**. | §5.3 vs §6.1 |
| **R6 — the plugin rots** | **Open, probability under-scored.** 131/181 plugins disabled; `process-improvement` is one of them → **M2**. | `~/.claude/settings.json` |
| **R14 — whole-tree lint blocks the PR** | **Inverted.** The plan scores it Low-Med/Low. Measured, the ruff gate does not fail — it **skips**, and the suite still exits 0 → **M1**. | `815 pass, 0 fail, 1 skipped`, `SUITE EXIT=0` |

### Closed by the plan (verified, not taken on trust)

- **CE-5 / R3 — Gate 195 blindness.** Genuinely closed. §5.4's registration triple matches reality:
  `Supported:` at `scripts/audit-gates.sh:1149`, Gate 218's dispatcher arm at `:522`, main-sequence block
  at `:7477`. `python3 scripts/check-gate-registration.py` → exit 0; `--self-test` → exit 0. The plan's
  warning against verifying by `grep "Gate <N>"` is correct and its `--check`-exit-code alternative works
  for numbers that have arms (218 → exit 0).
- **R9 — B's `wc -l | tail -1` acceptance test.** Correctly closed; the PI phases are deleted from the
  plan and PR #960 carries that work.
- **F2 — does `check-marketplace-claims.py` need a non-empty `agents/`?** Discharged.
  `scripts/check-marketplace-claims.py:162-165`: `agents = plugin_dir / "agents"; if not agents.is_dir(): return 0`.
- **R3 (plan) — `substrate/**` is denied, no `.repo-layout.json` edit needed.** Verified: the plugin globs
  are `plugins/*/{skills,knowledge,best-practices,templates,scenarios,commands,hooks,scripts,…}/**` plus
  the four top-level files — every directory the plan builds is allowed, and `substrate/**` is absent.
- **§11.1 — `turnstile-spin` is not a marketplace routing target.** Confirmed: it appears in the session's
  skill roster but `ls -d plugins/*/skills/turnstile-spin` has no match.

### Where the critic (and the G5 brief's own suspicion) is wrong

- **"#959 and #960 conflict with each other on `.claude-plugin/marketplace.json`" — FALSE.** #959's hunk is
  at line **364** (`web-design`, `0.16.1 → 0.16.2`); #960's is at line **504** (`process-improvement`,
  `0.2.2 → 0.3.0`). 140 lines apart, far outside 3-line context. Both PRs report
  `mergeStateStatus: CLEAN` **simultaneously**. Merge order is immaterial and neither rebase is required.
  The plan's §2.1 diagram implying an ordering constraint between them is over-specified — only the
  *forms* branch depends on both, and only for gate numbering and the conversion-design text.
- **"Someone might take gate 219/220/221 first" — no such race exists.** `gh pr list --state open` returns
  exactly **two** PRs (959, 960). `origin/main`'s gate ceiling is **217** and its `Supported:` list ends
  `…216, 217.`; the harden branch adds 218. Nothing else claims a number.

---

# Cannot reproduce

Required section. These are things I suspected, chased, and could **not** trigger. Several were in the
brief that assigned me; saying so is the point.

1. **A merge conflict between PR #959 and PR #960.** Chased explicitly per the brief. Their
   `marketplace.json` hunks are 140 lines apart and both PRs are `CLEAN` right now. No conflict, no order
   dependency, nothing for rerere to resolve on the GitHub side (those merges happen server-side, where
   the local rr-cache is not consulted at all).
2. **A rerere-produced wrong resolution or one-parent merge in THIS repo.** The mechanism is verified
   (`rerere.enabled=true`, 93 entries, gate-block and plugin-array preimages present), but I could not
   construct an outcome that ends green: partial gate loss trips Gate 195 parity, and a reverted version
   mirror trips the plugin.json/marketplace mirror gate. Filed as **L1** at LOW-MED with that limit stated,
   not inflated.
3. **Whether Gate 219 / 220 / 221's must-fail fixtures can actually fail.** The scripts do not exist yet.
   H4 and M3/M4 are read off the **specification** in §5.1/§5.2/§5.3 — a specification defect is real, but
   I did not execute a gate that has not been written, and I am not claiming I did.
4. **`chmod +x` denial on `plugins/forms-engineering/hooks/`.** The plan predicts a plain `chmod +x` will
   pass because the deny is scoped to `ravenclaude-core/{hooks,scripts}`. Testing it requires creating the
   plugin directory, which is outside a read-only red-team's remit. Untested; the plan's `!`-prefixed
   escape is the right fallback either way.
5. **Gate 206 tripping on the draft `description`.** No draft description exists. `check-description-count-literals.py`
   exists and its teeth pass in the suite (`16 count shapes caught … 15 domain literals spared`), so the
   plan's "verify the draft before committing" step is sound as written.
6. **A currently-red suite.** I looked for one; there isn't one. `815 pass, 0 fail, 1 skipped`. P0's
   baseline step will therefore record a **clean** baseline — which is good, except that it also records
   the ruff skip as pre-existing (M1).
7. **External claim rows 74–105** (WCAG criteria, GOV.UK's rationale, the ventureharbour case, Turnstile's
   plan pages) and **row 101's negative literature finding.** Not re-verified — same limit G4a declared in
   its §6. Anything I said about them would be invented.
8. **`claims-ravenpower.md` rows 48–73 against a live `RavenPower-Website` checkout.** Not probed. P7's
   anti-rot re-verification-command design is the right treatment and I have nothing to add to it.
9. **Whether the ~80% pointer-ratio STOP in P3 would actually fire.** No content exists to measure. It is a
   well-shaped falsifier; I could not exercise it.

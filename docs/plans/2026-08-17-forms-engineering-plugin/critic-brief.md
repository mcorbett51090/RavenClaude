# G4a — CRITIC brief · run `forms-process-expertise`

**Date:** 2026-08-17 · **Authored by:** neither panel. **Produces no third plan.**
**Read from disk:** `scope.md`, `plan-A.md`, `plan-B.md`, `gap-delta.md`, `claims-table.md`,
`claims-repo.md`, `claims-process-improvement.md`, `claims-ravenpower.md`, `claims-external.md`,
`plugins/ravenclaude-core/CLAUDE.md`, `AGENTS.md`.

---

## §0 — Method, and the controls I ran

Everything in §1 is a **re-run probe**, not a re-read. Where a plan or a claim row reports an
empty/zero result, I ran a **positive control** before accepting it, per this repo's own rule that
*"an empty result is a claim about the PROBE until you show the probe can return the opposite."*

Probes run against `/Users/matthewcorbett/RavenClaude` (primary checkout) and, where provenance
mattered, against the run's worktree `/Users/matthewcorbett/RavenClaude/.claude/worktrees/forge-forms-process-expertise`
(`8a253065`, confirmed **0 behind `origin/main`** — `git rev-list --count 8a253065..origin/main` → `0`;
scope.md's freshness claim is **true**).

Four of the plans' load-bearing facts I **confirmed**, and say so up front so the reproach below is
calibrated: highest existing gate is **217** (`grep -oE 'Gate [0-9]+' scripts/audit-gates.sh | sort -n | tail`);
`scripts/audit-gates.sh` is **7,480 lines**; `plugins/report-regeneration/` and `plugins/team-portfolio/`
have **no `agents/` directory**; `grep -c "lss_calc" scripts/audit-gates.sh` → **0** (row 39's
"zero gate coverage" is real).

I also **discharged both of Plan A's own falsifiers**, which A flagged as "the single most likely way
this plan is wrong". Neither fires:

- **F1 — does `web-design` already own discipline (c)?** **No.**
  `plugins/web-design/agents/frontend-implementer.md:48` is a single bullet
  ("Forms: native HTML form patterns first; controlled React forms when needed; validation strategy");
  `plugins/web-design/agents/accessibility-auditor.md:48` is a single bullet on form a11y. Neither file
  contains bot defense, upload handling, webhook idempotency, or PII. **F1 does not fire.**
- **F2 — does `check-marketplace-claims.py` require a non-empty `agents/`?** **No.**
  `scripts/check-marketplace-claims.py:163-165` — `agents = plugin_dir / "agents"; if not agents.is_dir(): return 0`.
  **F2 does not fire.**

That is the calibration. What follows is what the two panels could **not** see, because they saw it
together.

---

## §1 — CORRELATED ERRORS

Seven. Five are verified by command output; two are argued from the artifacts' own text. Ranked by
blast radius.

---

### CE-1 (HEADLINE) — Two "unowned topic" findings are **false**, produced by the same broken grep idiom, and both plans build content on them

**What both plans assume.** Claims-table rows 14 and 16 report zero-hit greps, both marked `settled`:

- Row 14 (`claims-table.md:24`): *"Grep for 'captcha' or 'turnstile' … returns zero hits. There is NO
  Turnstile/CAPTCHA content inside the RavenClaude marketplace repo."* Method recorded as
  `grep -rli "captcha/turnstile" plugins/` → exit 1.
- Row 16 (`claims-table.md:26`): *"Grep for 'file upload'/'file-upload' … returns zero hits. Topic is
  effectively unowned."* Method recorded as `grep -rli "file upload/file-upload" plugins/` → exit 1.

**Why it is wrong.** Both patterns are a **single literal containing a slash**. `grep` was asked
whether the string `captcha/turnstile` appears anywhere. It does not. Neither probe ever tested for
`captcha` or for `turnstile`. The recorded exit-1 is a fact about the pattern, not about the repo.

**The positive controls:**

```
$ grep -rli "file upload/file-upload" plugins/ ; echo "exit=$?"
exit=1                                    # reproduces the recorded result

$ grep -rliE "file[ -]upload" plugins/ | wc -l
23                                        # the probe can return the opposite

$ for p in captcha turnstile honeypot "form abandonment"; do
    printf "%-20s: " "$p"; grep -rli "$p" plugins/ | wc -l; done
captcha             : 18
turnstile           :  6
honeypot            :  0
form abandonment    :  0
```

**What is actually already owned — and where:**

| "Unowned" topic | Where it already lives | What it already says |
|---|---|---|
| File-upload hardening | `plugins/ravenclaude-core/rules/security.md:43-45` | *"Filenames from users: never trust them. Generate your own…"* · *"Uploads: validate type by content (magic bytes), not extension. Cap size at the boundary."* |
| Turnstile / server-side verification | `plugins/ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md` | A dated (`last_verified: 2026-07-21`), sourced concept doc citing Cloudflare's **server-side-validation** page, and whose `refresh_when:` clause names *"the 300-second token lifetime, single-use replay rule"* — i.e. rows 93/94 verbatim. Registered in `plugins/ravenclaude-core/concepts.json` (21 `turnstile` mentions). |

**Blast radius.**

1. **Plan A** ships `best-practices/a-content-type-allow-list-is-not-a-file-type-check.md` (Phase 4 rule
   #7: *"validate bytes, random server-generated filenames"*) — a restatement of two lines of the
   **constitution every agent already inherits**. It also ships
   `a-turnstile-token-is-not-verified-until-siteverify-returns.md` and a `knowledge/form-anti-abuse.md`
   Turnstile block — a second, unlinked copy of a concept doc that has a maintained refresh trigger. A's
   own §6 forbids exactly this ("Duplication is how a single source of truth dies"), and A's Phase 3
   anti-duplication probe only greps for the **`web-design`** rules of rows 1–3 — it would never look in
   `ravenclaude-core/rules/`.
2. **Plan B is worse hit**, because row 16 is load-bearing for a *rejection*. B's Phase 3 routing table
   (`plan-B.md:256`) says file-upload is *"a real, confirmed gap (row 16); this skill owns it directly."*
   And B's **Alternative 3** — the cheapest, lowest-rot design in either plan (a pure-routing skill with
   no owned best-practice files) — is rejected **solely** because *"the file-upload sub-topic has no
   existing routing target (row 16, confirmed zero hits)."* The routing target exists. B rejected its own
   cheapest alternative on a broken grep.
3. The duplicate lands in the **concepts graph's** blind spot: a fact with a `refresh_when` clause in core
   and a hard-coded copy in a domain plugin will silently diverge the first time Cloudflare changes the
   token lifetime.

**Why no gap-delta could see this.** Both panels consumed the same `claims-table.md`. The row said
`settled`. Agreement here is not corroboration — it is one broken probe, counted twice.

---

### CE-2 — Both plans schedule a cross-plugin fix for a defect **already fixed on an unmerged sibling branch**, and A's version of the fix is strictly worse than the one already authored

**What both plans assume.** Row 3 (`claims-table.md:13`): `web-design/skills/conversion-design/SKILL.md`
§3 carries an unsourced field-count/completion benchmark table (1 field 35–50% … 7+ <10%).

- **Plan A** builds a mandatory sub-phase on it (`plan-A.md:505-513`, "⛔ The reconciliation this phase
  must not skip"): edit `conversion-design` §3 to add *"the benchmark table is a **prior, not a law**"*
  plus a bidirectional link, and *"row 3's table has no source citation recorded — flag it, do not
  silently inherit it as fact."*
- **Plan B** ships the same counter-evidence as new content in Phase 2 (`plan-B.md:214-217`).
- **gap-delta.md** lists it under *Convergent*: *"both state it as a distribution/prior, not a causal law."*

**Why it is wrong.** The table is gone, and the fix is better than either plan's:

```
$ git log -1 --format='%h %ad %s' --date=short
158e5c80 2026-08-17 fix(web-design): conversion-design was shipping field-count folklore as a benchmark

$ git branch -a --contains 158e5c80
* fix/conversion-design-field-folklore
  remotes/origin/fix/conversion-design-field-folklore

$ git merge-base --is-ancestor 158e5c80 origin/main && echo YES || echo NO
NO
```

`plugins/web-design/skills/conversion-design/SKILL.md` in the primary checkout now reads, at §3:
*"⛔ 'Fewer fields always converts better' is folklore — do not repeat it"*, with the **14% drop /
19.21% relabel / 30+ questions at 53%** counter-evidence and a cited source
(`ventureharbour.com/how-form-length-impacts-conversion-rates/ — retrieved 2026-08-17`), and line 63:
*"Both were **unsourced** … They were **removed rather than re-cited**."*

The worktree the panels read (`8a253065`) still has the old table
(`grep -c "35–50%" <worktree>/…/conversion-design/SKILL.md` → `1`), so row 3 was **accurately captured**
and is **already obsolete**. The fix is on a pushed sibling branch, authored the same day, not yet merged.

**Blast radius.** A's Phase 9 edits the exact section an in-flight branch rewrites — a conflict on the
one file A already flags as its "largest blast radius" phase. Worse, A's prescribed remedy ("call the
table a prior, not a law") would **preserve an unsourced table** that the sibling branch **deleted as
unsourced**; if A lands second, someone resolves the conflict by re-litigating a decision already made
correctly. B's version silently duplicates the counter-evidence and its citation into a second plugin.

**Why no gap-delta could see this.** Both panels read the same worktree at the same SHA. Neither had
visibility into a sibling branch. Shared evidence provenance, correlated blind spot — and it is listed
in `gap-delta.md` as *convergent agreement*, which is precisely how this class of error survives.

---

### CE-3 — Both plans apply the house rule's **strictest** form to a case the rule explicitly **carves out**, and neither cites the carve-out

**What both plans assume.** That `ravenclaude-core/CLAUDE.md`'s indistinguishable-output test mandates
zero agents. A: *"Zero agents is … the rule's answer"* (`plan-A.md:75`). B: *"all four fail the 'ship an
agent' bar … Zero new agents ship"* (`plan-B.md:44-51`).

**What the rule actually says** (`plugins/ravenclaude-core/CLAUDE.md:11, 22, 24`):

- Line 11 scopes the test: *"**Test before adding a plugin-specific architect or reviewer**: could a
  competent core agent … produce indistinguishable output?"*
- Line 20 names the two failure modes it prevents: **dispatch ambiguity** and **rubric drift** —
  both review-role failures.
- Line 22: *"**The rule's strictest grip is on *review* roles (security-reviewer, architect), which never
  fork.** A *generalist* concern may earn its own plugin when it splits cleanly into 'domain-neutral
  hygiene' (stays core) and 'deep specialist craft' (the plugin)."*
- Line 24 admits a **second** carve-out on the same litmus.

Both carve-outs **shipped agents**: `ls plugins/project-management/agents/*.md | wc -l` → **4**;
`ls plugins/memory-engineering/agents/*.md | wc -l` → **3**. Neither plan mentions either carve-out;
`grep -c "carve-out" plan-A.md plan-B.md` → 0 / 0.

**Why this matters here.** The carve-out litmus is *"hygiene → core; running the discipline → the
plugin."* Forms splits on exactly that seam: label/placeholder/validate-on-blur hygiene already lives in
`web-design` + `ravenclaude-core/rules/security.md` and **stays there**; forms-as-instrumented-process
(the (a) discipline, which both plans agree has no owner and no literature) is the deep craft. That is
the same shape that admitted `project-management` and `memory-engineering`. I am **not** ruling that an
agent should ship — that is a design call and I produce no plan. I am ruling that **both panels answered
a question the rule does not ask of this case**, and reported the answer as "the rule's answer".

**Blast radius.** B **names the consequence and accepts it anyway** (`plan-B.md:392-402`): *"nothing in
the marketplace's agent `works_with` graph points here … A skill with no agent route and no inbound
cross-link is a documented rot pattern in this repo … **This is a real, accepted trade-off, not a solved
problem**."* A avoids rot only by editing five other plugins (Phase 9), which B reads as scope-barred and
which CE-2 shows now collides with an in-flight branch. So the shared ruling produces either **a plugin
that rots** or **a plan whose soundness depends on its most contested phase** — and the rule's own text
offered a third door neither panel opened.

---

### CE-4 — "Zero agents ⇒ zero budget" is false, and A's cost comparison is a category error. Both inherited the framing from `scope.md`

**What both plans assume.** A (`plan-A.md:36, 75`): *"this plugin ships **zero agents** … so it costs
**zero** budget"* · *"Cost against the ~15K budget: **0 tokens**."* B (`plan-B.md:51-54`): *"the ~15K
agent-description budget [is a] non-issue for this plugin **by construction**."*

**Why it is wrong.** The ~15K figure names agent descriptions specifically, so the literal arithmetic is
fine — but both plans use it as *the* cost axis and conclude the plugin is free. It is not. Per this
repo's own research:

- `docs/research/2026-06-24-claude-subreddit-scan/README.md:56`: *"a skill loads in three tiers —
  frontmatter (`name`+`description`) **preloaded for *every* skill every session**"*.
- `docs/research/2026-06-21-claude-subreddit-scan/README.md:53`: the `/plugin` Discover tab's
  **Context cost** is *"tokens added to every turn"*, and the **Will install** inventory enumerates
  *"commands/agents/skills/hooks/MCP+LSP servers"* — skills counted alongside agents.
- `docs/best-practices/2026-06-23-plugin-best-practices-audit.md:35`: *"The only documented length limit
  is the **skill** listing truncation at **1536 chars**"* — i.e. skills have a listing budget of their own.

A ships 7 skills + 2 commands; B ships 6 skills + 1 command. That is resident per-turn context in both
cases, not zero.

**The category error, A only but load-bearing for the shared ruling.** A's Ruling-1 evidence point 4
(`plan-A.md:34-38`) argues *"Enable-cost inverts the usual objection … Extending `web-design` instead
forces a consumer who wants forms expertise to enable a plugin carrying **7 agent descriptions** they may
not want. Standalone is the *cheaper* option here."* Two defects:

1. It compares the **marginal** cost of standalone against the **total** cost of `web-design`. The
   marginal agent-description cost of EXTEND is also **zero** — the extend option adds skills, not
   agents. On this axis the two options are **tied**, not inverted.
2. It is contradicted by A's own Phase 9, which places the routing priors that make the skills reachable
   inside `web-design/agents/*.md`, `ravenclaude-core/agents/security-reviewer.md`, and
   `process-improvement/agents/*.md`. A consumer who wants A's forms capability to *work as designed*
   must enable `web-design` **and** `forms-engineering` — strictly more resident context than extend,
   not less.

**Where the framing came from.** `scope.md:85-86` binding constraint #2 names only *"Agent-description
budget (~15K…). **Every new agent has a real cost**; 131 plugins are already disabled for this reason."*
The framing handed both panels one cost axis. Both priced that axis and declared the plugin free. Neither
priced skills, commands, or the 182nd catalog entry. **This is an orchestrator-framing error, inherited
identically by both panels — the exact class a gap-delta cannot surface.**

---

### CE-5 — Both plans add gates to `audit-gates.sh` while blind to **Gate 195**, the meta-gate that audits gate registration

```
$ grep -c "195" plan-A.md plan-B.md
plan-A.md:0
plan-B.md:0
```

Gate 195 exists (`scripts/audit-gates.sh:6800-6809`) and runs
`scripts/check-gate-registration.py` for *"reachability + number-uniqueness + **dispatcher/Supported
parity** + exit-2 specificity"*, plus a `--self-test` teeth gate. The file's own banner comment, repeated
above every recent gate: *"⛔ Registered in **BOTH** this main sequence **AND** the `--check` dispatcher
above **+** the `Supported:` string … a passing suite is not evidence your gate is in it (v0.243.0: Gate
184 was unreachable for a whole release while the suite reported green)."*

**A's failure mode is concrete.** A's Phase 1 files-touched list (`plan-A.md:175-177`) says: add Gate 218
to `audit-gates.sh` *"**and** its number appended to the `Supported:` string at line ~1140."* It never
mentions the `<n>)` **case arm** in the `--check` dispatcher (`scripts/audit-gates.sh:263`ff). Following A
literally puts 218 in `Supported:` and not in the arms → **Gate 195's dispatcher/Supported parity check
goes RED** → and per this repo's recorded masking defect, a red gate hides every later gate in the same CI
step. A's own acceptance test `--check 218 → PASS` would in fact fail (the `*)` arm exits 1, verified at
`audit-gates.sh:1138-1142`), so the error self-announces — but as an unexplained failure in the phase that
edits shared infrastructure, not as a known step.

**B's failure mode is broader.** B never names a gate number, the `Supported:` string, or the dispatcher
anywhere. B's registration check is `grep -c "check-novel-synthesis-marker\|…" scripts/audit-gates.sh`
must return ≥3 (`plan-B.md:411`) — **grep for a script name is not evidence of registration**, and it is
the same shape as the inverted-audit trap this repo recorded on 2026-08-17. B's Phase 9 backstop
("confirm the total gate count increased by exactly 5") is also not well defined: the suite counts
`gate` **assertions**, and every recent numbered gate registers **two** (main + `--self-test` teeth, e.g.
Gate 195 at `audit-gates.sh:6805` and `:6807`), while B's Gate-30 work adds assertions inside an existing
gate rather than a new number. "Exactly 5" cannot be checked as written — and `.github/workflows/validate-marketplace.yml:7` puts the suite at **593 gates**, so an off-by-a-few count is not a signal anyone would notice.

**Blast radius.** Both plans edit the single most shared file in the repo (7,480 lines, every plugin's CI)
without the one check that exists specifically to catch a mis-registered gate.

---

### CE-6 — Both plans claim a separable neutral/substrate split while putting **vendor-specific content in the neutral layer**. A's own Gate 218 would fail A's own Phase 2/4/5 files

**What both plans assume.** That "domain-neutral core + separable RavenPower substrate" is satisfied by
file placement (B) or a token blocklist (A).

**A's internal contradiction is mechanical and immediate.** Ruling 3 (`plan-A.md:88-94`) defines the
substrate layer as **exactly two files** — `knowledge/ravenpower-form-substrate.md` and
`skills/wire-form-substrate/SKILL.md` — and Gate 218 forbids the tokens
`Cloudflare, Turnstile, Astro, wrangler, R2, D1, Resend, Stripe, web3forms, siteverify, Pages Functions`
**anywhere outside that allowlist**. Now count the neutral files A itself plans that must contain those
tokens:

| A's neutral file | Contains a blocklisted token because A requires it to |
|---|---|
| `knowledge/form-anti-abuse.md` (Phase 2 §2) | *"Turnstile siteverify endpoint + params (row 93), 5-minute single-use token … Free-plan limits (row 95)"* + the named Turnstile WCAG conflict (row 96) |
| `best-practices/a-turnstile-token-is-not-verified-until-siteverify-returns.md` (Phase 4 #2) | two blocklisted tokens **in the filename** |
| `hooks/flag-form-antipatterns.sh` (Phase 5) | detection: *"a Turnstile/CAPTCHA widget with no server-side verify"* |
| `scenarios/2026-08-17-the-widget-rendered-and-nothing-was-verified.md` (Phase 4) | rows 93–94 = Turnstile |

Phase 2's acceptance list then asserts **both** *"Gate 218 → PASS (no vendor token leaked into neutral
knowledge)"* **and** *"Turnstile-conflict probe: `grep -rn "WCAG 2.2 AA…" knowledge/form-anti-abuse.md`
returns only lines inside the conflict paragraph"* — i.e. it asserts Turnstile is absent from and present
in the same neutral file. Phase 10 test 8 (`plan-A.md:559`) greps
`plugins/forms-engineering/ | grep -i turnstile` **expecting hits in the neutral tree**. Gate 218 cannot
pass as specified. Per A's own Phase 1 rationale ("a boundary added after the content is a boundary that
gets negotiated down"), the outcome is a blocklist quietly shortened to whatever the content already says
— a gate that asserts nothing.

**B has the same content problem with no gate at all.** B ships
`best-practices/turnstile-siteverify-is-not-optional.md` as neutral content (`plan-B.md:247`) while
placing only the RavenPower facts in the substrate skill. gap-delta correctly notes B has no separation
mechanism; it does not notice that B's neutral layer is *already* Cloudflare-bound.

**Where the framing came from.** `scope.md:30-35` defines the split as **domain-neutral vs
RavenPower-substrate**. It never says where a fact that is **vendor-specific but not RavenPower-specific**
belongs — and Turnstile, the single most-cited external vendor in the claims set (rows 93–96), is exactly
that. Both panels resolved the ambiguity the same way (put it in neutral) and then both claimed the layers
were separable. **Correlated, and traceable to a gap in the framing.**

---

### CE-7 — Both plans enforce the novel-synthesis honesty constraint with a **string grep**, which is the recorded "source-scan gates match PROSE" defect. A's grep additionally does not match A's own mandated sentence

**What both plans assume.** That a grep makes the honesty label load-bearing. A (`plan-A.md:628-629`):
*"A release gate … that greps for the label … The label is then **load-bearing, not decorative**."*
B: `check-novel-synthesis-marker.py`, file-level.

**Why a grep is not enforcement.** This repo has recorded the failure twice — *"source-scan gates match
PROSE"* and *"a grep is satisfied by the thing being **described**"* (19 of 25 tracker verifies did not
measure their own title). The property being asserted is *"this content does not read as received
practice."* The property being measured is *"a sentence is present in the file."* A file can carry the
sentence in its header and then, three sections later, state the SPC-on-form-telemetry method in the
declarative voice of established craft — and pass. **Both gates are satisfiable while the content is
dishonest.** B is the more honest of the two: B **names this blind spot explicitly**
(`plan-B.md:641-644`, *"file-level co-occurrence, not paragraph-level — a second unlabelled synthesis
claim later in an already-marked file evades it"*) and writes the limitation into the shipped file's own
header. A claims the opposite ("load-bearing, not decorative") and names no blind spot.

**A's grep is additionally broken, on its own text.** A mandates a **verbatim** sentence
(`plan-A.md:623-627`): *"Applying SPC to form telemetry is **our synthesis, not established practice**. We
found **no published work joining** web-form telemetry to SPC/DMAIC…"*. A's release gate
(`plan-A.md:561-564`) is `grep -rniL "novel synthesis\|not aware of prior published work"` over the three
surfaces, expecting empty. **Neither alternative appears in the mandated sentence.** Either the gate fails
against a correctly-labelled tree, or it passes because the phrase "novel synthesis" happens to appear in
a **heading** — in which case the gate certifies a heading while the mandated sentence could be absent
entirely. The gate's match target and the artifact it is supposed to protect are disjoint strings.

*(Related, same section: Phase 10 test 8's first bullet,
`grep -rn "WCAG 2.2 AA\|WCAG 2.2 AAA" plugins/forms-engineering/ | grep -i turnstile`, requires the WCAG
string and "Turnstile" on the **same physical line**. In wrapped markdown prose they will usually be on
different lines, so the probe returns empty and reads as a pass while asserting nothing.)*

---

### Where I looked for a correlated error and found none

Stated plainly, because a manufactured finding is worse than none:

- **The STANDALONE-vs-EXTEND fork itself.** I attacked it hardest, as instructed. A's structural argument
  survives my own probes: F1 does not fire (web-design's two unread agents carry bullet-level forms
  content, not discipline (c)); F2 does not fire (`check-marketplace-claims.py:163-165`); the zero-agent
  precedents are real (`report-regeneration`, `team-portfolio`). Disciplines (a) and (d) are genuinely
  unowned — `grep -rli "honeypot" plugins/` → **0**, `grep -rli "form abandonment" plugins/` → **0**, and
  no platform-evaluation skill exists. The **budget** argument for standalone is broken (CE-4) and the
  **agent-count** ruling was made against the wrong clause (CE-3), but the *placement* ruling is not
  something I can falsify. I do not oppose it.
- **The `process-improvement` findings.** Rows 39 and 40 are true by my own probes:
  `grep -c "lss_calc" scripts/audit-gates.sh` → **0**; `plugins/process-improvement/hooks/flag-process-improvement-antipatterns.sh`
  exists but is absent from Gate 30's roster (14 hook paths enumerated at `audit-gates.sh:3575-3683`,
  none from `process-improvement`); `ls plugins/process-improvement/best-practices/ | grep -v README | wc -l`
  → **21** against a README header reading *"17 rules"* (`best-practices/README.md:9`) and **21** index
  rows. Both plans read this correctly. No correlated error here.

---

## §2 — PREMISE ATTACK

### 2.1 The two deliverables do not belong in one change. Pairing them creates the only coupling that exists, and it is purely negative.

`scope.md:11` asserts *"Two deliverables in one marketplace change."* Both plans, independently, then
say the two tracks share **nothing but a hazard**:

- A: *"Phase 8 can otherwise start immediately after Phase 0 — it shares no content with the new plugin
  and **its only coupling is the shared gate file**"* (`plan-A.md:609-611`).
- B: *"**Phase 8 … has zero dependency on the forms track** — different plugin directory, no shared files.
  It is listed last only for narrative order"* (`plan-B.md:122-126`).

And then both name the pairing's cost. A: *"⛔ The serialization constraint that overrides the parallelism
… Land `audit-gates.sh` edits one at a time … a red gate masks every later gate in the same CI step"*
(`plan-A.md:603-607`). B: *"Phase 6 and Phase 8a both add gates to the same file; **this is a real
merge-conflict risk to name explicitly**, not a hypothetical one"* (`plan-B.md:539-543`).

So: zero shared content, zero shared dependency, and one shared 7,480-line file whose concurrent editing
both panels flag as the run's top mechanical hazard. The pairing is an artifact of how the request was
phrased, not a design. Nothing in `AGENTS.md` requires it — version bumps, CHANGELOGs, and the
count/regen discipline are all **per plugin**, and PR conventions are per plugin. **The
`process-improvement` harden is 5 bounded findings, all already proven, touching ~5 files; it should be
its own change and it should land first.** Splitting removes CE-5's serialization problem entirely,
de-risks the shared gate file by landing one small well-understood edit before a large one, and lets the
forms plugin's fork ruling be reconsidered (§2.2/§2.3) without holding a completed audit hostage.

### 2.2 "Forms coverage is unowned" is the framing's second defect, and it is overstated in a directional way

`scope.md:13` says the marketplace *"currently has no owner"* for the four disciplines. Measured:

| Discipline | Actual ownership found |
|---|---|
| (a) forms-as-process | **Genuinely unowned.** Adjacent: `ecommerce-dtc` owns checkout/cart abandonment (`best-practices/checkout-friction-is-a-separate-problem-from-product-page-friction.md`, `knowledge/ecommerce-kpi-glossary.md`) — named by neither plan. |
| (b) UX + a11y | **Owned, distributed:** 2 best-practice files (145 lines), `conversion-design` §3/§7, `accessibility-review` passes 2/4, `ux-designer` bullets, **two** decision trees (row 19). The real delta is the five WCAG 2.2 additions — B identifies this precisely (`plan-B.md:19`); A folds it into a larger bank. |
| (c) engineering | **Partly owned in the constitution** — `ravenclaude-core/rules/security.md` §"Untrusted input" + lines 43–45 (uploads, filenames, path traversal) and `plugins/ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md` (Turnstile). See CE-1. Genuinely thin: honeypots (0 hits), webhook idempotency in a *form* context. |
| (d) platform selection | **Genuinely unowned.** |

The framing's word "unowned" pointed both panels at *"build a home for four disciplines"* rather than
*"two are unowned, one has a constitution-level owner, one has a distributed owner."* Both plans then
sized a **7-skill / 11-rule / 4-knowledge / 4-template / 4-scenario** (A) or **6-skill** (B) bank. A
narrower reading — (a) + (d) owned outright, (b) as a WCAG-2.2 delta appended to the existing owner,
(c) as pointers into `ravenclaude-core/rules/security.md` — is a materially smaller change that neither
panel costed, because the framing did not present it. I name this as a scoping consequence, not a
counter-proposal.

### 2.3 `scope.md`'s "OUT of scope" line is load-bearing, ambiguous, and the two panels read it opposite ways — the framing should have resolved this, not the panels

`scope.md:39-41` lists `web-design` et al. as out of scope: *"their existing form-adjacent content is a
routing seam **to be named**, not content to be moved or duplicated."* A reads this as permitting
≤3-line inline pointers and builds Phase 9 on it; B reads it as a hard zero-edit boundary and accepts a
rot pattern rather than cross it (`plan-B.md:224-226`: *"`git diff --name-only | grep -c '^plugins/web-design/'`
must be 0"*). `gap-delta.md` correctly calls this the sharpest disagreement — but frames it as a panel
disagreement. **It is a framing defect.** The sentence is the *only* thing determining whether the
shared zero-agent ruling is reachable-but-scope-questionable or scope-safe-but-rotting, and it was left
for the panels to interpret. That is an owner ruling, not a panel ruling. CE-2 raises its price: A's
reading now also means editing a file an unmerged branch is rewriting.

### 2.4 Ruling 3 (A) designs a gate to avoid a one-line edit the house rules explicitly sanction

A's Ruling 3 rejects a `substrate/` directory because it *"would force a `.repo-layout.json` edit — the
one thing row 20/21 says we can avoid."* Confirmed there is no `plugins/*/substrate/**` glob
(`python3 -c "…allowed_globs…"` — the plugin globs are `agents|skills|hooks|knowledge|best-practices|scenarios|commands|templates|scripts|bin|docs|portable|copilot|codex|monitors|rules` + specific files).
But `AGENTS.md` § "Adding a new plugin" step 5 says plainly: *"Add any new top-level dirs to
`.repo-layout.json` `allowed_globs`"*, and § "Layout-allow-list discipline" documents the procedure. A
treated a **sanctioned, documented, one-line JSON edit** as a cost to design around, and bought instead a
token-blocklist gate that (CE-6) contradicts A's own content plan. The premise that the manifest edit is
expensive is not supported by the repo's own instructions.

---

## §3 — RISK MATRIX

Probability × impact, ranked. "Trigger" = the observable event that tells you the risk has fired.

| # | Risk | P | Impact | Trigger — what you would see |
|---|---|---|---|---|
| R1 | **Duplicated content vs `ravenclaude-core`** (CE-1): upload rules and Turnstile facts shipped as new into a domain plugin, diverging from `rules/security.md` and a `refresh_when`-maintained concept doc. | **High** (both plans schedule it; no probe in either would catch it) | **High** — breaks single-source-of-truth in the constitution; a future Cloudflare change updates one copy | The new tree contains "magic bytes"/"server-generated filename"/"siteverify" and `grep -rn` shows the same rule in `ravenclaude-core/rules/security.md` |
| R2 | **Collision with `fix/conversion-design-field-folklore`** (CE-2): A's Phase 9 edits a section an unmerged branch rewrote; B duplicates its counter-evidence. | **High** (certain if A's Phase 9 runs as written) | **Med-High** — merge conflict on the highest-blast-radius phase; risk of reverting a correct fix | `git log --oneline origin/main..fix/conversion-design-field-folklore` non-empty at build time, or a conflict in `conversion-design/SKILL.md` §3 |
| R3 | **Gate 195 goes red** (CE-5) on a mis-registered new gate, masking every later gate in the same CI step. | **Med-High** (A's file list omits the dispatcher arm; B omits registration entirely) | **High** — CI red on shared infrastructure; masking hides unrelated failures | `bash scripts/audit-gates.sh --check <new N>` → *"gate '<N>' is not registered for per-gate runs"*, or Gate 195's parity assertion fails |
| R4 | **Gate 218 negotiated down to nothing** (CE-6): the blocklist is trimmed to fit content that already violates it. | **High** if A is chosen (the violation is designed in, in 4+ files) | **Med** — a gate that certifies a boundary it no longer enforces; false assurance of "separable" | The Gate 218 token list shrinks during build, or the allowlist grows past 2 files |
| R5 | **The honesty label passes while the content reads as received practice** (CE-7). | **Med** (grep-shaped enforcement in both) | **High** — this is the reputational claim; a false "we labelled it" is worse than no label | A second SPC×form-telemetry paragraph exists in a file whose header carries the marker, and the gate is green |
| R6 | **The plugin rots** (CE-3 / B's own §5.1): zero agents, no inbound `works_with`, discoverable only by typing `/`. | **Med-High** under B; **Med** under A (depends on Phase 9, which R2 endangers) | **Med** — the whole deliverable is unreachable in practice | Six months on: `grep -rn "forms-engineering" plugins/ --include=*.md` outside the plugin itself returns ~0 |
| R7 | **Content bank oversized for the actual gap** (§2.2): (b) and (c) largely re-authored rather than delta'd. | **Med** | **Med** — maintenance liability + duplication surface | The new best-practices index and `web-design`'s / `ravenclaude-core/rules/`'s content state the same rule in different words |
| R8 | **Two-track merge conflict on `audit-gates.sh`** (§2.1) — both plans name it. | **Med** (mitigated by A's explicit serialization; B leaves 8a/6 concurrent) | **Med** | Conflict markers in `scripts/audit-gates.sh`, or a `Supported:` string missing a number that a case arm has |
| R9 | **B's PI acceptance test measures nothing** (verified): `wc -l …/best-practices/*.md \| tail -1` prints total **lines**, not files. Ran it: `1399 total`. It can never print "20 files". | **High** if B's 8b runs as written | **Low-Med** — the count fix ships unverified; this is the exact class the run exists to catch | The acceptance step reports a number in the thousands and is waved through |
| R10 | **Substrate facts rot** (B's own finding): the dead R2 bucket / unverified Resend domain are live, changeable state. B mitigates with re-verification commands; **A ships them as static `src/…:line` assertions**. | **Med** | **Med** | RavenPower-Website binds `UPLOADS`, and the shipped knowledge file still says it is inert |
| R11 | **Row 61 (Resend) is `[unverified — carried from memory, not re-probed]`** and ships as substrate fact under both plans. | **Low-Med** | **Low** — both plans mark it | The marker is dropped during authoring |

---

## §4 — PER-GATE VERDICT

Every new gate either plan proposes. Criteria: (i) would it pass while asserting nothing? (ii) is it
invoked by a workflow? (iii) does it have a proven must-fail half?

**Shared context for (ii):** B's check is correct and worth keeping — `scripts/audit-gates.sh` is invoked
by `.github/workflows/validate-marketplace.yml` with **no `paths:` filter**, so any gate genuinely
registered inside it *is* CI-wired. Re-verified: `validate-marketplace.yml:4` — *"NO `paths:` filter on pull_request — deliberate, and load-bearing twice over"*; the suite runs at `:374`. The "39 of 49 gates invoked by no workflow" population is not the
risk here; **mis-registration inside the suite** is (CE-5).

| Gate | Plan | Teeth? | Why |
|---|---|---|---|
| **218** — substrate token separation (`check-forms-substrate-separation.py`) | A | **NO, as specified** | Its blocklist (`Turnstile`, `Cloudflare`, `siteverify`, …) is violated by ≥4 files A's own Phases 2/4/5 require (CE-6), including a best-practice **filename**. It cannot pass without the blocklist being trimmed — and a blocklist trimmed to fit the content asserts nothing. The *must-fail fixture is well designed* (a neutral file containing `Turnstile`), and the **separability acceptance test** (delete the 2 files → full suite still green) is genuinely falsifiable and the best single idea in either plan. **Verdict: the mechanism has teeth; the token list as drafted is unshippable.** |
| **219** — `form_metrics.py` against a fixture CSV | A | **YES** | Hand-computed expected values, per-assertion, **plus a named negative control** (malformed CSV / completions > starts → non-zero exit). Round-trip test into `lss_calc.py imr` proves the seam executes rather than asserting it. This is the strongest gate design in either plan. Caveat: registration per CE-5. |
| **220** — `lss_calc.py` four modes | A | **YES** | Asserts specific values row 38 hand-checked (`sigma --dpmo 3.4` → `6.00`; `66807` → `3.00`; `308537` → `2.00`), has a negative control (`--usl 5 --lsl 10` → **exit 2**), and A specifies the must-fail proof ("a deliberately-wrong expected value makes it RED"). Closes a real hole: `grep -c "lss_calc" scripts/audit-gates.sh` → **0**. |
| **Gate 30 addition** — PI hook fire/silent pair | A (H1) & B (8a) | **YES — A's is stronger** | Both add the pair. **A alone specifies the mutation proof**: *"then **mutate the hook** to always-silent and confirm Gate 30 goes RED. A fixture pair that cannot fail is decoration."* B reuses the audit's existing fixtures (good — proven shape) and re-runs the hook under `env -i` first (good — guards against drift between audit and build), but never proves the pair can fail. **Take A's mutation step and B's pre-check.** |
| **`check-novel-synthesis-marker.py`** | B | **PARTIAL — honest** | File-level co-occurrence of an SPC term and a form-analytics term without a nearby marker. It *will* catch a wholly unlabelled new file. It will **not** catch a second unlabelled claim inside an already-marked file — **B says so, in the plan and in the shipped file's header.** A gate with a documented blind spot that runs on every future PR beats a one-shot release grep. Keep it; do not oversell it. |
| **`check-turnstile-wcag-conflict-labelled.py`** | B | **WEAK** | Same grep shape, and it depends on a specific "exact qualified phrasing" being reproduced verbatim. Its failure mode is a false green on a paraphrase. It also becomes partly moot given CE-1: `ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md` is the file that should carry the Turnstile conformance caveat, and it is **outside** the gate's scope as scoped to the new plugin. |
| **`check-no-vendor-pricing.py`** | B | **YES — best-designed gate in either plan** | Three fixtures: must-fail (`"Vendor X costs $29/month"`), must-pass (a decision-axis sentence), **and a third negative-instruction fixture** ("do not state a specific price such as an example figure") that must NOT trip. That third fixture is the reflexive-quoting trap `check-description-count-literals.py`'s own docstring documents; B anticipated it unprompted. Only caveat: `\$` in prose (a shell snippet, a `$PATH`, a variable) will false-positive — scope it to prose lines. |
| **A's Phase-10 "honesty greps" (tests 8a/8b)** | A | **NO** | Not gates. They run once, at release, and protect only the PR that introduces them — the exact defect A itself cites as the reason Gate 220 must exist (*"row 39's finding is that `lss_calc.py` shipped correct-but-ungated; the fix is to never do that again"*). A does not apply its own standard to its own honesty checks. Additionally **8b's match strings do not appear in A's own mandated sentence**, and **8a requires two strings on the same physical line** (CE-7). Both would report green while measuring nothing. **B's equivalents are permanent CI gates; on this specific point B is right and A is wrong.** |
| **A's "reachability probe" (Phase 9)** | A | **YES** | For each of the 6 skills, at least one edited agent file names it, verified by *resolving* `skills/<name>/SKILL.md` from each referrer — not by eyeballing. This is the correct shape and it is the only mechanism in either plan that tests R6. |
| **A's Phase-3 "`## Not this skill`" resolver loop** | A | **YES** | `test -e` each named routing target. **It must be extended:** B's Phase-3 routing table names `turnstile-spin`, which claims-row 15 itself records lives at `~/.claude/skills/turnstile-spin`, **outside `plugins/`** — confirmed: `ls -d plugins/*/skills/turnstile-spin` → *no matches*. A `test -e` loop scoped to `plugins/` catches this; B's own acceptance test (`ls plugins/api-engineering/…`) would too, and would show that **one routing target in B's table cannot be `ls`'d and is unavailable to every consumer who is not this owner.** |

---

## §5 — WHAT BOTH PLANS GOT RIGHT

Safe to keep. This is not padding — several of these are better than the repo's own average.

1. **The `process-improvement` findings are real and correctly bounded.** I re-verified all three
   substantive ones independently (zero `lss_calc` coverage; hook absent from Gate 30; 21 files vs a
   "17 rules" header vs 21 index rows). Both plans **refuse to manufacture work** — A: *"Do not manufacture
   work — rows 35, 36, 37, 38, 42, 43, 47 all measured healthy"*; B: *"bounded to exactly the 5 findings
   the audit already proved, nothing more."* That is the correct posture and both held it.
2. **Both plans front-load falsification.** A names F1/F2/F3 and makes F1 a hard Phase-0 gate; B names
   three conditions that would flip its ruling, including the sharp one (*"if >80% of shipped content is a
   thin pointer, it should have been a skill in `web-design`"*). Both are genuinely falsifiable rulings,
   which is rarer than it should be.
3. **A's Phase 0 is excellent and should survive whatever else changes.** A green baseline recorded
   *before* any diff (so a pre-existing red gate is not misattributed), a **layout positive control** that
   requires the deny to be observed and not just the allow, and a recorded tool-availability check so
   "gate skipped" is distinguishable from "gate passed". This is the discipline that would have caught
   CE-1 had it been applied to the claims table's own greps.
4. **A's mutation test for the Gate 30 pair** (*"mutate the hook to always-silent and confirm Gate 30 goes
   RED — a fixture pair that cannot fail is decoration"*) and **A's separability acceptance test**
   (delete the substrate files, run the full suite) are both real must-fail halves.
5. **B's third fixture on the pricing gate** — the negative-instruction case — is the single most
   sophisticated gate-design move in either document, and it was volunteered, not prompted.
6. **B's anti-rot design for the substrate layer**: ship a **re-verification command** instead of a static
   assertion, and require the grep to be *inside* an actual `[[r2_buckets]]` block rather than a nearby
   comment. That directly reuses this repo's own recorded comment-vs-binding trap. A has no equivalent and
   should adopt it.
7. **B's insistence that new gates be permanent CI gates rather than release greps**, and B's honest
   naming of its own gates' blind spots. Where the two plans disagree on this, B is right.
8. **Both correctly refuse `## Decision Tree:` headings**, no vendor pricing, no `RavenPower-Website`
   edits, no domain expansion of `process-improvement`, no re-implementation of SPC math, and both route
   the binding security verdict to `ravenclaude-core/security-reviewer` per the house rule. All correct.
9. **A's serialization constraint on `audit-gates.sh`** (land 218 → 219 → 30 → 220 one at a time, full
   suite between) is the correct mitigation for the masking defect, and B lacks it. If the two tracks stay
   in one change (§2.1 argues they should not), A's ordering is the one to use.
10. **B's confirmation that `validate-marketplace.yml` invokes `audit-gates.sh` with no `paths:` filter**
    is a cheap, correct, repeatable check that keeps new gates out of the unrun population.

---

## §6 — What I could not check

Named so the tiebreak does not over-trust this brief.

- **External claim rows (74–105)** — WCAG criterion numbers, GOV.UK's stated rationale, Baymard, the
  ventureharbour case, Turnstile's plan limits — I did **not** re-verify against sources. I verified only
  that the marketplace's own copy of the field-count evidence now exists and is cited (CE-2).
- **Row 101's negative finding** (no literature joining form telemetry to SPC/DMAIC) — I ran no searches.
  Both plans correctly treat it as bounded-by-method.
- **`claims-ravenpower.md` rows 48–73** — not re-probed against `RavenPower-Website`; B's own rot analysis
  is the right treatment for them.
- **Whether the owner intends `scope.md:39-41` as a hard zero-edit boundary** (§2.3). That is a preference
  call, and it is the one question in this run that a critic cannot settle.

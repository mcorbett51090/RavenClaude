# G6 — SYNTHESIS · the authoritative plan

**Run:** `forms-process-expertise` · **Date:** 2026-08-17 · **Gate:** G6
**Supersedes:** `plan-A.md`, `plan-B.md`. Where either disagrees with this file, this file wins.
**Inputs merged:** `scope.md`, `claims-table.md`, `claims-{repo,process-improvement,ravenpower,external}.md`,
`settlements.md`, `plan-A.md`, `plan-B.md`, `gap-delta.md`, `critic-brief.md`, `tiebreaks.md`.

This plan **encodes settled decisions**. It does not re-litigate them. Section 10 records every
tiebreak verdict with its rationale so a future PR cannot "fix" a ruling by reasoning that was
already rejected.

---

## 0. What this plan covers — and what was removed from it

### 0.1 THE SPLIT (owner-approved)

`scope.md` scoped **two** deliverables. Only one remains here.

The **`process-improvement` gold-standard harden was split out, built, and shipped separately** on
branch `fix/process-improvement-harden` (PR #960, `815 pass / 0 fail / 1 skipped`). Verified this
session against the branch:

| Audit finding | Shipped by PR #960 |
|---|---|
| Row 40 — hook absent from Gate 30's roster | `assert_hook_fires` + `assert_hook_silent` for `flag-process-improvement-antipatterns.sh` |
| Row 39 — `lss_calc.py` zero gate coverage | **Gate 218** (`scripts/check-lss-calc.py`, with `--self-test` and `--must-fail`) |
| Row 44 — no A2/D3/D4 constants | `knowledge/six-sigma-statistics-and-spc.md` +49 lines |
| Rows 45/46 — duplicate rule, "17 rules" header vs 21 files | merge + delete + README index corrected |
| Row 23 item 6 — version | `plugin.json` **0.3.0** and its `marketplace.json` mirror, CHANGELOG entry |

**Every `process-improvement` build phase is therefore DELETED from this plan.** Plan A's Phase 8
(H1–H5) and Plan B's Phases 8a/8b do not appear below. What survives is only the **seam**: the
forms↔SPC join, which consumes `process-improvement/scripts/lss_calc.py` and never modifies it.

Two consequences carried forward, not silently dropped:

- **Gate 218 is TAKEN.** New gates in this plan start at **219**. (Measured: `origin/main` ceiling is
  Gate 217; `fix/process-improvement-harden` adds 218. `Supported:` string is at
  `scripts/audit-gates.sh:1149` post-harden, dispatcher case arm at `:522`.)
- **Risk R9 from the critic brief is void.** It was `plan-B.md` Phase 8b's
  `wc -l …/best-practices/*.md | tail -1` acceptance test, which prints total *lines*, never a file
  count. That phase no longer exists. Recorded so it is not reintroduced by copy-paste.

### 0.2 SCOPE AMENDMENT — `web-design` edits are authorized

`scope.md:39-41` lists `web-design` et al. as "explicitly OUT of scope … a routing seam **to be
named**, not content to be moved or duplicated." The two panels read that sentence in opposite
directions (`gap-delta.md` §1 calls it the sharpest disagreement; `critic-brief.md` §2.3 correctly
re-classes it as a *framing defect*, not a panel disagreement).

**The owner has separately authorized editing `web-design`.** That sentence is therefore **amended**:
adding an inline reciprocal prior to another plugin's agent file is permitted. It stays bounded —
see Ruling R5 and Phase P8. Nothing is moved; nothing is duplicated; no other plugin's frontmatter is
touched.

### 0.3 SCOPE IS NARROWER THAN EITHER PANEL DRAFTED

Verified by probe (`settlements.md` Claim 31, re-confirmed by `critic-brief.md` §0 and `tiebreaks.md`):

| Already owned — the plugin MUST NOT re-teach it | Owner (path:line) |
|---|---|
| Client-side form implementation: native form patterns, `<label>`+`<input>` association, `required`/`pattern`/custom validation **strategy**, "placeholder is not a label" | `plugins/web-design/agents/frontend-implementer.md:32,41,48,60` |
| Form a11y: labels, instructions, `aria-describedby` error association, required indication, validation timing | `plugins/web-design/agents/accessibility-auditor.md:48` |
| Field-count → completion evidence; mid-form abandonment as a **conversion** diagnostic | `plugins/web-design/knowledge/gold-standard-website-references-2026.md:75`; `web-design-decision-trees.md:240,261` |

And `plugins/web-design/agents/accessibility-auditor.md:92` **routes auth / login / CAPTCHA / PII
security OUT to `ravenclaude-core/security-reviewer` by rule, zero-exception.** That routing rule is
*why* a standalone forms plugin survives at all — and **the plugin must preserve it, not absorb it.**
Every security verdict in this plugin routes to `ravenclaude-core/security-reviewer`.

### 0.4 ⛔ CE-1 — CITE AND EXTEND THE CONSTITUTION; NEVER RESTATE IT

This is the highest-value correction in the entire run and it is an **acceptance test**, not a note.

Two "unowned topic" findings that both plans built content on are **FALSE**. `claims-table.md` rows
14 and 16 each recorded a grep whose pattern was a **single literal containing a slash**
(`"captcha/turnstile"`, `"file upload/file-upload"`), so neither probe ever tested its topic. Positive
controls: `captcha` → 18 files, `turnstile` → 6, `file[ -]upload` → 23.

| Topic | Already owned, substantively | Content |
|---|---|---|
| Upload hardening | `plugins/ravenclaude-core/rules/security.md:43-45` | untrusted filenames → generate your own; path traversal → resolve-then-assert; **validate type by content (magic bytes), not extension**; cap size at the boundary |
| Turnstile | `plugins/ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md:10,20-21,51,53,73` | 300-second token lifetime, single-use replay rule, server-side `siteverify` at submit, hostname-covers-subdomains, Access-vs-Turnstile-vs-WAF boundary — **dated, sourced, with a `refresh_when:` clause** |

**Binding rule:** the forms plugin **CITES AND EXTENDS** these. It never restates them. A restatement
is the rubric drift `ravenclaude-core/CLAUDE.md:20` forbids, and the `refresh_when:` clause means a
copy silently rots the moment Cloudflare moves.

⛔ **G6-REPAIR (H4c) — AMENDED. The previous sentence here read: *"Enforced mechanically by Gate 219
sub-check B (§5.1) with a must-fail fixture, not by author discipline."* That was FALSE and is
withdrawn.** Measured: sub-checks B and C are literal-string matches, and a paragraph restating
`security.md:43-45` exactly in meaning — *"read the leading bytes of the upload itself … store it under
an identifier you generated, never under the name the browser sent"* — contains **none** of the six
literals and passes all of A, B and C green. Every must-fail fixture originally specified for 219 was a
**verbatim** copy, so the must-fail half proved only that the literal string trips it.

**What is actually true, stated at the strength the evidence supports:**

- **Gate 219 sub-check D** (§5.1, added by this repair) is a **positive** requirement — any forms file
  that discusses uploads or Turnstile must carry ≥1 **resolving** link into `plugins/ravenclaude-core/`.
  A paraphrase **cannot** evade it by word choice, and this was measured: the paraphrase above is
  **VIOLATION** under D while passing B and C. **D is the mechanical half that works.**
- **Sub-checks B and C raise the floor** against the *verbatim* copy-paste, which is the common case.
  They do **not** certify that no restatement exists. That limitation is written into
  `check-forms-substrate-separation.py`'s own header, and a **paraphrase fixture is committed** so the
  boundary stays visible in the test suite.
- **A human read at authoring time is REQUIRED and is a named step in two phases** — P2 (pre-build,
  already present) and **P4** (added here, because P4's seven rule files are where a paraphrase is most
  likely). Neither is optional; a gate that fires late costs a rewrite, and this one does not fire at all
  on the case it most needs to catch.

**Deleted from the build as a direct consequence:**

- `best-practices/a-content-type-allow-list-is-not-a-file-type-check.md` (Plan A, Phase 4 rule 7) —
  a restatement of `security.md:45`. **Not built.**
- `best-practices/a-turnstile-token-is-not-verified-until-siteverify-returns.md` (Plan A rule 2) and
  `best-practices/turnstile-siteverify-is-not-optional.md` (Plan B, Phase 3) — a second, unlinked copy
  of `cloudflare-who-gets-in.md:51,53`. **Not built.**
- Plan A's `knowledge/form-anti-abuse.md` Turnstile block (siteverify endpoint/params, 5-minute
  single-use, free-plan limits — rows 93/94/95) — **replaced by a citation.**
- Plan B's **Alternative 3** was rejected *solely* because "file-upload has no existing routing
  target (row 16)." The routing target exists. That rejection is void; Alternative 3 is re-scored in
  §9 and is **partially adopted** — file-upload is a routing target, not owned content.

**Still genuinely unowned** (these zeros were real, positive control `abandonment` → 23 files):
`honeypot` → **0 files**, `form abandonment` → **0 files**, multi-step-form-as-a-named-pattern
(2 incidental hits, neither owning), form-platform selection, and forms-as-instrumented-process.

---

## 1. Binding rulings

### R1 — STANDALONE plugin `plugins/forms-engineering/`

Not an extension of `web-design`. Both panels converged; the critic attacked the placement ruling
hardest and could not falsify it (`critic-brief.md` §1 "Where I looked for a correlated error and
found none"). Both of Plan A's own falsifiers were discharged mechanically:

- **F1** — does `web-design` already own discipline (c)? **No.** `frontend-implementer.md:48` and
  `accessibility-auditor.md:48` are single bullets; neither carries bot defense, uploads, webhook
  idempotency, or PII.
- **F2** — does `check-marketplace-claims.py` require a non-empty `agents/`? **No.**
  `scripts/check-marketplace-claims.py:163-165` — `agents = plugin_dir / "agents"; if not agents.is_dir(): return 0`.
  Live precedent: `plugins/report-regeneration/` and `plugins/team-portfolio/` are registered,
  gate-passing, and have **no `agents/` directory**.

`.repo-layout.json` needs **no edit** — settled by a bidirectional probe against the real hook
(`settlements.md` Claim 21): `plugins/forms-engineering/{skills,README.md,.claude-plugin}` → rc **0**;
negative controls `plugins/forms-engineering/substrate/…` and `some-random-toplevel-dir/…` → rc **2**.
That deny is also what makes Ruling R3 a measurement rather than an inference.

### R2 — ZERO AGENTS, on corrected reasoning ⛔

**The verdict is `zero-agents`. The panels' number survives; their reasoning does not.** Both applied
`plugins/ravenclaude-core/CLAUDE.md:11` (the indistinguishable-output test), which is scoped to
*plugin-specific architects and reviewers*. The clause that actually governs a new generalist plugin
is the **carve-out** at `:22`/`:24`. **Encode both the ruling and the corrected rationale — the wrong
rationale is precisely what would let a future PR "fix" this by citing the carve-out.**

Applying the carve-out (`tiebreaks.md`), the split is **NOT clean**, for three independent reasons:

1. **The depth is INVERTED relative to both admitted precedents.** In `project-management` and
   `memory-engineering`, core held the *thin hygiene half* and the plugin held a larger, categorically
   different specialist body (PMBOK/PMP; the memory-paradigm literature). Forms inverts it: the
   hygiene half is the **deeper, dated, sourced, `refresh_when:`-triggered body**
   (`ravenclaude-core/rules/security.md:43-45`, `cloudflare-who-gets-in.md:51,53`,
   `frontend-implementer.md:41,48,60`, `accessibility-auditor.md:48`,
   `gold-standard-website-references-2026.md:75` with its 41,000-checkout benchmark), and the residue
   left for the plugin is **thinner than the half it would extend**. The carve-out's own qualifier —
   *"a genuine specialist body the core generalist doesn't carry"* — is not satisfied.
2. **The one candidate agent is a narrower slice of an existing agent's body.** A
   `form-intake-architect` would sit beside `process-improvement/agents/process-analyst.md` (which
   already owns SIPOC, current-state mapping, and *"plan data collection for a baseline"*) with a
   narrower mandate on the same rubric — textbook **dispatch ambiguity + rubric drift**
   (`CLAUDE.md:20`), which the carve-out *relaxes the presumption against but does not abolish*.
3. **The genuinely-unowned half is a security-review lane, which even an admitted carve-out refused to
   fork.** `CLAUDE.md:24`: *"Memory security does not fork a reviewer"* — ASI06 shipped as
   `memory-engineering/skills/memory-poisoning-review/SKILL.md` invoked by core `security-reviewer`.
   Sibling precedent: `plugins/web-commerce/agents/commerce-webhook-security-reviewer.md` still routes
   its binding verdict to `ravenclaude-core/security-reviewer`.

**Net: forms is a SEAM between three existing owners** (`web-design` for construction/a11y/conversion
evidence, `process-improvement` for the process reasoning, `ravenclaude-core` for the trust boundary
and upload/Turnstile hygiene). **A seam ships as skills with reciprocal priors.**

What would reopen this (do not act without one of these): a named citable specialist body for
forms-as-process, probed by drafting the (a) skill, handing it to `process-analyst`, and diffing
against a dedicated agent's output; **or** a measured post-ship rot signal one release out (see R6 in
§8) — at which point exactly **one** first-contact agent is the correct remedy.

### R3 — The neutral/substrate boundary is a GATE, not a folder

`plugins/forms-engineering/substrate/**` is **denied** by `enforce-layout.sh` today (rc=2, measured).
So the split is file-level and mechanically checked:

- **SUBSTRATE layer** = exactly two allowlisted files: `knowledge/ravenpower-form-substrate.md` and
  `skills/wire-form-substrate/SKILL.md`.
- **NEUTRAL layer** = everything else.
- **Gate 219** enforces it — see §5.1 for the corrected design, which resolves CE-6.
- **"Separable" is falsifiable and run, not asserted:** delete the two allowlisted files → the full
  suite still passes.

### R4 — Discipline (b) ships as a five-criterion DELTA, not a skill

`web-design` owns form UX and form a11y deeply (§0.3). The only genuinely absent content is the
**five criteria new in WCAG 2.2 that land on forms**: 3.3.7 Redundant Entry (A), 3.3.8 Accessible
Authentication Minimum (AA) / 3.3.9 (AAA), 3.2.6 Consistent Help (A), 2.5.8 Target Size Minimum (AA,
24×24 CSS px), 2.4.11 Focus Not Obscured Minimum (AA) — rows 79–83. Plus the 4.1.1-Parsing-was-removed
correction (row 74).

**Ruling: this ships as ONE best-practice file in `forms-engineering`**, written explicitly as a
delta — it states only the five new criteria and **links** to `web-design`'s existing files for
everything pre-2.2. **No `form-ux-and-conversion` skill is built** (Plan B Phase 2) and **no
`accessible-form-patterns` / `form-ux-and-completion` skills are built** (Plan A Phase 3). This is the
single largest reduction against both panels and it is what §0.3 requires.

Alternative considered and recorded in §9 (A4): append the five criteria to `web-design`'s own
best-practices tree. Rejected as the primary route because the owner's authorization covers reciprocal
*priors*, not authoring new content inside another plugin's bank; the delta file plus a prior from
`accessibility-auditor` achieves the same reachability at a smaller blast radius.

### R5 — Reciprocal priors: minimal, declared, bounded

A's **direction** is adopted (reciprocal priors are necessary for a zero-agent plugin to be reachable
— R2 is only paid for by P8). B's **caution** is adopted (minimal, declared edits). Bounded to
**five files, one inline prior each, ≤3 lines, body prose only, frontmatter untouched**. Enumerated in
P8. This is materially smaller than A's nine-file Phase 9.

### R6 — Skill count is the budget lever, not agent count ⛔

"Zero agents ⇒ zero cost" is **false**. Measured this session:

| Surface | Always-on frontmatter (`name`+`description`) |
|---|---|
| `process-improvement` — 6 skills | **1,601 bytes** |
| `memory-engineering` — 6 skills | 1,552 bytes |
| `memory-engineering` — 3 agents | **937 bytes** |
| `web-design` — 7 agents | 1,890 bytes |

A skill's frontmatter is **preloaded for every skill every session**
(`docs/research/2026-06-24-claude-subreddit-scan/README.md:56`), and the `/plugin` Discover tab prices
install as *"tokens added to every turn"*, enumerating commands/agents/skills/hooks together
(`docs/research/2026-06-21-…/README.md:53`). Zero agents ⇒ **zero *budget*** (the ~15K figure names
agent descriptions specifically) — and the skills are where this plugin's real recurring cost lives.

**Also delete A's "enable-cost inverts" argument** (`plan-A.md:34-38`): it compares standalone's
*marginal* cost against `web-design`'s *total*. The EXTEND option adds skills, not agents, so its
marginal agent cost is also zero. The two options are **tied** on that axis, not inverted. R1 stands
on the structural argument alone.

**Budget this plan is sized against: 4 skills + 1 command ≈ 1,050–1,250 bytes always-on
(~260–310 tokens).** Each skill is justified in §3.2. That is ~35% below Plan A's 7 skills and ~33%
below Plan B's 6.

---

## 2. Dependency DAG

B's shape wins: genuinely parallel tracks with a **named merge step**, not A's self-contradicting
serialize. (A's DAG claimed Phase 8 "can start immediately after Phase 0" and then imposed a total
order over `audit-gates.sh` that blocked it — `gap-delta.md` §7. That contradiction is resolved by
splitting *content parallelism* from the *gate-file baton*.)

### 2.1 External dependencies — the rebase order

```
  PR #960  fix/process-improvement-harden  ──┐  (adds Gate 218; makes 219 the free number)
                                             ├──> merge to main ──> P0 rebases onto main
  PR #959  fix/conversion-design-field-folklore ─┘  (deletes the unsourced field-count table)
```

**Both must land before P0 completes.** Verified this session:

- The table row `^| 1 (email only) |` is still on `origin/main` (count **1**); PR #959 is **not merged**.
- `origin/main` gate ceiling → **217**; the harden branch adds **218**. PR #960 is **not merged**.

#### ⛔ G6-REPAIR (H1) — the old `grep -c "35–50%"` sentinel was UNSATISFIABLE. Do not restore it.

The original probe was `grep -c "35–50%"` → **0**. It can never return 0, because **#959's own
retraction paragraph quotes the figure it removed** (deliberate provenance: *"…carried a
completion-by-field-count benchmark table (1 field → 35–50%, 7+ → <10%) … They were removed rather than
re-cited"*). A grep written to detect the **claim** is satisfied by the **retraction** — this repo's
recorded *"a grep is satisfied by the thing being described"* defect, inverted.

Measured this session across both refs — **the old sentinel does not distinguish the two states; the
replacement pair does, in both directions**:

| ref | `grep -c "35–50%"` (OLD — useless) | `grep -c '^\| 1 (email only) \|'` (structure) | `grep -c 'removed rather than re-cited'` (control) |
|---|---|---|---|
| `origin/main` (pre-merge) | **1** | **1** | **0** |
| `origin/fix/conversion-design-field-folklore` | **1** ← identical | **0** | **1** |

**THE BINDING SENTINEL PAIR (used verbatim at P0 acc.2 and at P8's pre-build gate):**

```sh
F=plugins/web-design/skills/conversion-design/SKILL.md
git show origin/main:$F | grep -c '^| 1 (email only) |'          # MUST be 0  (the table row is gone)
git show origin/main:$F | grep -c 'removed rather than re-cited' # MUST be >=1 (positive control)
```

The second half is **not optional**. An absence-only probe also returns 0 on an empty read, a renamed
file, or a bad ref — the positive control is what proves the file being measured is the post-#959 one.
⛔ **zsh trap (§7): `git show "$B:file"` returns the COMMIT, not the file.** Use a literal ref or SHA.

**Why #959 blocks, explicitly:** Plan A's Phase 9 would edit `conversion-design` §3 to annotate the
field-count table as *"a prior, not a law"* — **preserving a table the sibling branch DELETED as
unsourced** (`158e5c80`, 2026-08-17: *"They were removed rather than re-cited"*, with the 14%-drop /
19.21%-relabel / 53%-at-30+-questions counter-evidence and a retrieved-2026-08-17 citation). Landing
second and resolving the conflict by re-adding the table would re-litigate a decision already made
correctly. **P8 must therefore rebase onto post-#959 `main` and then assert the table is absent
before writing anything into that file.** Plan B's Phase 2, which would duplicate the same
counter-evidence and citation into a second plugin, is likewise **not built** — the counter-evidence
now lives in `web-design`; the forms plugin **links** to it.

**Why #960 blocks:** if the forms track lands first, its gates take 218/219/220 and the harden's
Gate 218 collides on number *and* on the `Supported:` string. Gate 195 (`check-gate-registration.py`)
enforces number-uniqueness and would go red — masking every later gate in the same CI step.

#### ⛔ G6-REPAIR (H1, missing branch) — what to do if PR #959 is **CLOSED** rather than merged

The plan previously handled only *merged* / *not-yet-merged*. A closed-without-merge #959 left the STOP
with **no exit**. Ruled here:

> **If `gh pr view 959 --json state` returns `CLOSED` and `mergedAt` is null**, the sentinel pair above
> is **void** — do not run it, do not STOP. P8's five reciprocal priors go into `ux-designer.md`,
> `accessibility-auditor.md`, `frontend-implementer.md`, `security-reviewer.md` and
> `process-analyst.md`; **none of them touches `conversion-design/SKILL.md` at all.** The only real
> requirement is that P4's scenario `2026-08-17-we-removed-fields-and-conversion-fell.md` and the
> `best-practices/README.md` inherited-rules table **link to a section that exists**. On the closed
> branch: link to `conversion-design/SKILL.md` **§3 as it stands** and **drop the "post-#959" qualifier**
> everywhere it appears in this plan (§3.2, §3.4, P3's routing table, §9 A5).
> ⛔ What does **not** change: the plan still never re-cites `ventureharbour.com` and never restates the
> field-count numbers. Row 90 still ships as *"the claim 'fewer fields always converts better' is not
> supported"* — a negation of an absolute. #959 closing would mean the table survives on `main`; it
> would **not** mean the table became sourced.

#### ⛔ G6-REPAIR — two measured corrections to this section's premises

1. **PRs #959 and #960 do NOT conflict. Merge order is immaterial.** Measured this session: both report
   `mergeable: MERGEABLE` and `mergeStateStatus: CLEAN` **simultaneously**, and their
   `.claude-plugin/marketplace.json` hunks are **140 lines apart** (#959 at line 364, `web-design`
   `0.16.1 → 0.16.2`; #960 at line 504, `process-improvement` `0.2.2 → 0.3.0`) — far outside 3-line diff
   context. The diagram above shows *both are prerequisites of P0*, **not** an ordering between them.
   Neither PR needs a rebase against the other.
2. **There is no gate-number race.** `gh pr list --state open` returns exactly **two** PRs (959, 960).
   `origin/main`'s ceiling is **217** and its `Supported:` string ends `…216, 217.`; #960 takes **218**.
   Nothing else claims a number. **New gates start at 219** and that is not contingent on timing.

### 2.2 Internal DAG

```
P0  rebase onto post-#959/#960 main + green baseline        [BLOCKS EVERYTHING]
 │
P1  skeleton + registration + Gate 219 + Gate 221           [boundary gates ship BEFORE content]
 │
 ├── TRACK K (content, the long pole) ──────────────────────────────┐
 │     P2 knowledge ×3  ──>  P3 skills ×3  ──>  P4 rules/templates/scenarios
 │                                    │
 │                                    └──>  P7 substrate layer (2 files)
 │
 ├── TRACK M (capability)   P5  form_metrics.py + Gate 220          │  parallel with K
 │
 └── TRACK H (enforcement)  P6  hook + Gate 30 fire/silent pair     │  parallel with K
                                                                    │
                       ┌────────────────────────────────────────────┘
                       ▼
                     P8  reciprocal priors  (needs every skill to EXIST and be named)
                       │
                     P9  release
```

**Critical path:** `P0 → P1 → P2 → P3 → P4 → P7 → P8 → P9`. Content is the long pole: knowledge gates
the skills (skills cite, never restate), skills gate the rules, the substrate layer needs something to
be separable *from*, and P8 cannot name a skill that does not exist.

**Genuinely parallel:** TRACK M (P5) and TRACK H (P6) share no file with TRACK K. Dispatch them
concurrently with P2/P3.

### 2.3 The gate-file baton — the ONE named merge step

`scripts/audit-gates.sh` is 7,480 lines and shared by every plugin's CI. Four separate edits land in
it. They are **not** serialized as whole phases (that was A's error); only the **file edit itself** is
serialized, by a baton:

```
baton order:  P1 (219 + 221)  →  P5 (220)  →  P6 (Gate 30 pair)
```

Rules for the baton:
1. A track may do **all** of its content/script work in parallel. It may **not** append to
   `audit-gates.sh` until it holds the baton.
2. After each baton hand-off, run the **full suite** (`bash scripts/audit-gates.sh`), not `--check N`.
   A red gate hides every later gate in the same CI step — this repo's recorded masking defect.
3. Each append is one gate block + one dispatcher case arm + one `Supported:` token. Nothing else.

**Also a real collision inside TRACK K:** P2/P3/P4 all touch `plugins/forms-engineering/CLAUDE.md` and
`README.md`. P1 pre-creates delimited stub sections (`<!-- STUB: telemetry -->`, `<!-- STUB: harden -->`,
`<!-- STUB: platform -->`, `<!-- STUB: substrate -->`) so each later phase edits only its own stub;
P9 does the single consolidating edit that removes the markers. If these phases are dispatched as
literally concurrent subagents without the stub discipline they will race on two files. "Parallel" is
not free.

---

## 3. What gets built

### 3.1 Tree

```
plugins/forms-engineering/                      (new — 182nd marketplace entry; 181 today)
├── .claude-plugin/plugin.json                  v0.1.0, requires ravenclaude-core@>=0.7.0,
│                                               description with ZERO count literals (Gate 206)
├── README.md · CLAUDE.md · CHANGELOG.md        (the 3 gate-required files + house convention)
├── knowledge/     3 neutral + 1 substrate
├── skills/        3 neutral + 1 substrate
├── best-practices/ 7 new rules + README with an INHERITED-RULES table
├── templates/     3
├── scenarios/     3
├── commands/      1  (design-form-intake.md)
├── hooks/         flag-form-antipatterns.sh + hooks.json
└── scripts/       form_metrics.py
                                                 agents/ DOES NOT EXIST (R2)
```

Shape check against the two most recent deliberately-authored plugins (row 29): `memory-engineering`
3/6/9/5 and `accessibility-engineering` 4/5/9/4. At 0 agents / 4 skills / 7 rules / 4 knowledge this
sits at or below both.

### 3.2 The four skills, each justified against R6

| Skill | Discipline | Why it earns ~260 bytes of every session |
|---|---|---|
| `form-intake-and-triage-design` | (a) process | Genuinely unowned. Intake taxonomy that makes triage deterministic, request typing, routing rules, field-level SLA clocks, self-serve-vs-escalate bright lines, abandonment **as a process defect stream** (distinct from `web-design`'s abandonment-as-conversion-diagnostic, which it links to). |
| `form-telemetry-and-control` | (a) measurement | Genuinely unowned, and the run's novel-synthesis surface. The measurement contract: which events, **which denominator**, per-field drop-off and its proxy weakness, what "defect" means for a form, and the hand-off of an individuals series to `process-improvement`. Carries `form_metrics.py`. |
| `harden-a-form-submission` | (c) server half | The half `web-design` routes OUT by rule. Validation parity, honeypot with its AT/autofill exemption, time-trap (marked unverified), form-submission idempotency / double-submit, webhook verification, PII minimisation. **Cites** `ravenclaude-core/rules/security.md` and `cloudflare-who-gets-in.md`; **routes the binding verdict** to `ravenclaude-core/security-reviewer`. |
| `wire-form-substrate` | substrate | The RavenPower layer. Allowlisted; deletable without breaking a gate. |

**Discipline (d) is NOT a skill.** Platform selection ships as `knowledge/form-platform-evaluation.md`
(the seven axes) + `templates/form-platform-evaluation-matrix.md`, referenced from
`form-intake-and-triage-design`. A decision-axis checklist is the canonical
`data-platform/skills/stack-selection` shape, but at 7 axes it does not need its own always-on
frontmatter. This is a deliberate application of R6. **Trigger to revisit:** if the axes grow past a
single knowledge section or acquire a scoring procedure with branch logic, promote to a skill.

### 3.3 The three knowledge files

1. `knowledge/form-telemetry-and-spc.md` — metric definitions with the **denominator named** (GA4
   `form_start` = first *interaction*, not view; `form_submit`; `form_id`/`form_name`/
   `form_destination` need custom dimensions — row 100); completion/abandonment as exact complements;
   time-to-complete as disambiguator; per-field drop-off's proxy weakness stated inline (last field
   touched ≠ offending field). **Carries the novel-synthesis label** (§6.1) and the low-volume
   autocorrelation hazard (row 102).
2. `knowledge/form-anti-abuse.md` — honeypot and its AT/autofill false-positive failure mode (row
   103); time-trap `[unverified]` (row 104); the bot-defense **ladder** (what to reach for in what
   order, and when a challenge is the wrong tool); form-submission idempotency vs CSRF. **Turnstile
   and upload hardening appear here ONLY as citations** to `ravenclaude-core` (§0.4), plus the one
   thing core does not carry: the **named WCAG conflict** (§6.2).
3. `knowledge/form-platform-evaluation.md` — the seven durable axes: webhook/server-side egress with a
   verifiable signature; data residency; DPA/BAA on the plan actually bought; submission + upload +
   retention limits; export and form-definition lock-in; a11y of the vendor's own rendered markup;
   whether you keep your own anti-abuse layer. **No pricing, no feature matrix** (row 105).

### 3.4 The seven best-practice rules (trimmed from A's eleven)

| # | Rule file | Row | Why it is not a duplicate |
|---|---|---|---|
| 1 | `wcag-2-2-added-five-criteria-that-land-on-forms.md` | 74, 79–83 | R4 delta. The five are absent from `web-design`'s files, which cite only 1.3.1/2.4.6. |
| 2 | `a-honeypot-must-be-invisible-to-assistive-tech-and-to-autofill.md` | 103, 13 | `honeypot` → 0 files repo-wide (control: `abandonment` → 23). |
| 3 | `every-public-form-post-needs-a-double-submit-guard.md` | 55 | CSRF is anti-forgery, **not** anti-duplicate. `form.*idempotenc` → 7 hits, all data-pipeline idempotency — different concept, same word. |
| 4 | `name-the-denominator-before-you-quote-a-completion-rate.md` | 100 | Unowned. |
| 5 | `do-not-put-three-sigma-limits-on-a-low-volume-form-series.md` | 102 | The hazard that must ship *before* the method. |
| 6 | `degraded-bot-defense-must-be-loud.md` | 49, 52 | Generalized from a real observation: fail-open on an unset secret is defensible; a **silent** fail-open is not. Not in core. |
| 7 | `clear-the-error-the-moment-it-is-fixed.md` | 92 | The one thing `web-design`'s validate-on-blur rule (row 2) lacks. Links to it rather than restating it. |

**Deliberately NOT written** (already owned — the `best-practices/README.md` opens with an
**inherited-rules table** that links each): placeholder-as-label (row 1), validate-on-blur (row 2),
field-count evidence (row 3 → now `web-design`'s corrected §3 after #959), controlled-inputs/shared-Zod
(row 6), **upload content-type/magic-byte/filename rules** (`security.md:43-45` — §0.4), **Turnstile
siteverify/lifetime/replay** (`cloudflare-who-gets-in.md:51,53` — §0.4),
`never-mark-mandatory-fields-with-an-asterisk` (row 87 — `ux-designer.md:74` already flags unmarked
required/optional fields as an anti-pattern; a second home is drift),
`validate-on-the-server-and-encode-on-output` (row 98 — the sharper OWASP distinction belongs in the
`harden-a-form-submission` skill body as a cited line, not as a rule file competing with
`ravenclaude-core/rules/security.md` §Untrusted input).

**Templates (3):** `form-spec.md` (one form's fields, validation parity, abuse posture, telemetry
events, retention), `form-telemetry-plan.md`, `form-platform-evaluation-matrix.md`.

**Scenarios (3, dated):** `2026-08-17-the-honeypot-flagged-real-customers.md` (row 103),
`2026-08-17-we-removed-fields-and-conversion-fell.md` (row 90 — the 14%-drop / 19.21%-relabel case,
**linking** to `web-design`'s post-#959 §3, not restating its citation),
`2026-08-17-the-upload-endpoint-stored-nothing.md` (row 58 — fully coded, fully gated, fully inert).

---

## 4. Phased build

Every phase carries `depends_on_claims` citing `claims-table.md` rows 1..105, with `[]` written
explicitly where a phase rests on no claim row. **As it happens no phase in this plan is `[]`** —
every one cites at least one row, which is a deliberate check against the load-bearing-inference blind
spot the G3b premise gate exists to catch. If a future edit adds a phase that genuinely rests on
nothing, it must carry `depends_on_claims: []` rather than omit the field. Pre-build gates are
conditions that must hold **before** work starts. Acceptance tests are mechanical.

---

### P0 — Rebase, premise settlement, green baseline · BLOCKS EVERYTHING

`depends_on_claims: [20, 21, 33, 34]`

**Goal.** Start from a tree where the two blocking PRs have landed and where every later "gates pass"
claim is attributable to *our* diff.

**Files touched.** None (read-only + one throwaway probe file, deleted).

**PRE-BUILD GATES**
- `git branch --show-current` prints a non-empty name (a blank answer is a detached HEAD, not a pass).
- `git checkout -B forge/forms-process-expertise origin/main` **immediately after worktree init**, and
  print the behind-count as proof. `forge-worktree.sh` branches from the primary checkout's HEAD, not
  `origin/main` — measured 105 commits behind, twice, and it fails silently.

**ACCEPTANCE TESTS**
1. **PR #960 merged:** `git show origin/main:scripts/audit-gates.sh | grep -c "Gate 218"` → ≥1, and its
   title is the `lss_calc.py` gate. If 0, **STOP** — Gate 218 is not yet taken and this plan's gate
   numbering is wrong.
2. **PR #959 merged — the bidirectional sentinel pair (§2.1, G6-REPAIR H1).** ⛔ The old single probe
   `grep -c "35–50%"` → 0 is **DELETED as unsatisfiable**; #959's retraction quotes the figure it
   removed, so it reads **1 on both refs** and cannot distinguish them. Run **both** halves:

   ```sh
   F=plugins/web-design/skills/conversion-design/SKILL.md
   git show origin/main:$F | grep -c '^| 1 (email only) |'          # MUST be 0
   git show origin/main:$F | grep -c 'removed rather than re-cited' # MUST be >=1
   ```

   If the first is ≥1 **or** the second is 0, **STOP** — P8 would collide with an in-flight branch and
   could re-add a table deliberately deleted as unsourced (first half), or you are measuring the wrong
   file/ref entirely (second half). If #959 is **CLOSED not merged**, this test is **void** — take the
   closed-branch ruling in §2.1 instead of stopping.
3. `git rev-list --count HEAD..origin/main` → **0**.
4. **Green baseline recorded:** `bash scripts/audit-gates.sh` run end-to-end on the clean tree; exit
   code and the full failing-gate list written to `.ravenclaude/runs/forge/forms-process-expertise/baseline-gates.txt`.
   Row 34: no gate had ever been executed this run. Without this, a pre-existing red gate gets
   misattributed to our diff.
   ⛔ **G6-REPAIR (M1) — a SKIP IS NOT A PASS, and the suite's exit code does not carry it.** Measured:
   `815 pass, 0 fail, 1 skipped` → **SUITE EXIT=0**. Also record, in `baseline-gates.txt`:
   `grep -c 'SKIPPED' <suite output>` → must be **0**. Measured bidirectionally this session:
   **2** with `ruff` absent, **0** with `ruff` on PATH (and the suite went `815 pass/1 skipped` →
   `817 pass/0 skipped`). Do **not** let DoD #10's attribution rule (*"a failure present in the baseline
   is not ours"*) launder a recorded skip into a licence to ship — a skipped gate was never run against
   anything, ours included. The three new Python files this plan ships would be **entirely unlinted**
   locally while the suite printed `0 fail` and exited 0.
5. **Layout positive control (rows 20/21):** write `plugins/forms-engineering/README.md` (must be
   **ALLOWED**, rc 0) *and* attempt `plugins/forms-engineering/substrate/x.md` (must be **DENIED**,
   rc 2) through `plugins/ravenclaude-core/hooks/enforce-layout.sh`. A probe that only shows the allow
   proves nothing. Delete both afterwards.
6. **Tooling availability — a HARD STOP, not a recording** (G6-REPAIR, M1). Record
   `python3 --version` (expect 3.9.6), `python3 -m pip --version` (**bare `pip` is absent on stock
   macOS**), `npx --yes prettier@3.9.4 --version`. Then, for ruff, **STOP until this exits 0**:

   ```sh
   python3 -m pip install --quiet --user ruff
   PATH="$(python3 -c "import sysconfig;print(sysconfig.get_path('scripts',scheme='osx_framework_user'))"):$PATH"
   ruff --version && python3 -m ruff check .
   ```

   ⛔ Measured this session: `which ruff` → **not found (rc 1)** while `python3 -m ruff --version` →
   **ruff 0.15.8**. It is installed, just not on PATH — `--user` lands it in
   `~/Library/Python/3.9/bin`, which stock macOS does not export. `scripts/audit-gates.sh:1610` gates
   Gate 9b on `command -v ruff`, so the bare-`ruff` form yields **exit 127** and a *skipped* gate, not a
   failing one. Both forms are proven here: `ruff check .` → **rc 127**; `python3 -m ruff check .` →
   **rc 0**. Recording the skip instead of stopping is what makes the three new Python files ship
   unlinted under a green suite.
7. `ls plugins/ | grep -c forms-engineering` → **0** (no name collision; measured 0 this session).

**Blast radius:** none.

---

### P1 — Skeleton, registration, and BOTH boundary gates (gates ship FIRST)

`depends_on_claims: [20, 22, 23, 26, 27, 29, 30]`

**Goal.** A registered, gate-passing empty plugin, plus **Gate 219** (substrate/citation separation)
and **Gate 221** (honesty markers) *before any content exists to violate them*. This ordering is
deliberate: a boundary added after the content is a boundary that gets negotiated down to fit what was
already written — which is exactly how A's Gate 218 became unshippable (CE-6).

**Files touched**
- `plugins/forms-engineering/.claude-plugin/plugin.json` — `name`, `version: 0.1.0`, `description`,
  `author.name`, `homepage`, `license`, `keywords`, `requires: {plugins: ["ravenclaude-core@>=0.7.0"]}` (row 30).
- `plugins/forms-engineering/{README.md, CLAUDE.md, CHANGELOG.md}` (row 26 requires the first three;
  CHANGELOG is house convention). CLAUDE.md/README.md carry the delimited stub markers (§2.3).
- `.claude-plugin/marketplace.json` — append `{name, source, description, version, author:{name}, keywords}` (row 22).
- `scripts/check-forms-substrate-separation.py` (new) + `tests/fixtures/` for it.
- `scripts/check-forms-honesty-markers.py` (new) + its fixtures.
- `scripts/audit-gates.sh` — **Gate 219** and **Gate 221** (§5). **Holds the gate-file baton.**

**PRE-BUILD GATES**
- P0 acceptance 4 recorded a green (or known-red-and-attributed) baseline.
- **Gate 206:** the `description` in **both** `plugin.json` and its `marketplace.json` mirror contains
  **no artifact-count literal** ("4 skills", "a 3-file knowledge bank"). Row 27 — this caused a 3-PR
  hotfix chain. Write the description with zero numerals about our own contents, and verify by running
  `python3 scripts/check-description-count-literals.py` **against the draft before committing**.
- Portability floor for both new scripts: Python **3.9**, stdlib only, `from __future__ import annotations`
  if any `X | None` appears.
- **Gate 195 registration triple understood** — see §5.4. Each new gate registers in **three** places.

**ACCEPTANCE TESTS**
- `python3 -m json.tool` clean on both manifests; `len(plugins)` increased by exactly **1** (181 → 182).
- `python3 scripts/check-marketplace-claims.py` → PASS on a plugin with **no `agents/` directory**
  (falsifier F2 discharged mechanically, not by precedent alone).
- `bash scripts/audit-gates.sh --check 206` → PASS.
- `bash scripts/audit-gates.sh --check 219` → PASS; **and each of its FOUR sub-check must-fail
  fixtures makes it exit non-zero** (§5.1 — A, B, C **and new sub-check D**). A gate with no proven
  must-fail half asserts nothing. ⛔ **Two extra fixtures are mandatory here** (G6-REPAIR H4/M3):
  (a) the **paraphrase** fixture — committed, run, and expected to pass B/C while failing **D**, which
  is how the documented blind spot stays visible in the suite rather than in a memo; and
  (b) a **`.sh` must-PASS fixture containing `cf-turnstile`**, proving the `**/*.md` scope holds so P6's
  own hook does not trip the gate.
- `bash scripts/audit-gates.sh --check 221` → PASS; **and each of its three sub-check must-fail
  fixtures makes it exit non-zero**, and the **negative-instruction fixture does NOT trip it** (§5.3).
- `python3 scripts/check-gate-registration.py && python3 scripts/check-gate-registration.py --self-test`
  → both exit 0 (Gate 195: reachability, number-uniqueness, dispatcher/`Supported:` parity).
- Full suite run + **baton hand-off**: `bash scripts/audit-gates.sh` end-to-end, diffed against the P0
  baseline.

**Blast radius:** `scripts/audit-gates.sh` is shared by every plugin's CI. Keep the diff to two
appended gate blocks, two dispatcher case arms, and two `Supported:` tokens.

---

### P2 — Knowledge bank (3 neutral files) · TRACK K

`depends_on_claims: [55, 74, 79, 80, 81, 82, 83, 96, 100, 101, 102, 103, 104, 105]`

**Goal.** One durable, cited fact bank per owned discipline. Knowledge files are where citations live;
skills reference them rather than restating facts.

**Files touched.** The three files in §3.3.

**PRE-BUILD GATES**
- ⛔ **The CITE-DON'T-RESTATE read is done first.** Open
  `plugins/ravenclaude-core/rules/security.md` §File handling and
  `plugins/ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md` **in full** before writing a
  line of `form-anti-abuse.md`. Every Turnstile fact and every upload fact in the drafted file must be
  a link, not a sentence. (§0.4; Gate 219 sub-check B enforces it, but a gate that fires late costs a
  rewrite.)
- ⛔ **No `## Decision Tree:` headings.** That literal prefix triggers `scripts/render-trees.py`,
  creating a committed-SVG + manifest-hash CI obligation (`audit-gates.sh:3039-3053`,
  `regenerate-artifacts.yml`), needing mermaid-cli/Chromium locally, with a recorded catastrophic
  failure mode (`audit-gates.sh:6388` — printed "ok" and deleted 800+ SVGs). Use the table form
  sanctioned by `docs/best-practices/decision-trees-in-knowledge-files.md`. Promote later as a
  deliberate, separately budgeted change. *(Plan B was silent on this trap.)*
- Every external fact carries `(url, retrieved 2026-08-17)` inline **or** a persisted
  `[unverified — <reason>]` marker **in the file**. Chat-spoken caveats do not count.

**ACCEPTANCE TESTS**
- `grep -c "2026-08-17" knowledge/*.md` → ≥1 per file.
- Every `[unverified` marker has a reason clause after the em dash: `grep -c "\[unverified —"` equals
  `grep -c "\[unverified"`.
- `python3 scripts/render-trees.py --check` → PASS **unchanged** (proves we created no tree obligation).
- `python3 scripts/check-md-links.py` → exit 0. ⛔ **G6-REPAIR (H2): NOT `--check 29`.** Gate 29 has no
  dispatcher arm and is absent from `Supported:`; `--check 29` exits **1** with *"gate '29' is not
  registered for per-gate runs"* on every tree, clean or broken. Measured. The script is directly
  runnable and its exit code **is** the gate (verified: exit 0 on the current tree).
- `bash scripts/audit-gates.sh --check 219` → PASS; `--check 221` → PASS. *(219/220/221 are ours; we
  register their dispatcher arms in P1/P5 per §5.4, so these three are the `--check` numbers that
  genuinely work.)*
- **Anti-duplication probe (positive-controlled):** for each of the six distinctive phrases owned
  elsewhere — "magic bytes", "server-generated", "path traversal", "siteverify", "single-use",
  "placeholder is not a label" — `grep -rn` the new tree. A hit **outside a markdown link line** is a
  duplication defect. First run the same grep against `plugins/ravenclaude-core/` to prove the probe
  returns non-zero on a tree that *does* contain them.

---

### P3 — Skills (3 neutral) · TRACK K

`depends_on_claims: [1, 2, 4, 5, 6, 7, 8, 9, 10, 17, 18, 19, 42, 88, 89, 90, 91, 92, 97, 98, 100, 101]`

**Goal.** Three skills, one per owned job, each **naming what it does not own and who does** — the
`legal-ops-clm` step-6 handoff pattern (row 8) generalized.

| Skill | Owns | Explicitly routes away |
|---|---|---|
| `form-intake-and-triage-design` | intake taxonomy, request typing, routing rules, field-level SLA, self-serve-vs-escalate bright lines, abandonment-as-defect-stream, the 7 platform axes by reference | legal-specific intake → `legal-ops-clm` (rows 7–8); Dataverse/Power Pages → `power-platform` (row 10); **field-count / conversion evidence → `web-design/skills/conversion-design` §3** (post-#959); surveys → `ux-research` |
| `form-telemetry-and-control` | the measurement contract: which events, which denominator, per-field drop-off + its proxy weakness, what a "defect" is for a form, the individuals-series hand-off | charting + control limits → `process-improvement` (`lean-six-sigma-blackbelt`, `scripts/lss_calc.py`); any inferential test → `applied-statistics` (row 42 confirms both seams live) |
| `harden-a-form-submission` | the trust-boundary walk: client/server validation **parity**, honeypot + its exemption, time-trap `[unverified]`, double-submit/idempotency, webhook signature verification, PII minimisation | **binding security verdict → `ravenclaude-core/security-reviewer`** (zero-exception house rule, mirroring `accessibility-auditor.md:92`); upload hardening → **cite** `ravenclaude-core/rules/security.md:43-45`; Turnstile mechanics → **cite** `cloudflare-who-gets-in.md`; API-layer authz → `api-engineering/api-security-engineer`; idempotency-key design → `api-engineering/skills/idempotency-key-design`; webhook hardening → `web-commerce/skills/webhook-hardening`; legal/DSAR ruling → `data-governance-privacy` + owner |

**PRE-BUILD GATES**
- P2 merged (skills cite knowledge; they must not restate facts).
- **The `frontend-implementer` / `accessibility-auditor` boundary is written into each skill's
  `## Not this skill` section before its body is drafted** (§0.3). A skill that drifts into
  `<label>` association or `aria-describedby` timing is over-scoped.
- ⛔ **`turnstile-spin` MUST NOT appear as a routing target.** Ruled in §11.1 — it lives at
  `~/.claude/skills/turnstile-spin`, outside `plugins/`, and is unavailable to every consumer who is
  not this owner. Verified: `ls -d plugins/*/skills/turnstile-spin` → no matches. *(This voids Plan B's
  Phase 3 routing-table row.)*

**ACCEPTANCE TESTS**
- `python3 scripts/check-frontmatter.py` → exit 0: every `SKILL.md` strict-YAML-parses with a non-empty
  `description` (row 25). ⛔ **G6-REPAIR (H2): NOT `--check 18`** — Gate 18 has no dispatcher arm and
  `--check 18` exits **1** unconditionally (measured). Run the script; its exit code is the gate
  (verified exit 0 on the current tree).
- **Routing-target resolver loop:** every path named in any `## Not this skill` / routing table is
  resolved by `test -e`, **scoped to `plugins/`** — not eyeballed. Verified live this session:
  `plugins/api-engineering/skills/idempotency-key-design/SKILL.md` ✓,
  `plugins/web-commerce/skills/webhook-hardening/SKILL.md` ✓,
  `plugins/data-platform/skills/stack-selection/SKILL.md` ✓. Any target that fails `test -e` is a
  build blocker, not a warning.
- `python3 scripts/check-md-links.py` → exit 0 (**not** `--check 29`; see P2); `--check 219` and
  `--check 221` → PASS.
- **Glue check (B's own falsifier, operationalized):** measure the ratio of pointer lines to original
  craft lines across the three skills. If **>80% is a thin pointer** back into
  `web-design`/`process-improvement`/`api-engineering`, R1 is wrong and this should have been a single
  skill inside `web-design` — **STOP and escalate**, do not proceed to P4.

---

### P4 — best-practices, templates, scenarios · TRACK K

`depends_on_claims: [1, 2, 3, 6, 9, 13, 49, 52, 55, 58, 74, 79, 80, 81, 82, 83, 90, 92, 100, 102, 103]`

**Goal.** One file = one rule (house convention), and **only rules the marketplace does not already
own**. Contents enumerated in §3.4.

**PRE-BUILD GATES**
- **The inherited-rules table in `best-practices/README.md` is written FIRST**, so an author reaching
  for a rule that is already owned hits the table before writing a duplicate.
- ⛔ **G6-REPAIR (H4c) — NAMED HUMAN PARAPHRASE READ, required here as it already is in P2.** Before any
  rule file is committed, read `plugins/ravenclaude-core/rules/security.md` §File handling and
  `cloudflare-who-gets-in.md` in full, then read each drafted rule file asking **"does this say the same
  thing in different words?"** — not "does it contain a forbidden phrase?". Gate 219 sub-checks B/C are
  literal matches and **cannot** catch a paraphrase (measured; §5.1 H4). Sub-check D catches it only if
  the file *mentions* uploads/Turnstile by name. **P4's seven rule files are where a paraphrase is most
  likely** — rules #2, #3 and #6 all sit adjacent to territory `security.md` and
  `cloudflare-who-gets-in.md` already own. Record in the phase log that the read happened.
- Row 90's counter-evidence is tier **B** (single vendor case study). It ships as *"the claim 'fewer
  fields always converts better' is not supported"* — a **negation of an absolute**, which the evidence
  does support — never as *"more fields convert better,"* which it does not. And it **links** to
  `web-design`'s post-#959 §3 rather than re-citing `ventureharbour.com`; one source, one home.
- Rows 88–89: GOV.UK's own justification for one-thing-per-page is comprehension / mobile / error
  recovery / analytics / branching — **not conversion**, and the page presents **no** quantitative
  conversion evidence. Our structure guidance must not import a framing GOV.UK declines to make.

**ACCEPTANCE TESTS**
- `python3 scripts/check-md-links.py` → exit 0 (**not** `--check 29`; see P2). The inherited-rules table
  carries ~7 cross-plugin relative links — the most likely place this phase breaks CI.
  ⛔ **Note its documented limit** (`scripts/check-md-links.py:19-20`): *"For a target with an anchor
  suffix (`path/to/file.md#section`), only the path part is resolved; **the anchor fragment itself is
  not validated**."* A link to a heading that no longer exists resolves green. See §5.5 (M5).
- `ls best-practices | grep -v README | wc -l` **equals** the README index row count **exactly**, and
  equals any count stated in the README header. *(This is defect row 46, the one just fixed in
  `process-improvement`. Do not ship the bug we fixed.)*
- Every rule file names its source row's citation or an `[unverified — <reason>]` marker.
- `--check 219`, `--check 221` → PASS — **including new sub-check D** (§5.1), the positive link
  requirement: every rule file discussing uploads or Turnstile carries ≥1 resolving link into
  `plugins/ravenclaude-core/`.
- **Rule #5 states the minimum-n figure verbatim: 20 individual observations** (§5.2, G6-REPAIR H3).
  `grep -c '20 individual observations' best-practices/do-not-put-three-sigma-limits-on-a-low-volume-form-series.md`
  → ≥1, and it is the **same** number Gate 220's fixture carries. One number, two surfaces, no drift.

---

### P5 — `form_metrics.py` + Gate 220: the SPC join, made runnable · TRACK M

`depends_on_claims: [38, 39, 100, 101, 102, 105]`

**Goal.** The (a) discipline's join to `process-improvement` becomes an **artifact**, not an assertion.
**A wins on capability** (§10, T2) and this matters *more* precisely because the join has no
literature: a claim with no prior art must be mechanically testable or it is just prose.

`plugins/forms-engineering/scripts/form_metrics.py` reads a submission/event CSV and emits: starts,
submits, completion and abandonment rate **with the denominator printed**, time-to-complete for
completers, per-field error rate, per-field last-touch drop-off **labelled as a proxy in the output
itself**, and an `--emit-imr` mode producing the individuals series that
`plugins/process-improvement/scripts/lss_calc.py imr` consumes. **Two scripts, one seam, no duplicated
statistics** — `lss_calc.py` is verified correct (row 38) and now gated (Gate 218); we feed it, we do
not reimplement it.

**PRE-BUILD GATES**
- **Portability floor** (§7): Python **3.9**, stdlib only (`csv`, `statistics`, `argparse`). If any
  `X | None` annotation is used, `from __future__ import annotations` must be adjacent to line 1 —
  `lss_calc.py` already does exactly this and it is why it runs on stock 3.9.6.
- **The novel-synthesis label is printed by the tool itself**, not only in the docs (§6.1) — **on
  `stderr`, in every mode.** See the stream contract below.
- `python3 -m ruff check .` is a whole-tree reader (Gate 9b) — a violation here blocks unrelated PRs.
  ⛔ Not bare `ruff check .` (rc 127 on this host; P0 acc.6).

#### ⛔ G6-REPAIR (H3) — the round-trip AS WRITTEN DOES NOT EXECUTE. Binding stream contract.

The plan specified `form_metrics.py --emit-imr <fixture.csv> | lss_calc.py imr`. Measured:

```
$ printf '10.1\n10.3\n9.8\n' | python3 plugins/process-improvement/scripts/lss_calc.py imr
usage: lss_calc.py imr [-h] --values VALUES
lss_calc.py imr: error: the following arguments are required: --values     -> exit 2
```

`--values` is `required=True` (`lss_calc.py:372-375`) and **there is no stdin path anywhere in the
module**. The pipe's left side is discarded and the right side exits 2. This is the plan's **only
mechanical proof of its only no-prior-art claim** (T2), so it cannot stay aspirational.

Compounding: `_parse_values` (`lss_calc.py:105-113`) accepts comma **or whitespace** separation, so a
naive `--values "$(…)"` fix works — *unless* §6.1's ~50-word NOVEL SYNTHESIS marker lands on **stdout**,
in which case `_parse_values` raises `all values must be numbers` and it exits 2 again. §6.1 and P5 were
in direct conflict and neither section noticed.

**BINDING CONTRACT — resolves all three at once:**

1. `--emit-imr` writes **only whitespace-separated numbers to stdout**. Nothing else. No header, no
   marker, no units, no blank-line banner.
2. The **verbatim NOVEL SYNTHESIS marker (§6.1) goes to `stderr`, in EVERY mode** — plain runs and
   `--emit-imr` alike. Piping stays clean; the label still reaches a human; a user who redirects stdout
   to a file still sees it. (This also closes M4's library-import path: emit it from the public entry
   function, and state in the module header that a caller who suppresses stderr owns the omission.)
3. **The round-trip becomes command substitution, not a pipe:**

   ```sh
   python3 plugins/process-improvement/scripts/lss_calc.py imr \
     --values "$(python3 plugins/forms-engineering/scripts/form_metrics.py --emit-imr <fixture.csv>)"
   ```

4. **Minimum n is 20 individual observations** — named here, and rule #5
   (`do-not-put-three-sigma-limits-on-a-low-volume-form-series.md`) states the **same** number.
   ⛔ Why this must be named: `cmd_imr` accepts **n ≥ 2** (`lss_calc.py:259-261`), so without a stated
   floor Gate 220 could certify "valid control limits" on a **2-point series** — precisely what this
   plugin's own best-practice rule #5 forbids. The gate would bless what the plugin prohibits. The
   committed fixture CSV therefore carries **≥20 completed-form rows**.

**Proven this session** against a mock honouring the contract (`good`) and one violating it by printing
the marker to stdout (`bad`), plus a 20-point series through the real `lss_calc.py`:

| assertion | good mock | bad mock |
|---|---|---|
| (i) round-trip exit 0 **and** stdout carries `UCL` **and** `LCL` | **PASS** (rc 0) | **FAIL** (rc 2) |
| (ii) every `--emit-imr` stdout line numeric-only | **PASS** (0 bad lines) | **FAIL** (1 bad line) |
| (iii) verbatim marker present in captured **stderr** | **PASS** | **FAIL** |

Real `lss_calc.py imr --values "<20 readings>"` → **exit 0**, `readings (n) : 20`, UCL/CL/LCL printed.

⛔ **Assertion-form trap found while proving (ii), and binding on the gate script.** Write the
numeric-only check as a **count**, never as `grep -q -v`:

```sh
bad=$(printf '%s\n' "$out" | grep -c -v -E '^[0-9eE+.,[:space:]-]*$'); [ "$bad" -eq 0 ]   # CORRECT
printf '%s\n' "$out" | grep -qvE '^[0-9eE+.,[:space:]-]*$'                                # ⛔ WRONG
```

Measured on this host (`ugrep 7.5.0` shimming `grep`): on input `abc\n123\n`, `grep -v '^[0-9]*$'`
prints `abc` and returns **rc 0**, while `grep -qv '^[0-9]*$'` returns **rc 1**. Adding `-q` inverts the
answer *toward clean*. A first draft of assertion (ii) used `-q -v` and **passed the bad mock** — a
false green caught only by running it. Also note `grep -q` succeeds if **any** line matches, so an
anchored per-line rule must be expressed as "count of violating lines is 0", not "some line conforms".

**ACCEPTANCE TESTS**
- **Gate 220** (§5.2) runs `form_metrics.py` against a committed fixture CSV (**≥20 rows**) with
  **hand-computed** expected values, asserts each, and includes a **negative control**: a malformed CSV
  and a CSV where completions > starts must each exit non-zero.
- **Round-trip, executed** in the command-substitution form above → exit 0 and `UCL`/`LCL` present.
  This proves the seam **executes** rather than asserting it exists.
- **Stream contract asserted, both halves:** `--emit-imr` stdout has **0** non-numeric lines; the
  verbatim §6.1 marker appears in captured **stderr** of a plain run **and** of `--emit-imr`.
- **Must-fail proof:** a deliberately wrong expected value in the gate makes Gate 220 RED; and a build
  of `form_metrics.py` that prints the marker to stdout makes assertions (i) and (iii) RED (proven
  above with the `bad` mock).
- Runs under the stock `python3` recorded in P0 (3.9.6).
- **Baton:** append Gate 220 to `audit-gates.sh` only after P1's baton hand-off; full suite after.

**Rests on a verified negative** (rows 101/102): the script is an **original instrument** and its
per-field drop-off column inherits a proxy weakness nobody has validated. It ships labelled. See §12.

---

### P6 — Advisory hook + its Gate 30 fire/silent pair, same change · TRACK H

`depends_on_claims: [13, 24, 37, 40, 41, 49, 55, 100, 102, 103]`

**Goal.** `hooks/flag-form-antipatterns.sh` (PostToolUse, advisory; `FORMS_STRICT=1` → exit 2), plus
its **fire/silent fixture pair registered in Gate 30 in the same change**. Row 40 is exactly the defect
just fixed in `process-improvement`; shipping a hook without its Gate 30 pair reproduces it on day one.

**Detections — scoped strictly to rules THIS plugin owns** (a detection for a rule owned elsewhere
would create a second enforcement home, which is drift):
- a honeypot input without `aria-hidden` / `tabindex="-1"` / `autocomplete="off"` (row 103);
- a CAPTCHA/Turnstile widget introduced with no server-side verification in the same change — the
  message **cites** `cloudflare-who-gets-in.md`, it does not restate the rule (rows 93/94 via §0.4);
- a public form POST handler with no double-submit/idempotency guard (row 55);
- a completion or abandonment rate quoted with no denominator named (row 100);
- 3-sigma control limits applied to a form series with fewer than the stated minimum points (row 102).

*Not detected here* (owned elsewhere — `web-design`): placeholder-as-only-label, `*` on a required
field, `type="text"` on an email/tel field.

**PRE-BUILD GATES**
- **Portability floor:** bash **3.2** only — no `declare -A`, `mapfile`, `${x^^}`, `shopt -s globstar`,
  GNU `timeout`, `grep -P`, `sed -i`. Row 37 is the model protocol: the `process-improvement` hook was
  *proven* clean under `env -i PATH=/usr/bin:/bin bash`, in **both** stdin-JSON and `$1`-arg modes, in
  **both** directions. Reproduce that exact protocol.
- `hooks.json` registered with `${CLAUDE_PLUGIN_ROOT}` paths.
- Executable bit set. Note the host constraint: `chmod +x` is Bash-**denied** on
  `ravenclaude-core/{hooks,scripts}`; **this plugin is not that substrate**, so a plain `chmod +x`
  should pass. If it is denied, the escape is a `!`-prefixed one-liner handed to the user, never a bare
  retry.

**ACCEPTANCE TESTS**
- `bash -n` clean; `test -x` true (row 24, Gates 3/3b/4).
- `env -i PATH=/usr/bin:/bin bash hooks/flag-form-antipatterns.sh <bad-fixture>` → ≥1 finding;
  `<clean-fixture>` → 0 findings, exit 0; `FORMS_STRICT=1` on bad → exit 2.
- Both invocation modes exercised (stdin JSON and `$1`). Gate 128 covers stdin-fallback generically
  (row 41) but **not** the behavioural contract.
#### ⛔ G6-REPAIR (H2, the critical one) — the Gate 30 teeth proof was PASSING VACUOUSLY

The plan previously read: *"`bash scripts/audit-gates.sh --check 30` → PASS"* and *"mutate the hook to
always-silent and confirm Gate 30 goes RED."* **`--check 30` is RED unconditionally** — measured exit
**1** with *"gate '30' is not registered for per-gate runs"*, before the mutation, after the mutation,
and on a tree with no forms hook at all. Gate 30 exists as a full-suite block only
(`scripts/audit-gates.sh:3584`); it has no dispatcher arm and is not in `Supported:`. The operator would
mutate, see non-zero, conclude the fixture pair has teeth, revert, and ship. **The probe and the subject
fail the same way** — the recorded *"my own probes fail silently toward clean"* pattern, reproducing on
day one the exact row-40 defect this phase exists to prevent.

**Re-specified: key on the flipped NAMED ASSERTION LINE in the FULL-SUITE output, never on a per-gate
exit code.** `scripts/audit-gates.sh:1200-1206`'s `gate()` prints `  ✓ <label> …` / `  ✗ <label> …`, and
`assert_hook_fires "<label>"` / `assert_hook_silent "<label>"` render as
`<label> (fires on anti-pattern)` / `<label> (silent on clean)`.

```sh
# 1. clean tree — the fires-half must be present AND passing
bash scripts/audit-gates.sh > /tmp/before.txt 2>&1
grep -c '✓ forms anti-patterns (fires on anti-pattern)' /tmp/before.txt   # MUST be 1
grep -c '✓ forms anti-patterns (silent on clean)'       /tmp/before.txt   # MUST be 1

# 2. mutate hooks/flag-form-antipatterns.sh to always-silent  (printf '#!/usr/bin/env bash\nexit 0\n')
bash scripts/audit-gates.sh > /tmp/after.txt 2>&1
grep -c '✗ forms anti-patterns (fires on anti-pattern)' /tmp/after.txt    # MUST be 1  <- THE TEETH
grep -c '✓ forms anti-patterns (fires on anti-pattern)' /tmp/after.txt    # MUST be 0

# 3. revert, and prove you reverted:  git diff --stat plugins/forms-engineering/hooks/ | wc -l  -> 0
```

⛔ **Executed this session against the existing `process-improvement` hook** (the same
`assert_hook_fires`/`assert_hook_silent` contract) to prove the mechanism distinguishes pass from fail
before it was written here:

| | `✓ … (fires on anti-pattern)` | `✗ … (fires on anti-pattern)` | `✓ … (silent on clean)` | suite exit |
|---|---|---|---|---|
| clean hook | **1** | **0** | 1 | **0** |
| mutated to always-silent | **0** | **1** | 1 | **1** |

Note the `(silent on clean)` half reads `✓` in **both** rows — which is precisely why the suite's
overall exit code is not enough: it says *something* failed, not *which half*. Keying on the named
assertion that flipped is the only form that cannot be satisfied by an unrelated failure elsewhere in a
815-assertion suite. *A fixture pair that cannot fail is decoration; a proof that cannot fail is worse.*

- Gate 30 is **never** invoked as `--check 30` anywhere in this plan. It is a full-suite block; run the
  full suite. (This also satisfies §2.3 baton rule 2, which already required a full run here.)
- **Baton:** the Gate 30 edit lands last in the baton order; full suite after.

---

### P7 — Substrate layer (RavenPower) — exactly two files · TRACK K

`depends_on_claims: [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68]`

**Goal.** Make the neutral guidance executable on the real stack, grounded in what
`RavenPower-Website` **actually does today**, not what a generic forms plugin would assume.

**Files touched (both on the Gate 219 allowlist)**
- `knowledge/ravenpower-form-substrate.md` — the six live form surfaces (row 48); Turnstile wired with
  server-side `siteverify` on every anonymous public-write form **except `/intake`**, which substitutes
  a signed-HMAC link or an authenticated session (rows 49, 50); **fail-open when `TURNSTILE_SECRET` is
  unset** — deliberate, documented, and the reason rule #6 exists (row 49); no third-party form service
  anywhere (row 51); no honeypot, no timing check (row 52); the shared D1 fixed-window `rateLimitAllow`
  with a per-route fail-open/fail-closed choice (row 53); Pages Functions + D1/R2/KV, **no Queues, no
  Durable Objects, no rate-limiting binding** (rows 56, 57); Pages-environment secrets (row 60); the
  CSRF double-submit pattern on authenticated writes and why public forms do not need it (row 66); the
  upload authority chain in order (row 67); upload content-type validation is **allow-list by declared
  header only, no magic-byte sniffing** (row 68) — stated as a **gap against**
  `ravenclaude-core/rules/security.md:45`, which is a citation, not a restatement.
- `skills/wire-form-substrate/SKILL.md` — the ordered recipe (origin → content-length → session → CSRF
  → rate limit → ownership → content-type → size → storage), plus four **honest gap** call-outs: the
  `UPLOADS` R2 bucket is unbound so every valid upload dies at the storage seam (row 58); Resend's
  sender domain is unverified so customer email may not deliver (row 61); no aggregate error summary on
  the 54-question `/intake` (row 64); no scripted focus move to `/call`'s `role="alert"` (row 65).

**⛔ ANTI-ROT DESIGN — B wins here and A has no equivalent.** Every claim describing **current,
changeable state** of `RavenPower-Website` ships as a **re-verification command**, not a static
assertion. A's static `src/…:line` pointers rot silently the moment that repo ships the R2 bucket.
Pattern:

> As of 2026-08-17, `grep -A2 '\[\[r2_buckets\]\]' wrangler.toml` in RavenPower-Website shows only
> `SITES`. Re-run this before relying on the claim — **and require the match to be inside an actual
> `[[r2_buckets]]` block, not a nearby comment**: memory `ravenpower-portal-substrate-traps.md`
> records a case where a grep matched a *comment describing* a binding rather than the binding itself,
> and the tracker flipped an item to DONE with nothing bound.

**PRE-BUILD GATES**
- **Scope wall: this run touches ZERO files in `RavenPower-Website`.** The substrate layer *describes*;
  it does not fix. Rows 58/61/64/65 are documented gaps, not tasks.
  `git diff --name-only` must show no path outside this repo.
- Every claim sourced from `claims-ravenpower.md` carries its row citation **inline in the shipped
  file**, not only in this plan — a reader of the skill must see the evidence trail.
- Row 61 is `[unverified — carried from memory, not re-probed]`; it ships wearing that marker.
  Row 49's fail-open branch is verified **in code**, but whether `TURNSTILE_SECRET` is actually set in
  live production was **never probed** — say so; do not state the live posture.

**ACCEPTANCE TESTS**
- ⛔ **The separability test, RUN FOR REAL:** copy the tree with the two substrate files removed → full
  `bash scripts/audit-gates.sh` → **PASS**. If removing them breaks anything, Ruling R3 has failed and
  the coupling must be found and cut. *(This is the best single idea in either plan; it is what makes
  "separable" falsifiable.)*
- Gate 219 reports exactly **2** allowlisted files and **0** violations elsewhere.
- Every substrate claim carries a `src/…:line` pointer **or** a re-verification command **or** an
  `[unverified — <reason>]` marker.
- **Anti-rot proof:** paste each re-verification command into a shell against a local
  `RavenPower-Website` checkout and confirm it still returns what the file claims. If no checkout is
  available, record that fact in the file — do not silently skip the test.

---

### P8 — Reciprocal routing seams (largest blast radius)

`depends_on_claims: [3, 5, 6, 17, 19, 42, 88, 89, 90]`

**Goal.** R2 (zero agents) is only *paid for* here. A zero-agent plugin with no inbound pointer is a
documented rot pattern in this repo — B named the consequence and accepted it; A's fix was correct in
direction but nine files wide. **R5 rules the middle: five files, one inline prior each, ≤3 lines.**

**Files touched (exhaustive — adding a sixth requires re-opening R5):**
1. `plugins/web-design/agents/ux-designer.md` → `form-intake-and-triage-design`
2. `plugins/web-design/agents/accessibility-auditor.md` → the WCAG-2.2-delta best-practice file
3. `plugins/web-design/agents/frontend-implementer.md` → `harden-a-form-submission` (and a one-line
   restatement of the boundary: it keeps client-side implementation, we take the server half)
4. `plugins/ravenclaude-core/agents/security-reviewer.md` → `harden-a-form-submission` (the compliant
   shape: a skill invoked by core's reviewer, exactly as `memory-poisoning-review` does)
5. `plugins/process-improvement/agents/process-analyst.md` → `form-telemetry-and-control`

**PRE-BUILD GATES**
- **PR #959 is merged and the field-count table is gone** (P0 acceptance 2 re-asserted here, because
  the rebase may be stale by now). ⛔ **G6-REPAIR (H1): use the bidirectional pair, NOT `grep -c "35–50%"`** —
  that probe reads **1 on `origin/main` and 1 on the fix branch** and cannot distinguish them (§2.1):

  ```sh
  F=plugins/web-design/skills/conversion-design/SKILL.md
  grep -c '^| 1 (email only) |' $F            # MUST be 0
  grep -c 'removed rather than re-cited' $F   # MUST be >=1
  ```

  If the first is ≥1, **STOP**. Do not annotate, do not restore, do not "call the table a prior, not a
  law" — that remedy would preserve a table deliberately deleted as unsourced. If the second is 0 you
  are reading a stale or wrong tree — re-fetch before drawing any conclusion. If #959 **closed**, apply
  §2.1's closed-branch ruling; this gate is void, not failed.
- ⛔ **rerere hygiene for this rebase** (L1). `rerere.enabled=true` here with 93 cached resolutions, at
  least one covering `audit-gates.sh` gate blocks and one covering the `marketplace.json` plugin array —
  both files this plan appends to. Do the integration as
  `git -c rerere.enabled=false rebase origin/main`, and afterwards re-assert
  `grep -c "Gate 218" scripts/audit-gates.sh` ≥ 2 (block + arm) and the sentinel pair above. If you
  merge rather than rebase, assert `git log -1 --format='%p' | wc -w` = **2** before pushing.
- **Zero-edit discipline on frontmatter.** Adding body prose is safe; touching `description` risks the
  300-char cap (rows 25, 28) and re-prices the ~15K budget. `git diff` on each edited file must show
  **no line inside the YAML block**.
- No file outside the five is touched. `frontend-engineering/best-practices/forms-are-controlled-and-validated-at-the-edge.md`
  and `accessibility-engineering/CLAUDE.md` (A's Phase 9) are **dropped** — routing already reaches
  them through `web-design`, and each extra file is blast radius bought with no measured return.

**ACCEPTANCE TESTS**
- `python3 scripts/check-frontmatter.py` → exit 0 on **every** edited agent file (frontmatter unchanged
  is the intent; the check proves it). ⛔ **G6-REPAIR (H2): NOT `--check 18`** — unregistered, exits 1
  unconditionally. Same for links: run `python3 scripts/check-md-links.py`, **not `--check 29`**.
- ⛔ **Reachability probe:** for each of the **four** skills, at least one file outside
  `plugins/forms-engineering/` names it — verified by a loop that **resolves**
  `plugins/forms-engineering/skills/<name>/SKILL.md` from each referrer, not by reading prose. A skill
  nothing points at is a skill nothing invokes. *(This is the only mechanism in the plan that tests R6
  in §8.)*
- **Positive control on the probe:** point the resolver at a deliberately misspelled skill name and
  confirm it reports a failure. An all-green resolver that cannot go red is measuring nothing.

#### ⛔ G6-REPAIR (M2) — `test -e` is blind to plugin ENABLEMENT. One of the five priors is inert here.

Measured this session in `~/.claude/settings.json`: **181 plugins, 50 enabled, 131 disabled** — and
`process-improvement@ravenclaude` is **`false`**. Prior #5 (`process-analyst.md` →
`form-telemetry-and-control`) therefore does not load in the owner's own session, and
`form-telemetry-and-control`'s primary routing targets (`lean-six-sigma-blackbelt`, the DMAIC seam,
`lss_calc.py`) sit in that same disabled plugin. **The run's self-declared "novel-synthesis surface"
routes into something not loaded on the machine that ships it.** `test -e` on a path inside a disabled
plugin succeeds; the misspelling positive control proves the resolver goes red on a **typo**, not on a
**dead route**. The probe would report 5/5 green while 1/5 is inert.

**The probe must test reachability, not file existence.** Extend the P8 loop to print, per referrer:

```sh
python3 - <<'PY'
import json, os
cfg = json.load(open(os.path.expanduser('~/.claude/settings.json')))
en  = cfg.get('enabledPlugins', {})
for referrer_plugin in ('web-design','web-design','web-design','ravenclaude-core','process-improvement'):
    key = f'{referrer_plugin}@ravenclaude'
    print(f'{key:40s} enabled={en.get(key)}')
PY
```

**Do NOT fail the build on it** — the owner's config is not the consumer's, and a disabled plugin is a
local setting, not a defect in the shipped tree. **But it must be PRINTED**, so "5 referrers, 4 of them
in plugins enabled on this host" is visible rather than invisible. Silence is the thing to avoid.

**Ruled here** (this is a limitation statement, not a scope change): the plugin's telemetry seam is
**dark whenever `process-improvement` is disabled**, and that is **accepted**. R5's five-file budget is
not re-opened by this repair — a sixth reciprocal prior in an enabled plugin would require re-opening
R5, and this measurement is recorded as the evidence that *would* justify it if R6 fires. It does not
authorize taking it now.

---

### P9 — Consolidation, regen, whole-tree gates, release

`depends_on_claims: [22, 23, 24, 26, 27, 28, 34]`

**Goal.** Land it green, with the count/regen discipline satisfied. Full definition of done in §13.

**Files touched.** `plugins/forms-engineering/{CLAUDE.md, README.md}` (single consolidating edit that
removes the §2.3 stub markers), `CHANGELOG.md`.

**PRE-BUILD GATES**
- Every earlier phase's acceptance tests passed **locally, individually**. ⛔ **The masking defect:** a
  red gate hides every later gate in the same CI step — so after the last fix, run the **whole chain**
  locally, not just the gate that was failing. A fix once revealed a second failure that had been
  hidden across 26 surfaces.
- Both tracks present in the working tree **simultaneously** before the final gate run. A partial run
  reports green while masking the other track's breakage.

**ACCEPTANCE TESTS.** See §13 (Definition of done) — it is the acceptance test list for this phase.

---

## 5. Gate register

**Gate numbers: 219, 220, 221.** 218 is taken by the shipped `process-improvement` harden (§0.1).
Plus two assertions appended to existing **Gate 30**.

### 5.1 Gate 219 — `check-forms-substrate-separation.py` (P1)

**⛔ This is A's Gate 218 with CE-6 fixed.** A's design forbade the tokens `Cloudflare, Turnstile,
Astro, wrangler, R2, D1, Resend, Stripe, web3forms, siteverify, Pages Functions` anywhere outside a
two-file allowlist — while A's own Phases 2/4/5 required four neutral files to contain them, one of
them **in a filename**. A gate that cannot pass gets its blocklist quietly trimmed to fit the content:
a gate that asserts nothing.

**§0.4 dissolves the contradiction.** With CITE-DON'T-RESTATE binding, a vendor token in a neutral file
is legitimate **only as a citation**. So the gate keys on *how* the token appears, not merely whether:

| Sub-check | Rule | Must-fail fixture | Must-pass fixture |
|---|---|---|---|
| **A — allowlist** | A vendor token outside the 2 allowlisted substrate files is a violation **unless** its line satisfies sub-check B | a neutral `SKILL.md` containing a bare sentence `Turnstile tokens are valid for 300 seconds` | the same file with that sentence replaced by a link |
| **B — citation form** | A vendor token in a neutral file must appear on a line that is a markdown link into `plugins/ravenclaude-core/` **or** inside a fenced `## Routes to` block | `- Turnstile: verify server-side` (no link) | `- Turnstile mechanics → [cloudflare-who-gets-in.md](../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md)` |
| **C — no restated constitution** | The six distinctive phrases owned by `ravenclaude-core` ("magic bytes", "server-generated filename", "resolve to absolute", "single-use", "300 second"/"5 minute" token, "siteverify") may not appear in any forms file except on a link line | a rule file restating "validate type by content (magic bytes), not extension" | the inherited-rules table row linking `security.md` |

**Filenames are checked too** — `a-turnstile-token-is-not-verified-until-siteverify-returns.md` would
fail sub-check A on its path alone. That file is not built (§0.4).

#### ⛔ G6-REPAIR (M3) — FILE-TYPE SCOPE, written here BEFORE the script exists

Sub-checks A/B/C/D apply to **`plugins/forms-engineering/**/*.md` ONLY.** `hooks/`, `scripts/` and
`tests/fixtures/` are **out of scope by construction**, and the reason goes in the script header:
*a hook's detection strings are code, not prose, and a shell line can never be a markdown link.*

Why this must be fixed before P1 and not negotiated at P6: P6's `hooks/flag-form-antipatterns.sh`
**cannot detect a Turnstile widget without matching `turnstile`/`cf-turnstile` in its own source.**
Unscoped, Gate 219 goes red the moment P6 lands, and both available remedies — add `hooks/*.sh` to the
allowlist, or drop `Turnstile` from the token list — are *the blocklist being quietly trimmed to fit the
content*, i.e. **CE-6 / R4 recurring in a new place**. Scoping is not a concession; it is the correct
boundary, decided before any content pressures it.

Measured this session on a fixture `.sh` containing `cf-turnstile`: an `*.md`-scoped sweep finds **0**;
an unscoped sweep finds **1**. The scope is what makes the difference, and it is testable.

- **Add a must-PASS fixture:** a `.sh` file containing `cf-turnstile` must **not** trip Gate 219,
  proving the scope holds and did not rot.
- **Sub-check C's bare `"single-use"` is replaced by a CO-OCCURRENCE requirement:** `single-use` **and**
  a Turnstile/challenge-token mention within N lines. Bare `single-use` is generic and best-practice
  rule #3 (`every-public-form-post-needs-a-double-submit-guard.md`) is *about* one-shot submit tokens —
  it will plausibly use those words in a sense with nothing to do with Turnstile replay. A false
  positive on the plugin's own owned content is how a term list gets "trimmed to fit".

#### ⛔ G6-REPAIR (H4) — sub-checks B+C CANNOT FAIL ON A PARAPHRASE. Sub-check D is the half that works.

§0.4 claimed these are *"enforced mechanically … not by author discipline."* **That claim was false**
and is amended in §0.4. Sub-check C is six **literal** phrases, and *every* must-fail fixture the plan
specified was a **verbatim copy** — so the must-fail half proved only that the literal string trips it.

**The measured evasion.** This paragraph restates `security.md:43-45` and
`cloudflare-who-gets-in.md` exactly in meaning, contains **none of the six literals** and no vendor
token, and passes A, B and C green:

> *"Never let the client's declared content type decide what a file is — read the leading bytes of the
> upload itself and match them against your allow-list. Reject the request at the boundary if it exceeds
> your size ceiling, and store it under an identifier you generated, never under the name the browser
> sent. The challenge token stops being accepted after five minutes and may only be redeemed once."*

Executed against three fixtures — verbatim, the paraphrase above, and a correctly-linked file:

| fixture | sub-check C literal hits | **sub-check D** (topic present, ≥1 core link?) |
|---|---|---|
| verbatim restatement | **2** → correctly RED | topic 3 / links 0 → **VIOLATION** |
| **paraphrase** | **0** → ⛔ **passes green** | topic 3 / links 0 → **VIOLATION** ✅ caught |
| linked citation | 0 → correctly green | topic 3 / links 2 → **ok** |

**Four required changes, all of them:**

**(a) A PARAPHRASE must-fail fixture is added to sub-check C** — the paragraph above, verbatim, as a
committed fixture. Run it. **It will not go red on C**, and that is the point: the fixture's job is to
*document the boundary in the test suite itself*, so a future editor cannot mistake C for coverage it
does not have. It is a must-fail fixture for **sub-check D**, where it does go red.

**(b) The limitation is written into `check-forms-substrate-separation.py`'s own header**, exactly as
§5.3 already does for Gate 221 — a named blind spot beats a false claim of coverage:

> *Sub-checks B and C are literal-string matches. A restatement in different words — the actual CE-1
> failure mode — evades them; this was measured, and a paraphrase fixture is committed alongside the
> verbatim ones to keep the boundary visible. Sub-check D (the positive link requirement) is what
> catches a paraphrase. These checks raise the floor; a human read at authoring time is still required.*

**(c) §0.4's "not by author discipline" claim is AMENDED** (see §0.4) — the gate raises the floor and a
human read is required, named as a step in **both** P2 and P4.

**(d) NEW sub-check D — the POSITIVE link requirement. This is the half that actually works.**

| Sub-check | Rule | Must-fail fixture | Must-pass fixture |
|---|---|---|---|
| **D — cite-or-be-silent** | Any `plugins/forms-engineering/**/*.md` whose body mentions uploads, Turnstile, CAPTCHA or a challenge token must carry **≥1 markdown link that RESOLVES into `plugins/ravenclaude-core/`** | the paraphrase paragraph above, in a file with no core link | the same content replaced by `→ [security.md](../../ravenclaude-core/rules/security.md)` |

A paraphrase cannot evade a **positive** requirement by word choice — that is exactly why it works where
B and C do not. Discussing the topic *at all* obliges a pointer home. The link must **resolve** (`test -e`
on the target path), not merely be link-shaped; a dangling link is a violation, not a pass.

⛔ **P2's anti-duplication probe inherits the same blind spot** — it greps the *same six phrases*, and
its positive control (grep `ravenclaude-core/` first) proves the grep **runs**, not that it detects a
paraphrase. P2's probe therefore also gains the sub-check D form: for each new knowledge file mentioning
uploads/Turnstile, count resolving links into `plugins/ravenclaude-core/` and require ≥1.

**Plus the separability acceptance test** (P7): delete the two allowlisted files → full suite green.

### 5.2 Gate 220 — `check-form-metrics.py` (P5)

The strongest gate design in either plan, kept whole in shape and **repaired in mechanism**. Runs
`form_metrics.py` against a committed fixture CSV (**≥20 rows** — see below); asserts each
**hand-computed** expected value per-assertion; **negative controls**: malformed CSV → non-zero exit,
completions > starts → non-zero exit. Must-fail proof: a deliberately wrong expected value makes the
gate RED.

⛔ **G6-REPAIR (H3 + M4) — the round-trip as originally written DID NOT EXECUTE.** `lss_calc.py imr` has
`--values required=True` and **no stdin path** (`lss_calc.py:372-375`); the piped form exits **2** with
the left side discarded. The pipe is replaced by command substitution, and Gate 220 now asserts **three**
things, not one:

| # | Assertion | Proven to distinguish |
|---|---|---|
| **(i)** | `lss_calc.py imr --values "$(form_metrics.py --emit-imr <fixture>)"` exits **0** and its stdout carries both `UCL` and `LCL` | good mock rc 0 / bad mock rc 2 |
| **(ii)** | `--emit-imr` stdout is **numeric-only**: `bad=$(… \| grep -c -v -E '^[0-9eE+.,[:space:]-]*$'); [ "$bad" -eq 0 ]` | 0 bad lines / 1 bad line |
| **(iii)** | the **verbatim §6.1 marker** appears in captured **stderr** of a plain run **and** of `--emit-imr` | present / absent |

(iii) is an **execution** assertion and is the surface-5 half of §6.1 that Gate 221 sub-check A cannot
honestly cover (M4). ⛔ Write (ii) as a **count**, never as `grep -q -v`: on this host
(`ugrep 7.5.0` as `grep`) adding `-q` to `-v` inverts the result *toward clean* — `grep -v` returns rc 0
where `grep -qv` returns rc 1, measured. A first draft of (ii) used `-q -v` and passed the bad fixture.

**Fixture minimum: 20 individual observations.** `cmd_imr` accepts **n ≥ 2** (`lss_calc.py:259-261`), so
without a stated floor this gate would certify "valid control limits" on a 2-point series — exactly what
best-practice rule #5 forbids. **The gate must not bless what the plugin prohibits.** Rule #5 states the
same figure; the two are checked against each other in P4.

### 5.3 Gate 221 — `check-forms-honesty-markers.py` (P1)

**B wins on enforcement** (§10, T1): honesty constraints ship as **permanent numbered CI gates with
must-fail halves**, not A's one-time manual release greps. A's greps were additionally broken — they
searched for `"novel synthesis"` and `"not aware of prior published work"`, **neither of which appears
in A's own mandated sentence**, and its Turnstile probe required `WCAG 2.2 AA` and `Turnstile` on the
same **physical line**, which wrapped markdown prose almost never produces. Both would have reported
green while measuring nothing.

**One script, one gate number, three sub-checks, all run and aggregated (no short-circuit)** — three
separate gate numbers would triple the Gate 195 registration surface for no added signal:

| Sub-check | Asserts | Must-fail fixture | Must-pass fixture | Extra fixture |
|---|---|---|---|---|
| **A — novel-synthesis marker** | **scoped to `plugins/forms-engineering/**/*.md`** (G6-REPAIR M4 — the script's own output is Gate 220's job, not a string check's): every doc file that co-occurs an SPC/DMAIC term (control chart, X-mR, DMAIC, sigma, common-cause, special-cause) with a form-analytics term (`form_start`, abandonment, drop-off, completion rate) carries the **verbatim marker string** (§6.1). **All five §6.1 doc surfaces must be in the passing set** — including rule #5 and `templates/form-telemetry-plan.md`, which co-occur both families by construction | a file with both term families and no marker | a marked file | ⛔ **must-pass fixture: rule #5's own filename+body**, proving the gate does not go red on required content (M4's contradiction, regression-locked) |
| **B — Turnstile WCAG named conflict** | no file states `WCAG 2.2 AA` or `WCAG 2.2 AAA` **anywhere within N lines of** a Turnstile mention without the conflict phrasing in the same block. **Line-window based, never same-physical-line** | a file asserting "Turnstile is WCAG 2.2 AA compliant" | the named-conflict paragraph | — |
| **C — no vendor pricing** | no prose line carries a currency figure, `/mo`, `/month`, `per month`, `per year` | `"Vendor X costs $29/month"` | a decision-axis sentence | ⛔ **negative-instruction fixture**: *"do not state a specific price such as an example figure"* must **NOT** trip the gate |

Two limitations are **written into the shipped script's own header**, because a gate with a documented
blind spot beats a gate that oversells itself:

1. Sub-check A is **file-level co-occurrence, not paragraph-level** — a second unlabelled synthesis
   claim later in an already-marked file evades it. A human read at authoring time is still required.
2. All three are **string-shaped**. This repo has recorded twice that *source-scan gates match PROSE*
   and *a grep is satisfied by the thing being described*. These gates measure "a sentence is present",
   not "the content is honest". They raise the floor; they do not certify the property.
3. ⛔ **G6-REPAIR (M4): sub-check A covers DOCUMENTATION SURFACES ONLY.** It does **not** and cannot
   verify that `form_metrics.py` **prints** the marker — a marker in a docstring, a comment, or an
   unexercised branch satisfies a file-level string check identically to one emitted on every run. That
   half is **Gate 220 assertion (iii)**, which executes the script and reads captured stderr. A reader
   of this script must not infer script-output coverage from a green sub-check A.

Sub-check C must be **scoped to prose lines** — a `$PATH`, a shell snippet, or a `$` in a code fence
would otherwise false-positive.

#### ⛔ G6-REPAIR (M4) — sub-check A contradicted §6.1, and was satisfiable by a DOCSTRING

**Two defects, two fixes.**

**1. The contradiction.** Sub-check A fires on any file co-occurring an SPC/DMAIC term (…**sigma**…)
with a form-analytics term (…**abandonment**, **completion rate**…). But §6.1 listed only **three**
required surfaces. Best-practice rule #5 is literally named
`do-not-put-three-sigma-limits-on-a-low-volume-form-series.md` — "sigma" is in its **filename** and
unavoidably in its body, and "form series"/"abandonment"/"completion" are its subject. Same for
`templates/form-telemetry-plan.md`. Both co-occur both families; **neither was on §6.1's list.** Gate
221 would go red at P4 on the plugin's own required content, and the remedy under time pressure is to
narrow the term list — R5/CE-7's failure mode.
**Fix: §6.1's required-surface list grows to five** (see §6.1). The marker is verbatim and adding it to
a one-rule file costs nothing. Do **not** exempt files "whose only SPC term is in a prohibition" — that
exemption is unspecifiable and is how the term list starts shrinking.

**2. The silent half.** §6.1 requires the marker to be *"printed by `form_metrics.py`'s own output"*.
Sub-check A is a **file-level string co-occurrence check** — a marker sitting in a module docstring, a
comment, or an `if args.verbose:` branch no gate exercises satisfies it **identically** to one printed
on every run. This is the repo's recorded trap verbatim: *a grep is satisfied by the thing being
described* — the `[[r2_buckets]]`-in-a-comment case that flipped a tracker item to DONE with nothing
bound. This plan **quotes that incident in P7** and then reproduced its shape here.
**Fix: the PRINTING assertion moves out of Gate 221 and into Gate 220, which already EXECUTES the
script.** Gate 220 asserts the verbatim marker in **captured stderr** of a plain run **and** of
`--emit-imr` (H3's stream contract). An execution assertion cannot be satisfied by a docstring. Gate 221
sub-check A keeps only the **documentation** surfaces; it no longer claims to cover the script's output,
and its script header says so.
**Library-import path:** if `form_metrics.py` is imported rather than run, a marker printed inside
`main()` never executes. Emit it from the **public entry function** (or module import), and state in the
module header that a caller who suppresses stderr owns the omission.

#### ⛔ G6-REPAIR (M5) — §5.5: `path:line` citations ROT, and P8 is the phase that rots them

The plan pins `security.md:43-45`, `cloudflare-who-gets-in.md:51,53`, `frontend-implementer.md:41,48,60`,
`accessibility-auditor.md:48,92`. **All four are accurate today** — re-verified this session. But
`accessibility-auditor.md:92` is load-bearing three times over (§0.3 justifies the plugin with it, R2
grounds the zero-agent ruling on it, P3 writes it into every skill's `## Not this skill` block), and
**P8 by ruling R5 inserts up to 3 body lines into that same file.** The red team demonstrated line 92
shifting off the zero-exception routing rule it is cited for — **P8 invalidates a citation P3 already
shipped, in the same run**, and nothing notices:

- `scripts/check-md-links.py:19-20` explicitly **does not validate anchor fragments**.
- A link target written literally as `…/rules/security.md:43-45` is not a path that exists, so the link
  checker would go **red** — the plan's own citation style cannot be expressed as a checked link at all.
- Gate 219 sub-check B keys on citation **form**, never on citation **target**.

**Binding remedy — cite by stable ANCHOR TEXT, not by line number:**

| Cited file | Anchor text that ships (verified present this session) |
|---|---|
| `ravenclaude-core/rules/security.md` | `Uploads: validate type by content (magic bytes), not extension` |
| `web-design/agents/accessibility-auditor.md` | `zero-exception` |
| `ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md` | `Secret key` |
| `web-design/agents/frontend-implementer.md` | `native HTML form patterns first` |

Each returns **1** today; a deliberately absent control string returns **0** — the check distinguishes.

- **One assertion added to Gate 219:** for each cited file, its quoted anchor text must still be found
  (`grep -c -F "<anchor>" <file>` ≥ 1). That is a real, cheap must-fail half — delete the sentence
  upstream and the gate goes red.
- **Line numbers stay in THIS plan and in `claims-table.md` only — never in shipped content.**
- Sequence P8's edits to append **below** the cited lines where possible, and re-read §0.3's citations
  at P9 as part of DoD.
- ⛔ Note the anchor text for `accessibility-auditor.md` is deliberately the short distinctive token
  `zero-exception`, not the whole sentence: the sentence may legitimately be re-worded, the property
  being cited may not.

### 5.4 ⛔ CE-5 — the Gate 195 registration triple

`scripts/audit-gates.sh:1008` runs `scripts/check-gate-registration.py` (Gate 195), which enforces
**reachability + number-uniqueness + dispatcher/`Supported:` parity**, plus a `--self-test` teeth gate.
**Both plans were blind to it** (`grep -c "195"` → 0 / 0).

**Every new gate registers in ALL THREE places:**

1. The **main sequence** — the `echo "── Gate N: … ──"` block plus its assertions, in numeric order.
2. The **`--check` dispatcher case arm** — a `N)` arm (shape verified at `scripts/audit-gates.sh:522`,
   which is Gate 218's). **Plan A's file list omitted this entirely**, which would have put 219 in
   `Supported:` and not in the arms → Gate 195 parity RED → masking every later gate in the same step.
3. The **`Supported:` string** (`scripts/audit-gates.sh:1149` post-harden) — append the number.

**Verification, keyed on the thing that EXECUTES:**
- `bash scripts/audit-gates.sh --check <N>` exits 0 (a missing arm hits `*)` and exits 1 with
  *"gate '<N>' is not registered for per-gate runs"*).
- `python3 scripts/check-gate-registration.py` and `--self-test` both exit 0.
- ⛔ **Do NOT verify a gate ran by grepping the suite output for `"Gate <N>"`.** A batched
  `── Gates 120–125 ──` header once made that grep return 0 for **seven gates that all ran**, and the
  false red nearly caused a "restoration" of gates that were never lost. Key on the **script name in
  the executed line** and on `--check` exit codes.
- **B's registration check is void as written**: `grep -c "check-novel-synthesis-marker\|…" scripts/audit-gates.sh`
  ≥3 — *a grep for a script name is not evidence of registration*. So is B's backstop "confirm the
  total gate count increased by exactly 5": every recent numbered gate registers **two** assertions
  (main + `--self-test` teeth), the suite counts assertions not numbers, and
  `.github/workflows/validate-marketplace.yml:7` puts the suite at ~593 gates, where an off-by-a-few is
  invisible.

**CI wiring, re-confirmed:** `scripts/audit-gates.sh` is invoked by
`.github/workflows/validate-marketplace.yml` with **no `paths:` filter** (deliberate and load-bearing).
Any gate genuinely registered inside it **is** CI-wired — which keeps these three out of the "39 of 49
gates invoked by no workflow" population. Re-confirm this with one grep at P9; never add a `paths:`
filter to a required workflow.

---

## 6. Honesty constraints (both enforced by CI gate, per §10 T1)

### 6.1 The forms↔SPC/DMAIC join has NO established literature

Row 101 is a **verified negative**: two targeted searches returned SPC/DMAIC generalities and
form-analytics generalities with **zero intersection**. Presenting the join as received practice would
be exactly the confident-reasoning error this repo's Claim Grounding rule targets. Vigilance will not
hold it; three mechanisms will.

**The verbatim marker string, used identically in every surface** (so the gate can match exactly rather
than fuzzily):

> `[NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not established practice. We
> found no published work joining web-form telemetry to SPC/DMAIC (open-web search, 2026-08-17); the
> negative finding is bounded by that method and is not proof of universal absence.]`

⛔ **G6-REPAIR (M4) — the required-surface list was THREE and Gate 221 sub-check A fires on FIVE.**
Rule #5 (`do-not-put-three-sigma-limits-on-a-low-volume-form-series.md`) carries "sigma" in its own
filename and "form series"/"abandonment"/"completion" as its subject; `templates/form-telemetry-plan.md`
is the same shape. Both co-occur both term families and neither was listed — so Gate 221 would go red at
P4 on this plan's own required content, and the remedy under time pressure is to narrow the term list
(R5/CE-7's failure mode). **The list is now FIVE surfaces:**

1. `knowledge/form-telemetry-and-spc.md`
2. `skills/form-telemetry-and-control/SKILL.md`
3. `best-practices/do-not-put-three-sigma-limits-on-a-low-volume-form-series.md` *(added)*
4. `templates/form-telemetry-plan.md` *(added)*
5. `scripts/form_metrics.py` — **emitted on `stderr`, in every mode**, so a user who never opens a doc
   still sees it *(and see the stream contract in P5 / H3: the marker must NOT go to stdout, or it
   poisons the `--emit-imr` round-trip)*

**Split of enforcement, deliberate** (G6-REPAIR M4): surfaces **1–4** are enforced by **Gate 221
sub-check A** (a documentation-surface string check). Surface **5** is enforced by **Gate 220**, which
**executes** the script and asserts the marker in **captured stderr**. Sub-check A is file-level string
co-occurrence and would be satisfied identically by a marker sitting in a docstring, a comment, or an
unexercised `--verbose` branch — *a grep is satisfied by the thing being described*, the recorded
`[[r2_buckets]]`-in-a-comment defect this plan quotes in P7. **Only an execution assertion proves the
label reaches a user.** Both gates are permanent, on every future PR, not once at release.

**The paired hazard ships with it, before the method, not in a footnote** (row 102): form-conversion
series are low-volume and autocorrelated by weekday and campaign, so naïve 3-sigma limits manufacture
false special-cause signals on a small-business form. That is best-practice rule #5.

And row 105's sibling gap: **"last field interacted" as a proxy for "the field that caused
abandonment" is used uncritically by every vendor and validated by none.** `form_metrics.py` prints the
proxy caveat in its own output column header.

### 6.2 Cloudflare's docs CONTRADICT THEMSELVES on Turnstile's WCAG level

Row 96: the Turnstile **overview page** says "WCAG 2.2 AA compliant"; the **plans page** tabulates
"WCAG 2.2 AAA" for Free. **Ship it ONLY as a named conflict. No surface may state either level
unqualified.** The shipped sentence:

> Cloudflare's own documentation gives **AA** in one place and **AAA** in another. We do not repeat
> either figure unqualified; treat Turnstile's conformance level as **unestablished pending a VPAT**,
> and verify independently before relying on it.

Enforced by **Gate 221 sub-check B**, line-window based (never same-physical-line — that was A's broken
probe). Note the gate is scoped to `plugins/forms-engineering/`; the conflict caveat arguably also
belongs in `ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`, which is outside this
plan's edit set. **Ruled in §11.3.**

---

## 7. Portability floor (binding on every shipped script)

Stock macOS is the target. **Doors 1–4 are closed and must stay closed.**

| Constraint | Why |
|---|---|
| **bash 3.2** — no `declare -A`, `mapfile`, `${x^^}`, `shopt -s globstar` | stock macOS ships bash 3.2 |
| ⛔ **no GNU `timeout`** — use `perl -e 'alarm N; exec @ARGV'` | GNU `timeout` is **absent** on stock macOS; a sweep wrapped in it once ran **zero** programs and printed a clean table |
| **no `grep -P`** | BSD grep has no PCRE |
| **no `sed -i`** | BSD `sed -i` requires a backup-suffix argument and silently differs |
| **Python 3.9** — stdlib only; `from __future__ import annotations` if any `X \| None` appears | measured interpreter is 3.9.6 |
| **`python3 -m pip`**, never bare `pip` | bare `pip` is absent on stock macOS |
| Hook protocol proven in **both** invocation modes (stdin JSON and `$1`) and **both** directions, under `env -i PATH=/usr/bin:/bin bash` | row 37's method |

⛔ **zsh trap:** `git show "$B:file"` returns the **COMMIT**, not the file — quoting does not help. Use a
literal SHA in any probe that reads a file at a revision.

⛔ **G6-REPAIR — `grep -q -v` INVERTS THE ANSWER TOWARD CLEAN on this host. Binding on every gate
script.** Measured (`grep` here is `ugrep 7.5.0`), on input `abc\n123\n`:

| form | result |
|---|---|
| `grep -v '^[0-9]*$'` | prints `abc`, **rc 0** (a violation was found) |
| `grep -q -v '^[0-9]*$'` | prints nothing, **rc 1** (reads as *no violation*) |
| `grep -c -v '^[0-9]*$'` | **1** ✅ |

An "every line must match P" assertion must therefore be written as a **count of violating lines**:

```sh
bad=$(printf '%s\n' "$out" | grep -c -v -E 'PATTERN'); [ "$bad" -eq 0 ]
```

Two compounding reasons, both live: `-q` + `-v` misreports here, **and** plain `grep -q P` succeeds if
**any** line matches — so an anchored per-line rule expressed as `grep -q` asks "does *some* line
conform?", never "do *all* lines conform?". A draft of Gate 220's numeric-only assertion used `-q -v`
and **passed the deliberately-bad fixture**. This is the same family as the recorded *"my own probes
fail silently toward clean"* pattern; it was caught only by running the assertion against a fixture
designed to fail it.

---

## 8. Risk matrix

Probability × impact. **Trigger** = the observable event that says the risk has fired. Merged from the
critic's matrix, re-scored against this plan's mitigations; rows whose cause this plan removed are
marked **CLOSED** rather than deleted, so a future editor can see they were considered.

⛔ **G6-REPAIR — G5 red-team findings, all four HIGHs and five MEDs, folded in below as H1–H4 / M1–M5.**
Every one was a **broken acceptance test inside this plan**, not a build risk: three of the four fired
in the first two phases. Each is marked **MITIGATED** with the mechanism and the command that proves the
mechanism distinguishes pass from fail. The pre-existing R1–R14 rows are unchanged in scope; R2, R4, R5,
R6 and R14 are re-scored where a repair moved them.

| # | Risk | P | Impact | Trigger — what you would see | Mitigation in this plan |
|---|---|---|---|---|---|
| **R1** | **Duplicated content vs `ravenclaude-core`** (CE-1) — upload rules / Turnstile facts shipped as new, diverging from a `refresh_when:`-maintained concept doc | **Med** (was High; the content is deleted, but an author can re-add it) | **High** — breaks single-source-of-truth in the constitution | The new tree contains "magic bytes" / "server-generated filename" / "siteverify" **outside a link line** | §0.4 deletes the files; **Gate 219 sub-checks B+C** with must-fail fixtures; P2's positive-controlled anti-duplication probe |
| **R2** | **Collision with `fix/conversion-design-field-folklore` (PR #959)** — P8 edits a section an unmerged branch rewrote, or restores a deleted unsourced table | **Low** (was High) | **Med-High** | ⛔ **Trigger CORRECTED (H1):** `grep -c '^\| 1 (email only) \|'` → **≥1** at P8 time. The old trigger `grep -c "35–50%"` → 1 fires on **every** state including the correct one | Hard **STOP** gates at P0 acc.2 and P8 pre-build, now using the **bidirectional pair** (H1); the #959-CLOSED branch ruled in §2.1; A's "call it a prior, not a law" remedy explicitly **voided**. ⛔ Note: **#959 and #960 do not conflict with each other** — both `CLEAN` simultaneously, hunks 140 lines apart. Merge order between them is immaterial |
| **R3** | **Gate 195 goes red** on a mis-registered gate, masking every later gate in the same CI step | **Med** (was Med-High) | **High** — CI red on shared infrastructure | `--check <N>` → *"gate '<N>' is not registered for per-gate runs"*, or the parity assertion fails | §5.4 registration triple + `check-gate-registration.py` (+`--self-test`) in every gate-touching phase's acceptance list |
| **R4** | **Separation gate negotiated down to nothing** (CE-6) — the blocklist trimmed to fit content that already violates it | **Low** (was High) | **Med** — false assurance of "separable" | The Gate 219 token list shrinks during build, or the allowlist grows past 2 files, **or `hooks/*.sh` gets added to the allowlist at P6** | Gate ships in **P1, before any content**; §5.1 keys on *citation form*. ⛔ **Re-scored by M3:** it was **open in a new place** — §5.1 had no file-type scope, so P6's own hook would have forced exactly this negotiation. Scope is now decided in P1 (`**/*.md` only) with a `.sh` must-pass fixture locking it |
| **R5** | **The honesty label passes while the content reads as received practice** (CE-7) | **Med** | **High** — the reputational claim; a false "we labelled it" is worse than no label | A second SPC×form-telemetry paragraph in a file whose header carries the marker, and the gate is green | Gate 221 is permanent, not a release grep; **the paragraph-level blind spot is written into the script's own header**; a human read is a named P2 **and P4** step. ⛔ **Re-scored by M4 — it was wider than scored:** nobody had documented the **execution** blind spot (marker in source ≠ marker printed). That half now moves to **Gate 220**, which runs the script, and §5.3 limitation #3 states the boundary |
| **R6** | **The plugin rots** — zero agents, no inbound `works_with`, discoverable only by typing `/` | ⛔ **Med** (raised from Low-Med by **M2**: 131 of 181 plugins are disabled as the ambient condition, and **one of the five priors lands in a disabled plugin**. "A file names it" is not the same property as "something routes to it", and the file-existence probe cannot see the difference) | **Med** — the deliverable is unreachable | Six months on: `grep -rn "forms-engineering" plugins/ --include=*.md` outside the plugin returns ~0 | P8 reciprocal priors (now authorized) + the reachability probe **with a positive control**; `commands/design-form-intake.md` as a second path. **If it fires, R2's remedy is exactly one first-contact agent** (`tiebreaks.md` falsifier 3) |
| **R7** | **Content bank oversized for the actual gap** — (b) and (c) re-authored rather than delta'd | **Low** (was Med) | **Med** — maintenance liability + duplication surface | The new best-practices index and `web-design`'s state the same rule in different words | R4 collapses (b) to one delta file; 11 rules → 7; 7 skills → 4; §3.4's "deliberately NOT written" list; the inherited-rules table is written **first** |
| **R8** | **Merge conflict on `audit-gates.sh`** — concurrent appends to a 7,480-line shared file | **Low-Med** | **Med** | Conflict markers in `scripts/audit-gates.sh`, or a `Supported:` number with no matching case arm | §2.3 **gate-file baton** (219+221 → 220 → Gate 30), full suite between hand-offs |
| **R9** | ~~B's PI acceptance test measures nothing (`wc -l \| tail -1`)~~ | — | — | — | **CLOSED** — the PI track shipped separately (§0.1). Recorded so it is not reintroduced by copy-paste |
| **R10** | **Substrate facts rot** — the dead R2 bucket / unverified Resend domain are live, changeable state | **Med** | **Med** | RavenPower-Website binds `UPLOADS` and the shipped file still says it is inert | B's re-verification-command design (P7), including the **inside-the-block, not-the-comment** requirement; A's static `src/…:line`-only approach rejected |
| **R11** | **Row 61 (Resend) is `[unverified — carried from memory, not re-probed]`** and ships as substrate fact | **Low** | **Low** | The marker is dropped during authoring | P7 pre-build gate; §12 names the settling probe |
| **R12** | **A dead routing target ships** — a named skill that no consumer can resolve | **Low** | **Med** — the skill reads authoritative and routes into a void | `test -e` fails on a path in a `## Not this skill` block | P3's `plugins/`-scoped resolver loop; `turnstile-spin` already caught and ruled out (§11.1) |
| **R13** | **A `## Decision Tree:` heading slips in**, creating an unmet committed-SVG + Chromium CI obligation | **Low** | **Med-High** — recorded catastrophic failure mode (printed "ok", deleted 800+ SVGs) | `render-trees.py --check` output changes | P2 pre-build gate + `--check` **unchanged** as an acceptance test |
| **R14** | ~~**`prettier` / `ruff` whole-tree gates fail on an unrelated pre-existing file**, blocking the PR~~ | — | — | — | **INVERTED, not closed — see M1.** Measured: the ruff gate does not **fail**, it **SKIPS**, and the suite still exits **0**. The risk was scored in the wrong direction: the danger is a silent pass, not a noisy block. P0's baseline still governs attribution |

### G6-REPAIR — the G5 red-team rows

| # | Finding | Sev | Trigger — what you would see | Status + mechanism | Command that proves the mechanism distinguishes pass from fail |
|---|---|---|---|---|---|
| **H1** | **The PR #959 STOP sentinel is unsatisfiable** — `grep -c "35–50%"` → 0 can never hold, because #959's retraction quotes the figure it removed | HIGH | The run halts permanently on a state that is actually correct — or the operator concludes the gate is broken and **deletes** the one defense against re-adding the unsourced table | ⛔ **MITIGATED.** Replaced by a **bidirectional pair** — `^\| 1 (email only) \|` → 0 (structure) **AND** `removed rather than re-cited` → ≥1 (positive control), at §2.1, P0 acc.2 and P8 pre-build. Plus the previously-missing **#959-CLOSED branch** (§2.1): the sentinel becomes **void**, not failed, and P4 links to §3 as it stands | `for r in origin/main origin/fix/conversion-design-field-folklore; do git show $r:plugins/web-design/skills/conversion-design/SKILL.md \| grep -c '^\| 1 (email only) \|'; done` → **1** then **0**; the control half → **0** then **1**. The old probe → **1 on both**. Both halves flip; the old one does not move |
| **H2** | **`--check 30`, `--check 18`, `--check 29` are unregistered** and exit 1 unconditionally (~10 uses across P2/P3/P4/P6/P8 + DoD #11). P6's hook-mutation **teeth proof keyed on `--check 30`'s exit code — so it passed vacuously** | HIGH | Every one of ~10 acceptance steps reads red on a clean tree, training the operator to skip `--check` output — including 219/220/221, the three that work. And a decorative Gate 30 fixture pair ships, reproducing row 40 on day one | ⛔ **MITIGATED.** All uses removed. 29 → `python3 scripts/check-md-links.py`; 18 → `python3 scripts/check-frontmatter.py`; **30 → full suite, keyed on the flipped NAMED ASSERTION LINE**, never a per-gate exit code (P6, DoD #14). Deleted from DoD #11 **with the reason recorded** so a future editor does not re-add them | `bash scripts/audit-gates.sh --check 30` → exit **1**, *"not registered for per-gate runs"*, on a tree measured `815 pass, 0 fail`. Mutation proof executed against the existing `process-improvement` hook: `✓ …(fires on anti-pattern)` **1 → 0** and `✗ …(fires on anti-pattern)` **0 → 1** across the mutation; suite exit **0 → 1**; hook restored, `git diff --stat` → 0 |
| **H3** | **The P5/T2 round-trip does not execute** — `lss_calc.py imr` has `--values required=True` and no stdin path; and §6.1's marker on stdout would poison the pipe even after a naive fix | HIGH | The plan's **only mechanical proof of its only no-prior-art claim** (T2) exits 2. Loud enough to notice, expensive enough to invite a shortcut | ⛔ **MITIGATED.** Binding **stream contract** (P5, §5.2): `--emit-imr` writes numbers-only to **stdout**; the NOVEL-SYNTHESIS marker goes to **stderr in every mode**; the round-trip becomes `--values "$(…)"`. Gate 220 asserts **three** things — round-trip exit 0 + UCL/LCL, numeric-only stdout, marker-in-stderr. **Minimum n named as 20**, matching rule #5, so the gate cannot bless a 2-point series the plugin forbids | Piped form → **exit 2**. Substitution form with 20 readings → **exit 0**, `readings (n) : 20`, UCL/CL/LCL printed. Good-vs-bad mock across all three assertions: **PASS/PASS/PASS** vs **FAIL/FAIL/FAIL** |
| **H4** | **Gate 219 sub-checks B+C cannot fail on a paraphrase** — six literals, and every must-fail fixture was a verbatim copy. §0.4 claimed mechanical enforcement that did not exist | HIGH | Silent and compounding: a restatement of `security.md:43-45` in different words ships green, then diverges the first time Cloudflare or the rule changes, with nothing pointing at it | ⛔ **MITIGATED — by (d), honestly scoped by (a)–(c).** (a) a **paraphrase must-fail fixture** is committed; (b) the limitation is written into `check-forms-substrate-separation.py`'s header, as §5.3 already does for 221; (c) **§0.4's "not by author discipline" claim is amended** — a human read is a named step in P2 **and P4**; (d) **new sub-check D**: any forms file discussing uploads/Turnstile must carry ≥1 **resolving** link into `plugins/ravenclaude-core/`. A positive requirement cannot be evaded by word choice | Three fixtures run: literal hits **2 / 0 / 0** (verbatim / paraphrase / linked) — C misses the paraphrase. Sub-check D: **VIOLATION / VIOLATION / ok** — D catches it and still passes the correctly-linked file |
| **M1** | **Gate 9b (ruff) is the one SKIPPED gate and the suite still exits 0**; DoD #8's literal command was broken on this host | MED | `815 pass, 0 fail, 1 skipped` → **SUITE EXIT=0**; the three new Python files never linted locally while the suite reads green | ⛔ **MITIGATED.** P0 acc.6 is now a **hard STOP** using `python3 -m ruff` + a PATH prepend; DoD #8 fixed; DoD #10 adds `grep -c 'SKIPPED'` → **0** and states that **a skip is not a pass** and does not inherit the baseline-attribution licence | `ruff check .` → **rc 127**; `python3 -m ruff check .` → **rc 0**. `grep -c SKIPPED`: **2** without ruff on PATH, **0** with (`817 pass, 0 fail, 0 skipped`) |
| **M2** | **`process-improvement` is DISABLED in the owner's config** (131/181 disabled), so P8 prior #5 is inert while the file-existence probe reports green | MED | Probe says 5/5; one referrer does not load, and `form-telemetry-and-control`'s own routing targets are in the same disabled plugin | ⛔ **MITIGATED as a REPORTING requirement + an explicit waiver.** The P8 probe now reads `enabledPlugins` and **prints** each referrer's enabled state (does not fail on it — the owner's config is not the consumer's). The telemetry seam being **dark whenever `process-improvement` is disabled** is recorded as **accepted**. R5's five-file budget is **not** re-opened; the measurement is filed as the evidence that would justify a sixth prior if R6 fires | `python3` read of `~/.claude/settings.json` → `total 181 enabled 50 disabled 131`, `process-improvement@ravenclaude **False**`, `web-design`/`ravenclaude-core`/`data-platform` **True**. `test -e` on a path inside the disabled plugin still **succeeds** — which is the defect |
| **M3** | **Gate 219 has no file-type scope**, so P6's own hook trips it; and bare `"single-use"` false-positives on rule #3 | MED | Gate 219 goes red the moment P6 lands; both remedies are the blocklist being trimmed to fit content — **CE-6 / R4 recurring** | ⛔ **MITIGATED, and decided in P1 before any content exists to pressure it.** Scope is `plugins/forms-engineering/**/*.md` **only**; `hooks/`, `scripts/`, `tests/fixtures/` out by construction with the reason in the script header. `"single-use"` becomes a **co-occurrence** requirement with a Turnstile/challenge mention. A **`.sh` must-pass fixture** containing `cf-turnstile` regression-locks the scope | Fixture `.sh` containing `cf-turnstile`: `*.md`-scoped sweep → **0 hits**; unscoped sweep → **1 hit** |
| **M4** | **Gate 221 sub-check A contradicts §6.1's surface list** (rule #5 carries "sigma" in its filename) **and is satisfied by the marker sitting in source rather than PRINTED** | MED | Gate 221 red at P4 on the plugin's own required content; and a docstring marker certifies "the user sees the label" | ⛔ **MITIGATED, both halves.** §6.1's required-surface list grows **3 → 5** (rule #5 + `templates/form-telemetry-plan.md`), with rule #5 added as a **must-pass fixture** so the contradiction is regression-locked. The **printing** assertion moves to **Gate 220, which executes the script**, asserting the marker in captured **stderr**; sub-check A is scoped to doc surfaces and its header says so. Library-import path covered by emitting from the public entry function | Gate 220's assertion (iii) on good vs bad mock: marker in stderr **PASS / FAIL**. A file-level string check returns identical results for a docstring and a printed line — which is why (iii) had to move to the executing gate |
| **M5** | **`path:line` citations rot, and P8 is the phase that rots them** — `accessibility-auditor.md:92` is load-bearing 3× and P8 inserts up to 3 lines into that file | MED | *"A link to the right file, a line number to the wrong line"* — reads authoritative, is wrong. `check-md-links.py:19-20` does not validate anchors, and a `file.md:43-45` target is not a resolvable path at all | ⛔ **MITIGATED.** New **§5.5**: cite by **stable anchor text**, not line; **one assertion added to Gate 219** requiring each cited file to still contain its quoted anchor (`grep -c -F` ≥ 1); line numbers stay in this plan and `claims-table.md`, **never in shipped content**; P8 appends below cited lines; P9 re-reads §0.3's citations | All four anchors return **1** today (`Uploads: validate type by content (magic bytes), not extension`; `zero-exception`; `Secret key`; `native HTML form patterns first`); a deliberately absent control string returns **0**. The check moves |
| **L1** | **rerere armed with 93 cached resolutions**, at least one covering gate blocks and one covering the marketplace plugin array — both files this plan appends to | LOW-MED | A silently auto-resolved rebase conflict in `audit-gates.sh` or `marketplace.json` | **MITIGATED, mechanism-verified but bad outcome NOT reproduced.** P8 pre-build now mandates `git -c rerere.enabled=false rebase`, post-integration re-assertion of `grep -c "Gate 218"` ≥ 2 and the H1 sentinel pair, and the two-parent check before pushing any merge | Red team could not construct a **green** bad outcome (Gate 195 parity and the version-mirror gate both catch the plausible ones). Recorded at LOW-MED with that limit stated, not inflated |
| **L2** | **DoD #23's scope wall flagged the plan's own P1 fixtures as a scope breach** — `tests/fixtures/**` was not in the allowed set | LOW | A self-contradicting acceptance test, which is the kind that gets waved through | ⛔ **MITIGATED.** `tests/fixtures/**` added to DoD #23 | It is already an allowed glob in `.repo-layout.json` and already holds `bad-marketplace.json` / `bad-plugin.json` — the layout hook permitted exactly what the wall forbade |

⛔ **Standing rule this repair establishes for the build: an acceptance test that has never been
EXECUTED is not an acceptance test.** All four HIGHs were unrun tests inside an authoritative plan, and
two of them (H2's teeth proof, H4's must-fail halves) *reported success while measuring nothing* —
failing toward clean. While repairing them, a **fifth** instance was produced and caught only by running
it: a numeric-only assertion written as `grep -q -v` **passed the bad fixture** (see P5/§5.2). Before any
gate in this plan is considered done, show it going **red** on something.

---

## 9. Alternatives considered

| # | Approach | Trade-off | Verdict |
|---|---|---|---|
| **A1** | **Extend `web-design`** with a forms sub-bank | Zero new catalog entries, reuses live agents — but leaves the (c) server half homeless in a plugin that **routes security OUT by rule** (`accessibility-auditor.md:92`), leaves (a)/(d) unowned, and pushes the largest domain plugin further past every shape baseline. Note the *cost* argument for standalone is void (§R6): on marginal agent cost the two are **tied**; the case is structural, not economic. | **Rejected** (R1) |
| **A2** | **Two plugins** — `form-design` (UX+a11y) and `form-engineering` (security+platform) | Cleanest boundaries — but doubles registration/README/CLAUDE/CHANGELOG overhead, splits discipline (a) across both, and manufactures the dispatch ambiguity the house rule exists to prevent. | **Rejected** |
| **A3** | **Skills-only into `ravenclaude-core`** (the `brand-extraction` precedent) | Genuinely tempting — forms are domain-neutral. But core is the **constitution**, and a vertical bank with a vendor substrate layer is a domain body, not a protocol every agent inherits. It would also make the RavenPower substrate inseparable from core. | **Rejected** |
| **A4** | **Ship the WCAG-2.2 delta into `web-design`'s own best-practices bank** instead of a forms file | Puts the five criteria with their natural owner and needs no cross-link. But authoring new content inside another plugin's bank exceeds the owner's authorization (which covers reciprocal *priors*), and it splits the forms narrative. | **Rejected as primary; revisit** if the delta file grows past ~1 screen or acquires non-form criteria |
| **A5** | **Pure-routing (c) skill — no owned best-practice files at all** (B's Alternative 3) | B rejected this **solely** because "file-upload has no routing target (row 16)" — a **broken grep** (§0.4). The target exists: `ravenclaude-core/rules/security.md:43-45`. | **Partially ADOPTED.** File-upload is now routing, not owned content. The skill retains owned content only for honeypot, double-submit/idempotency, and PII minimisation, which are genuinely unowned |
| **A6** | **Ship one agent** (`forms-engineer`) to make the plugin self-dispatching | Removes the P8 dependency — but fails the carve-out on all three grounds in R2 and buys reachability an inline prior gives for free. | **Rejected; reversible.** Adding one agent later if R6 fires is cheap; deleting a shipped agent after `works_with` edges form is not |
| **A7** | **A `substrate/` directory** instead of a two-file allowlist | `AGENTS.md` sanctions a one-line `.repo-layout.json` edit, so A's "expensive edit" premise was unsupported (critic §2.4). But `plugins/*/substrate/**` is **denied today** (rc=2, measured), a folder is not a mechanical check, and the allowlist + separability test is falsifiable where a folder is not. | **Rejected on mechanism, not on cost** |
| **A8** | **Keep both deliverables in one change** (`scope.md`'s original framing) | The two tracks shared **zero content** and exactly **one** 7,480-line file that both panels flagged as the run's top mechanical hazard. | **Rejected — and already executed:** the harden shipped first and alone (§0.1). This is why the DAG has one baton instead of a four-way serialize |

---

## 10. Tiebreak verdicts, recorded with rationale

| # | Question | Verdict | Rationale (why the loser lost) |
|---|---|---|---|
| **T0** | How many agents? | **ZERO** (R2) | Confirmed by G4b on **corrected** reasoning. The panels used `CLAUDE.md:11`, scoped to plugin-specific architects/reviewers. Under the actual carve-out (`:22`/`:24`) the split is **not clean** and fails **inverted**: core holds the deeper, dated, sourced hygiene body, where both admitted precedents had core holding the thin half. Plus: the candidate agent is a narrower slice of `process-analyst`'s body (dispatch ambiguity + rubric drift), and the unowned residue is a **security-review lane** that even `memory-engineering` refused to fork. **Encode the rationale, not just the number — the wrong rationale is what a future PR would use to "fix" this.** |
| **T1** | Honesty enforcement — release greps or CI gates? | **B — permanent numbered CI gates with must-fail halves** | A's checks run **once, at release**, protecting only the PR that introduces them — the exact defect A itself cites as the reason `lss_calc.py` needed a gate. A did not apply its own standard to its own honesty checks. A's greps were **additionally broken**: they searched for phrases absent from A's own mandated sentence, and the Turnstile probe required two strings on one **physical line**. Both would report green while measuring nothing. |
| **T2** | The (a)-discipline artifact — runnable or prose? | **A — ship `form_metrics.py`, round-tripping into `lss_calc.py imr`** | B ships prose only. This matters **more** because the forms↔SPC join has **no literature**: a claim with no prior art must be mechanically testable. The round-trip either produces valid control limits or it does not. |
| **T3** | DAG shape | **B — parallel tracks with a named merge step** | A claimed Phase 8 could "start immediately after Phase 0" and then imposed a total order (`218→219→30→220`) over `audit-gates.sh` that blocked Phase 8's own edits — a direct self-contradiction. B is internally consistent but pushes the pain late. **Reconciled:** content parallelism is B's; the *file edit* is serialized by the gate-file baton (§2.3), which is A's ordering applied only where it is actually needed. |
| **T4** | Boundary with `web-design` | **A's direction, B's caution** | Reciprocal priors are **necessary** for a zero-agent plugin to be reachable — B named its own rot pattern and accepted it. But A's nine-file Phase 9 is more blast radius than the mechanism needs. **Ruled: five files, one inline prior each, ≤3 lines, frontmatter untouched** (R5). `scope.md`'s "out of scope" line is **amended** by owner authorization (§0.2) — a framing defect the panels should never have been left to interpret. |
| **T5** | Zero-agent live precedent | **A** — `report-regeneration` and `team-portfolio` ship with **no `agents/`**, re-verified twice | B reached the same conclusion by reasoning alone without checking whether the shape was proven in this marketplace. Absorbed as fact. |
| **T6** | Concrete gate numbers | **A's method, B's numbers void** | A measured the ceiling (217) and committed to numbers; B used "a new gate" placeholders throughout. **Both are now superseded** by the shipped harden: the ceiling is **218**, so this plan starts at **219**. |
| **T7** | Anti-rot for substrate content | **B** — re-verification commands, including the inside-the-block-not-the-comment requirement | A ships static `src/…:line` assertions that rot silently the moment RavenPower-Website binds the R2 bucket. A has no equivalent mechanism. |
| **T8** | Pre-build baseline + hard read-first STOP gate | **A** | B has neither. Without a recorded baseline every later "gates pass" claim is unfalsifiable; without a blocking read-first gate a plan can execute to completion on an unverified premise. Both adopted in P0. |
| **T9** | `## Decision Tree:` heading trap | **A** | B was silent. A named the specific catastrophic-failure precedent. Adopted as a P2 pre-build gate with `render-trees.py --check` unchanged as the test. |
| **T10** | `process-improvement` semver (0.3.0 vs 0.2.3) | **A — 0.3.0** | Moot and already resolved: the shipped harden used **0.3.0** (verified in both `plugin.json` and the `marketplace.json` mirror). A's reading matched the actual change size (new constants table, a file delete needing a migration note, new gate coverage). |
| **T11** | Copilot-regen obligation | **A** | A verified `process-improvement` has no `copilot/` directory (only `ravenclaude-core` does) and concluded the obligation does not apply — citing the check rather than assuming. B never mentioned it. Same check applies to `forms-engineering`: it ships **no `copilot/`**, so no regen is owed. **Verify, do not assume** (§13). |

---

## 11. Rulings I made myself (no tiebreak covered these)

**No dangling conflict is left. Where two inputs disagreed and no tiebreak covered it, I ruled.**

### 11.1 `turnstile-spin` is NOT a routing target — RULED

Plan B's Phase 3 routing table sends Turnstile widget-wiring to the `turnstile-spin` skill. Verified
this session: `ls -d plugins/*/skills/turnstile-spin` → **no matches**;
`ls -d ~/.claude/skills/turnstile-spin` → **exists**. It is a separately-installed local skill bundle,
**outside the marketplace**, available to this owner and to nobody else who installs
`forms-engineering`.

**Ruling:** it must not appear as a routing target in shipped content. Turnstile mechanics route to
`plugins/ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md` (owned, dated, sourced,
`refresh_when:`-triggered). `turnstile-spin` may be mentioned **once**, in the substrate skill only, as
an *optional local convenience that is not part of this marketplace*. Enforced by P3's `plugins/`-scoped
`test -e` resolver loop, which would fail on it.

### 11.2 Discipline (d) ships as knowledge + template, not as a skill — RULED

Both panels made platform selection a skill. Under R6 (skill count is the real recurring cost) a
seven-axis checklist with no branch logic does not earn always-on frontmatter. It ships as
`knowledge/form-platform-evaluation.md` + `templates/form-platform-evaluation-matrix.md`, referenced
from `form-intake-and-triage-design`. **Trigger to promote:** the axes acquire a scoring procedure with
branch logic, or exceed one knowledge section.

### 11.3 The Turnstile WCAG conflict caveat is NOT written into `ravenclaude-core` — RULED

The critic observed that `cloudflare-who-gets-in.md` is arguably the right home for the conformance
caveat, and that Gate 221 sub-check B (scoped to `plugins/forms-engineering/`) therefore cannot protect
it. True — but editing a core **knowledge concept** is materially more than the reciprocal-prior
authorization covers, and core's own `refresh_when:` clause is the mechanism by which that file stays
current.

**Ruling:** the caveat ships in `forms-engineering/knowledge/form-anti-abuse.md` as the named conflict,
**and** P8's prior into `ravenclaude-core/agents/security-reviewer.md` names it. A separate,
owner-routed change may later move it into the concept doc. **This is recorded as a known gap, not
silently accepted:** a future PR stating "Turnstile is WCAG 2.2 AA" inside `ravenclaude-core` would not
be caught by Gate 221.

### 11.4 The three honesty checks share ONE gate number — RULED

B proposed three separate gates. Each new number costs three registration sites (§5.4) and one more
chance at a Gate 195 parity failure, for no added signal — the three checks share a corpus and a
fixture harness. **One script, one number (221), three sub-checks, all run and aggregated (never
short-circuit on the first failure), each with its own must-fail fixture.**

### 11.5 The hook does not detect rules owned elsewhere — RULED

Plan A's hook detected placeholder-as-only-label, `*` on required fields, and `type="text"` on
email/tel — all owned by `web-design` (rows 1, 87; `ux-designer.md:74`). A second enforcement home for
someone else's rule is rubric drift wearing a hook's clothes. **Detections are scoped strictly to rules
this plugin owns** (P6).

### 11.6 Discipline (b) is one best-practice file, not a skill — RULED (see R4)

Both panels shipped a (b) skill. Given §0.3 (web-design owns form UX and form a11y deeply) the only
absent content is five criteria. Five criteria are a rule file, not a skill.

---

## 12. `[unverified]` claims and the step that will settle each

Every marker below ships **inline in the file**, with its reason clause. Chat-spoken caveats do not
count. Five premise trips stand from G3b; three are **ACCEPTED-unsettled as direction-of-error safe**.

| Claim | Marker that ships | Cited by | The step that settles it |
|---|---|---|---|
| **104** — time-trap anti-abuse unvalidated for a fast/autofilling user | `[unverified — premise not disconfirmed: shipped hedged; a settling experiment is named]` | P2 (`form-anti-abuse.md`), P4 rule #2's sibling text | The named experiment: instrument a real form with a time-trap threshold and measure the false-positive rate against autofill/password-manager sessions. **If wrong, we shipped a hedge — nothing is built on it.** |
| **105** — platform pricing goes stale within a quarter | `[unverified — volatile, verify at use]` | P2 (`form-platform-evaluation.md`), P5 | Never publish pricing; **Gate 221 sub-check C** makes it mechanical. If the premise is false the plan is merely over-cautious. |
| **36** — both `process-improvement` agents are genuine specialist craft | *(no marker ships)* | **no phase** | **Inert here.** The PI track split out (§0.1); no phase in this plan acts on it. Recorded so its absence is deliberate. |
| **101** — no literature joins form telemetry to SPC/DMAIC | the verbatim NOVEL SYNTHESIS marker (§6.1), which states its own method bound | P2, P3, P5 | A paywalled-venue search (ACM DL / IEEE Xplore / Scopus), which the open-web method did not cover. Until then the negative is **bounded by method and is not proof of universal absence** — and the artifact says so. |
| **96** — Cloudflare contradicts itself on Turnstile's WCAG level | the named-conflict paragraph (§6.2) | P2, P6 | A **VPAT** from Cloudflare, or a documentation correction on one of the two pages. Until then no surface states either level unqualified. |
| **61** — Resend sending domain unverified ⇒ no customer email delivers | `[unverified — carried from memory, not re-probed]` | P7 | Re-probe: `wrangler pages secret list` for `RESEND_API_KEY` + the Resend dashboard's domain status. **The founder-alerts-work / customer-email-fails split IS the sandbox-sender signature.** |
| **49** — whether `TURNSTILE_SECRET` is set in live production | `[unverified — code branch verified, live posture not probed]` | P7 | `wrangler pages secret list --env production`. The rule generalizes correctly regardless; only the live-posture sentence is gated on it. |
| **55** — no generic double-submit/idempotency on plain form POSTs (inference, medium confidence) | `[unverified — inference from route reading, not an exhaustive sweep]` | P4 rule #3, P7 | A route-by-route sweep of `src/pages/api/**` keyed on **behaviour** (does the handler dedupe?), not on the presence of the word "idempotent". |
| **Rows 24–27, 34** — gate numbers/behaviour read from source, never executed | *(resolved before any content ships)* | P0 | **P0 acceptance 4** converts them from inference to fact by running the suite end to end and recording the result. |
| **Row 33** — the two `web-design` agent files never read | **SETTLED** | — | Read in full at G3b; result is §0.3, which **narrowed the scope**. Claim 31 is partially falsified; the ruling survived, the boundaries changed. |
| **Row 32** — CAPTCHA/Turnstile/honeypot/upload "confirmed unowned" | **PARTIALLY FALSE** | — | Settled and corrected: the unowned set shrinks to **{honeypot, form abandonment, multi-step-as-pattern}**. See §0.4. |
| **Rows 21, 31** | **SETTLED** | — | See `settlements.md`. Row 21: no `.repo-layout.json` edit needed (bidirectional probe with two negative controls). |

---

## 13. Definition of done

The plan is done when **all** of the following hold, each **executed**, not asserted:

**Versioning and registration**
1. `plugins/forms-engineering/.claude-plugin/plugin.json` version is `0.1.0`, and its
   `.claude-plugin/marketplace.json` mirror carries the **identical** version string (CI fails on drift).
2. `.claude-plugin/marketplace.json` `len(plugins)` is **182** (181 measured before this change).
3. `plugins/forms-engineering/CHANGELOG.md` has a dated `0.1.0` entry naming what shipped.
4. `python3 scripts/check-description-count-literals.py` → clean (Gate 206): **no artifact-count
   literal** in either description mirror.
5. `python3 scripts/check-marketplace-claims.py` → PASS: the three required files present, no drifted
   count claim, and a plugin with **no `agents/` directory** accepted.
6. **Copilot regen:** `ls plugins/forms-engineering/copilot` → absent, therefore
   `generate-copilot-plugin.py` is **not** owed. *Verify with the `ls`; do not assume.*

**Formatting and links**
7. `npx --yes prettier@3.9.4 --write . && npx --yes prettier@3.9.4 --check .` → exit 0, **whole tree**
   (a single mis-formatted file anywhere blocks this).
8. ⛔ **G6-REPAIR (M1) — the literal command here was BROKEN on this host and is replaced:**

   ```sh
   python3 -m pip install --quiet --user ruff
   python3 -m ruff check .        # exit 0, whole tree
   ```

   *(**Bare `pip` is absent on stock macOS** — use `python3 -m pip`. And **bare `ruff` is not on PATH**:
   `--user` installs to `~/Library/Python/3.9/bin`, which stock macOS does not export, so the old
   `&& ruff check .` half exits **127 even after a successful install**. Measured both ways this
   session: `ruff check .` → **rc 127**; `python3 -m ruff check .` → **rc 0**. To make Gate 9b itself
   run rather than skip — it gates on `command -v ruff` at `audit-gates.sh:1610` — prepend that
   directory to PATH for the suite run, as in P0 acc.6.)*
9. `python3 scripts/check-md-links.py` → clean. The inherited-rules table's ~7 cross-plugin relative
   links are the most likely failure point. ⛔ Run the **script**, not `--check 29` (unregistered; see
   DoD #11), and remember it does **not** validate anchor fragments (`check-md-links.py:19-20`) — the
   §5.5 anchor-text assertion is what covers that.

**Gates**
10. `bash scripts/audit-gates.sh` end-to-end → **green**, diffed against the P0 baseline. *A failure
    present in the baseline is not ours; a failure absent from it is.*
    ⛔ **G6-REPAIR (M1) — AND `grep -c 'SKIPPED' <suite output>` → 0. A SKIP IS NOT A PASS.** The
    suite's exit code does not carry the skip: measured `815 pass, 0 fail, 1 skipped` → **exit 0**.
    Nothing else in this plan reads it. Verified bidirectional: **2** with `ruff` absent, **0** with
    `ruff` on PATH (`817 pass, 0 fail, 0 skipped`). The attribution rule in this item does **not**
    license shipping a baseline skip — a skipped gate was never run against our diff either, and the
    three new Python files this plan ships are exactly what Gate 9b would have linted.
11. `bash scripts/audit-gates.sh --check N` → exit 0 for **N ∈ {219, 220, 221, 206}**.
    ⛔ **G6-REPAIR (H2) — `30`, `18` and `29` are DELETED from this set. Do not re-add them.** They are
    **not registered for per-gate runs**: none has a dispatcher case arm and none is in the
    `Supported:` string at `audit-gates.sh:1149`. Measured — `--check 30`, `--check 18` and `--check 29`
    each exit **1** with *"gate 'N' is not registered for per-gate runs"* on a **clean, fully green
    tree**. They are RED unconditionally and therefore assert nothing. Gate 30 is a full-suite block
    only (`audit-gates.sh:3584`); Gate 18 is at `:2201`; Gate 29 at `:3520`.
    **Their replacements, each directly runnable with its exit code as the gate:**
    - Gate 29 → `python3 scripts/check-md-links.py` (verified exit 0)
    - Gate 18 → `python3 scripts/check-frontmatter.py` (verified exit 0)
    - Gate 30 → the **full suite** plus the named-assertion flip proof in P6 — never a per-gate exit code
12. ⛔ **Proof each new gate RUNS IN THE FULL SUITE.** For each of 219, 220, 221:
    - grep the **full-suite output** for the gate's own **script name on an executed line**
      (`check-forms-substrate-separation.py`, `check-form-metrics.py`, `check-forms-honesty-markers.py`)
      — **not** for the string `"Gate <N>"`. A batched `── Gates 120–125 ──` header once made a
      by-number grep return 0 for **seven gates that all ran**;
    - and confirm `--check <N>` exits 0 while `--check <N>` against its must-fail fixture exits
      non-zero. *A gate nothing invokes reports green while measuring nothing.*
13. `python3 scripts/check-gate-registration.py` **and** `--self-test` → both exit 0 (Gate 195:
    reachability, number-uniqueness, dispatcher/`Supported:` parity). Each new number appears in **all
    three** registration sites (§5.4).
14. **Every must-fail half proven:** Gate 219 ×**4** sub-checks (A, B, C, **D**) **plus** the paraphrase
    fixture and the `.sh`-scope must-pass fixture; Gate 221 ×3 sub-checks **plus** the
    negative-instruction fixture that must **not** trip **plus** rule #5's must-pass fixture; Gate 220's
    wrong-expected-value proof **and** its stream-contract halves (marker-to-stdout build makes (i) and
    (iii) RED); and the Gate 30 pair's **hook-mutation** proof.
    ⛔ **G6-REPAIR (H2) — the Gate 30 mutation proof is RE-SPECIFIED. The old form passed vacuously.**
    It keyed on `--check 30`'s exit code, which is **non-zero unconditionally** (unregistered) — before
    the mutation, after it, and on a tree with no forms hook at all. The operator would mutate, see
    non-zero, conclude the pair had teeth, revert, and ship an untested fixture pair: **the probe and
    the subject failing the same way.** The proof now keys on the **named assertion line that flipped**
    in the **full-suite** output:
    `✓ forms anti-patterns (fires on anti-pattern)` = 1 on a clean tree, and
    `✗ forms anti-patterns (fires on anti-pattern)` = 1 after mutating the hook to always-silent.
    Executed against the existing `process-improvement` hook this session to prove the mechanism
    distinguishes pass from fail before it was written here (P6 carries the measured table). Note the
    `(silent on clean)` half reads `✓` in **both** states — which is why the suite exit code alone is
    insufficient.
15. `bash scripts/audit-gates.sh` is still invoked by `.github/workflows/validate-marketplace.yml`
    with **no `paths:` filter** — one grep, confirmed at release.

**Design invariants, re-run on the final tree**
16. **Separability:** the tree with the two allowlisted substrate files removed passes the **full**
    suite.
17. **Reachability:** every one of the four skills is named by ≥1 file outside
    `plugins/forms-engineering/`, verified by a resolver loop — **and the resolver is positive-controlled**
    (a deliberately misspelled name makes it report a failure).
18. **Routing:** every path named in any `## Not this skill` / routing block resolves under `plugins/`
    by `test -e`. `turnstile-spin` appears **at most once**, in the substrate skill, flagged as
    non-marketplace.
19. **No duplication:** the six constitution-owned phrases appear in the new tree **only on link lines**.
20. **No tree obligation:** `python3 scripts/render-trees.py --check` → PASS **unchanged**.
21. **Layout:** the `git diff --diff-filter=A main` fnmatch sweep from `AGENTS.md` → "Layout OK".
    `.repo-layout.json` is **unmodified**.
22. `bash -n` + executable-bit check clean on every new/touched `.sh`.
23. **Scope wall:** `git diff --name-only origin/main` contains **zero** paths outside
    `plugins/forms-engineering/`, `scripts/`, **`tests/fixtures/**`**, `.claude-plugin/marketplace.json`,
    and the **five** enumerated reciprocal-prior files. Any further file is a scope breach.
    *(G6-REPAIR, L2: `tests/fixtures/**` was missing and P1's own file list puts the Gate 219/221
    fixtures there — this item flagged the plan's own build as a breach. It is an allowed glob in
    `.repo-layout.json` and already holds `bad-marketplace.json`/`bad-plugin.json`, so the layout hook
    permitted exactly what this wall forbade.)*
24. **Local install test** (`AGENTS.md` step 6): marketplace add + plugin install in a scratch project;
    `/design-form-intake` appears in autocomplete and **zero agents** appear for the plugin — proving
    the zero-agent design **shipped**, not merely was planned.

---

## 14. What this plan does NOT build

- **No agents** (R2), in either plugin.
- **No `process-improvement` work of any kind** — shipped separately (§0.1). No domain expansion into
  BPM / process mining / TOC / ISO-9001; that was ruled out and remains so.
- **No restatement of `ravenclaude-core/rules/security.md` §File handling or of
  `cloudflare-who-gets-in.md`** (§0.4). Cite and extend. Enforced by Gate 219.
- **No restatement of `web-design`'s existing form rules** (rows 1–3, 6) — linked in the
  inherited-rules table. Duplication is how a single source of truth dies.
- **No client-side form implementation or form-a11y craft** — `frontend-implementer` and
  `accessibility-auditor` own those by measurement (§0.3).
- **No re-implementation of control charts.** `lss_calc.py` exists, is verified correct (row 38), and
  is now gated (Gate 218). `form_metrics.py` **feeds** it.
- **No inferential statistics** — route to `applied-statistics` (row 42 confirms the seam is live).
- **No `## Decision Tree:` sections.** Tables are sanctioned and sufficient.
- **No vendor pricing or feature matrix** — stale within a quarter (row 105); Gate 221 sub-check C.
- **No `substrate/` directory** and **no `.repo-layout.json` edit** (R3, A7).
- **No changes to `RavenPower-Website`.** Rows 58/61/64/65 are documented gaps, not tasks.
- **No survey-design content** — `ux-research` owns surveys; a transactional form is a different object.
- **No Power Pages / Dataverse form content** — row 10: a routing target, not a seam.
- **No legal/compliance ruling.** PII content is practice-level only; any GDPR/CCPA/PIPA determination
  routes to `data-governance-privacy` + the owner.
- **No new CI workflow file.** Every new gate goes inside the existing `scripts/audit-gates.sh`,
  invoked by the existing `validate-marketplace.yml`. **Never add a `paths:` filter to a required
  workflow.**
- **No `turnstile-spin` routing target** (§11.1).
- **No magic-byte sniffing library.** The plugin documents; consumers implement.

---

## 15. G6-REPAIR log (post-G5 red team) — what changed in this file and nothing else

G5 returned **FAIL with 4 unmitigated HIGH findings**. This pass repaired `plan.md` **in place**. The
structure, the 10 phases, the DAG, the tracks, the baton, the scope and every §10 tiebreak and §11
ruling are **unchanged**. No decision was re-opened. Every change below is a repair to a **broken
acceptance test** or a correction of a **measured-false premise**.

| Ref | Change | Sections touched |
|---|---|---|
| **H1** | Unsatisfiable `grep -c "35–50%"` STOP sentinel → **bidirectional pair** (structure probe + positive control), both halves measured flipping between refs; **#959-CLOSED branch** added | §2.1, P0 acc.2, P8 pre-build, R2, §8 |
| **H2** | All ~10 uses of unregistered `--check 30 / 18 / 29` removed → direct scripts; **P6's vacuous teeth proof re-specified** onto the flipped named assertion line in the full-suite output | P2, P3, P4, P6, P8, DoD #11, DoD #14, §8 |
| **H3** | Non-executing round-trip → **binding stream contract** (numbers-only stdout, marker on stderr, `--values "$(…)"`), Gate 220 grows to 3 assertions, **minimum n = 20** named | P5, §5.2, §6.1, §8 |
| **H4** | Paraphrase blind spot → **new sub-check D** (positive resolving-link requirement) + paraphrase fixture + script-header limitation + **§0.4's false "not by author discipline" claim amended** + named human read in P4 | §0.4, §5.1, P1, P4, §8 |
| **M1** | ruff skip → hard STOP with a working invocation; `grep -c 'SKIPPED'` → 0; *a skip is not a pass* | P0 acc.4/acc.6, DoD #8, DoD #10, R14, §8 |
| **M2** | Enablement-blind reachability probe → prints `enabledPlugins` state; the dark-telemetry-seam limitation **explicitly waived**; R6 raised to Med | P8, R6, §8 |
| **M3** | Gate 219 file-type scope (`**/*.md` only) decided in P1; `single-use` → co-occurrence; `.sh` must-pass fixture | §5.1, P1, R4, §8 |
| **M4** | §6.1 surface list 3 → 5; the **printing** assertion moved to Gate 220 (which executes) | §5.3, §6.1, §5.2, R5, §8 |
| **M5** | `path:line` rot → **§5.5** cite-by-anchor-text + a Gate 219 anchor assertion | §5.5 (new), P4, DoD, §8 |
| **L1 / L2** | rerere-off integration + post-integration re-assertions; `tests/fixtures/**` added to the scope wall | P8, DoD #23, §8 |
| **Corrections** | **#959 and #960 do NOT conflict** (both `CLEAN`, hunks 140 lines apart, order immaterial); **no gate-number race** (2 open PRs, ceiling 217, #960 takes 218, new gates start at 219) | §2.1, R2 |

⛔ **Every replacement mechanism in this table was EXECUTED and shown to distinguish pass from fail
before it was written into the plan.** The one that could not be executed is named as such: Gate 219/220/221's
must-fail fixtures cannot be run because **the scripts do not exist yet** — H4/M3/M4 are read off the
**specification**, and the fixture *designs* were proven against stand-in fixtures instead (the
paraphrase table in §5.1, the mock round-trip in §5.2, the `.sh` scope sweep in §5.1). The Gate 30
mechanism was proven on the **existing** `process-improvement` hook, which shares the identical
`assert_hook_fires`/`assert_hook_silent` contract.

---

---RESULT_START---
{"gate":"G6","superseded_by":"G6-repair","status":"pass","artifact":"/Users/matthewcorbett/RavenClaude/.ravenclaude/runs/forge/forms-process-expertise/plan.md","bytes":0,"digest":["10 phases (P0-P9), forms plugin only — every process-improvement build phase deleted (shipped via PR #960); 4 skills / 3 knowledge / 7 rules / 0 agents","New gates 219 (substrate+cite-don't-restate separation), 220 (form_metrics.py + lss_calc.py I-MR round-trip), 221 (3 honesty sub-checks), plus 2 assertions on existing Gate 30 — 218 is taken","Critical path P0-P1-P2-P3-P4-P7-P8-P9 with a gate-file baton (219+221 -> 220 -> Gate 30); hard STOP gates on PR #959 and #960 both being merged first, verified unmerged this session","Ruled myself: turnstile-spin is NOT a routing target (lives outside plugins/, unavailable to consumers); discipline (d) is knowledge+template not a skill; discipline (b) is one WCAG-2.2-delta rule file not a skill; 3 honesty checks share one gate number; hook detects only rules this plugin owns; Turnstile WCAG caveat stays out of core (recorded as a known gap)","CE-1 is an acceptance test not a note: Gate 219 sub-checks B+C forbid restating security.md:43-45 and cloudflare-who-gets-in.md:51,53 anywhere outside a link line — 3 planned best-practice files deleted as a result"],"blockers":[],"confidence":0.86}
---RESULT_END---

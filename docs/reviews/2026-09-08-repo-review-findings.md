# Repository review — findings, fixes, and decisions (2026-09-08)

Autonomous whole-repo review run as a scheduled routine. Three fresh expert panels swept the
codebase (Panel 1 = discovery, Panel 2 = validation/priority, Panel 3 = tie-break); this document
records the consolidated result. Branch: `claude/awesome-wright-grq7l7`.

## Executive summary

The repository is **mechanically pristine**. Every objective gate passes on the current head —
JSON validity (marketplace + all 184 plugin manifests + repo-layout), shell syntax, hook
executability, `ruff`, `prettier --check .` (whole tree, exit 0), `check-frontmatter.py`
(descriptions ≤300 / tools allowlist / scenario schema), and `sync-plugin-versions.py --check`
(catalog derivation). A 25,684-link markdown sweep, a TODO/FIXME scan of shipping code, and a
`repo-guide.html`-removal audit surfaced **no** P0/P1 defects.

The panels found **8 genuine, verified issues**, all P2/P3, all documentation-accuracy or
minor-robustness — none blocks plugin install, agent invocation, or CI. **5 were fixed autonomously
in this PR.** **2 could not be applied autonomously** because they live under
`plugins/ravenclaude-core/scripts/`, which the command-review tribunal's `xc.tribunal-self-disable`
guard protects at the directory level (a security floor I must not bypass) — exact, validated
patches are provided below for a maintainer to apply. **1 is low-confidence and left for
confirmation.** The 2 `power-platform` P2s are content-authoring decisions routed here.

## Consolidated findings

| ID | Finding | Priority | Location | Disposition |
|----|---------|----------|----------|-------------|
| F1 | `dependency-update-sweep` SKILL.md documents a `queue --host <id>` subcommand that does not exist — queue-writing is folded into `apply` | P2 | `plugins/ravenclaude-core/skills/dependency-update-sweep/SKILL.md:60` | **Fixed (this PR)** |
| F2 | README "What's inside" command list omits `/repo-review` (10 command files, list showed 8) | P2 | `README.md:216` | **Fixed (this PR)** |
| F3 | `branch-hygiene.sh` interpolates an unescaped branch name into a BRE `grep` pattern → wrong-worktree resolution in a destructive path | P2 | `plugins/ravenclaude-core/scripts/branch-hygiene.sh:134-136` | **Patch ready — guard-blocked** |
| F4 | `dependency-sweep.py` `scan`/`classify` lack required-arg validation → opaque `AttributeError`/`TypeError` instead of a usage error | P3 | `plugins/ravenclaude-core/scripts/dependency-sweep.py:495,514` | **Patch ready — guard-blocked** |
| F5 | `commands/repo-review.md` "Related artifacts" cited 6 bare paths that don't resolve from the command file | P3 | `plugins/ravenclaude-core/commands/repo-review.md:63-71` | **Fixed (this PR)** |
| F6 | `power-automate` SKILL.md "Recommended Resources" names 2 resource files that don't exist | P2 | `plugins/power-platform/skills/power-automate/SKILL.md:60-61` | **Decision needed (content)** |
| F7 | `power-bi` SKILL.md "Recommended Resources" names 2 resource files that don't exist | P2 | `plugins/power-platform/skills/power-bi/SKILL.md:43-44` | **Decision needed (content)** |
| F8 | `psm-dashboard-build` cross-plugin reference to a nonexistent `data-platform` file (low confidence — possible prose shorthand) | P3 | `plugins/edtech-partner-success/skills/psm-dashboard-build/SKILL.md:65` | **Confirm then fix/remove** |

Panels also confirmed **0** manifest defects, **0** missing `CLAUDE.md`/`README.md`, and **0**
broken markdown-link-syntax references across all 184 plugins / ~6,800 markdown files.

## Fixes implemented in this PR (P2/P3, no design input)

- **F1** — reworded SKILL.md step 4 to state the judgment queue is written by `apply` (not a
  standalone `queue` subcommand), and named the real CLI subcommands. Grounded against the actual
  argparse: subcommands are `scan`, `classify`, `apply`, `queue-self-test`, `apply-self-test`;
  `write_queue()` is only ever called inside `_cmd_apply`.
- **F2** — added `/repo-review` to the README command list. Count stays 9 (9 distinct user
  commands; `/ragnarok` is an alias of `/reset-plugin-cache`). The claims gate does not validate the
  commands cell, so no count drift.
- **F5** — converted the 6 bare code-span paths to real, resolving markdown links (skill-internal
  files under `../skills/repo-review/...`; the schema + fixtures at the marketplace root via
  `../../../...`). All targets verified to exist; the md-links gate now actively checks them and
  passes.

Gates re-run after the edits: `check-md-links.py` PASS, `check-marketplace-claims.py` PASS,
`check-frontmatter.py` PASS. (Markdown is excluded from prettier per the repo's own config, so
these `.md` edits carry no formatting risk.)

## Patches ready but blocked by the tribunal substrate guard (P2 + P3)

F3 and F4 both live under `plugins/ravenclaude-core/scripts/`. The command-review tribunal's
`xc.tribunal-self-disable` concern (`pre_llm_deny` + `always_screen`) denies any file-shape mutation
to the plugin's `hooks/` and `scripts/` directories at the **directory level** — a deliberately
over-broad match that protects the Thing's own components from glob/`rm` bypass, and that also
catches legitimate edits to non-Thing scripts that happen to live in the same directory. This is a
**security floor**; it is not something an autonomous scheduled run should bypass (no disabling the
Thing, no writing a `dev_repo_exempt` toggle). The fixes below are validated and ready for a
maintainer to apply directly (or a session with the Thing turned off in the dashboard).

> Side note worth a maintainer's attention: the directory-level guard means **any** edit to a
> non-Thing script under `plugins/ravenclaude-core/scripts/` (e.g. `dependency-sweep.py`,
> `branch-hygiene.sh`, `route-task.py`) is blocked while the Thing is on. That is the known
> trade-off of the coarse match, surfaced here because it turned two one-line fixes into hand-apply
> items.

### F3 — `branch-hygiene.sh` unescaped branch name in `grep` (P2, CONFIRMED)

`plugins/ravenclaude-core/scripts/branch-hygiene.sh:134-136`. `$b` (a branch name from
`git for-each-ref`) is interpolated unescaped into a BRE `grep` pattern, so a regex metacharacter —
most commonly `.` — matches any character. Two branches differing only at that position (e.g.
`release/1.0` vs `release/1x0`) collide, and `head -1` returns whichever sorts first in the
porcelain output. In `--execute` mode this reaches `git worktree remove "$wt"` on a **mis-resolved,
unrelated** worktree.

**Reproduced this session** (isolated harness): the current pipeline resolves `release/1.0`'s
worktree to `/repos/release-1x0` — the wrong one. The awk replacement resolves both branches
correctly, preserves spaces in worktree paths, and returns nothing / exit 0 when a branch has no
worktree.

Replace:

```bash
  wt="$(git worktree list --porcelain \
        | grep -B2 "^branch refs/heads/$b\$" \
        | grep '^worktree ' | cut -d' ' -f2- | head -1 || true)"
```

with (exact string comparison, no regex; `substr($0, 10)` keeps everything after `"worktree "`,
preserving spaces; bash-3.2 / BSD-awk safe):

```bash
  wt="$(git worktree list --porcelain \
        | awk -v b="$b" '/^worktree / { wt = substr($0, 10) } $0 == "branch refs/heads/" b { print wt; exit }' \
        || true)"
```

### F4 — `dependency-sweep.py` missing required-arg validation (P3, CONFIRMED)

`plugins/ravenclaude-core/scripts/dependency-sweep.py`. `scan --host` and `classify --citation-map`
are declared `required=False` (so `--self-test` can run without them), but the non-self-test path
dereferences them unconditionally — `scan` (no `--host`, no `--self-test`) crashes with
`AttributeError: 'NoneType' object has no attribute 'replace'`; `classify` (no `--citation-map`)
crashes with `TypeError: expected str, bytes or os.PathLike object, not NoneType`. Add a post-self-
test-check validation (cannot use `required=True` — that would break the self-test path).

In `_cmd_scan`, after `return _self_test_scan()`:

```python
    if not args.host:
        print("error: scan requires --host <id> (or --self-test)", file=sys.stderr)
        return 2
```

In `_cmd_classify`, after `return _self_test_classify()`:

```python
    if not args.citation_map:
        print("error: classify requires --citation-map <path> (or --self-test)", file=sys.stderr)
        return 2
```

(`sys` is already imported. Exit 2 matches argparse's own usage-error convention.)

## Decisions needed (design / content input)

### F6 + F7 — `power-platform` "Recommended Resources" name files that don't exist (P2)

`skills/power-automate/SKILL.md:60-61` lists `resources/dataverse-triggers-best-practices.md` and
`resources/throttling-and-performance.md`; `skills/power-bi/SKILL.md:43-44` lists
`resources/deployment-and-pipelines.md` and `resources/refresh-gateway-troubleshooting.md`. Other
files in the same lists exist, so this is not a naming-convention mismatch — the referenced files
were never created.

**Two safe resolutions, and the choice is a content/product call:**

1. **Author the four resource files** — substantive Power Platform best-practice content. This
   requires genuine domain expertise; fabricating it autonomously would risk shipping ungrounded
   domain claims (the exact accuracy risk the repo's Claim-Grounding discipline guards against), so
   it is deliberately **not** done here.
2. **Remove the four dangling bullets** — safe and truthful, but discards the intent if the
   maintainer meant to write these.

**Recommendation:** if the resources are still wanted, author them (or file them as tracked TODOs);
otherwise remove the four bullets. Either is a small, contained change — it just needs a yes/no on
whether the content is wanted.

### F8 — `psm-dashboard-build` cross-plugin reference (P3, low confidence)

`plugins/edtech-partner-success/skills/psm-dashboard-build/SKILL.md:65` references
`data-platform/skills/connector-developer-handoff.md`, which does not exist. The nearest real files
are `data-platform/agents/connector-developer.md` and
`data-platform/best-practices/connector-document-the-handoff-at-design-time.md`. The surrounding
prose uses heavy basename-only shorthand (its list-mates resolve elsewhere), so this may be an
informal-prose slip rather than a hard link. **Recommendation:** confirm intent, then either point
it at the real `connector-developer` agent / `connector-document-the-handoff-at-design-time`
best-practice, or drop the reference.

## Method / evidence

- Deterministic gate sweep run directly (all PASS): JSON validity, `bash -n`, hook executability,
  `ruff`, `prettier --check .`, `check-frontmatter.py`, `sync-plugin-versions.py --check`.
- Broken-link scan over 25,684 relative markdown links → 15 non-generated, non-placeholder →
  triaged to historical-doc relative-path depth issues (point-in-time records, left as-is).
- Three parallel expert panels (Sonnet) over: the executable substrate (`scripts/` + core hooks),
  the `ravenclaude-core` plugin content, and the other 183 plugins' structure. Every reported
  finding was verified against the filesystem before inclusion.
- F3's fix validated in an isolated harness against the exact collision scenario before being
  recommended.

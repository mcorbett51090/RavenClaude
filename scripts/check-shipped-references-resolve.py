#!/usr/bin/env python3
"""check-shipped-references-resolve.py — CI gate (FORGE github-gold-standard P2).

Closes the *class* of the P1 defect: a file that SHIPS inside the plugin
(anything under plugins/ravenclaude-core/** that a consumer receives on
`/plugin install`) points at a script/hook by a path the consumer cannot
resolve, because the target does not ship inside the plugin.

The P1 instance: guard-destructive.sh (a shipped hook) hard-blocks branch
force-delete and routes the agent to a recovery escape hatch that lived only
at the marketplace-root `scripts/` and never shipped — so a consumer hit the
block with no working exit. The constitution's "Still open, stated precisely"
section records the same class open for premise-gate.py / classify_claim.py,
cited repo-relative in forge-pipeline/SKILL.md.

Three checks, all keyed on the same invariant — "does
plugins/ravenclaude-core/(scripts|hooks)/<basename> exist?":

  A. ${CLAUDE_PLUGIN_ROOT}/(scripts|hooks)/<name>  — the syntax explicitly
     promises the target ships in the plugin; a missing target is an
     unambiguous bug in ANY shipped file. Scanned everywhere.

  B. markdown links whose relative target RESOLVES UNDER
     plugins/ravenclaude-core/(scripts|hooks)/  — assert the exact file
     exists (catches a typo'd in-plugin link). Scanned everywhere. Links
     that resolve OUTSIDE the plugin (to the marketplace root) are NOT
     extracted here — those are the many legitimate `../../scripts/...`
     references to marketplace-dev tooling in the plugin's own CLAUDE.md /
     CHANGELOG.md, and flagging them would red-fail every PR.

  C. THE P1-CLASS CHECK — bare marketplace-root references (NOT
     ${CLAUDE_PLUGIN_ROOT}-prefixed) in OPERATIONAL surfaces the consumer's
     agent acts on (rules / skills / commands / agents / templates): a
     command invocation `bash scripts/x.sh` / `python3 scripts/x.py`, or a
     markdown link/anchor naming `(scripts|hooks)/x`. Violation iff the
     plugin does not carry <basename> AND <basename> is not on the
     dev-tooling / deferred ignore-list. If the plugin DOES carry it the
     reference is resolvable in-plugin and fine.

Design bias (per the task tiebreak): PREFER FALSE-NEGATIVES. When a
reference is ambiguous, do not flag — a false positive that red-fails every
PR is worse than a missed edge case. Operational-surface scoping keeps
Check C off the marketplace-meta docs (CLAUDE.md / CHANGELOG.md / knowledge /
concepts.json / copilot/) that legitimately describe root-level dev tooling.

Exit codes: 0 clean, 1 violations found, 2 cannot-run (LOUD fail).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

PLUGIN_REL = os.path.join("plugins", "ravenclaude-core")
KINDS = ("scripts", "hooks")
TEXT_EXT = (".md", ".sh", ".json", ".yaml", ".yml")

# Operational surfaces: files a consumer's AGENT reads and ACTS on. The P1
# escape-hatch bug and the forge still-open cases both live here. The
# marketplace-meta docs (CLAUDE.md / CHANGELOG.md / README.md / knowledge /
# concepts.json / copilot/) are deliberately excluded from Check C: they
# describe the marketplace's OWN dev/CI loop and cite root-level tooling by
# design, so a bare `scripts/...` there is not a consumer escape hatch.
OPERATIONAL_DIRS = ("rules", "skills", "commands", "agents", "templates")

# ── Ignore-list (basename) — intentional references that legitimately do NOT
#    ship inside the plugin. Two documented groups. ────────────────────────────
#
# GROUP 1 — marketplace-internal dev / CI / regen tooling. Lives at the
# marketplace-root scripts/ BY DESIGN (wired into CI, the regen loop, or the
# release checklist) and is cited in shipped skill/agent docs that describe
# MARKETPLACE-MAINTENANCE workflows. A consumer never runs these in their own
# repo, so a bare reference is intentional, not the P1 bug.
_MARKETPLACE_DEV_TOOLING = {
    "audit-gates.sh",            # the CI gate meta-test (this very suite)
    "open-dashboard.sh",         # opens the marketplace clone's dashboard
    "generate-dashboards.py",    # regenerates dashboard.html
    "generate-index-dashboard.py",  # regenerates the portal index.html
    "generate-copilot-plugin.py",   # regenerates the Copilot package
    "review-ledger.py",          # the code-review reopen-ledger CLI
}
# GROUP 2 — deliberately deferred packaging move. See
# plugins/ravenclaude-core/CLAUDE.md § "Still open, stated precisely":
# premise-gate.py / classify_claim.py live at the marketplace root and are
# cited repo-relative in forge-pipeline/SKILL.md; the move into the plugin (or
# repoint to ${CLAUDE_PLUGIN_ROOT}) is deferred because it spans ~6 call sites.
# REMOVE these two entries when that move lands — the gate then keeps them honest.
_DEFERRED_PACKAGING = {
    "premise-gate.py",
    "classify_claim.py",
}
IGNORED_BASENAMES = _MARKETPLACE_DEV_TOOLING | _DEFERRED_PACKAGING

# Consumer-repo conventional paths that legitimately never ship (documented per
# the task). The extractors below only surface (scripts|hooks) references, so
# these do not normally arise; kept here so a future broadening has a home.
CONSUMER_CONVENTIONAL_PATHS = {
    "docs/pm/raid-log.md",
    ".repo-layout.json",
    "AGENTS.md",
    "CLAUDE.md",
}

# ── Extractors ───────────────────────────────────────────────────────────────
# Form A: an explicit plugin-root reference. Always a promise of in-plugin.
_RE_CPR = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/(scripts|hooks)/([A-Za-z0-9._-]+)")
# Markdown link: [anchor](target)
_RE_MDLINK = re.compile(r"\[(?P<anchor>[^\]]*)\]\((?P<target>[^)\s]+)\)")
# A (scripts|hooks)/name.(sh|py) path token anywhere in a string.
_RE_PATHTOKEN = re.compile(r"(scripts|hooks)/([A-Za-z0-9._-]+\.(?:sh|py))")
# Command invocation of a BARE marketplace-root path (optional quote / ./),
# NOT ${CLAUDE_PLUGIN_ROOT}- or plugins/-prefixed. The negative-lookbehind on
# the runner keeps it from matching mid-token.
_RE_CMD = re.compile(
    r"(?<![\w./-])(?:bash|sh|source|python3|python)\s+['\"]?(?:\./)?"
    r"(scripts|hooks)/([A-Za-z0-9._-]+\.(?:sh|py))"
)
_RE_DOTSLASH = re.compile(
    r"(?<![\w])\./(scripts|hooks)/([A-Za-z0-9._-]+\.(?:sh|py))"
)


class Violation:
    __slots__ = ("relpath", "line", "kind", "name", "check", "detail")

    def __init__(self, relpath, line, kind, name, check, detail):
        self.relpath = relpath
        self.line = line
        self.kind = kind
        self.name = name
        self.check = check
        self.detail = detail

    def key(self):
        return (self.relpath, self.line, self.kind, self.name, self.check)


def _plugin_has(repo_root, kind, name):
    return os.path.isfile(os.path.join(repo_root, PLUGIN_REL, kind, name))


def _is_operational(rel_within_plugin):
    top = rel_within_plugin.replace("\\", "/").split("/", 1)[0]
    return top in OPERATIONAL_DIRS


def _iter_text_files(plugin_abs):
    for dirpath, _dirnames, filenames in os.walk(plugin_abs):
        for fn in filenames:
            if fn.endswith(TEXT_EXT):
                yield os.path.join(dirpath, fn)


def scan(repo_root):
    """Return (violations, files_scanned, refs_checked). Raises on unreadable tree."""
    plugin_abs = os.path.join(repo_root, PLUGIN_REL)
    if not os.path.isdir(plugin_abs):
        raise RuntimeError(
            "plugin directory not found: %s" % os.path.join(PLUGIN_REL)
        )

    violations = {}
    files_scanned = 0
    refs_checked = 0

    def add(v):
        violations[v.key()] = v

    for path in _iter_text_files(plugin_abs):
        rel_repo = os.path.relpath(path, repo_root)
        rel_plugin = os.path.relpath(path, plugin_abs)
        fdir = os.path.dirname(path)
        operational = _is_operational(rel_plugin)
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except (OSError, UnicodeDecodeError):
            # A file we cannot read is not a silent pass — surface it loudly.
            raise RuntimeError("unreadable shipped file: %s" % rel_repo)
        files_scanned += 1

        for lineno, line in enumerate(lines, 1):
            stripped = line.strip()
            is_comment = stripped.startswith("#")
            is_example = "# example" in line.lower()

            # ── Check A: ${CLAUDE_PLUGIN_ROOT}/(scripts|hooks)/name (any file)
            for kind, name in _RE_CPR.findall(line):
                refs_checked += 1
                if not _plugin_has(repo_root, kind, name):
                    add(
                        Violation(
                            rel_repo,
                            lineno,
                            kind,
                            name,
                            "A:plugin-root",
                            "${CLAUDE_PLUGIN_ROOT}/%s/%s promises an in-plugin "
                            "file that does not ship" % (kind, name),
                        )
                    )

            # ── Check B: markdown links resolving UNDER the plugin (any file)
            for m in _RE_MDLINK.finditer(line):
                target = m.group("target")
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                if "${" in target:
                    continue
                if not _RE_PATHTOKEN.search(target):
                    continue
                resolved = os.path.normpath(os.path.join(fdir, target))
                for kind in KINDS:
                    base = os.path.join(plugin_abs, kind) + os.sep
                    if resolved.startswith(base):
                        name = os.path.basename(resolved)
                        refs_checked += 1
                        if not os.path.isfile(resolved):
                            add(
                                Violation(
                                    rel_repo,
                                    lineno,
                                    kind,
                                    name,
                                    "B:in-plugin-link",
                                    "markdown link resolves to a missing "
                                    "in-plugin file: %s" % target,
                                )
                            )
                        break

            # ── Check C: the P1-class check — OPERATIONAL surfaces only ────────
            if not operational or is_comment or is_example:
                continue

            candidates = []  # (kind, name)

            # (i) bare command invocation of a marketplace-root path
            for kind, name in _RE_CMD.findall(line):
                candidates.append((kind, name))
            for kind, name in _RE_DOTSLASH.findall(line):
                candidates.append((kind, name))

            # (ii) markdown link/anchor naming a (scripts|hooks) file. Take the
            #      basename; a shipped operational surface must only point at
            #      scripts/hooks the plugin actually carries.
            for m in _RE_MDLINK.finditer(line):
                anchor = m.group("anchor")
                target = m.group("target")
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    hay = anchor
                else:
                    hay = anchor + " " + target
                for kind, name in _RE_PATHTOKEN.findall(hay):
                    candidates.append((kind, name))

            for kind, name in candidates:
                refs_checked += 1
                if name in IGNORED_BASENAMES:
                    continue
                if _plugin_has(repo_root, kind, name):
                    continue
                add(
                    Violation(
                        rel_repo,
                        lineno,
                        kind,
                        name,
                        "C:p1-class",
                        "operational surface references marketplace-root "
                        "%s/%s, which does not ship in the plugin (a consumer "
                        "cannot resolve it)" % (kind, name),
                    )
                )

    return list(violations.values()), files_scanned, refs_checked


def _run(repo_root):
    try:
        violations, files_scanned, refs_checked = scan(repo_root)
    except RuntimeError as exc:
        print("THIS IS NOT A PASS: checker could not run — %s" % exc, file=sys.stderr)
        return 2

    if violations:
        violations.sort(key=lambda v: (v.relpath, v.line, v.name))
        print(
            "check-shipped-references-resolve: %d violation(s) "
            "(scanned %d files, %d references):"
            % (len(violations), files_scanned, refs_checked),
            file=sys.stderr,
        )
        for v in violations:
            print(
                "  %s:%d [%s] %s" % (v.relpath, v.line, v.check, v.detail),
                file=sys.stderr,
            )
        print(
            "\nFix: ship the target inside plugins/ravenclaude-core/%s/, cite it "
            "as ${CLAUDE_PLUGIN_ROOT}/%s/<name>, or (if it is intentional "
            "marketplace-dev tooling) add its basename to IGNORED_BASENAMES "
            "with a one-line rationale." % ("{scripts,hooks}", "{scripts,hooks}"),
            file=sys.stderr,
        )
        return 1

    print(
        "check-shipped-references-resolve: OK — %d shipped files, %d "
        "script/hook references all resolve." % (files_scanned, refs_checked)
    )
    return 0


# ── Self-test ────────────────────────────────────────────────────────────────
def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _self_test():
    """Plant a synthetic tree with a known-bad reference of each class and
    assert it is caught, plus a known-good tree that passes."""
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        pdir = os.path.join(tmp, PLUGIN_REL)
        # A shipped script the good references point at.
        _write(os.path.join(pdir, "scripts", "exists.sh"), "echo hi\n")
        _write(os.path.join(pdir, "hooks", "exists-hook.sh"), "echo hi\n")

        # GOOD file: every form resolves.
        _write(
            os.path.join(pdir, "rules", "good.md"),
            "Run it: [`${CLAUDE_PLUGIN_ROOT}/scripts/exists.sh`](../scripts/exists.sh)\n"
            "`bash ${CLAUDE_PLUGIN_ROOT}/scripts/exists.sh`\n"
            "Or `bash scripts/exists.sh` (plugin carries it, so resolvable).\n"
            "Dev tooling is fine: `bash scripts/audit-gates.sh` (ignore-listed).\n"
            "Hook: [`hooks/exists-hook.sh`](../hooks/exists-hook.sh)\n",
        )
        v_good, _, _ = scan(tmp)
        if v_good:
            print("SELF-TEST FAIL: good tree produced violations: %s"
                  % [(x.relpath, x.name, x.check) for x in v_good], file=sys.stderr)
            ok = False

        # BAD: Check A — ${CLAUDE_PLUGIN_ROOT} points at a non-shipping file.
        _write(
            os.path.join(pdir, "rules", "bad_cpr.md"),
            "`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/missing_a.py` never ships.\n",
        )
        # BAD: Check B — in-plugin markdown link to a missing file.
        _write(
            os.path.join(pdir, "skills", "s", "bad_link.md"),
            "See [x](../../scripts/missing_b.sh) — resolves under plugin, absent.\n",
        )
        # BAD: Check C (command) — bare marketplace-root invocation, not shipped.
        _write(
            os.path.join(pdir, "rules", "bad_cmd.md"),
            "The sanctioned exit is `bash scripts/not_shipped_hatch.sh --reason x`.\n",
        )
        # BAD: Check C (markdown anchor/target escaping to root), not shipped.
        _write(
            os.path.join(pdir, "commands", "bad_anchor.md"),
            "Route to [`scripts/gone.sh`](../../../scripts/gone.sh) for recovery.\n",
        )

        v_all, _, _ = scan(tmp)
        got = {(v.name, v.check.split(":")[0]) for v in v_all}
        expected = {
            ("missing_a.py", "A"),
            ("missing_b.sh", "B"),
            ("not_shipped_hatch.sh", "C"),
            ("gone.sh", "C"),
        }
        for want in expected:
            if want not in got:
                print("SELF-TEST FAIL: planted bad reference not caught: %s "
                      "(got %s)" % (str(want), sorted(got)), file=sys.stderr)
                ok = False

        # And the good file's references must NOT appear among violations even
        # in the mixed tree.
        for v in v_all:
            if v.relpath.endswith("good.md"):
                print("SELF-TEST FAIL: good reference flagged: %s %s"
                      % (v.relpath, v.name), file=sys.stderr)
                ok = False

    if ok:
        print("self-test OK: each planted bad reference (A/B/C) caught; "
              "good references pass; ignore-list honored.")
        return 0
    print("THIS IS NOT A PASS: self-test failed.", file=sys.stderr)
    return 1


def _find_repo_root(explicit):
    if explicit:
        return os.path.abspath(explicit)
    cwd = os.getcwd()
    cur = cwd
    while True:
        if os.path.isdir(os.path.join(cur, PLUGIN_REL)):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    # Fallback: repo root is the parent of this script's scripts/ dir.
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true",
                    help="plant synthetic bad+good references and assert detection")
    ap.add_argument("--root", default=None,
                    help="repo root (default: auto-detect from cwd)")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    repo_root = _find_repo_root(args.root)
    return _run(repo_root)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""thing-decision.py — the routing brain of the command-review tribunal ("the Thing").

Given a shell command, this answers three questions the orchestrator hook
(`thing-orchestrator.sh`, the "Lawspeaker") needs before it spends an LLM call:

  1. Which comfort-posture category does the command belong to? (reuses the
     EMISSIONS table in apply-comfort-posture.py — the ONE source of truth, so
     category matching never drifts from the permission translator).
  2. Is command review toggled ON for that category? (reads the per-category
     `thing:` field in .ravenclaude/comfort-posture.yaml — written by the
     dashboard's Command-review toggle).
  3. What seat config applies? (reads the optional .ravenclaude/thing.yaml;
     falls back to built-in defaults when absent).

It prints ONE JSON object to stdout and always exits 0 (so the bash orchestrator
can `jq` the result without worrying about exit codes). A malformed thing.yaml
is reported via a `config_error` field — the orchestrator fails closed (ask) on
that, never a silent skip.

T2 scope: single category supported end-to-end (`shell_readonly`), single seat.
Classification covers all categories so T3+ only flips toggles, no code change.

Usage:
    thing-decision.py --root <project-dir> classify "<command string>"
"""

from __future__ import annotations

import argparse
import hashlib

# ── Reuse the EMISSIONS table from apply-comfort-posture.py (single source of
#    truth for category ⇄ command-pattern mapping). Same importlib trick the
#    dashboard generator uses, so the two never drift. ────────────────────────
import importlib.util
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_APPLY = _HERE / "apply-comfort-posture.py"


def _load_emissions() -> dict[str, list[str]]:
    spec = importlib.util.spec_from_file_location("_apply_comfort_posture", _APPLY)
    if spec is None or spec.loader is None:
        return {}
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return dict(getattr(mod, "EMISSIONS", {}))


_CONCERNS = _HERE / "thing-concerns.py"


def _route(command: str, category: str | None) -> dict:
    """Deterministic seat routing + pre-LLM screen, via thing-concerns.py.

    Returns the routing subset {concerns, max_severity, pre_llm_deny,
    deny_concern, convened_seats}. On any failure to load/evaluate, returns a
    conservative fallback that convenes the full panel (never silently empties
    the routing) so the orchestrator still reviews the command.
    """
    fallback = {
        "concerns": [],
        "max_severity": None,
        "pre_llm_deny": False,
        "deny_concern": None,
        "convened_seats": ["forseti", "mimir", "heimdall"],
        "high_blast": False,
    }
    try:
        spec = importlib.util.spec_from_file_location("_thing_concerns", _CONCERNS)
        if spec is None or spec.loader is None:
            return fallback
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        catalog = mod._load_catalog()
        res = mod.evaluate(catalog, command, category)
        return {k: res[k] for k in fallback}
    except Exception:
        return fallback


def _screen_always(command: str) -> dict:
    """Category-independent self-disable screen (§B.9.5), via thing-concerns.py.

    Runs regardless of the per-category toggle: a command that would disable or
    tamper with the Thing is denied pre-LLM whenever the orchestrator reached us
    (i.e. some category is toggled on), even if THIS command's own category is
    off.

    Fail direction (hardened after the 2026-07 three-panel review): this screen
    enforces the two category-independent invariants the constitution calls
    UNCONDITIONAL — "the Thing cannot disable itself" and the force-push / `curl|sh`
    hard rules. If the catalog can't be loaded/evaluated (corrupt YAML, missing
    PyYAML, a future schema change), the screen MUST fail CLOSED, not silently
    clear the command: the prior no-deny fallback let any error disable both
    invariants for as long as it persisted (verified reproducible by corrupting
    concerns-catalog.md). We therefore DENY both on error, and surface a
    `screen_error` flag the orchestrator can log/distinguish. The documented
    maintainer escape hatch (`command_review.enabled: false`) remains the way to
    edit the substrate itself while a catalog is mid-edit.
    """
    ok_fallback = {
        "self_disable_deny": False,
        "self_disable_concern": None,
        "hard_rule_deny": False,
        "hard_rule_concern": None,
        "screen_error": False,
    }
    fail_closed = {
        "self_disable_deny": True,
        "self_disable_concern": "internal-error-fail-closed",
        "hard_rule_deny": True,
        "hard_rule_concern": "internal-error-fail-closed",
        "screen_error": True,
    }
    try:
        spec = importlib.util.spec_from_file_location("_thing_concerns", _CONCERNS)
        if spec is None or spec.loader is None:
            return fail_closed
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        catalog = mod._load_catalog()
        res = mod.screen_always(catalog, command)
        return {k: res.get(k, ok_fallback[k]) for k in ok_fallback}
    except Exception:
        return fail_closed


_BASH_PATTERN_RE = re.compile(r"^Bash\((.+?)(:\*)?\)$")


def _command_prefixes() -> list[tuple[str, str, bool]]:
    """Flatten EMISSIONS into (category, prefix, is_wildcard) for Bash patterns.

    `Bash(ls:*)`      -> ("shell_readonly", "ls", True)   # command starts with "ls"
    `Bash(pwd)`       -> ("shell_readonly", "pwd", False) # command IS exactly "pwd"
    """
    out: list[tuple[str, str, bool]] = []
    for category, patterns in _load_emissions().items():
        for pat in patterns:
            m = _BASH_PATTERN_RE.match(pat)
            if not m:
                continue  # non-Bash pattern (Read/Edit/WebFetch/...) — irrelevant here
            prefix = m.group(1).strip()
            is_wildcard = m.group(2) is not None
            out.append((category, prefix, is_wildcard))
    return out


# git global options that precede the subcommand. A `git <globals> <subcmd>`
# must normalize to `git <subcmd>` so a force-push / branch -D hidden behind
# `--git-dir=`, `-C`, etc. is still classified (and screened) correctly.
# MUST stay identical to `_GIT_GLOBAL_OPT` in thing-concerns.py — the Gate 21
# git-global FN corpus (audit-gates.sh) fails if either copy drifts.
_GIT_GLOBAL_OPT = (
    r"-[cC]\s+\S+"
    r"|--(?:git-dir|work-tree|namespace|super-prefix)(?:=\S+|\s+\S+)"
    r"|--exec-path(?:=\S+)?"
    r"|--no-pager|--paginate|-p"
    r"|--bare|--literal-pathspecs|--no-replace-objects|--no-optional-locks|--no-advice"
)


def _normalize_lead(lead: str) -> str:
    """Strip wrappers that would let a command dodge EMISSIONS prefix matching.

    Closes the classification holes from the tribunal assessment (§should-fix #8):
    leading env-var assignments (`LS_COLORS=x ls`), `sudo`/`env` prefixes,
    absolute interpreter paths (`/usr/bin/python3` -> `python3`), and `git`
    global options (`git --git-dir=/x push` -> `git push`). Conservative + idempotent.
    """
    prev = None
    while lead and lead != prev:
        prev = lead
        # leading VAR=value assignments (one or more)
        lead = re.sub(r"^[A-Za-z_][A-Za-z0-9_]*=\S*\s+", "", lead)
        # sudo / env wrappers (with any of their own flags before the real cmd)
        lead = re.sub(r"^(?:sudo|env|command|nohup|nice|stdbuf)\b(?:\s+-\S+)*\s+", "", lead)
        lead = re.sub(r"^(?:sudo|env)\s+[A-Za-z_][A-Za-z0-9_]*=\S*\s+", "", lead)
    # absolute / relative path on the first token -> basename (/usr/bin/python3 -> python3)
    m = re.match(r"^(\S*/)?(\S+)(.*)$", lead, re.S)
    if m and m.group(1):
        lead = m.group(2) + m.group(3)
    # git global options: `git --git-dir=/x -C dir push` -> `git push`
    if lead.startswith("git "):
        rest = lead[4:]
        rest = re.sub(r"^(?:\s*(?:" + _GIT_GLOBAL_OPT + r"))+\s*", "", rest)
        lead = "git " + rest.lstrip()
    return lead.strip()


def classify(command: str) -> str | None:
    """Return the comfort-posture category for a Bash command, or None.

    Longest matching prefix wins (so `git status` beats a bare `git`). A
    wildcard prefix matches when the command equals it or is followed by a
    space; an exact prefix (no `:*`) matches only an exact command. The match
    is on the leading segment of the command so a pipe/chain classifies by its
    first command (`ls | grep x` -> shell_readonly).
    """
    cmd = command.strip()
    if not cmd:
        return None
    # Leading segment only — split on the first shell separator so `ls | grep`
    # classifies as its first command. Keep it conservative (T2 is low-stakes).
    lead = re.split(r"\s*(?:\||\|\||&&|;)\s*", cmd, maxsplit=1)[0].strip()
    lead = _normalize_lead(lead)

    best_cat: str | None = None
    best_len = -1
    for category, prefix, is_wildcard in _command_prefixes():
        if is_wildcard:
            matched = lead == prefix or lead.startswith(prefix + " ")
        else:
            matched = lead == prefix
        if matched and len(prefix) > best_len:
            best_cat, best_len = category, len(prefix)
    # Flag-aware tribunal override (routing only — does NOT touch the permission
    # EMISSIONS table). EMISSIONS lumps every `git branch` form into
    # shell_readonly, but a FORCE delete (`-D`, or `--delete` together with
    # `--force`) is a destructive local mutation, not a read. Match `-D`
    # case-sensitively so `-d` — the safe merged-only delete — is NOT re-routed.
    # Without this, slm.delete-protected-branch-locally is unreachable: the
    # command auto-allows as a "read" before its concern can ever fire.
    if best_cat == "shell_readonly" and re.match(r"git\s+branch\b", lead):
        # `-D` matched case-sensitively (so safe `-d` is excluded) but allowing
        # other flag letters around it (`-Dr`, `-rD`, `-vD`); or `--delete` +
        # `--force` in any order.
        force_delete = re.search(r"(?:^|\s)-[A-Za-z]*D[A-Za-z]*\b", lead) or (
            re.search(r"(?:^|\s)--delete\b", lead) and re.search(r"(?:^|\s)--force\b", lead)
        )
        if force_delete:
            best_cat = "shell_local_mutate"
    # Flag-aware network-write override (routing only — does NOT touch EMISSIONS,
    # same pattern as the git branch -D override above). The EMISSIONS prefixes
    # catch explicit `curl -X POST` / `gh api POST`, but curl/wget also write via
    # data/upload flags (implicit POST) and `=`-attached method flags the space-
    # delimited prefix matcher can't see — those fall through to network_read
    # (curl/wget:*) or None and would auto-allow as a "read" before a write concern
    # can fire. A curl/wget/gh command carrying a write signal is network_write.
    if best_cat in ("network_read", None) and re.match(r"(?:curl|wget|gh)\b", lead):
        has_method = re.search(
            r"(?:^|\s)(?:-X|--request|--method)[=\s]+(?:POST|PUT|PATCH|DELETE)\b", lead, re.I
        )
        curl_body = re.match(r"curl\b", lead) and re.search(
            r"(?:^|\s)(?:-[dFT]\b|--(?:data(?:-ascii|-binary|-raw|-urlencode)?|form|upload-file)\b)",
            lead,
        )
        wget_body = re.match(r"wget\b", lead) and re.search(
            r"(?:^|\s)--(?:post-data|post-file|body-data|body-file)\b", lead
        )
        # `gh api` performs an IMPLICIT POST whenever a field/input flag is present
        # with no explicit -X/--method (`gh api repos/o/r/issues -f title=x` creates
        # an issue). Without this branch bare `gh api` isn't in any EMISSIONS prefix,
        # so best_cat is None and the write auto-allows unreviewed. -f/--raw-field,
        # -F/--field, --input all force the write; explicit -X POST is already caught
        # by has_method above (so a bare `gh api <path>` GET stays a read).
        gh_body = re.match(r"gh\s+api\b", lead) and re.search(
            r"(?:^|\s)(?:-f|-F|--field|--raw-field|--input)\b", lead
        )
        if has_method or curl_body or wget_body or gh_body:
            best_cat = "network_write"
    return best_cat


# ── Payload classification (Track B Engine Foundation §1) ─────────────────────
# Bash classifies by the EMISSIONS command-prefix table (classify, above). Every
# OTHER reviewed tool shape (file Edit/Write/MultiEdit/Read, network
# WebFetch/WebSearch, MCP) is NAME-keyed here — mcp_tools EMISSIONS is empty and
# the file/network patterns are path/URL-shaped, not command prefixes. Bump
# CLASSIFY_PAYLOAD_VERSION by hand whenever this logic changes; it folds into
# config_hash so a cached verdict is invalidated when classification changes.
CLASSIFY_PAYLOAD_VERSION = "1"

# MCP verb read/write split (locked decision 4): a fixed read-verb prefix set;
# everything else is a write at an escalated tier. Shipped now so the version is
# stable across phases (the allowlist + concern triggers land in Phase 4).
_MCP_READ_VERB_PREFIXES = ("get_", "list_", "read_", "search_", "describe_", "fetch_")

# Track B §Payload caps: the local screen scans up to SCREEN_MAX_BYTES of reviewed
# text IN FULL. A larger payload DENIES for a toggled category (cannot fully screen
# → fail closed) — it is never truncate-then-screened.
SCREEN_MAX_BYTES = 1024 * 1024


def _path_scope(raw_path: str, project_root: Path) -> str:
    """'project' or 'global' for a file-shape target (§4). Resolves stricter:
    ANY ambiguity (empty, lexical `..`, leading `~`, unresolvable, or a realpath
    outside the project) returns 'global' — mis-classification may only bump the
    tier, never skip the screen."""
    if not raw_path:
        return "global"
    norm = unicodedata.normalize("NFC", raw_path)
    if norm.startswith("~") or ".." in norm.replace("\\", "/").split("/"):
        return "global"  # lexical traversal / home → stricter tier
    try:
        p = Path(norm)
        if not p.is_absolute():
            p = project_root / p
        rp = unicodedata.normalize("NFC", os.path.realpath(str(p)))
        root_rp = unicodedata.normalize("NFC", os.path.realpath(str(project_root)))
        if os.path.normcase(rp) == os.path.normcase(root_rp):
            return "project"
        try:
            common = os.path.commonpath([os.path.normcase(rp), os.path.normcase(root_rp)])
        except ValueError:
            return "global"  # different drives / mixed abs+rel
        return "project" if common == os.path.normcase(root_rp) else "global"
    except (OSError, ValueError):
        return "global"


def mcp_verb_is_read(tool_name: str) -> bool:
    """True if an mcp__server__verb tool name's verb starts with a read-verb
    prefix. Unknown / non-prefixed verbs are writes (escalated), per decision 4."""
    parts = tool_name.split("__", 2)
    verb = parts[2] if len(parts) >= 3 else ""
    return verb.startswith(_MCP_READ_VERB_PREFIXES)


def mcp_server_name(tool_name: str) -> str:
    """The server segment of an `mcp__server__verb` tool name (between the first
    and second `__`), or '' if not an mcp tool. `mcp__github__create_issue` →
    'github'; a bare `mcp__slack` → 'slack'."""
    if not tool_name.startswith("mcp__"):
        return ""
    return tool_name[len("mcp__") :].split("__", 1)[0]


def classify_payload(tool_name: str, tool_input: dict, project_root: Path) -> str | None:
    """Comfort-posture category for ANY reviewed tool shape, or None. Bash
    delegates to classify(); the rest are name-keyed (§1)."""
    ti = tool_input or {}
    if not tool_name:
        return None
    if tool_name == "Bash":
        return classify(ti.get("command", "") or "")
    if tool_name in ("Edit", "Write", "MultiEdit"):
        scope = _path_scope(ti.get("file_path", "") or "", project_root)
        return "file_edit_project" if scope == "project" else "file_edit_global"
    if tool_name == "Read":
        scope = _path_scope(ti.get("file_path", "") or "", project_root)
        return "file_read_project" if scope == "project" else "file_read_global"
    if tool_name in ("WebFetch", "WebSearch"):
        return "network_read"
    if tool_name.startswith("mcp__"):
        return "mcp_tools"
    return None


def reviewed_text(tool_name: str, tool_input: dict) -> str:
    """The text a non-Bash payload is SCREENED against (§3). Per locked decisions:
    WebFetch reviews the URL only (not the prompt); MCP reviews canonical-json
    args; file shapes review path + content/diff."""
    ti = tool_input or {}
    if tool_name == "Bash":
        return ti.get("command", "") or ""
    if tool_name == "Write":
        return f"{ti.get('file_path', '')}\n{ti.get('content', '')}"
    if tool_name == "Edit":
        return f"{ti.get('file_path', '')}\n{ti.get('old_string', '')}\n{ti.get('new_string', '')}"
    if tool_name == "MultiEdit":
        edits = ti.get("edits") or []
        parts = [str(ti.get("file_path", ""))]
        for e in edits:
            if isinstance(e, dict):
                parts.append(f"{e.get('old_string', '')}\n{e.get('new_string', '')}")
        return "\n".join(parts)
    if tool_name == "Read":
        return ti.get("file_path", "") or ""
    if tool_name == "WebFetch":
        return ti.get("url", "") or ""  # URL only (decision 4)
    if tool_name == "WebSearch":
        return ti.get("query", "") or ""
    if tool_name.startswith("mcp__"):
        args = ti.get("arguments", ti)
        try:
            return tool_name + "\n" + json.dumps(args, sort_keys=True, default=str)
        except (TypeError, ValueError):
            return tool_name
    return ti.get("command", "") or ""


# ── Per-shape serialization (Track B §Serialization) ──────────────────────────
def saga_tool_input(tool_name: str, tool_input: dict) -> dict:
    """The `tool_input` recorded in the Sága audit log — per shape, and NEVER the
    full content (a content hash + byte count instead)."""
    ti = tool_input or {}
    if tool_name in ("Edit", "Write", "MultiEdit"):
        content = reviewed_text(tool_name, ti)
        b = content.encode("utf-8", "replace")
        return {
            "file_path": ti.get("file_path", "") or "",
            "content_sha256": hashlib.sha256(b).hexdigest(),
            "bytes": len(b),
        }
    if tool_name in ("WebFetch", "WebSearch"):
        return {"url": ti.get("url", "") or ti.get("query", "") or ""}
    if tool_name.startswith("mcp__"):
        try:
            args = json.dumps(ti.get("arguments", ti), sort_keys=True, default=str)
        except (TypeError, ValueError):
            args = ""
        return {
            "name": tool_name,
            "args_sha256": hashlib.sha256(args.encode("utf-8", "replace")).hexdigest(),
        }
    return {"command": ti.get("command", "") or ""}


def cache_identity(tool_name: str, tool_input: dict, project_root: Path) -> str:
    """The per-shape identity in the verdict-cache key (file = realpath + content
    hash; network = URL; MCP = name + args hash; Bash = the command string)."""
    ti = tool_input or {}
    if tool_name in ("Edit", "Write", "MultiEdit"):
        try:
            rp = os.path.realpath(str(project_root / (ti.get("file_path", "") or "")))
        except (OSError, ValueError):
            rp = ti.get("file_path", "") or ""
        return (
            rp
            + "|"
            + hashlib.sha256(reviewed_text(tool_name, ti).encode("utf-8", "replace")).hexdigest()
        )
    if tool_name in ("WebFetch", "WebSearch"):
        return ti.get("url", "") or ti.get("query", "") or ""
    if tool_name.startswith("mcp__"):
        try:
            args = json.dumps(ti.get("arguments", ti), sort_keys=True, default=str)
        except (TypeError, ValueError):
            args = ""
        return tool_name + "|" + hashlib.sha256(args.encode("utf-8", "replace")).hexdigest()
    return ti.get("command", "") or ""


# ── File-shape self-disable: screen_substrate_path (Track B §2/§2a/§4) ────────
# The Bash self-disable guard (xc.tribunal-self-disable) is command-shaped — it
# matches `rm/tee/sed … <substrate path>`. A FILE-shape mutation (a Write/Edit
# tool whose TARGET is a substrate file) has no shell verb, so it dodges that
# regex. screen_substrate_path is the catalog-INDEPENDENT (stdlib-only) path
# check that closes it: it never loads the concern catalog (so no catalog-load
# except-branch), and denies if the canonicalized target is — or is under — any
# substrate path, by lexical path, realpath, OR st_ino (the inode check closes a
# hardlink to a substrate file). SINGLE SOURCE for the runtime substrate set.
# Scoped to ravenclaude-core specifically — the Thing IS ravenclaude-core, so its
# runtime substrate lives only under plugins/ravenclaude-core/. A bare `plugins/*`
# wildcard also matched every SIBLING plugin's hooks/scripts dir, so in any repo
# shaped like a plugin monorepo (this repo, or any consumer with a top-level
# plugins/<name>/hooks|scripts layout) a Write/Edit to an unrelated plugin's files
# was pre-LLM denied with xc.tribunal-self-disable — a false positive. In a normal
# consumer repo the plugin lives in the ~/.claude cache (not the project tree), so
# these globs correctly match nothing there.
THING_SUBSTRATE = [
    "plugins/ravenclaude-core/hooks",  # dir — any write under the plugin hooks
    "plugins/ravenclaude-core/scripts",  # dir — thing-*, apply-comfort-posture, serve-dashboards, …
    "plugins/ravenclaude-core/knowledge/concerns-catalog.md",
    "scripts/generate-dashboards.py",
    ".ravenclaude/thing.yaml",
]


def _substrate_paths(project_root: Path) -> tuple[set[str], set[tuple[int, int]]]:
    """Concrete substrate realpaths (normcased) + their (dev, ino) under the
    project root. CI tooling (audit-gates.sh, fixtures) is intentionally OUT of
    scope — editing a CI gate cannot disable the runtime hook (§2a)."""
    rps: set[str] = set()
    inodes: set[tuple[int, int]] = set()
    for pat in THING_SUBSTRATE:
        for p in project_root.glob(pat):
            try:
                rps.add(os.path.normcase(os.path.realpath(str(p))))
            except OSError:
                continue
            # Inode set: the matched path itself PLUS, if it is a directory, every
            # file under it — so a hardlink to ANY substrate file (e.g. a hardlink
            # to plugins/*/hooks/thing-orchestrator.sh) is caught (§4 step 5).
            targets = [p] + ([f for f in p.rglob("*") if f.is_file()] if p.is_dir() else [])
            for t in targets:
                try:
                    st = os.stat(str(t))
                    inodes.add((st.st_dev, st.st_ino))
                except OSError:
                    continue
    return rps, inodes


# ── Maintainer-substrate exemption (dev-repo only) ──────────────────────────
# Suppresses the self-disable DENY for marketplace-substrate paths when ALL
# three signals hold: (a) opt-in flag in posture, (b) gh-authenticated repo
# identity == mcorbett51090/RavenClaude, (c) marketplace.json exists + has
# name "ravenclaude". FAIL-SAFE OFF: any error/missing gh/no auth/network
# failure/mismatch → False (enforce). Never weakens the hard-rule floor.


def _gh_owner(root: Path) -> str | None:
    """Return the gh-authenticated repo's 'owner/repo' string, or None on any error.

    Calls `gh repo view --json nameWithOwner -q .nameWithOwner` from `root`.
    This is the ONLY signal used for repo identity — NOT a marker file, path
    string, or remote URL the session could forge. Wrapped in try/except so
    any failure (missing gh, no auth, network, non-zero exit) returns None.

    Designed to be thin so tests can stub it: pass an injected owner via
    `_maintainer_substrate_exempt(root, posture, _resolved_owner=<stub>)`.

    Defense-in-depth residual: this function trusts the `gh` binary resolved
    on PATH and assumes an uncompromised maintainer environment. A compromised
    PATH (e.g. a malicious `gh` wrapper that echoes the expected owner) could
    spoof the identity check. The exemption is therefore a dev-time convenience
    only — never enabled in consumer repos (dev_repo_exempt is opt-in and False
    by default). No mitigation exists at this layer for a fully compromised host.
    """
    import subprocess  # stdlib only — no new dependency

    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(root),
        )
        if result.returncode != 0:
            return None
        owner = result.stdout.strip()
        return owner if owner else None
    except Exception:
        return None


_EXEMPT_REPO = "mcorbett51090/RavenClaude"


def _marketplace_json_valid(root: Path) -> bool:
    """True iff <root>/.claude-plugin/marketplace.json exists and parses with name 'ravenclaude'."""
    mp = root / ".claude-plugin" / "marketplace.json"
    if not mp.is_file():
        return False
    try:
        import json as _json

        doc = _json.loads(mp.read_text(encoding="utf-8"))
        return isinstance(doc, dict) and doc.get("name") == "ravenclaude"
    except Exception:
        return False


_OWNER_NOT_INJECTED = object()  # sentinel: "use live gh", distinguishable from None (gh failed)


def _maintainer_substrate_exempt(
    root: Path,
    posture: dict,
    *,
    _resolved_owner: object = _OWNER_NOT_INJECTED,
) -> tuple[bool, str | None]:
    """Return (exempt, resolved_owner_or_None).

    True ONLY when ALL hold:
      (a) posture's command_review.dev_repo_exempt is strictly True (opt-in),
      (b) gh-authenticated repo identity == mcorbett51090/RavenClaude,
      (c) <root>/.claude-plugin/marketplace.json exists + parses with name 'ravenclaude'.

    _resolved_owner: test injection point. Supply a string to skip the live gh call.
    Supply None explicitly to simulate a gh failure (owner not resolved). Leave as
    the default sentinel to invoke the live _gh_owner() call.

    FAIL-SAFE OFF: any missing signal, error, or mismatch → (False, None).
    EFFECT: suppresses ONLY the substrate-path self-disable DENY; the hard-rule
    floor (force-push, curl|sh), secret-egress backstop, xc.injection-attempt,
    and the discretionary panel are never touched by this exemption.
    """
    try:
        cr = (posture or {}).get("command_review")
        if not isinstance(cr, dict):
            return False, None
        dev_exempt = cr.get("dev_repo_exempt")
        if dev_exempt is not True:  # strict is True — must be a Python bool True
            return False, None

        # Signal (b): gh-authenticated repo identity.
        # _resolved_owner sentinel → live call; None → simulate gh failure; str → injected.
        if _resolved_owner is _OWNER_NOT_INJECTED:
            owner: str | None = _gh_owner(root)
        else:
            owner = _resolved_owner  # type: ignore[assignment]
        if owner != _EXEMPT_REPO:
            return False, None

        # Signal (c): marketplace.json presence + name.
        if not _marketplace_json_valid(root):
            return False, None

        return True, owner
    except Exception:
        return False, None


def screen_substrate_path(target_raw: str, project_root: Path) -> tuple[bool, str | None]:
    """(deny, concern_id) for a file-shape target that mutates the Thing's own
    substrate. Catalog-independent; fail-closed on doubt for a toggled category."""
    if not target_raw:
        return False, None
    norm = unicodedata.normalize("NFC", target_raw)
    rps, inodes = _substrate_paths(project_root)
    p = Path(norm)
    if not p.is_absolute() and not norm.startswith("~"):
        p = project_root / p
    cands = {
        os.path.normcase(os.path.realpath(str(p))),  # resolves .. and symlinks
        os.path.normcase(os.path.abspath(str(p))),  # lexical (target may not exist yet)
    }
    for sp in rps:
        for c in cands:
            if c == sp or c.startswith(sp + os.sep):
                return True, "xc.tribunal-self-disable"
    try:  # inode membership — catches a hardlink to a substrate file
        st = os.stat(str(p))
        if (st.st_dev, st.st_ino) in inodes:
            return True, "xc.tribunal-self-disable"
    except OSError:
        pass
    return False, None


def _posture_content_disables(content: str) -> bool:
    """True if the RESULTING comfort-posture.yaml document would self-disable the
    tribunal: parse it (not a regex — a regex over content is evaded by
    reformatting, §2a) and deny if it flips any category's `thing:` off or carries
    a `command_review:` / `gate_floor:` block. Unparseable → DENY (fail closed)."""
    try:
        import yaml  # type: ignore

        doc = yaml.safe_load(content)
    except Exception:
        return True  # unparseable posture write → DENY
    if not isinstance(doc, dict):
        return True
    if "command_review" in doc or "gate_floor" in doc:
        return True
    cats = doc.get("categories") or {}
    if isinstance(cats, dict):
        for cfg in cats.values():
            if isinstance(cfg, dict):
                v = cfg.get("thing")
                # Flag a write that sets `thing` to ANY value `thing_enabled_for`
                # treats as OFF — not just the {off,false,no} strings. Mirrors that
                # function's truthiness exactly so `thing: 0` / `"0"` / `disabled`
                # can't slip a tribunal-disabling write past the self-disable guard.
                if v is not None:
                    enabled = v in _TRUTHY or (
                        isinstance(v, str) and v.strip().lower() in {"on", "true", "yes"}
                    )
                    if not enabled:
                        return True
    return False


def _apply_edits_to_text(original: str, tool_name: str, ti: dict) -> str | None:
    """Reconstruct the post-edit file content for an Edit/MultiEdit, or None if it
    cannot be reconstructed faithfully (an old_string that doesn't occur, an
    ambiguous non-replace_all match, or a malformed edit list). None → the caller
    fails closed (DENY), so a crafted Edit can't dodge the screen by being
    unreconstructable."""
    if tool_name == "Edit":
        edits = [ti]
    elif tool_name == "MultiEdit":
        edits = ti.get("edits")
        if not isinstance(edits, list) or not edits:
            return None
    else:
        return None
    text = original
    for e in edits:
        if not isinstance(e, dict):
            return None
        old = e.get("old_string")
        new = e.get("new_string")
        if not isinstance(old, str) or not isinstance(new, str):
            return None
        if old == "":
            # Create/prepend semantics: only valid against an empty original.
            if text != "":
                return None
            text = new
            continue
        count = text.count(old)
        if count == 0:
            return None  # edit wouldn't apply — can't reconstruct the result
        if e.get("replace_all"):
            text = text.replace(old, new)
        else:
            if count > 1:
                return None  # ambiguous (the real tool errors) — fail closed
            text = text.replace(old, new, 1)
    return text


def _posture_write_disables(tool_name: str, tool_input: dict, project_root: Path) -> bool:
    """True if a Write/Edit/MultiEdit to comfort-posture.yaml would self-disable the
    tribunal. The Write (full-content) shape screens its content directly; the
    Edit/MultiEdit shapes RECONSTRUCT the resulting document from the on-disk file
    plus the edits and screen that (2026-07-09 P2 fix — the prior code returned
    False for Edit/MultiEdit and relied only on the \\A-anchored 4000-char
    screen_always regex, which a >4 KiB MultiEdit can push the disabling text past).
    An Edit/MultiEdit whose result can't be faithfully reconstructed → DENY."""
    ti = tool_input or {}
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        return False
    target = unicodedata.normalize("NFC", ti.get("file_path", "") or "")
    if not target.endswith("comfort-posture.yaml"):
        return False
    if tool_name == "Write":
        return _posture_content_disables(ti.get("content", ""))
    # Edit / MultiEdit — reconstruct the resulting document from disk + the edits.
    try:
        disk_path = (project_root / target) if not os.path.isabs(target) else Path(target)
        original = disk_path.read_text(encoding="utf-8") if disk_path.is_file() else ""
    except Exception:
        return True  # can't read the base doc → fail closed
    resulting = _apply_edits_to_text(original, tool_name, ti)
    if resulting is None:
        return True  # unreconstructable → fail closed
    return _posture_content_disables(resulting)


# ── Config reading ───────────────────────────────────────────────────────────


def _load_yaml(path: Path):
    """Load a YAML file with pyyaml; raise ValueError on a parse error."""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        # pyyaml is present in the devcontainer + CI; this path only triggers on
        # a stripped consumer environment. Be honest rather than guess.
        raise ValueError("pyyaml not available to parse YAML")


_TRUTHY = {True, "on", "true", "yes", "1"}


def thing_enabled_for(posture: dict, category: str | None) -> bool:
    """Is the per-category `thing:` toggle ON in comfort-posture.yaml?

    Effective enabled = master_gate AND per-category toggle.

    Master gate (`command_review.enabled`): absent/True → enabled; False →
    globally off (no category is reviewed, regardless of per-category toggles).
    This is the AND-gate: master must be True (or absent) AND the per-category
    `thing:` must be truthy. The dashboard serialises `command_review.enabled`
    when it is explicitly set; consumers who never touch it get the default (True)
    via the absent-key logic here. NOT a bulk per-category setter — it is a
    top-level circuit-breaker only.
    """
    if not category:
        return False
    # Master gate: absent → True (enabled by default).
    cr = (posture or {}).get("command_review")
    if isinstance(cr, dict):
        master = cr.get("enabled")
        if master is False or (
            isinstance(master, str) and master.strip().lower() in {"off", "false", "no", "0"}
        ):
            return False
    cats = (posture or {}).get("categories", {}) or {}
    cfg = cats.get(category)
    if isinstance(cfg, dict):
        val = cfg.get("thing")
        return val in _TRUTHY or (
            isinstance(val, str) and val.strip().lower() in {"on", "true", "yes"}
        )
    return False  # bare-string (legacy) category has no toggle


# ── T3 panel defaults (design §B.4.3) ─────────────────────────────────────────
# The four seats, each filled by an existing ravenclaude-core agent (no new
# agents — House Rule). Heterogeneous backbones break seat correlation: spend
# the budget on the security + tie-break seats, run the fast seats on Haiku.
_DEFAULT_PANEL = {
    "forseti": {"agent": "security-reviewer", "model": "claude-opus-4-8"},
    "mimir": {"agent": "code-reviewer", "model": "claude-haiku-4-5"},
    # Heimdall is the injection seat — the assessment (must-fix #4) flagged that
    # running the adversarial-content reviewer on the weakest model is exactly
    # where you don't want to economize. Bumped to Sonnet (Mímir, the correctness
    # seat, stays on the fast/cheap Haiku).
    "heimdall": {"agent": "prompt-engineer", "model": "claude-sonnet-4-6"},
    "thor": {"agent": "architect", "model": "claude-opus-4-8"},
}
_DEFAULT_CONFIDENCE_THRESHOLD = 0.5
_DEFAULT_SEAT_TIMEOUT = 45  # per-seat soft cap (s); parallel `claude -p` cold-starts
#   contend and run ~24-29s (a single warm seat is ~8s), so 18s abstained the
#   whole panel on modest machines. 45s clears the observed parallel latency with
#   margin and stays well under panel_deadline_seconds (75) and the 90s hook timeout.
_DEFAULT_PANEL_DEADLINE = 75  # panel hard deadline (s); must stay < hook timeout (90)
_DEFAULT_AUDIT_DIR = ".ravenclaude/runs/thing"
# Timeout / abstention posture per category. The high-stakes categories fail
# CLOSED (deny) — *deviation from design §B.3.5* (which says "ask"): deny is the
# only verdict that holds under bypass modes, and these are exactly where
# failing open is catastrophic. shell_readonly keeps "ask".
_DEFAULT_TIMEOUT_POSTURE = {
    "shell_remote_mutate": "deny",
    "shell_code_exec": "deny",
    "shell_readonly": "ask",
}
_SEATS = ("forseti", "mimir", "heimdall", "thor")


def _merge_panel(base: dict, override) -> None:
    """Per-seat merge of a panel override (mutates base in place)."""
    if not isinstance(override, dict):
        return
    for seat in _SEATS:
        entry = override.get(seat)
        if isinstance(entry, dict):
            if isinstance(entry.get("agent"), str):
                base[seat]["agent"] = entry["agent"]
            if isinstance(entry.get("model"), str):
                base[seat]["model"] = entry["model"]


def resolve_panel_config(root: Path, posture: dict | None) -> tuple[dict, str | None]:
    """Resolve the tribunal panel config with precedence:

        comfort-posture.yaml `command_review:`  (dashboard-authored)
          >  .ravenclaude/thing.yaml             (advanced / manual)
          >  built-in defaults

    Dashboard authors only per-seat models + the confidence threshold; the
    timers, audit dir, and per-category timeout posture come from thing.yaml or
    the defaults. Returns (config, error); a malformed thing.yaml yields an
    error so the orchestrator fails closed.
    """
    cfg = {
        "panel": {s: dict(_DEFAULT_PANEL[s]) for s in _SEATS},
        "confidence_threshold": _DEFAULT_CONFIDENCE_THRESHOLD,
        "seat_timeout_seconds": _DEFAULT_SEAT_TIMEOUT,
        "panel_deadline_seconds": _DEFAULT_PANEL_DEADLINE,
        "audit_dir": _DEFAULT_AUDIT_DIR,
        "timeout_posture_map": dict(_DEFAULT_TIMEOUT_POSTURE),
    }
    error: str | None = None

    # Layer 1: thing.yaml (advanced / manual).
    path = root / ".ravenclaude" / "thing.yaml"
    if path.exists():
        try:
            data = _load_yaml(path) or {}
            if not isinstance(data, dict):
                error = "thing.yaml: top level is not a mapping"
            else:
                _merge_panel(cfg["panel"], data.get("panel"))
                # Legacy T2 single-seat config maps to the Mímir seat.
                legacy = data.get("seat")
                if isinstance(legacy, dict) and not data.get("panel"):
                    if isinstance(legacy.get("agent"), str):
                        cfg["panel"]["mimir"]["agent"] = legacy["agent"]
                    if isinstance(legacy.get("model"), str):
                        cfg["panel"]["mimir"]["model"] = legacy["model"]
                if isinstance(data.get("confidence_threshold"), (int, float)):
                    cfg["confidence_threshold"] = float(data["confidence_threshold"])
                # Accept the new timer names and the legacy internal_timeout_seconds.
                # `not isinstance(bool)` so a stray `seat_timeout_seconds: true`
                # isn't silently coerced to a 1-second timeout (bool is an int).
                for key in ("seat_timeout_seconds", "internal_timeout_seconds"):
                    if isinstance(data.get(key), int) and not isinstance(data.get(key), bool):
                        cfg["seat_timeout_seconds"] = data[key]
                if isinstance(data.get("panel_deadline_seconds"), int) and not isinstance(
                    data.get("panel_deadline_seconds"), bool
                ):
                    cfg["panel_deadline_seconds"] = data["panel_deadline_seconds"]
                if isinstance(data.get("timeout_posture"), dict):
                    cfg["timeout_posture_map"].update(
                        {k: v for k, v in data["timeout_posture"].items() if isinstance(v, str)}
                    )
                audit = data.get("audit")
                if isinstance(audit, dict) and isinstance(audit.get("dir"), str):
                    cfg["audit_dir"] = audit["dir"]
        except Exception as exc:  # malformed YAML — fail closed upstream
            error = f"thing.yaml: {exc}"

    # Layer 2: comfort-posture.yaml `command_review:` (dashboard-authored; wins).
    cr = (posture or {}).get("command_review")
    if isinstance(cr, dict):
        _merge_panel(cfg["panel"], cr.get("panel"))
        if isinstance(cr.get("confidence_threshold"), (int, float)):
            cfg["confidence_threshold"] = float(cr["confidence_threshold"])

    # Phase 2 (v0.112.0): Copilot-aware seat soft cap. Under Copilot CLI, the
    # adapter (PR A) exports THING_HOST=copilot before invoking the real hook.
    # `claude -p` cold-starts ~24-29s per seat under Copilot; the 45s default
    # gave only ~1.5 seats of margin and abstained on modest machines. 90s gives
    # ~3 seats of margin. Removes the abstain at its source — never lowers the
    # security floor (an abstaining panel still fails closed per timeout_posture).
    # Only applies if the user hasn't already overridden seat_timeout_seconds —
    # an explicit override always wins. The cap stays under panel_deadline_seconds
    # if the user raises BOTH; otherwise we also bump the panel deadline so the
    # seat cap doesn't get clipped by the panel deadline before it can fire.
    if os.environ.get("THING_HOST") == "copilot":
        if cfg["seat_timeout_seconds"] == _DEFAULT_SEAT_TIMEOUT:
            cfg["seat_timeout_seconds"] = 90
            # Ensure panel_deadline > seat_timeout so the seat cap isn't clipped.
            if cfg["panel_deadline_seconds"] == _DEFAULT_PANEL_DEADLINE:
                cfg["panel_deadline_seconds"] = 105

    return cfg, error


# ── T5 tier model (risk = category base tier + severity escalation bump) ──────
# Every reviewed command resolves to one of four tiers. The category sets a base
# tier; a deterministic high/critical concern bumps it up. The tier drives which
# seats convene, the confidence bar, and whether a panel-ALLOW is surfaced to the
# human (gate_floor). A clean low command (a read with no escalation) is cleared
# by the zero-cost deterministic screen alone — no LLM panel.

_TIER_ORDER = ("low", "medium", "high", "extreme")
_TIER_RANK = {t: i for i, t in enumerate(_TIER_ORDER)}

# Read-shaped categories are never surfaced to the human as an `ask`: a clean
# read auto-allows, an escalated read is auto-decided by the panel. The low base
# tier and this set coincide by construction.
_READ_CATEGORIES = {
    "file_read_project",
    "file_read_global",
    "shell_readonly",
    "network_read",
}

# Category -> base risk tier, over the 12 comfort-posture categories (EMISSIONS).
_DEFAULT_CATEGORY_TIER_MAP = {
    "file_read_project": "low",
    "file_read_global": "low",
    "shell_readonly": "low",
    "network_read": "low",
    "file_edit_project": "medium",
    "shell_local_mutate": "medium",
    "shell_package_install": "medium",
    "network_write": "medium",
    "mcp_tools": "medium",
    "file_edit_global": "high",
    "shell_remote_mutate": "high",
    "shell_code_exec": "extreme",
}

# Per-tier panel shape. `seats` = which seats convene; `mandatory` can't be
# removed by a dashboard override (re-unioned in); `confidence` is the per-tier
# bar (escalating with stakes) below which a seat vote convenes Thor. `low` runs
# no panel.
_DEFAULT_TIERS = {
    "low": {"seats": [], "mandatory": [], "confidence": _DEFAULT_CONFIDENCE_THRESHOLD},
    "medium": {"seats": ["mimir", "heimdall"], "mandatory": ["heimdall"], "confidence": 0.5},
    "high": {
        "seats": ["forseti", "mimir", "heimdall"],
        "mandatory": ["heimdall"],
        "confidence": 0.6,
    },
    "extreme": {
        "seats": ["forseti", "mimir", "heimdall"],
        "mandatory": ["forseti", "heimdall"],
        "confidence": 0.7,
    },
}

# Default lowest tier whose panel-ALLOW is surfaced to the human for confirmation.
# medium..extreme is the dashboard-exposed range; `high` is the conservative
# default (reads + low mutates auto-resolve via the panel; high/extreme surface).
_DEFAULT_GATE_FLOOR = "high"


def _norm_tier(value, fallback: str) -> str:
    return value if isinstance(value, str) and value in _TIER_RANK else fallback


def _escalate_tier(base: str, max_severity: str | None) -> str:
    """Severity bump: a high concern bumps the base up one tier; a critical
    concern bumps straight to extreme; low/medium/none does not bump."""
    rank = _TIER_RANK.get(base, _TIER_RANK["medium"])
    if max_severity == "critical":
        rank = _TIER_RANK["extreme"]
    elif max_severity == "high":
        rank = min(_TIER_RANK["extreme"], rank + 1)
    return _TIER_ORDER[rank]


def resolve_tier_config(root: Path, posture: dict | None) -> tuple[dict, str | None]:
    """Resolve the tier model, same precedence as the panel config:

        comfort-posture.yaml `command_review:`  >  .ravenclaude/thing.yaml  >  defaults

    Returns (cfg, error). cfg carries everything resolve_panel_config returns
    (per-seat models, timers, audit dir) PLUS tiers, category_tier_map, gate_floor.
    """
    panel_cfg, error = resolve_panel_config(root, posture)
    tiers = {t: dict(_DEFAULT_TIERS[t]) for t in _TIER_ORDER}
    cat_map = dict(_DEFAULT_CATEGORY_TIER_MAP)
    gate_floor = _DEFAULT_GATE_FLOOR
    # #15 knobs (same precedence: command_review > thing.yaml > defaults).
    bypass: list[str] = []
    cache_ttl = 0
    fatigue = 0
    # §MCP identity — the deterministic server allowlist. thing.yaml carries it at
    # top level (`mcp.allowed_servers:`); comfort-posture carries it under
    # `command_review.mcp.allowed_servers`. Last-present-wins (posture > thing.yaml).
    mcp_allowed: list[str] = []

    def _apply(block) -> None:
        nonlocal gate_floor, bypass, cache_ttl, fatigue, mcp_allowed
        if not isinstance(block, dict):
            return
        mcp_block = block.get("mcp")
        if isinstance(mcp_block, dict) and isinstance(mcp_block.get("allowed_servers"), list):
            mcp_allowed = [s for s in mcp_block["allowed_servers"] if isinstance(s, str)]
        gf = block.get("gate_floor")
        if isinstance(gf, str) and gf in _TIER_RANK and gf != "low":
            gate_floor = gf
        if isinstance(block.get("bypass"), list):
            bypass = [p for p in block["bypass"] if isinstance(p, str)]
        for key, attr in (("cache_ttl_seconds", "cache_ttl"), ("fatigue_threshold", "fatigue")):
            v = block.get(key)
            if isinstance(v, int) and v >= 0:
                if attr == "cache_ttl":
                    cache_ttl = v
                else:
                    fatigue = v
        tm = block.get("category_tier_map")
        if isinstance(tm, dict):
            for cat, tier in tm.items():
                if isinstance(tier, str) and tier in _TIER_RANK:
                    cat_map[cat] = tier
        tcfg = block.get("tiers")
        if isinstance(tcfg, dict):
            for t in _TIER_ORDER:
                entry = tcfg.get(t)
                if not isinstance(entry, dict):
                    continue
                if isinstance(entry.get("seats"), list):
                    tiers[t]["seats"] = [s for s in entry["seats"] if s in _SEATS]
                if isinstance(entry.get("mandatory_seats"), list):
                    tiers[t]["mandatory"] = [s for s in entry["mandatory_seats"] if s in _SEATS]
                if isinstance(entry.get("confidence_threshold"), (int, float)):
                    tiers[t]["confidence"] = float(entry["confidence_threshold"])

    # Layer 1: thing.yaml. Layer 2: comfort-posture command_review: (wins).
    path = root / ".ravenclaude" / "thing.yaml"
    if path.exists():
        try:
            data = _load_yaml(path) or {}
            if isinstance(data, dict):
                _apply(data)
        except Exception as exc:
            if not error:
                error = f"thing.yaml: {exc}"
    _apply((posture or {}).get("command_review"))

    cfg = dict(panel_cfg)
    cfg["tiers"] = tiers
    cfg["category_tier_map"] = cat_map
    cfg["gate_floor"] = gate_floor
    cfg["bypass"] = bypass
    cfg["cache_ttl_seconds"] = cache_ttl
    cfg["fatigue_threshold"] = fatigue
    cfg["mcp_allowed_servers"] = mcp_allowed
    return cfg, error


# Anti-correlated-hallucination rule (Matt 2026-05-26): when >=2 seats convene, at
# least two DISTINCT model backbones must run, so a single model's blind spot can't
# pass the whole panel unseen. If a config collapsed the convened seats onto one
# model, reassign one seat to a different (preferring equal-or-stronger) model.
_DIVERSITY_PREF = ["claude-sonnet-4-6", "claude-opus-4-8", "claude-haiku-4-5"]


def _enforce_model_diversity(panel: dict, convened: list[str]) -> tuple[dict, bool]:
    """Return (panel, adjusted). Guarantees >=2 distinct models among `convened`."""
    if len(convened) < 2:
        return panel, False
    models = [(panel.get(s) or {}).get("model") for s in convened]
    if len({m for m in models if m}) >= 2:
        return panel, False  # already heterogeneous
    common = models[0]
    alt = next((m for m in _DIVERSITY_PREF if m != common), "claude-sonnet-4-6")
    out = {k: dict(v) for k, v in panel.items()}
    out.setdefault(convened[-1], {})["model"] = alt  # diversify the last convened seat
    return out, True


def _decision_detail(root: Path, posture: dict, command: str, category: str | None) -> dict:
    """Full tier/route/gate computation for a (command, category).

    Used by `classify` when the category's toggle is on, AND by `preview`
    unconditionally (the dashboard 'Test a command' simulator) so the preview
    is the REAL engine decision, never a reimplementation that could drift.
    """
    d: dict = {}
    cfg, cfg_err = resolve_tier_config(root, posture)
    cfg.pop("timeout_posture_map", None)
    d["seat_timeout_seconds"] = cfg["seat_timeout_seconds"]
    d["panel_deadline_seconds"] = cfg["panel_deadline_seconds"]
    d["audit_dir"] = cfg["audit_dir"]
    if cfg_err:
        d["config_error"] = cfg_err

    route = _route(command, category)
    d.update(route)

    # §MCP identity — deterministic server allowlist (design §MCP identity). When an
    # allowlist IS configured, a WRITE verb from a server NOT on it is denied pre-LLM
    # (cite mcp.unverified-server) — folded into pre_llm_deny so the orchestrator's
    # existing deny path handles emit + Sága with no special-casing. An ABSENT
    # allowlist changes nothing (opt-in strictness): the mcp concerns stay
    # seat-judged, so no existing mcp_tools user is newly blocked. Reads and
    # allowlisted-server writes fall through to the panel as before. The `command`
    # arg is the reviewed_text; for mcp its first line is the `mcp__server__verb`.
    allowed = cfg.get("mcp_allowed_servers") or []
    d["mcp_allowed_servers"] = allowed
    d["mcp_unverified_deny"] = False
    if category == "mcp_tools" and allowed:
        mcp_tool = command.split("\n", 1)[0]
        server = mcp_server_name(mcp_tool)
        if server and server not in allowed and not mcp_verb_is_read(mcp_tool):
            d["pre_llm_deny"] = True
            d["deny_concern"] = "mcp.unverified-server"
            d["mcp_unverified_deny"] = True
            if "mcp.unverified-server" not in (d.get("concerns") or []):
                d["concerns"] = list(d.get("concerns") or []) + ["mcp.unverified-server"]

    base_tier = _norm_tier(cfg["category_tier_map"].get(category), "medium")
    final_tier = _escalate_tier(base_tier, route.get("max_severity"))
    tier_cfg = cfg["tiers"][final_tier]
    is_read = category in _READ_CATEGORIES
    gate_floor = cfg["gate_floor"]

    want = set(tier_cfg["seats"]) | set(tier_cfg["mandatory"])
    convened = [s for s in _SEATS if s in want and s != "thor"]
    if _TIER_RANK[final_tier] >= _TIER_RANK["medium"] and not convened:
        convened = ["forseti", "mimir", "heimdall"]
    # Enforce model heterogeneity across the convened panel (anti-correlated
    # hallucination): >=2 seats must run >=2 distinct models.
    panel_models, diversified = _enforce_model_diversity(cfg["panel"], convened)
    d["panel"] = panel_models
    d["convened_seats"] = convened
    d["model_diversity_enforced"] = diversified
    d["confidence_threshold"] = float(tier_cfg["confidence"])
    d["tier"] = final_tier
    d["base_tier"] = base_tier
    d["is_read"] = is_read
    d["gate_floor"] = gate_floor
    d["panel_required"] = _TIER_RANK[final_tier] >= _TIER_RANK["medium"]
    d["gate_allow"] = (not is_read) and _TIER_RANK[final_tier] >= _TIER_RANK[gate_floor]
    d["timeout_posture"] = "deny"

    # ── #15 cost/UX knobs (bypass-list / verdict cache / session-fatigue) ────────
    # These let the orchestrator skip the EXPENSIVE LLM panel; the deterministic
    # screen (pre_llm_deny + self-disable) ALWAYS runs regardless, so the hard
    # floor is never bypassed. bypass also requires a non-critical screen.
    bypass_match = False
    for p in cfg.get("bypass") or []:
        try:
            if re.search(p, command):
                bypass_match = True
                break
        except re.error:
            continue
    # Never bypass a critical-severity screen even if the pattern matches.
    d["bypass_match"] = bool(bypass_match) and route.get("max_severity") != "critical"
    d["cache_ttl_seconds"] = int(cfg.get("cache_ttl_seconds") or 0)
    d["fatigue_threshold"] = int(cfg.get("fatigue_threshold") or 0)
    # config_hash invalidates the verdict cache when the rules (tiers/panel/
    # gate_floor/category map) OR the concern catalog change — so a cached
    # permissive verdict is never reused after the policy that produced it moves.
    cfg_blob = json.dumps(
        {
            "tiers": cfg["tiers"],
            "panel": cfg["panel"],
            "gate_floor": cfg["gate_floor"],
            "category_tier_map": cfg["category_tier_map"],
            # Track B §Serialization: fold the substrate set + classifier version so a
            # cached verdict is invalidated when either changes (the VALUEs, not file
            # mtimes — deterministic across checkouts).
            "substrate": sorted(THING_SUBSTRATE),
            "classify_payload_version": CLASSIFY_PAYLOAD_VERSION,
            # §MCP identity — a change to the server allowlist must invalidate a cached
            # mcp_tools verdict (a server added/removed flips the deterministic deny).
            "mcp_allowed_servers": sorted(cfg.get("mcp_allowed_servers") or []),
        },
        sort_keys=True,
    )
    try:
        cat_text = (_HERE.parent / "knowledge" / "concerns-catalog.md").read_text(encoding="utf-8")
    except OSError:
        cat_text = ""
    d["config_hash"] = hashlib.sha256((cfg_blob + cat_text).encode("utf-8")).hexdigest()[:16]

    # Human-readable predicted outcome for the simulator.
    if d.get("pre_llm_deny"):
        d["predicted_gate"] = (
            f"DENY — blocked before any model runs ({d.get('deny_concern') or 'hard rule'})"
        )
    elif not d["panel_required"]:
        d["predicted_gate"] = "ALLOW — clean low-risk command, no panel convened"
    elif is_read:
        d["predicted_gate"] = "panel auto-decides (reads are never surfaced to you)"
    elif d["gate_allow"]:
        d["predicted_gate"] = (
            "a confident panel-ALLOW is surfaced to you as ASK; DENY blocks, EDIT rewrites"
        )
    else:
        d["predicted_gate"] = (
            "panel decides autonomously (tier is below gate_floor); DENY blocks, EDIT rewrites"
        )
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="project root (consumer cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("classify", help="classify a command + report toggle state")
    c.add_argument("command", help="the shell command string")
    p = sub.add_parser(
        "preview", help="full tier/seat/gate preview regardless of toggle (dashboard simulator)"
    )
    p.add_argument("command", help="the shell command string")
    # Track B: classify ANY tool shape. Reads {tool_name, tool_input} as JSON on
    # stdin (not argv — a 1 MiB Write.content would overflow ARG_MAX).
    sub.add_parser("classify-payload", help="classify a tool-call payload (JSON on stdin)")
    args = ap.parse_args()

    root = Path(args.root).resolve()

    # `screened` is the text the self-disable / hard-rule / concern screens run
    # against; `category` is the routing target. Bash uses the command string;
    # other shapes extract a per-shape reviewed text (§3).
    if args.cmd == "classify-payload":
        try:
            payload = json.load(sys.stdin)
        except (json.JSONDecodeError, ValueError):
            payload = {}
        # Valid-but-non-object JSON (["a","b"], null) parses cleanly but has no
        # .get(); normalize to an empty dict so classify fails safe rather than crashing.
        if not isinstance(payload, dict):
            payload = {}
        tool_name = payload.get("tool_name", "") or ""
        tool_input = payload.get("tool_input", {}) or {}
        category = classify_payload(tool_name, tool_input, root)
        screened = reviewed_text(tool_name, tool_input)
        result: dict = {"category": category, "tool_name": tool_name, "thing_enabled": False}
    else:
        category = classify(args.command)
        screened = args.command
        result = {"category": category, "thing_enabled": False}

    # §Payload caps — a reviewed payload larger than SCREEN_MAX_BYTES cannot be
    # fully screened, so it fails closed (the orchestrator denies it for a toggled
    # category). Don't scan the oversize content; the path-based file self-disable
    # below still runs (it's content-independent).
    payload_too_large = (
        args.cmd == "classify-payload"
        and len(screened.encode("utf-8", "replace")) > SCREEN_MAX_BYTES
    )
    result["payload_too_large"] = payload_too_large
    # The orchestrator passes this to the seat as THING_PAYLOAD (non-Bash shapes).
    # Omitted when oversize (we deny before convening) so the JSON isn't bloated.
    if args.cmd == "classify-payload":
        # Per-shape Sága tool_input + cache identity (§Serialization) — always
        # emitted (cheap; the Sága self-disable/hard-rule writes need them even
        # when oversize denies before the panel).
        result["saga_tool_input"] = saga_tool_input(tool_name, tool_input)
        result["cache_identity"] = cache_identity(tool_name, tool_input, root)
    if args.cmd == "classify-payload" and not payload_too_large:
        result["reviewed_text"] = screened
        result["payload_shape"] = (
            "file"
            if (result.get("tool_name") or "") in ("Edit", "Write", "MultiEdit")
            else "network"
            if (result.get("tool_name") or "") in ("WebFetch", "WebSearch")
            else "mcp"
            if (result.get("tool_name") or "").startswith("mcp__")
            else "command"
        )

    # §B.9.5 / §B.9.3 — the self-disable + hard-rule screens are CATEGORY-
    # INDEPENDENT. The orchestrator only reaches us when some category is toggled
    # on, so this is screened regardless of THIS payload's category or toggle.
    if not payload_too_large:
        result.update(_screen_always(screened))

    # §2/§2a — FILE-shape self-disable: a Write/Edit/MultiEdit whose target is a
    # substrate path (or a Write that rewrites comfort-posture.yaml to disable a
    # category / retune the tiers) has no shell verb for screen_always to match,
    # so screen it here, category-independently, and merge into the self-disable
    # verdict the orchestrator already denies on.
    _file_sd: bool = False
    _file_sd_concern: str | None = None
    if args.cmd == "classify-payload" and tool_name in ("Edit", "Write", "MultiEdit"):
        _file_sd, _file_sd_concern = screen_substrate_path(
            (tool_input or {}).get("file_path", "") or "", root
        )
        if not _file_sd and _posture_write_disables(tool_name, tool_input, root):
            _file_sd, _file_sd_concern = True, "xc.tribunal-self-disable"
        if _file_sd:
            result["self_disable_deny"] = True
            result["self_disable_concern"] = _file_sd_concern

    posture: dict = {}
    posture_path = root / ".ravenclaude" / "comfort-posture.yaml"
    if posture_path.exists():
        try:
            posture = _load_yaml(posture_path) or {}
            result["thing_enabled"] = thing_enabled_for(posture, category)
        except Exception as exc:
            # Malformed posture: can't determine the toggle. Fall through to the
            # settings.json floor (do NOT claim enabled). Report for visibility.
            result["posture_error"] = f"comfort-posture.yaml: {exc}"

    # §Maintainer-substrate exemption — suppresses the file-shape self-disable DENY
    # for marketplace-substrate paths ONLY. Applies after posture is loaded (the
    # exemption reads command_review.dev_repo_exempt).
    #
    # Both trigger sources that can set _file_sd=True are eligible for suppression:
    #   • screen_substrate_path branch  → Write/Edit/MultiEdit targeting a substrate
    #     path (orchestrator, seat wrappers, decision script, hooks/ dir, etc.).
    #   • _posture_write_disables branch → Write to comfort-posture.yaml whose PARSED
    #     result would flip a category off or retune tiers (§2a).
    # Either way _file_sd=True → self_disable_deny=True, and the exemption gate at
    # the `if _file_sd and result.get("self_disable_deny")` check below can clear it.
    # The safety guarantee rests ENTIRELY on the gh-authenticated-owner gate (signal b
    # in _maintainer_substrate_exempt) — not on which trigger source set the flag.
    #
    # Bash-shaped self-disables (sed/rm/echo >> on the same files) are NOT in scope
    # here; those are pre-LLM denied by screen_always (xc.tribunal-self-disable,
    # always_screen) independently of _file_sd, and the exemption never touches
    # _screen_always results.
    # NOT touched: hard-rule floor, secret-egress backstop, xc.injection-attempt,
    # the discretionary panel, or _screen_always results.
    # The exemption is computed ONCE here. The cheap dict-gate inside
    # _maintainer_substrate_exempt (command_review.dev_repo_exempt must be strictly
    # True) short-circuits to (False, None) BEFORE the live `gh` probe, so in a
    # consumer repo — where the flag is never set — this is a couple of dict lookups
    # with zero subprocess cost. The gh-owner probe only fires in the opted-in dev
    # repo, exactly where both exemption effects below are wanted.
    dev_exempt, dev_exempt_owner = _maintainer_substrate_exempt(root, posture)

    if _file_sd and result.get("self_disable_deny") and dev_exempt:
        # Clear ONLY the substrate-path self-disable; preserve everything else.
        result.pop("self_disable_deny", None)
        result.pop("self_disable_concern", None)
        # Audit field: the orchestrator logs why a substrate edit wasn't denied.
        result["maintainer_substrate_exempt"] = True
        result["maintainer_substrate_exempt_owner"] = dev_exempt_owner

    # §A1 — abstain-downgrade (the dev-repo lockout fix). In the SAME verified
    # maintainer dev-repo context, an abstaining / inconclusive panel downgrades its
    # fail-closed DENY to ASK (never to ALLOW). The orchestrator reads this flag at
    # abstain time and substitutes "ask" for the "deny" timeout_posture. An abstain
    # in the maintainer context is a latency artifact (parallel `claude -p` seats
    # cold-starting past the per-seat soft cap), not a security signal — so it should
    # defer to the human, not hard-block the maintainer editing the Thing's own
    # engine in the Thing's own repo. UNTOUCHED — all resolve before/independent of
    # the posture branch the orchestrator applies this to: the hard-rule floor
    # (force-push, curl|sh), the self-disable guard, the injection DENY, and the
    # secret-egress backstop. It can only ever turn a deny into an ask, never allow.
    if dev_exempt:
        result["dev_repo_abstain_downgrade"] = True

    # `preview` (dashboard simulator) computes the full detail unconditionally;
    # `classify`/`classify-payload` (the live hook path) only when toggled on.
    # Skip the detail/panel for an oversize payload — it fails closed (deny) without
    # convening, so there's no need to run evaluate() over >1 MiB of text.
    if (args.cmd == "preview" or result["thing_enabled"]) and not payload_too_large:
        result.update(_decision_detail(root, posture, screened, category))

    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

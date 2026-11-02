#!/usr/bin/env python3
"""session-claims.py: cross-session work claims for the overnight session-resume routine.

WHY THIS EXISTS
---------------
The "Overnight session resume" routine (docs/overnight-session-resume-routine.md)
restarts idle Claude Code cloud sessions that still have open work. Before it
restarts one, it must know that nothing else is already working on the same
content. A cloud routine can list every cloud session on the account, but it
cannot see Claude CLI sessions running on a laptop. This script closes that gap
in two halves:

  * LOCAL (writer). A user-level hook on each machine records what every local
    session is working on (repo, branch, changed and uncommitted files, a
    scrubbed one-line title) and publishes it as one JSON file per session on
    the orphan data branch `ravenclaude/session-claims` OF THE REPO THE SESSION
    IS WORKING IN. A claim about a private repo therefore never leaves that
    repo, and a claim pushed to a public repo carries no title.
  * ROUTINE (reader). For each repo it can see, the routine reads that repo's
    claims and recent git activity (`evidence`), adds the running cloud sessions,
    and asks `check` for a deterministic conflict verdict per candidate session.

MARKETPLACE-ONLY. Like scripts/notify.sh, this never ships inside a plugin, so it
never changes a consumer's behavior. The hooks are installed into the user's own
~/.claude/settings.json by `install`, never into any repo's settings.

SUBCOMMANDS
  hook          Hook entry point (SessionStart, UserPromptSubmit, PostToolUse,
                SessionEnd). Always exits 0 and prints nothing on stdout, because
                stdout from SessionStart/UserPromptSubmit is injected into the
                conversation. Publishing runs in a detached child.
  publish       Sync this host's claims to each repo's data branch (the hook spawns it).
  install       Add the hooks to ~/.claude/settings.json and write the config.
  uninstall     Remove the hooks (and, with --purge, the local state).
  status        Show the config, hook wiring, local claims and the publish log.
  active        Read published claims and classify them live / dirty-recent / expired.
  git-signals   Recent commits per remote branch of a clone, with files and the
                Claude-Session trailers that attribute them to a session.
  evidence      One repo's live claims plus its git-signals, in the shape `check` reads.
  branch-files  Files a branch changes relative to the default branch.
  check         Deterministic conflict verdict for candidate sessions.
  --self-test   Prove each rule passes on a good fixture and fails on a bad one.

Fail-safe throughout: a missing config, no git, no network or a cloud container
(CLAUDE_CODE_REMOTE=true) all make the hook a silent no-op.
"""

from __future__ import annotations

import argparse
import contextlib
import fnmatch
import hashlib
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA_VERSION = 1
DEFAULT_BRANCH = "ravenclaude/session-claims"
PUBLISH_EVERY_S = 15 * 60  # heartbeat throttle
LIVE_TTL_H = 6  # an un-ended claim older than this is no longer "live"
DIRTY_TTL_H = 48  # uncommitted files keep a claim relevant this long
PRUNE_DAYS = 7  # this host's claims older than this are deleted
FILE_CAP = 300  # files recorded per workspace
TITLE_CAP = 120
GIT_TIMEOUT = 10
NET_TIMEOUT = 60
LOCK_STALE_S = 300
LOG_CAP_BYTES = 200_000
VISIBILITY_TTL_S = 7 * 24 * 3600  # cache of public/private lookups
HOOK_MARKER = "session-claims.py"  # identifies our entries in settings.json
DEFAULT_BRANCH_NAMES = {"", "head", "main", "master"}
MIN_BARE_REF = 100  # a bare "#N" counts as a PR reference only from #100 up

SCRIPT = Path(__file__).resolve()
REPO_ROOT = SCRIPT.parent.parent
SCRUB_HELPER = REPO_ROOT / "plugins" / "ravenclaude-core" / "hooks" / "_scrub.sh"
HOOK_EVENTS = ("SessionStart", "UserPromptSubmit", "PostToolUse", "SessionEnd")
POST_TOOL_MATCHER = "Write|Edit|MultiEdit|NotebookEdit|Bash"


# --------------------------------------------------------------------------- utils


def _home() -> Path:
    override = os.environ.get("RAVENCLAUDE_SESSION_CLAIMS_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".ravenclaude" / "session-claims"


def _settings_path() -> Path:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    return Path(base).expanduser() / "settings.json"


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _host() -> str:
    raw = os.environ.get("RAVENCLAUDE_SESSION_CLAIMS_HOST") or socket.gethostname()
    short = raw.split(".")[0] or "host"
    return re.sub(r"[^A-Za-z0-9._-]", "-", short)[:64]


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "-", value)[:128]


def _read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _git(args: list[str], cwd: Path | str | None = None, timeout: int = GIT_TIMEOUT):
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        return subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(["git", *args], 124, "", f"{type(exc).__name__}: {exc}")


def normalize_repo(url: str) -> str | None:
    """Map any GitHub remote URL (https, ssh, scp-style, the cloud git proxy) to owner/repo."""
    url = (url or "").strip()
    patterns = (
        r"^git@github\.com:(?P<o>[^/]+)/(?P<r>[^/]+?)(?:\.git)?/?$",
        r"^(?:ssh://)?git@github\.com[:/](?P<o>[^/]+)/(?P<r>[^/]+?)(?:\.git)?/?$",
        r"^https?://(?:[^@/]+@)?github\.com/(?P<o>[^/]+)/(?P<r>[^/]+?)(?:\.git)?/?$",
        # Claude Code on the web: http://local_proxy@127.0.0.1:<port>/git/<owner>/<repo>
        r"^https?://(?:[^@/]+@)?127\.0\.0\.1(?::\d+)?/git/(?P<o>[^/]+)/(?P<r>[^/]+?)(?:\.git)?/?$",
    )
    for pat in patterns:
        m = re.match(pat, url)
        if m:
            return f"{m.group('o')}/{m.group('r')}".lower()
    return None


_REF_RE = re.compile(r"(?<![\w/#])(?:(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+))?#(?P<num>\d{1,6})\b")


def extract_refs(text: str, repos: list[str]) -> list[str]:
    """PR/issue references in free text as owner/repo#N. A bare #N maps to every repo given."""
    out: set[str] = set()
    for m in _REF_RE.finditer(text or ""):
        num = int(m.group("num"))
        if m.group("repo"):
            out.add(f"{m.group('repo').lower()}#{num}")
        elif num >= MIN_BARE_REF:
            out.update(f"{r.lower()}#{num}" for r in repos)
    return sorted(out)


def scrub(text: str) -> str | None:
    """Redact secret-shaped tokens with the repo's canonical patterns (_scrub.sh).

    Returns None when the helper cannot run: a title we cannot scrub is dropped,
    never published raw.
    """
    if not text:
        return ""
    if not SCRUB_HELPER.is_file() or not shutil.which("bash"):
        return None
    try:
        res = subprocess.run(
            ["bash", "-c", 'source "$1" && _scrub_reason "$2"', "_", str(SCRUB_HELPER), text],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if res.returncode != 0:
        return None
    return res.stdout


def make_title(prompt: str) -> str | None:
    one_line = " ".join((prompt or "").split())
    if not one_line:
        return ""
    cleaned = scrub(one_line)
    if cleaned is None:
        return None
    return cleaned[:TITLE_CAP]


# ----------------------------------------------------------------- workspace snapshot


def _default_ref(top: Path) -> str | None:
    res = _git(["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], cwd=top)
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip()
    for cand in ("origin/main", "origin/master"):
        if _git(["rev-parse", "--verify", "--quiet", cand], cwd=top).returncode == 0:
            return cand
    return None


def _porcelain_paths(raw: str) -> list[str]:
    """Paths from `git status --porcelain=v1 -z` (renames carry the old path as a second field)."""
    paths: list[str] = []
    fields = raw.split("\0")
    i = 0
    while i < len(fields):
        entry = fields[i]
        i += 1
        if len(entry) < 4:
            continue
        status, path = entry[:2], entry[3:]
        paths.append(path)
        if "R" in status or "C" in status:
            i += 1  # skip the original path
    return paths


def _origin_url(top: Path | str) -> str:
    """Raw origin URL. Reads the config value first: `remote get-url` expands insteadOf."""
    for args in (["config", "--get", "remote.origin.url"], ["remote", "get-url", "origin"]):
        url = _git(args, cwd=top).stdout.strip()
        if normalize_repo(url):
            return url
    return ""


def _origin_repo(top: Path | str) -> str | None:
    url = _origin_url(top)
    return normalize_repo(url) if url else None


def deploy_guard(top: Path | str, branch: str = DEFAULT_BRANCH) -> str:
    """'' when pushing `branch` to this repo should start no deploy; otherwise the reason.

    GitHub Actions and Cloudflare Pages skip a push whose commit message starts with
    "[skip ci]", which every claim commit does. Vercel's Git integration builds every
    pushed branch and documents no commit-message skip, so a repo with a vercel.json
    must turn deployments off for the branch with git.deploymentEnabled.
    """
    vercel = Path(top) / "vercel.json"
    if not vercel.exists():
        return ""
    data = _read_json(vercel)
    git_cfg = data.get("git") if isinstance(data, dict) else None
    enabled = git_cfg.get("deploymentEnabled") if isinstance(git_cfg, dict) else None
    if enabled is False:
        return ""
    if isinstance(enabled, dict):
        rules = [v for k, v in enabled.items() if fnmatch.fnmatchcase(branch, k)]
        # Vercel deploys a branch that matches several rules if any of them is true.
        if rules and all(v is False for v in rules):
            return ""
    return f'vercel.json has no git.deploymentEnabled {{"{branch}": false}}'


def snapshot_workspace(cwd: str) -> dict | None:
    top_res = _git(["rev-parse", "--show-toplevel"], cwd=cwd)
    if top_res.returncode != 0:
        return None
    top = Path(top_res.stdout.strip())
    remote_url = _origin_url(top)
    repo = normalize_repo(remote_url) if remote_url else None
    if not repo:
        return None
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=top).stdout.strip()
    head = _git(["rev-parse", "HEAD"], cwd=top).stdout.strip()
    status = _git(["status", "--porcelain=v1", "-z", "--untracked-files=normal"], cwd=top)
    dirty = _porcelain_paths(status.stdout) if status.returncode == 0 else []
    branch_files: list[str] = []
    base = _default_ref(top)
    if base and head:
        diff = _git(["diff", "--name-only", f"{base}...HEAD"], cwd=top)
        if diff.returncode == 0:
            branch_files = [p for p in diff.stdout.splitlines() if p]
    return {
        "key": hashlib.sha256(str(top).encode()).hexdigest()[:12],
        "repo": repo,
        "branch": "" if branch == "HEAD" else branch,
        "head": head,
        "base": base or "",
        "dirty_files": sorted(set(dirty))[:FILE_CAP],
        "branch_files": sorted(set(branch_files))[:FILE_CAP],
        # Local only: used to publish, stripped from every published claim.
        "top": str(top),
        "remote_url": remote_url,
    }


LOCAL_ONLY_FIELDS = ("top", "remote_url")


# ------------------------------------------------------------------------- the hook


def load_config() -> dict | None:
    cfg = _read_json(_home() / "config.json")
    if not isinstance(cfg, dict) or cfg.get("enabled") is False:
        return None
    cfg.setdefault("branch", DEFAULT_BRANCH)
    cfg.setdefault("include_title", True)
    return cfg


def _state_path(session_id: str) -> Path:
    return _home() / "state" / f"{_safe_id(session_id)}.json"


def _spawn_publish() -> None:
    if os.environ.get("RAVENCLAUDE_SESSION_CLAIMS_INLINE") == "1":
        cmd_publish(argparse.Namespace())
        return
    subprocess.Popen(
        [sys.executable, str(SCRIPT), "publish"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )


def run_hook(payload: dict, event: str | None = None) -> None:
    if os.environ.get("CLAUDE_CODE_REMOTE") == "true":
        return  # cloud sessions are visible to the routine directly
    cfg = load_config()
    if not cfg:
        return
    event = payload.get("hook_event_name") or event or ""
    session_id = payload.get("session_id")
    if not session_id:
        return
    now = _now()
    path = _state_path(session_id)
    state = _read_json(path) or {
        "schema_version": SCHEMA_VERSION,
        "session_id": session_id,
        "host": _host(),
        "kind": "cli",
        "started_at": _iso(now),
        "status": "active",
        "title": "",
        "workspaces": {},
        "published_at": "",
    }
    due = event in ("SessionStart", "SessionEnd")
    if event == "UserPromptSubmit" and not state.get("title") and cfg.get("include_title"):
        title = make_title(payload.get("prompt", ""))
        if title:
            state["title"] = title
            due = True
    last = _parse_iso(state.get("published_at"))
    if last is None or (now - last).total_seconds() >= PUBLISH_EVERY_S:
        due = True
    if not due:
        return
    ws = snapshot_workspace(payload.get("cwd") or os.getcwd())
    if ws is None and not state["workspaces"]:
        return  # not inside a GitHub repo: nothing worth claiming
    if ws is not None:
        ws["seen_at"] = _iso(now)
        state["workspaces"][ws.pop("key")] = ws
    state["heartbeat_at"] = _iso(now)
    if event == "SessionEnd":
        state["status"] = "ended"
        state["ended_at"] = _iso(now)
    elif state.get("status") == "ended":
        state["status"] = "active"  # a resumed session claims again
        state.pop("ended_at", None)
    state["published_at"] = _iso(now)
    _write_json(path, state)
    _spawn_publish()


def cmd_hook(args) -> int:
    try:
        raw = "" if sys.stdin is None or sys.stdin.isatty() else sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        if isinstance(payload, dict):
            run_hook(payload, getattr(args, "event", None))
    except BaseException:  # a hook must never break the session
        pass
    return 0


# ---------------------------------------------------------------------- publishing


def _log(message: str) -> None:
    path = _home() / "publish.log"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > LOG_CAP_BYTES:
            path.write_text("", encoding="utf-8")
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"{_iso(_now())} {message}\n")
    except OSError:
        pass


@contextlib.contextmanager
def _lock():
    lock = _home() / "lock.d"
    lock.parent.mkdir(parents=True, exist_ok=True)
    acquired = False
    for _ in range(2):
        try:
            lock.mkdir()
            acquired = True
            break
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > LOCK_STALE_S:
                    lock.rmdir()
                    continue
            except OSError:
                pass
            break
    try:
        yield acquired
    finally:
        if acquired:
            with contextlib.suppress(OSError):
                lock.rmdir()


README = """# ravenclaude/session-claims (data branch: never merge)

One JSON file per local Claude CLI session working in this repo, at
`claims/<host>/<session_id>.json`. They are written by `scripts/session-claims.py`
from the RavenClaude marketplace (`python3 scripts/session-claims.py install`, once
per machine). The "Overnight session resume" routine reads them so that it does not
restart cloud work that collides with local work.

Claims about this repo stay in this repo. In a public repo, a claim carries no title.
This branch shares no history with the default branch. Do not open a pull request from it.
"""


def repo_is_private(repo: str) -> bool:
    """True only when GitHub confirms `repo` is private. Unknown counts as public.

    An unauthenticated GET of the repo returns 200 for a public repo and 404 for a
    private one. No token is ever sent. Answers are cached for a week; a failed
    lookup is not cached and is treated as public, so the title is left out.
    """
    override = os.environ.get("RAVENCLAUDE_SESSION_CLAIMS_VISIBILITY", "").strip()
    if override:
        pairs = dict(item.split("=", 1) for item in override.split(",") if "=" in item)
        value = pairs.get(repo, "public") if pairs else override
        return value.strip() == "private"
    cache_file = _home() / "visibility.json"
    cache = _read_json(cache_file, default={}) or {}
    hit = cache.get(repo)
    if isinstance(hit, dict) and time.time() - hit.get("checked", 0) < VISIBILITY_TTL_S:
        return bool(hit.get("private"))
    private = None
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "ravenclaude-session-claims"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            private = bool(json.load(response).get("private"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            private = True
    except (OSError, ValueError):
        pass
    if private is None:
        return False
    cache[repo] = {"private": private, "checked": int(time.time())}
    _write_json(cache_file, cache)
    return private


def _live_states() -> list[dict]:
    """This host's session states, deleting any older than PRUNE_DAYS."""
    now = _now()
    states = []
    state_dir = _home() / "state"
    for state_file in sorted(state_dir.glob("*.json")) if state_dir.is_dir() else []:
        state = _read_json(state_file)
        hb = _parse_iso(state.get("heartbeat_at")) if isinstance(state, dict) else None
        if hb is None or now - hb > timedelta(days=PRUNE_DAYS) or not state.get("session_id"):
            with contextlib.suppress(OSError):
                state_file.unlink()
            continue
        states.append(state)
    return states


def claims_by_repo(states: list[dict]) -> dict[str, dict]:
    """Split session states into one claim per (repo, session), each naming only that repo."""
    out: dict[str, dict] = {}
    for state in states:
        for ws in state.get("workspaces", {}).values():
            repo = ws.get("repo")
            if not repo:
                continue
            entry = out.setdefault(repo, {"remote": "", "tops": [], "claims": {}})
            entry["remote"] = entry["remote"] or ws.get("remote_url", "")
            if ws.get("top") and ws["top"] not in entry["tops"]:
                entry["tops"].append(ws["top"])
            claim = entry["claims"].get(state["session_id"])
            if claim is None:
                claim = {k: v for k, v in state.items() if k not in ("workspaces", "published_at")}
                claim["workspaces"] = []
                entry["claims"][state["session_id"]] = claim
            claim["workspaces"].append({k: v for k, v in ws.items() if k not in LOCAL_ONLY_FIELDS})
    for entry in out.values():
        for claim in entry["claims"].values():
            claim["workspaces"].sort(key=lambda w: w.get("seen_at", ""), reverse=True)
            del claim["workspaces"][5:]
    return out


def _cache_dir(repo: str) -> Path:
    return _home() / "repos" / repo.replace("/", "__")


def _write_host_claims(cache: Path, host: str, claims: dict[str, dict]) -> int:
    host_dir = cache / "claims" / host
    host_dir.mkdir(parents=True, exist_ok=True)
    keep = set()
    for session_id, claim in claims.items():
        name = f"{_safe_id(session_id)}.json"
        keep.add(name)
        _write_json(host_dir / name, claim)
    for old in host_dir.glob("*.json"):
        if old.name not in keep:
            old.unlink()
    return len(keep)


def _ensure_cache(cache: Path, remote: str, branch: str) -> tuple[bool | None, bool]:
    """Prepare the cache clone. Return (ready, is_new_orphan); ready None means unreachable."""
    if (cache / ".git").is_dir():
        _git(["remote", "set-url", "origin", remote], cwd=cache)
        return True, False
    shutil.rmtree(cache, ignore_errors=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    heads = _git(["ls-remote", "--heads", remote, branch], timeout=NET_TIMEOUT)
    if heads.returncode != 0:
        _log(f"ls-remote failed for {remote}: {heads.stderr.strip()[:300]}")
        return None, False
    if heads.stdout.strip():
        res = _git(
            ["clone", "--quiet", "--depth", "20", "--single-branch", "--branch", branch]
            + [remote, str(cache)],
            timeout=NET_TIMEOUT,
        )
        if res.returncode != 0:
            _log(f"clone failed for {remote}: {res.stderr.strip()[:300]}")
            return None, False
        return True, False
    _git(["init", "--quiet", str(cache)])
    _git(["remote", "add", "origin", remote], cwd=cache)
    _git(["checkout", "--quiet", "--orphan", branch], cwd=cache)
    (cache / "README.md").write_text(README, encoding="utf-8")
    return True, True


def _commit(cache: Path, message: str) -> bool:
    res = _git(
        [
            "-c",
            "user.name=RavenClaude session claims",
            "-c",
            "user.email=session-claims@users.noreply.github.com",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "--no-verify",
            "-m",
            message,
        ],
        cwd=cache,
    )
    return res.returncode == 0


def _publish_repo(repo: str, remote: str, branch: str, host: str, claims: dict[str, dict]) -> tuple[bool, str]:
    cache = _cache_dir(repo)
    ready, orphan = _ensure_cache(cache, remote, branch)
    if ready is None:
        return False, "could not reach the repo (see publish.log)"
    if orphan and not claims:
        shutil.rmtree(cache, ignore_errors=True)
        return True, "nothing to publish"
    for attempt in range(1, 4):
        fetch = _git(["fetch", "--quiet", "--depth", "20", "origin", branch], cwd=cache, timeout=NET_TIMEOUT)
        if fetch.returncode == 0:
            _git(["reset", "--quiet", "--hard", "FETCH_HEAD"], cwd=cache)
            orphan = False
        elif not orphan:
            return False, f"fetch failed: {fetch.stderr.strip()[:300]}"
        count = _write_host_claims(cache, host, claims)
        _git(["add", "-A", "--", "."], cwd=cache)
        staged = _git(["diff", "--cached", "--quiet"], cwd=cache).returncode != 0
        if not staged and not orphan:
            done = True
        else:
            # "[skip ci]" must LEAD the message: Cloudflare Pages honours it only as a prefix.
            if staged and not _commit(cache, f"[skip ci] chore(session-claims): {host} {count} claim(s)"):
                return False, "commit failed"
            push = _git(["push", "--quiet", "origin", f"HEAD:refs/heads/{branch}"], cwd=cache, timeout=NET_TIMEOUT)
            if push.returncode != 0:
                _log(f"{repo}: push attempt {attempt} failed: {push.stderr.strip()[:300]}")
                continue
            done = True
        if done:
            if not claims:
                shutil.rmtree(cache, ignore_errors=True)  # nothing left here: stop fetching it
            return True, f"{count} claim(s) for {host}"
    return False, "push failed after 3 attempts"


def publish(cfg: dict) -> tuple[bool, str]:
    branch, host = cfg["branch"], _host()
    groups = claims_by_repo(_live_states())
    repos_dir = _home() / "repos"
    for cache in sorted(repos_dir.iterdir()) if repos_dir.is_dir() else []:
        url = _git(["config", "--get", "remote.origin.url"], cwd=cache).stdout.strip()
        repo = normalize_repo(url)
        if repo and repo not in groups:
            groups[repo] = {"remote": url, "tops": [], "claims": {}}  # clear what we published before
    results = []
    for repo, entry in sorted(groups.items()):
        if not entry["remote"]:
            results.append((False, f"{repo}: no remote URL recorded"))
            continue
        guard = next((g for g in (deploy_guard(t, branch) for t in entry["tops"] if Path(t).is_dir()) if g), "")
        if guard:
            results.append((True, f"{repo}: skipped, {guard}"))
            continue
        claims = entry["claims"]
        if claims and not repo_is_private(repo):
            claims = {sid: {**c, "title": ""} for sid, c in claims.items()}
        ok, message = _publish_repo(repo, entry["remote"], branch, host, claims)
        results.append((ok, f"{repo}: {message}"))
    if not results:
        return True, "no local sessions to publish"
    return all(ok for ok, _ in results), "; ".join(m for _, m in results)


def cmd_publish(args) -> int:
    cfg = load_config()
    if not cfg:
        return 0
    with _lock() as acquired:
        if not acquired:
            return 0  # another publisher is running; the next heartbeat catches up
        try:
            ok, message = publish(cfg)
        except Exception as exc:  # background job: log, never raise
            ok, message = False, f"{type(exc).__name__}: {exc}"
        _log(("ok " if ok else "FAILED ") + message)
    return 0 if ok else 1


# ---------------------------------------------------------------- install / status


def _hook_command() -> str:
    return f"python3 {shlex.quote(str(SCRIPT))} hook"


def _strip_our_hooks(settings: dict) -> int:
    removed = 0
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return 0
    for event in list(hooks):
        groups = hooks[event]
        if not isinstance(groups, list):
            continue
        kept_groups = []
        for group in groups:
            entries = group.get("hooks", []) if isinstance(group, dict) else []
            if not isinstance(entries, list):
                kept_groups.append(group)
                continue
            kept = [e for e in entries if not (isinstance(e, dict) and HOOK_MARKER in str(e.get("command", "")))]
            removed += len(entries) - len(kept)
            if kept:
                group["hooks"] = kept
                kept_groups.append(group)
            elif not entries:
                kept_groups.append(group)
        if kept_groups:
            hooks[event] = kept_groups
        else:
            del hooks[event]
    if not hooks:
        settings.pop("hooks", None)
    return removed


def _add_our_hooks(settings: dict) -> None:
    hooks = settings.setdefault("hooks", {})
    command = _hook_command()
    for event in HOOK_EVENTS:
        group: dict = {"hooks": [{"type": "command", "command": command, "timeout": 10}]}
        if event == "PostToolUse":
            group = {"matcher": POST_TOOL_MATCHER, **group}
        hooks.setdefault(event, []).append(group)


def _save_settings(path: Path, settings: dict) -> Path | None:
    backup = None
    if path.exists():
        backup = path.with_name(f"{path.name}.bak-session-claims-{int(time.time())}")
        shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return backup


def cmd_install(args) -> int:
    if os.environ.get("CLAUDE_CODE_REMOTE") == "true" and not args.force:
        print("This is a cloud session; cloud sessions are visible to the routine already.")
        print("Run install on your own machine (or pass --force).")
        return 1
    settings_file = _settings_path()
    settings = _read_json(settings_file, default=None) if settings_file.exists() else {}
    if not isinstance(settings, dict):
        print(f"{settings_file} does not parse as a JSON object; refusing to edit it.")
        return 1
    removed = _strip_our_hooks(settings)
    _add_our_hooks(settings)
    cfg = {"enabled": True, "branch": args.branch, "include_title": not args.no_title}
    if args.dry_run:
        print(json.dumps({"config": cfg, "hooks": settings.get("hooks", {})}, indent=2))
        return 0
    _write_json(_home() / "config.json", cfg)
    backup = _save_settings(settings_file, settings)
    print(f"config:   {_home() / 'config.json'} (branch {args.branch} in each repo you work in)")
    print(f"hooks:    {settings_file} ({', '.join(HOOK_EVENTS)}; {removed} previous entries replaced)")
    if backup:
        print(f"backup:   {backup}")
    print("New Claude sessions on this machine now publish claims to the repo they work in.")
    print("Already-open sessions start on their next restart. Check with: session-claims.py status")
    return 0


def cmd_uninstall(args) -> int:
    settings_file = _settings_path()
    settings = _read_json(settings_file, default=None) if settings_file.exists() else {}
    if not isinstance(settings, dict):
        print(f"{settings_file} does not parse as a JSON object; refusing to edit it.")
        return 1
    removed = _strip_our_hooks(settings)
    if removed:
        backup = _save_settings(settings_file, settings)
        print(f"removed {removed} hook entries from {settings_file} (backup {backup})")
    else:
        print(f"no session-claims hooks found in {settings_file}")
    cfg_file = _home() / "config.json"
    if cfg_file.exists():
        cfg_file.unlink()
        print(f"removed {cfg_file}")
    if args.purge:
        shutil.rmtree(_home(), ignore_errors=True)
        print(f"purged {_home()} (already-published claims expire on their own)")
    return 0


def cmd_status(args) -> int:
    cfg = load_config()
    settings_file = _settings_path()
    settings = _read_json(settings_file, default={})
    hooks = settings.get("hooks") if isinstance(settings, dict) else None
    wired = sorted(
        event
        for event, groups in (hooks if isinstance(hooks, dict) else {}).items()
        for group in (groups if isinstance(groups, list) else [])
        if isinstance(group, dict)
        for entry in (group.get("hooks") if isinstance(group.get("hooks"), list) else [])
        if isinstance(entry, dict) and HOOK_MARKER in str(entry.get("command", ""))
    )
    states = sorted((_home() / "state").glob("*.json")) if (_home() / "state").is_dir() else []
    print(f"config:  {json.dumps(cfg) if cfg else 'none (hook is a no-op)'}")
    print(f"hooks:   {', '.join(wired) if wired else 'not installed'} in {settings_file}")
    print(f"claims:  {len(states)} local session state file(s) under {_home() / 'state'}")
    repos_dir = _home() / "repos"
    cached = sorted(d.name.replace("__", "/") for d in repos_dir.iterdir()) if repos_dir.is_dir() else []
    print(f"repos:   {', '.join(cached) if cached else 'none published yet'}")
    log = _home() / "publish.log"
    if log.exists():
        tail = log.read_text(encoding="utf-8").splitlines()[-5:]
        print("publish.log (last 5):")
        for line in tail:
            print(f"  {line}")
    return 0


# ---------------------------------------------------------------- routine readers


def classify_claim(claim: dict, now: datetime) -> str:
    hb = _parse_iso(claim.get("heartbeat_at"))
    if hb is None:
        return "expired"
    age_h = (now - hb).total_seconds() / 3600
    dirty = any(ws.get("dirty_files") for ws in claim.get("workspaces", []))
    if claim.get("status") != "ended" and age_h <= LIVE_TTL_H:
        return "live"
    if dirty and age_h <= DIRTY_TTL_H:
        return "dirty-recent"
    return "expired"


def _load_claims(claims_dir: str | None, repo_dir: str | None, ref: str | None) -> list[dict]:
    claims: list[dict] = []
    if claims_dir:
        for path in sorted(Path(claims_dir).glob("claims/*/*.json")):
            data = _read_json(path)
            if isinstance(data, dict):
                claims.append(data)
        return claims
    listing = _git(["ls-tree", "-r", "--name-only", ref, "--", "claims"], cwd=repo_dir)
    if listing.returncode != 0:
        raise RuntimeError(f"cannot read {ref} in {repo_dir}: {listing.stderr.strip()}")
    for name in listing.stdout.splitlines():
        if not name.endswith(".json"):
            continue
        blob = _git(["show", f"{ref}:{name}"], cwd=repo_dir)
        with contextlib.suppress(ValueError):
            data = json.loads(blob.stdout)
            if isinstance(data, dict):
                claims.append(data)
    return claims


def claim_as_other(claim: dict, state: str) -> dict:
    workspaces = [
        {
            "repo": ws.get("repo", ""),
            "branch": ws.get("branch", ""),
            "files": sorted(set(ws.get("dirty_files", [])) | set(ws.get("branch_files", []))),
        }
        for ws in claim.get("workspaces", [])
    ]
    repos = [w["repo"] for w in workspaces]
    return {
        "id": f"claim:{claim.get('host', '?')}/{claim.get('session_id', '?')}",
        "kind": "claim",
        "state": state,
        "title": claim.get("title", ""),
        "heartbeat_at": claim.get("heartbeat_at", ""),
        "workspaces": workspaces,
        "refs": extract_refs(claim.get("title", ""), repos),
        "sessions": [],
    }


def cmd_active(args) -> int:
    if not args.claims_dir and not (args.repo_dir and args.ref):
        print("active needs --claims-dir, or --repo-dir with --ref", file=sys.stderr)
        return 2
    now = _parse_iso(args.now) if args.now else _now()
    try:
        claims = _load_claims(args.claims_dir, args.repo_dir, args.ref)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    rows = []
    for claim in claims:
        state = classify_claim(claim, now)
        if state == "expired" and not args.include_expired:
            continue
        rows.append(claim_as_other(claim, state) if args.as_others else {"state": state, **claim})
    print(json.dumps(rows, indent=2, sort_keys=True))
    return 0


_SESSION_RE = re.compile(r"session_[A-Za-z0-9]+")


def git_signals(repo_dir: str, since_hours: float, fetch: bool) -> list[dict]:
    if fetch:
        # Every branch tip, bounded: the window only needs recent history, and
        # origin/<default> at this depth still covers it for the --not exclusion.
        _git(
            ["fetch", "--quiet", "--prune", "--depth=100", "origin", "+refs/heads/*:refs/remotes/origin/*"],
            cwd=repo_dir,
            timeout=NET_TIMEOUT,
        )
    repo = _origin_repo(repo_dir) or ""
    top = Path(repo_dir)
    base = _default_ref(top) or "origin/main"
    cutoff = _now() - timedelta(hours=since_hours)
    refs = _git(
        ["for-each-ref", "--format=%(refname:short)%09%(committerdate:iso-strict)", "refs/remotes/origin"],
        cwd=repo_dir,
    )
    out: list[dict] = []
    for line in refs.stdout.splitlines():
        name, _, date = line.partition("\t")
        if name in (base, "origin/HEAD", "origin", f"origin/{DEFAULT_BRANCH}") or not name.startswith("origin/"):
            continue
        tip_at = _parse_iso(date)
        if tip_at is None or tip_at < cutoff:
            continue
        log = _git(
            [
                "log",
                "--no-merges",
                f"--since={_iso(cutoff)}",
                "--format=%x1e%H%x1f%cI%x1f%(trailers:key=Claude-Session,valueonly,separator=%x2C)",
                "--name-only",
                name,
                "--not",
                base,
            ],
            cwd=repo_dir,
        )
        commits, files, sessions = [], set(), set()
        for chunk in log.stdout.split("\x1e"):
            if not chunk.strip():
                continue
            header, _, body = chunk.partition("\n")
            sha, _, rest = header.partition("\x1f")
            at, _, trailer = rest.partition("\x1f")
            found = set(_SESSION_RE.findall(trailer))
            sessions |= found
            changed = [p for p in body.splitlines() if p.strip()]
            files.update(changed)
            commits.append({"sha": sha[:12], "at": at, "sessions": sorted(found)})
        if not commits:
            continue
        branch = name[len("origin/") :]
        out.append(
            {
                "id": f"git:{repo}:{branch}",
                "kind": "git-branch",
                "title": f"{len(commits)} commit(s) on {branch} in the last {since_hours:g}h",
                "last_commit_at": _iso(tip_at),
                "workspaces": [{"repo": repo, "branch": branch, "files": sorted(files)}],
                "refs": [],
                "sessions": sorted(sessions),
                "commits": commits[:20],
            }
        )
    return out


def _fetch_branches(top: Path | str, branches: list[str], depth: int | None = None, unshallow=False):
    """Fetch named branches into origin/* explicitly (cloud clones are shallow)."""
    specs = [f"+refs/heads/{b}:refs/remotes/origin/{b}" for b in branches if b]
    args = ["fetch", "--quiet"]
    if unshallow:
        args.append("--unshallow")
    elif depth:
        args.append(f"--depth={depth}")
    return _git([*args, "origin", *specs], cwd=top, timeout=NET_TIMEOUT)


def _strip_origin(ref: str) -> str:
    return ref[len("origin/") :] if ref.startswith("origin/") else ref


def branch_files(top: Path | str, branch: str, base: str | None = None, fetch: bool = False) -> dict:
    """Files `branch` changes since its merge-base with the default branch.

    A shallow clone may lack the merge-base, so a failed diff deepens, then
    unshallows, before giving up. Giving up returns files=None: the caller must
    treat that session as not checkable, never as "touches nothing".
    """
    top = Path(top)
    name = _strip_origin(branch)
    base = base or _default_ref(top) or "origin/main"
    if fetch:
        _fetch_branches(top, [name, _strip_origin(base)], depth=200)

    def diff():
        return _git(["diff", "--name-only", f"{base}...origin/{name}"], cwd=top)

    res = diff()
    if res.returncode != 0 and fetch:
        shallow = _git(["rev-parse", "--is-shallow-repository"], cwd=top).stdout.strip() == "true"
        _fetch_branches(top, [name, _strip_origin(base)], unshallow=shallow)
        res = diff()
    if res.returncode != 0:
        return {"base": base, "branch": f"origin/{name}", "files": None, "error": res.stderr.strip()[:300]}
    return {"base": base, "branch": f"origin/{name}", "files": [p for p in res.stdout.splitlines() if p]}


def evidence(repo_dir: str, since_hours: float, branch: str = DEFAULT_BRANCH) -> dict:
    """One repo's live claims and recent git activity, as `check` others.

    claims_branch is "present", "absent" (nobody has published claims here) or
    "error: ..." (unreadable). A caller must treat "error" as not checkable.
    """
    repo = _origin_repo(repo_dir) or ""
    others: list[dict] = []
    heads = _git(["ls-remote", "--heads", "origin", branch], cwd=repo_dir, timeout=NET_TIMEOUT)
    if heads.returncode != 0:
        status = f"error: {heads.stderr.strip()[:200]}"
    elif not heads.stdout.strip():
        status = "absent"
    else:
        spec = f"+refs/heads/{branch}:refs/remotes/origin/{branch}"
        fetch = _git(["fetch", "--quiet", "--depth=1", "origin", spec], cwd=repo_dir, timeout=NET_TIMEOUT)
        if fetch.returncode != 0:
            status = f"error: {fetch.stderr.strip()[:200]}"
        else:
            try:
                claims = _load_claims(None, repo_dir, f"origin/{branch}")
                status = "present"
            except RuntimeError as exc:
                claims, status = [], f"error: {exc}"
            now = _now()
            for claim in claims:
                state = classify_claim(claim, now)
                if state != "expired":
                    others.append(claim_as_other(claim, state))
    live = len(others)
    others += git_signals(repo_dir, since_hours, fetch=True)
    return {"repo": repo, "claims_branch": status, "live_claims": live, "others": others}


def cmd_evidence(args) -> int:
    result = evidence(args.repo_dir, args.since_hours)
    print(json.dumps(result, indent=2))
    return 2 if result["claims_branch"].startswith("error") else 0


def cmd_git_signals(args) -> int:
    print(json.dumps(git_signals(args.repo_dir, args.since_hours, args.fetch), indent=2))
    return 0


def cmd_branch_files(args) -> int:
    result = branch_files(args.repo_dir, args.branch, args.base, args.fetch)
    print(json.dumps(result))
    return 0 if result["files"] is not None else 2


# ---------------------------------------------------------------------- the check


def _overlaps(cand: dict, other: dict, cand_id: str) -> list[dict]:
    """Every reason `other` collides with `cand`. Empty list means clear."""
    reasons: list[dict] = []
    if other.get("kind") == "git-branch":
        sessions = set(other.get("sessions") or [])
        if sessions and sessions <= {cand_id}:
            return []  # the candidate's own commits
    for cw in cand.get("workspaces", []):
        for ow in other.get("workspaces", []):
            if (cw.get("repo") or "").lower() != (ow.get("repo") or "").lower() or not cw.get("repo"):
                continue
            repo = cw["repo"].lower()
            cb, ob = (cw.get("branch") or "").lower(), (ow.get("branch") or "").lower()
            if cb and cb == ob and cb not in DEFAULT_BRANCH_NAMES:
                reasons.append({"rule": "same-branch", "repo": repo, "detail": cw["branch"]})
            cf, of = set(cw.get("files") or []), set(ow.get("files") or [])
            shared = sorted(cf & of)
            if shared:
                reasons.append({"rule": "file-overlap", "repo": repo, "detail": shared[:10]})
            elif not cf or not of:
                reasons.append(
                    {"rule": "same-repo-no-file-info", "repo": repo, "detail": "files unknown on one side"}
                )
    shared_refs = sorted(set(cand.get("refs") or []) & set(other.get("refs") or []))
    if shared_refs:
        reasons.append({"rule": "same-pr", "repo": "", "detail": shared_refs})
    return reasons


HARD_RULES = {"same-branch", "file-overlap", "same-pr"}


def _with_refs(entity: dict) -> dict:
    """Add the PR references named in an entity's title/summary to its explicit refs."""
    repos = [w.get("repo", "") for w in entity.get("workspaces", []) if w.get("repo")]
    text = f"{entity.get('title', '')} {entity.get('summary', '')}"
    return {**entity, "refs": sorted(set(entity.get("refs") or []) | set(extract_refs(text, repos)))}


def run_check(candidates: list[dict], others: list[dict], self_id: str = "", accept_unknown=()) -> dict:
    candidates = [_with_refs(c) for c in candidates]
    pool = [_with_refs(o) for o in others if o.get("id") and o.get("id") != self_id]
    accepted: list[str] = []
    results = []
    for cand in sorted(candidates, key=lambda c: (c.get("priority", 99), c.get("id", ""))):
        cid = cand.get("id", "")
        reasons = []
        for other in pool:
            if other.get("id") == cid:
                continue
            for reason in _overlaps(cand, other, cid):
                reasons.append({**reason, "with": other["id"], "kind": other.get("kind", "")})
        rules = {r["rule"] for r in reasons}
        if rules & HARD_RULES:
            verdict = "conflict"
        elif rules:
            verdict = "unknown"
        else:
            verdict = "clear"
        resume = verdict == "clear" or (verdict == "unknown" and cid in accept_unknown)
        if resume:
            accepted.append(cid)
            pool.append({**cand, "kind": "accepted-candidate"})
        results.append({"id": cid, "verdict": verdict, "resume": resume, "reasons": reasons})
    return {"results": results, "accepted": accepted}


def _load_list(path: str, key: str) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get(key, [])
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a list or an object with '{key}'")
    return data


def cmd_check(args) -> int:
    try:
        candidates = _load_list(args.input, "candidates")
        base = json.loads(Path(args.input).read_text(encoding="utf-8"))
        others = list(base.get("others", [])) if isinstance(base, dict) else []
        for extra in args.others or []:
            others.extend(_load_list(extra, "others"))
    except (OSError, ValueError) as exc:
        print(f"check: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(run_check(candidates, others, args.self_id, set(args.accept_unknown or [])), indent=2))
    return 0


# ---------------------------------------------------------------------- self-test


def _ws(repo, branch, files):
    return {"repo": repo, "branch": branch, "files": files}


def _check_cases(check=run_check) -> list[str]:
    """Return a list of failure messages (empty == all rules behave)."""
    fails: list[str] = []

    def verdict(cand, others, **kw):
        return check([cand], others, **kw)["results"][0]["verdict"]

    a = {"id": "session_A", "workspaces": [_ws("o/r", "feat/a", ["src/a.py"])]}
    cases = [
        ("same branch", a, [{"id": "x", "workspaces": [_ws("o/r", "feat/a", ["src/z.py"])]}], "conflict"),
        ("file overlap", a, [{"id": "x", "workspaces": [_ws("o/r", "feat/b", ["src/a.py"])]}], "conflict"),
        ("disjoint", a, [{"id": "x", "workspaces": [_ws("o/r", "feat/b", ["src/b.py"])]}], "clear"),
        ("other repo", a, [{"id": "x", "workspaces": [_ws("o/other", "feat/a", ["src/a.py"])]}], "clear"),
        (
            "both on main, disjoint",
            {"id": "session_M", "workspaces": [_ws("o/r", "main", ["a"])]},
            [{"id": "x", "workspaces": [_ws("o/r", "main", ["b"])]}],
            "clear",
        ),
        ("no file info", a, [{"id": "x", "workspaces": [_ws("o/r", "feat/b", [])]}], "unknown"),
        (
            "same PR",
            {**a, "refs": ["o/r#696"]},
            [{"id": "x", "workspaces": [], "refs": ["o/r#696"]}],
            "conflict",
        ),
        (
            "same PR named in summaries",
            {**a, "summary": "fix CI on #743"},
            [{"id": "x", "summary": "merging fleet PRs; #743 build fails", "workspaces": [_ws("o/r", "", [])]}],
            "conflict",
        ),
        (
            "own commits",
            a,
            [{"id": "g", "kind": "git-branch", "sessions": ["session_A"], "workspaces": [_ws("o/r", "feat/a", ["src/a.py"])]}],
            "clear",
        ),
        (
            "someone else on my branch",
            a,
            [
                {
                    "id": "g",
                    "kind": "git-branch",
                    "sessions": ["session_A", "session_B"],
                    "workspaces": [_ws("o/r", "feat/a", ["src/a.py"])],
                }
            ],
            "conflict",
        ),
    ]
    for name, cand, others, want in cases:
        got = verdict(cand, others)
        if got != want:
            fails.append(f"check[{name}]: want {want}, got {got}")
    if verdict(a, [{"id": "session_SELF", "workspaces": [_ws("o/r", "feat/a", ["src/a.py"])]}], self_id="session_SELF") != "clear":
        fails.append("check[self excluded]: the routine's own session must be ignored")
    two = check(
        [
            {"id": "c1", "priority": 1, "workspaces": [_ws("o/r", "feat/1", ["shared.py"])]},
            {"id": "c2", "priority": 2, "workspaces": [_ws("o/r", "feat/2", ["shared.py"])]},
        ],
        [],
    )
    if two["accepted"] != ["c1"]:
        fails.append(f"check[candidate vs candidate]: want accepted [c1], got {two['accepted']}")
    unk = check([{"id": "u", "workspaces": [_ws("o/r", "feat/u", ["f"])]}], [{"id": "x", "workspaces": [_ws("o/r", "b", [])]}], accept_unknown={"u"})
    if unk["accepted"] != ["u"]:
        fails.append("check[accept-unknown]: an explicitly accepted unknown must resume")
    return fails


def _unit_cases() -> list[str]:
    fails: list[str] = []
    for url, want in (
        ("git@github.com:mcorbett51090/RavenClaude.git", "mcorbett51090/ravenclaude"),
        ("https://github.com/o/r", "o/r"),
        ("https://x-access-token:abc@github.com/o/r.git", "o/r"),
        ("ssh://git@github.com/o/r.git", "o/r"),
        ("http://local_proxy@127.0.0.1:43210/git/mcorbett51090/RavenPower-Website", "mcorbett51090/ravenpower-website"),
        ("https://gitlab.com/o/r.git", None),
    ):
        if normalize_repo(url) != want:
            fails.append(f"normalize_repo({url!r}) != {want!r}")
    refs = extract_refs("fix mcorbett51090/RavenClaude#12, see #696 and step #2", ["o/r"])
    if refs != ["mcorbett51090/ravenclaude#12", "o/r#696"]:
        fails.append(f"extract_refs: got {refs}")
    now = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)

    def claim(hours_ago, status="active", dirty=()):
        return {
            "heartbeat_at": _iso(now - timedelta(hours=hours_ago)),
            "status": status,
            "workspaces": [{"dirty_files": list(dirty)}],
        }

    for name, c, want in (
        ("fresh", claim(1), "live"),
        ("stale clean", claim(8), "expired"),
        ("stale dirty", claim(8, dirty=["a"]), "dirty-recent"),
        ("ended clean", claim(1, status="ended"), "expired"),
        ("ended dirty", claim(1, status="ended", dirty=["a"]), "dirty-recent"),
        ("ancient dirty", claim(72, dirty=["a"]), "expired"),
    ):
        if classify_claim(c, now) != want:
            fails.append(f"classify_claim[{name}]: want {want}, got {classify_claim(c, now)}")
    secret = "deploy with ghp_" + "a" * 36 + " please"
    scrubbed = make_title(secret)
    if scrubbed is None or "ghp_" in scrubbed or "[REDACTED]" not in scrubbed:
        fails.append(f"make_title did not scrub a GitHub token: {scrubbed!r}")
    saved_vis = os.environ.get("RAVENCLAUDE_SESSION_CLAIMS_VISIBILITY")
    try:
        os.environ["RAVENCLAUDE_SESSION_CLAIMS_VISIBILITY"] = "o/priv=private,o/pub=public"
        if not repo_is_private("o/priv") or repo_is_private("o/pub") or repo_is_private("o/unlisted"):
            fails.append("repo_is_private: a mapped override must decide, and an unlisted repo counts as public")
    finally:
        if saved_vis is None:
            os.environ.pop("RAVENCLAUDE_SESSION_CLAIMS_VISIBILITY", None)
        else:
            os.environ["RAVENCLAUDE_SESSION_CLAIMS_VISIBILITY"] = saved_vis
    if _porcelain_paths(" M a.py\0R  new.py\0old.py\0?? n.txt\0") != ["a.py", "new.py", "n.txt"]:
        fails.append("_porcelain_paths mis-parsed a rename")
    return fails


def _sh(cmd: list[str], cwd: Path) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t"}
    env["GIT_COMMITTER_EMAIL"] = "t@t"
    return subprocess.run(cmd, cwd=cwd, env=env, check=True, capture_output=True, text=True).stdout


def _hook(payload: dict, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "hook"], input=json.dumps(payload), capture_output=True, text=True, env=env
    )


def _make_repo(tmp: Path, name: str, files: dict[str, str]) -> Path:
    """A bare remote reachable as https://github.com/acme/<name>.git plus a working clone."""
    bare = tmp / f"{name}.git"
    _sh(["git", "init", "--quiet", "--bare", "-b", "main", str(bare)], tmp)
    url = f"https://github.com/acme/{name}.git"
    with open(os.environ["GIT_CONFIG_GLOBAL"], "a") as fh:
        fh.write(f'[url "{bare}"]\n\tinsteadOf = {url}\n')
    work = tmp / name
    _sh(["git", "clone", "--quiet", url, str(work)], tmp)
    for rel, text in {"README.md": "x\n", **files}.items():
        (work / rel).write_text(text)
    _sh(["git", "add", "."], work)
    _sh(["git", "commit", "--quiet", "-m", "init"], work)
    _sh(["git", "push", "--quiet", "origin", "HEAD:main"], work)
    _sh(["git", "fetch", "--quiet", "origin"], work)
    _sh(["git", "remote", "set-head", "origin", "main"], work)
    return work


def _remote_claims(tmp: Path, name: str, label: str) -> list[dict]:
    reader = tmp / f"reader-{name}-{label}"
    _sh(["git", "clone", "--quiet", "--branch", DEFAULT_BRANCH, f"https://github.com/acme/{name}.git", str(reader)], tmp)
    return _load_claims(None, str(reader), "HEAD")


def _has_claims_branch(tmp: Path, name: str) -> bool:
    return DEFAULT_BRANCH in _sh(["git", "ls-remote", "--heads", f"https://github.com/acme/{name}.git"], tmp)


def _git_cases(tmp: Path) -> list[str]:
    fails: list[str] = []
    os.environ["RAVENCLAUDE_SESSION_CLAIMS_HOME"] = str(tmp / "home")
    os.environ["RAVENCLAUDE_SESSION_CLAIMS_HOST"] = "testhost"
    os.environ["CLAUDE_CONFIG_DIR"] = str(tmp / "claude")
    os.environ["GIT_CONFIG_GLOBAL"] = str(tmp / "gitconfig")
    os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
    os.environ["RAVENCLAUDE_SESSION_CLAIMS_VISIBILITY"] = "acme/widgets=private,acme/gadgets=public"
    os.environ.pop("CLAUDE_CODE_REMOTE", None)
    Path(os.environ["GIT_CONFIG_GLOBAL"]).write_text("")

    widgets = _make_repo(tmp, "widgets", {})
    allowed = json.dumps({"git": {"deploymentEnabled": {"ravenclaude/*": False}}})
    gadgets = _make_repo(tmp, "gadgets", {"vercel.json": allowed})
    sprockets = _make_repo(tmp, "sprockets", {"vercel.json": json.dumps({"crons": []})})
    _sh(["git", "checkout", "--quiet", "-b", "feat/x"], widgets)
    (widgets / "src.py").write_text("print(1)\n")
    _sh(["git", "add", "."], widgets)
    trailer = "Claude-Session: https://claude.ai/code/session_01Other"
    _sh(["git", "commit", "--quiet", "-m", f"feat: x\n\n{trailer}"], widgets)
    _sh(["git", "push", "--quiet", "origin", "feat/x"], widgets)

    # deploy_guard: Vercel must exclude the branch; other hosts honour the [skip ci] prefix.
    for label, cfg_text, want_ok in (
        ("no vercel.json", None, True),
        ("deployments off", json.dumps({"git": {"deploymentEnabled": False}}), True),
        ("branch excluded", json.dumps({"git": {"deploymentEnabled": {DEFAULT_BRANCH: False}}}), True),
        ("glob excluded", allowed, True),
        ("glob overridden", json.dumps({"git": {"deploymentEnabled": {"ravenclaude/*": False, "*": True}}}), False),
        ("no exclusion", json.dumps({"crons": []}), False),
        ("unparseable", "{", False),
    ):
        d = tmp / f"guard-{abs(hash(label))}"
        d.mkdir()
        if cfg_text is not None:
            (d / "vercel.json").write_text(cfg_text)
        if (deploy_guard(d) == "") != want_ok:
            fails.append(f"deploy_guard[{label}]: want {'ok' if want_ok else 'blocked'}, got {deploy_guard(d)!r}")

    sig = git_signals(str(widgets), since_hours=6, fetch=False)
    if not sig or sig[0]["workspaces"][0]["files"] != ["src.py"] or sig[0]["sessions"] != ["session_01Other"]:
        fails.append(f"git_signals: unexpected {sig}")
    snap = snapshot_workspace(str(widgets))
    if not snap or snap["repo"] != "acme/widgets" or snap["branch_files"] != ["src.py"]:
        fails.append(f"snapshot_workspace: unexpected {snap}")

    _write_json(_home() / "config.json", {"enabled": True, "branch": DEFAULT_BRANCH})
    env = {**os.environ, "RAVENCLAUDE_SESSION_CLAIMS_INLINE": "1"}

    # Cloud sessions: a silent no-op that writes nothing.
    cloud = _hook({"hook_event_name": "SessionStart", "session_id": "s-1", "cwd": str(widgets)}, {**env, "CLAUDE_CODE_REMOTE": "true"})
    if cloud.returncode != 0 or cloud.stdout or _state_path("s-1").exists():
        fails.append("hook in a cloud session must be a silent no-op")

    # A session in a private repo: its claim lands in THAT repo, with its title.
    start = _hook({"hook_event_name": "SessionStart", "session_id": "s-1", "cwd": str(widgets)}, env)
    if start.returncode != 0 or start.stdout:
        fails.append(f"hook must exit 0 with empty stdout (rc={start.returncode}, out={start.stdout!r})")
    _hook({"hook_event_name": "UserPromptSubmit", "session_id": "s-1", "cwd": str(widgets), "prompt": "build the analytics page"}, env)
    if not _has_claims_branch(tmp, "widgets"):
        log = (_home() / "publish.log").read_text() if (_home() / "publish.log").exists() else ""
        fails.append(f"publish did not create the claims branch in acme/widgets (log: {log})")
    else:
        claim = next((c for c in _remote_claims(tmp, "widgets", "1") if c.get("session_id") == "s-1"), {})
        if claim.get("title") != "build the analytics page":
            fails.append(f"a private repo's claim must keep its title, got {claim.get('title')!r}")
        # Named literally: reusing LOCAL_ONLY_FIELDS here would let an emptied constant pass.
        leaked = [k for w in claim.get("workspaces", []) for k in ("top", "remote_url") if k in w]
        if leaked:
            fails.append(f"local-only fields were published: {leaked}")

    # The same session moves to a public repo: a separate claim there, untitled, naming only that repo.
    state = _read_json(_state_path("s-1"))
    state["published_at"] = ""
    _write_json(_state_path("s-1"), state)
    _hook({"hook_event_name": "PostToolUse", "session_id": "s-1", "cwd": str(gadgets)}, env)
    if not _has_claims_branch(tmp, "gadgets"):
        fails.append("publish did not create the claims branch in acme/gadgets")
    else:
        claim = next((c for c in _remote_claims(tmp, "gadgets", "1") if c.get("session_id") == "s-1"), {})
        repos = {w.get("repo") for w in claim.get("workspaces", [])}
        if claim.get("title") != "" or repos != {"acme/gadgets"}:
            fails.append(f"public-repo claim must be untitled and name only acme/gadgets: {claim}")
    claim = next((c for c in _remote_claims(tmp, "widgets", "2") if c.get("session_id") == "s-1"), {})
    if {w.get("repo") for w in claim.get("workspaces", [])} != {"acme/widgets"}:
        fails.append(f"the private repo's claim must not mention other repos: {claim}")

    # A repo whose vercel.json would build the branch gets no claims branch at all.
    _hook({"hook_event_name": "SessionStart", "session_id": "s-2", "cwd": str(sprockets)}, env)
    if _has_claims_branch(tmp, "sprockets"):
        fails.append("publish must not push the claims branch to a repo whose vercel.json would build it")

    # The routine's view of one repo: live claims plus git activity.
    ev = evidence(str(widgets), since_hours=6)
    kinds = sorted({o["kind"] for o in ev["others"]})
    if ev["claims_branch"] != "present" or ev["live_claims"] != 1 or kinds != ["claim", "git-branch"]:
        fails.append(f"evidence(widgets): unexpected {ev['claims_branch']}, {ev['live_claims']}, {kinds}")
    ev = evidence(str(sprockets), since_hours=6)
    if ev["claims_branch"] != "absent":
        fails.append(f"evidence(sprockets): want claims_branch absent, got {ev['claims_branch']}")

    # A throttled heartbeat must not publish (fast path).
    t0 = time.time()
    _hook({"hook_event_name": "PostToolUse", "session_id": "s-1", "cwd": str(widgets)}, env)
    if time.time() - t0 > 2.0:
        fails.append("throttled PostToolUse hook took over 2s")

    # Race: another host pushes to the claims branch; the next publish must still land.
    other = tmp / "other-host"
    _sh(["git", "clone", "--quiet", "--branch", DEFAULT_BRANCH, "https://github.com/acme/widgets.git", str(other)], tmp)
    (other / "claims" / "otherhost").mkdir(parents=True)
    (other / "claims" / "otherhost" / "s-9.json").write_text(json.dumps({"session_id": "s-9"}))
    _sh(["git", "add", "."], other)
    _sh(["git", "commit", "--quiet", "-m", "other host"], other)
    _sh(["git", "push", "--quiet", "origin", f"HEAD:{DEFAULT_BRANCH}"], other)
    _hook({"hook_event_name": "SessionEnd", "session_id": "s-1", "cwd": str(widgets)}, env)
    claims = _remote_claims(tmp, "widgets", "3")
    ids = sorted(c.get("session_id", "") for c in claims)
    if ids != ["s-1", "s-9"]:
        fails.append(f"claims after a concurrent push: want [s-1, s-9], got {ids}")
    mine = next((c for c in claims if c.get("session_id") == "s-1"), {})
    if mine.get("status") != "ended":
        fails.append(f"SessionEnd did not mark the claim ended: {mine}")

    # A shallow clone (as in cloud sessions) must still yield a branch's files.
    deep = tmp / "deep.git"
    _sh(["git", "init", "--quiet", "--bare", "-b", "main", str(deep)], tmp)
    seed = tmp / "seed"
    _sh(["git", "clone", "--quiet", str(deep), str(seed)], tmp)
    for i in range(12):
        (seed / f"m{i}.txt").write_text(str(i))
        _sh(["git", "add", "."], seed)
        _sh(["git", "commit", "--quiet", "-m", f"m{i}"], seed)
        if i == 2:
            _sh(["git", "branch", "old-feature"], seed)
    _sh(["git", "push", "--quiet", "origin", "main"], seed)
    _sh(["git", "checkout", "--quiet", "old-feature"], seed)
    (seed / "feature.txt").write_text("f")
    _sh(["git", "add", "."], seed)
    _sh(["git", "commit", "--quiet", "-m", "feature"], seed)
    _sh(["git", "push", "--quiet", "origin", "old-feature"], seed)
    shallow = tmp / "shallow"
    _sh(["git", "clone", "--quiet", "--depth", "1", f"file://{deep}", str(shallow)], tmp)
    got = branch_files(shallow, "old-feature", fetch=True)
    if got.get("files") != ["feature.txt"]:
        fails.append(f"branch_files on a shallow clone: want ['feature.txt'], got {got}")
    missing = branch_files(shallow, "no-such-branch", fetch=True)
    if missing.get("files") is not None:
        fails.append("branch_files must return files=None (not checkable) for an unreadable branch")

    # install refuses to rewrite a settings file it cannot parse.
    _settings_path().parent.mkdir(parents=True, exist_ok=True)
    _settings_path().write_text("{ not json")
    install_args = argparse.Namespace(branch=DEFAULT_BRANCH, no_title=False, dry_run=False, force=True)
    with open(os.devnull, "w") as devnull, contextlib.redirect_stdout(devnull):
        rc = cmd_install(install_args)
    if rc == 0 or _settings_path().read_text() != "{ not json":
        fails.append("install must refuse, and leave untouched, a settings.json that does not parse")

    # install / uninstall keep foreign hooks intact and are idempotent.
    foreign = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo keep"}]}]}}
    _write_json(_settings_path(), foreign)
    with open(os.devnull, "w") as devnull, contextlib.redirect_stdout(devnull):
        cmd_install(install_args)
        cmd_install(install_args)
    settings = _read_json(_settings_path())
    ours = sum(
        HOOK_MARKER in e.get("command", "")
        for groups in settings["hooks"].values()
        for g in groups
        for e in g["hooks"]
    )
    if ours != len(HOOK_EVENTS) or "Stop" not in settings["hooks"]:
        fails.append(f"install: want {len(HOOK_EVENTS)} entries + the foreign Stop hook, got {ours}")
    with open(os.devnull, "w") as devnull, contextlib.redirect_stdout(devnull):
        cmd_uninstall(argparse.Namespace(purge=False))
    if _read_json(_settings_path()) != foreign:
        fails.append("uninstall did not restore the original settings")
    return fails


def self_test() -> int:
    fails = _unit_cases() + _check_cases()

    # Must-fail half: a checker with the file-overlap rule removed must be caught.
    def broken(candidates, others, self_id="", accept_unknown=()):
        stripped = [{**o, "workspaces": [{**w, "files": []} for w in o.get("workspaces", [])]} for o in others]
        res = run_check(candidates, stripped, self_id, accept_unknown)
        for r in res["results"]:
            if r["verdict"] == "unknown":
                r["verdict"] = "clear"
        return res

    if not _check_cases(broken):
        fails.append("must-fail half: a checker without the file-overlap rule passed every case")

    saved = {
        k: os.environ.get(k)
        for k in (
            "RAVENCLAUDE_SESSION_CLAIMS_HOME",
            "RAVENCLAUDE_SESSION_CLAIMS_HOST",
            "RAVENCLAUDE_SESSION_CLAIMS_VISIBILITY",
            "CLAUDE_CONFIG_DIR",
            "CLAUDE_CODE_REMOTE",
            "GIT_CONFIG_GLOBAL",
            "GIT_CONFIG_NOSYSTEM",
        )
    }
    if shutil.which("git"):
        with tempfile.TemporaryDirectory(prefix="session-claims-") as tmp:
            try:
                fails += _git_cases(Path(tmp))
            except subprocess.CalledProcessError as exc:
                fails.append(f"git fixture setup failed: {exc.stderr}")
            finally:
                for key, value in saved.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
    else:
        fails.append("git not found: the publish/git-signals half could not run")
    for line in fails:
        print(f"FAIL {line}")
    print(f"session-claims self-test: {'FAILED' if fails else 'ok'} ({len(fails)} failure(s))")
    return 1 if fails else 0


# --------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("--self-test", action="store_true", help="run the self-test and exit")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("hook", help="hook entry point (reads the hook JSON on stdin)")
    p.add_argument("--event", help="event name when the payload lacks one")
    p.set_defaults(func=cmd_hook)
    sub.add_parser("publish", help="sync this host's claims").set_defaults(func=cmd_publish)

    p = sub.add_parser("install", help="add the hooks to ~/.claude/settings.json")
    p.add_argument("--branch", default=DEFAULT_BRANCH)
    p.add_argument("--no-title", action="store_true", help="do not publish the first prompt as a title")
    p.add_argument("--dry-run", action="store_true", help="print what would be written")
    p.add_argument("--force", action="store_true", help="install even inside a cloud session")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("uninstall", help="remove the hooks")
    p.add_argument("--purge", action="store_true", help="also delete local state and the cache clone")
    p.set_defaults(func=cmd_uninstall)
    sub.add_parser("status", help="show config, hooks and publish log").set_defaults(func=cmd_status)

    p = sub.add_parser("active", help="classify published claims")
    p.add_argument("--claims-dir", help="a checkout of the claims branch")
    p.add_argument("--repo-dir", help="a clone that has the claims branch fetched")
    p.add_argument("--ref", help="ref of the claims branch inside --repo-dir")
    p.add_argument("--now", help="evaluate ages at this ISO time (testing)")
    p.add_argument("--include-expired", action="store_true")
    p.add_argument("--as-others", action="store_true", help="emit the shape `check` reads")
    p.set_defaults(func=cmd_active)

    p = sub.add_parser("git-signals", help="recent commits per remote branch, as `check` others")
    p.add_argument("--repo-dir", required=True)
    p.add_argument("--since-hours", type=float, default=6)
    p.add_argument("--fetch", action="store_true", help="git fetch --prune origin first")
    p.set_defaults(func=cmd_git_signals)

    p = sub.add_parser("evidence", help="one repo's live claims + git-signals, as `check` others")
    p.add_argument("--repo-dir", required=True)
    p.add_argument("--since-hours", type=float, default=6)
    p.set_defaults(func=cmd_evidence)

    p = sub.add_parser("branch-files", help="files a branch changes vs the default branch")
    p.add_argument("--repo-dir", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--base", help="default: origin/HEAD, then origin/main")
    p.add_argument("--fetch", action="store_true")
    p.set_defaults(func=cmd_branch_files)

    p = sub.add_parser("check", help="conflict verdict per candidate")
    p.add_argument("--input", required=True, help='JSON {"candidates": [...], "others": [...]}')
    p.add_argument("--others", action="append", help="extra JSON list of others (repeatable)")
    p.add_argument("--self-id", default="", help="the routine's own session id (ignored)")
    p.add_argument("--accept-unknown", action="append", help="resume this id despite an unknown verdict")
    p.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not getattr(args, "func", None):
        parser.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

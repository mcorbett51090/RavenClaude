#!/usr/bin/env python3
"""install_launch_guard.py — installer for the claude-launch-safeguard feature (P2).

Wires the P1 decision helper (`bin/claude-launch-guard`) into the user's shell so
a `claude` launch outside a git work tree is caught BEFORE it hangs
(anthropics/claude-code#92932). This installer is a ONE-WAY DOOR the first time it
runs: it is the first phase of this feature that writes to a user's real dotfiles.
Every rollback/kill-switch discipline below exists because of that.

TWO DESIGN CONSTRAINTS CARRIED OVER FROM `install_stall_watch.py`, NOT NEGOTIABLE.

1. THE HELPER IS COPIED TO A STABLE PATH, NEVER THE VERSION-KEYED PLUGIN CACHE.
   `~/.claude/launch-guard/bin/claude-launch-guard` survives a future plugin
   version bump; a symlink into the plugin cache would not.

2. THE SHELL BLOCK IS GENERATED HERE, NEVER SHIPPED AS A COMMITTED RC FRAGMENT.
   It is written into the user's OWN rc file at install time, marker-delimited,
   so a re-run replaces it in place instead of duplicating it.

THE SINGLE MOST SAFETY-CRITICAL LINE IN THE WHOLE FEATURE: every pass-through path
in the emitted shell function calls `command claude "$@"` — NEVER a bare `claude`.
A bare recursive call would wedge the terminal in an infinite loop. Get this
right; the self-test drives it through a REAL shell, not just a syntax check.

Env var read by the emitted function (P1's contract, confirmed from its source —
NOT the plan's guess): RAVENCLAUDE_LAUNCH_GUARD=off — checked first, before
anything else, exactly like P1's own `cmd_check` does.

Allowlist file (P1's contract, confirmed from its source): a path or `*` per
line, comments (`#`) and blank lines ignored, at ~/.claude/launch-guard/allow.
The "Always allow" choice below appends to it in that exact shape.

DIRECTORY RECOMMENDATION + ONE-CLICK SWITCH (the P1 `preferred`/`recommend`
subcommands this installer's emitted function now calls). On every SAFE
launch the function writes $PWD to ~/.claude/launch-guard/last-dir — this is
the ONLY writer of that file; P1's `recommend` only reads it. On an UNSAFE
launch, the function calls `claude-launch-guard recommend` and appends its
output (up to 5 directories: preferred dirs first, then last-used, deduped)
as extra numbered menu choices after the fixed 1-4. Choosing one `cd`s the
CURRENT SHELL into that directory (this is a shell FUNCTION, not a
subprocess, so the `cd` is real and persists after `claude` exits — that is
the whole point: a subprocess cannot change its parent shell's cwd) and then
launches from there. A `cd` failure (deleted dir, permissions) falls through
to launching from the original unsafe cwd rather than silently doing
nothing — the fail-open discipline P1 documents applies here too.

Contract:
  install_launch_guard.py install [--shell zsh|bash|fish]
      Writes the managed block into the detected (or overridden) shell's rc
      file(s), staging the helper first. Backs up before every write; validates
      the resulting file with that shell's own `-n` (skips gracefully if the
      shell binary is absent); on validation failure, restores the backup and
      exits non-zero, naming the exact file and reason.
  install_launch_guard.py --check [--shell zsh|bash|fish]
      Report-only dry run. Writes nothing.
  install_launch_guard.py --uninstall [--shell zsh|bash|fish]
      Removes the fence. Restores the file to its exact pre-install byte
      content when a pristine snapshot exists (the normal case); otherwise
      best-effort strips just the marker span.
  install_launch_guard.py status
      installed (yes/no) / which shell(s) / helper staged / allowlist entry
      count. Scans every supported shell target, not just the detected one.
      Never crashes when nothing is installed.
  install_launch_guard.py --self-test
      Exercises install -> verify -> uninstall -> verify-restored against a
      SCRATCH $HOME (mktemp -d), never the real user's dotfiles.

Unknown/unrecognized shell: refuses to write anything, prints the managed
block to stdout so the user can add it by hand, exits 0 (per spec — "don't
guess a shell you don't recognize").

Portability note: the emitted function bodies are written as POSIX-ish
shell (works unmodified in bash and zsh — no bashisms, no zsh-only syntax)
and a SEPARATE native-fish function for the fish target (fish syntax is not
bash syntax; shipping bash into a .fish file would be silently broken there).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time

# --- constants ---------------------------------------------------------------

MARKER_BEGIN = "# >>> ravenclaude launch-guard >>>   (managed block — edit via install_launch_guard.py)"
MARKER_END = "# <<< ravenclaude launch-guard <<<"

PRISTINE_SUFFIX = ".ravenclaude-original"
PRISTINE_MISSING_SUFFIX = ".ravenclaude-original-missing"

HELPER_NAME = "claude-launch-guard"

# --- the emitted shell bodies (raw strings: backslashes are literal, so a
#     printf format's `\n` reaches the written file as the two-character
#     escape sequence, to be interpreted by printf at RUNTIME — not expanded
#     now) ------------------------------------------------------------------

# bash + zsh share this body verbatim: no bashisms, no zsh-only syntax. `local`
# and `read -r` and `case` all work identically in both.
POSIX_FUNCTION_BODY = r'''claude() {
  if [ "${RAVENCLAUDE_LAUNCH_GUARD:-}" = "off" ]; then
    command claude "$@"
    return
  fi
  local _rc_g="$HOME/.claude/launch-guard/bin/claude-launch-guard"
  if [ ! -x "$_rc_g" ]; then
    command claude "$@"
    return
  fi
  if "$_rc_g" check -- "$@"; then
    mkdir -p "$HOME/.claude/launch-guard" 2>/dev/null
    printf '%s\n' "$PWD" > "$HOME/.claude/launch-guard/last-dir" 2>/dev/null
    command claude "$@"
    return
  fi
  if [ ! -t 0 ]; then
    printf 'claude-launch-guard: WARNING — non-interactive session; launching anyway despite the above.\n' >&2
    command claude "$@"
    return
  fi
  local _rc_recs="" _rc_line="" _rc_i=0 _rc_oldifs=""
  _rc_recs="$("$_rc_g" recommend 2>/dev/null)"
  printf '\nChoose:\n  1) Just once\n  2) This session (disable the guard for this shell)\n  3) Always allow (this path, or * for everywhere)\n  4) Deny — do not launch\n' >&2
  if [ -n "$_rc_recs" ]; then
    _rc_oldifs="$IFS"
    IFS='
'
    for _rc_line in $_rc_recs; do
      _rc_i=$((_rc_i + 1))
      printf '  %d) switch to %s and launch\n' "$((4 + _rc_i))" "$_rc_line" >&2
    done
    IFS="$_rc_oldifs"
  fi
  printf 'Choice [1]: ' >&2
  local _rc_choice=""
  read -r _rc_choice
  case "$_rc_choice" in
    2)
      export RAVENCLAUDE_LAUNCH_GUARD=off
      command claude "$@"
      ;;
    3)
      printf 'Allow just this path, or always (enter * for always)? [this path]: ' >&2
      local _rc_scope=""
      read -r _rc_scope
      mkdir -p "$HOME/.claude/launch-guard" 2>/dev/null
      if [ "$_rc_scope" = "*" ]; then
        printf '*\n' >> "$HOME/.claude/launch-guard/allow"
      else
        printf '%s\n' "$PWD" >> "$HOME/.claude/launch-guard/allow"
      fi
      command claude "$@"
      ;;
    4)
      printf 'claude-launch-guard: launch cancelled.\n' >&2
      return 1
      ;;
    *)
      if [ -n "$_rc_recs" ] && [ -n "$_rc_choice" ]; then
        local _rc_j=0 _rc_target=""
        _rc_oldifs="$IFS"
        IFS='
'
        for _rc_line in $_rc_recs; do
          _rc_j=$((_rc_j + 1))
          if [ "$_rc_choice" = "$((4 + _rc_j))" ]; then
            _rc_target="$_rc_line"
          fi
        done
        IFS="$_rc_oldifs"
        if [ -n "$_rc_target" ] && [ -d "$_rc_target" ]; then
          if cd "$_rc_target" 2>/dev/null; then
            printf 'claude-launch-guard: switched to %s\n' "$_rc_target" >&2
            mkdir -p "$HOME/.claude/launch-guard" 2>/dev/null
            printf '%s\n' "$PWD" > "$HOME/.claude/launch-guard/last-dir" 2>/dev/null
            command claude "$@"
            return
          fi
          printf 'claude-launch-guard: could not switch to %s — launching anyway.\n' "$_rc_target" >&2
        fi
      fi
      command claude "$@"
      ;;
  esac
}'''

# Native fish — deliberately NOT the body above. fish has no `local`/`case`; it
# uses `set -l`/`switch`, and command substitution is `(...)`, not `$(...)`.
FISH_FUNCTION_BODY = r'''function claude
    if test "$RAVENCLAUDE_LAUNCH_GUARD" = "off"
        command claude $argv
        return
    end
    set -l rc_g "$HOME/.claude/launch-guard/bin/claude-launch-guard"
    if not test -x "$rc_g"
        command claude $argv
        return
    end
    if "$rc_g" check -- $argv
        mkdir -p "$HOME/.claude/launch-guard" 2>/dev/null
        echo "$PWD" > "$HOME/.claude/launch-guard/last-dir" 2>/dev/null
        command claude $argv
        return
    end
    if not isatty stdin
        printf 'claude-launch-guard: WARNING — non-interactive session; launching anyway despite the above.\n' >&2
        command claude $argv
        return
    end
    set -l rc_recs ("$rc_g" recommend 2>/dev/null)
    printf '\nChoose:\n  1) Just once\n  2) This session (disable the guard for this shell)\n  3) Always allow (this path, or * for everywhere)\n  4) Deny — do not launch\n' >&2
    set -l rc_i 0
    for rc_line in $rc_recs
        set rc_i (math $rc_i + 1)
        set -l rc_opt (math 4 + $rc_i)
        printf '  %d) switch to %s and launch\n' "$rc_opt" "$rc_line" >&2
    end
    printf 'Choice [1]: ' >&2
    read -l rc_choice
    switch "$rc_choice"
        case 2
            set -gx RAVENCLAUDE_LAUNCH_GUARD off
            command claude $argv
        case 3
            printf 'Allow just this path, or always (enter * for always)? [this path]: ' >&2
            read -l rc_scope
            mkdir -p "$HOME/.claude/launch-guard" 2>/dev/null
            if test "$rc_scope" = "*"
                printf '*\n' >> "$HOME/.claude/launch-guard/allow"
            else
                printf '%s\n' "$PWD" >> "$HOME/.claude/launch-guard/allow"
            end
            command claude $argv
        case 4
            printf 'claude-launch-guard: launch cancelled.\n' >&2
            return 1
        case '*'
            set -l rc_target ""
            if test -n "$rc_recs"; and test -n "$rc_choice"
                set -l rc_j 0
                for rc_line in $rc_recs
                    set rc_j (math $rc_j + 1)
                    if test "$rc_choice" = (math 4 + $rc_j)
                        set rc_target "$rc_line"
                    end
                end
            end
            if test -n "$rc_target"; and test -d "$rc_target"
                if cd "$rc_target" 2>/dev/null
                    printf 'claude-launch-guard: switched to %s\n' "$rc_target" >&2
                    mkdir -p "$HOME/.claude/launch-guard" 2>/dev/null
                    echo "$PWD" > "$HOME/.claude/launch-guard/last-dir" 2>/dev/null
                    command claude $argv
                    return
                end
                printf 'claude-launch-guard: could not switch to %s — launching anyway.\n' "$rc_target" >&2
            end
            command claude $argv
    end
end'''

# Sourced into ~/.bash_profile only when it exists and does not already source
# ~/.bashrc (macOS convention: login shells read .bash_profile, not .bashrc).
SOURCE_BASHRC_BODY = r'''[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"'''


# --- tiny helpers --------------------------------------------------------------

def home_dir() -> str:
    h = os.environ.get("HOME")
    return h if h else os.path.expanduser("~")


def zshrc_path() -> str:
    zdotdir = os.environ.get("ZDOTDIR") or home_dir()
    return os.path.join(zdotdir, ".zshrc")


def bashrc_path() -> str:
    return os.path.join(home_dir(), ".bashrc")


def bash_profile_path() -> str:
    return os.path.join(home_dir(), ".bash_profile")


def fish_function_path() -> str:
    return os.path.join(home_dir(), ".config", "fish", "functions", "claude.fish")


def helper_bin_path() -> str:
    return os.path.join(home_dir(), ".claude", "launch-guard", "bin", HELPER_NAME)


def allow_file_path() -> str:
    return os.path.join(home_dir(), ".claude", "launch-guard", "allow")


def _source_helper_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "bin", HELPER_NAME)


def render_block(body: str) -> str:
    return MARKER_BEGIN + "\n" + body + "\n" + MARKER_END + "\n"


def _has_marker(text: str) -> bool:
    return any(line.rstrip("\n") == MARKER_BEGIN for line in text.splitlines())


def _sources_bashrc(text: str) -> bool:
    if _has_marker(text):
        return True
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if "bashrc" in s and (s.startswith(".") or s.startswith("source ")):
            return True
    return False


# --- marker splice / remove ---------------------------------------------------

def splice_block(existing_text: str, block_text: str):
    """Return (new_text, replaced_bool). Replaces an existing MARKER_BEGIN..
    MARKER_END span in place; if no span is found, appends block_text (with
    exactly one blank-line separator when existing_text is non-empty)."""
    lines = existing_text.splitlines(keepends=True)
    start_idx = end_idx = None
    for i, line in enumerate(lines):
        if line.rstrip("\n") == MARKER_BEGIN:
            start_idx = i
        elif start_idx is not None and line.rstrip("\n") == MARKER_END:
            end_idx = i
            break
    if start_idx is not None and end_idx is not None:
        before = "".join(lines[:start_idx])
        after = "".join(lines[end_idx + 1:])
        return before + block_text + after, True

    if not existing_text:
        return block_text, False
    stripped = existing_text.rstrip("\n")
    return stripped + "\n\n" + block_text, False


def remove_block(text: str) -> str:
    """Best-effort marker-span strip, used only when no pristine snapshot
    exists to restore from exactly."""
    lines = text.splitlines(keepends=True)
    start = end = None
    for i, line in enumerate(lines):
        if line.rstrip("\n") == MARKER_BEGIN:
            start = i
        elif start is not None and line.rstrip("\n") == MARKER_END:
            end = i
            break
    if start is None or end is None:
        return text
    before = lines[:start]
    after = lines[end + 1:]
    if before and before[-1] == "\n":
        before = before[:-1]
    return "".join(before) + "".join(after)


# --- backup / pristine snapshot -----------------------------------------------

def _timestamped_backup(path: str):
    if not os.path.isfile(path):
        return None
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    backup_path = "%s.ravenclaude-backup-%s" % (path, ts)
    shutil.copy2(path, backup_path)
    return backup_path


def _snapshot_pristine_if_needed(path: str):
    """Record the pre-any-install state, once, the first time this path is
    ever touched. Silently a no-op on every subsequent call."""
    pristine_path = path + PRISTINE_SUFFIX
    missing_path = path + PRISTINE_MISSING_SUFFIX
    if os.path.exists(pristine_path) or os.path.exists(missing_path):
        return
    if os.path.isfile(path):
        with open(path, "rb") as fh:
            existing = fh.read()
        if _has_marker(existing.decode("utf-8", "replace")):
            # Already carries our marker with no pristine record — cannot
            # reconstruct the true original; leave no (possibly-wrong) record.
            return
        with open(pristine_path, "wb") as fh:
            fh.write(existing)
    else:
        with open(missing_path, "w", encoding="utf-8") as fh:
            fh.write("")


# --- syntax validation ---------------------------------------------------------

_VALIDATORS = {"zsh": "zsh", "bash": "bash", "fish": "fish"}


def _validate(path: str, kind: str):
    exe = _VALIDATORS.get(kind)
    if not exe or shutil.which(exe) is None:
        return True, "skipped (%s not available)" % (exe or kind)
    try:
        proc = subprocess.run([exe, "-n", path], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return True, "skipped (%s -n failed to run: %s)" % (exe, exc)
    if proc.returncode == 0:
        return True, "ok"
    return False, (proc.stderr or proc.stdout or "non-zero exit").strip()[:400]


# --- shell detection -----------------------------------------------------------

_KNOWN_SHELLS = ("zsh", "bash", "fish")


def detect_shell(override=None):
    if override:
        s = override.strip().lower()
        if s in _KNOWN_SHELLS:
            return s
        return "unknown:" + override
    shell_env = os.environ.get("SHELL", "")
    base = os.path.basename(shell_env)
    if base in _KNOWN_SHELLS:
        return base
    return "unknown:" + (base or "(unset)")


# --- staging the P1 helper ------------------------------------------------------

def stage_helper():
    home = home_dir()
    state_dir = os.path.join(home, ".claude", "launch-guard")
    bin_dir = os.path.join(state_dir, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    try:
        os.chmod(state_dir, 0o700)
    except OSError:
        pass
    src = _source_helper_path()
    if not os.path.isfile(src):
        raise SystemExit("missing source helper: %s" % src)
    dst = os.path.join(bin_dir, HELPER_NAME)
    shutil.copy2(src, dst)
    try:
        os.chmod(dst, 0o755)
    except OSError:
        pass
    return dst


# --- per-shell target resolution -----------------------------------------------

def _install_targets(shell: str):
    """[(path, validator_kind, block_text), ...] for what INSTALL should write."""
    if shell == "zsh":
        return [(zshrc_path(), "zsh", render_block(POSIX_FUNCTION_BODY))]
    if shell == "bash":
        targets = [(bashrc_path(), "bash", render_block(POSIX_FUNCTION_BODY))]
        bp = bash_profile_path()
        if os.path.isfile(bp):
            try:
                with open(bp, encoding="utf-8", errors="replace") as fh:
                    bp_text = fh.read()
            except OSError:
                bp_text = ""
            if not _sources_bashrc(bp_text):
                targets.append((bp, "bash", render_block(SOURCE_BASHRC_BODY)))
        return targets
    if shell == "fish":
        return [(fish_function_path(), "fish", render_block(FISH_FUNCTION_BODY))]
    return []


def _candidate_paths(shell: str):
    """Every path that MIGHT carry our marker for `shell` — used by uninstall
    and status, where we must look regardless of the install-time heuristics
    (e.g. bash_profile already sourcing .bashrc) that governed whether install
    wrote to it."""
    if shell == "zsh":
        return [zshrc_path()]
    if shell == "bash":
        return [bashrc_path(), bash_profile_path()]
    if shell == "fish":
        return [fish_function_path()]
    return []


# --- install / check -----------------------------------------------------------

def _install_or_check_one(path, validator_kind, block_text, check_only, results):
    exists_before = os.path.isfile(path)
    existing_text = ""
    if exists_before:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                existing_text = fh.read()
        except OSError:
            existing_text = ""
    had_marker = _has_marker(existing_text)

    if check_only:
        if had_marker:
            status = "up-to-date (managed block already present)"
        elif exists_before:
            status = "would append the managed block"
        else:
            status = "would create this file with the managed block"
        results.append((path, status))
        return True

    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    _snapshot_pristine_if_needed(path)
    backup_path = _timestamped_backup(path)

    new_text, replaced = splice_block(existing_text, block_text)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new_text)

    ok, reason = _validate(path, validator_kind)
    if not ok:
        if backup_path and os.path.isfile(backup_path):
            shutil.copy2(backup_path, path)
        elif not exists_before:
            try:
                os.remove(path)
            except OSError:
                pass
        print(
            "install_launch_guard: VALIDATION FAILED for %s: %s. Restored previous state."
            % (path, reason),
            file=sys.stderr,
        )
        results.append((path, "FAILED: %s" % reason))
        return False

    results.append((path, "replaced in place" if replaced else ("appended" if exists_before else "created")))
    return True


def cmd_install(shell_override, check_only=False):
    shell = detect_shell(shell_override)
    if shell.startswith("unknown:"):
        name = shell.split(":", 1)[1]
        print("install_launch_guard: unrecognized shell (%s) — not writing any rc file." % name)
        print("Add this function to your shell's startup file by hand:\n")
        print(render_block(POSIX_FUNCTION_BODY))
        return 0

    if not check_only:
        stage_helper()

    targets = _install_targets(shell)
    if not targets:
        print("install_launch_guard: no targets resolved for shell '%s'." % shell)
        return 1

    results = []
    ok = True
    for path, validator_kind, block_text in targets:
        ok = _install_or_check_one(path, validator_kind, block_text, check_only, results) and ok

    verb = "would be touched" if check_only else "touched"
    print("install_launch_guard: shell=%s, %d file(s) %s:" % (shell, len(results), verb))
    for path, status in results:
        print("  %s -> %s" % (path, status))
    if not check_only and ok:
        print("  helper staged -> %s" % helper_bin_path())
    return 0 if ok else 1


# --- uninstall -------------------------------------------------------------------

def _uninstall_one(path: str) -> bool:
    pristine_path = path + PRISTINE_SUFFIX
    missing_path = path + PRISTINE_MISSING_SUFFIX

    if os.path.isfile(pristine_path):
        shutil.copy2(pristine_path, path)
        try:
            os.remove(pristine_path)
        except OSError:
            pass
        try:
            os.remove(missing_path)
        except OSError:
            pass
        print("install_launch_guard: restored %s to its pre-install state." % path)
        return True

    if os.path.isfile(missing_path):
        try:
            os.remove(path)
        except OSError:
            pass
        try:
            os.remove(missing_path)
        except OSError:
            pass
        print("install_launch_guard: removed %s (it did not exist before install)." % path)
        return True

    if not os.path.isfile(path):
        print("install_launch_guard: %s does not exist — nothing to uninstall." % path)
        return True

    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    if not _has_marker(text):
        print("install_launch_guard: %s has no managed block — nothing to uninstall." % path)
        return True

    _timestamped_backup(path)
    new_text = remove_block(text)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    print(
        "install_launch_guard: removed the managed block from %s "
        "(no pristine snapshot found — best-effort strip)." % path
    )
    return True


def cmd_uninstall(shell_override):
    shell = detect_shell(shell_override)
    if shell.startswith("unknown:"):
        name = shell.split(":", 1)[1]
        print("install_launch_guard: unrecognized shell (%s) — nothing to uninstall." % name)
        return 0
    ok = True
    for path in _candidate_paths(shell):
        ok = _uninstall_one(path) and ok
    return 0 if ok else 1


# --- status ----------------------------------------------------------------------

def cmd_status_report():
    all_shells = {
        "zsh": [zshrc_path()],
        "bash": [bashrc_path(), bash_profile_path()],
        "fish": [fish_function_path()],
    }
    installed_shells = []
    for shell, paths in all_shells.items():
        for path in paths:
            if not os.path.isfile(path):
                continue
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            if _has_marker(text):
                installed_shells.append(shell)
                break

    helper_path = helper_bin_path()
    helper_staged = os.path.isfile(helper_path)

    allow_path = allow_file_path()
    allow_count = 0
    if os.path.isfile(allow_path):
        try:
            with open(allow_path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    entry = line.split("#", 1)[0].strip()
                    if entry:
                        allow_count += 1
        except OSError:
            pass

    print("claude-launch-guard status:")
    print("  installed:         %s" % ("yes" if installed_shells else "no"))
    print("  shells:            %s" % (", ".join(sorted(set(installed_shells))) if installed_shells else "(none)"))
    print("  helper staged:     %s (%s)" % ("yes" if helper_staged else "no", helper_path))
    print("  allowlist entries: %d (%s)" % (allow_count, allow_path))
    return 0


# --- self-test ----------------------------------------------------------------

def _st_fail(msgs, msg):
    msgs.append(msg)
    sys.stderr.write("SELF-TEST FAIL: %s\n" % msg)


def _run_self(args, env, cwd=None, timeout=15, input_text=None):
    return subprocess.run(
        [sys.executable, os.path.abspath(__file__)] + args,
        env=env,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        input=input_text,
    )


def _run_shell(cmd_list, env, cwd, timeout=8):
    return subprocess.run(
        cmd_list,
        env=env,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        stdin=subprocess.DEVNULL,
    )


def cmd_self_test():
    failures = []
    scratch = tempfile.mkdtemp(prefix="rc-launch-guard-selftest-")
    try:
        scratch_home = os.path.join(scratch, "home")
        os.makedirs(scratch_home, exist_ok=True)
        stub_bin = os.path.join(scratch, "bin")
        os.makedirs(stub_bin, exist_ok=True)
        stub_claude = os.path.join(stub_bin, "claude")
        with open(stub_claude, "w", encoding="utf-8") as fh:
            fh.write("#!/bin/sh\necho 'stub-claude 9.9.9'\n")
        os.chmod(stub_claude, 0o755)

        nonrepo = os.path.join(scratch, "nonrepo")
        os.makedirs(nonrepo, exist_ok=True)

        env = dict(os.environ)
        env["HOME"] = scratch_home
        env["PATH"] = stub_bin + os.pathsep + env.get("PATH", "")
        env.pop("ZDOTDIR", None)
        env.pop("RAVENCLAUDE_LAUNCH_GUARD", None)

        zshrc = os.path.join(scratch_home, ".zshrc")
        original_zshrc = "# my original zshrc\nexport FOO=bar\n"
        with open(zshrc, "w", encoding="utf-8") as fh:
            fh.write(original_zshrc)

        # --- 1. Fresh install on the zsh fixture --------------------------
        proc = _run_self(["install", "--shell", "zsh"], env)
        if proc.returncode != 0:
            _st_fail(failures, "fresh zsh install exited %d: %s" % (proc.returncode, proc.stderr))
        with open(zshrc, encoding="utf-8") as fh:
            after_first = fh.read()
        if after_first.count(MARKER_BEGIN) != 1 or after_first.count(MARKER_END) != 1:
            _st_fail(failures, "fresh install did not produce exactly one marker span")
        if "export FOO=bar" not in after_first:
            _st_fail(failures, "fresh install lost pre-existing .zshrc content")
        ok, reason = _validate(zshrc, "zsh")
        if not ok:
            _st_fail(failures, "zsh -n on fresh install failed: %s" % reason)

        def _outside_markers(text):
            lines = text.splitlines(keepends=True)
            s = e = None
            for i, ln in enumerate(lines):
                if ln.rstrip("\n") == MARKER_BEGIN:
                    s = i
                elif s is not None and ln.rstrip("\n") == MARKER_END:
                    e = i
                    break
            if s is None or e is None:
                return text, ""
            return "".join(lines[:s]), "".join(lines[e + 1:])

        before1, after1 = _outside_markers(after_first)

        # --- 2. Re-run install -> replaced in place, not duplicated -------
        proc = _run_self(["install", "--shell", "zsh"], env)
        if proc.returncode != 0:
            _st_fail(failures, "re-install exited %d: %s" % (proc.returncode, proc.stderr))
        with open(zshrc, encoding="utf-8") as fh:
            after_second = fh.read()
        if after_second.count(MARKER_BEGIN) != 1 or after_second.count(MARKER_END) != 1:
            _st_fail(failures, "re-install duplicated the marker span")
        before2, after2 = _outside_markers(after_second)
        if before1 != before2 or after1 != after2:
            _st_fail(failures, "re-install changed content OUTSIDE the marker span")

        # --- 3. Real zsh sourcing: function defined, --version returns ----
        if shutil.which("zsh"):
            t0 = time.time()
            proc = _run_shell(
                ["zsh", "-i", "-c", "type claude; command claude --version; claude --version"],
                env, nonrepo,
            )
            elapsed = time.time() - t0
            if "stub-claude 9.9.9" not in proc.stdout:
                _st_fail(failures, "real zsh: claude --version did not reach the stub (stdout=%r stderr=%r)" % (proc.stdout, proc.stderr))
            if elapsed >= 5:
                _st_fail(failures, "real zsh: claude --version took %.1fs (>=5s, possible recursion)" % elapsed)
        else:
            print("install_launch_guard self-test: zsh not on PATH — skipping real-shell zsh checks")

        # --- 4. RAVENCLAUDE_LAUNCH_GUARD=off passthrough -------------------
        if shutil.which("zsh"):
            env_off = dict(env)
            env_off["RAVENCLAUDE_LAUNCH_GUARD"] = "off"
            proc = _run_shell(["zsh", "-i", "-c", "claude --version"], env_off, nonrepo)
            if "stub-claude 9.9.9" not in proc.stdout:
                _st_fail(failures, "RAVENCLAUDE_LAUNCH_GUARD=off did not pass through cleanly: %r/%r" % (proc.stdout, proc.stderr))

        # --- 5. Helper deleted -> still fail-open --------------------------
        if shutil.which("zsh"):
            helper_path = os.path.join(scratch_home, ".claude", "launch-guard", "bin", HELPER_NAME)
            if os.path.isfile(helper_path):
                os.remove(helper_path)
            proc = _run_shell(["zsh", "-i", "-c", "claude --version"], env, nonrepo)
            if "stub-claude 9.9.9" not in proc.stdout:
                _st_fail(failures, "helper-deleted fail-open did not launch stub: %r/%r" % (proc.stdout, proc.stderr))
            # Restage for the remaining tests.
            proc = _run_self(["install", "--shell", "zsh"], env)
            if proc.returncode != 0:
                _st_fail(failures, "restage-after-delete install exited %d" % proc.returncode)

        # --- 10. Non-interactive, NOT-safe path never hangs, auto-allows ---
        if shutil.which("zsh"):
            t0 = time.time()
            proc = _run_shell(["zsh", "-i", "-c", "claude somecmd --unrelated"], env, nonrepo, timeout=8)
            elapsed = time.time() - t0
            if "stub-claude 9.9.9" not in proc.stdout:
                _st_fail(failures, "non-interactive not-safe path did not auto-allow: %r/%r" % (proc.stdout, proc.stderr))
            if "WARNING" not in proc.stderr:
                _st_fail(failures, "non-interactive not-safe path printed no warning: %r" % proc.stderr)
            if elapsed >= 5:
                _st_fail(failures, "non-interactive not-safe path took %.1fs (possible hang)" % elapsed)

        # --- 11. Safe launch records last-dir (the directory-recommendation
        #     feature's write side; the read side — `recommend`/`preferred` —
        #     is unit-tested in claude-launch-guard's own --self-test, and the
        #     interactive switch-and-launch branch is exercised only by shell
        #     syntax validation below, since this harness has no pty to drive
        #     a live interactive choice through). ---------------------------
        if shutil.which("zsh") and shutil.which("git"):
            git_fixture = os.path.join(scratch, "gitrepo")
            os.makedirs(git_fixture, exist_ok=True)
            subprocess.run(["git", "init", "-q", "."], cwd=git_fixture, check=False)
            subprocess.run(["git", "-C", git_fixture, "config", "user.email", "st@example.com"], check=False)
            subprocess.run(["git", "-C", git_fixture, "config", "user.name", "selftest"], check=False)
            last_dir_file = os.path.join(scratch_home, ".claude", "launch-guard", "last-dir")
            if os.path.isfile(last_dir_file):
                os.remove(last_dir_file)
            proc = _run_shell(["zsh", "-i", "-c", "claude --version"], env, git_fixture)
            if "stub-claude 9.9.9" not in proc.stdout:
                _st_fail(failures, "last-dir fixture: safe launch did not reach the stub: %r/%r" % (proc.stdout, proc.stderr))
            if not os.path.isfile(last_dir_file):
                _st_fail(failures, "safe launch did not write last-dir")
            else:
                with open(last_dir_file, encoding="utf-8") as fh:
                    recorded = fh.read().strip()
                if os.path.realpath(recorded) != os.path.realpath(git_fixture):
                    _st_fail(failures, "last-dir recorded %r, expected %r" % (recorded, git_fixture))

        # --- 6. --uninstall -> byte-identical to pre-install state ---------
        proc = _run_self(["--uninstall", "--shell", "zsh"], env)
        if proc.returncode != 0:
            _st_fail(failures, "uninstall exited %d: %s" % (proc.returncode, proc.stderr))
        with open(zshrc, encoding="utf-8") as fh:
            restored = fh.read()
        if restored != original_zshrc:
            _st_fail(failures, "uninstall did not restore byte-identical .zshrc content")

        # --- 7. fish target: valid native syntax or clean refusal ----------
        proc = _run_self(["install", "--shell", "fish"], env)
        if proc.returncode != 0:
            _st_fail(failures, "fish install exited %d: %s" % (proc.returncode, proc.stderr))
        fish_file = os.path.join(scratch_home, ".config", "fish", "functions", "claude.fish")
        if not os.path.isfile(fish_file):
            _st_fail(failures, "fish install did not create %s" % fish_file)
        else:
            with open(fish_file, encoding="utf-8") as fh:
                fish_text = fh.read()
            if "function claude" not in fish_text:
                _st_fail(failures, "fish function file missing 'function claude'")
            if "\nlocal " in fish_text or fish_text.startswith("local "):
                _st_fail(failures, "fish function file contains bash-only 'local' — not native fish")
            if shutil.which("fish"):
                ok, reason = _validate(fish_file, "fish")
                if not ok:
                    _st_fail(failures, "fish -n on generated function failed: %s" % reason)
            else:
                print("install_launch_guard self-test: fish not on PATH — skipping fish -n syntax check")
        proc = _run_self(["--uninstall", "--shell", "fish"], env)
        if proc.returncode != 0:
            _st_fail(failures, "fish uninstall exited %d" % proc.returncode)
        if os.path.isfile(fish_file):
            _st_fail(failures, "fish uninstall left %s in place" % fish_file)

        # --- 8. Unknown shell -> refuse, print block, exit 0 ---------------
        proc = _run_self(["install", "--shell", "notarealshell"], env)
        if proc.returncode != 0:
            _st_fail(failures, "unknown-shell install did not exit 0 (got %d)" % proc.returncode)
        if "unrecognized shell" not in proc.stdout or "claude()" not in proc.stdout:
            _st_fail(failures, "unknown-shell install did not print the expected refusal + block")

        # --- 9. Must-fail half: a broken marker match duplicates the block -
        fixture = render_block(POSIX_FUNCTION_BODY)
        broken_new_text, broken_replaced = _st_broken_splice(fixture)
        if broken_new_text.count(MARKER_BEGIN) != 2:
            _st_fail(
                failures,
                "must-fail half: a broken marker match did NOT duplicate the block — "
                "the idempotency test would not have teeth (got %d copies)"
                % broken_new_text.count(MARKER_BEGIN),
            )
        correct_new_text, _ = splice_block(fixture, render_block(POSIX_FUNCTION_BODY))
        if correct_new_text.count(MARKER_BEGIN) != 1:
            _st_fail(failures, "control: the REAL marker matching duplicated the block too")

    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    if failures:
        sys.stderr.write("SELF-TEST: %d failure(s)\n" % len(failures))
        return 1
    print("SELF-TEST PASS: install_launch_guard.py")
    return 0


def _st_broken_splice(existing_text: str):
    """Simulate a corrupted marker-replace: markers that never match. This is
    the must-fail-half proof that `splice_block`'s marker matching is what
    prevents duplication — feed it markers that can never match the real ones
    and confirm the (append-because-no-match) path duplicates instead of
    replacing, so the idempotency test above is proven to have real teeth."""
    lines = existing_text.splitlines(keepends=True)
    start_idx = end_idx = None
    bogus_begin, bogus_end = "# BOGUS BEGIN (never present)", "# BOGUS END (never present)"
    for i, line in enumerate(lines):
        if line.rstrip("\n") == bogus_begin:
            start_idx = i
        elif start_idx is not None and line.rstrip("\n") == bogus_end:
            end_idx = i
            break
    if start_idx is not None and end_idx is not None:
        before = "".join(lines[:start_idx])
        after = "".join(lines[end_idx + 1:])
        return before + render_block(POSIX_FUNCTION_BODY) + after, True
    if not existing_text:
        return render_block(POSIX_FUNCTION_BODY), False
    stripped = existing_text.rstrip("\n")
    return stripped + "\n\n" + render_block(POSIX_FUNCTION_BODY), False


# --- dispatch -------------------------------------------------------------------

def main(argv):
    action = None
    shell_override = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("install", "status", "--check", "--uninstall", "--self-test"):
            action = a
            i += 1
            continue
        if a == "--shell":
            shell_override = argv[i + 1] if i + 1 < len(argv) else None
            i += 2
            continue
        i += 1

    if action is None:
        action = "install"

    if action == "install":
        return cmd_install(shell_override, check_only=False)
    if action == "--check":
        return cmd_install(shell_override, check_only=True)
    if action == "--uninstall":
        return cmd_uninstall(shell_override)
    if action == "status":
        return cmd_status_report()
    if action == "--self-test":
        return cmd_self_test()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

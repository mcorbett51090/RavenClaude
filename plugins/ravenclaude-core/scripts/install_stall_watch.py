#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""install_stall_watch.py — install the stall watchdog as a macOS LaunchAgent.

TWO DESIGN CONSTRAINTS THAT ARE NOT NEGOTIABLE.

1. THE PLIST IS GENERATED HERE, NEVER SHIPPED AS XML. A committed .plist is
   reachable by the repo's formatter, and a `covers[]` entry watching a
   toolchain-rewritten file oscillates forever — a defect this project has hit
   twice. Generating it at install time keeps it out of the formatter's reach
   entirely.

2. THE INSTALLED CODE GOES TO A STABLE PATH, NOT THE PLUGIN CACHE. The cache is
   version-keyed — 23 version directories exist on this machine right now — so a
   LaunchAgent pointing into it would die silently at the next plugin bump. We
   copy into ~/.claude/stall-watch/bin/ and point the job there.

Idempotent: re-running replaces the copy, regenerates the plist, and re-bootstraps
the single job. It never creates a second job.
"""

from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys

LABEL = "net.ravenpower.claude-stall-watch"
INTERVAL_SEC = 300

HOME = os.path.expanduser("~")
STATE_DIR = os.path.join(HOME, ".claude", "stall-watch")
BIN_DIR = os.path.join(STATE_DIR, "bin")
LOG_DIR = os.path.join(STATE_DIR, "logs")
AGENTS_DIR = os.path.join(HOME, "Library", "LaunchAgents")
PLIST_PATH = os.path.join(AGENTS_DIR, LABEL + ".plist")

MODULES = ("stall_watch.py", "stall_reach.py")


def log(msg):
    sys.stdout.write("  %s\n" % msg)


def stage_modules(source_dir: str):
    for d in (STATE_DIR, BIN_DIR, LOG_DIR):
        if not os.path.isdir(d):
            os.makedirs(d, 0o700)
    os.chmod(STATE_DIR, 0o700)
    for name in MODULES:
        src = os.path.join(source_dir, name)
        if not os.path.isfile(src):
            raise SystemExit("missing source module: %s" % src)
        dst = os.path.join(BIN_DIR, name)
        shutil.copy2(src, dst)
        os.chmod(dst, 0o700)
        log("staged %s" % dst)


def generate_plist() -> dict:
    """Built as a dict and written with plistlib — no XML string templating,
    so a path can never break the document structure."""
    return {
        "Label": LABEL,
        "ProgramArguments": ["/usr/bin/python3", os.path.join(BIN_DIR, "stall_watch.py")],
        "StartInterval": INTERVAL_SEC,
        "RunAtLoad": True,
        "ProcessType": "Background",
        "StandardOutPath": os.path.join(LOG_DIR, "stdout.log"),
        "StandardErrorPath": os.path.join(LOG_DIR, "stderr.log"),
        # A launchd agent inherits almost nothing: a real bootstrapped agent was
        # measured seeing 12 env vars with this exact PATH. Declared explicitly
        # so the job does not depend on an inherited environment that is absent.
        "EnvironmentVariables": {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin"},
    }


def write_plist():
    if not os.path.isdir(AGENTS_DIR):
        os.makedirs(AGENTS_DIR, 0o755)
    with open(PLIST_PATH, "wb") as fh:
        plistlib.dump(generate_plist(), fh)
    os.chmod(PLIST_PATH, 0o644)
    log("generated %s" % PLIST_PATH)


def launchctl(args, check=False):
    proc = subprocess.run(["launchctl"] + args, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def bootstrap():
    uid = os.getuid()
    domain = "gui/%d" % uid
    # bootout first so re-running never yields two jobs. A non-zero rc here is
    # normal on a first install (nothing to unload) and is not an error.
    rc, out = launchctl(["bootout", "%s/%s" % (domain, LABEL)])
    if rc == 0:
        log("unloaded previous job")
    rc, out = launchctl(["bootstrap", domain, PLIST_PATH])
    if rc != 0:
        log("bootstrap rc=%d: %s" % (rc, out))
        return False
    log("bootstrapped %s into %s" % (LABEL, domain))
    return True


def verify():
    uid = os.getuid()
    rc, out = launchctl(["print", "gui/%d/%s" % (uid, LABEL)])
    if rc != 0:
        log("VERIFY FAILED: job not present after bootstrap (rc=%d)" % rc)
        return False
    state = [l.strip() for l in out.splitlines() if l.strip().startswith("state =")]
    log("job present; %s" % (state[0] if state else "state unknown"))
    return True


def main(argv):
    source_dir = os.path.dirname(os.path.abspath(__file__))
    sys.stdout.write("Installing %s\n" % LABEL)
    stage_modules(source_dir)
    write_plist()
    if not bootstrap():
        return 1
    if not verify():
        return 1
    sys.stdout.write("\nInstalled. Next: the P7 positive control —\n")
    sys.stdout.write("  launchctl kickstart -p gui/%d/%s\n" % (os.getuid(), LABEL))
    sys.stdout.write("  (fire it through the REAL loaded agent, never from a shell:\n")
    sys.stdout.write("   an interactive shell is a different execution context and\n")
    sys.stdout.write("   would test something other than what launchd actually does.)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Packaging move; canonical path is plugins/ravenclaude-core/scripts/classify_claim.py.

Thin compatibility shim so `python3 scripts/classify_claim.py` keeps working.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_CANON = (
    Path(__file__).resolve().parents[1]
    / "plugins"
    / "ravenclaude-core"
    / "scripts"
    / Path(__file__).name
)
if not _CANON.is_file():
    sys.stderr.write("shim: missing canonical %s\n" % _CANON)
    sys.exit(2)
# Preserve interpreter flags (Gate 177 runs `python3 -O scripts/classify_claim.py`).
_opt = ["-O"] * sys.flags.optimize
os.execv(sys.executable, [sys.executable, *_opt, str(_CANON), *sys.argv[1:]])

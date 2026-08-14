#!/usr/bin/env python3
"""Packaging move; canonical path is plugins/ravenclaude-core/scripts/check-design-schema.py.

Thin compatibility shim so `python3 scripts/check-design-schema.py` keeps working.
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
_opt = ["-O"] * sys.flags.optimize
os.execv(sys.executable, [sys.executable, *_opt, str(_CANON), *sys.argv[1:]])

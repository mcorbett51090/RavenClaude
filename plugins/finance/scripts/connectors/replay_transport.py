#!/usr/bin/env python3
"""replay_transport.py - a stdlib RECORD/REPLAY HTTP transport for the finance connectors.

WHAT THIS IS (and is NOT). This is the test/offline seam that lets the connector code and
its acceptance suite run with ZERO live credentials and ZERO network: it serves recorded,
obviously-synthetic JSON fixtures instead of calling a vendor API. It is NOT a live client
and NEVER opens a socket — that is a hard property, asserted by the acceptance suite by
patching socket.socket to raise and proving replay still works. Live wiring (a real HTTP
transport against the real token/report endpoints) is the CONSUMER's step; this module is
the fixture-backed stand-in used to develop and test against it. Decision-support
scaffolding, not a certified connector (../../CLAUDE.md sec.3).

Two modes:
  * REPLAY (default) — reads `<fixture_dir>/<name>.json`. A MISSING fixture is a LOUD
    failure (FixtureMissing), never a silent empty result or a fall-through to the network.
  * RECORD — `save(name, obj)` writes a fixture to disk (used to author fixtures from a
    known-good synthetic payload; it does not fetch anything live).

It exposes the two seams the connectors need:
  * token_request(url, data) -> TokenResponse     (OAuth token endpoint; keyed by provider)
  * fetch(name) -> dict                            (a recorded report/query payload)

Stdlib only (json/os/socket-for-the-guard-only). Python 3.8+.
"""
from __future__ import annotations

import json
import os
from collections import namedtuple

# Duck-typed response the OAuthClient reads (.status/.body/.headers).
TokenResponse = namedtuple("TokenResponse", ["status", "body", "headers"])


class FixtureMissing(FileNotFoundError):
    """Raised LOUDLY when a requested fixture does not exist. Never degrade to a live call
    or an empty result — a missing fixture is a test-authoring error that must surface."""


class ReplayTransport:
    """A fixture-backed transport. It has no HTTP/socket code at all — the only reason
    `import socket` appears nowhere here is deliberate: there is no live path to take."""

    def __init__(self, fixture_dir: str, mode: str = "replay"):
        if mode not in ("replay", "record"):
            raise ValueError(f"mode must be 'replay' or 'record', got {mode!r}")
        self.fixture_dir = fixture_dir
        self.mode = mode
        self.calls = []          # audit trail of (kind, name) for test assertions

    def _path(self, name: str) -> str:
        return os.path.join(self.fixture_dir, name + ".json")

    def _load(self, name: str) -> dict:
        path = self._path(name)
        if not os.path.exists(path):
            raise FixtureMissing(
                f"REPLAY: no recorded fixture for {name!r} at {path}. "
                f"Record it (ReplayTransport(mode='record').save({name!r}, ...)) or fix the "
                f"request name — replay NEVER falls through to a live network call."
            )
        with open(path) as fh:
            return json.load(fh)

    def save(self, name: str, obj: dict) -> str:
        """RECORD mode: persist a synthetic payload as a fixture. Returns the path written."""
        if self.mode != "record":
            raise RuntimeError("save() requires mode='record'")
        path = self._path(name)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(obj, fh, indent=2)
            fh.write("\n")
        self.calls.append(("record", name))
        return path

    def fetch(self, name: str) -> dict:
        """Return a recorded report/query payload (e.g. 'qbo/trial_balance'). Loud on miss."""
        self.calls.append(("fetch", name))
        return self._load(name)

    def token_request(self, url: str, data: dict) -> TokenResponse:
        """Serve a recorded token-endpoint response, keyed by the caller's provider tag.
        `url` is recorded for the audit trail but the fixture is selected by provider so a
        provider's endpoint URL can change without re-keying every fixture."""
        provider = (data or {}).get("provider")
        if not provider:
            raise ValueError("token_request payload must carry a 'provider' tag for replay keying")
        name = f"{provider}/token_refresh"
        self.calls.append(("token_request", name))
        rec = self._load(name)
        return TokenResponse(
            status=int(rec.get("status", 200)),
            body=rec.get("body", {}),
            headers=rec.get("headers", {}),
        )
